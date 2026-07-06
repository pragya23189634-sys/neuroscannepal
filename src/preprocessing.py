from pathlib import Path
from typing import List, Tuple

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


def is_supported_path(path: Path) -> bool:
    name = path.name.lower()
    return any(name.endswith(ext) for ext in SUPPORTED_EXTENSIONS)


def list_scan_files(folder: Path) -> List[Path]:
    if not folder.exists():
        return []
    return sorted([path for path in folder.rglob("*") if is_supported_path(path)])


def load_scan(path: Path) -> np.ndarray:
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
        return np.asarray(scan, dtype=np.float32)

    if cv2 is not None:
        image = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
        if image is None:
            raise ValueError(f"Unable to load image: {path}")
        return image.astype(np.float32)

    with Image.open(str(path)) as image_file:
        return np.asarray(image_file.convert("L"), dtype=np.float32)


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
        image = load_scan(path)
        features.append(extract_features(image))
        labels.append(0)
        paths.append(path)

    for path in abnormal_paths:
        image = load_scan(path)
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
