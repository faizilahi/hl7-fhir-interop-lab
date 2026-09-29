"""Round-trip: extract ADTEvent fields from FHIR Bundle (educational subset)."""

from __future__ import annotations

from hl7_parser import ADTEvent


def fhir_bundle_to_adt(bundle: dict) -> ADTEvent:
    patient = next(
        e["resource"] for e in bundle["entry"] if e["resource"]["resourceType"] == "Patient"
    )
    encounter = next(
        e["resource"] for e in bundle["entry"] if e["resource"]["resourceType"] == "Encounter"
    )
    header = next(
        (
            e["resource"]
            for e in bundle["entry"]
            if e["resource"]["resourceType"] == "MessageHeader"
        ),
        {},
    )
    gender_rev = {"male": "M", "female": "F", "other": "O", "unknown": "U"}
    birth = patient.get("birthDate", "").replace("-", "")
    start = encounter.get("period", {}).get("start", "")
    admit = start.replace("-", "").replace("T", "").replace(":", "")[:14]
    name = patient.get("name", [{}])[0]
    code = header.get("eventCoding", {}).get("code", "A01")
    return ADTEvent(
        message_type=f"ADT^{code}",
        patient_id=patient.get("id", ""),
        family_name=name.get("family", ""),
        given_name=(name.get("given") or [""])[0],
        birth_date=birth,
        sex=gender_rev.get(patient.get("gender", "unknown"), "U"),
        visit_number=encounter.get("id", ""),
        patient_class=encounter.get("class", {}).get("code", "IMP"),
        admit_datetime=admit,
        sending_facility=header.get("source", {}).get("name", "SYNTH_FACILITY"),
    )
