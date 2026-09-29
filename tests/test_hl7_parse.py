from pathlib import Path

from src.hl7_parse import is_adt_a01, parse_hl7
from src.pipeline import walk_message

SAMPLE = Path(__file__).resolve().parents[1] / "data" / "sample_adt_a01.hl7"


def test_parse_pid_mrn():
    msg = parse_hl7(SAMPLE.read_text(encoding="utf-8"))
    assert is_adt_a01(msg)
    assert msg.component("PID", 3, 1) == "MRN77821"


def test_walk_warehouse_row():
    row = walk_message(SAMPLE.read_text(encoding="utf-8"))["warehouse_row"]
    assert row["msg_control_id"] == "MSG00042"
    assert row["mrn"] == "MRN77821"
    assert row["encounter_id"] == "ENC-44021"
    assert row["location"].startswith("ICU")
