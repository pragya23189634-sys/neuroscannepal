from argparse import ArgumentParser
from pathlib import Path
import sys

try:
    import numpy as np
except ImportError:  # pragma: no cover
    print("Error: NumPy is required to run predict.py. Install it with `pip install numpy`.")
    sys.exit(1)

try:
    import torch
except ImportError:  # pragma: no cover
    torch = None

from preprocessing import load_scan
from train_cnn import SimpleCNN


def _prepare_scan(scan: np.ndarray, image_size: tuple[int, int] = (128, 128)):
    scan = np.nan_to_num(scan, nan=0.0, posinf=0.0, neginf=0.0)
    scan = np.asarray(scan, dtype=np.float32)
    scan = np.clip(scan, 0.0, None)

    if scan.size == 0:
        scan = np.zeros(image_size, dtype=np.float32)

    scan = scan - scan.min()
    if scan.max() > 0.0:
        scan = scan / scan.max()

    from PIL import Image as PILImage

    scan_image = PILImage.fromarray((scan * 255.0).astype(np.uint8))
    scan_image = scan_image.resize(image_size, PILImage.BILINEAR)
    scan = np.asarray(scan_image, dtype=np.float32) / 255.0
    if scan.ndim == 2:
        scan = np.expand_dims(scan, axis=0)
    return torch.from_numpy(scan).unsqueeze(0) if torch is not None else scan


def predict_scan(model_path: Path, scan_path: Path):
    if torch is None:
        raise ImportError("PyTorch is required for CNN prediction. Install it with `pip install torch torchvision`.")

    model = SimpleCNN(num_classes=2)
    state = torch.load(model_path, map_location="cpu")
    model.load_state_dict(state)
    model.eval()

    scan = load_scan(scan_path, use_clahe=True)
    tensor = _prepare_scan(scan)
    with torch.no_grad():
        outputs = model(tensor)
        probs = torch.softmax(outputs, dim=1)[0]
        predicted_index = int(torch.argmax(probs).item())
        confidence = float(probs[predicted_index].item())

    label = "abnormal" if predicted_index == 1 else "normal"
    print(f"Input scan: {scan_path}")
    print(f"Predicted label: {label}")
    print(f"Confidence: {confidence:.4f}")
    return label, confidence


def parse_args() -> ArgumentParser:
    parser = ArgumentParser(description="Predict neuroscan abnormality from a trained model")
    parser.add_argument(
        "--model-path",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "models" / "neuroscan_cnn.pth",
        help="Path to the trained CNN model file",
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
