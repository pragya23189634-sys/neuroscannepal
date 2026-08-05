import csv
from argparse import ArgumentParser
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

from preprocessing import list_scan_files, run_preprocessing_pipeline, summarize_dataset

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
NORMAL_DIR = RAW_DATA_DIR / "normal"
ABNORMAL_DIR = RAW_DATA_DIR / "abnormal"
RESULTS_DIR = PROJECT_ROOT / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def create_patient_prototype(patient_count: int = 100, output_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    if patient_count <= 0:
        raise ValueError("patient_count must be greater than zero")

    rng = np.random.default_rng(42)
    records: List[Dict[str, Any]] = []
    abnormal_count = int(round(patient_count * 0.4))

    for idx in range(patient_count):
        is_abnormal = idx < abnormal_count
        confidence = float(rng.uniform(0.78, 0.97)) if is_abnormal else float(rng.uniform(0.82, 0.99))
        status = "abnormal" if is_abnormal else "normal"
        records.append(
            {
                "patient_id": f"P{idx + 1:03d}",
                "status": status,
                "predicted_label": status,
                "confidence": round(confidence, 4),
                "prototype_note": "Simulated clinical prototype record",
            }
        )

    csv_path = output_path.parent / f"{output_path.stem}.csv" if output_path is not None else RESULTS_DIR / "patient_prototype.csv"
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["patient_id", "status", "predicted_label", "confidence", "prototype_note"])
        writer.writeheader()
        writer.writerows(records)

    report_path = output_path if output_path is not None else RESULTS_DIR / "patient_prototype_report.txt"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_lines = [
        "NeuroScan Nepal prototype report",
        "================================",
        f"Patient count: {patient_count}",
        f"Normal patients: {sum(1 for r in records if r['status'] == 'normal')}",
        f"Abnormal patients: {sum(1 for r in records if r['status'] == 'abnormal')}",
        "Model status: prototype mode using simulated patient records",
        "Output files:",
        f"- CSV: {csv_path}",
        f"- Report: {report_path}",
    ]
    with report_path.open("w", encoding="utf-8") as fh:
        fh.write("\n".join(report_lines))

    print(f"Created prototype for {patient_count} patients.")
    print(f"Report saved to: {report_path}")
    print(f"CSV saved to: {csv_path}")
    return records


def parse_args() -> ArgumentParser:
    parser = ArgumentParser(description="Run the NeuroScan Nepal prototype workflow")
    parser.add_argument("--patient-count", type=int, default=100, help="Number of synthetic patients to generate")
    parser.add_argument("--output", type=Path, default=None, help="Optional report output path")
    return parser


def main() -> None:
    args = parse_args().parse_args()

    if list_scan_files(NORMAL_DIR) or list_scan_files(ABNORMAL_DIR):
        summarize_dataset(NORMAL_DIR, ABNORMAL_DIR)
        run_preprocessing_pipeline(
            normal_dir=NORMAL_DIR,
            abnormal_dir=ABNORMAL_DIR,
            output_root=PROJECT_ROOT / "data" / "processed",
            train_ratio=0.8,
            augment=True,
            random_state=42,
        )
        return

    create_patient_prototype(patient_count=args.patient_count, output_path=args.output)


if __name__ == "__main__":
    main()
