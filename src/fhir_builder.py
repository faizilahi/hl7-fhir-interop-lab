"""Build and validate a minimal FHIR R4 Bundle from ADTEvent."""

from __future__ import annotations

import json
from typing import Any

from hl7_parser import ADTEvent


def _format_fhir_date(hl7_dt: str) -> str:
    if not hl7_dt:
        return "2024-01-01T12:00:00+00:00"
    if len(hl7_dt) >= 8:
        d = hl7_dt[:8]
        return f"{d[:4]}-{d[4:6]}-{d[6:8]}T12:00:00+00:00"
    return hl7_dt


def _format_birth(hl7_date: str) -> str:
    if len(hl7_date) == 8:
        return f"{hl7_date[:4]}-{hl7_date[4:6]}-{hl7_date[6:8]}"
    return hl7_date


def adt_to_fhir_bundle(event: ADTEvent) -> dict[str, Any]:
    patient_id = event.patient_id or "unknown"
    encounter_id = event.visit_number or f"enc-{patient_id}"
    gender_map = {"M": "male", "F": "female", "O": "other", "U": "unknown"}
    bundle = {
        "resourceType": "Bundle",
        "type": "collection",
        "timestamp": _format_fhir_date(event.admit_datetime),
        "entry": [
            {
                "fullUrl": f"urn:uuid:patient-{patient_id}",
                "resource": {
                    "resourceType": "Patient",
                    "id": patient_id,
                    "identifier": [{"system": "urn:synthetic:mrn", "value": patient_id}],
                    "name": [{"family": event.family_name, "given": [event.given_name]}],
                    "gender": gender_map.get(event.sex, "unknown"),
                    "birthDate": _format_birth(event.birth_date),
                },
            },
            {
                "fullUrl": f"urn:uuid:encounter-{encounter_id}",
                "resource": {
                    "resourceType": "Encounter",
                    "id": encounter_id,
                    "status": "finished",
                    "class": {
                        "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                        "code": event.patient_class or "IMP",
                    },
                    "subject": {"reference": f"Patient/{patient_id}"},
                    "period": {"start": _format_fhir_date(event.admit_datetime)},
                },
            },
            {
                "fullUrl": "urn:uuid:messageheader-1",
                "resource": {
                    "resourceType": "MessageHeader",
                    "eventCoding": {
                        "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                        "code": event.message_type.split("^")[-1] if event.message_type else "A01",
                    },
                    "source": {"name": event.sending_facility or "SYNTH_FACILITY"},
                },
            },
        ],
    }
    return bundle


def validate_bundle(bundle: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if bundle.get("resourceType") != "Bundle":
        errors.append("Root resourceType must be Bundle")
    if "entry" not in bundle or not bundle["entry"]:
        errors.append("Bundle must contain entry array")
    types = {e["resource"]["resourceType"] for e in bundle.get("entry", []) if "resource" in e}
    if "Patient" not in types:
        errors.append("Bundle missing Patient resource")
    if "Encounter" not in types:
        errors.append("Bundle missing Encounter resource")
    return errors


def bundle_to_json(bundle: dict[str, Any], indent: int = 2) -> str:
    return json.dumps(bundle, indent=indent)
