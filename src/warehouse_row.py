"""Flatten FHIR Patient+Encounter into a warehouse landing row."""
from __future__ import annotations

from typing import Any


def flatten(patient: dict[str, Any], encounter: dict[str, Any], msg_control_id: str) -> dict[str, Any]:
    name = (patient.get("name") or [{}])[0]
    loc = ""
    if encounter.get("location"):
        loc = encounter["location"][0]["location"]["display"]
    return {
        "msg_control_id": msg_control_id,
        "mrn": patient.get("id"),
        "patient_family": name.get("family"),
        "patient_given": (name.get("given") or [None])[0],
        "birth_date": patient.get("birthDate"),
        "gender": patient.get("gender"),
        "encounter_id": encounter.get("id"),
        "encounter_class": (encounter.get("class") or {}).get("code"),
        "location": loc,
        "admit_ts": (encounter.get("period") or {}).get("start"),
        "status": encounter.get("status"),
    }
