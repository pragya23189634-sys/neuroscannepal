# Chapter 6: Testing

## 6.1 Introduction

This chapter describes the testing strategy applied to NeuroScan Nepal, the test types executed, results obtained, and known issues. Testing validates that the software artefact meets the functional and non-functional requirements defined in Chapter 3 before formal evaluation in Chapter 7.

Testing was organised into four levels:

1. **Unit testing** — isolated module tests (pytest)
2. **Model testing** — offline inference on a 25-image sample
3. **Integration testing** — full pipeline through the live FastAPI backend with RBAC
4. **Manual / system testing** — role-based workflow verification via the React dashboard

## 6.2 Test Strategy

| Level | Purpose | Tool / method |
|-------|---------|---------------|
| Unit | Verify individual functions and modules | pytest |
| Model | Measure classification accuracy offline | `scripts/test_25.py` |
| Integration | Verify end-to-end pipeline + auth + persistence | `scripts/integration_test_25.py` |
| Manual | Verify UI workflow and RBAC behaviour | Manual checklist (Appendix A) |
| Health | Confirm backend readiness | `GET /health` |

The test strategy prioritises **integration and model testing** because the primary risk in this project is incorrect ML inference or broken pipeline stages, not individual utility functions in isolation.

## 6.3 Unit Testing

### 6.3.1 Framework and location

Unit tests reside in `tests/` and are executed with:

```powershell
py -3.11 -m pytest tests/ -v
```

| Test file | Target module | Description |
|-----------|---------------|-------------|
| `test_predict.py` | `src/predict.py` | Loads dummy SimpleCNN weights; verifies label and confidence range |
| `test_preprocessing_pipeline.py` | `src/preprocessing.py` | Verifies train/test split creation on synthetic images |
| `test_prototype.py` | `src/main.py` | Verifies legacy patient prototype report generation |

### 6.3.2 Unit test results

**Run date:** August 2026  
**Environment:** Windows 11, Python 3.11.9, pytest 9.1.1

| Test | Result |
|------|--------|
| `test_predict_scan_with_cnn_model` | **PASS** |
| `test_run_preprocessing_pipeline_creates_splits` | **FAIL** |
| `test_create_patient_prototype` | **FAIL** |

**Summary:** 1 passed, 2 failed (3 total) in 19.14 seconds.

### 6.3.3 Analysis of unit test failures

The two failing tests target **legacy modules** that predate the current production pipeline:

1. **`test_preprocessing_pipeline_creates_splits`** — expects `run_preprocessing_pipeline()` to create on-disk train/test folder splits. The current training path uses in-memory loading via `dataset_utils.py` with a stratified random split, making this test outdated.

2. **`test_create_patient_prototype`** — tests `src/main.py` prototype report generation, which is superseded by the FastAPI backend and eight-stage pipeline.

These failures do **not** affect the live NeuroScan Nepal application. They indicate **test debt** — unit tests were not updated when the architecture migrated from standalone scripts to the integrated backend. Remediation (updating or removing legacy tests) is recommended but was deprioritised in favour of integration testing for the submission deadline.

### 6.3.4 Recommended future unit tests

| Module | Suggested test |
|--------|----------------|
| `src/auth.py` | JWT creation, role enforcement, patient ID generation |
| `src/pipeline.py` | Stage ordering, low-quality skip path, result schema |
| `frontend/src/utils/jobResult.js` | Confidence field fallback (`score` vs `confidence`) |
| `backend.py` | RBAC returns 403 for unauthorised roles |

## 6.4 Model Testing (Offline 25-Image Test)

### 6.4.1 Procedure

Script: `scripts/test_25.py`

1. Sample 25 images (13 normal, 12 abnormal) with random seed 42 from `data/raw/`.
2. Apply CLAHE preprocessing and quality check per image.
3. Run `BaselineCNN` inference directly (no HTTP backend).
4. Compare predicted label to ground truth.
5. Save results to `results/test_25_results.json`.

### 6.4.2 Results

| Metric | Value |
|--------|-------|
| Total selected | 25 |
| Processed | 25 |
| Skipped (low quality) | 0 |
| **Accuracy** | **96.0%** (24/25 correct) |

### 6.4.3 Misclassification detail

| File | True label | Predicted | Correct |
|------|-----------|-----------|---------|
| `Te-no_150.jpg` | Normal | Abnormal | **No** |

This single false positive (normal classified as abnormal) is analysed further in Chapter 7. All 12 abnormal cases were correctly identified (100% sensitivity on this sample). 12 of 13 normal cases were correct (92.3% specificity on this sample).

## 6.5 Integration Testing (Live Backend)

### 6.5.1 Procedure

Script: `scripts/integration_test_25.py`

1. Start FastAPI backend on `http://127.0.0.1:8000`.
2. Authenticate as radiologist (`radiologist@neuroscan.np`).
3. Retrieve patient ID from `/auth/patients`.
4. Upload the same 25-image sample (seed 42) via `POST /upload` with JWT and `patient_id`.
5. Poll `GET /jobs/{id}` until status is `completed` or `failed`.
6. Record label, confidence, and correctness.
7. Save report to `results/integration_test_25.json`.

This test validates the **complete production path**: authentication, upload, asynchronous pipeline, all eight stages, job persistence, and result retrieval.

### 6.5.2 Results

| Metric | Value |
|--------|-------|
| Total selected | 25 |
| Processed | 25 |
| Skipped (low quality) | 0 |
| **Accuracy** | **96.0%** (24/25 correct) |
| Auth | JWT radiologist login successful |
| Pipeline completion | 25/25 jobs reached `completed` status |

### 6.5.3 Offline vs integration comparison

| Test type | Accuracy | Same misclassification? |
|-----------|----------|------------------------|
| Offline (`test_25.py`) | 96% | `Te-no_150.jpg` |
| Integration (`integration_test_25.py`) | 96% | `Te-no_150.jpg` (confidence 85.11%) |

The identical results confirm **training/inference parity** — the live pipeline produces the same classifications as direct model inference. The misclassified scan received 85.11% confidence (above the 70% review threshold), illustrating that high confidence does not guarantee correctness.

### 6.5.4 Confidence distribution (integration test)

| Confidence range | Count |
|-----------------|-------|
| ≥ 99% | 14 |
| 95–99% | 5 |
| 85–95% | 5 |
| 70–85% | 1 (misclassified normal) |

Most predictions were highly confident; the single error occurred at 85.11% confidence on a normal scan.

## 6.6 Manual System Testing

Manual testing verified the three-role clinical workflow through the React dashboard. A full checklist is provided in **Appendix A** (`MANUAL_TEST_CHECKLIST.md`).

### 6.6.1 Test environment

| Component | Configuration |
|-----------|---------------|
| OS | Windows 11 |
| Browser | Chrome / Edge |
| Backend | FastAPI on port 8000 |
| Frontend | Vite dev server on port 3000 |
| Launcher | `START_NEUROSCAN.bat` |

### 6.6.2 Manual test summary

| Area | Tests | Passed | Notes |
|------|-------|--------|-------|
| Authentication | 6 | 6 | Login, logout, role redirect, invalid credentials |
| Radiologist workflow | 8 | 8 | Upload, processing, results, notes |
| Doctor workflow | 4 | 4 | Review queue, recommendation submit |
| Patient workflow | 3 | 3 | Own records only, report display |
| RBAC enforcement | 5 | 5 | 403 on unauthorised API calls |
| UI / display | 4 | 4 | Confidence display, Grad-CAM, model metrics |
| **Total** | **30** | **30** | All manual checks passed |

**[INSERT FIGURE 6.1: Screenshot of processing page with all stages complete]**  
**[INSERT FIGURE 6.2: Screenshot of doctor review submitted]**

### 6.6.3 RBAC test cases

| # | Action | Role | Expected | Result |
|---|--------|------|----------|--------|
| RB-1 | POST `/upload` | Doctor | 403 Forbidden | Pass |
| RB-2 | POST `/upload` | Radiologist | 200 + job_id | Pass |
| RB-3 | GET `/jobs` | Patient | Only own jobs | Pass |
| RB-4 | POST `/jobs/{id}/doctor-review` | Radiologist | 403 Forbidden | Pass |
| RB-5 | GET `/jobs/{id}` (other patient's job) | Patient | 403 Forbidden | Pass |

## 6.7 Health and Performance Testing

### 6.7.1 Backend health check

`GET /health` response (August 2026):

```json
{
  "status": "ok",
  "pipeline_ready": true,
  "model_available": true,
  "jobs_count": 51,
  "auth_enabled": true
}
```

### 6.7.2 Pipeline performance

| Metric | Target (NFR-1) | Observed |
|--------|----------------|----------|
| Single scan pipeline time | ≤ 60 seconds | ~15–45 seconds (CPU) |
| Upload response time | Immediate | < 1 second (async processing) |
| Job poll interval | — | 1 second (frontend) |

Performance meets the non-functional requirement on development hardware without GPU acceleration.

## 6.8 Requirements Traceability (Testing)

| Requirement | Test evidence |
|-------------|---------------|
| FR-A1–A5 (Auth/RBAC) | Manual RBAC tests RB-1 to RB-5 |
| FR-U1–U6 (Upload/pipeline) | Integration test 25/25 completed |
| FR-C1–C5 (Classification) | Model test 96%; validation 97.81% |
| FR-W1–W4 (Clinical workflow) | Manual tests (30/30 passed) |
| NFR-1 (Performance) | Pipeline ≤ 60s observed |
| NFR-2 (Accuracy ≥ 90%) | Validation 97.81%; integration 96% |
| NFR-4 (Security) | JWT + bcrypt verified manually |

## 6.9 Known Issues and Test Limitations

| Issue | Severity | Impact |
|-------|----------|--------|
| 2 legacy unit tests fail | Low | Does not affect live system |
| Single 25-image test set | Medium | Small sample; not statistically definitive |
| No automated frontend tests | Medium | UI regressions require manual re-testing |
| Usability study with real clinicians not completed | Medium | Document as future work |
| CPU-only inference | Low | Slower but functional for demo |

## 6.10 Summary

NeuroScan Nepal was tested at unit, model, integration, and manual system levels. The critical validation paths — offline model inference and live backend integration — both achieved **96% accuracy** on an identical 25-image sample, with one consistent false positive. Manual testing confirmed all 30 workflow and RBAC checks passed. Two legacy unit tests fail due to architectural drift and should be updated post-submission. Chapter 7 evaluates these results against project objectives and discusses limitations.

---

## Appendix A: Manual Test Checklist

See `MANUAL_TEST_CHECKLIST.md` in the project root for the full printable checklist used during manual system testing.

---

**Suggested word count:** ~2,000 words
