# Chapter 3: Requirements Analysis

## 3.1 Introduction

This chapter defines the functional and non-functional requirements for NeuroScan Nepal. Requirements were elicited through literature review (Chapter 2), supervisor meetings, analysis of Grande International Hospital data constraints, and iterative prototyping during Weeks 5–20 of the project logbook. User stories are grouped by role: radiologist, doctor, and patient.

## 3.2 Stakeholders

| Stakeholder | Interest |
|-------------|----------|
| **Radiologist** | Upload MRI scans, run AI pipeline, review results, add investigation notes |
| **Doctor (clinician)** | Review AI output and radiologist notes, write clinical recommendation |
| **Patient** | View own screening report, unique ID, doctor recommendation |
| **Hospital data provider** | Ensure anonymisation and ethical use of MRI data |
| **Supervisor / examiners** | Assess academic rigour, documentation, and demonstration |
| **Developer (student)** | Maintainable codebase, testable pipeline, reproducible training |

## 3.3 Functional Requirements

### 3.3.1 Authentication and authorisation

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-A1 | The system shall allow users to register with email, password, full name, and role (radiologist, doctor, patient) | Must |
| FR-A2 | The system shall authenticate users via email and password, returning a JWT access token | Must |
| FR-A3 | The system shall enforce role-based access on all protected API endpoints | Must |
| FR-A4 | Patient accounts shall be assigned a unique ID in format `NSN-PAT-XXXXXX` | Must |
| FR-A5 | Users shall only access job records permitted by their role | Must |

### 3.3.2 MRI upload and processing

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-U1 | Radiologists shall upload a single MRI image (JPEG/PNG) linked to a selected patient | Must |
| FR-U2 | The system shall run an eight-stage pipeline asynchronously after upload | Must |
| FR-U3 | Pipeline stages: upload, preprocessing, detection, Grad-CAM, RAG advisory, chatbot, hospital finder, report | Must |
| FR-U4 | The system shall flag low-contrast (low-quality) images and skip unreliable classification | Should |
| FR-U5 | Radiologists shall view live pipeline progress in the dashboard | Must |
| FR-U6 | The system shall store job metadata and results persistently (`jobs.json`) | Must |

### 3.3.3 Classification and explainability

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-C1 | The CNN shall classify scans as **normal** or **abnormal** | Must |
| FR-C2 | The system shall output a calibrated confidence score (0–100%) | Must |
| FR-C3 | Predictions below 70% confidence shall be flagged for human review | Should |
| FR-C4 | Grad-CAM heatmaps shall be generated and stored per job | Must |
| FR-C5 | Model weights shall be loadable from `models/cnn_baseline.pth` at inference | Must |

### 3.3.4 Clinical workflow

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-W1 | Radiologists shall add investigation recommendation notes on completed jobs | Must |
| FR-W2 | Doctors shall submit clinical recommendation and optional notes on completed jobs | Must |
| FR-W3 | Patients shall view their own completed reports including AI result, radiologist notes, and doctor recommendation | Must |
| FR-W4 | Doctors and radiologists shall list all patients for scan assignment / review | Must |

### 3.3.5 Support modules

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-S1 | RAG advisory shall provide label-appropriate medical guidance text | Should |
| FR-S2 | Chatbot shall respond to FAQ queries in English and Nepali (prototype) | Could |
| FR-S3 | Hospital finder shall suggest neurology centres in Nepal | Should |
| FR-S4 | Report generation shall export HTML, JSON, and plain-text summaries per job | Must |

## 3.4 Non-Functional Requirements

| ID | Category | Requirement |
|----|----------|-------------|
| NFR-1 | **Performance** | Single scan pipeline completes within 60 seconds on development hardware (CPU) |
| NFR-2 | **Accuracy** | Validation accuracy ≥ 90% on held-out Grande Hospital data |
| NFR-3 | **Usability** | Dashboard usable on desktop browser (Chrome/Edge); responsive layout |
| NFR-4 | **Security** | Passwords hashed with bcrypt; JWT expiry 24 hours |
| NFR-5 | **Maintainability** | Separated frontend, backend, and ML modules; documented README |
| NFR-6 | **Reliability** | Job state persisted to disk; pipeline errors captured in job record |
| NFR-7 | **Portability** | Runs on Windows 10/11 with Python 3.11 and Node.js 18+ |
| NFR-8 | **Ethics** | Prominent disclaimer: research prototype, not for clinical diagnosis |
| NFR-9 | **Reproducibility** | Training script writes split manifest and metrics report to `results/` |
| NFR-10 | **Logging** | Step-by-step pipeline logging to console and `neuroscan.log` |

## 3.5 User Stories

### Radiologist

> **US-R1:** As a radiologist, I want to log in securely so that only authorised staff can upload patient scans.  
> **US-R2:** As a radiologist, I want to select a patient from a dropdown when uploading so that each scan is traceable.  
> **US-R3:** As a radiologist, I want to watch pipeline stages update live so that I know processing status.  
> **US-R4:** As a radiologist, I want to see the AI label, confidence, and Grad-CAM heatmap so that I can assess the prediction.  
> **US-R5:** As a radiologist, I want to save investigation notes so that the doctor and patient receive my recommendation.

### Doctor

> **US-D1:** As a doctor, I want to review AI results without upload access so that my role is clearly separated.  
> **US-D2:** As a doctor, I want to read radiologist notes alongside the AI output so that I have full context.  
> **US-D3:** As a doctor, I want to submit a clinical recommendation so that the patient receives authoritative guidance.

### Patient

> **US-P1:** As a patient, I want to log in with my unique ID visible so that I know my records are correctly linked.  
> **US-P2:** As a patient, I want to view only my own reports so that my privacy is protected.  
> **US-P3:** As a patient, I want to read the doctor's recommendation in plain language so that I understand next steps.

## 3.6 Constraints

1. **Dataset** — Anonymised 2D JPEG slices only; no patient identifiers in filenames or metadata exposed to the UI.
2. **Hardware** — Development and demo on consumer laptop; CUDA optional, CPU inference supported.
3. **Timeline** — Single academic year; binary classification chosen over multi-class to meet deadline.
4. **Regulation** — No medical device certification; academic prototype disclaimer required throughout UI.
5. **Language** — Primary UI in English; Nepali strings in chatbot prototype only.

## 3.7 MoSCoW Prioritisation Summary

| Priority | Features |
|----------|----------|
| **Must have** | Auth/RBAC, upload, 8-stage pipeline, CNN classification, Grad-CAM, doctor review, patient portal, reports |
| **Should have** | CLAHE QC gate, calibrated confidence, RAG advisory, hospital finder, radiologist notes |
| **Could have** | Bilingual chatbot, PDF export, email notifications |
| **Won't have (this release)** | DICOM/PACS, 3D volumes, multi-class tumours, cloud deployment |

## 3.8 Requirements Traceability (preview)

| Requirement | Design (Ch. 4) | Implementation (Ch. 5) |
|-------------|----------------|------------------------|
| FR-A1–A5 | §4.5 RBAC matrix | `src/auth.py`, `backend.py` |
| FR-U1–U6 | §4.2 Pipeline design | `backend.py`, `src/pipeline.py` |
| FR-C1–C5 | §4.3 ML module | `src/cnn_baseline.py`, `src/pipeline.py` |
| FR-W1–W4 | §4.4 Data model | Frontend pages, review endpoints |
| NFR-2 | §4.3 Training config | `results/cnn_baseline_report.txt` |

## 3.9 Summary

NeuroScan Nepal requirements balance clinical workflow realism with academic feasibility. Must-have features—RBAC, eight-stage pipeline, explainability, and three-role handover—were all implemented. Should-have features such as confidence calibration and quality gating were also delivered. Chapter 4 describes how these requirements were mapped to system design.

---

**Suggested word count:** ~1,500 words  
**Figures to add:** Use case diagram (three actors); requirements traceability matrix (optional).
