"""Shared dataset helpers for faster CNN training."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Tuple
import random

import numpy as np
import torch
from PIL import Image
from torch.utils.data import DataLoader, Dataset

from preprocessing import load_scan, list_scan_files

IMAGE_SIZE = (128, 128)


def dataloader_kwargs(batch_size: int, shuffle: bool, device: torch.device) -> Dict[str, Any]:
    use_cuda = device.type == "cuda"
    worker_count = 0 if device.type == "cpu" else min(4, max(1, (torch.get_num_threads() or 4) // 2))
    return {
        "batch_size": batch_size,
        "shuffle": shuffle,
        "num_workers": worker_count,
        "pin_memory": use_cuda,
        "persistent_workers": worker_count > 0,
    }


def build_scan_paths(normal_dir: Path, abnormal_dir: Path) -> Tuple[List[Path], List[int]]:
    normal_paths = list_scan_files(normal_dir)
    abnormal_paths = list_scan_files(abnormal_dir)
    labels = [0] * len(normal_paths) + [1] * len(abnormal_paths)
    return normal_paths + abnormal_paths, labels


def build_processed_paths(processed_root: Path) -> Tuple[List[Path], List[int]]:
    train_root = processed_root / "train"
    test_root = processed_root / "test"
    train_paths, train_labels = build_scan_paths(train_root / "normal", train_root / "abnormal")
    test_paths, test_labels = build_scan_paths(test_root / "normal", test_root / "abnormal")
    paths = train_paths + test_paths
    labels = train_labels + test_labels
    return paths, labels


def _normalize_scan(scan: np.ndarray) -> np.ndarray:
    scan = np.nan_to_num(scan, nan=0.0, posinf=0.0, neginf=0.0)
    scan = scan.astype(np.float32)
    scan = np.clip(scan, 0.0, None)
    if scan.size == 0:
        return np.zeros(IMAGE_SIZE, dtype=np.float32)

    scan = scan - scan.min()
    max_val = scan.max()
    if max_val > 0.0:
        scan = scan / max_val
    return scan


def _resize_scan(scan: np.ndarray, image_size: Tuple[int, int] = IMAGE_SIZE) -> np.ndarray:
    pil = Image.fromarray((scan * 255.0).astype(np.uint8), mode="L")
    pil = pil.resize(image_size, Image.BILINEAR)
    return np.asarray(pil, dtype=np.float32) / 255.0


def _augment_scan(scan: np.ndarray, index: int, seed: int) -> np.ndarray:
    rng = random.Random(seed + index)

    if rng.random() < 0.5:
        scan = np.fliplr(scan)
    if rng.random() < 0.5:
        scan = np.flipud(scan)
    if rng.random() < 0.5:
        scan = np.rot90(scan, k=rng.choice([0, 1, 2, 3]))
    if rng.random() < 0.4:
        scan = scan + rng.normalvariate(0.0, 0.02)
        scan = np.clip(scan, 0.0, 1.0)
    return scan


def _prepare_tensor(scan: np.ndarray) -> torch.Tensor:
    return torch.from_numpy(np.ascontiguousarray(scan)).unsqueeze(0).float()


class ScanImageDataset(Dataset):
    """Loads and preprocesses scans on every access (slow for repeated epochs)."""

    def __init__(
        self,
        paths: List[Path],
        labels: List[int],
        image_size: Tuple[int, int] = IMAGE_SIZE,
        augment: bool = False,
        seed: int = 42,
        use_clahe: bool = True,
    ) -> None:
        self.paths = paths
        self.labels = labels
        self.image_size = image_size
        self.augment = augment
        self.seed = seed
        self.use_clahe = use_clahe

    def __len__(self) -> int:
        return len(self.paths)

    def __getitem__(self, index: int):
        path = self.paths[index]
        label = self.labels[index]
        scan = load_scan(path, use_clahe=self.use_clahe)
        scan = _normalize_scan(scan)
        if self.augment:
            scan = _augment_scan(scan, index, self.seed)
        scan = _resize_scan(scan, self.image_size)
        return _prepare_tensor(scan), torch.tensor(label, dtype=torch.long)


class CachedScanDataset(Dataset):
    """Preloads scans once into memory; augmentation stays cheap per epoch."""

    def __init__(
        self,
        paths: List[Path],
        labels: List[int],
        image_size: Tuple[int, int] = IMAGE_SIZE,
        augment: bool = False,
        seed: int = 42,
        use_clahe: bool = True,
    ) -> None:
        self.labels = labels
        self.image_size = image_size
        self.augment = augment
        self.seed = seed
        self.scans: List[np.ndarray] = []

        total = len(paths)
        for index, path in enumerate(paths):
            scan = load_scan(path, use_clahe=use_clahe)
            scan = _normalize_scan(scan)
            scan = _resize_scan(scan, image_size)
            self.scans.append(scan)
            if total >= 100 and (index + 1) % max(1, total // 10) == 0:
                print(f"  Cached {index + 1}/{total} scans...")

    def __len__(self) -> int:
        return len(self.scans)

    def __getitem__(self, index: int):
        scan = self.scans[index].copy()
        if self.augment:
            scan = _augment_scan(scan, index, self.seed)
        return _prepare_tensor(scan), torch.tensor(self.labels[index], dtype=torch.long)


def make_loaders(
    train_paths: List[Path],
    train_labels: List[int],
    val_paths: List[Path],
    val_labels: List[int],
    batch_size: int,
    device: torch.device,
    augment: bool = True,
    seed: int = 42,
    cache: bool = True,
    use_clahe: bool = True,
) -> Tuple[DataLoader, DataLoader]:
    dataset_cls = CachedScanDataset if cache else ScanImageDataset

    if cache:
        print("Preloading training scans into memory (one-time step)...")
    train_dataset = dataset_cls(
        train_paths, train_labels, augment=augment, seed=seed, use_clahe=use_clahe
    )

    if cache:
        print("Preloading validation scans into memory...")
    val_dataset = dataset_cls(
        val_paths, val_labels, augment=False, seed=seed, use_clahe=use_clahe
    )

    train_loader = DataLoader(
        train_dataset,
        **dataloader_kwargs(batch_size, shuffle=True, device=device),
    )
    val_loader = DataLoader(
        val_dataset,
        **dataloader_kwargs(batch_size, shuffle=False, device=device),
    )
    return train_loader, val_loader
