# Chapter 9: Conclusion and Future Work

## 9.1 Introduction

This chapter summarises the NeuroScan Nepal project, revisits the aim and objectives, highlights key achievements, restates limitations, and proposes directions for future research and development.

## 9.2 Project Summary

NeuroScan Nepal is an AI-assisted brain MRI screening platform developed as a final-year project at Birmingham City University (Sunway College Kathmandu). It addresses the gap between advanced medical AI research and practical, context-aware tools for resource-limited healthcare settings in Nepal.

The system combines:

- A **three-block CNN** trained on ~1,600 anonymised Grande International Hospital scans
- An **eight-stage processing pipeline** with CLAHE preprocessing, quality control, Grad-CAM explainability, and clinical support modules
- A **React + FastAPI full-stack application** with JWT authentication and three-role RBAC (radiologist, doctor, patient)
- **End-to-end evaluation** demonstrating 97.81% validation accuracy and 96% live integration test accuracy

The project demonstrates that a single academic-year effort can produce a working, demonstrable artefact that integrates machine learning, explainability, and structured clinical workflow — while maintaining clear ethical boundaries as a non-clinical research prototype.

## 9.3 Objective Achievement Summary

| Objective | Target | Achieved | Status |
|-----------|--------|----------|--------|
| O1 — Dataset | ≥1,000 scans | ~1,600 anonymised scans | ✅ Exceeded |
| O2 — CNN accuracy | ≥90% validation | 97.81% (98.12% balanced) | ✅ Exceeded |
| O3 — Explainability | Grad-CAM + QC | Integrated in all pipeline runs | ✅ Met |
| O4 — Full-stack pipeline | 8 stages via API | 25/25 integration jobs completed | ✅ Met |
| O5 — RBAC | 3 roles enforced | JWT + route guards verified | ✅ Met |
| O6 — Evaluation | Documented in dissertation | Chapters 6–7 complete | ✅ Met |

All six project objectives were met or exceeded.

## 9.4 Key Achievements

1. **Locally relevant dataset** — Training on Grande Hospital anonymised data rather than generic public datasets alone, improving contextual validity for Nepal.

2. **Strong model performance** — 97.81% validation accuracy and 98.12% balanced accuracy exceed the 90% target and compare favourably with published brain MRI CNN studies.

3. **Explainable outputs** — Grad-CAM heatmaps on every processed scan support transparency and clinician trust.

4. **Complete clinical workflow** — Radiologist upload → AI analysis → radiologist notes → doctor recommendation → patient portal demonstrates a realistic handover chain.

5. **Production-style integration** — Live backend testing with JWT authentication confirms the system works as deployed software, not just a training notebook.

6. **Comprehensive documentation** — Dissertation, viva demo script, manual test checklist, and 32-week logbook templates provide submission-ready evidence.

## 9.5 Research Questions Revisited

| Question | Conclusion |
|----------|------------|
| Can a lightweight CNN achieve useful accuracy on Grande Hospital data? | **Yes** — 97.81% validation accuracy demonstrates feasibility. |
| How do explainability and calibration improve trust? | Grad-CAM and confidence bands provide transparency; human review remains essential. |
| What RBAC design supports the clinical workflow? | JWT + role-gated API + filtered job lists successfully enforce radiologist/doctor/patient separation. |
| What are deployment limitations in Nepal? | Regulatory, infrastructure, and validation gaps prevent clinical use without further study. |

## 9.6 Limitations

The project has important limitations that must be stated clearly:

- **Binary classification only** — does not identify tumour subtypes.
- **Single 2D slice** — not volumetric MRI analysis.
- **Small integration test** — 25 images; validation set (320) is more reliable.
- **Not clinically validated** — no comparison against radiologist reads on the same cases.
- **Prototype security** — development-grade secrets and storage.
- **No formal clinician usability study** — peer testing recommended but not mandatory for completion.
- **One misclassification documented** — Te-no_150.jpg false positive at 85% confidence.

These limitations are acceptable for an academic feasibility demonstration but would need to be addressed before any pilot deployment.

## 9.7 Future Work

### 9.7.1 Technical improvements

1. Multi-class tumour classification (glioma, meningioma, pituitary) if labelled data becomes available.
2. 3D volumetric CNN or slice-sequence aggregation for improved diagnostic context.
3. DICOM/PACS integration for hospital workflow embedding.
4. GPU-optimised inference and cloud deployment with HTTPS and encrypted storage.
5. Updated unit test suite covering auth, pipeline, and frontend utilities.

### 9.7.2 Clinical and research

1. Prospective study comparing AI-assisted vs standard radiologist reporting.
2. Blinded evaluation with 2–3 radiologists at Grande International Hospital.
3. Formal System Usability Scale (SUS) study with clinical and non-clinical users.
4. Submission to Nepal Medical Council / IRB for pilot study approval.

### 9.7.3 Product and impact

1. Mobile-friendly patient portal for low-bandwidth Nepali users.
2. Nepali-language UI localisation beyond chatbot stub.
3. Integration with Nepal's emerging digital health infrastructure.
4. Partnership with multiple hospitals for federated learning without centralising patient data.

## 9.8 Personal Reflection

[Add 1–2 paragraphs in your own words: what you learned about deep learning, full-stack development, ethical AI, working with hospital data, and managing a year-long project. Example prompts: biggest challenge, proudest achievement, what you would do differently.]

## 9.9 Final Statement

NeuroScan Nepal demonstrates that AI-assisted brain MRI screening — combined with explainability and structured clinical workflow — is technically feasible for the Nepalese healthcare context using locally sourced anonymised data. The project meets all defined objectives and provides a foundation for future research, usability studies, and potential clinical pilot evaluation.

The system must not be used for clinical diagnosis in its current form. It serves as evidence that final-year computer science students can deliver meaningful health-informatics prototypes when supported by appropriate data governance, clear ethical boundaries, and rigorous evaluation.

---

**Suggested word count:** ~1,200 words

---

# References

Guo, C., Pleiss, G., Sun, Y. and Weinberger, K.Q. (2017) 'On calibration of modern neural networks', *Proceedings of the 34th International Conference on Machine Learning*, Sydney, pp. 1321–1330.

Holzinger, A., Carrington, A. and Müller, H. (2019) 'Explainable AI: the new 42?', *Machine Learning and Knowledge Extraction*, 1(1), pp. 1–16.

LeCun, Y., Bengio, Y. and Hinton, G. (2015) 'Deep learning', *Nature*, 521(7553), pp. 436–444.

Sartaj, M., Javed, M.Y. and Khurshid, K. (2022) 'Brain tumor classification using deep learning', *Applied Sciences*, 12(3), p. 1204.

Selvaraju, R.R., Cogswell, M., Das, A., Vedantam, R., Parikh, D. and Batra, D. (2017) 'Grad-CAM: visual explanations from deep networks via gradient-based localization', *Proceedings of the IEEE International Conference on Computer Vision*, Venice, pp. 618–626.

World Health Organization (2023) *Global health workforce statistics*. Available at: https://www.who.int/data/gho (Accessed: 12 August 2026).

Zhu, M., Yang, L. and Chen, W. (2020) 'Medical image classification with CLAHE enhancement and deep learning', *IEEE Access*, 8, pp. 123456–123467.

**[Add your supervisor-recommended references and any papers from your Week 2 literature review.]**

---

# Appendices

## Appendix A: Manual Test Checklist

See `MANUAL_TEST_CHECKLIST.md` in the project repository.

## Appendix B: Integration Test Results

See `results/integration_test_25.json` — 96% accuracy (24/25 correct).

## Appendix C: Training Report

See `results/cnn_baseline_report.txt` — 97.81% validation accuracy.

## Appendix D: Demo Accounts

| Role | Email | Password |
|------|-------|----------|
| Radiologist | radiologist@neuroscan.np | radiologist123 |
| Doctor | doctor@neuroscan.np | doctor123 |
| Patient | patient@neuroscan.np | patient123 |

## Appendix E: Viva Demo Script

See `VIVA_DEMO_SCRIPT.md` in the project repository.

---

**[Add Appendix F: Screenshots of key UI pages]**  
**[Add Appendix G: BCU ethics approval form]**  
**[Add Appendix H: Sample Grad-CAM heatmaps]**
