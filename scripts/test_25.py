#!/usr/bin/env python3
"""Run a 25-image test through preprocessing + model inference and report accuracy.

Selects up to 25 images from data/raw/normal and data/raw/abnormal (balanced), applies preprocessing (CLAHE + QC), runs the baseline CNN, and saves a JSON report.
"""
from pathlib import Path
import random
import json
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'src'))

from preprocessing import load_scan, list_scan_files, is_low_contrast
from cnn_baseline import BaselineCNN, IMAGE_SIZE

import numpy as np
import torch

# Config
DATA_ROOT = ROOT / 'data' / 'raw'
NORMAL_DIR = DATA_ROOT / 'normal'
ABNORMAL_DIR = DATA_ROOT / 'abnormal'
MODEL_PATH = ROOT / 'models' / 'cnn_baseline.pth'
OUTPUT = ROOT / 'results' / 'test_25_results.json'

random.seed(42)

normal_paths = list_scan_files(NORMAL_DIR)
abnormal_paths = list_scan_files(ABNORMAL_DIR)

if not normal_paths or not abnormal_paths:
    print('No data found in data/raw/normal and data/raw/abnormal')
    raise SystemExit(1)

# pick up to 13 normal and 12 abnormal (or balanced if fewer available)
num = 25
n_norm = min(len(normal_paths), num // 2 + num % 2)
n_abn = min(len(abnormal_paths), num - n_norm)

sample_norm = random.sample(normal_paths, n_norm)
sample_abn = random.sample(abnormal_paths, n_abn)

samples = [(p, 0) for p in sample_norm] + [(p, 1) for p in sample_abn]
random.shuffle(samples)

# Load model
device = torch.device('cpu')
model = BaselineCNN(num_classes=2)
if MODEL_PATH.exists():
    try:
        model.load_state_dict(torch.load(MODEL_PATH, map_location='cpu'))
        print(f'Loaded model from {MODEL_PATH}')
    except Exception as e:
        print('Failed to load model:', e)
else:
    print('Model file not found at', MODEL_PATH)

model.eval()

results = []
correct = 0
processed = 0
skipped_lowq = 0

for path, label in samples:
    img = load_scan(path, use_clahe=True)
    if img.ndim != 2:
        img = np.mean(img, axis=-1)
    lowq = is_low_contrast(img)
    if lowq:
        skipped_lowq += 1
        results.append({'path': str(path), 'label': label, 'skipped_low_quality': True})
        continue

    # normalize and resize like ScanImageDataset
    img = np.nan_to_num(img, nan=0.0, posinf=0.0, neginf=0.0)
    img = img.astype(np.float32)
    img = img - img.min()
    maxv = img.max()
    if maxv > 0:
        img = img / maxv

    from PIL import Image
    pil = Image.fromarray((img * 255.0).astype(np.uint8), mode='L')
    pil = pil.resize(IMAGE_SIZE, Image.BILINEAR)
    arr = np.asarray(pil, dtype=np.float32) / 255.0
    tensor = torch.from_numpy(arr).unsqueeze(0).unsqueeze(0).float()

    with torch.no_grad():
        out = model(tensor)
        pred = int(out.argmax(dim=1).item())

    ok = int(pred == label)
    if ok:
        correct += 1
    processed += 1
    results.append({'path': str(path), 'label': label, 'pred': pred, 'correct': bool(ok)})

acc_processed = correct / processed if processed>0 else None
acc_overall = correct / (processed + skipped_lowq) if (processed+skipped_lowq)>0 else None

report = {
    'total_selected': len(samples),
    'processed': processed,
    'skipped_low_quality': skipped_lowq,
    'accuracy_processed': acc_processed,
    'accuracy_overall': acc_overall,
    'details': results,
}

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
with open(OUTPUT, 'w', encoding='utf-8') as fh:
    json.dump(report, fh, indent=2)

print('Test complete. Report written to', OUTPUT)
print(json.dumps({'processed': processed, 'skipped_low_quality': skipped_lowq, 'accuracy_processed': acc_processed}, indent=2))
