#!/usr/bin/env python3
"""Run 25-image integration test through the live backend pipeline."""

from __future__ import annotations

import json
import random
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from preprocessing import list_scan_files

API_BASE = "http://127.0.0.1:8000"
OUTPUT = ROOT / "results" / "integration_test_25.json"

RADIOLOGIST_EMAIL = "radiologist@neuroscan.np"
RADIOLOGIST_PASSWORD = "radiologist123"


def _request_json(
    method: str,
    path: str,
    *,
    data: dict | None = None,
    token: str | None = None,
) -> dict | list:
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(f"{API_BASE}{path}", data=body, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _login_radiologist() -> tuple[str, str]:
    payload = _request_json(
        "POST",
        "/auth/login",
        data={"email": RADIOLOGIST_EMAIL, "password": RADIOLOGIST_PASSWORD},
    )
    token = payload["access_token"]
    patients = _request_json("GET", "/auth/patients", token=token)
    if not patients:
        raise SystemExit("No patient accounts found — run backend once to seed demo users.")
    patient_id = patients[0].get("patient_unique_id") or patients[0]["id"]
    return token, patient_id


def _post_file(path: Path, token: str, patient_id: str) -> str:
    boundary = "----NeuroScanBoundary"
    data = path.read_bytes()
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="patient_id"\r\n\r\n'
        f"{patient_id}\r\n"
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{path.name}"\r\n'
        f"Content-Type: application/octet-stream\r\n\r\n"
    ).encode("utf-8") + data + f"\r\n--{boundary}--\r\n".encode("utf-8")
    req = urllib.request.Request(
        f"{API_BASE}/upload",
        data=body,
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Authorization": f"Bearer {token}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    return payload["job_id"]


def _get_job(job_id: str, token: str) -> dict:
    return _request_json("GET", f"/jobs/{job_id}", token=token)


def _result_confidence(result: dict) -> float | None:
    if result.get("confidence") is not None:
        return result["confidence"]
    if result.get("score") is not None:
        return result["score"]
    return None


def main() -> None:
    normal = list_scan_files(ROOT / "data" / "raw" / "normal")
    abnormal = list_scan_files(ROOT / "data" / "raw" / "abnormal")
    if not normal or not abnormal:
        print("Dataset missing in data/raw/")
        raise SystemExit(1)

    try:
        token, patient_id = _login_radiologist()
    except urllib.error.URLError as exc:
        print(f"Auth failed — is backend running at {API_BASE}? {exc}")
        raise SystemExit(1)

    print(f"Logged in as radiologist; patient={patient_id}")

    random.seed(42)
    samples = [(p, 0) for p in random.sample(normal, min(13, len(normal)))]
    samples += [(p, 1) for p in random.sample(abnormal, min(12, len(abnormal)))]
    random.shuffle(samples)

    print(f"Integration test via {API_BASE} — {len(samples)} images")
    results = []
    correct = 0
    processed = 0
    low_quality = 0

    for index, (path, label) in enumerate(samples, start=1):
        print(f"[{index}/{len(samples)}] Uploading {path.name} (label={'abnormal' if label else 'normal'})")
        try:
            job_id = _post_file(path, token, patient_id)
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            print(f"  FAILED upload ({exc.code}): {detail}")
            raise SystemExit(1)
        except urllib.error.URLError as exc:
            print(f"  FAILED upload — is backend running? {exc}")
            raise SystemExit(1)

        for _ in range(120):
            job = _get_job(job_id, token)
            if job.get("status") in {"completed", "failed"}:
                break
            time.sleep(1)

        job = _get_job(job_id, token)
        result = job.get("result") or {}
        if result.get("low_quality"):
            low_quality += 1
            results.append({"path": str(path), "label": label, "skipped_low_quality": True})
            print("  WARNING low-quality image flagged")
            continue

        pred_label = 1 if result.get("label") == "abnormal" else 0
        ok = pred_label == label
        processed += 1
        if ok:
            correct += 1
        conf = _result_confidence(result)
        results.append({
            "path": str(path),
            "label": label,
            "pred": pred_label,
            "confidence": conf,
            "correct": ok,
            "job_id": job_id,
        })
        print(f"  -> pred={'abnormal' if pred_label else 'normal'} correct={ok} conf={conf}")

    report = {
        "total_selected": len(samples),
        "processed": processed,
        "skipped_low_quality": low_quality,
        "accuracy_processed": correct / processed if processed else None,
        "details": results,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("\nIntegration test complete")
    print(json.dumps({
        "processed": processed,
        "skipped_low_quality": low_quality,
        "accuracy_processed": report["accuracy_processed"],
        "report": str(OUTPUT),
    }, indent=2))


if __name__ == "__main__":
    main()
