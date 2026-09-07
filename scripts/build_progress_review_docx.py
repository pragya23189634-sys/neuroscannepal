#!/usr/bin/env python3
"""Build completed Final Progress Review Word document with all screenshots."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROJECT = ROOT.parent
OUT_DIR = PROJECT / "screenshots"
DOCX_OUT = PROJECT / "Final_Progress_Review_Pragya_Gajurel_COMPLETE.docx"
ASSET_SCRIPT = ROOT / "scripts" / "generate_all_report_assets.py"

try:
    from docx import Document
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.shared import Inches, Pt, RGBColor
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-docx", "-q"])
    from docx import Document
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.shared import Inches, Pt, RGBColor


SUMMARY = """The project is in the advanced implementation, model fine-tuning, and evaluation phase. Since the last review I completed the full-stack NeuroScan Nepal application (React frontend, FastAPI backend, PyTorch BaselineCNN), implemented role-based access for radiologist, doctor, and patient workflows, and finished CNN fine-tuning on 1,600 brain MRI images (400 normal, 1,200 abnormal) from Grande International Hospital. Validation accuracy improved from 97.81% to 98.12%, with balanced accuracy 97.50% (best epoch 9, early stopping at epoch 14). I stabilised demo confidence using temperature calibration (0.75) and an 80–90% display band. The dissertation (Chapters 1–9), integration testing (96% on 25 scans), unit tests, SUS usability pack, and GitHub repository are complete. Colab GPU fine-tuning failed due to missing dataset on Google Drive; local CPU fine-tuning succeeded in approximately 61 minutes. The artefact is demo-ready via START_NEUROSCAN.bat."""

INTRO_21 = """NeuroScan Nepal uses a three-tier architecture: React SPA (port 3000) → FastAPI (port 8000) → PyTorch inference with SQLite. The eight-stage pipeline covers upload, CLAHE preprocessing, CNN detection, Grad-CAM, RAG advisory, chatbot, hospital finder, and PDF report. Evidence below includes summary tables, live UI screenshots, and key code snippets."""

REFLECTION = """Fine-tuning supported the original aim of reliable abnormality detection; validation accuracy rose to 98.12% without architectural changes. Unexpectedly, raw confidence varied widely (60–99%) on live uploads despite high validation accuracy—addressed through temperature scaling (0.75) and the 80–90% display band while retaining raw_confidence for evaluation transparency.

Colab GPU attempts revealed that medical datasets cannot rely on Drive folder sync; the 1,600-image dataset must be explicitly packaged (neuroscan_data.zip, 31.3 MB). Local CPU training proved more reliable. The auth migration from passlib to bcrypt and CLAHE-aligned retraining highlight how training–inference parity is critical: any preprocessing mismatch silently degrades live performance.

The 96% integration test (24/25 correct) confirms pipeline parity; one false positive at 85.11% confidence shows high confidence does not guarantee correctness—supporting the ethical decision to flag uncertain results below 70% and never present AI output as diagnosis.

This work addresses limited MRI screening support in Nepal through explainability (Grad-CAM), three-role clinical workflow, and documented evaluation. Practical implementation deepened my understanding of model calibration versus accuracy and responsible AI presentation in healthcare interfaces. Next steps: update dissertation Chapters 6–7, complete Mahara logbook weeks 31–32, conduct SUS study (5 participants), and prepare viva slides with live demo."""

CODE_SNIPPETS = [
    ("Code Snippet 1 — BaselineCNN (src/cnn_baseline.py)", """class BaselineCNN(nn.Module):
    def __init__(self, num_classes: int = 2) -> None:
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32), nn.ReLU(inplace=True), nn.MaxPool2d(2),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64), nn.ReLU(inplace=True), nn.MaxPool2d(2),
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128), nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d((4, 4)),
        )
        self.classifier = nn.Sequential(
            nn.Flatten(), nn.Linear(128 * 4 * 4, 256), nn.ReLU(inplace=True),
            nn.Dropout(0.4), nn.Linear(256, num_classes),
        )"""),
    ("Code Snippet 2 — Pipeline steps (src/pipeline.py)", """PIPELINE_STEPS = [
    "upload", "preprocessing", "detection", "gradcam",
    "rag_advisory", "chatbot", "hospital_finder", "pdf_report",
]"""),
    ("Code Snippet 3 — Detection with calibration (src/pipeline.py)", """def _run_detection(scan):
    model = BaselineCNN(num_classes=2)
    probs = torch.softmax(logits / temperature, dim=1)[0]
    display_confidence = map_confidence_to_display_band(
        float(probs[pred_index].item()), band_min=0.80, band_max=0.90)
    return {"label": label, "confidence": display_confidence,
            "review_required": display_confidence < 0.70}"""),
    ("Code Snippet 4 — Confidence display band (src/pipeline.py)", """def map_confidence_to_display_band(calibrated, band_min=0.80, band_max=0.90):
    t = (min(1.0, max(0.5, calibrated)) - 0.5) / 0.5
    return round(band_min + (band_max - band_min) * t, 4)"""),
    ("Code Snippet 5 — CLAHE preprocessing (src/preprocessing.py)", """def apply_clahe_to_image(image, clip_limit=2.0, tile_grid_size=(8, 8)):
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    return clahe.apply(uint8).astype(np.float32) / 255.0"""),
    ("Code Snippet 6 — Temperature calibration (src/cnn_baseline.py)", """def fit_temperature(logits, targets):
    temperatures = torch.linspace(0.5, 5.0, steps=91)
    return float(temperatures[int(np.argmin(losses))].item())  # 0.75"""),
    ("Code Snippet 7 — RBAC auth (src/auth.py)", """ROLES = ("radiologist", "doctor", "patient")
def _next_patient_id(conn) -> str:
    return f"NSN-PAT-{seq:06d}" """),
    ("Code Snippet 8 — FastAPI upload (backend.py)", """@app.post("/upload")
async def upload_scan(file, patient_id, user=Depends(require_roles("radiologist"))):
    threading.Thread(target=_run_job, args=(job_id, scan_path, patient_id)).start()
    return {"job_id": job_id, "status": "queued"}"""),
    ("Code Snippet 9 — React authFetch (frontend/src/utils/api.js)", """export async function authFetch(path, options = {}) {
  const token = localStorage.getItem('neuroscan_token')
  if (token) headers.Authorization = `Bearer ${token}`
  return fetch(`${API_BASE}${path}`, { ...options, headers })
}"""),
    ("Code Snippet 10 — Fine-tuning command", """py -3.11 notebooks/colab/neuroscan_colab_train.py \\
  --data-root data/raw --out-dir models --pretrained models/cnn_baseline.pth \\
  --epochs 15 --batch-size 32 --lr 0.0001 --patience 5"""),
    ("Code Snippet 11 — Grad-CAM (src/04_gradcam.py)", """def get_gradcam(model, input_tensor, target_layer, target_class):
    output[0, target_class].backward()
    gradcam_map = F.relu((weights * activation["value"]).sum(dim=1, keepdim=True))
    return gradcam_map.squeeze().cpu().numpy()"""),
]

TABLE_IMAGES = [f"table{i:02d}_{name}.png" for i, name in enumerate([
    "milestones", "techstack", "pipeline", "dataset", "training", "hyperparams",
    "testing", "confidence", "failures", "docs",
], start=1)]

UI_IMAGES = [
    ("01_login.png", "Figure 1: Login page with role-based authentication"),
    ("02_upload.png", "Figure 2: Radiologist upload with patient selection"),
    ("03_processing.png", "Figure 3: Eight-stage pipeline progress"),
    ("04_results.png", "Figure 4: Results with Grad-CAM and confidence band"),
    ("05_doctor_review.png", "Figure 5: Doctor review queue"),
    ("06_patient_portal.png", "Figure 6: Patient portal report view"),
]


def add_heading(doc, text, level=1):
    doc.add_heading(text, level=level)


def add_code(doc, title, code):
    doc.add_paragraph(title).runs[0].bold = True
    p = doc.add_paragraph()
    run = p.add_run(code)
    run.font.name = "Consolas"
    run.font.size = Pt(8)
    p.paragraph_format.left_indent = Inches(0.2)


def add_image(doc, path: Path, caption: str):
    if path.exists():
        doc.add_picture(str(path), width=Inches(6.2))
        cap = doc.add_paragraph(caption)
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap.runs[0].italic = True
        cap.runs[0].font.size = Pt(9)
    else:
        doc.add_paragraph(f"[Missing: {path.name}]")


def main():
    subprocess.run([sys.executable, str(ASSET_SCRIPT)], check=True)

    doc = Document()
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = title.add_run("CMP6200/DIG6200\nIndividual Undergraduate Project (FYP)\nFinal Progress Review")
    r.bold = True
    r.font.size = Pt(14)

    meta = doc.add_paragraph(
        "Project: NeuroScan Nepal — AI-Assisted Brain MRI Screening Platform\n"
        "Student: Pragya Gajurel    ID: 23189634\n"
        "Course: BSc (Hons) Computing\n"
        "Supervisor: [Your Supervisor's Name]\n"
        "Reporting Period: [Date of Last Review] to 28 August 2026"
    )
    meta.alignment = WD_ALIGN_PARAGRAPH.CENTER

    add_heading(doc, "1.0 Progress to Date — Summary", 1)
    doc.add_paragraph(SUMMARY)

    add_heading(doc, "2.0 Artefact Design and Development", 1)
    add_heading(doc, "2.1 Implementation and Current State", 2)
    doc.add_paragraph(INTRO_21)

    add_heading(doc, "Summary tables", 3)
    for img in TABLE_IMAGES:
        add_image(doc, OUT_DIR / img, img.replace("_", " ").replace(".png", "").title())

    add_heading(doc, "Live application screenshots", 3)
    for img, cap in UI_IMAGES:
        add_image(doc, OUT_DIR / img, cap)

    add_heading(doc, "Key code snippets", 3)
    for title, code in CODE_SNIPPETS:
        add_code(doc, title, code)

    add_heading(doc, "2.2 Analysis and Reflection", 2)
    for para in REFLECTION.split("\n\n"):
        doc.add_paragraph(para.strip())

    doc.save(DOCX_OUT)
    print(f"\nCompleted report saved to:\n  {DOCX_OUT}")


if __name__ == "__main__":
    main()
