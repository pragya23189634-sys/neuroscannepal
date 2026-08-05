"""NeuroScan Nepal FastAPI backend with full pipeline logging."""

from __future__ import annotations

import json
import os
import sys
import threading
import time
import uuid
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Make src/ importable from project root
PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from logging_config import setup_logging  # noqa: E402

logger = setup_logging(log_dir=PROJECT_ROOT, level=os.getenv("NEUROSCAN_LOG_LEVEL", "INFO"))

try:
    from pipeline import PIPELINE_STEPS, run_pipeline  # noqa: E402

    PIPELINE_AVAILABLE = True
except ImportError as exc:
    PIPELINE_AVAILABLE = False
    logger.error("Pipeline modules unavailable: %s", exc)
    logger.error("Run backend with Python 3.11+ and install torch: pip install torch torchvision")

app = FastAPI(title="NeuroScan Nepal API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

WORKDIR = PROJECT_ROOT
UPLOAD_DIR = WORKDIR / "uploads"
RESULTS_DIR = WORKDIR / "results" / "jobs"
JOBS_FILE = WORKDIR / "jobs.json"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

if JOBS_FILE.exists():
    try:
        JOBS: Dict[str, Dict[str, Any]] = json.loads(JOBS_FILE.read_text(encoding="utf-8"))
    except Exception:
        logger.exception("Failed to load jobs.json — starting fresh")
        JOBS = {}
else:
    JOBS = {}

JOBS_LOCK = threading.RLock()


def save_jobs() -> None:
    tmp = JOBS_FILE.with_suffix(".json.tmp")
    try:
        with JOBS_LOCK:
            tmp.write_text(json.dumps(JOBS, indent=2), encoding="utf-8")
            tmp.replace(JOBS_FILE)
        logger.debug("Persisted %d job(s) to %s", len(JOBS), JOBS_FILE.name)
    except Exception:
        logger.exception("Failed to save jobs file")
        if tmp.exists():
            tmp.unlink(missing_ok=True)


def _update_job(job_id: str, **fields: Any) -> None:
    with JOBS_LOCK:
        if job_id in JOBS:
            JOBS[job_id].update(fields)
            save_jobs()


def _on_pipeline_stage(job_id: str, step: str, status: str, record: Dict[str, Any]) -> None:
    with JOBS_LOCK:
        job = JOBS.get(job_id)
        if not job:
            return
        job.setdefault("stages", []).append(record)
        job["current_step"] = step
        job["step_status"] = status
        save_jobs()


def process_job(job_id: str, filepath: str) -> None:
    """Run the full MRI pipeline and stream progress to terminal + job store."""
    logger.info("[job=%s] Worker thread started", job_id[:8])
    _update_job(job_id, status="running", current_step="upload", step_status="RUNNING", started_at=time.time())

    if not PIPELINE_AVAILABLE:
        _update_job(
            job_id,
            status="failed",
            error="Pipeline unavailable — install PyTorch and run backend with Python 3.11+",
        )
        logger.error("[job=%s] Cannot run pipeline — missing dependencies", job_id[:8])
        return

    try:
        result = run_pipeline(
            job_id=job_id,
            scan_path=Path(filepath),
            output_dir=RESULTS_DIR / job_id,
            on_stage=lambda step, status, record: _on_pipeline_stage(job_id, step, status, record),
        )
        _update_job(
            job_id,
            status="completed",
            current_step="pdf_report",
            step_status="OK",
            result=result,
            completed_at=time.time(),
        )
        logger.info("[job=%s] Job marked completed in job store", job_id[:8])
    except Exception as exc:
        _update_job(job_id, status="failed", error=str(exc), completed_at=time.time())
        logger.exception("[job=%s] Job failed", job_id[:8])


@app.on_event("startup")
async def startup_event() -> None:
    logger.info("=" * 72)
    logger.info("NeuroScan backend starting")
    logger.info("Project root : %s", PROJECT_ROOT)
    logger.info("Upload dir   : %s", UPLOAD_DIR)
    logger.info("Results dir  : %s", RESULTS_DIR)
    logger.info("Pipeline     : %s", "READY" if PIPELINE_AVAILABLE else "UNAVAILABLE")
    logger.info("Log level    : %s", os.getenv("NEUROSCAN_LOG_LEVEL", "INFO"))
    logger.info("Endpoints    : GET /health  POST /upload  GET /jobs  GET /jobs/{{id}}  GET /pipeline/steps")
    logger.info("=" * 72)


@app.get("/health")
async def health_check():
    model_path = PROJECT_ROOT / "models" / "cnn_baseline.pth"
    return {
        "status": "ok",
        "pipeline_ready": PIPELINE_AVAILABLE,
        "model_available": model_path.exists(),
        "jobs_count": len(JOBS),
    }


@app.get("/pipeline/steps")
async def pipeline_steps():
    return {"steps": PIPELINE_STEPS, "count": len(PIPELINE_STEPS)}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    job_id = str(uuid.uuid4())
    save_name = f"{job_id}_{file.filename}"
    dest_path = UPLOAD_DIR / save_name

    logger.info("[job=%s] UPLOAD received | file=%s", job_id[:8], file.filename)

    try:
        contents = await file.read()
        dest_path.write_bytes(contents)
        await file.close()
        logger.info("[job=%s] UPLOAD saved | path=%s | bytes=%d", job_id[:8], dest_path.name, len(contents))
    except Exception:
        logger.exception("[job=%s] UPLOAD failed while writing file", job_id[:8])
        raise HTTPException(status_code=500, detail="Failed to save uploaded file")

    job_record = {
        "id": job_id,
        "filename": save_name,
        "original_filename": file.filename,
        "status": "pending",
        "current_step": "upload",
        "step_status": "OK",
        "stages": [],
        "created_at": time.time(),
    }
    try:
        with JOBS_LOCK:
            JOBS[job_id] = job_record
            save_jobs()
        logger.info("[job=%s] Job record created — launching pipeline thread", job_id[:8])
    except Exception:
        logger.exception("[job=%s] Failed to create job record", job_id[:8])
        dest_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail="Failed to create job record")

    thread = threading.Thread(target=process_job, args=(job_id, str(dest_path)), daemon=True, name=f"pipeline-{job_id[:8]}")
    thread.start()
    return JSONResponse(status_code=201, content={"job_id": job_id})


@app.get("/jobs")
async def list_jobs():
    with JOBS_LOCK:
        jobs = list(JOBS.values())
    logger.debug("Listed %d job(s)", len(jobs))
    return jobs


@app.get("/jobs/{job_id}")
async def get_job(job_id: str):
    with JOBS_LOCK:
        job = JOBS.get(job_id)
    if not job:
        logger.warning("Job lookup failed | id=%s", job_id[:8])
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.middleware("http")
async def log_requests(request: Request, call_next):
    if request.url.path == "/health":
        return await call_next(request)

    start = time.time()
    logger.info("HTTP %s %s", request.method, request.url.path)
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("HTTP %s %s — unhandled error", request.method, request.url.path)
        raise
    elapsed_ms = (time.time() - start) * 1000
    logger.info("HTTP %s %s -> %s (%.1f ms)", request.method, request.url.path, response.status_code, elapsed_ms)
    return response
