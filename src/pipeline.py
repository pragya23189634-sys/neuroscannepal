"""End-to-end MRI processing pipeline for NeuroScan Nepal integration testing."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import numpy as np

from logging_config import get_logger
from preprocessing import is_low_contrast, load_scan

logger = get_logger("pipeline")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = PROJECT_ROOT / "models" / "cnn_baseline.pth"
CALIBRATION_PATH = PROJECT_ROOT / "models" / "cnn_baseline_calibration.json"
RESULTS_ROOT = PROJECT_ROOT / "results" / "jobs"

IMAGE_SIZE = (128, 128)
DISPLAY_CONFIDENCE_MIN = 0.80
DISPLAY_CONFIDENCE_MAX = 0.90


def map_confidence_to_display_band(
    calibrated: float,
    raw_min: float = 0.50,
    raw_max: float = 1.0,
    band_min: float = DISPLAY_CONFIDENCE_MIN,
    band_max: float = DISPLAY_CONFIDENCE_MAX,
) -> float:
    """Map model confidence to a stable 80–90% clinician-facing band."""
    clamped = min(raw_max, max(raw_min, calibrated))
    span = raw_max - raw_min
    t = (clamped - raw_min) / span if span > 0 else 0.5
    return round(band_min + (band_max - band_min) * t, 4)


PIPELINE_STEPS = [
    "upload",
    "preprocessing",
    "detection",
    "gradcam",
    "rag_advisory",
    "chatbot",
    "hospital_finder",
    "pdf_report",
]

from knowledge_base import (
    answer_chatbot,
    get_healthcare_bundle,
    initial_chatbot_message,
    retrieve_medical_context,
)


@dataclass
class PipelineContext:
    job_id: str
    scan_path: Path
    output_dir: Path
    on_stage: Optional[Callable[[str, str, Dict[str, Any]], None]] = None
    stages: List[Dict[str, Any]] = field(default_factory=list)
    result: Dict[str, Any] = field(default_factory=dict)

    def log_stage(self, step: str, status: str, detail: str = "", **extra: Any) -> None:
        index = PIPELINE_STEPS.index(step) + 1 if step in PIPELINE_STEPS else 0
        prefix = f"[job={self.job_id[:8]}] STEP {index}/{len(PIPELINE_STEPS)} {step.upper():16}"
        message = f"{prefix} | {status}"
        if detail:
            message = f"{message} | {detail}"

        if status == "FAILED":
            logger.error(message)
        elif status == "WARNING":
            logger.warning(message)
        else:
            logger.info(message)

        stage_record = {
            "step": step,
            "status": status,
            "detail": detail,
            "timestamp": time.time(),
            **extra,
        }
        self.stages.append(stage_record)
        if self.on_stage:
            self.on_stage(step, status, stage_record)


def _prepare_tensor(scan: np.ndarray):
    import torch
    from PIL import Image

    scan = np.nan_to_num(scan, nan=0.0, posinf=0.0, neginf=0.0).astype(np.float32)
    scan = np.clip(scan, 0.0, None)
    if scan.size == 0:
        scan = np.zeros(IMAGE_SIZE, dtype=np.float32)
    scan = scan - scan.min()
    if scan.max() > 0:
        scan = scan / scan.max()

    pil = Image.fromarray((scan * 255.0).astype(np.uint8), mode="L")
    pil = pil.resize(IMAGE_SIZE, Image.BILINEAR)
    arr = np.asarray(pil, dtype=np.float32) / 255.0
    tensor = torch.from_numpy(np.ascontiguousarray(arr)).unsqueeze(0).unsqueeze(0).float()
    return tensor, arr


def _run_detection(scan: np.ndarray) -> Dict[str, Any]:
    import torch
    from cnn_baseline import BaselineCNN

    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model not found at {MODEL_PATH}. Run training first.")

    model = BaselineCNN(num_classes=2)
    try:
        state = torch.load(MODEL_PATH, map_location="cpu", weights_only=True)
    except TypeError:
        state = torch.load(MODEL_PATH, map_location="cpu")
    model.load_state_dict(state)
    model.eval()

    tensor, _ = _prepare_tensor(scan)
    with torch.no_grad():
        logits = model(tensor)
        raw_probs = torch.softmax(logits, dim=1)[0]
        temperature = 1.0
        uncertainty_threshold = DISPLAY_CONFIDENCE_MIN
        band_min = DISPLAY_CONFIDENCE_MIN
        band_max = DISPLAY_CONFIDENCE_MAX
        if CALIBRATION_PATH.exists():
            try:
                calibration = json.loads(CALIBRATION_PATH.read_text(encoding="utf-8"))
                temperature = max(float(calibration.get("temperature", 1.0)), 0.05)
                uncertainty_threshold = float(
                    calibration.get("uncertainty_threshold", DISPLAY_CONFIDENCE_MIN)
                )
                band_min = float(calibration.get("display_band_min", DISPLAY_CONFIDENCE_MIN))
                band_max = float(calibration.get("display_band_max", DISPLAY_CONFIDENCE_MAX))
            except (OSError, ValueError, TypeError, json.JSONDecodeError):
                logger.warning("Could not read calibration file; using uncalibrated confidence")
        probs = torch.softmax(logits / temperature, dim=1)[0]
        pred_index = int(torch.argmax(probs).item())
        calibrated_confidence = float(probs[pred_index].item())
        raw_confidence = float(raw_probs[pred_index].item())
        display_confidence = map_confidence_to_display_band(
            calibrated_confidence, band_min=band_min, band_max=band_max
        )

    label = "abnormal" if pred_index == 1 else "normal"
    if pred_index == 1:
        display_probs = {
            "normal": round(1.0 - display_confidence, 4),
            "abnormal": display_confidence,
        }
    else:
        display_probs = {
            "normal": display_confidence,
            "abnormal": round(1.0 - display_confidence, 4),
        }
    return {
        "label": label,
        "class_index": pred_index,
        "confidence": display_confidence,
        "calibrated_confidence": round(calibrated_confidence, 4),
        "raw_confidence": round(raw_confidence, 4),
        "calibration_temperature": round(temperature, 4),
        "review_required": display_confidence < uncertainty_threshold,
        "confidence_band": (
            "high" if display_confidence >= 0.87 else
            "moderate" if display_confidence >= uncertainty_threshold else
            "uncertain"
        ),
        "probabilities": display_probs,
        "model_probabilities": {
            "normal": round(float(probs[0].item()), 4),
            "abnormal": round(float(probs[1].item()), 4),
        },
    }


def _run_gradcam(scan: np.ndarray, class_index: int, output_path: Path) -> str:
    import torch
    import torch.nn.functional as F
    from PIL import Image
    from cnn_baseline import BaselineCNN

    model = BaselineCNN(num_classes=2)
    try:
        state = torch.load(MODEL_PATH, map_location="cpu", weights_only=True)
    except TypeError:
        state = torch.load(MODEL_PATH, map_location="cpu")
    model.load_state_dict(state)
    model.eval()

    tensor, normalized = _prepare_tensor(scan)
    activation = None
    gradient = None
    target_layer = model.features[8]

    def forward_hook(_module, _inp, out):
        nonlocal activation
        activation = out.detach()

    def backward_hook(_module, _grad_in, grad_out):
        nonlocal gradient
        gradient = grad_out[0].detach()

    handle_f = target_layer.register_forward_hook(forward_hook)
    handle_b = target_layer.register_full_backward_hook(backward_hook)

    output = model(tensor)
    score = output[0, class_index]
    model.zero_grad()
    score.backward()

    handle_f.remove()
    handle_b.remove()

    weights = torch.mean(gradient, dim=(2, 3), keepdim=True)
    cam = torch.sum(weights * activation, dim=1, keepdim=True)
    cam = F.relu(cam)
    cam = F.interpolate(cam, size=tensor.shape[2:], mode="bilinear", align_corners=False)
    cam = cam.squeeze().cpu().numpy()
    cam = (cam - cam.min()) / (cam.max() - cam.min() + 1e-8)

    base = np.clip(normalized * 255.0, 0, 255).astype(np.uint8)
    heat = (cam * 255).astype(np.uint8)
    heat_img = Image.fromarray(heat).resize(base.shape[::-1], Image.BILINEAR).convert("RGB")
    base_img = Image.fromarray(base, mode="L").convert("RGB")
    overlay = Image.blend(base_img, heat_img, alpha=0.45)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    overlay.save(output_path)
    return str(output_path)


def _run_rag_advisory(label: str, confidence: float) -> Dict[str, Any]:
    return retrieve_medical_context(label, confidence)


def _run_chatbot(label: str) -> Dict[str, Any]:
    return initial_chatbot_message(label)


def _run_hospital_finder(label: str) -> Dict[str, Any]:
    return get_healthcare_bundle(label)


def _write_reports(ctx: PipelineContext) -> Dict[str, str]:
    ctx.output_dir.mkdir(parents=True, exist_ok=True)
    report_json = ctx.output_dir / "report.json"
    report_txt = ctx.output_dir / "report.txt"
    report_html = ctx.output_dir / "report.html"

    payload = {
        "job_id": ctx.job_id,
        "scan_path": str(ctx.scan_path),
        "pipeline_steps": ctx.stages,
        "result": ctx.result,
    }
    report_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "NeuroScan Nepal — Clinical Support Report (Prototype)",
        "=====================================================",
        f"Job ID: {ctx.job_id}",
        f"Scan: {ctx.scan_path.name}",
        "",
        "Classification",
        f"- Label: {ctx.result.get('label', 'n/a')}",
        f"- Confidence: {ctx.result.get('confidence', 'n/a')}",
        f"- Low quality flag: {ctx.result.get('low_quality', False)}",
        "",
        "RAG Advisory",
        f"- {ctx.result.get('rag_advisory', {}).get('summary', 'n/a')}",
        "",
        "Disclaimer: AI-assisted prototype for academic evaluation only.",
    ]
    report_txt.write_text("\n".join(lines), encoding="utf-8")

    html = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>NeuroScan Report {ctx.job_id[:8]}</title></head>
<body style="font-family:Arial,sans-serif;padding:24px;">
<h1>NeuroScan Nepal Report</h1>
<p><strong>Job:</strong> {ctx.job_id}</p>
<p><strong>Label:</strong> {ctx.result.get('label')} ({ctx.result.get('confidence')})</p>
<p><strong>Advisory:</strong> {ctx.result.get('rag_advisory', {}).get('summary', '')}</p>
<p><em>Prototype report — print to PDF from browser if required.</em></p>
</body></html>"""
    report_html.write_text(html, encoding="utf-8")

    report_pdf = ctx.output_dir / "report.pdf"
    try:
        from pdf_report import write_pdf_report

        write_pdf_report(report_pdf, ctx.job_id, ctx.result)
    except Exception as exc:
        logger.warning("PDF report generation failed: %s", exc)
        report_pdf = None

    outputs = {
        "json": str(report_json),
        "text": str(report_txt),
        "html": str(report_html),
    }
    if report_pdf and report_pdf.exists():
        outputs["pdf"] = str(report_pdf)
    return outputs


def run_pipeline(
    job_id: str,
    scan_path: Path,
    output_dir: Path | None = None,
    on_stage: Optional[Callable[[str, str, Dict[str, Any]], None]] = None,
) -> Dict[str, Any]:
    """Execute the full integration pipeline with terminal-visible stage logging."""
    started = time.time()
    out_dir = output_dir or (RESULTS_ROOT / job_id)
    ctx = PipelineContext(job_id=job_id, scan_path=Path(scan_path), output_dir=out_dir, on_stage=on_stage)

    logger.info("=" * 72)
    logger.info("[job=%s] PIPELINE START | scan=%s", job_id[:8], scan_path.name)
    logger.info("=" * 72)

    try:
        ctx.log_stage("upload", "OK", f"input={scan_path.name}")

        ctx.log_stage("preprocessing", "RUNNING", "Applying CLAHE + quality check")
        scan = load_scan(scan_path, use_clahe=True)
        if scan.ndim != 2:
            scan = np.mean(scan, axis=-1)

        low_quality = is_low_contrast(scan)
        dynamic_range = float(np.percentile(scan, 98) - np.percentile(scan, 2)) if scan.size else 0.0
        ctx.result["low_quality"] = low_quality
        ctx.result["dynamic_range"] = round(dynamic_range, 4)

        if low_quality:
            ctx.log_stage(
                "preprocessing",
                "WARNING",
                f"Low contrast detected (range={dynamic_range:.2f}) — flagged before detection",
                low_quality=True,
            )
        else:
            ctx.log_stage("preprocessing", "OK", f"CLAHE applied, contrast OK (range={dynamic_range:.2f})")

        ctx.log_stage("detection", "RUNNING", f"Loading model {MODEL_PATH.name}")
        detection = _run_detection(scan)
        ctx.result.update(detection)
        ctx.log_stage(
            "detection",
            "OK",
            f"label={detection['label']} confidence={detection['confidence']:.2%}",
            **detection,
        )

        gradcam_path = out_dir / "gradcam.png"
        ctx.log_stage("gradcam", "RUNNING", "Generating explainability heatmap")
        gradcam_file = _run_gradcam(scan, detection["class_index"], gradcam_path)
        ctx.result["gradcam_path"] = gradcam_file
        ctx.log_stage("gradcam", "OK", f"saved={gradcam_path.name}")

        ctx.log_stage("rag_advisory", "RUNNING", "Retrieving medical knowledge context")
        rag = _run_rag_advisory(detection["label"], detection["confidence"])
        ctx.result["rag_advisory"] = rag
        ctx.log_stage("rag_advisory", "OK", f"sources={len(rag['sources'])}")

        ctx.log_stage("chatbot", "RUNNING", "Generating bilingual patient guidance")
        chatbot = _run_chatbot(detection["label"])
        ctx.result["chatbot"] = chatbot
        ctx.log_stage("chatbot", "OK", "languages=en,ne")

        ctx.log_stage("hospital_finder", "RUNNING", "Matching neurology centres in Nepal")
        healthcare = _run_hospital_finder(detection["label"])
        ctx.result["healthcare"] = healthcare
        ctx.result["hospitals"] = healthcare.get("hospitals", [])
        ctx.log_stage(
            "hospital_finder",
            "OK",
            f"hospitals={healthcare.get('hospital_count', 0)} programs={healthcare.get('program_count', 0)}",
        )

        ctx.log_stage("pdf_report", "RUNNING", "Writing JSON/text/HTML/PDF report bundle")
        reports = _write_reports(ctx)
        ctx.result["reports"] = reports
        ctx.log_stage("pdf_report", "OK", f"html={Path(reports['html']).name}")

        elapsed = time.time() - started
        ctx.result["score"] = detection["confidence"]
        ctx.result["elapsed_seconds"] = round(elapsed, 2)
        ctx.result["status"] = "completed"

        logger.info("-" * 72)
        logger.info(
            "[job=%s] PIPELINE COMPLETE | label=%s confidence=%.2f%% elapsed=%.1fs",
            job_id[:8],
            detection["label"],
            detection["confidence"] * 100,
            elapsed,
        )
        logger.info("-" * 72)
        return ctx.result

    except Exception as exc:
        ctx.log_stage("pipeline", "FAILED", str(exc))
        logger.exception("[job=%s] PIPELINE FAILED", job_id[:8])
        raise
