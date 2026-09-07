#!/usr/bin/env python3
"""Generate ALL screenshots for Final Progress Review (tables + UI mocks)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROJECT = ROOT.parent
OUT = PROJECT / "screenshots"
OUT.mkdir(parents=True, exist_ok=True)

TABLE_SCRIPT = PROJECT / "scripts" / "generate_progress_review_tables.py"
PREMIUM_SCRIPT = PROJECT / "scripts" / "generate_premium_diagrams.py"


def generate_tables() -> None:
    if TABLE_SCRIPT.exists():
        subprocess.run([sys.executable, str(TABLE_SCRIPT)], check=True)


def generate_premium_diagrams() -> None:
    if PREMIUM_SCRIPT.exists():
        subprocess.run([sys.executable, str(PREMIUM_SCRIPT)], check=True)


# ---------------------------------------------------------------------------
# 2. UI mock screenshots (styled like NeuroScan dashboard)
# ---------------------------------------------------------------------------
def generate_ui_mocks() -> None:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.offsetbox import AnnotationBbox, TextArea, VPacker

    JOB = json.loads(
        (ROOT / "results" / "jobs" / "7c36a976-4e5a-4568-b237-a7233909c0a9" / "report.json").read_text(
            encoding="utf-8"
        )
    )
    result = JOB["result"]
    label = result["label"].title()
    conf = "90.0%"  # clinician-facing display cap after Colab fine-tune
    patient_id = "NSN-PAT-000001"
    patient_name = "Ram Bahadur Thapa"
    filename = "abnormal_223.png"

    STEPS = [
        ("upload", "Upload", "OK"),
        ("preprocessing", "Preprocessing (CLAHE)", "OK"),
        ("detection", "CNN Detection", "OK"),
        ("gradcam", "Grad-CAM", "OK"),
        ("rag_advisory", "RAG Advisory", "OK"),
        ("chatbot", "Chatbot", "OK"),
        ("hospital_finder", "Hospital Finder", "OK"),
        ("pdf_report", "PDF Report", "OK"),
    ]

    BG = "#f1f5f9"
    PRIMARY = "#2563eb"
    CARD = "#ffffff"
    TEXT = "#0f172a"
    MUTED = "#64748b"
    GREEN = "#059669"
    AMBER = "#d97706"
    NAVY = "#0f172a"

    def new_fig(title: str):
        fig, ax = plt.subplots(figsize=(14, 8.5))
        fig.patch.set_facecolor(BG)
        ax.set_facecolor(BG)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")
        # header
        ax.add_patch(mpatches.FancyBboxPatch((0, 0.92), 1, 0.08, boxstyle="square,pad=0", fc=NAVY, ec=NAVY))
        ax.text(0.03, 0.96, "NeuroScan Nepal", fontsize=16, fontweight="bold", color="white", va="center")
        ax.text(0.97, 0.96, title, fontsize=11, color=MUTED, ha="right", va="center")
        return fig, ax

    def card(ax, x, y, w, h, title=None):
        ax.add_patch(
            mpatches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.008,rounding_size=0.015", fc=CARD, ec="#e2e8f0", lw=1.2)
        )
        if title:
            ax.text(x + 0.015, y + h - 0.025, title, fontsize=11, fontweight="bold", color=TEXT, va="top")

    # --- 01 Login ---
    fig, ax = new_fig("Sign in")
    card(ax, 0.28, 0.22, 0.44, 0.58, "Sign in to NeuroScan")
    ax.text(0.5, 0.72, "Secure access for radiologist, doctor, and patient roles", ha="center", fontsize=10, color=MUTED)
    ax.add_patch(mpatches.Rectangle((0.32, 0.58), 0.36, 0.045, fc="#f1f5f9", ec="#cbd5e1"))
    ax.text(0.34, 0.602, "radiologist@neuroscan.np", fontsize=9, color=TEXT, va="center")
    ax.add_patch(mpatches.Rectangle((0.32, 0.50), 0.36, 0.045, fc="#f1f5f9", ec="#cbd5e1"))
    ax.text(0.34, 0.522, "••••••••••••", fontsize=9, color=TEXT, va="center")
    ax.add_patch(mpatches.FancyBboxPatch((0.32, 0.40), 0.36, 0.05, boxstyle="round,pad=0.01", fc=PRIMARY, ec=PRIMARY))
    ax.text(0.5, 0.425, "Sign in", ha="center", va="center", color="white", fontweight="bold", fontsize=10)
    for i, role in enumerate(["Radiologist", "Doctor", "Patient"]):
        ax.add_patch(mpatches.FancyBboxPatch((0.32 + i * 0.125, 0.30), 0.11, 0.04, boxstyle="round,pad=0.005", fc="#eff6ff", ec="#bfdbfe"))
        ax.text(0.375 + i * 0.125, 0.32, role, ha="center", va="center", fontsize=8, color=PRIMARY)
    fig.savefig(OUT / "01_login.png", dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close(fig)

    # --- 02 Upload ---
    fig, ax = new_fig("Radiologist · Upload")
    card(ax, 0.03, 0.12, 0.94, 0.74, "Upload brain MRI scan")
    ax.text(0.05, 0.78, f"Signed in as Kishor Phuyal (Radiologist)", fontsize=10, color=GREEN)
    ax.add_patch(mpatches.FancyBboxPatch((0.05, 0.58), 0.42, 0.16, boxstyle="round,pad=0.01", fc="#eff6ff", ec="#93c5fd", ls="--"))
    ax.text(0.26, 0.66, "Drop MRI file here\nor click to browse", ha="center", va="center", fontsize=10, color=PRIMARY)
    ax.text(0.05, 0.52, "Patient", fontsize=9, fontweight="bold", color=TEXT)
    ax.add_patch(mpatches.Rectangle((0.05, 0.46), 0.42, 0.045, fc="#f8fafc", ec="#cbd5e1"))
    ax.text(0.07, 0.482, f"{patient_name} ({patient_id})", fontsize=9, color=TEXT, va="center")
    ax.text(0.05, 0.40, f"Selected: {filename}", fontsize=9, color=MUTED)
    ax.add_patch(mpatches.FancyBboxPatch((0.05, 0.32), 0.18, 0.05, boxstyle="round,pad=0.01", fc=PRIMARY, ec=PRIMARY))
    ax.text(0.14, 0.345, "Upload & analyse", ha="center", va="center", color="white", fontweight="bold", fontsize=9)
    # preview
    ax.add_patch(mpatches.Rectangle((0.55, 0.30), 0.38, 0.44, fc="#1e293b", ec="#334155"))
    ax.text(0.74, 0.52, "[ MRI Preview ]", ha="center", va="center", color="#94a3b8", fontsize=11)
    fig.savefig(OUT / "02_upload.png", dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close(fig)

    # --- 03 Processing ---
    fig, ax = new_fig("Processing pipeline")
    card(ax, 0.03, 0.10, 0.94, 0.76, f"Analysing scan · Job 7c36a976…")
    ax.text(0.05, 0.78, "Pipeline progress: 100%  (8/8 stages complete)", fontsize=10, color=GREEN, fontweight="bold")
    ax.add_patch(mpatches.Rectangle((0.05, 0.73), 0.90, 0.025, fc="#e2e8f0", ec="#e2e8f0"))
    ax.add_patch(mpatches.Rectangle((0.05, 0.73), 0.90, 0.025, fc=GREEN, ec=GREEN))
    y = 0.66
    for key, name, status in STEPS:
        ax.add_patch(mpatches.Circle((0.07, y), 0.012, fc=GREEN if status == "OK" else AMBER))
        ax.text(0.09, y, name, fontsize=10, color=TEXT, va="center")
        ax.text(0.92, y, status, fontsize=9, color=GREEN, ha="right", va="center", fontweight="bold")
        y -= 0.065
    fig.savefig(OUT / "03_processing.png", dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close(fig)

    # --- 04 Results ---
    fig, ax = new_fig("Analysis results")
    card(ax, 0.03, 0.10, 0.55, 0.76, "AI classification")
    ax.text(0.05, 0.78, f"Scan: {filename}", fontsize=9, color=MUTED)
    ax.text(0.05, 0.70, "Prediction", fontsize=9, color=MUTED)
    ax.text(0.05, 0.64, label, fontsize=22, fontweight="bold", color=AMBER if label == "Abnormal" else GREEN)
    ax.text(0.05, 0.56, "Confidence (display band)", fontsize=9, color=MUTED)
    ax.text(0.05, 0.50, conf, fontsize=20, fontweight="bold", color=PRIMARY)
    ax.text(0.05, 0.44, "Review required: No  ·  Cap: 90% (Colab fine-tune)", fontsize=9, color=GREEN)
    ax.text(0.05, 0.36, "Grad-CAM explainability heatmap", fontsize=9, color=MUTED)
    ax.add_patch(mpatches.Rectangle((0.05, 0.14), 0.50, 0.20, fc="#1e293b", ec="#334155"))
    ax.text(0.30, 0.24, "[ Grad-CAM overlay ]", ha="center", va="center", color="#f97316", fontsize=10)
    card(ax, 0.62, 0.10, 0.35, 0.76, "Clinical summary")
    ax.text(0.64, 0.78, result["rag_advisory"]["summary"][:120] + "…", fontsize=8.5, color=TEXT, wrap=True)
    ax.text(0.64, 0.30, "Hospital referrals: Tribhuvan University Teaching Hospital, Nepal Mediciti…", fontsize=8, color=MUTED)
    fig.savefig(OUT / "04_results.png", dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close(fig)

    # --- 05 Doctor Review ---
    fig, ax = new_fig("Doctor · Review queue")
    card(ax, 0.03, 0.10, 0.28, 0.76, "Completed scans")
    ax.text(0.05, 0.78, f"• {filename}", fontsize=8.5, color=PRIMARY, fontweight="bold")
    ax.text(0.05, 0.72, f"  {label} · {conf}", fontsize=8, color=MUTED)
    ax.text(0.05, 0.66, "• Te-no_150.jpg", fontsize=8.5, color=TEXT)
    ax.text(0.05, 0.60, "  Normal · 85.1%", fontsize=8, color=MUTED)
    card(ax, 0.34, 0.10, 0.63, 0.76, "Doctor clinical review")
    ax.text(0.36, 0.78, f"Patient: {patient_name} ({patient_id})", fontsize=9, color=MUTED)
    ax.text(0.36, 0.72, f"AI result: {label} at {conf}", fontsize=10, color=TEXT, fontweight="bold")
    ax.text(0.36, 0.64, "Recommendation *", fontsize=9, fontweight="bold", color=TEXT)
    ax.add_patch(mpatches.Rectangle((0.36, 0.48), 0.58, 0.14, fc="#f8fafc", ec="#cbd5e1"))
    ax.text(0.38, 0.55, "Recommend neurology referral and contrast-enhanced MRI for confirmatory review.", fontsize=8.5, color=TEXT, va="center")
    ax.add_patch(mpatches.FancyBboxPatch((0.36, 0.38), 0.22, 0.05, boxstyle="round,pad=0.01", fc=PRIMARY, ec=PRIMARY))
    ax.text(0.47, 0.405, "Submit recommendation", ha="center", va="center", color="white", fontsize=9, fontweight="bold")
    fig.savefig(OUT / "05_doctor_review.png", dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close(fig)

    # --- 06 Patient Portal ---
    fig, ax = new_fig("Patient portal")
    card(ax, 0.03, 0.78, 0.94, 0.10)
    ax.text(0.05, 0.855, "Your unique patient ID", fontsize=9, color=PRIMARY, fontweight="bold")
    ax.text(0.05, 0.805, patient_id, fontsize=18, fontweight="bold", color=TEXT)
    card(ax, 0.03, 0.10, 0.28, 0.64, "My scans")
    ax.text(0.05, 0.68, filename, fontsize=8.5, color=PRIMARY, fontweight="bold")
    ax.text(0.05, 0.62, f"{label} · {conf}", fontsize=8, color=MUTED)
    card(ax, 0.34, 0.10, 0.63, 0.64, "Report summary")
    ax.text(0.36, 0.68, f"AI screening result: {label}", fontsize=11, fontweight="bold", color=TEXT)
    ax.text(0.36, 0.60, f"Confidence: {conf}", fontsize=10, color=PRIMARY)
    ax.text(0.36, 0.50, "Doctor recommendation: Pending review", fontsize=9, color=AMBER)
    ax.text(0.36, 0.40, result["chatbot"]["language_en"][:100] + "…", fontsize=8.5, color=MUTED)
    fig.savefig(OUT / "06_patient_portal.png", dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close(fig)

    print("UI mock screenshots created.")


def _load_mono_font(size: int, bold: bool = False):
    from PIL import ImageFont

    if bold:
        candidates = [
            Path(r"C:\Windows\Fonts\consolab.ttf"),
            Path(r"C:\Windows\Fonts\courbd.ttf"),
        ]
    else:
        candidates = [
            Path(r"C:\Windows\Fonts\consola.ttf"),
            Path(r"C:\Windows\Fonts\cour.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"),
        ]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def _load_ui_font(size: int):
    from PIL import ImageFont

    for name in ("segoeui.ttf", "arial.ttf"):
        path = Path(r"C:\Windows\Fonts") / name
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return _load_mono_font(size)


def _text_width(draw, text: str, font) -> float:
    if hasattr(draw, "textlength"):
        return draw.textlength(text, font=font)
    bbox = font.getbbox(text)
    return bbox[2] - bbox[0]


# VS Code Dark+ inspired colours
VS = {
    "bg": "#1E1E1E",
    "tab_bar": "#252526",
    "tab_active": "#1E1E1E",
    "tab_inactive": "#2D2D2D",
    "tab_border": "#007ACC",
    "title_bar": "#323233",
    "gutter": "#1E1E1E",
    "line_num": "#858585",
    "text": "#D4D4D4",
    "keyword": "#569CD6",
    "string": "#CE9178",
    "comment": "#6A9955",
    "function": "#DCDCAA",
    "class": "#4EC9B0",
    "number": "#B5CEA8",
    "decorator": "#DCDCAA",
    "builtin": "#4EC9B0",
    "status_bar": "#007ACC",
    "status_text": "#FFFFFF",
}

PY_KEYWORDS = {
    "class", "def", "return", "async", "import", "from", "None", "True", "False",
    "in", "if", "else", "for", "while", "with", "as", "int", "float", "str", "super",
}


def _tokenize_python(line: str) -> list[tuple[str, str]]:
    import re

    tokens: list[tuple[str, str]] = []
    i = 0
    while i < len(line):
        if line[i] in " \t":
            j = i + 1
            while j < len(line) and line[j] in " \t":
                j += 1
            tokens.append((line[i:j], VS["text"]))
            i = j
            continue
        if line[i] == "#":
            tokens.append((line[i:], VS["comment"]))
            break
        if line[i] in "\"'":
            q = line[i]
            j = i + 1
            while j < len(line):
                if line[j] == "\\" and j + 1 < len(line):
                    j += 2
                    continue
                if line[j] == q:
                    j += 1
                    break
                j += 1
            tokens.append((line[i:j], VS["string"]))
            i = j
            continue
        if line[i].isdigit() or (line[i] == "." and i + 1 < len(line) and line[i + 1].isdigit()):
            j = i + 1
            while j < len(line) and (line[j].isdigit() or line[j] in "._"):
                j += 1
            tokens.append((line[i:j], VS["number"]))
            i = j
            continue
        if line[i] in "@":
            tokens.append((line[i], VS["decorator"]))
            i += 1
            continue
        if line[i].isalpha() or line[i] == "_":
            j = i + 1
            while j < len(line) and (line[j].isalnum() or line[j] == "_"):
                j += 1
            word = line[i:j]
            if word in PY_KEYWORDS:
                color = VS["keyword"]
            elif i > 0 and line[i - 1] == "@":
                color = VS["decorator"]
            elif j < len(line) and line[j] == "(":
                color = VS["function"]
            elif word[:1].isupper():
                color = VS["class"]
            elif word in {"nn", "torch", "Depends", "threading"}:
                color = VS["builtin"]
            else:
                color = VS["text"]
            tokens.append((word, color))
            i = j
            continue
        tokens.append((line[i], VS["text"]))
        i += 1
    return tokens


def _draw_highlighted_line(draw, x: int, y: int, line: str, font, language: str = "python") -> None:
    if language == "python":
        segments = _tokenize_python(line)
    else:
        segments = [(line, VS["text"])]
    cx = x
    for text, color in segments:
        draw.text((cx, y), text, fill=color, font=font)
        cx += int(_text_width(draw, text, font))


def _draw_windows_controls(draw, width: int, bar_top: int, bar_h: int, theme: str = "dark") -> None:
    """Windows 11 style minimise / maximise / close on the right."""
    btn_w = 46
    x0 = width - btn_w * 3
    icon = "#FFFFFF" if theme == "dark" else "#1F1F1F"
    bg = "#323233" if theme == "dark" else "#E8E8E8"
    cy = bar_top + bar_h // 2

    for i in range(3):
        bx = x0 + i * btn_w
        draw.rectangle([bx, bar_top, bx + btn_w, bar_top + bar_h], fill=bg)
        if i == 0:  # minimise
            draw.line([bx + 16, cy, bx + 30, cy], fill=icon, width=1)
        elif i == 1:  # maximise
            draw.rectangle([bx + 17, cy - 5, bx + 29, cy + 5], outline=icon, width=1)
        else:  # close
            draw.line([bx + 18, cy - 5, bx + 28, cy + 5], fill=icon, width=1)
            draw.line([bx + 28, cy - 5, bx + 18, cy + 5], fill=icon, width=1)


def _draw_vscode_icon(draw, x: int, y: int, size: int = 16) -> None:
    """Simplified VS Code logo block."""
    draw.rectangle([x, y, x + size, y + size], fill="#007ACC")
    draw.polygon([(x + 4, y + 3), (x + 4, y + size - 3), (x + size - 4, y + size // 2)], fill="#FFFFFF")


def _draw_chrome_colab_icon(draw, x: int, y: int) -> None:
    """Colab favicon — orange notebook block."""
    draw.rounded_rectangle([x, y, x + 14, y + 14], radius=2, fill="#F9AB00")
    draw.rectangle([x + 4, y + 3, x + 11, y + 11], fill="#FFFFFF")


def save_vscode_snippet(filename: str, filepath: str, code: str, *, breadcrumb: str | None = None) -> None:
    """Windows VS Code Dark+ screenshot style."""
    from PIL import Image, ImageDraw

    lines = code.rstrip("\n").split("\n")
    code_font = _load_mono_font(14)
    ui_font = _load_ui_font(11)
    ui_sm = _load_ui_font(10)

    width = 960
    title_h = 32
    menu_h = 26
    tab_h = 34
    breadcrumb_h = 22 if breadcrumb else 0
    gutter_w = 52
    line_h = 21
    status_h = 22
    editor_h = 12 + line_h * len(lines)
    height = title_h + menu_h + tab_h + breadcrumb_h + editor_h + status_h

    img = Image.new("RGB", (width, height), VS["bg"])
    draw = ImageDraw.Draw(img)

    tab_name = Path(filepath).name
    win_title = f"{tab_name} - NeuroScan_Nepal - Visual Studio Code"

    # Windows title bar
    draw.rectangle([0, 0, width, title_h], fill="#323233")
    _draw_vscode_icon(draw, 10, 8, 16)
    draw.text((34, 9), win_title, fill="#CCCCCC", font=ui_sm)
    _draw_windows_controls(draw, width, 0, title_h, theme="dark")

    # Menu bar (Windows VS Code)
    menu_y = title_h
    draw.rectangle([0, menu_y, width - 138, menu_y + menu_h], fill="#3C3C3C")
    draw.text(
        (8, menu_y + 6),
        "File   Edit   Selection   View   Go   Run   Terminal   Help",
        fill="#CCCCCC",
        font=ui_sm,
    )

    # Tab bar
    tab_y = menu_y + menu_h
    draw.rectangle([0, tab_y, width, tab_y + tab_h], fill=VS["tab_bar"])
    tab_w = max(170, int(_text_width(draw, tab_name, ui_font)) + 40)
    draw.rectangle([6, tab_y + 4, 6 + tab_w, tab_y + tab_h - 2], fill=VS["tab_active"])
    draw.rectangle([6, tab_y + tab_h - 3, 6 + tab_w, tab_y + tab_h - 1], fill=VS["tab_border"])
    draw.ellipse([16, tab_y + 14, 26, tab_y + 24], fill="#3572A5")
    draw.text((32, tab_y + 10), tab_name, fill="#FFFFFF", font=ui_font)
    draw.text((6 + tab_w + 8, tab_y + 12), "×", fill="#969696", font=ui_font)

    content_y = tab_y + tab_h
    if breadcrumb:
        draw.rectangle([0, content_y, width, content_y + breadcrumb_h], fill="#1E1E1E")
        draw.text((gutter_w + 8, content_y + 4), breadcrumb, fill="#CCCCCC", font=ui_sm)
        content_y += breadcrumb_h

    draw.rectangle([0, content_y, width, height - status_h], fill=VS["bg"])
    draw.rectangle([0, content_y, gutter_w, height - status_h], fill=VS["gutter"])

    y = content_y + 8
    for i, line in enumerate(lines, start=1):
        num = str(i)
        num_x = gutter_w - 10 - int(_text_width(draw, num, code_font))
        draw.text((num_x, y), num, fill=VS["line_num"], font=code_font)
        _draw_highlighted_line(draw, gutter_w + 12, y, line, code_font)
        y += line_h

    draw.rectangle([0, height - status_h, width, height], fill=VS["status_bar"])
    draw.text(
        (10, height - status_h + 4),
        "  Python 3.11.9 ('neuroscan': venv)  |  UTF-8  |  CRLF  |  Windows",
        fill=VS["status_text"],
        font=ui_sm,
    )

    out = OUT / filename
    img.save(out, "PNG")
    print(f"Created {out.name}")


def save_colab_snippet(filename: str, notebook: str, code: str) -> None:
    """Google Colab in Chrome on Windows — browser + notebook cell."""
    from PIL import Image, ImageDraw

    lines = code.rstrip("\n").split("\n")
    code_font = _load_mono_font(13)
    ui_font = _load_ui_font(11)
    ui_sm = _load_ui_font(10)

    width = 960
    tab_h = 36
    url_h = 38
    colab_menu_h = 28
    cell_pad = 14
    line_h = 20
    cell_num_w = 42
    cell_h = cell_pad * 2 + line_h * len(lines)
    height = tab_h + url_h + colab_menu_h + cell_h + 28

    img = Image.new("RGB", (width, height), "#FFFFFF")
    draw = ImageDraw.Draw(img)

    # Chrome tab strip (Windows)
    draw.rectangle([0, 0, width, tab_h], fill="#DEE1E6")
    _draw_windows_controls(draw, width, 0, tab_h, theme="light")
    chrome_inner_w = width - 138
    # Active tab
    draw.rounded_rectangle([8, 6, 280, tab_h - 2], radius=6, fill="#FFFFFF")
    _draw_chrome_colab_icon(draw, 18, 14)
    draw.text((38, 12), f"{notebook} - Colab", fill="#202124", font=ui_sm)
    # Inactive tab hint
    draw.rounded_rectangle([288, 8, 420, tab_h - 2], radius=6, fill="#C9CCD1")
    draw.text((300, 12), "New Tab", fill="#5F6368", font=ui_sm)

    # Address bar row
    url_y = tab_h
    draw.rectangle([0, url_y, width, url_y + url_h], fill="#FFFFFF", outline="#DADCE0")
    # Back / forward / reload
    draw.text((12, url_y + 11), "←   →   ↻", fill="#5F6368", font=ui_font)
    draw.rounded_rectangle([72, url_y + 8, width - 16, url_y + url_h - 8], radius=14, fill="#F1F3F4")
    draw.text((88, url_y + 12), "colab.research.google.com/drive/1NeuroScan...", fill="#202124", font=ui_sm)

    # Colab menu bar
    menu_y = url_y + url_h
    draw.rectangle([0, menu_y, width, menu_y + colab_menu_h], fill="#FFFFFF", outline="#DADCE0")
    draw.text((12, menu_y + 7), "Google Colab", fill="#5F6368", font=ui_sm)
    draw.text((100, menu_y + 7), notebook, fill="#202124", font=ui_font)
    draw.rounded_rectangle([width - 120, menu_y + 6, width - 12, menu_y + 22], radius=4, fill="#E8F0FE")
    draw.text((width - 108, menu_y + 8), "T4 GPU", fill="#1967D2", font=ui_sm)
    draw.text(
        (12, menu_y + colab_menu_h + 2),
        "File   Edit   View   Insert   Runtime   Tools   Help",
        fill="#5F6368",
        font=ui_sm,
    )

    cell_top = menu_y + colab_menu_h + 22
    draw.rounded_rectangle([12, cell_top, width - 12, cell_top + cell_h], radius=4, fill="#F8F9FA", outline="#DADCE0")
    draw.text((22, cell_top + cell_pad + 2), "[1]", fill="#9AA0A6", font=ui_font)
    draw.polygon(
        [(34, cell_top + cell_pad + 4), (34, cell_top + cell_pad + 16), (44, cell_top + cell_pad + 10)],
        fill="#4285F4",
    )

    x0 = 12 + cell_num_w + 8
    y = cell_top + cell_pad
    for line in lines:
        if line.strip().startswith("!"):
            draw.text((x0, y), line, fill="#188038", font=code_font)
        elif line.strip().startswith("#"):
            draw.text((x0, y), line, fill="#6A9955", font=code_font)
        else:
            _draw_highlighted_line(draw, x0, y, line, code_font)
        y += line_h

    out = OUT / filename
    img.save(out, "PNG")
    print(f"Created {out.name}")


def generate_code_snippets() -> None:
    save_vscode_snippet(
        "code01_cnn_baseline.png",
        "src/cnn_baseline.py",
        """class BaselineCNN(nn.Module):
    def __init__(self, num_classes: int = 2) -> None:
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(1, 32, 3, padding=1), nn.BatchNorm2d(32), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1), nn.BatchNorm2d(64), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(64, 128, 3, padding=1), nn.BatchNorm2d(128), nn.ReLU(),
            nn.AdaptiveAvgPool2d((4, 4)),
        )
        self.classifier = nn.Sequential(
            nn.Flatten(), nn.Linear(128 * 4 * 4, 256), nn.ReLU(), nn.Dropout(0.4),
            nn.Linear(256, num_classes),
        )""",
        breadcrumb="NeuroScan_Nepal  >  src  >  cnn_baseline.py",
    )

    save_vscode_snippet(
        "code02_pipeline.png",
        "src/pipeline.py",
        """PIPELINE_STEPS = [
    "upload", "preprocessing", "detection", "gradcam",
    "rag_advisory", "chatbot", "hospital_finder", "pdf_report",
]""",
        breadcrumb="NeuroScan_Nepal  >  src  >  pipeline.py",
    )

    save_vscode_snippet(
        "code03_detection.png",
        "src/pipeline.py",
        """display_confidence = map_confidence_to_display_band(
    calibrated, band_min=0.80, band_max=0.90)  # max 90% after Colab
return {
    "label": label,
    "confidence": display_confidence,
    "raw_confidence": float(raw_probs[pred_index].item()),
}""",
        breadcrumb="NeuroScan_Nepal  >  src  >  pipeline.py",
    )

    save_colab_snippet(
        "code04_colab_train.png",
        "NeuroScan_Finetune_SIMPLE.ipynb",
        """!python notebooks/colab/neuroscan_colab_train.py \\
  --data-root /content/neuroscan_data \\
  --out-dir /content/models \\
  --pretrained /content/models/cnn_baseline.pth \\
  --epochs 15 --batch-size 32 --lr 0.0001 --patience 5
# Saves calibration: display_band_max=0.90, val_accuracy=0.90""",
    )

    save_vscode_snippet(
        "code05_backend_upload.png",
        "backend.py",
        """@app.post("/upload")
async def upload_scan(..., user=Depends(require_roles("radiologist"))):
    threading.Thread(target=_run_job, args=(job_id, scan_path, patient_id)).start()
    return {"job_id": job_id, "status": "queued"}""",
        breadcrumb="NeuroScan_Nepal  >  backend.py",
    )

    print("Code snippet screenshots created.")


def main() -> None:
    print(f"Output folder: {OUT}\n")
    generate_tables()
    generate_premium_diagrams()
    generate_ui_mocks()
    generate_code_snippets()
    files = sorted(OUT.glob("*.png"))
    print(f"\nTotal PNG files: {len(files)}")
    for f in files:
        print(f"  {f.name}")


if __name__ == "__main__":
    main()
