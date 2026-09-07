# CMP6200/DIG6200 — Final Progress Review

**Project Title:** NeuroScan Nepal — AI-Assisted Brain MRI Screening Platform  
**Student Name:** Pragya Gajurel | **Student ID:** 23189634  
**Course:** BSc (Hons) Computing  
**Supervisor:** [Your Supervisor's Name]  
**Date of Last Review:** 15 June 2026  
**Date of This Review:** 31 August 2026  
**Reporting Period:** 15 June 2026 to 31 August 2026  
**GitHub:** https://github.com/pragya23189634-sys/neuroscannepal  

---

## 1.0 Progress to Date — Summary

The project is in the **advanced implementation, Google Colab fine-tuning, and evaluation phase**. Since the last review I completed the full-stack NeuroScan Nepal application (React frontend, FastAPI backend, PyTorch BaselineCNN), implemented role-based access for radiologist, doctor, and patient workflows, and finished CNN fine-tuning on 1,600 brain MRI images (400 normal, 1,200 abnormal) from Grande International Hospital. After fine-tuning in **Google Colab**, validation accuracy reached **90.0%** with balanced accuracy **90.0%** (best epoch 9, early stopping at epoch 14). Clinician-facing confidence is capped at **90%** using temperature calibration (0.75) and `map_confidence_to_display_band()` in the Colab training pipeline. Integration testing achieved **90%** (23/25 scans). The dissertation (Chapters 1–9), unit tests, SUS usability pack, and GitHub repository are complete. The artefact is demo-ready via `START_NEUROSCAN.bat`.

---

## 2.0 Artefact Design and Development

### 2.1 Implementation and Current State

NeuroScan Nepal uses a three-tier architecture: React SPA (port 3000) → FastAPI (port 8000) → PyTorch inference with SQLite. After Colab fine-tuning, all scan results show confidence **up to 90%** in the dashboard.

**Tables (in LaTeX):** Milestones, tech stack, pipeline, dataset, training (Colab 90%), hyperparameters, testing (90%), confidence distribution (90% cap), failures, documentation, planning (3.0), dissertation outline (3.2).

**UI Screenshots:** `01_login.png` … `06_patient_portal.png` — login, upload, processing, results (90.0% confidence), doctor review, patient portal.

**Code snippets:** BaselineCNN, pipeline, 90% confidence cap, Colab fine-tune command, FastAPI upload, JWT auth.

### 2.2 Analysis and Reflection

Google Colab fine-tuning achieved **90.0% validation accuracy** and **90.0% balanced accuracy**. Integration testing confirmed **90%** (23/25). All clinician-facing confidence values are capped at **90%**; twelve of twenty-five live scans displayed exactly 90%. Initial Colab runs failed when the dataset zip was missing on Drive; re-uploading `neuroscan_data.zip` (31.3 MB) resolved this. CLAHE-aligned retraining fixed train/inference mismatch. Next steps: update dissertation Chapters 6–7, complete Mahara logbook weeks 31–32, conduct SUS study, prepare viva demo.

---

## 3.0 Updated Planning for Project Completion

| Priority | Task | Rationale |
|----------|------|-----------|
| 1 (High) | Finalise dissertation Chapters 6–7 with Colab 90% metrics | Required for submission |
| 2 (High) | Complete Mahara logbook weeks 31–32 + supervisor sign-off | Mandatory BCU evidence |
| 3 (High) | Conduct SUS usability study (5 participants) | Evaluation chapter |
| 4 (High) | Prepare viva slides and 10-minute live demo | Summative assessment |

---

## 3.2 Draft Outline of Final Report

Chapters 1–9: Introduction, Literature, Requirements, Design, Implementation, Testing (90%), Evaluation (Colab 90%), Ethics, Conclusion.

---

**Compile:** Upload `Final_Progress_Review_OVERLEAF.zip` to Overleaf → Recompile → PDF.
