# Chapter 1: Introduction

## 1.1 Background

Neurological disorders, including brain tumours, stroke, and neurodegenerative conditions, represent a significant and growing burden on healthcare systems worldwide. Magnetic Resonance Imaging (MRI) is the gold-standard non-invasive modality for visualising brain tissue and detecting structural abnormalities. However, accurate MRI interpretation requires specialist radiological expertise, which is unevenly distributed globally.

Nepal, a low- and middle-income country in South Asia, faces particular challenges in neurological care. The country has a limited number of trained radiologists relative to its population of approximately 30 million, and specialist services are concentrated in urban centres such as Kathmandu, Lalitpur, and Pokhara. Patients in rural districts may wait weeks or travel long distances for MRI review. This access gap creates delays in diagnosis and treatment planning, with potentially serious consequences for conditions where early intervention improves outcomes.

Artificial intelligence (AI), and specifically deep learning applied to medical imaging, has demonstrated strong performance in automating or assisting abnormality detection in brain MRI scans. Convolutional Neural Networks (CNNs) can learn spatial features from large image datasets and achieve classification accuracy comparable to human experts on specific tasks. Explainable AI techniques such as Gradient-weighted Class Activation Mapping (Grad-CAM) further address the "black box" concern by highlighting image regions that influenced a model's decision.

Despite promising research results, few AI-assisted MRI screening systems have been designed with the Nepalese healthcare context in mind—incorporating local hospital data, bilingual support, referral pathways to Nepali hospitals, and workflow roles that reflect how radiologists, clinicians, and patients interact in practice.

## 1.2 Problem Statement

There is a need for a research prototype that demonstrates how AI-assisted brain MRI screening could support early abnormality detection in resource-limited settings such as Nepal. Specifically:

1. **Limited radiologist capacity** — The ratio of radiologists to population in Nepal is far below WHO recommendations, leading to delayed MRI reporting.
2. **No integrated local workflow** — Existing open-source medical AI tools typically provide classification APIs without role-based clinical workflows tailored to radiologist–doctor–patient handover.
3. **Trust and explainability gap** — Clinicians and patients are unlikely to accept AI outputs without visual explanation and clear disclaimers that the system assists rather than replaces human judgment.
4. **Data relevance** — Public datasets (e.g., Figshare, Kaggle) may not reflect the acquisition characteristics of scans collected at Nepali hospitals.

This project addresses these gaps by building **NeuroScan Nepal**: an end-to-end platform that classifies brain MRI scans as normal or abnormal, explains its predictions, and routes results through a three-role clinical workflow backed by anonymised data from Grande International Hospital, Kathmandu.

## 1.3 Aim and Objectives

### 1.3.1 Aim

To design, implement, and evaluate an AI-assisted brain MRI screening platform tailored to the Nepalese healthcare context, demonstrating feasibility for academic research and future clinical pilot studies.

### 1.3.2 Objectives

| # | Objective | Success criterion |
|---|-----------|-------------------|
| O1 | Collect and preprocess an anonymised brain MRI dataset from Grande International Hospital | ≥1,000 labelled scans in normal/abnormal classes |
| O2 | Train and evaluate a CNN classifier for binary abnormality detection | ≥90% validation accuracy on held-out data |
| O3 | Integrate explainability (Grad-CAM) and preprocessing quality control | Heatmaps generated for every processed scan |
| O4 | Build a full-stack web application with an eight-stage processing pipeline | All stages complete end-to-end via API |
| O5 | Implement role-based access control for radiologist, doctor, and patient roles | Each role restricted to permitted actions |
| O6 | Evaluate the live system on a representative test sample | Document accuracy and limitations in dissertation |

## 1.4 Scope

### 1.4.1 In scope

- Binary classification: **normal** vs **abnormal** brain MRI (single 2D slice per upload).
- Preprocessing: Contrast Limited Adaptive Histogram Equalisation (CLAHE), resize to 128×128 grayscale, low-contrast quality gate.
- CNN baseline model trained on Grande Hospital anonymised data (~1,600 scans).
- Grad-CAM visualisation, prototype RAG advisory text, bilingual chatbot stub, Nepal hospital finder, HTML/JSON report export.
- React frontend, FastAPI backend, JWT authentication, SQLite user store.
- Integration testing on 25 images; validation metrics on 320-image hold-out set.

### 1.4.2 Out of scope

- Multi-class tumour subtype classification (glioma, meningioma, pituitary, etc.).
- DICOM PACS integration or real hospital deployment.
- 3D volumetric MRI analysis.
- Certified medical device approval (FDA, CE, Nepal Medical Council).
- Production-grade cloud hosting, HL7/FHIR interoperability.
- Real-time tele-radiology or teleradiology billing.

## 1.5 Research Questions

1. Can a lightweight CNN achieve clinically useful binary classification accuracy on anonymised Grande Hospital brain MRI data?
2. How can explainability and confidence calibration improve trust in AI-assisted screening outputs?
3. What system architecture and RBAC design best support a radiologist → doctor → patient workflow in a prototype setting?
4. What are the ethical and practical limitations of deploying such a system in Nepal?

## 1.6 Contribution

This project contributes:

1. A **working software artefact** (NeuroScan Nepal) combining ML inference, explainability, and multi-role clinical workflow in one integrated platform.
2. A **locally relevant dataset application** — training and evaluation on Grande International Hospital anonymised scans rather than generic public datasets alone.
3. **Documented pipeline design** — an eight-stage architecture with step-by-step logging suitable for integration testing and demonstration.
4. **RBAC implementation** — practical JWT-based role enforcement across upload, review, and patient portal endpoints.
5. **Evaluation evidence** — 97.81% validation accuracy, 96% live integration test accuracy, with explicit limitation analysis.

## 1.7 Dissertation Structure

| Chapter | Content |
|---------|---------|
| **1 Introduction** | Background, problem, aims, scope, research questions |
| **2 Literature Review** | MRI AI, CNNs, XAI, Nepal healthcare, related systems |
| **3 Requirements** | Functional and non-functional requirements, user stories |
| **4 Design** | Architecture, pipeline, RBAC matrix, data model |
| **5 Implementation** | Technology stack, ML pipeline, frontend, backend, auth |
| **6 Testing** | Unit, integration, manual test plans *(Phase 3)* |
| **7 Evaluation** | Model metrics, usability, limitations *(Phase 3)* |
| **8 Ethics** | Data governance, consent, disclaimer *(Phase 4)* |
| **9 Conclusion** | Summary, achievements, future work *(Phase 4)* |

## 1.8 Summary

NeuroScan Nepal responds to a real access gap in neurological imaging services in Nepal by combining deep learning classification with explainability and structured clinical workflow support. The following chapters document how the system was specified, designed, built, and evaluated as a final-year research project at Birmingham City University.

---

**Suggested word count:** ~1,800 words  
**Figures to add:** Map of Nepal showing hospital concentration; optional photo of MRI scanner (with permission).
