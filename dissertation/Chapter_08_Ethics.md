# Chapter 8: Ethics and Legal Considerations

## 8.1 Introduction

NeuroScan Nepal processes medical imaging data and presents AI-generated outputs in a clinical-adjacent context. Ethical and legal considerations therefore apply even though the artefact is an academic research prototype and not a deployed medical device. This chapter documents data governance, consent and anonymisation procedures, regulatory positioning, risk mitigation, and the limitations of AI-assisted screening in Nepal.

## 8.2 Ethical Approval

This project uses anonymised secondary data and a software prototype for academic evaluation. Ethics requirements were identified during Week 1–4 project planning:

| Stage | Action | Status |
|-------|--------|--------|
| Initial scoping | Discussed ethics requirements with supervisor | Completed |
| Proposal | Documented data handling and anonymisation plan | Completed |
| BCU ethics application | Submit ethics form if required by programme | **[Attach approval reference / form number]** |
| Usability testing | Information sheet + consent for peer participants | **[Attach if peer testing conducted]** |

**Note for submission:** Replace bracketed placeholders with your actual BCU ethics approval reference, submission date, and any participant information sheets. If your programme classified this as exempt (secondary anonymised data only), state the exemption category and supervisor confirmation.

## 8.3 Data Source and Anonymisation

### 8.3.1 Grande International Hospital dataset

The primary dataset comprises approximately **1,600 anonymised brain MRI scans** from Grande International Hospital, Kathmandu. The data was provided for academic research under agreed conditions:

- **No patient names, IDs, or dates** appear in filenames, image metadata exposed to the application, or dissertation appendices.
- Scans are stored locally in `data/raw/normal/` and `data/raw/abnormal/` and are **not committed to version control** (listed in `.gitignore`).
- Labels are binary (normal vs abnormal) for screening research, not individual patient diagnoses for clinical use.

### 8.3.2 Data handling principles

| Principle | Implementation |
|-----------|----------------|
| **Minimisation** | Only 2D slice images required for classification; no full DICOM with embedded PHI |
| **Purpose limitation** | Used solely for model training, testing, and academic demonstration |
| **Storage** | Local development machine; not uploaded to public cloud |
| **Access control** | Dataset accessible only to the student and supervisor |
| **Retention** | Retained for project duration and examination; disposal per hospital/university agreement |
| **Anonymisation** | Patient identifiers removed before transfer to researcher |

### 8.3.3 Synthetic and demo data

Demo user accounts (`radiologist@neuroscan.np`, etc.) use fictitious names (Kishor Phuyal, Dr. Bikram Prasad Gajurel, Ram Bahadur Thapa) and are not linked to real patients. Uploaded test scans during demonstration use anonymised dataset images, not live patient data.

## 8.4 Privacy and Security

### 8.4.1 Application security

| Control | Description |
|---------|-------------|
| Password hashing | bcrypt with per-user salt |
| Authentication | JWT bearer tokens, 24-hour expiry |
| Authorisation | Role-based access on all protected endpoints |
| Patient isolation | Patients can only view their own job records |
| HTTPS | Recommended for production; localhost used in development |

### 8.4.2 Privacy by design

- Patient unique IDs (`NSN-PAT-XXXXXX`) are system-generated pseudonyms, not national health IDs.
- Job records link scans to patient user accounts within the prototype only.
- No personal data is transmitted to external APIs (RAG/chatbot are local rule-based modules).

### 8.4.3 Known security limitations (prototype)

- JWT secret defaults to a development value (`NEUROSCAN_JWT_SECRET` environment variable should be set in production).
- SQLite and `jobs.json` are not encrypted at rest.
- No audit trail for clinical medico-legal purposes.
- These limitations are acceptable for academic demonstration but must be addressed before any real deployment.

## 8.5 Clinical Ethics and AI Governance

### 8.5.1 Not a medical device

NeuroScan Nepal is explicitly labelled as a **research prototype**:

- The About page states: *"This is a research prototype for academic evaluation… not a certified medical device and must not be used for clinical diagnosis."*
- RAG advisory and chatbot outputs include disclaimers that they do not constitute medical advice.
- The system is designed as **decision support** requiring radiologist upload and doctor sign-off, not autonomous diagnosis.

### 8.5.2 Human-in-the-loop design

Ethical AI practice requires human oversight. NeuroScan Nepal enforces this through workflow design:

```
Radiologist uploads → AI classifies → Radiologist adds notes → Doctor recommends → Patient reads report
```

At no stage does the patient receive AI output without clinician review pathways. Predictions below 70% confidence are flagged for additional human review.

### 8.5.3 Risk of harm

| Risk | Mitigation |
|------|------------|
| **False negative** (missed abnormality) | Doctor review stage; disclaimer; not for unsupervised use |
| **False positive** ( unnecessary anxiety) | Doctor recommendation; explainability via Grad-CAM; documented error case (Te-no_150.jpg) |
| **Over-reliance on AI** | UI disclaimers; confidence bands; academic framing |
| **Data breach** | RBAC; local storage; no cloud upload in prototype |
| **Algorithmic bias** | Balanced accuracy reporting; local dataset; limitations documented |

### 8.5.4 Explainability as ethical requirement

Grad-CAM heatmaps address the "black box" concern by showing which image regions influenced the classification. This supports clinician scrutiny and aligns with emerging expectations for explainable AI in healthcare (Holzinger et al., 2019).

## 8.6 Legal and Regulatory Context

### 8.6.1 Nepal

Medical device and digital health regulation in Nepal is evolving. NeuroScan Nepal has **not** been submitted to the Nepal Medical Council, Department of Drug Administration, or any regulatory body. It cannot legally be marketed or used for clinical diagnosis in Nepal without appropriate approval.

### 8.6.2 United Kingdom (BCU)

As a Birmingham City University final-year project, the artefact is assessed as academic work. It does not require UKCA or CE marking. If the project were to continue toward commercialisation, MHRA guidance on software as a medical device (SaMD) would apply.

### 8.6.3 Intellectual property

- **Student authorship:** Software code and dissertation written by the student.
- **Dataset ownership:** Remains with Grande International Hospital; used under research agreement.
- **Third-party libraries:** PyTorch, React, FastAPI — open-source licences (MIT, Apache, BSD) complied with via dependency declarations in `requirements.txt`.

## 8.7 Usability Testing Ethics

If peer usability testing was conducted (recommended: 3–5 participants):

| Requirement | Detail |
|-------------|--------|
| **Information sheet** | Explain project purpose, voluntary participation, data collected |
| **Consent form** | Signed before testing; right to withdraw |
| **Data collected** | Task completion times, SUS scores, qualitative feedback — no health data |
| **Anonymisation** | Participant names not published; use IDs (P1, P2…) in dissertation |
| **Storage** | Consent forms stored securely; destroyed per university policy after examination |

**[Attach: Participant Information Sheet and Consent Form if applicable]**

## 8.8 GDPR and Data Protection

Although the primary dataset is anonymised hospital data from Nepal, BCU students may also be subject to UK GDPR for any personal data processed (e.g., usability participant emails). Principles applied:

- Lawful basis: consent (participants) / legitimate interest (academic assessment)
- Data minimisation: collect only what is needed
- Right to erasure: participants may withdraw and request deletion
- No cross-border transfer of identifiable patient data

## 8.9 Ethical Limitations Acknowledged

1. Retrospective use of labelled scans without prospective patient consent for AI research (mitigated by hospital anonymisation and research agreement).
2. No independent ethics review board approval from a Nepali institution documented here — **[add if applicable]**.
3. Prototype accuracy (96% on small sample) insufficient to justify clinical deployment.
4. Rule-based RAG/chatbot could mislead if disclaimers are ignored — mitigated by prominent UI warnings.

## 8.10 Summary

NeuroScan Nepal was developed with awareness of ethical obligations around medical data, AI transparency, and human oversight. Anonymised Grande Hospital data was handled under agreed research conditions. The application includes disclaimers, RBAC, and a clinician-in-the-loop workflow. Regulatory approval was not sought because the project is an academic prototype. Before any real-world deployment in Nepal, formal ethics review, clinical validation, and regulatory assessment would be required.

---

**Suggested word count:** ~1,800 words  
**Attachments for submission folder:** BCU ethics approval, data handling agreement, consent forms (if used).
