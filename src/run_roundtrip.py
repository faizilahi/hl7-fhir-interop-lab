"""Demonstrate HL7 -> FHIR -> HL7 round trip on synthetic messages."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fhir_builder import adt_to_fhir_bundle, bundle_to_json, validate_bundle  # noqa: E402
from fhir_to_adt import fhir_bundle_to_adt  # noqa: E402
from hl7_parser import adt_from_message, adt_to_hl7  # noqa: E402
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "output"


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    hl7_path = DATA_DIR / "sample_adt_messages.hl7"
    raw_messages = hl7_path.read_text(encoding="utf-8").split("\n\n")
    results = []
    for idx, block in enumerate(raw_messages, start=1):
        block = block.strip()
        if not block:
            continue
        original = adt_from_message(block)
        bundle = adt_to_fhir_bundle(original)
        errors = validate_bundle(bundle)
        if errors:
            raise RuntimeError(f"Validation failed message {idx}: {errors}")
        if idx <= 10:
            json_path = OUTPUT_DIR / f"bundle_{idx:03d}.json"
            json_path.write_text(bundle_to_json(bundle), encoding="utf-8")
        roundtrip_event = fhir_bundle_to_adt(bundle)
        rebuilt_hl7 = adt_to_hl7(roundtrip_event)
        rt = adt_from_message(rebuilt_hl7)
        results.append(
            {
                "message_index": idx,
                "patient_id_match": original.patient_id == rt.patient_id,
                "visit_match": original.visit_number == rt.visit_number,
            }
        )
    summary_path = OUTPUT_DIR / "roundtrip_summary.json"
    summary_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))
    print(f"Wrote bundles and {summary_path}")


if __name__ == "__main__":
    main()
