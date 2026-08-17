# NeuroScan Nepal: An AI-Assisted Brain MRI Screening Platform for Nepal

**Final Year Project Dissertation**

---

**Student:** Pragya Gajurel  
**Student ID:** 23189634  
**Programme:** BSc (Hons) Computer and Data Science  
**Institution:** Birmingham City University · Sunway College Kathmandu  
**Supervisor:** [Supervisor Name]  
**Submission Date:** [Month Year]

**Contact:** gajurelpragya@gmail.com

---

## Abstract

Brain MRI is a critical diagnostic tool for detecting neurological abnormalities, yet access to specialist radiologists remains limited in low- and middle-income countries such as Nepal. This project presents **NeuroScan Nepal**, a full-stack research prototype that combines deep learning, explainable AI, and role-based clinical workflow support to assist brain MRI screening.

The system implements an eight-stage processing pipeline: image upload, CLAHE-based preprocessing with quality control, convolutional neural network (CNN) classification, Grad-CAM explainability, retrieval-augmented medical advisory, bilingual chatbot support, hospital finder, and automated report generation. A custom three-block CNN was trained on approximately 1,600 anonymised brain MRI scans sourced from Grande International Hospital, Kathmandu, achieving **97.81% validation accuracy** and **98.12% balanced accuracy**. Temperature scaling was applied for probability calibration, and predictions below 70% confidence are flagged for human review.

The platform exposes three user roles—radiologist, doctor, and patient—enforced through JWT authentication and role-based access control (RBAC) on all API endpoints. Radiologists upload scans and add investigation notes; doctors provide clinical recommendations; patients view their own reports through a dedicated portal.

Evaluation on a held-out 25-image test set yielded **96% accuracy** through the live integration pipeline. This dissertation documents the problem context, literature review, requirements, system design, and implementation of NeuroScan Nepal. The artefact is intended for academic evaluation and feasibility demonstration only; it is not a certified medical device and must not be used for clinical diagnosis.

**Keywords:** brain MRI, deep learning, convolutional neural network, explainable AI, Grad-CAM, Nepal healthcare, role-based access control, medical image classification

---

## Acknowledgements

[Add personal acknowledgements to your supervisor, Grande International Hospital staff, family, and peers who supported usability testing.]

---

## Table of Contents

| Chapter | Title | File |
|---------|-------|------|
| 1 | Introduction | `Chapter_01_Introduction.md` |
| 2 | Literature Review | `Chapter_02_Literature_Review.md` |
| 3 | Requirements Analysis | `Chapter_03_Requirements.md` |
| 4 | System Design | `Chapter_04_Design.md` |
| 5 | Implementation | `Chapter_05_Implementation.md` |
| 6 | Testing | `Chapter_06_Testing.md` |
| 7 | Evaluation | `Chapter_07_Evaluation.md` |
| 8 | Ethics and Legal Considerations | `Chapter_08_Ethics.md` |
| 9 | Conclusion and Future Work | `Chapter_09_Conclusion.md` |

---

## How to use these drafts

1. Review each chapter markdown file in this folder.
2. Add screenshots from the live application where indicated with `[INSERT FIGURE]`.
3. Replace placeholder supervisor name, ethics approval reference, and submission date.
4. Run `py -3.11 scripts/generate_dissertation_doc.py` to compile the **full dissertation** into Word.
5. Use `LOGBOOK_FILLING_GUIDE.md` to copy weekly entries into Mahara.
