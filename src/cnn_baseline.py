from argparse import ArgumentParser
from pathlib import Path
import os
import sys

try:
    import numpy as np
except ImportError:  # pragma: no cover
    print("Error: NumPy is required to run 02_cnn_baseline.py. Install it with `pip install numpy`.")
    sys.exit(1)

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import DataLoader
except ImportError:  # pragma: no cover
    print("Error: PyTorch is required to run 02_cnn_baseline.py. Install it with `pip install torch torchvision`.")
    sys.exit(1)

try:
    from sklearn.model_selection import train_test_split
except ImportError:  # pragma: no cover
    print("Error: scikit-learn is required to run 02_cnn_baseline.py. Install it with `pip install scikit-learn`.")
    sys.exit(1)

try:
    import matplotlib.pyplot as plt
except ImportError:  # pragma: no cover
    plt = None

from dataset_utils import build_scan_paths, make_loaders


class BaselineCNN(nn.Module):
    def __init__(self, num_classes: int = 2) -> None:
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d((4, 4)),
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(128 * 4 * 4, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(0.4),
            nn.Linear(256, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.features(x)
        x = self.classifier(x)
        return x


def train_baseline_cnn(
    normal_dir: Path,
    abnormal_dir: Path,
    model_path: Path,
    results_path: Path,
    epochs: int = 15,
    batch_size: int = 32,
    learning_rate: float = 1e-3,
    test_size: float = 0.2,
    random_state: int = 42,
    augment: bool = True,
    cache: bool = True,
    use_clahe: bool = True,
    processed_root: Path | None = None,
) -> None:
    if processed_root is not None and processed_root.exists():
        train_paths, train_labels = build_scan_paths(
            processed_root / "train" / "normal",
            processed_root / "train" / "abnormal",
        )
        val_paths, val_labels = build_scan_paths(
            processed_root / "test" / "normal",
            processed_root / "test" / "abnormal",
        )
        use_clahe = False
        print(f"Using preprocessed data from: {processed_root}")
    else:
        paths, labels = build_scan_paths(normal_dir, abnormal_dir)
        if len(paths) == 0:
            print("No scan data found in the dataset directories. Add files to data/raw/normal and data/raw/abnormal.")
            return

        if len(set(labels)) < 2:
            print("At least two classes are required for training. Add both normal and abnormal scans.")
            return

        train_paths, val_paths, train_labels, val_labels = train_test_split(
            paths,
            labels,
            test_size=test_size,
            stratify=labels,
            random_state=random_state,
        )

    if len(train_paths) == 0 or len(val_paths) == 0:
        print("Training or validation split is empty. Check your dataset folders.")
        return

    if len(set(train_labels)) < 2 or len(set(val_labels)) < 2:
        print("Both classes must appear in train and validation splits.")
        return

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training on: {device}")
    if device.type == "cpu":
        torch.set_num_threads(max(1, (os.cpu_count() or 4) - 1))
        print(f"CPU threads: {torch.get_num_threads()}")

    train_loader, val_loader = make_loaders(
        train_paths,
        train_labels,
        val_paths,
        val_labels,
        batch_size=batch_size,
        device=device,
        augment=augment,
        seed=random_state,
        cache=cache,
        use_clahe=use_clahe,
    )
    model = BaselineCNN(num_classes=2).to(device)
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    criterion = nn.CrossEntropyLoss()

    best_val_accuracy = 0.0
    model_path.parent.mkdir(parents=True, exist_ok=True)
    results_path.parent.mkdir(parents=True, exist_ok=True)

    train_losses = []
    train_accuracies = []
    val_losses = []
    val_accuracies = []

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
        train_losses.append(train_loss)
        train_accuracies.append(train_acc)

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
        val_losses.append(val_loss)
        val_accuracies.append(val_acc)

        print(
            f"Epoch {epoch}/{epochs}: train_loss={train_loss:.4f}, train_acc={train_acc:.4f}, "
            f"val_loss={val_loss:.4f}, val_acc={val_acc:.4f}"
        )

        if val_acc > best_val_accuracy:
            best_val_accuracy = val_acc
            torch.save(model.state_dict(), model_path)

    if plt is not None:
        fig, axes = plt.subplots(1, 2, figsize=(10, 4))
        axes[0].plot(range(1, len(train_losses) + 1), train_losses, label="train loss")
        axes[0].plot(range(1, len(val_losses) + 1), val_losses, label="val loss")
        axes[0].set_title("Loss curves")
        axes[0].set_xlabel("Epoch")
        axes[0].set_ylabel("Loss")
        axes[0].legend()

        axes[1].plot(range(1, len(train_accuracies) + 1), train_accuracies, label="train acc")
        axes[1].plot(range(1, len(val_accuracies) + 1), val_accuracies, label="val acc")
        axes[1].set_title("Accuracy curves")
        axes[1].set_xlabel("Epoch")
        axes[1].set_ylabel("Accuracy")
        axes[1].legend()

        fig.tight_layout()
        curve_path = results_path.parent / "training_curves.png"
        fig.savefig(curve_path, dpi=150)
        print(f"Saved training curves to: {curve_path}")

    report_path = results_path.parent / "preprocessing_decisions.txt"
    report_path.write_text(
        "NeuroScan Nepal preprocessing decisions\n"
        "====================================\n"
        "- CLAHE was applied to improve contrast across MRI scans collected under different acquisition settings.\n"
        "- All images were resized to 224x224 pixels to align with common CNN backbone input requirements.\n"
        "- Data augmentation was applied with horizontal flip, random rotation, brightness variation, zoom, width shift, and height shift.\n"
        "- The normal class was expanded to improve class balance and reduce model bias toward the majority class.\n"
        "- The final dataset used an 80:20 train/test split with balanced class representation.\n",
        encoding="utf-8",
    )

    with open(results_path, "w", encoding="utf-8") as fh:
        fh.write("NeuroScan Nepal CNN baseline training report\n")
        fh.write("=======================================\n")
        fh.write(f"Model path: {model_path}\n")
        fh.write(f"Train samples: {len(train_labels)}\n")
        fh.write(f"Validation samples: {len(val_labels)}\n")
        fh.write(f"Epochs: {epochs}\n")
        fh.write(f"Batch size: {batch_size}\n")
        fh.write(f"Learning rate: {learning_rate}\n")
        fh.write(f"Best validation accuracy: {best_val_accuracy:.4f}\n")

    print(f"Best validation accuracy: {best_val_accuracy:.4f}")
    print(f"Saved best model to: {model_path}")
    print(f"Saved report to: {results_path}")


def parse_args() -> ArgumentParser:
    parser = ArgumentParser(description="Train a baseline CNN for NeuroScan classification")
    parser.add_argument(
        "--data-root",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "data" / "raw",
        help="Root directory containing raw normal and abnormal folders",
    )
    parser.add_argument(
        "--model-path",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "models" / "cnn_baseline.pth",
        help="Path to save the trained CNN model",
    )
    parser.add_argument(
        "--results-path",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "results" / "cnn_baseline_report.txt",
        help="Path to save the training report",
    )
    parser.add_argument("--epochs", type=int, default=10, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size")
    parser.add_argument("--learning-rate", type=float, default=1e-3, help="Learning rate")
    parser.add_argument("--test-size", type=float, default=0.2, help="Validation split fraction (raw data only)")
    parser.add_argument("--random-state", type=int, default=42, help="Random seed")
    parser.add_argument("--no-augment", action="store_true", help="Disable training data augmentation")
    parser.add_argument("--no-cache", action="store_true", help="Load images from disk every epoch (slower)")
    parser.add_argument(
        "--processed-root",
        type=Path,
        default=None,
        help="Use preprocessed PNGs from data/processed (skips CLAHE, much faster)",
    )
    parser.add_argument("--no-clahe", action="store_true", help="Skip CLAHE when loading raw images")
    return parser


def main() -> None:
    parser = parse_args()
    args = parser.parse_args()
    processed_root = args.processed_root
    if processed_root is None:
        default_processed = Path(__file__).resolve().parent.parent / "data" / "processed"
        if (default_processed / "train" / "normal").exists():
            processed_root = default_processed

    train_baseline_cnn(
        normal_dir=args.data_root / "normal",
        abnormal_dir=args.data_root / "abnormal",
        model_path=args.model_path,
        results_path=args.results_path,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        test_size=args.test_size,
        random_state=args.random_state,
        augment=not args.no_augment,
        cache=not args.no_cache,
        use_clahe=not args.no_clahe,
        processed_root=processed_root,
    )


if __name__ == "__main__":
    main()
