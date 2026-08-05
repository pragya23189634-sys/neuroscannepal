from pathlib import Path
from typing import Any, Dict, List, Tuple
import random

try:
    from PIL import Image
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "Pillow is required for image loading. Install it with `pip install pillow`."
    ) from exc

try:
    import nibabel as nib
except ImportError:  # pragma: no cover
    nib = None

try:
    import numpy as np
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "NumPy is required for preprocessing. Install it with `pip install numpy`."
    ) from exc

try:
    import cv2
except ImportError:  # pragma: no cover
    cv2 = None

SUPPORTED_EXTENSIONS = {".nii", ".nii.gz", ".png", ".jpg", ".jpeg", ".bmp"}


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def is_supported_path(path: Path) -> bool:
    name = path.name.lower()
    return any(name.endswith(ext) for ext in SUPPORTED_EXTENSIONS)


def list_scan_files(folder: Path) -> List[Path]:
    if not folder.exists():
        return []
    return sorted([path for path in folder.rglob("*") if is_supported_path(path)])


def apply_clahe_to_image(image: np.ndarray, clip_limit: float = 2.0, tile_grid_size: Tuple[int, int] = (8, 8)) -> np.ndarray:
    image = np.asarray(image, dtype=np.float32)
    if image.size == 0:
        return image

    if cv2 is not None:
        image_uint8 = np.clip(image, 0.0, 255.0).astype(np.uint8)
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
        return clahe.apply(image_uint8).astype(np.float32)

    try:
        from PIL import ImageOps
    except ImportError:
        return image

    image_uint8 = np.clip(image, 0.0, 255.0).astype(np.uint8)
    pil_image = Image.fromarray(image_uint8, mode="L")
    equalized = ImageOps.equalize(pil_image)
    return np.asarray(equalized, dtype=np.float32)


def load_scan(
    path: Path,
    use_clahe: bool = False,
    clip_limit: float = 2.0,
    tile_grid_size: Tuple[int, int] = (8, 8),
) -> np.ndarray:
    name = path.name.lower()
    if name.endswith(".nii") or name.endswith(".nii.gz"):
        if nib is None:
            raise ImportError(
                "Nibabel is required to load NIfTI files (.nii, .nii.gz). "
                "Install it with `pip install nibabel` or use image files like .png/.jpg instead."
            )
        scan = nib.load(str(path)).get_fdata(dtype=np.float32)
        if scan.ndim == 3:
            scan = scan[:, :, scan.shape[2] // 2]
        elif scan.ndim == 4:
            scan = scan[:, :, scan.shape[2] // 2, 0]
        if use_clahe:
            scan = apply_clahe_to_image(scan, clip_limit, tile_grid_size)
        return np.asarray(scan, dtype=np.float32)

    if cv2 is not None:
        image = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
        if image is not None:
            scan = image.astype(np.float32)
            if use_clahe:
                scan = apply_clahe_to_image(scan, clip_limit, tile_grid_size)
            return scan
        # If OpenCV fails, fall back to Pillow for more robust image loading.

    try:
        with Image.open(str(path)) as image_file:
            scan = np.asarray(image_file.convert("L"), dtype=np.float32)
            if use_clahe:
                scan = apply_clahe_to_image(scan, clip_limit, tile_grid_size)
            return scan
    except (OSError, ValueError) as exc:
        raise ValueError(f"Unable to load image: {path}") from exc


def extract_features(image: np.ndarray) -> np.ndarray:
    image = image.astype(np.float32)
    image = image[np.isfinite(image)]
    if image.size == 0:
        return np.zeros(8, dtype=np.float32)

    values = np.clip(image, a_min=0.0, a_max=None)
    percentiles = np.percentile(values, [0, 10, 25, 50, 75, 90, 100])
    return np.array([
        np.mean(values),
        np.std(values),
        np.min(values),
        np.max(values),
        percentiles[1],
        percentiles[3],
        percentiles[5],
        np.median(values),
    ], dtype=np.float32)


def build_dataset(normal_dir: Path, abnormal_dir: Path) -> Tuple[np.ndarray, np.ndarray, List[Path]]:
    normal_paths = list_scan_files(normal_dir)
    abnormal_paths = list_scan_files(abnormal_dir)

    features: List[np.ndarray] = []
    labels: List[int] = []
    paths: List[Path] = []

    for path in normal_paths:
        image = load_scan(path, use_clahe=True)
        features.append(extract_features(image))
        labels.append(0)
        paths.append(path)

    for path in abnormal_paths:
        image = load_scan(path, use_clahe=True)
        features.append(extract_features(image))
        labels.append(1)
        paths.append(path)

    if not features:
        return np.empty((0, 8), dtype=np.float32), np.empty((0,), dtype=np.int64), []

    return np.vstack(features), np.array(labels, dtype=np.int64), paths


def summarize_dataset(normal_dir: Path, abnormal_dir: Path) -> None:
    normal_paths = list_scan_files(normal_dir)
    abnormal_paths = list_scan_files(abnormal_dir)

    print("NeuroScan Nepal dataset summary")
    print("----------------------------")
    print(f"Normal samples:   {len(normal_paths)}")
    print(f"Abnormal samples: {len(abnormal_paths)}")
    print("Supported extensions:", ", ".join(sorted(SUPPORTED_EXTENSIONS)))

    if normal_paths:
        print(f"Sample normal file:   {normal_paths[0]}")
    if abnormal_paths:
        print(f"Sample abnormal file: {abnormal_paths[0]}")


def _apply_basic_augmentation(image: np.ndarray, seed: int) -> np.ndarray:
    if image.size == 0:
        return image

    rng = np.random.default_rng(seed)
    augmented = image.astype(np.float32)
    if augmented.ndim != 2:
        return augmented

    if rng.random() > 0.5:
        augmented = np.fliplr(augmented)
    if rng.random() > 0.5:
        augmented = np.rot90(augmented, k=1)
    return augmented


def _save_preprocessed_image(image: np.ndarray, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    clipped = np.clip(image, 0.0, 255.0).astype(np.uint8)
    Image.fromarray(clipped).save(output_path)


def is_low_contrast(image: np.ndarray, contrast_threshold: float = 0.05) -> bool:
    """Simple low-contrast check.

    Computes a normalized dynamic range using percentiles. Returns True if below threshold.
    """
    if image.size == 0:
        return True
    vals = image.astype(np.float32)
    p2 = np.percentile(vals, 2)
    p98 = np.percentile(vals, 98)
    dynamic = float(p98 - p2)
    # Normalize by the 99th percentile to handle different acquisition scales
    denom = float(max(1.0, np.percentile(vals, 99)))
    norm = dynamic / denom
    return norm < contrast_threshold


def run_preprocessing_pipeline(
    normal_dir: Path,
    abnormal_dir: Path,
    output_root: Path | None = None,
    train_ratio: float = 0.8,
    augment: bool = True,
    random_state: int = 42,
) -> Dict[str, Any]:
    if not 0 < train_ratio < 1:
        raise ValueError("train_ratio must be between 0 and 1")

    if output_root is None:
        output_root = Path(__file__).resolve().parent.parent / "data" / "processed"
    output_root = Path(output_root)

    train_root = output_root / "train"
    test_root = output_root / "test"
    for folder in [train_root / "normal", train_root / "abnormal", test_root / "normal", test_root / "abnormal"]:
        _ensure_dir(folder)

    normal_paths = list_scan_files(normal_dir)
    abnormal_paths = list_scan_files(abnormal_dir)
    if not normal_paths or not abnormal_paths:
        raise ValueError("Both normal and abnormal folders must contain supported scan files")

    rng = random.Random(random_state)
    normal_paths = sorted(normal_paths)
    abnormal_paths = sorted(abnormal_paths)
    rng.shuffle(normal_paths)
    rng.shuffle(abnormal_paths)

    train_normal_count = max(1, int(len(normal_paths) * train_ratio))
    train_abnormal_count = max(1, int(len(abnormal_paths) * train_ratio))

    train_normal_paths = normal_paths[:train_normal_count]
    train_abnormal_paths = abnormal_paths[:train_abnormal_count]
    test_normal_paths = normal_paths[train_normal_count:]
    test_abnormal_paths = abnormal_paths[train_abnormal_count:]

    def process_and_save(paths: List[Path], target_dir: Path, label: str, seed_offset: int) -> int:
        saved = 0
        for idx, path in enumerate(paths):
            image = load_scan(path, use_clahe=True)
            if image.ndim != 2:
                image = np.mean(image, axis=-1)

            # Quality check: low contrast images are moved to a separate folder
            if is_low_contrast(image):
                lowq_dir = output_root / "low_quality"
                _ensure_dir(lowq_dir)
                lowq_path = lowq_dir / f"{label}_{idx + 1}_{path.name}"
                _save_preprocessed_image(image, lowq_path)
                continue

            if augment and idx % 2 == 0:
                image = _apply_basic_augmentation(image, seed=seed_offset + idx)
            output_path = target_dir / f"{label}_{idx + 1}.png"
            _save_preprocessed_image(image, output_path)
            saved += 1
        return saved

    train_normal_saved = process_and_save(train_normal_paths, train_root / "normal", "normal", 100)
    train_abnormal_saved = process_and_save(train_abnormal_paths, train_root / "abnormal", "abnormal", 200)
    test_normal_saved = process_and_save(test_normal_paths, test_root / "normal", "normal", 300)
    test_abnormal_saved = process_and_save(test_abnormal_paths, test_root / "abnormal", "abnormal", 400)

    summary = {
        "total_samples": len(normal_paths) + len(abnormal_paths),
        "normal_total": len(normal_paths),
        "abnormal_total": len(abnormal_paths),
        "train_total": train_normal_saved + train_abnormal_saved,
        "test_total": test_normal_saved + test_abnormal_saved,
        "train_normal": train_normal_saved,
        "train_abnormal": train_abnormal_saved,
        "test_normal": test_normal_saved,
        "test_abnormal": test_abnormal_saved,
        "class_balance": {
            "train": {
                "normal": train_normal_saved,
                "abnormal": train_abnormal_saved,
            },
            "test": {
                "normal": test_normal_saved,
                "abnormal": test_abnormal_saved,
            },
        },
    }

    report_path = output_root / "report.txt"
    lines = [
        "NeuroScan Nepal preprocessing report",
        "==================================",
        f"Total samples: {summary['total_samples']}",
        f"Normal samples: {summary['normal_total']}",
        f"Abnormal samples: {summary['abnormal_total']}",
        f"Train samples: {summary['train_total']}",
        f"Test samples: {summary['test_total']}",
        "Class balance:",
        f"- Train normal: {summary['class_balance']['train']['normal']}",
        f"- Train abnormal: {summary['class_balance']['train']['abnormal']}",
        f"- Test normal: {summary['class_balance']['test']['normal']}",
        f"- Test abnormal: {summary['class_balance']['test']['abnormal']}",
    ]
    report_path.write_text("\n".join(lines), encoding="utf-8")

    print("Preprocessing pipeline completed.")
    print(f"Output root: {output_root}")
    print(f"Train samples: {summary['train_total']}")
    print(f"Test samples: {summary['test_total']}")
    return {"output_root": str(output_root), "summary": summary, "report_path": str(report_path)}
