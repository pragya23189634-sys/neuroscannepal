#!/usr/bin/env python3
"""Calculate SUS scores from docs/SUS_RESULTS_TEMPLATE.csv.

Each q1-q10 column should contain the raw Likert response (1-5).
"""

from __future__ import annotations

import csv
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CSV = ROOT / "docs" / "SUS_RESULTS_TEMPLATE.csv"
OUTPUT = ROOT / "results" / "sus_results.json"

# 1-based item numbers that are reverse-scored
REVERSE = {2, 4, 6, 8, 10}


def _item_score(item_number: int, raw: int) -> int:
    if not 1 <= raw <= 5:
        raise ValueError(f"Item {item_number} must be 1-5, got {raw}")
    return (5 - raw) if item_number in REVERSE else (raw - 1)


def sus_score(responses: list[int]) -> float:
    if len(responses) != 10:
        raise ValueError("SUS requires exactly 10 responses")
    total = sum(_item_score(i + 1, r) for i, r in enumerate(responses))
    return round(total * 2.5, 2)


def main() -> None:
    csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_CSV
    if not csv_path.exists():
        print(f"CSV not found: {csv_path}")
        raise SystemExit(1)

    rows = list(csv.DictReader(csv_path.open(encoding="utf-8")))
    results = []
    for row in rows:
        participant = row.get("participant", "").strip()
        if not participant:
            continue
        try:
            responses = [int(row[f"q{i}"]) for i in range(1, 11)]
        except (KeyError, ValueError):
            print(f"Skipping {participant}: fill q1-q10 with numbers 1-5")
            continue
        score = sus_score(responses)
        results.append({
            "participant": participant,
            "sus_score": score,
            "notes": row.get("notes", ""),
        })
        print(f"{participant}: SUS = {score}/100")

    if not results:
        print("No complete rows found. Fill q1-q10 in the CSV (values 1-5).")
        raise SystemExit(1)

    scores = [r["sus_score"] for r in results]
    summary = {
        "participants": len(results),
        "scores": results,
        "mean_sus": round(statistics.mean(scores), 2),
        "stdev_sus": round(statistics.stdev(scores), 2) if len(scores) > 1 else 0.0,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print()
    print(json.dumps(summary, indent=2))
    print(f"\nSaved: {OUTPUT}")


if __name__ == "__main__":
    main()
