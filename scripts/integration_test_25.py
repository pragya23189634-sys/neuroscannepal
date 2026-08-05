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


def _post_file(path: Path) -> str:
    boundary = "----NeuroScanBoundary"
    data = path.read_bytes()
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{path.name}"\r\n'
        f"Content-Type: application/octet-stream\r\n\r\n"
    ).encode("utf-8") + data + f"\r\n--{boundary}--\r\n".encode("utf-8")
    req = urllib.request.Request(
        f"{API_BASE}/upload",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    return payload["job_id"]


def _get_job(job_id: str) -> dict:
    with urllib.request.urlopen(f"{API_BASE}/jobs/{job_id}", timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> None:
    normal = list_scan_files(ROOT / "data" / "raw" / "normal")
    abnormal = list_scan_files(ROOT / "data" / "raw" / "abnormal")
    if not normal or not abnormal:
        print("Dataset missing in data/raw/")
        raise SystemExit(1)

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
            job_id = _post_file(path)
        except urllib.error.URLError as exc:
            print(f"  FAILED upload — is backend running? {exc}")
            raise SystemExit(1)

        for _ in range(60):
            job = _get_job(job_id)
            if job.get("status") in {"completed", "failed"}:
                break
            time.sleep(1)

        job = _get_job(job_id)
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
        results.append({
            "path": str(path),
            "label": label,
            "pred": pred_label,
            "confidence": result.get("confidence"),
            "correct": ok,
            "job_id": job_id,
        })
        print(f"  -> pred={'abnormal' if pred_label else 'normal'} correct={ok} conf={result.get('confidence')}")

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
