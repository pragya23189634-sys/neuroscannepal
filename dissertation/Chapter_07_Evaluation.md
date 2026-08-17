# Chapter 7: Evaluation

## 7.1 Introduction

This chapter evaluates NeuroScan Nepal against the project aim, objectives, and success criteria defined in Chapter 1. Evaluation covers machine learning performance, system-level testing outcomes, objective achievement, comparison with related work, and critical limitations. The evaluation is honest about what the prototype demonstrates and what it does not claim to deliver.

## 7.2 Evaluation Methodology

Evaluation combined **quantitative** and **qualitative** methods:

| Method | Data source | Purpose |
|--------|-------------|---------|
| Validation metrics | 320-image held-out set from training | Primary model performance |
| 25-image offline test | `results/test_25_results.json` | Reproducible inference check |
| 25-image integration test | `results/integration_test_25.json` | End-to-end system validation |
| Manual workflow testing | 30-item checklist | RBAC and UI correctness |
| Requirements traceability | Chapters 3, 5, 6 | Objective completion mapping |
| Critical review | Student + supervisor feedback | Limitations and future work |

No formal clinician usability study (e.g., System Usability Scale with radiologists) was completed within the project timeline. This is documented as a limitation and recommended future work.

## 7.3 Machine Learning Evaluation

### 7.3.1 Training and validation results

The final `BaselineCNN` model was trained on 1,280 scans and validated on 320 scans (80/20 stratified split, seed 42). Results from `results/cnn_baseline_report.txt`:

| Metric | Value |
|--------|-------|
| Validation accuracy | **97.81%** |
| Balanced accuracy | **98.12%** |
| Best epoch | 18 (of 30) |
| Calibration temperature | 0.75 |
| Train samples | 1,280 |
| Validation samples | 320 |
| CLAHE at load | Enabled |
| Split strategy | Stratified random file split |

**[INSERT FIGURE 7.1: Training/validation accuracy curve — if available from results/]**

The balanced accuracy (98.12%) indicates strong performance on both normal and abnormal classes, not just the majority class. This exceeds the non-functional requirement NFR-2 (≥ 90% accuracy).

### 7.3.2 Confusion matrix interpretation (validation set)

On the 320-image validation set (approximate, from balanced accuracy):

Balanced accuracy = (sensitivity + specificity) / 2 = 0.9812 implies roughly equal performance on both classes. With ~160 samples per class, the model likely misclassified fewer than 7 images total on validation.

Exact per-class counts are stored in the training run output; the key finding is that both sensitivity and specificity are high, reducing the risk of systematic bias toward one class.

### 7.3.3 25-image test set results

Both offline and integration tests used the same 25-image sample (seed 42):

| Metric | Offline | Integration |
|--------|---------|-------------|
| Accuracy | 96.0% | 96.0% |
| Correct | 24/25 | 24/25 |
| False positive | 1 (`Te-no_150.jpg`) | 1 (same) |
| False negative | 0 | 0 |
| Low quality skipped | 0 | 0 |

**Sensitivity (abnormal detection):** 12/12 = **100%** on this sample  
**Specificity (normal detection):** 12/13 = **92.3%** on this sample

The 96% integration accuracy is slightly below the 97.81% validation accuracy, which is expected because:
- The 25-image set is a different random sample (not the validation split).
- Small sample size (n=25) produces high variance.
- Integration includes full preprocessing pipeline effects identical to training.

### 7.3.4 Error analysis: Te-no_150.jpg

The single misclassification was a **false positive** — a normal scan classified as abnormal with 85.11% calibrated confidence.

Possible contributing factors:
1. **Ambiguous imaging features** — subtle intensity patterns resembling pathology.
2. **Single-slice limitation** — abnormality assessment often requires multi-slice context.
3. **High confidence despite error** — calibration improves average reliability but cannot eliminate all errors; the 70% review threshold would not have flagged this case.

**Lesson:** Even at 97.81% validation accuracy, human review remains essential. This supports the design decision to route all results through radiologist and doctor review rather than direct patient self-diagnosis.

### 7.3.5 Confidence calibration evaluation

Temperature scaling (T = 0.75) was fitted on validation logits. On the 25-image integration test:

- 19/25 predictions had ≥ 95% confidence (76%).
- 1/25 misclassified case had 85.11% confidence.
- 0/25 triggered the `review_required` flag (< 70%).

Calibration successfully spread confidence scores, but **confidence is not a guarantee of correctness** — a key message for clinical users.

## 7.4 System Evaluation

### 7.4.1 Pipeline reliability

| Metric | Result |
|--------|--------|
| Jobs completed (integration test) | 25/25 (100%) |
| Pipeline stages per job | 8/8 completed |
| Average pipeline time | ~15–45 seconds (CPU) |
| Backend health | OK, model loaded |
| Auth on all protected routes | Verified |

The eight-stage pipeline completed reliably for all test uploads with no failures or timeouts.

### 7.4.2 Role-based workflow evaluation

The three-role workflow (radiologist → doctor → patient) was evaluated manually (30/30 checks passed):

| Workflow step | Evaluated criterion | Result |
|---------------|--------------------|----|
| Radiologist upload | Only radiologist can upload | Pass |
| Patient linkage | Scan linked to NSN-PAT-XXXXXX | Pass |
| Radiologist notes | Saved and visible to doctor/patient | Pass |
| Doctor review | Only doctor can submit recommendation | Pass |
| Patient portal | Patient sees only own records | Pass |
| Disclaimer | Visible on About page | Pass |

This workflow design addresses the research question on RBAC architecture (Chapter 1, RQ3).

## 7.5 Objective Achievement

| Objective | Criterion | Result | Status |
|-----------|-----------|--------|--------|
| O1 — Dataset | ≥1,000 labelled scans | ~1,600 from Grande Hospital | **Achieved** |
| O2 — CNN accuracy | ≥90% validation | 97.81% | **Achieved** |
| O3 — Explainability | Grad-CAM per scan | Generated for all 25 integration jobs | **Achieved** |
| O4 — Full-stack app | 8-stage pipeline via API | 25/25 jobs completed | **Achieved** |
| O5 — RBAC | Three roles enforced | 30/30 manual checks passed | **Achieved** |
| O6 — Evaluation documented | Test results in dissertation | This chapter | **Achieved** |

All six project objectives were met or exceeded.

## 7.6 Comparison with Related Work

| System / study | Dataset | Task | Reported accuracy | NeuroScan Nepal |
|----------------|---------|------|-------------------|-----------------|
| Sartaj et al. (2022) | Public Figshare | 4-class tumour | ~98% | — (different task) |
| NeuroScan Nepal (validation) | Grande Hospital | Binary normal/abnormal | **97.81%** | Primary metric |
| NeuroScan Nepal (integration) | Grande Hospital | Binary + full pipeline | **96%** (n=25) | System-level |
| Commercial AI (Aidoc, etc.) | Multi-site clinical | Specific pathologies | Variable; FDA cleared | Not comparable (research prototype) |

NeuroScan Nepal's validation accuracy is competitive with published brain MRI CNN studies on binary or multi-class tasks. Its distinguishing contribution is not raw accuracy alone but the **integrated workflow** with local data and explainability — absent in most academic baselines.

## 7.7 Research Questions Answered

| Research question | Finding |
|-------------------|---------|
| **RQ1:** Can a lightweight CNN achieve useful accuracy on Grande Hospital data? | Yes — 97.81% validation, 98.12% balanced accuracy. |
| **RQ2:** How does explainability/calibration improve trust? | Grad-CAM provides visual evidence; calibration improves confidence reliability; review flags add safety net for low-confidence cases. |
| **RQ3:** What RBAC design supports radiologist → doctor → patient workflow? | JWT + role-gated API + filtered job lists; manually verified. |
| **RQ4:** What are ethical/practical limitations in Nepal? | See Section 7.8; prototype disclaimer essential; no clinical deployment without regulatory approval. |

## 7.8 Limitations

### 7.8.1 Technical limitations

1. **Binary classification only** — does not distinguish tumour types (glioma, meningioma, etc.).
2. **Single 2D slice** — clinical diagnosis uses multi-slice and multi-sequence MRI volumes.
3. **Small integration test sample** — 25 images is insufficient for statistical significance; validation set (320) is more reliable.
4. **CPU inference** — acceptable for demo but not scalable for hospital throughput.
5. **Legacy unit test debt** — 2 of 3 pytest tests fail on outdated modules.
6. **File-based persistence** — `jobs.json` is not suitable for production concurrency.

### 7.8.2 Clinical and ethical limitations

1. **Not a medical device** — no regulatory approval (Nepal Medical Council, FDA, CE).
2. **No prospective clinical trial** — performance measured retrospectively on labelled dataset.
3. **No inter-rater comparison** — AI accuracy not compared directly against radiologist reads on the same scans.
4. **Dataset representativeness** — Grande Hospital scans may not represent all Nepali acquisition settings.
5. **False positives cause anxiety** — the Te-no_150.jpg error illustrates potential patient harm if used without human review.

### 7.8.3 Project scope limitations

1. **No DICOM/PACS integration** — manual JPEG upload only.
2. **No formal usability study** — peer feedback informal, not SUS-validated.
3. **RAG/chatbot are prototypes** — rule-based, not validated medical advice.
4. **Single developer** — no independent code review team.

## 7.9 Threats to Validity

| Threat | Description | Mitigation |
|--------|-------------|------------|
| **Internal** | Train/val from same hospital | Stratified split; separate 25-image test sample |
| **External** | Generalisation to other hospitals unknown | Document dataset source; recommend multi-site validation |
| **Construct** | Binary labels may oversimplify clinical reality | Scope limited to screening triage, not diagnosis |
| **Conclusion** | Small integration sample | Report validation metrics as primary evidence |

## 7.10 Future Work

1. **Multi-class classification** — extend to tumour subtypes if labels available.
2. **3D volumetric analysis** — use full MRI series rather than single slices.
3. **DICOM integration** — connect to hospital PACS for real workflow embedding.
4. **Clinician usability study** — SUS questionnaire with 5–10 radiologists at Grande Hospital.
5. **Prospective pilot** — blinded comparison of AI + radiologist vs radiologist alone.
6. **Cloud deployment** — containerised FastAPI on AWS/Azure with HTTPS and audit logging.
7. **Fix unit test debt** — update tests for current auth and pipeline modules.
8. **Federated learning** — train across multiple Nepali hospitals without centralising patient data.

## 7.11 Summary

NeuroScan Nepal meets all project objectives. The CNN achieves **97.81% validation accuracy** and **98.12% balanced accuracy** on 320 held-out scans. End-to-end integration testing confirms **96% accuracy** on 25 live pipeline runs with one interpretable false positive. Manual testing validates the three-role clinical workflow and RBAC enforcement. The system demonstrates feasibility as an academic research prototype but is explicitly not ready for unsupervised clinical use. Chapter 8 addresses ethics and data governance; Chapter 9 concludes the dissertation.

---

**Suggested word count:** ~2,200 words  
**Figures to add:** Validation accuracy chart; confusion matrix; screenshot of misclassified scan with Grad-CAM (optional).
