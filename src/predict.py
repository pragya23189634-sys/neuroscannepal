from argparse import ArgumentParser
from pathlib import Path
import sys

try:
    import numpy as np
except ImportError:  # pragma: no cover
    print("Error: NumPy is required to run predict.py. Install it with `pip install numpy`.")
    sys.exit(1)

from model_utils import load_model
from preprocessing import extract_features, load_scan


def load_model_from_path(model_path: Path):
    return load_model(model_path)


def predict_scan(model_path: Path, scan_path: Path) -> None:
    model = load_model_from_path(model_path)
    scan = load_scan(scan_path)
    features = extract_features(scan).reshape(1, -1)

    prediction = model.predict(features)[0]
    label = "abnormal" if int(prediction) == 1 else "normal"

    print(f"Input scan: {scan_path}")
    print(f"Predicted label: {label}")

    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(features)[0]
        score = float(proba[1] if int(prediction) == 1 else proba[0])
        print(f"Confidence: {score:.4f}")


def parse_args() -> ArgumentParser:
    parser = ArgumentParser(description="Predict neuroscan abnormality from a trained model")
    parser.add_argument(
        "--model-path",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "models" / "neuroscan_model.pkl",
        help="Path to the trained model file",
    )
    parser.add_argument(
        "--scan-path",
        type=Path,
        required=True,
        help="Path to the scan file to classify",
    )
    return parser


def main() -> None:
    parser = parse_args()
    args = parser.parse_args()
    predict_scan(args.model_path, args.scan_path)


if __name__ == "__main__":
    main()
