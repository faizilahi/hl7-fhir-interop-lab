"""Map parsed ADT fields into FHIR R4-shaped dicts."""
from __future__ import annotations

from typing import Any

from .hl7_parse import HL7Message


def to_patient(msg: HL7Message) -> dict[str, Any]:
    mrn = msg.component("PID", 3, 1)
    family = msg.component("PID", 5, 1)
    given = msg.component("PID", 5, 2)
    dob = msg.field("PID", 7)
    sex = msg.field("PID", 8)
    return {
        "resourceType": "Patient",
        "id": mrn,
        "identifier": [{"system": "urn:synthetic:mrn", "value": mrn}],
        "name": [{"family": family, "given": [given]}],
        "gender": {"F": "female", "M": "male"}.get(sex, "unknown"),
        "birthDate": _hl7_date(dob),
    }


def to_encounter(msg: HL7Message, patient_id: str) -> dict[str, Any]:
    # Prefer classic PV1-19 / PV1-44; fall back to compact synthetic offsets 15/40.
    enc_id = (
        msg.field("PV1", 19)
        or msg.field("PV1", 15)
        or msg.component("PV1", 19, 1)
    )
    poc = msg.component("PV1", 3, 1)
    room = msg.component("PV1", 3, 2)
    admit = msg.field("PV1", 44) or msg.field("PV1", 40)
    cls = msg.field("PV1", 2)
    return {
        "resourceType": "Encounter",
        "id": enc_id,
        "status": "in-progress",
        "class": {"code": "IMP" if cls == "I" else "AMB"},
        "subject": {"reference": f"Patient/{patient_id}"},
        "location": [{"location": {"display": f"{poc}^{room}"}}],
        "period": {"start": _hl7_dt(admit)},
    }


def _hl7_date(yyyymmdd: str) -> str:
    if len(yyyymmdd) >= 8:
        return f"{yyyymmdd[0:4]}-{yyyymmdd[4:6]}-{yyyymmdd[6:8]}"
    return yyyymmdd


def _hl7_dt(yyyymmddhhmmss: str) -> str:
    if len(yyyymmddhhmmss) >= 14:
        return (
            f"{yyyymmddhhmmss[0:4]}-{yyyymmddhhmmss[4:6]}-{yyyymmddhhmmss[6:8]}T"
            f"{yyyymmddhhmmss[8:10]}:{yyyymmddhhmmss[10:12]}:{yyyymmddhhmmss[12:14]}"
        )
    return _hl7_date(yyyymmddhhmmss)
