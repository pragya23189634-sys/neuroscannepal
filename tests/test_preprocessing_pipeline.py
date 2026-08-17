from pathlib import Path

import numpy as np
from PIL import Image

from preprocessing import run_preprocessing_pipeline


def create_sample_image(path: Path, base: int) -> None:
    """Create a grayscale image with enough contrast to pass the QC gate."""
    grid = np.linspace(base, min(base + 180, 255), 64, dtype=np.uint8)
    image = np.tile(grid, (64, 1))
    Image.fromarray(image).save(path)


def test_run_preprocessing_pipeline_creates_splits(tmp_path):
    raw_root = tmp_path / "raw"
    normal_dir = raw_root / "normal"
    abnormal_dir = raw_root / "abnormal"
    normal_dir.mkdir(parents=True)
    abnormal_dir.mkdir(parents=True)

    for idx in range(4):
        create_sample_image(normal_dir / f"normal_{idx}.png", 20 + idx * 5)
        create_sample_image(abnormal_dir / f"abnormal_{idx}.png", 40 + idx * 5)

    output_root = tmp_path / "processed"
    report = run_preprocessing_pipeline(
        normal_dir=normal_dir,
        abnormal_dir=abnormal_dir,
        output_root=output_root,
        train_ratio=0.5,
        augment=False,
        random_state=7,
    )

    assert report["summary"]["total_samples"] == 8
    assert report["summary"]["train_total"] >= 2
    assert report["summary"]["test_total"] >= 2
    assert (output_root / "train" / "normal").exists()
    assert (output_root / "train" / "abnormal").exists()
    assert (output_root / "test" / "normal").exists()
    assert (output_root / "test" / "abnormal").exists()
    assert (output_root / "report.txt").exists()
