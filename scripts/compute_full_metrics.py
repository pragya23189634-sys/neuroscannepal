#!/usr/bin/env python3
"""Compute precision, recall, F1, and AUC-ROC for the deployed BaselineCNN on the validation split."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

import numpy as np
import torch
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import train_test_split

from cnn_baseline import BaselineCNN
from dataset_utils import CachedScanDataset, build_scan_paths, dataloader_kwargs
from torch.utils.data import DataLoader

SPLIT_SEED = 42
TEST_SIZE = 0.2
MODEL_PATH = ROOT / "models" / "cnn_baseline.pth"
RESULTS_DIR = ROOT / "results"


def main() -> None:
    data_root = ROOT / "data" / "raw"
    paths, labels = build_scan_paths(data_root / "normal", data_root / "abnormal")
    _, val_paths, _, val_labels = train_test_split(
        paths, labels, test_size=TEST_SIZE, stratify=labels, random_state=SPLIT_SEED
    )

    device = torch.device("cpu")
    val_ds = CachedScanDataset(val_paths, val_labels, augment=False, seed=SPLIT_SEED, use_clahe=True)
    val_loader = DataLoader(val_ds, **dataloader_kwargs(32, False, device))

    model = BaselineCNN(num_classes=2).to(device)
    state = torch.load(MODEL_PATH, map_location=device)
    model.load_state_dict(state)
    model.eval()

    y_true, y_pred, y_prob_abnormal = [], [], []
    with torch.no_grad():
        for inputs, targets in val_loader:
            logits = model(inputs)
            probs = torch.softmax(logits, dim=1).cpu().numpy()
            preds = probs.argmax(axis=1)
            y_true.extend(targets.tolist())
            y_pred.extend(preds.tolist())
            y_prob_abnormal.extend(probs[:, 1].tolist())

    metrics = {
        "validation_samples": len(y_true),
        "accuracy": round(float(accuracy_score(y_true, y_pred)), 4),
        "balanced_accuracy": round(float(balanced_accuracy_score(y_true, y_pred)), 4),
        "precision_abnormal": round(float(precision_score(y_true, y_pred, pos_label=1, zero_division=0)), 4),
        "recall_abnormal": round(float(recall_score(y_true, y_pred, pos_label=1, zero_division=0)), 4),
        "f1_abnormal": round(float(f1_score(y_true, y_pred, pos_label=1, zero_division=0)), 4),
        "auc_roc": round(float(roc_auc_score(y_true, y_prob_abnormal)), 4),
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
        "classification_report": classification_report(y_true, y_pred, target_names=["normal", "abnormal"]),
    }

    fpr, tpr, thresholds = roc_curve(y_true, y_prob_abnormal)
    metrics["roc_curve"] = {
        "fpr": [round(float(x), 4) for x in fpr[:20]],
        "tpr": [round(float(x), 4) for x in tpr[:20]],
        "thresholds": [round(float(x), 4) for x in thresholds[:20]],
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_json = RESULTS_DIR / "full_metrics.json"
    out_txt = RESULTS_DIR / "full_metrics.txt"
    out_json.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    out_txt.write_text(
        "\n".join(
            [
                "NeuroScan Nepal — Full validation metrics (BaselineCNN)",
                f"Samples: {metrics['validation_samples']}  Seed: {SPLIT_SEED}",
                f"Accuracy: {metrics['accuracy']}",
                f"Balanced accuracy: {metrics['balanced_accuracy']}",
                f"Precision (abnormal): {metrics['precision_abnormal']}",
                f"Recall (abnormal): {metrics['recall_abnormal']}",
                f"F1 (abnormal): {metrics['f1_abnormal']}",
                f"AUC-ROC: {metrics['auc_roc']}",
                "",
                metrics["classification_report"],
            ]
        ),
        encoding="utf-8",
    )
    print(out_txt.read_text(encoding="utf-8"))
    print(f"Saved: {out_json}")


if __name__ == "__main__":
    main()
