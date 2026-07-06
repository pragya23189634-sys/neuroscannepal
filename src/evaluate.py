from argparse import ArgumentParser
from pathlib import Path

import numpy as np

from model_utils import (
    classification_report,
    confusion_matrix,
    load_model,
    train_test_split,
)
from preprocessing import build_dataset


def load_model(model_path: Path):
    if not model_path.exists():
        raise FileNotFoundError(f"Model file not found: {model_path}")

    if joblib is not None and model_path.suffix == ".joblib":
        return joblib.load(model_path)

    import pickle

    with open(model_path, "rb") as fh:
        return pickle.load(fh)


def save_confusion_matrix(y_true: np.ndarray, y_pred: np.ndarray, output_path: Path) -> bool:
    try:
        import matplotlib.pyplot as plt
    except ImportError:  # pragma: no cover
        return False

    cm = confusion_matrix(y_true, y_pred)
    labels = ["normal", "abnormal"]
    fig, ax = plt.subplots(figsize=(4, 4))
    im = ax.imshow(cm, interpolation="nearest", cmap="Blues")
    ax.figure.colorbar(im, ax=ax)
    ax.set(
        xticks=np.arange(len(labels)),
        yticks=np.arange(len(labels)),
        xticklabels=labels,
        yticklabels=labels,
        ylabel="True label",
        xlabel="Predicted label",
        title="Confusion Matrix",
    )
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    fmt = "d"
    thresh = cm.max() / 2.0 if cm.size else 0
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(
                j,
                i,
                format(int(cm[i, j]), fmt),
                ha="center",
                va="center",
                color="white" if cm[i, j] > thresh else "black",
            )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    plt.savefig(output_path)
    plt.close(fig)
    return True


def evaluate_model(model_path: Path, normal_dir: Path, abnormal_dir: Path, test_size: float = 0.2) -> None:
    X, y, _ = build_dataset(normal_dir, abnormal_dir)
    if X.shape[0] == 0:
        print("No scan data found in the dataset directories. Add files to data/raw/normal and data/raw/abnormal.")
        return

    model = load_model(model_path)
    model_name = model_path.name

    stratify = y if len(np.unique(y)) > 1 else None
    if stratify is None:
        print("Not enough classes in dataset for evaluation.")
        return

    _, X_test, _, y_test = train_test_split(
        X, y, test_size=test_size, stratify=stratify, random_state=42
    )

    y_pred = model.predict(X_test)
    accuracy = np.mean(y_pred == y_test)
    report = classification_report(y_test, y_pred, target_names=["normal", "abnormal"], zero_division=0)

    results_dir = model_path.parent.parent / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    report_path = results_dir / "evaluation_report.txt"
    with open(report_path, "w", encoding="utf-8") as fh:
        fh.write("NeuroScan Nepal evaluation report\n")
        fh.write("===============================\n")
        fh.write(f"Model path: {model_path}\n")
        fh.write(f"Test samples: {len(y_test)}\n")
        fh.write(f"Accuracy: {accuracy:.4f}\n")
        fh.write("\nClassification report:\n")
        fh.write(report)

    confusion_image_path = results_dir / "confusion_matrix.png"
    saved = save_confusion_matrix(y_test, y_pred, confusion_image_path)

    print(f"Evaluation completed for model: {model_name}")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Report saved to: {report_path}")
    if saved:
        print(f"Confusion matrix saved to: {confusion_image_path}")
    else:
        print("Matplotlib not installed, skipped confusion matrix generation.")


def parse_args() -> ArgumentParser:
    parser = ArgumentParser(description="Evaluate a trained NeuroScan model")
    parser.add_argument(
        "--model-path",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "models" / "neuroscan_model.pkl",
        help="Path to the trained model file",
    )
    parser.add_argument(
        "--data-root",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "data" / "raw",
        help="Root directory containing raw data folders",
    )
    parser.add_argument(
        "--test-size",
        type=float,
        default=0.2,
        help="Fraction of data to hold out for evaluation",
    )
    return parser


def main() -> None:
    parser = parse_args()
    args = parser.parse_args()
    evaluate_model(
        args.model_path,
        args.data_root / "normal",
        args.data_root / "abnormal",
        test_size=args.test_size,
    )


if __name__ == "__main__":
    main()
