from pathlib import Path

import numpy as np
import torch
from PIL import Image

from predict import predict_scan
from train_cnn import SimpleCNN


def test_predict_scan_with_cnn_model(tmp_path):
    model_path = tmp_path / "dummy_model.pth"
    image_path = tmp_path / "sample.png"

    torch.manual_seed(7)
    model = SimpleCNN(num_classes=2)
    torch.save(model.state_dict(), model_path)

    image = np.full((64, 64), 120, dtype=np.uint8)
    Image.fromarray(image).save(image_path)

    label, confidence = predict_scan(model_path=model_path, scan_path=image_path)

    assert label in {"normal", "abnormal"}
    assert 0.0 <= confidence <= 1.0
