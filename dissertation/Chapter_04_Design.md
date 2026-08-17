# Chapter 4: System Design

## 4.1 Introduction

This chapter presents the high-level and detailed design of NeuroScan Nepal. It covers system architecture, the eight-stage processing pipeline, machine learning module design, data models, role-based access control, and user interface structure. Design decisions are traced to requirements in Chapter 3.

## 4.2 High-Level Architecture

NeuroScan Nepal follows a **three-tier decoupled architecture**:

```
┌─────────────────────────────────────────────────────────────────┐
│                     Presentation Tier                            │
│  React 18 + Vite + Tailwind CSS (port 3000)                     │
│  Pages: Login, Upload, Processing, Results, DoctorReview,       │
│         PatientPortal, ModelInfo, About                          │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTP/JSON + JWT Bearer
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Application Tier                             │
│  FastAPI (Python 3.11, port 8000) — backend.py                 │
│  Auth, job management, file upload, review endpoints             │
└───────────────────────────┬─────────────────────────────────────┘
                            │ function calls
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                     ML / Data Tier                               │
│  src/pipeline.py — 8-stage inference pipeline                   │
│  src/cnn_baseline.py — BaselineCNN model                        │
│  src/preprocessing.py — CLAHE, QC, scan loading                 │
│  src/auth.py — SQLite users, JWT, RBAC                          │
│  Storage: uploads/, jobs.json, results/jobs/{id}/, neuroscan.db │
└─────────────────────────────────────────────────────────────────┘
```

**[INSERT FIGURE 4.1: System architecture diagram]**

### 4.2.1 Design rationale

| Decision | Rationale |
|----------|-----------|
| Decoupled frontend/backend | Independent development, clear API contract, demonstrates full-stack skills |
| FastAPI | Async support, automatic OpenAPI docs, Python ML ecosystem compatibility |
| React SPA | Component reuse, fast dev with Vite, industry-standard UI framework |
| File-based job persistence | Simplicity for prototype; avoids database complexity for job blobs |
| SQLite for users | Zero-config, sufficient for demo-scale user base |
| Background thread for pipeline | Non-blocking upload response; frontend polls job status |

## 4.3 Eight-Stage Processing Pipeline

Each uploaded MRI triggers an asynchronous pipeline executed in a background thread:

| Step | Key | Description | Output |
|------|-----|-------------|--------|
| 1 | `upload` | File saved to `uploads/{job_id}_{filename}` | Stored path |
| 2 | `preprocessing` | CLAHE, resize 128×128, low-contrast QC | Normalised tensor; QC flag |
| 3 | `detection` | BaselineCNN inference + temperature calibration | Label, confidence, review flag |
| 4 | `gradcam` | Gradient-weighted class activation map | `gradcam.png` overlay |
| 5 | `rag_advisory` | Label-conditioned advisory text from knowledge base | Advisory JSON |
| 6 | `chatbot` | FAQ response stub (English/Nepali) | Chat response |
| 7 | `hospital_finder` | Nepali neurology hospital list | Hospital array |
| 8 | `pdf_report` | HTML, JSON, TXT report export | Files in `results/jobs/{id}/` |

**[INSERT FIGURE 4.2: Pipeline flowchart]**

Each stage calls `on_stage(job_id, step, status, record)` to update `jobs.json` in real time, enabling the Processing page to poll and render progress.

### 4.3.1 Quality control gate

If `is_low_contrast()` returns true during preprocessing, the pipeline marks the job with `low_quality: true` and skips unreliable classification. This implements FR-U4 and prevents overconfident predictions on unusable inputs.

### 4.3.2 Confidence calibration

Validation logits are used to fit a temperature scalar (stored in `models/cnn_baseline_calibration.json`). At inference, softmax probabilities are scaled by this temperature before reporting confidence. Predictions below 70% set `review_required: true`.

## 4.4 Machine Learning Module Design

### 4.4.1 BaselineCNN architecture

```
Input: 1 × 128 × 128 grayscale
  → Conv2d(1→32) + BN + ReLU + MaxPool
  → Conv2d(32→64) + BN + ReLU + MaxPool
  → Conv2d(64→128) + BN + ReLU + AdaptiveAvgPool(4×4)
  → Flatten → Linear(2048→256) + ReLU + Dropout(0.4)
  → Linear(256→2)
Output: logits [normal, abnormal]
```

**[INSERT FIGURE 4.3: CNN architecture diagram]**

### 4.4.2 Training design

| Parameter | Value |
|-----------|-------|
| Train / validation split | 80 / 20 stratified (1280 / 320) |
| Optimiser | AdamW (lr=0.0005, weight decay=0.0001) |
| Loss | Cross-entropy with label smoothing (0.03) + class weights |
| Epochs | 30 (early stopping patience=7) |
| Batch size | 32 |
| Augmentation | Horizontal flip, rotation, brightness, zoom, shift |
| CLAHE at load | Enabled (training/inference parity) |
| Best epoch | 18 |

Split manifest written to `results/cnn_baseline_split.json` for reproducibility.

### 4.4.3 Grad-CAM design

Grad-CAM targets the final convolutional layer (`features[8]`). Gradients of the predicted class score flow back to produce a spatial heatmap, which is resized and overlaid on the preprocessed scan using a colour map (jet/inferno). Output saved as PNG alongside the job report.

## 4.5 Role-Based Access Control Matrix

| Resource / Action | Radiologist | Doctor | Patient |
|-------------------|:-----------:|:------:|:-------:|
| Upload MRI | ✓ | ✗ | ✗ |
| View all jobs | ✓ (all) | ✓ (all) | ✗ |
| View own jobs | — | — | ✓ |
| View scan image | ✓ | ✓ | ✓ (own) |
| Add radiologist notes | ✓ | ✗ | ✗ |
| Submit doctor review | ✗ | ✓ | ✗ |
| List patients | ✓ | ✓ | ✗ |
| Model info page | ✓ | ✗ | ✗ |

Enforcement layers:
1. **Frontend** — `ProtectedRoute` component checks JWT role before rendering pages.
2. **Backend** — FastAPI `Depends(require_roles(...))` and `_user_can_access_job()` on every protected route.

### 4.5.1 Authentication flow

```
Client → POST /auth/login {email, password}
       ← {access_token, user, role_label}

Client → GET /jobs  (Header: Authorization: Bearer <token>)
       ← filtered job list per role
```

JWT payload contains user ID, email, role; expires after 24 hours.

## 4.6 Data Model

### 4.6.1 User (SQLite)

| Field | Type | Notes |
|-------|------|-------|
| id | TEXT PK | UUID |
| email | TEXT UNIQUE | Login identifier |
| password_hash | TEXT | bcrypt |
| full_name | TEXT | Display name |
| role | TEXT | radiologist / doctor / patient |
| patient_unique_id | TEXT UNIQUE | NSN-PAT-XXXXXX (patients only) |
| created_at | REAL | Unix timestamp |

### 4.6.2 Job (jobs.json)

| Field | Type | Notes |
|-------|------|-------|
| id | string | UUID |
| filename | string | Stored upload path |
| status | string | pending / running / completed / failed |
| current_step | string | Pipeline stage key |
| stages | array | Stage log with timestamps |
| result | object | Label, confidence, gradcam path, flags |
| patient_user_id | string | Linked patient |
| patient_unique_id | string | NSN-PAT-XXXXXX |
| uploaded_by_name | string | Radiologist name |
| radiologist_notes | object | Notes text + timestamp |
| doctor_recommendation | object | Recommendation + doctor name |

## 4.7 User Interface Design

| Route | Role | Purpose |
|-------|------|---------|
| `/login` | Public | Authentication |
| `/register` | Public | Account creation |
| `/` | Radiologist | Dashboard / job stats |
| `/upload` | Radiologist | MRI upload form |
| `/processing` | Radiologist | Live pipeline tracker |
| `/results` | Radiologist | Results + Grad-CAM + notes |
| `/model` | Radiologist | Model metrics display |
| `/doctor-review` | Doctor | Review queue + recommendation form |
| `/my-records` | Patient | Personal report viewer |
| `/about` | All | Project info + ethics disclaimer |

UI design uses Tailwind CSS with a clinical palette (teal accent `#0D9488`, slate neutrals). Cards, badges, and stat components provide consistent visual hierarchy.

**[INSERT FIGURE 4.4: UI wireframe or screenshot collage — Upload, Results, Patient Portal]**

## 4.8 Deployment Design (development)

For demonstration and viva:

- **Launcher:** `START_NEUROSCAN.bat` → `scripts/start_dashboard.ps1`
- **Backend:** `py -3.11 -m uvicorn backend:app --host 127.0.0.1 --port 8000`
- **Frontend:** `npm run dev -- --host 127.0.0.1` (port 3000)
- **Logs:** `neuroscan.log` + backend terminal stdout

Production deployment (out of scope) would require HTTPS, secrets management, PostgreSQL, and container orchestration.

## 4.9 Summary

NeuroScan Nepal's design separates presentation, application, and ML concerns while linking them through a well-defined REST API and eight-stage pipeline callback pattern. RBAC is enforced at both UI and API layers. The next chapter describes how this design was implemented in code.

---

**Suggested word count:** ~2,000 words
