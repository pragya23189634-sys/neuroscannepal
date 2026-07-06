from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from main import create_patient_prototype


def test_create_patient_prototype(tmp_path):
    report_path = tmp_path / "prototype_report.txt"
    results = create_patient_prototype(patient_count=100, output_path=report_path)

    assert len(results) == 100
    assert report_path.exists()
    assert "100 patients" in report_path.read_text(encoding="utf-8")
    assert results[0]["status"] in {"normal", "abnormal"}
