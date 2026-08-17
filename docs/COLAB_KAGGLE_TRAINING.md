# Train NeuroScan Nepal on Google Colab or Kaggle (GPU)

Your local PC trains on **CPU** (~15–30 min per run). Colab/Kaggle give you a **free GPU (T4)** and finish in **~3–8 minutes**.

---

## Colab vs Kaggle — which to pick?

| | **Google Colab** (recommended to start) | **Kaggle Notebooks** |
|---|----------------------------------------|----------------------|
| **Ease** | Easiest — upload zip, run notebook | Need Kaggle account + dataset upload |
| **GPU** | T4 free tier | T4 / P100 (~30 hrs/week) |
| **Session** | May disconnect after ~90 min idle | Up to 9–12 hours |
| **Data storage** | Google Drive or manual upload | Kaggle Dataset (persistent) |
| **Best for** | Quick fine-tune, first GPU run | Repeated training across weeks |

**Suggestion:** Start with **Colab** using `notebooks/NeuroScan_Colab_Training.ipynb`. Move to **Kaggle** if you train often.

---

## Files you must upload

### Minimum (training code)

Upload these 3 Python files into Colab (or zip as `neuroscan_src.zip`):

| File | Path in project |
|------|-----------------|
| Training script | `src/cnn_baseline.py` |
| Dataset helpers | `src/dataset_utils.py` |
| Preprocessing | `src/preprocessing.py` |

### Dataset (required)

Zip your MRI folders:

```
data/raw/normal/    → ~800 images
data/raw/abnormal/  → ~800 images
```

Create **`neuroscan_data.zip`** containing:

```
raw/normal/...
raw/abnormal/...
```

**Do not upload** the whole `final year project` folder (too large, includes 512 MB old models).

### Optional (fine-tune from current model)

| File | Why |
|------|-----|
| `models/cnn_baseline.pth` | Continue training from 97.81% model |
| `models/cnn_baseline_calibration.json` | Re-calibrate after fine-tune |

---

## Google Colab — step by step

### 1. Open the notebook

1. Go to [https://colab.research.google.com](https://colab.research.google.com)
2. **File → Upload notebook**
3. Upload: `NeuroScan_Nepal/notebooks/NeuroScan_Colab_Training.ipynb`

### 2. Enable GPU

**Runtime → Change runtime type → Hardware accelerator → GPU → T4 → Save**

### 3. Prepare data on Google Drive (recommended)

1. Zip `data/raw/normal` and `data/raw/abnormal` as `neuroscan_data.zip`
2. Upload to Google Drive (e.g. `My Drive/NeuroScan/`)
3. Optionally upload `cnn_baseline.pth` to same folder

### 4. Run all cells

The notebook will:

- Verify GPU (`cuda` available)
- Install `opencv-python-headless`, `scikit-learn`
- Mount Drive and unzip data
- Copy/upload `src/` files
- Train with same settings as `train_fast.ps1`
- Save `cnn_baseline.pth`, calibration JSON, report, curves
- Download files back to your PC

### 5. Copy results back to your project

Put downloaded files into:

```
NeuroScan_Nepal/models/cnn_baseline.pth
NeuroScan_Nepal/models/cnn_baseline_calibration.json
NeuroScan_Nepal/results/cnn_baseline_report.txt
NeuroScan_Nepal/results/training_curves.png
```

Restart your dashboard and test with `integration_test_25.py`.

---

## Kaggle — step by step

### 1. Create a Dataset

1. [kaggle.com](https://www.kaggle.com) → **Datasets → New Dataset**
2. Upload `neuroscan_data.zip` (and optionally `cnn_baseline.pth`)
3. Name: `neuroscan-mri-grande`

### 2. Create Notebook

1. **Code → New Notebook → Add data → your dataset**
2. **Settings → Accelerator → GPU T4 x2**
3. Copy cells from `NeuroScan_Colab_Training.ipynb` (same logic; skip Drive mount)
4. Set paths:

```python
DATA_ZIP = "/kaggle/input/neuroscan-mri-grande/neuroscan_data.zip"
PRETRAINED = Path("/kaggle/input/neuroscan-mri-grande/cnn_baseline.pth")  # if uploaded
```

### 3. Output

Download from **Output** tab or save to Kaggle dataset, then copy to your PC `models/` folder.

---

## GPU — how it works in your code

Your `cnn_baseline.py` already uses GPU automatically:

```python
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = BaselineCNN(num_classes=2).to(device)
```

In Colab cell 1 you should see:

```
GPU: Tesla T4
CUDA available: True
```

If it says `CPU`, go back and enable GPU runtime.

**Fine-tune tip:** In the notebook, set `LOAD_PRETRAINED = True` to load your existing weights before training (lower learning rate e.g. `0.0001`).

---

## Recommended training settings (GPU)

| Setting | Fine-tune (has .pth) | Train from scratch |
|---------|----------------------|--------------------|
| Epochs | 15–20 | 30 |
| Learning rate | 0.0001 | 0.0005 |
| Batch size | 64 (GPU) | 64 |
| Patience | 5 | 7 |

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `CUDA not available` | Runtime → Change runtime type → GPU |
| `No module named cv2` | Run `pip install opencv-python-headless` |
| `No scan data found` | Check zip has `raw/normal/` and `raw/abnormal/` |
| Colab disconnects | Use Kaggle or save checkpoint each epoch to Drive |
| Out of memory | Set `batch_size=16`, or `--no-cache` |

---

## What NOT to upload to Colab/Kaggle

- `transfer_learning_model.pth` (512 MB — unused)
- `uploads/` folder (test junk)
- `frontend/node_modules/`
- Full `_archive/` backup
