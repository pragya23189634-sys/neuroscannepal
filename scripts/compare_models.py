#!/usr/bin/env python3
"""Train/evaluate BaselineCNN, VGG16, and EfficientNetB0 on the same split.

Writes:
  results/model_comparison.json
  results/model_comparison.txt
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, Dataset
from torchvision import models

from cnn_baseline import BaselineCNN, binary_metrics
from dataset_utils import build_scan_paths, dataloader_kwargs, make_loaders, CachedScanDataset
from preprocessing import list_scan_files

# Import transfer-learning dataset + model factory from numbered module
import importlib.util

_tl_spec = importlib.util.spec_from_file_location("transfer_learning", SRC / "03_transfer_learning.py")
_tl = importlib.util.module_from_spec(_tl_spec)
_tl_spec.loader.exec_module(_tl)
TransferLearningDataset = _tl.TransferLearningDataset
create_transfer_model = _tl.create_model

DATA_ROOT = ROOT / "data" / "raw"
RESULTS_DIR = ROOT / "results"
MODELS_DIR = ROOT / "models"
FRONTEND_CONFIG = ROOT / "frontend" / "src" / "config.js"
SPLIT_SEED = 42
TEST_SIZE = 0.2


class CachedTransferDataset(Dataset):
    """Preload 224×224 transfer-learning tensors once (avoids repeated CLAHE disk I/O)."""

    def __init__(self, paths, labels, seed: int = SPLIT_SEED) -> None:
        source = TransferLearningDataset(paths, labels, augment=False, seed=seed)
        self.labels = list(labels)
        self.tensors: list[torch.Tensor] = []
        total = len(source)
        for index in range(total):
            tensor, _ = source[index]
            self.tensors.append(tensor)
            if total >= 64 and (index + 1) % 128 == 0:
                print(f"  Cached {index + 1}/{total} transfer tensors...", flush=True)
        if total:
            print(f"  Cached {total}/{total} transfer tensors.", flush=True)

    def __len__(self) -> int:
        return len(self.tensors)

    def __getitem__(self, index: int):
        return self.tensors[index], torch.tensor(self.labels[index], dtype=torch.long)


def _run_validation(model, val_loader, device: torch.device) -> tuple[float, float]:
    model.eval()
    val_targets, val_preds = [], []
    with torch.no_grad():
        for inputs, targets in val_loader:
            inputs = inputs.to(device)
            preds = model(inputs).argmax(dim=1).cpu().tolist()
            val_preds.extend(preds)
            val_targets.extend(targets.tolist())
    val_acc = sum(t == p for t, p in zip(val_targets, val_preds)) / max(len(val_targets), 1)
    bal = binary_metrics(val_targets, val_preds)["balanced_accuracy"]
    return val_acc, bal


def evaluate_baseline_checkpoint(
    val_paths,
    val_labels,
    device: torch.device,
    weights_path: Path,
    batch_size: int = 32,
) -> dict:
    """Score an existing BaselineCNN checkpoint on the shared validation split."""
    print("Preloading validation scans into memory...", flush=True)
    val_dataset = CachedScanDataset(
        val_paths, val_labels, augment=False, seed=SPLIT_SEED, use_clahe=True
    )
    val_loader = DataLoader(val_dataset, **dataloader_kwargs(batch_size, False, device))
    model = BaselineCNN(num_classes=2).to(device)
    state = torch.load(weights_path, map_location=device)
    model.load_state_dict(state)
    val_acc, bal = _run_validation(model, val_loader, device)
    print(
        f"  BaselineCNN (checkpoint): val_acc={val_acc:.4f}, balanced={bal:.4f}",
        flush=True,
    )
    return {
        "model": "BaselineCNN",
        "input": "128×128 grayscale + CLAHE",
        "parameters": "~0.5M (custom)",
        "validation_accuracy_pct": round(val_acc * 100, 2),
        "balanced_accuracy_pct": round(bal * 100, 2),
        "best_epoch": None,
        "epochs_run": 0,
        "weights_path": str(weights_path.relative_to(ROOT)),
        "deployed": True,
        "notes": "Evaluated from saved checkpoint on the shared 80/20 split (seed 42).",
    }


def evaluate_baseline(
    train_paths,
    train_labels,
    val_paths,
    val_labels,
    device: torch.device,
    epochs: int = 15,
    batch_size: int = 32,
) -> dict:
    """Train BaselineCNN (128x128 CLAHE) on the shared split."""
    train_loader, val_loader = make_loaders(
        train_paths,
        train_labels,
        val_paths,
        val_labels,
        batch_size=batch_size,
        device=device,
        augment=True,
        seed=SPLIT_SEED,
        cache=True,
        use_clahe=True,
    )
    model = BaselineCNN(num_classes=2).to(device)
    class_counts = np.bincount(np.asarray(train_labels, dtype=np.int64), minlength=2)
    weights = len(train_labels) / (2.0 * np.maximum(class_counts, 1))
    criterion = nn.CrossEntropyLoss(
        weight=torch.tensor(weights, dtype=torch.float32, device=device),
        label_smoothing=0.03,
    )
    optimizer = optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)

    best = {"val_accuracy": 0.0, "balanced_accuracy": 0.0, "best_epoch": 0}
    model_path = MODELS_DIR / "compare_baselinecnn.pth"

    for epoch in range(1, epochs + 1):
        model.train()
        for inputs, targets in train_loader:
            inputs, targets = inputs.to(device), targets.to(device)
            optimizer.zero_grad()
            loss = criterion(model(inputs), targets)
            loss.backward()
            optimizer.step()

        val_acc, bal = _run_validation(model, val_loader, device)
        print(f"  BaselineCNN epoch {epoch}/{epochs}: val_acc={val_acc:.4f}, balanced={bal:.4f}", flush=True)

        if val_acc >= best["val_accuracy"]:
            best = {"val_accuracy": val_acc, "balanced_accuracy": bal, "best_epoch": epoch}
            torch.save(model.state_dict(), model_path)

    return {
        "model": "BaselineCNN",
        "input": "128×128 grayscale + CLAHE",
        "parameters": "~0.5M (custom)",
        "validation_accuracy_pct": round(best["val_accuracy"] * 100, 2),
        "balanced_accuracy_pct": round(best["balanced_accuracy"] * 100, 2),
        "best_epoch": best["best_epoch"],
        "epochs_run": epochs,
        "weights_path": str(model_path.relative_to(ROOT)),
        "deployed": True,
        "notes": "Selected for offline deployment and train–inference parity at 128×128.",
    }


def evaluate_transfer(
    arch: str,
    train_paths,
    train_labels,
    val_paths,
    val_labels,
    device: torch.device,
    epochs: int = 10,
    batch_size: int = 16,
) -> dict:
    """Train VGG16 or EfficientNetB0 (224×224 RGB + CLAHE)."""
    label = "VGG16" if arch == "vgg16" else "EfficientNetB0"
    print(f"  Preloading {label} tensors...", flush=True)
    train_ds = CachedTransferDataset(train_paths, train_labels, seed=SPLIT_SEED)
    val_ds = CachedTransferDataset(val_paths, val_labels, seed=SPLIT_SEED)
    train_loader = DataLoader(train_ds, **dataloader_kwargs(batch_size, True, device))
    val_loader = DataLoader(val_ds, **dataloader_kwargs(batch_size, False, device))

    model = create_transfer_model(arch, num_classes=2, freeze_backbone=True).to(device)
    optimizer = optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=1e-4)
    criterion = nn.CrossEntropyLoss()

    model_path = MODELS_DIR / f"compare_{arch}.pth"
    best = {"val_accuracy": 0.0, "balanced_accuracy": 0.0, "best_epoch": 0}

    for epoch in range(1, epochs + 1):
        model.train()
        for inputs, targets in train_loader:
            inputs, targets = inputs.to(device), targets.to(device)
            optimizer.zero_grad()
            loss = criterion(model(inputs), targets)
            loss.backward()
            optimizer.step()

        val_acc, bal = _run_validation(model, val_loader, device)
        print(f"  {label} epoch {epoch}/{epochs}: val_acc={val_acc:.4f}, balanced={bal:.4f}", flush=True)

        if val_acc > best["val_accuracy"]:
            best = {"val_accuracy": val_acc, "balanced_accuracy": bal, "best_epoch": epoch}
            torch.save(model.state_dict(), model_path)

    return {
        "model": label,
        "input": "224×224 RGB + CLAHE",
        "parameters": "VGG16 ~138M / EfficientNetB0 ~5M (ImageNet pretrained)",
        "validation_accuracy_pct": round(best["val_accuracy"] * 100, 2),
        "balanced_accuracy_pct": round(best["balanced_accuracy"] * 100, 2),
        "best_epoch": best["best_epoch"],
        "epochs_run": epochs,
        "weights_path": str(model_path.relative_to(ROOT)),
        "deployed": False,
        "notes": "Transfer-learning comparison run; not used in live pipeline.",
    }


def evaluate_transfer_checkpoint(
    arch: str,
    val_paths,
    val_labels,
    device: torch.device,
    weights_path: Path,
    batch_size: int = 16,
) -> dict:
    """Score a saved VGG16 / EfficientNetB0 checkpoint on the shared validation split."""
    label = "VGG16" if arch == "vgg16" else "EfficientNetB0"
    print(f"  Evaluating {label} checkpoint...", flush=True)
    val_ds = CachedTransferDataset(val_paths, val_labels, seed=SPLIT_SEED)
    val_loader = DataLoader(val_ds, **dataloader_kwargs(batch_size, False, device))
    model = create_transfer_model(arch, num_classes=2, freeze_backbone=True).to(device)
    model.load_state_dict(torch.load(weights_path, map_location=device))
    val_acc, bal = _run_validation(model, val_loader, device)
    print(f"  {label} (checkpoint): val_acc={val_acc:.4f}, balanced={bal:.4f}", flush=True)
    return {
        "model": label,
        "input": "224×224 RGB + CLAHE",
        "parameters": "VGG16 ~138M / EfficientNetB0 ~5M (ImageNet pretrained)",
        "validation_accuracy_pct": round(val_acc * 100, 2),
        "balanced_accuracy_pct": round(bal * 100, 2),
        "best_epoch": None,
        "epochs_run": 0,
        "weights_path": str(weights_path.relative_to(ROOT)),
        "deployed": False,
        "notes": "Evaluated from saved comparison checkpoint on the shared split.",
    }


def pick_best(rows: list[dict]) -> str:
    """Highest balanced accuracy; tie-breaker = smaller model (BaselineCNN)."""
    ranked = sorted(
        rows,
        key=lambda r: (r["balanced_accuracy_pct"], r["validation_accuracy_pct"]),
        reverse=True,
    )
    return ranked[0]["model"]


def write_results(rows: list[dict], train_count: int, val_count: int, started: float) -> None:
    best_name = pick_best(rows)
    for row in rows:
        row["highest_balanced_acc"] = row["model"] == best_name

    payload = {
        "dataset": "Grande International Hospital (data/raw)",
        "train_samples": train_count,
        "val_samples": val_count,
        "split": f"stratified 80/20, seed={SPLIT_SEED}",
        "best_by_balanced_accuracy": best_name,
        "deployed_model": "BaselineCNN",
        "deployment_reason": (
            "BaselineCNN chosen for live system: offline CPU inference, 128×128 CLAHE parity, "
            "and strong accuracy even when transfer models score higher on 224×224 RGB."
        ),
        "elapsed_minutes": round((time.time() - started) / 60, 1),
        "models": rows,
    }

    json_path = RESULTS_DIR / "model_comparison.json"
    txt_path = RESULTS_DIR / "model_comparison.txt"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "NeuroScan Nepal — Model comparison (same train/val split)",
        "=" * 56,
        f"Train: {train_count}  Val: {val_count}  Seed: {SPLIT_SEED}",
        f"Best balanced accuracy: {best_name}",
        "Deployed in pipeline: BaselineCNN",
        "",
    ]
    for row in rows:
        lines.extend(
            [
                f"{row['model']}",
                f"  Validation accuracy: {row['validation_accuracy_pct']}%",
                f"  Balanced accuracy:   {row['balanced_accuracy_pct']}%",
                f"  Input: {row['input']}",
                f"  Best epoch: {row.get('best_epoch', 'n/a')} / {row['epochs_run']}",
                f"  Deployed: {'yes' if row['deployed'] else 'no'}",
                "",
            ]
        )
    txt_path.write_text("\n".join(lines), encoding="utf-8")
    print("\n" + txt_path.read_text(encoding="utf-8"), flush=True)
    print(f"Saved: {json_path}", flush=True)
    print(f"Saved: {txt_path}", flush=True)
    sync_frontend_config(rows, best_name)


def sync_frontend_config(rows: list[dict], best_name: str) -> None:
    """Patch MODEL_COMPARISON in frontend/src/config.js from recorded scores."""
    if not FRONTEND_CONFIG.exists():
        return

    lines = [
        "/** Same stratified 80/20 split (seed 42). Auto-updated by scripts/compare_models.py */",
        "export const MODEL_COMPARISON = [",
    ]
    for row in rows:
        lines.append("  {")
        lines.append(f"    model: '{row['model']}',")
        lines.append(f"    input: '{row['input']}',")
        lines.append(f"    validationAccuracy: '{row['validation_accuracy_pct']}%',")
        lines.append(f"    balancedAccuracy: '{row['balanced_accuracy_pct']}%',")
        lines.append(f"    deployed: {str(bool(row['deployed'])).lower()},")
        lines.append(f"    best: {str(row['model'] == best_name).lower()},")
        lines.append("  },")
    lines.append("]")
    block = "\n".join(lines)

    text = FRONTEND_CONFIG.read_text(encoding="utf-8")
    start = text.find("/** Same stratified 80/20 split")
    end = text.find("]", start) + 1 if start >= 0 else -1
    if start >= 0 and end > start:
        updated = text[:start] + block + text[end:]
    else:
        updated = text
    FRONTEND_CONFIG.write_text(updated, encoding="utf-8")
    print(f"Updated: {FRONTEND_CONFIG}", flush=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare BaselineCNN, VGG16, and EfficientNetB0.")
    parser.add_argument("--baseline-epochs", type=int, default=15)
    parser.add_argument("--transfer-epochs", type=int, default=None)
    parser.add_argument(
        "--skip-baseline-train",
        action="store_true",
        help="Evaluate compare_baselinecnn.pth (or cnn_baseline.pth) instead of retraining.",
    )
    parser.add_argument(
        "--only",
        choices=["baseline", "vgg16", "efficientnetb0"],
        help="Run a single model stage (useful on CPU).",
    )
    parser.add_argument(
        "--eval-checkpoint",
        action="store_true",
        help="Evaluate saved compare_*.pth weights instead of training.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    normal_dir = DATA_ROOT / "normal"
    abnormal_dir = DATA_ROOT / "abnormal"
    if not normal_dir.exists() or not abnormal_dir.exists():
        raise SystemExit(f"Dataset not found under {DATA_ROOT}. Add normal/ and abnormal/ MRI folders.")

    paths, labels = build_scan_paths(normal_dir, abnormal_dir)
    train_paths, val_paths, train_labels, val_labels = train_test_split(
        paths, labels, test_size=TEST_SIZE, stratify=labels, random_state=SPLIT_SEED
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    transfer_epochs = args.transfer_epochs or (10 if device.type == "cuda" else 5)
    print(f"Device: {device}", flush=True)
    print(f"Samples: train={len(train_paths)}, val={len(val_paths)} (seed={SPLIT_SEED})", flush=True)
    print(f"Transfer epochs: {transfer_epochs}", flush=True)
    print(flush=True)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    started = time.time()
    rows = []

    run_baseline = args.only in (None, "baseline")
    run_vgg16 = args.only in (None, "vgg16")
    run_efficientnet = args.only in (None, "efficientnetb0")

    if run_baseline:
        print("=== BaselineCNN ===", flush=True)
        baseline_weights = MODELS_DIR / "compare_baselinecnn.pth"
        fallback_weights = MODELS_DIR / "cnn_baseline.pth"
        if args.skip_baseline_train and baseline_weights.exists():
            rows.append(
                evaluate_baseline_checkpoint(val_paths, val_labels, device, baseline_weights)
            )
        elif args.skip_baseline_train and fallback_weights.exists():
            row = evaluate_baseline_checkpoint(val_paths, val_labels, device, fallback_weights)
            row["notes"] = "Evaluated deployed cnn_baseline.pth on the shared split."
            rows.append(row)
        else:
            rows.append(
                evaluate_baseline(
                    train_paths,
                    train_labels,
                    val_paths,
                    val_labels,
                    device,
                    epochs=args.baseline_epochs,
                )
            )

    if run_efficientnet:
        print("\n=== EfficientNetB0 ===", flush=True)
        eff_weights = MODELS_DIR / "compare_efficientnetb0.pth"
        if args.eval_checkpoint and eff_weights.exists():
            rows.append(
                evaluate_transfer_checkpoint(
                    "efficientnetb0", val_paths, val_labels, device, eff_weights
                )
            )
        else:
            rows.append(
                evaluate_transfer(
                    "efficientnetb0",
                    train_paths,
                    train_labels,
                    val_paths,
                    val_labels,
                    device,
                    epochs=transfer_epochs,
                )
            )

    if run_vgg16:
        print("\n=== VGG16 ===", flush=True)
        vgg_weights = MODELS_DIR / "compare_vgg16.pth"
        if args.eval_checkpoint and vgg_weights.exists():
            rows.append(
                evaluate_transfer_checkpoint("vgg16", val_paths, val_labels, device, vgg_weights)
            )
        else:
            rows.append(
                evaluate_transfer(
                    "vgg16",
                    train_paths,
                    train_labels,
                    val_paths,
                    val_labels,
                    device,
                    epochs=transfer_epochs,
                    batch_size=8,
                )
            )

    if args.only:
        json_path = RESULTS_DIR / "model_comparison.json"
        if json_path.exists():
            existing = json.loads(json_path.read_text(encoding="utf-8")).get("models", [])
            existing_names = {row["model"] for row in rows}
            rows = [row for row in existing if row["model"] not in existing_names] + rows

    write_results(rows, len(train_paths), len(val_paths), started)


if __name__ == "__main__":
    main()
