# NeuroScan Nepal — Project Structure

Quick map of the repository after cleanup (August 2026).

```
NeuroScan_Nepal/
├── START_NEUROSCAN.bat      ← Double-click to run the app
├── backend.py               ← FastAPI server entry point
├── README.md                  ← Setup and demo instructions
│
├── frontend/                  ← React dashboard (port 3000)
├── src/                       ← Python ML + auth + pipeline
├── scripts/                   ← Training, tests, doc generators
├── tests/                     ← pytest unit tests (7 tests)
│
├── data/raw/                  ← MRI dataset (normal/ + abnormal/)
├── models/                    ← cnn_baseline.pth + calibration
├── results/                   ← Training reports, test JSON outputs
├── uploads/                   ← Runtime uploaded scans (regenerated on use)
│
├── dissertation/              ← Chapters 1–9 (Markdown source)
├── docs/
│   ├── submission/            ← Dissertation Word doc, weekly journal, interim PDF
│   ├── guides/                ← Viva script, logbook guide, manual test checklist
│   └── SUS_*.md / *.csv       ← Usability study pack
│
└── legacy/
    └── static-prototype/      ← Old HTML prototype (before React app)
```

## What to use for submission

| Item | Location |
|------|----------|
| Final dissertation (Word) | `docs/submission/NeuroScan_Nepal_Dissertation_Full.docx` |
| 32-week journal | `docs/submission/NeuroScan_Nepal_Weekly_Journal_32_Weeks_Updated.docx` |
| Interim report PDF | `docs/submission/Interim_Project_Report_PragyaGajurel (2).pdf` |
| Viva rehearsal | `docs/guides/VIVA_DEMO_SCRIPT.md` |
| Mahara logbook help | `docs/guides/LOGBOOK_FILLING_GUIDE.md` |
| Manual testing | `docs/guides/MANUAL_TEST_CHECKLIST.md` |
| SUS study | `docs/SUS_USABILITY_STUDY.md` |

## Regenerate documents

```powershell
py -3.11 scripts/generate_dissertation_doc.py      # → docs/submission/
py -3.11 scripts/generate_weekly_journal_doc.py
py -3.11 scripts/generate_logbook_doc.py
```

## Runtime files (safe to ignore / regenerate)

These grow during testing and are listed in `.gitignore`:

- `uploads/` — uploaded MRI files
- `jobs.json` — job history
- `neuroscan.db` — demo user accounts
- `neuroscan.log` — pipeline logs
- `results/jobs/` — per-job HTML/JSON reports

To clear test clutter and start fresh:

```powershell
.\scripts\cleanup_test_artifacts.ps1
```

## Parent folder (`final year project/`)

```
final year project/
├── README.md              ← Overview of the whole folder
├── NeuroScan_Nepal/       ← Main project (use this)
├── _archive/              ← Old dissertation drafts, large zip backup
└── .venv/                 ← Python environment (optional)
```

## Legacy code (still in `src/` but not main path)

| File | Notes |
|------|-------|
| `src/train_cnn.py`, `src/evaluate.py`, `src/train.py` | Early training experiments |
| `src/03_transfer_learning.py`, `src/04_gradcam.py` | Numbered coursework scripts |
| `src/main.py` | Early prototype report generator |
| `legacy/static-prototype/` | Pre-React HTML demo |

**Production path:** `backend.py` → `src/pipeline.py` → `src/cnn_baseline.py`
