"""End-to-end ADT walk: raw -> parse -> FHIR -> warehouse row."""
from __future__ import annotations

from .fhir_map import to_encounter, to_patient
from .hl7_parse import is_adt_a01, parse_hl7
from .warehouse_row import flatten


def walk_message(raw: str) -> dict:
    msg = parse_hl7(raw)
    if not is_adt_a01(msg):
        raise ValueError("Not an ADT^A01 message")
    # MSH control id is field 9 in classic numbering after encoding chars quirks
    control = ""
    msh = msg.segments.get("MSH", [""])[0]
    parts = msh.split("|")
    # MSH|^~\&|EPIC|HOSP|DEST|HOSP|ts||ADT^A01|MSG00042|P|2.5
    if len(parts) > 9:
        control = parts[9]
    patient = to_patient(msg)
    encounter = to_encounter(msg, patient["id"])
    row = flatten(patient, encounter, control)
    return {"patient": patient, "encounter": encounter, "warehouse_row": row}
