from argparse import ArgumentParser
from pathlib import Path
from typing import List, Tuple
import sys

try:
    import numpy as np
except ImportError:  # pragma: no cover
    print("Error: NumPy is required to run train_cnn.py. Install it with `pip install numpy`.")
    sys.exit(1)

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    print("Error: Pillow is required to run train_cnn.py. Install it with `pip install pillow`.")
    sys.exit(1)

try:
    from sklearn.model_selection import train_test_split
except ImportError:  # pragma: no cover
    print("Error: scikit-learn is required to run train_cnn.py. Install it with `pip install scikit-learn`.")
    sys.exit(1)

from preprocessing import load_scan, list_scan_files

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import DataLoader, Dataset
except ImportError:  # pragma: no cover
    torch = None


IMAGE_SIZE = (128, 128)


class ScanDataset(Dataset):
    def __init__(self, paths: List[Path], labels: List[int], image_size: Tuple[int, int] = IMAGE_SIZE):
        self.paths = paths
        self.labels = labels
        self.image_size = image_size

    def __len__(self) -> int:
        return len(self.paths)

    def __getitem__(self, index: int):
        path = self.paths[index]
        label = self.labels[index]
        scan = load_scan(path)
        tensor = self._prepare_scan(scan)
        return tensor, torch.tensor(label, dtype=torch.long)

    def _prepare_scan(self, scan: np.ndarray) -> torch.Tensor:
        scan = np.nan_to_num(scan, nan=0.0, posinf=0.0, neginf=0.0)
        scan = np.asarray(scan, dtype=np.float32)
        scan = np.clip(scan, 0.0, None)

        if scan.size == 0:
            scan = np.zeros(self.image_size, dtype=np.float32)

        scan = scan - scan.min()
        if scan.max() > 0.0:
            scan = scan / scan.max()

        scan_image = Image.fromarray((scan * 255.0).astype(np.uint8))
        scan_image = scan_image.resize(self.image_size, Image.BILINEAR)
        scan = np.asarray(scan_image, dtype=np.float32) / 255.0
        scan = scan.astype(np.float32)

        if scan.ndim == 2:
            scan = np.expand_dims(scan, axis=0)

        return torch.from_numpy(scan)


class SimpleCNN(nn.Module):
    def __init__(self, num_classes: int = 2):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(1, 16, kernel_size=3, padding=1),
            nn.BatchNorm2d(16),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            nn.Conv2d(16, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d((4, 4)),
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64 * 4 * 4, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(0.4),
            nn.Linear(128, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.features(x)
        x = self.classifier(x)
        return x


def build_scan_paths(normal_dir: Path, abnormal_dir: Path) -> Tuple[List[Path], List[int]]:
    normal_paths = list_scan_files(normal_dir)
    abnormal_paths = list_scan_files(abnormal_dir)
    paths = normal_paths + abnormal_paths
    labels = [0] * len(normal_paths) + [1] * len(abnormal_paths)
    return paths, labels


def train_cnn(
    normal_dir: Path,
    abnormal_dir: Path,
    model_path: Path,
    results_path: Path,
    epochs: int = 10,
    batch_size: int = 16,
    learning_rate: float = 1e-3,
    test_size: float = 0.2,
    random_state: int = 42,
) -> None:
    if torch is None:
        raise ImportError(
            "PyTorch is required for CNN training. Install it with `pip install torch torchvision`.")

    paths, labels = build_scan_paths(normal_dir, abnormal_dir)
    if len(paths) == 0:
        print("No scan data found in the dataset directories. Add files to data/raw/normal and data/raw/abnormal.")
        return

    if len(set(labels)) < 2:
        print("At least two classes are required for CNN training. Add both normal and abnormal scans.")
        return

    train_paths, val_paths, train_labels, val_labels = train_test_split(
        paths, labels, test_size=test_size, stratify=labels, random_state=random_state
    )

    train_dataset = ScanDataset(train_paths, train_labels)
    val_dataset = ScanDataset(val_paths, val_labels)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = SimpleCNN(num_classes=2).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    for epoch in range(1, epochs + 1):
        model.train()
        train_loss = 0.0
        train_correct = 0
        train_total = 0

        for inputs, targets in train_loader:
            inputs = inputs.to(device)
            targets = targets.to(device)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()

            train_loss += loss.item() * inputs.size(0)
            train_correct += (outputs.argmax(dim=1) == targets).sum().item()
            train_total += inputs.size(0)

        train_loss /= max(train_total, 1)
        train_acc = train_correct / max(train_total, 1)

        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0

        with torch.no_grad():
            for inputs, targets in val_loader:
                inputs = inputs.to(device)
                targets = targets.to(device)
                outputs = model(inputs)
                loss = criterion(outputs, targets)
                val_loss += loss.item() * inputs.size(0)
                val_correct += (outputs.argmax(dim=1) == targets).sum().item()
                val_total += inputs.size(0)

        val_loss /= max(val_total, 1)
        val_acc = val_correct / max(val_total, 1)

        print(
            f"Epoch {epoch}/{epochs}: train_loss={train_loss:.4f}, train_acc={train_acc:.4f}, "
            f"val_loss={val_loss:.4f}, val_acc={val_acc:.4f}"
        )

    model_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), model_path)

    results_path.parent.mkdir(parents=True, exist_ok=True)
    with open(results_path, "w", encoding="utf-8") as fh:
        fh.write("NeuroScan Nepal CNN training report\n")
        fh.write("==============================\n")
        fh.write(f"Model path: {model_path}\n")
        fh.write(f"Train samples: {len(train_labels)}\n")
        fh.write(f"Validation samples: {len(val_labels)}\n")
        fh.write(f"Epochs: {epochs}\n")
        fh.write(f"Batch size: {batch_size}\n")
        fh.write(f"Learning rate: {learning_rate}\n")
        fh.write(f"Final validation accuracy: {val_acc:.4f}\n")

    print("CNN training completed successfully.")
    print(f"Saved model to: {model_path}")
    print(f"Saved report to: {results_path}")


def parse_args() -> ArgumentParser:
    parser = ArgumentParser(description="Train a simple CNN on NeuroScan image data")
    parser.add_argument(
        "--data-root",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "data" / "raw",
        help="Root directory containing raw data folders",
    )
    parser.add_argument(
        "--model-path",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "models" / "neuroscan_cnn.pth",
        help="Path to save the trained CNN model",
    )
    parser.add_argument(
        "--results-path",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "results" / "training_cnn_report.txt",
        help="Path to save the training report",
    )
    parser.add_argument("--epochs", type=int, default=10, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=16, help="Batch size for training")
    parser.add_argument("--learning-rate", type=float, default=1e-3, help="Learning rate")
    parser.add_argument("--test-size", type=float, default=0.2, help="Validation split fraction")
    parser.add_argument("--random-state", type=int, default=42, help="Random seed")
    return parser


def main() -> None:
    parser = parse_args()
    args = parser.parse_args()
    train_cnn(
        normal_dir=args.data_root / "normal",
        abnormal_dir=args.data_root / "abnormal",
        model_path=args.model_path,
        results_path=args.results_path,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        test_size=args.test_size,
        random_state=args.random_state,
    )


if __name__ == "__main__":
    main()
