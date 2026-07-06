from pathlib import Path

import numpy as np

from model_utils import (
    NearestCentroidClassifier,
    accuracy_score,
    classification_report,
    save_model,
    train_test_split,
)
from preprocessing import build_dataset


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
NORMAL_DIR = RAW_DATA_DIR / "normal"
ABNORMAL_DIR = RAW_DATA_DIR / "abnormal"
MODELS_DIR = PROJECT_ROOT / "models"
RESULTS_DIR = PROJECT_ROOT / "results"
MODELS_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def train_and_evaluate(random_state: int = 42) -> None:
    X, y, paths = build_dataset(NORMAL_DIR, ABNORMAL_DIR)
    if X.shape[0] == 0:
        print("No scan data found in the dataset directories. Add files to data/raw/normal and data/raw/abnormal.")
        return

    classes, counts = np.unique(y, return_counts=True)
    if len(classes) < 2:
        print("At least two classes are required for training. Add both normal and abnormal scans.")
        return

    stratify = y if all(counts >= 2) else None
    if stratify is None:
        print("Warning: class counts are too small for stratified splitting, using an unstratified split.")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=stratify, random_state=random_state
    )

    model = NearestCentroidClassifier()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, target_names=["normal", "abnormal"], zero_division=0)

    model_path = MODELS_DIR / "neuroscan_model.pkl"
    save_model(model, model_path)

    results_path = RESULTS_DIR / "training_report.txt"
    with open(results_path, "w", encoding="utf-8") as f:
        f.write("NeuroScan Nepal training report\n")
        f.write("==============================\n")
        f.write(f"Model path: {model_path}\n")
        f.write(f"Samples: {len(y)}\n")
        f.write(f"Accuracy: {accuracy:.4f}\n")
        f.write("\nClassification report:\n")
        f.write(report)

    print("Training completed successfully.")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Model saved to: {model_path}")
    print(f"Report saved to: {results_path}")


if __name__ == "__main__":
    train_and_evaluate()
