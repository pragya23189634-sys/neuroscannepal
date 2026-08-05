from argparse import ArgumentParser
from pathlib import Path
from typing import List, Tuple
import random
import sys

try:
    import numpy as np
except ImportError:  # pragma: no cover
    print("Error: NumPy is required to run 03_transfer_learning.py. Install it with `pip install numpy`.")
    sys.exit(1)

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import DataLoader, Dataset
except ImportError:  # pragma: no cover
    print("Error: PyTorch is required to run 03_transfer_learning.py. Install it with `pip install torch torchvision`.")
    sys.exit(1)

try:
    from torchvision import models, transforms
except ImportError:  # pragma: no cover
    print("Error: torchvision is required to run 03_transfer_learning.py. Install it with `pip install torchvision`.")
    sys.exit(1)

try:
    from sklearn.model_selection import train_test_split
except ImportError:  # pragma: no cover
    print("Error: scikit-learn is required to run 03_transfer_learning.py. Install it with `pip install scikit-learn`.")
    sys.exit(1)

from preprocessing import load_scan, list_scan_files
from PIL import Image

IMAGE_SIZE = (224, 224)
MEAN = [0.485, 0.485, 0.485]
STD = [0.229, 0.229, 0.229]


class TransferLearningDataset(Dataset):
    def __init__(
        self,
        paths: List[Path],
        labels: List[int],
        image_size: Tuple[int, int] = IMAGE_SIZE,
        augment: bool = False,
        seed: int = 42,
    ) -> None:
        self.paths = paths
        self.labels = labels
        self.image_size = image_size
        self.augment = augment
        self.seed = seed
        self.transform = self._build_transform(augment)

    def _build_transform(self, augment: bool) -> transforms.Compose:
        pipeline = []
        if augment:
            pipeline.extend([
                transforms.RandomHorizontalFlip(p=0.5),
                transforms.RandomVerticalFlip(p=0.5),
                transforms.RandomRotation(15),
            ])
        pipeline.extend([
            transforms.Resize(self.image_size),
            transforms.ToTensor(),
            transforms.Normalize(mean=MEAN, std=STD),
        ])
        return transforms.Compose(pipeline)

    def __len__(self) -> int:
        return len(self.paths)

    def __getitem__(self, index: int):
        path = self.paths[index]
        label = self.labels[index]
        scan = load_scan(path, use_clahe=True)
        scan = self._prepare_image(scan)
        image = Image.fromarray(scan, mode="L").convert("RGB")
        tensor = self.transform(image)
        return tensor, torch.tensor(label, dtype=torch.long)

    def _prepare_image(self, scan: np.ndarray) -> np.ndarray:
        scan = np.nan_to_num(scan, nan=0.0, posinf=0.0, neginf=0.0)
        scan = scan.astype(np.float32)
        scan = np.clip(scan, 0.0, None)

        if scan.size == 0:
            scan = np.zeros(self.image_size, dtype=np.float32)

        scan = scan - scan.min()
        max_val = scan.max()
        if max_val > 0.0:
            scan = scan / max_val
        scan = np.clip(scan * 255.0, 0, 255).astype(np.uint8)
        return scan


def build_scan_paths(normal_dir: Path, abnormal_dir: Path) -> Tuple[List[Path], List[int]]:
    normal_paths = list_scan_files(normal_dir)
    abnormal_paths = list_scan_files(abnormal_dir)
    labels = [0] * len(normal_paths) + [1] * len(abnormal_paths)
    return normal_paths + abnormal_paths, labels


def create_model(arch: str, num_classes: int = 2, freeze_backbone: bool = True) -> nn.Module:
    arch = arch.lower()
    if arch == "vgg16":
        model = models.vgg16(weights=models.VGG16_Weights.IMAGENET1K_V1)
        in_features = model.classifier[6].in_features
        model.classifier[6] = nn.Linear(in_features, num_classes)
    elif arch == "efficientnetb0" or arch == "efficientnet_b0":
        model = models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.IMAGENET1K_V1)
        in_features = model.classifier[1].in_features
        model.classifier[1] = nn.Linear(in_features, num_classes)
    else:
        raise ValueError(f"Unsupported architecture: {arch}. Use 'vgg16' or 'efficientnetb0'.")

    if freeze_backbone:
        for name, param in model.named_parameters():
            if not any(key in name for key in ["classifier", "head", "fc"]):
                param.requires_grad = False

    return model


def train_transfer_learning(
    normal_dir: Path,
    abnormal_dir: Path,
    model_path: Path,
    results_path: Path,
    arch: str = "vgg16",
    epochs: int = 10,
    batch_size: int = 16,
    learning_rate: float = 1e-4,
    test_size: float = 0.2,
    random_state: int = 42,
    augment: bool = True,
    freeze_backbone: bool = True,
) -> None:
    paths, labels = build_scan_paths(normal_dir, abnormal_dir)
    if len(paths) == 0:
        print("No scan data found in the dataset directories. Add files to data/raw/normal and data/raw/abnormal.")
        return

    if len(set(labels)) < 2:
        print("At least two classes are required for transfer learning. Add both normal and abnormal scans.")
        return

    train_paths, val_paths, train_labels, val_labels = train_test_split(
        paths,
        labels,
        test_size=test_size,
        stratify=labels,
        random_state=random_state,
    )

    train_dataset = TransferLearningDataset(train_paths, train_labels, augment=augment, seed=random_state)
    val_dataset = TransferLearningDataset(val_paths, val_labels, augment=False, seed=random_state)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=2, pin_memory=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=2, pin_memory=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = create_model(arch, num_classes=2, freeze_backbone=freeze_backbone).to(device)
    optimizer = optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=learning_rate)
    criterion = nn.CrossEntropyLoss()

    best_val_acc = 0.0
    model_path.parent.mkdir(parents=True, exist_ok=True)
    results_path.parent.mkdir(parents=True, exist_ok=True)

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

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), model_path)

    with open(results_path, "w", encoding="utf-8") as fh:
        fh.write("NeuroScan Nepal transfer learning report\n")
        fh.write("====================================\n")
        fh.write(f"Model architecture: {arch}\n")
        fh.write(f"Use augmentation: {augment}\n")
        fh.write(f"Freeze backbone: {freeze_backbone}\n")
        fh.write(f"Train samples: {len(train_labels)}\n")
        fh.write(f"Validation samples: {len(val_labels)}\n")
        fh.write(f"Epochs: {epochs}\n")
        fh.write(f"Batch size: {batch_size}\n")
        fh.write(f"Learning rate: {learning_rate}\n")
        fh.write(f"Best validation accuracy: {best_val_acc:.4f}\n")

    print(f"Best validation accuracy: {best_val_acc:.4f}")
    print(f"Saved best model to: {model_path}")
    print(f"Saved report to: {results_path}")


def parse_args() -> ArgumentParser:
    parser = ArgumentParser(description="Train a transfer learning model for NeuroScan classification")
    parser.add_argument(
        "--data-root",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "data" / "raw",
        help="Root directory containing raw data folders",
    )
    parser.add_argument(
        "--arch",
        type=str,
        default="vgg16",
        choices=["vgg16", "efficientnetb0"],
        help="Backbone architecture to train",
    )
    parser.add_argument(
        "--model-path",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "models" / "transfer_learning_model.pth",
        help="Path to save the trained transfer learning model",
    )
    parser.add_argument(
        "--results-path",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "results" / "transfer_learning_report.txt",
        help="Path to save the training report",
    )
    parser.add_argument("--epochs", type=int, default=10, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=16, help="Batch size")
    parser.add_argument("--learning-rate", type=float, default=1e-4, help="Learning rate")
    parser.add_argument("--test-size", type=float, default=0.2, help="Validation split fraction")
    parser.add_argument("--random-state", type=int, default=42, help="Random seed")
    parser.add_argument("--no-augment", action="store_true", help="Disable training augmentation")
    parser.add_argument("--no-freeze", action="store_true", help="Do not freeze backbone parameters")
    return parser


def main() -> None:
    parser = parse_args()
    args = parser.parse_args()
    train_transfer_learning(
        normal_dir=args.data_root / "normal",
        abnormal_dir=args.data_root / "abnormal",
        model_path=args.model_path,
        results_path=args.results_path,
        arch=args.arch,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        test_size=args.test_size,
        random_state=args.random_state,
        augment=not args.no_augment,
        freeze_backbone=not args.no_freeze,
    )


if __name__ == "__main__":
    main()
