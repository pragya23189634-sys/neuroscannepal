#!/usr/bin/env python3
"""Capture NeuroScan UI screenshots for Final Progress Review."""

from __future__ import annotations

import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FRONTEND = ROOT / "frontend"
OUT = ROOT.parent / "screenshots"
OUT.mkdir(parents=True, exist_ok=True)

LOGIN_URL = "http://127.0.0.1:3000/login"
API_HEALTH = "http://127.0.0.1:8000/health"

ACCOUNTS = {
    "radiologist": ("radiologist@neuroscan.np", "radiologist123"),
    "doctor": ("doctor@neuroscan.np", "doctor123"),
    "patient": ("patient@neuroscan.np", "patient123"),
}

COMPLETED_JOB = "7c36a976-4e5a-4568-b237-a7233909c0a9"


def _http_ok(url: str, timeout: float = 2.0) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return resp.status == 200
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


def _start_servers() -> None:
    if not _http_ok(API_HEALTH):
        print("Starting backend on :8000 …")
        subprocess.Popen(
            ["py", "-3.11", "-m", "uvicorn", "backend:app", "--host", "127.0.0.1", "--port", "8000"],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=getattr(subprocess, "CREATE_NEW_CONSOLE", 0),
        )
    if not _http_ok(LOGIN_URL):
        print("Starting frontend on :3000 …")
        subprocess.Popen(
            ["npm", "run", "dev", "--", "--host", "127.0.0.1", "--port", "3000"],
            cwd=FRONTEND,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            shell=True,
            creationflags=getattr(subprocess, "CREATE_NEW_CONSOLE", 0),
        )

    for _ in range(60):
        if _http_ok(API_HEALTH) and _http_ok(LOGIN_URL):
            print("Servers ready.")
            return
        time.sleep(2)
    raise SystemExit("Servers did not start in time. Run START_NEUROSCAN.bat manually.")


def _login(page, role: str) -> None:
    email, password = ACCOUNTS[role]
    page.goto(LOGIN_URL, wait_until="networkidle")
    page.fill('input[type="email"], input[name="email"]', email)
    page.fill('input[type="password"], input[name="password"]', password)
    page.click('button[type="submit"]')
    page.wait_for_load_state("networkidle")
    time.sleep(1.5)


def main() -> None:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Installing playwright …")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright", "-q"])
        subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
        from playwright.sync_api import sync_playwright

    # Regenerate table images too
    table_script = ROOT / "scripts" / "generate_progress_review_tables.py"
    if table_script.exists():
        subprocess.run([sys.executable, str(table_script)], check=False)

    _start_servers()
    time.sleep(2)

    shots = [
        ("01_login.png", lambda p: p.goto(LOGIN_URL, wait_until="networkidle")),
        ("02_upload.png", lambda p: (_login(p, "radiologist"), p.goto("http://127.0.0.1:3000/upload", wait_until="networkidle"))),
        ("03_processing.png", lambda p: (_login(p, "radiologist"), p.goto(f"http://127.0.0.1:3000/processing?job={COMPLETED_JOB}", wait_until="networkidle"))),
        ("04_results.png", lambda p: (_login(p, "radiologist"), p.goto(f"http://127.0.0.1:3000/results?job={COMPLETED_JOB}", wait_until="networkidle"), p.wait_for_timeout(3000))),
        ("05_doctor_review.png", lambda p: (_login(p, "doctor"), p.goto("http://127.0.0.1:3000/doctor-review", wait_until="networkidle"))),
        ("06_patient_portal.png", lambda p: (_login(p, "patient"), p.goto("http://127.0.0.1:3000/my-records", wait_until="networkidle"))),
    ]

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1400, "height": 900})
        page = context.new_page()

        for filename, action in shots:
            print(f"Capturing {filename} …")
            context.clear_cookies()
            page.goto("about:blank")
            action(page)
            time.sleep(2)
            path = OUT / filename
            page.screenshot(path=str(path), full_page=True)
            print(f"  Saved {path}")

        browser.close()

    print(f"\nDone. All screenshots in:\n  {OUT}")


if __name__ == "__main__":
    main()
