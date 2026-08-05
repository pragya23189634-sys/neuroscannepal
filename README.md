# NeuroScan Nepal

AI-assisted brain MRI screening platform — final year project (BCU / Sunway College Kathmandu).

## Features

- CNN-based abnormality classification (baseline model, ~94% validation accuracy)
- CLAHE preprocessing with low-contrast quality check
- 8-stage integration pipeline: upload → preprocessing → detection → Grad-CAM → RAG advisory → chatbot → hospital finder → report
- FastAPI backend with step-by-step terminal logging
- React dashboard for upload, live processing, and results review

## Project structure

- `data/raw/` — MRI dataset (not committed; add locally)
- `models/` — trained weights (not committed)
- `results/` — reports and job outputs (not committed)
- `src/` — ML pipeline, preprocessing, training scripts
- `frontend/` — React + Vite dashboard
- `backend.py` — FastAPI server
- `scripts/` — training and integration test helpers

## Setup

### Backend (Python 3.11 recommended — PyTorch support)

```powershell
pip install -r requirements.txt
pip install -r requirements-cnn.txt
py -3.11 -m uvicorn backend:app --host 127.0.0.1 --port 8000 --reload
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

Open http://127.0.0.1:3000

### Quick start (Windows)

```powershell
.\scripts\start_dashboard.ps1
```

## Training

```powershell
py -3.11 src/cnn_baseline.py --epochs 10 --batch-size 32
```

## Integration testing

```powershell
py -3.11 scripts/test_25.py
py -3.11 scripts/integration_test_25.py
```

## Disclaimer

Research prototype for academic evaluation only — not for clinical diagnosis.
