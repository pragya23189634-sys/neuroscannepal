# NeuroScan Nepal

A Python project template for organizing and processing neuroimaging data in Nepal.

## Project structure

- `data/raw/normal` - raw normal scan samples
- `data/raw/abnormal` - raw abnormal scan samples
- `models` - trained models and checkpoints
- `results` - evaluation outputs, figures, and reports
- `src` - project source code

## Setup

1. Create a virtual environment:

```bash
python -m venv .venv
```

2. Activate it:

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1
```

3. Install the base dependencies needed for the loader and preprocessing pipeline:

```bash
pip install -r requirements.txt
```

4. (Optional) If you want to generate a confusion matrix plot during evaluation, install matplotlib separately:

```bash
pip install matplotlib
```

5. If you want to train the CNN, install the PyTorch dependencies separately:

```bash
pip install -r requirements-cnn.txt
```

## Usage

Start the project from `src/main.py`:

```bash
python src/main.py
```

Train a simple abnormality classifier with the sample pipeline:

```bash
python src/train.py
```

The training script uses a NumPy-based classifier and will create a model at `models/neuroscan_model.pkl`.
It also writes a report to `results/training_report.txt`.

Evaluate a trained model:

```bash
python src/evaluate.py
```

Predict a label for a single scan file:

```bash
python src/predict.py --scan-path data/raw/normal/sample.nii
```

Train a simple convolutional neural network on the image data:

```bash
python src/train_cnn.py
```

The CNN training script saves a model to `models/neuroscan_cnn.pth` and a report to `results/training_cnn_report.txt`.

By default, the evaluation script loads `models/neuroscan_model.pkl`, performs a hold-out split, and writes `results/evaluation_report.txt`. It also saves a confusion matrix image to `results/confusion_matrix.png` when `matplotlib` is available.

## Next steps

- add neuroimaging data to `data/raw/normal` and `data/raw/abnormal`
- implement preprocessing and feature extraction in `src/main.py`
- add training and evaluation pipelines
