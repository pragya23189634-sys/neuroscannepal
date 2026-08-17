# Chapter 5: Implementation

## 5.1 Introduction

This chapter describes the implementation of NeuroScan Nepal: technology choices, directory structure, key modules, and notable engineering decisions. Screenshots from the running application should be inserted where indicated.

## 5.2 Technology Stack

| Layer | Technology | Version / notes |
|-------|-----------|-----------------|
| Language (ML/API) | Python | 3.11 |
| ML framework | PyTorch | CNN training and inference |
| API framework | FastAPI | REST endpoints, async upload |
| ASGI server | Uvicorn | Development server |
| Frontend | React | 18.x |
| Build tool | Vite | Fast HMR dev server |
| Styling | Tailwind CSS | Utility-first CSS |
| Auth | python-jose (JWT), bcrypt | Token + password hashing |
| Database | SQLite | User accounts (`neuroscan.db`) |
| Icons | Heroicons | UI iconography |

## 5.3 Project Structure

```
NeuroScan_Nepal/
├── backend.py              # FastAPI application entry point
├── frontend/               # React SPA
│   └── src/
│       ├── pages/          # Upload, Processing, Results, etc.
│       ├── components/     # Header, ProtectedRoute, StatCard
│       ├── utils/          # authFetch, jobResult helpers
│       └── config.js       # API base URL, MODEL_INFO, pipeline steps
├── src/
│   ├── auth.py             # Users, JWT, RBAC dependencies
│   ├── pipeline.py         # 8-stage inference pipeline
│   ├── cnn_baseline.py     # BaselineCNN + training script
│   ├── dataset_utils.py    # Data loading, augmentation, splits
│   ├── preprocessing.py    # CLAHE, scan loading, QC
│   └── logging_config.py   # Structured logging
├── models/
│   ├── cnn_baseline.pth           # Trained weights
│   └── cnn_baseline_calibration.json
├── data/raw/
│   ├── normal/             # Grande Hospital normal slices
│   └── abnormal/           # Grande Hospital abnormal slices
├── results/                # Training reports, job outputs
├── scripts/                # Training, integration tests, doc generators
├── uploads/                # Uploaded MRI files
├── jobs.json               # Job state persistence
├── START_NEUROSCAN.bat     # One-click launcher
└── VIVA_DEMO_SCRIPT.md     # Demonstration guide
```

## 5.4 Backend Implementation

### 5.4.1 Application entry (`backend.py`)

FastAPI initialises the SQLite database and seeds demo users on startup via `init_db()` and `seed_demo_users()`. Key endpoints:

| Method | Path | Role | Function |
|--------|------|------|----------|
| POST | `/auth/login` | Public | Authenticate, return JWT |
| POST | `/auth/register` | Public | Create account |
| GET | `/auth/patients` | Radiologist, Doctor | List patients |
| POST | `/upload` | Radiologist | Upload MRI + create job |
| GET | `/jobs` | Authenticated | List jobs (role-filtered) |
| GET | `/jobs/{id}` | Authenticated | Job detail |
| POST | `/jobs/{id}/radiologist-notes` | Radiologist | Save notes |
| POST | `/jobs/{id}/doctor-review` | Doctor | Submit recommendation |
| GET | `/health` | Public | Health check |

Upload handler saves the file, creates a job record with patient linkage, and spawns `process_job()` in a `threading.Thread`. The pipeline callback `_on_pipeline_stage` writes incremental updates to `jobs.json`.

### 5.4.2 Job processing

```python
def process_job(job_id: str, filepath: str) -> None:
    run_pipeline(
        job_id=job_id,
        scan_path=Path(filepath),
        on_stage=lambda step, status, record: _on_pipeline_stage(job_id, step, status, record),
    )
```

This design keeps the HTTP response fast (returns `job_id` immediately) while the frontend polls `/jobs/{id}` every second during processing.

## 5.5 Machine Learning Implementation

### 5.5.1 Training (`src/cnn_baseline.py`)

The training script:

1. Loads scan paths from `data/raw/normal/` and `data/raw/abnormal/`.
2. Applies stratified 80/20 train/validation split (seed=42).
3. Builds PyTorch `DataLoader`s with MRI-safe augmentation from `dataset_utils.py`.
4. Trains `BaselineCNN` with class-weighted loss, AdamW, cosine LR schedule, and early stopping.
5. Fits temperature scaling on validation logits.
6. Writes `models/cnn_baseline.pth`, calibration JSON, split manifest, and `results/cnn_baseline_report.txt`.

**Final metrics:**

| Metric | Value |
|--------|-------|
| Validation accuracy | 97.81% |
| Balanced accuracy | 98.12% |
| Calibration temperature | 0.75 |
| Train / val samples | 1280 / 320 |

### 5.5.2 Inference (`src/pipeline.py`)

Detection stage loads weights, applies CLAHE via `load_scan()`, normalises to [0,1], and runs forward pass. Softmax probabilities are temperature-scaled. Result object includes:

- `label` — "normal" or "abnormal"
- `confidence` — calibrated probability of predicted class
- `review_required` — true if confidence < 0.70
- `confidence_band` — "high" / "moderate" / "low"

Grad-CAM uses `torch.autograd.grad` on the predicted class logit with respect to the final conv feature map.

### 5.5.3 Preprocessing (`src/preprocessing.py`)

`load_scan(path, apply_clahe=True)` reads JPEG/PNG, converts to grayscale float32, applies CLAHE (clip limit 2.0, tile grid 8×8), and resizes to 128×128. `is_low_contrast()` computes standard deviation of pixel intensities; values below threshold trigger the QC warning path.

## 5.6 Authentication Implementation (`src/auth.py`)

- Passwords hashed with `bcrypt.gensalt()`.
- JWT created with `jose.jwt.encode()`; payload includes `sub` (user ID), `email`, `role`, `exp`.
- `get_current_user()` dependency extracts Bearer token and validates.
- `require_roles(*roles)` factory returns a dependency that raises HTTP 403 if role not matched.
- Patient IDs generated sequentially: `NSN-PAT-{count+1:06d}`.

Demo accounts seeded on first run:

| Role | Email | Name |
|------|-------|------|
| Radiologist | radiologist@neuroscan.np | Kishor Phuyal |
| Doctor | doctor@neuroscan.np | Dr. Bikram Prasad Gajurel |
| Patient | patient@neuroscan.np | Ram Bahadur Thapa |

## 5.7 Frontend Implementation

### 5.7.1 Routing and protection

`App.jsx` defines role-gated routes. `ProtectedRoute` reads the JWT from `localStorage`, verifies role membership, and redirects to `/login` if unauthorised.

### 5.7.2 API client

`authFetch()` wraps `fetch()` with `Authorization: Bearer` header and base URL from `config.js`. Used by all data-fetching pages.

### 5.7.3 Key pages

| Page | Implementation notes |
|------|------------------------|
| **Upload** | Fetches `/auth/patients`, multipart POST to `/upload` with `patient_id` |
| **Processing** | Polls `/jobs/{id}`; renders `PIPELINE_STEPS` with status badges |
| **Results** | Displays label, confidence (via `jobResult.js` helper), Grad-CAM image, RAG text; POST notes |
| **DoctorReview** | Lists completed jobs; POST `/jobs/{id}/doctor-review` |
| **PatientPortal** | Filters to patient's own jobs; shows doctor recommendation |
| **ModelInfo** | Reads `MODEL_INFO` from config (97.81% accuracy) |

**[INSERT FIGURE 5.1: Upload page screenshot]**  
**[INSERT FIGURE 5.2: Processing page with completed stages]**  
**[INSERT FIGURE 5.3: Results page with Grad-CAM]**  
**[INSERT FIGURE 5.4: Doctor review page]**  
**[INSERT FIGURE 5.5: Patient portal]**

### 5.7.4 Confidence display fix

Initial frontend code read `result.confidence` while the pipeline stored `result.score`. The utility `frontend/src/utils/jobResult.js` was updated to check both fields, resolving a bug where the UI showed 0% despite valid backend scores.

## 5.8 Report Generation

The final pipeline stage writes three formats to `results/jobs/{job_id}/`:

- `report.html` — styled summary for browser viewing
- `report.json` — machine-readable full job result
- `report.txt` — plain-text summary for logging

Reports include classification, confidence, advisory text, hospital list, and timestamps.

## 5.9 Integration Test Script

`scripts/integration_test_25.py` authenticates as radiologist, uploads 25 stratified samples (13 normal, 12 abnormal), polls until completion, and computes accuracy. Updated for RBAC (JWT + `patient_id` form field). Latest run: **96% accuracy** (24/25 correct), results in `results/integration_test_25.json`.

## 5.10 Logging

`logging_config.py` configures structured logging. Pipeline stages log at INFO level with job ID prefix:

```
[job=a1b2c3d4] STEP 3/8 DETECTION       | OK | label=abnormal confidence=98.71%
```

Logs append to `neuroscan.log` for post-demo analysis.

## 5.11 Challenges and Solutions

| Challenge | Solution |
|-----------|----------|
| Dataset had only Te-* files (no train/test prefix) | Stratified random 80/20 split with manifest |
| Low confidence scores (55–60%) | Retrained with augmentation, class weights, calibration |
| RBAC broke integration tests (401) | Added JWT login to test script |
| UI confidence 0% | Fixed field name mismatch in `jobResult.js` |
| CPU-only training slow | Preloaded scans into memory; reduced image size to 128×128 |

## 5.12 Summary

NeuroScan Nepal was implemented as a modular Python/React application with a clearly separated ML pipeline, auth layer, and clinical workflow UI. The trained CNN achieves 97.81% validation accuracy; the live integration pipeline achieves 96% on a 25-image test. Chapters 6 and 7 (Phase 3) will document formal testing and evaluation; Chapter 8 (Phase 4) will address ethics.

---

**Suggested word count:** ~2,200 words
