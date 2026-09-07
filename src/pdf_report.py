"""Generate native PDF clinical support reports."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict


def write_pdf_report(output_path: Path, job_id: str, result: Dict[str, Any]) -> Path:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.pdfgen import canvas

    output_path.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(output_path), pagesize=A4)
    width, height = A4
    y = height - 2 * cm

    def line(text: str, size: int = 11, gap: float = 0.55) -> None:
        nonlocal y
        if y < 2 * cm:
            c.showPage()
            y = height - 2 * cm
        c.setFont("Helvetica", size)
        c.drawString(2 * cm, y, text[:110])
        y -= gap * cm

    line("NeuroScan Nepal — Clinical Support Report", 14, 0.8)
    line("Prototype for academic evaluation only. Not a medical device.", 9, 0.5)
    line(f"Job ID: {job_id}", 10)
    line(f"Classification: {result.get('label', 'n/a')}  |  Confidence: {result.get('confidence', 'n/a')}", 10)
    line(f"Low quality flag: {result.get('low_quality', False)}", 10)
    line("", 10, 0.3)
    line("RAG Advisory:", 11, 0.5)
    advisory = (result.get("rag_advisory") or {}).get("summary", "n/a")
    for chunk in _wrap(advisory, 95):
        line(chunk, 10, 0.45)
    line("", 10, 0.3)
    line("Chatbot (EN):", 11, 0.5)
    for chunk in _wrap((result.get("chatbot") or {}).get("language_en", ""), 95):
        line(chunk, 10, 0.45)
    line("", 10, 0.3)
    hospitals = result.get("hospitals") or []
    line(f"Recommended hospitals ({len(hospitals)}):", 11, 0.5)
    for h in hospitals[:6]:
        line(f"- {h.get('name', '')} ({h.get('city', '')})", 9, 0.42)
    programs = (result.get("healthcare") or {}).get("government_programs") or []
    if programs:
        line("", 10, 0.3)
        line("Government programmes (reference):", 11, 0.5)
        for p in programs[:3]:
            line(f"- {p.get('name', '')}", 9, 0.42)
    line("", 10, 0.3)
    line("Disclaimer: AI-assisted screening support only. Clinician review required.", 9)
    c.save()
    return output_path


def _wrap(text: str, width: int) -> list[str]:
    words = text.split()
    lines, current = [], []
    for word in words:
        if sum(len(w) for w in current) + len(current) + len(word) > width:
            lines.append(" ".join(current))
            current = [word]
        else:
            current.append(word)
    if current:
        lines.append(" ".join(current))
    return lines or [""]
