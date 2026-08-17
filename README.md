# NeuroScan Nepal

AI-assisted brain MRI screening platform — final year project (BCU / Sunway College Kathmandu).

## Features

- CNN-based abnormality classification (baseline model, **97.81%** validation accuracy on Grande International Hospital data)
- Role-based access: radiologist (upload + AI), doctor (clinical review), patient (view reports)
- CLAHE preprocessing with low-contrast quality check
- 8-stage integration pipeline: upload → preprocessing → detection → Grad-CAM → RAG advisory → chatbot → hospital finder → report
- FastAPI backend with step-by-step terminal logging
- React dashboard for upload, live processing, and results review

## Quick start

Double-click **`START_NEUROSCAN.bat`** or run:

```powershell
.\scripts\start_dashboard.ps1
```

Open http://127.0.0.1:3000/login

## Project structure

See **`PROJECT_STRUCTURE.md`** for a full folder map.

| Folder | Purpose |
|--------|---------|
| `frontend/` | React dashboard |
| `src/` | ML pipeline, auth, preprocessing |
| `scripts/` | Training, tests, doc generators |
| `dissertation/` | Report chapters 1–9 (Markdown) |
| `docs/submission/` | Dissertation Word doc, journal, interim PDF |
| `docs/guides/` | Viva script, logbook guide, test checklist |
| `legacy/` | Old HTML prototype (not used for demo) |

## Demo accounts

| Role | Email | Password |
|------|-------|----------|
| Radiologist | radiologist@neuroscan.np | radiologist123 |
| Doctor | doctor@neuroscan.np | doctor123 |
| Patient | patient@neuroscan.np | patient123 |

See **`docs/guides/VIVA_DEMO_SCRIPT.md`** for the full 10-minute viva workflow.

## Setup (manual)

### Backend (Python 3.11)

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

## Training

```powershell
.\scripts\train_fast.ps1
```

Metrics: **97.81%** validation accuracy · **98.12%** balanced accuracy (see `results/cnn_baseline_report.txt`)

## Testing

```powershell
py -3.11 -m pytest tests/ -v
py -3.11 scripts/integration_test_25.py
```

## Submission documents

| Document | Path |
|----------|------|
| Full dissertation | `docs/submission/NeuroScan_Nepal_Dissertation_Full.docx` |
| 32-week journal | `docs/submission/NeuroScan_Nepal_Weekly_Journal_32_Weeks_Updated.docx` |
| SUS usability pack | `docs/SUS_USABILITY_STUDY.md` |

Regenerate dissertation Word file:

```powershell
py -3.11 scripts/generate_dissertation_doc.py
```

## Disclaimer

Research prototype for academic evaluation only — not for clinical diagnosis.
