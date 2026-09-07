"""NeuroScan Nepal FastAPI backend with full pipeline logging and RBAC."""

from __future__ import annotations

import json
import os
import sys
import threading
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import Depends, FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from auth import (  # noqa: E402
    ROLE_LABELS,
    ROLES,
    authenticate_user,
    create_access_token,
    create_user,
    get_current_user,
    get_user_by_email,
    get_user_by_id,
    get_user_by_patient_id,
    init_db,
    list_patients,
    require_roles,
    seed_demo_users,
)
from logging_config import setup_logging  # noqa: E402

logger = setup_logging(log_dir=PROJECT_ROOT, level=os.getenv("NEUROSCAN_LOG_LEVEL", "INFO"))

try:
    from pipeline import PIPELINE_STEPS, run_pipeline  # noqa: E402

    PIPELINE_AVAILABLE = True
except ImportError as exc:
    PIPELINE_AVAILABLE = False
    logger.error("Pipeline modules unavailable: %s", exc)
    logger.error("Run backend with Python 3.11+ and install torch: pip install torch torchvision")

app = FastAPI(title="NeuroScan Nepal API", version="2.0.0")

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


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    email: str
    password: str = Field(min_length=6)
    full_name: str
    role: str


class DoctorReviewRequest(BaseModel):
    recommendation: str = Field(min_length=10)
    clinical_notes: Optional[str] = None


class RadiologistNotesRequest(BaseModel):
    recommendation: str = Field(min_length=10)
    clinical_notes: Optional[str] = None


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=500)
    language: str = Field(default="en", pattern="^(en|ne)$")


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


def _resolve_patient(patient_ref: str) -> Dict[str, Any]:
    patient = get_user_by_id(patient_ref) or get_user_by_patient_id(patient_ref)
    if not patient or patient["role"] != "patient":
        raise HTTPException(status_code=400, detail="Invalid patient ID")
    return patient


def _user_can_access_job(user: Dict[str, Any], job: Dict[str, Any]) -> bool:
    role = user["role"]
    if role == "radiologist":
        return True
    if role == "doctor":
        return job.get("status") == "completed"
    if role == "patient":
        return job.get("patient_user_id") == user["id"]
    return False


def _filter_jobs_for_user(user: Dict[str, Any]) -> List[Dict[str, Any]]:
    with JOBS_LOCK:
        jobs = list(JOBS.values())
    role = user["role"]
    if role == "radiologist":
        return jobs
    if role == "doctor":
        return [j for j in jobs if j.get("status") == "completed"]
    if role == "patient":
        return [j for j in jobs if j.get("patient_user_id") == user["id"]]
    return []


def _get_job_or_404(job_id: str) -> Dict[str, Any]:
    with JOBS_LOCK:
        job = JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


def process_job(job_id: str, filepath: str) -> None:
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
    init_db()
    seed_demo_users()
    logger.info("=" * 72)
    logger.info("NeuroScan backend starting (RBAC enabled)")
    logger.info("Project root : %s", PROJECT_ROOT)
    logger.info("Upload dir   : %s", UPLOAD_DIR)
    logger.info("Results dir  : %s", RESULTS_DIR)
    logger.info("Pipeline     : %s", "READY" if PIPELINE_AVAILABLE else "UNAVAILABLE")
    logger.info("Roles        : %s", ", ".join(ROLES))
    logger.info("Demo logins  : radiologist@neuroscan.np / doctor@neuroscan.np / patient@neuroscan.np")
    logger.info("=" * 72)


@app.get("/health")
async def health_check():
    model_path = PROJECT_ROOT / "models" / "cnn_baseline.pth"
    return {
        "status": "ok",
        "pipeline_ready": PIPELINE_AVAILABLE,
        "model_available": model_path.exists(),
        "jobs_count": len(JOBS),
        "auth_enabled": True,
    }


@app.get("/pipeline/steps")
async def pipeline_steps(user: Dict[str, Any] = Depends(get_current_user)):
    return {"steps": PIPELINE_STEPS, "count": len(PIPELINE_STEPS)}


@app.post("/auth/login")
async def login(body: LoginRequest):
    user = authenticate_user(body.email, body.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token(user)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user,
        "role_label": ROLE_LABELS.get(user["role"], user["role"]),
    }


@app.post("/auth/register")
async def register(body: RegisterRequest):
    if body.role not in ROLES:
        raise HTTPException(status_code=400, detail=f"Role must be one of: {', '.join(ROLES)}")
    if get_user_by_email(body.email):
        raise HTTPException(status_code=409, detail="Email already registered")
    try:
        user = create_user(body.email, body.password, body.full_name, body.role)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    token = create_access_token(user)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user,
        "role_label": ROLE_LABELS.get(user["role"], user["role"]),
    }


@app.get("/auth/me")
async def me(user: Dict[str, Any] = Depends(get_current_user)):
    return {
        **user,
        "role_label": ROLE_LABELS.get(user["role"], user["role"]),
    }


@app.get("/auth/patients")
async def patients(user: Dict[str, Any] = Depends(require_roles("radiologist", "doctor"))):
    return list_patients()


@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    patient_id: str = Form(...),
    user: Dict[str, Any] = Depends(require_roles("radiologist")),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    patient = _resolve_patient(patient_id)
    job_id = str(uuid.uuid4())
    save_name = f"{job_id}_{file.filename}"
    dest_path = UPLOAD_DIR / save_name

    logger.info(
        "[job=%s] UPLOAD by radiologist %s for patient %s | file=%s",
        job_id[:8],
        user["email"],
        patient["patient_unique_id"],
        file.filename,
    )

    try:
        contents = await file.read()
        dest_path.write_bytes(contents)
        await file.close()
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
        "uploaded_by_user_id": user["id"],
        "uploaded_by_name": user["full_name"],
        "patient_user_id": patient["id"],
        "patient_unique_id": patient["patient_unique_id"],
        "patient_name": patient["full_name"],
        "doctor_recommendation": None,
        "radiologist_notes": None,
    }
    try:
        with JOBS_LOCK:
            JOBS[job_id] = job_record
            save_jobs()
    except Exception:
        dest_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail="Failed to create job record")

    thread = threading.Thread(
        target=process_job,
        args=(job_id, str(dest_path)),
        daemon=True,
        name=f"pipeline-{job_id[:8]}",
    )
    thread.start()
    return JSONResponse(
        status_code=201,
        content={
            "job_id": job_id,
            "patient_unique_id": patient["patient_unique_id"],
            "patient_name": patient["full_name"],
        },
    )


@app.get("/jobs")
async def list_jobs(user: Dict[str, Any] = Depends(get_current_user)):
    jobs = _filter_jobs_for_user(user)
    logger.debug("Listed %d job(s) for role=%s", len(jobs), user["role"])
    return jobs


@app.get("/jobs/{job_id}")
async def get_job(job_id: str, user: Dict[str, Any] = Depends(get_current_user)):
    job = _get_job_or_404(job_id)
    if not _user_can_access_job(user, job):
        raise HTTPException(status_code=403, detail="Access denied")
    return job


@app.get("/jobs/{job_id}/scan-image")
async def get_scan_image(job_id: str, user: Dict[str, Any] = Depends(get_current_user)):
    job = _get_job_or_404(job_id)
    if not _user_can_access_job(user, job):
        raise HTTPException(status_code=403, detail="Access denied")

    scan_path = UPLOAD_DIR / job["filename"]
    if not scan_path.exists():
        raise HTTPException(status_code=404, detail="Scan image not found")

    media = "image/png" if scan_path.suffix.lower() == ".png" else "image/jpeg"
    return FileResponse(scan_path, media_type=media, filename=job.get("original_filename", scan_path.name))


@app.get("/jobs/{job_id}/gradcam")
async def get_gradcam_image(job_id: str, user: Dict[str, Any] = Depends(get_current_user)):
    job = _get_job_or_404(job_id)
    if not _user_can_access_job(user, job):
        raise HTTPException(status_code=403, detail="Access denied")

    gradcam_path = RESULTS_DIR / job_id / "gradcam.png"
    if not gradcam_path.exists():
        result_path = (job.get("result") or {}).get("gradcam_path")
        if result_path:
            gradcam_path = Path(result_path)
    if not gradcam_path.exists():
        raise HTTPException(status_code=404, detail="Grad-CAM image not found")

    return FileResponse(gradcam_path, media_type="image/png", filename=f"gradcam_{job_id[:8]}.png")


@app.get("/jobs/{job_id}/report/{kind}")
async def download_report(job_id: str, kind: str, user: Dict[str, Any] = Depends(get_current_user)):
    job = _get_job_or_404(job_id)
    if not _user_can_access_job(user, job):
        raise HTTPException(status_code=403, detail="Access denied")

    kind = kind.lower()
    allowed = {
        "html": ("report.html", "text/html"),
        "json": ("report.json", "application/json"),
        "text": ("report.txt", "text/plain"),
        "pdf": ("report.pdf", "application/pdf"),
    }
    if kind not in allowed:
        raise HTTPException(status_code=400, detail="Report kind must be html, json, or text")

    filename, media_type = allowed[kind]
    report_path = RESULTS_DIR / job_id / filename
    if not report_path.exists():
        raise HTTPException(status_code=404, detail="Report not found")

    return FileResponse(report_path, media_type=media_type, filename=f"neuroscan_{job_id[:8]}.{kind if kind != 'text' else 'txt'}")


@app.post("/jobs/{job_id}/chat")
async def chat_with_job(job_id: str, body: ChatRequest, user: Dict[str, Any] = Depends(get_current_user)):
    job = _get_job_or_404(job_id)
    if not _user_can_access_job(user, job):
        raise HTTPException(status_code=403, detail="Access denied")
    if job.get("status") != "completed":
        raise HTTPException(status_code=400, detail="Job must be completed before chat")

    from knowledge_base import answer_chatbot  # noqa: E402

    label = (job.get("result") or {}).get("label", "normal")
    reply = answer_chatbot(body.message, label, body.language)
    return {"job_id": job_id, "label": label, **reply}


@app.post("/jobs/{job_id}/doctor-review")
async def submit_doctor_review(
    job_id: str,
    body: DoctorReviewRequest,
    user: Dict[str, Any] = Depends(require_roles("doctor")),
):
    job = _get_job_or_404(job_id)
    if job.get("status") != "completed":
        raise HTTPException(status_code=400, detail="Job must be completed before doctor review")

    review = {
        "doctor_id": user["id"],
        "doctor_name": user["full_name"],
        "recommendation": body.recommendation.strip(),
        "clinical_notes": (body.clinical_notes or "").strip() or None,
        "updated_at": time.time(),
    }
    _update_job(job_id, doctor_recommendation=review)
    logger.info("[job=%s] Doctor review submitted by %s", job_id[:8], user["email"])
    return {"status": "ok", "doctor_recommendation": review}


@app.post("/jobs/{job_id}/radiologist-notes")
async def submit_radiologist_notes(
    job_id: str,
    body: RadiologistNotesRequest,
    user: Dict[str, Any] = Depends(require_roles("radiologist")),
):
    job = _get_job_or_404(job_id)
    if job.get("status") != "completed":
        raise HTTPException(status_code=400, detail="Job must be completed before adding radiologist notes")

    notes = {
        "radiologist_id": user["id"],
        "radiologist_name": user["full_name"],
        "recommendation": body.recommendation.strip(),
        "clinical_notes": (body.clinical_notes or "").strip() or None,
        "updated_at": time.time(),
    }
    _update_job(job_id, radiologist_notes=notes)
    logger.info("[job=%s] Radiologist notes submitted by %s", job_id[:8], user["email"])
    return {"status": "ok", "radiologist_notes": notes}


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
