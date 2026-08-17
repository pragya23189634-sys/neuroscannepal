#!/usr/bin/env python3
"""
NeuroScan Nepal — STANDALONE Colab/Kaggle training script.

Does NOT modify your local src/ files. Copy this single file into Google Colab.

Usage in Colab (after enabling GPU + uploading data zip):
  !python neuroscan_colab_train.py --data-root /content/data/raw
"""

from __future__ import annotations

import argparse
import json
import random
import shutil
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from PIL import Image
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, Dataset

try:
    import cv2
except ImportError:
    cv2 = None

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

IMAGE_SIZE = (128, 128)
SUPPORTED = {".png", ".jpg", ".jpeg", ".bmp"}


# ---------- preprocessing (standalone copy) ----------

def list_scan_files(folder: Path) -> List[Path]:
    if not folder.exists():
        return []
    return sorted(p for p in folder.rglob("*") if p.suffix.lower() in SUPPORTED)


def apply_clahe(image: np.ndarray) -> np.ndarray:
    image = np.asarray(image, dtype=np.float32)
    if cv2 is not None:
        u8 = np.clip(image, 0, 255).astype(np.uint8)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        return clahe.apply(u8).astype(np.float32)
    from PIL import ImageOps
    u8 = np.clip(image, 0, 255).astype(np.uint8)
    return np.asarray(ImageOps.equalize(Image.fromarray(u8, "L")), dtype=np.float32)


def load_scan(path: Path, use_clahe: bool = True) -> np.ndarray:
    if cv2 is not None:
        img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
        if img is not None:
            scan = img.astype(np.float32)
            return apply_clahe(scan) if use_clahe else scan
    with Image.open(path) as im:
        scan = np.asarray(im.convert("L"), dtype=np.float32)
        return apply_clahe(scan) if use_clahe else scan


def normalize_scan(scan: np.ndarray) -> np.ndarray:
    scan = np.nan_to_num(scan, nan=0.0).astype(np.float32)
    scan = np.clip(scan, 0, None)
    scan = scan - scan.min()
    if scan.max() > 0:
        scan = scan / scan.max()
    return scan


def resize_scan(scan: np.ndarray) -> np.ndarray:
    pil = Image.fromarray((scan * 255).astype(np.uint8), "L")
    pil = pil.resize(IMAGE_SIZE, Image.BILINEAR)
    return np.asarray(pil, dtype=np.float32) / 255.0


def augment_scan(scan: np.ndarray) -> np.ndarray:
    rng = np.random.default_rng()
    if rng.random() < 0.5:
        scan = np.fliplr(scan)
    if rng.random() < 0.7:
        angle = float(rng.uniform(-12, 12))
        pil = Image.fromarray((np.clip(scan, 0, 1) * 255).astype(np.uint8), "L")
        pil = pil.rotate(angle, resample=Image.BILINEAR, fillcolor=0)
        scan = np.asarray(pil, dtype=np.float32) / 255.0
    if rng.random() < 0.5:
        scan = np.power(np.clip(scan, 0, 1), float(rng.uniform(0.85, 1.15)))
    if rng.random() < 0.35:
        scan = scan + rng.normal(0, 0.015, scan.shape).astype(np.float32)
    return np.clip(scan, 0, 1)


# ---------- model ----------

class BaselineCNN(nn.Module):
    def __init__(self, num_classes: int = 2) -> None:
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(1, 32, 3, padding=1), nn.BatchNorm2d(32), nn.ReLU(True), nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1), nn.BatchNorm2d(64), nn.ReLU(True), nn.MaxPool2d(2),
            nn.Conv2d(64, 128, 3, padding=1), nn.BatchNorm2d(128), nn.ReLU(True),
            nn.AdaptiveAvgPool2d((4, 4)),
        )
        self.classifier = nn.Sequential(
            nn.Flatten(), nn.Linear(2048, 256), nn.ReLU(True), nn.Dropout(0.4),
            nn.Linear(256, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.classifier(self.features(x))


# ---------- dataset ----------

class CachedScanDataset(Dataset):
    def __init__(self, paths: List[Path], labels: List[int], augment: bool = False) -> None:
        self.labels = labels
        self.augment = augment
        self.scans: List[np.ndarray] = []
        for i, path in enumerate(paths):
            s = resize_scan(normalize_scan(load_scan(path)))
            self.scans.append(s)
            if len(paths) >= 100 and (i + 1) % max(1, len(paths) // 10) == 0:
                print(f"  Cached {i + 1}/{len(paths)}")

    def __len__(self) -> int:
        return len(self.scans)

    def __getitem__(self, index: int):
        scan = self.scans[index].copy()
        if self.augment:
            scan = augment_scan(scan)
        t = torch.from_numpy(np.ascontiguousarray(scan)).unsqueeze(0).float()
        return t, torch.tensor(self.labels[index], dtype=torch.long)


def make_loaders(train_p, train_y, val_p, val_y, batch_size, device):
    kw = dict(batch_size=batch_size, pin_memory=device.type == "cuda")
    if device.type == "cuda":
        kw["num_workers"] = 2
    print("Caching training scans...")
    train_ds = CachedScanDataset(train_p, train_y, augment=True)
    print("Caching validation scans...")
    val_ds = CachedScanDataset(val_p, val_y, augment=False)
    return (
        DataLoader(train_ds, shuffle=True, **kw),
        DataLoader(val_ds, shuffle=False, **kw),
    )


def binary_metrics(targets, predictions):
    tp = sum(t == 1 and p == 1 for t, p in zip(targets, predictions))
    tn = sum(t == 0 and p == 0 for t, p in zip(targets, predictions))
    fp = sum(t == 0 and p == 1 for t, p in zip(targets, predictions))
    fn = sum(t == 1 and p == 0 for t, p in zip(targets, predictions))
    sens = tp / max(tp + fn, 1)
    spec = tn / max(tn + fp, 1)
    return {"balanced_accuracy": (sens + spec) / 2, "sensitivity": sens, "specificity": spec}


def fit_temperature(logits, targets):
    if logits.numel() == 0:
        return 1.0
    temps = torch.linspace(0.5, 5.0, 91)
    losses = [nn.functional.cross_entropy(logits / t, targets).item() for t in temps]
    return float(temps[int(np.argmin(losses))].item())


def train(
    data_root: Path,
    out_dir: Path,
    epochs: int = 30,
    batch_size: int = 64,
    lr: float = 5e-4,
    pretrained: Path | None = None,
    patience: int = 7,
    seed: int = 42,
) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

    normal_dir = data_root / "normal"
    abnormal_dir = data_root / "abnormal"
    paths = list_scan_files(normal_dir) + list_scan_files(abnormal_dir)
    labels = [0] * len(list_scan_files(normal_dir)) + [1] * len(list_scan_files(abnormal_dir))
    if len(paths) < 2 or len(set(labels)) < 2:
        raise SystemExit("Need normal + abnormal images in data_root/normal and data_root/abnormal")

    train_p, val_p, train_y, val_y = train_test_split(
        paths, labels, test_size=0.2, stratify=labels, random_state=seed
    )
    print(f"Train: {len(train_p)}, Val: {len(val_p)}")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}" + (f" ({torch.cuda.get_device_name(0)})" if device.type == "cuda" else ""))

    train_loader, val_loader = make_loaders(train_p, train_y, val_p, val_y, batch_size, device)
    model = BaselineCNN().to(device)

    out_dir.mkdir(parents=True, exist_ok=True)
    model_path = out_dir / "cnn_baseline.pth"
    if pretrained and pretrained.exists():
        model.load_state_dict(torch.load(pretrained, map_location=device, weights_only=True))
        print(f"Loaded pretrained: {pretrained}")
    elif model_path.exists():
        shutil.copy2(model_path, out_dir / "cnn_baseline_previous.pth")

    counts = np.bincount(np.array(train_y), minlength=2)
    weights = torch.tensor(len(train_y) / (2.0 * np.maximum(counts, 1)), dtype=torch.float32, device=device)
    optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    criterion = nn.CrossEntropyLoss(weight=weights, label_smoothing=0.03)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, factor=0.5, patience=2, min_lr=1e-6)

    best_bal, best_acc, best_loss, best_epoch = 0.0, 0.0, float("inf"), 0
    stale = 0

    for epoch in range(1, epochs + 1):
        model.train()
        tl, tc, tt = 0.0, 0, 0
        for x, y in train_loader:
            x, y = x.to(device), y.to(device)
            optimizer.zero_grad()
            out = model(x)
            loss = criterion(out, y)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 5.0)
            optimizer.step()
            tl += loss.item() * x.size(0)
            tc += (out.argmax(1) == y).sum().item()
            tt += x.size(0)

        model.eval()
        vl, vc, vt = 0.0, 0, 0
        vt_list, vp_list = [], []
        with torch.no_grad():
            for x, y in val_loader:
                x, y = x.to(device), y.to(device)
                out = model(x)
                loss = criterion(out, y)
                pred = out.argmax(1)
                vl += loss.item() * x.size(0)
                vc += (pred == y).sum().item()
                vt += x.size(0)
                vt_list.extend(y.cpu().tolist())
                vp_list.extend(pred.cpu().tolist())

        metrics = binary_metrics(vt_list, vp_list)
        val_acc = vc / max(vt, 1)
        val_loss = vl / max(vt, 1)
        scheduler.step(val_loss)
        print(
            f"Epoch {epoch}/{epochs} | train_acc={tc/max(tt,1):.4f} | val_acc={val_acc:.4f} | "
            f"balanced={metrics['balanced_accuracy']:.4f} | lr={optimizer.param_groups[0]['lr']:.2e}"
        )

        improved = metrics["balanced_accuracy"] > best_bal + 1e-4 or (
            abs(metrics["balanced_accuracy"] - best_bal) <= 1e-4 and val_loss < best_loss
        )
        if improved:
            best_bal, best_acc, best_loss, best_epoch, stale = metrics["balanced_accuracy"], val_acc, val_loss, epoch, 0
            torch.save(model.state_dict(), model_path)
        else:
            stale += 1
            if stale >= patience:
                print(f"Early stop at epoch {epoch}, best={best_epoch}")
                break

    state = torch.load(model_path, map_location=device, weights_only=True)
    model.load_state_dict(state)
    model.eval()

    logits, targets = [], []
    with torch.no_grad():
        for x, y in val_loader:
            logits.append(model(x.to(device)).cpu())
            targets.append(y)
    all_logits = torch.cat(logits)
    all_targets = torch.cat(targets)
    temp = fit_temperature(all_logits, all_targets)
    cal_path = out_dir / "cnn_baseline_calibration.json"
    cal_path.write_text(json.dumps({
        "temperature": round(temp, 4),
        "uncertainty_threshold": 0.70,
        "best_epoch": best_epoch,
        "validation_accuracy": round(best_acc, 4),
        "balanced_accuracy": round(best_bal, 4),
    }, indent=2), encoding="utf-8")

    report = out_dir / "cnn_baseline_report.txt"
    report.write_text(
        f"NeuroScan Nepal Colab training report\n"
        f"Train samples: {len(train_y)}\n"
        f"Validation samples: {len(val_y)}\n"
        f"Best epoch: {best_epoch}\n"
        f"Best validation accuracy: {best_acc:.4f}\n"
        f"Best balanced accuracy: {best_bal:.4f}\n"
        f"Calibration temperature: {temp:.4f}\n"
        f"Device: {device}\n",
        encoding="utf-8",
    )
    print(f"\nDone. val_acc={best_acc:.4f} balanced={best_bal:.4f}")
    print(f"Saved: {model_path}\n       {cal_path}\n       {report}")

    if plt:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(["Val accuracy", "Balanced acc"], [best_acc, best_bal])
        ax.set_ylim(0, 1)
        ax.set_title("NeuroScan Colab training")
        fig.savefig(out_dir / "training_summary.png", dpi=150)
        print(f"Saved: {out_dir / 'training_summary.png'}")


def main():
    p = argparse.ArgumentParser(description="NeuroScan standalone Colab trainer")
    p.add_argument("--data-root", type=Path, required=True, help="Folder with normal/ and abnormal/")
    p.add_argument("--out-dir", type=Path, default=Path("/content/output"))
    p.add_argument("--pretrained", type=Path, default=None)
    p.add_argument("--epochs", type=int, default=30)
    p.add_argument("--batch-size", type=int, default=64)
    p.add_argument("--lr", type=float, default=5e-4)
    p.add_argument("--patience", type=int, default=7)
    args = p.parse_args()
    train(args.data_root, args.out_dir, args.epochs, args.batch_size, args.lr, args.pretrained, args.patience)


if __name__ == "__main__":
    main()
