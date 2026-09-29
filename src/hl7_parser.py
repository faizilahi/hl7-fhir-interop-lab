"""Minimal HL7 v2.x pipe-delimited message parser for ADT teaching."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ADTEvent:
    message_type: str
    patient_id: str
    family_name: str
    given_name: str
    birth_date: str
    sex: str
    visit_number: str
    patient_class: str
    admit_datetime: str
    sending_facility: str


def parse_segment(segment: str) -> list[str]:
    return segment.strip().split("|")


def parse_hl7_message(raw: str) -> dict[str, Any]:
    normalized = raw.replace("\r\n", "\n").replace("\r", "\n")
    segments = [s for s in normalized.split("\n") if s.strip()]
    parsed: dict[str, list[list[str]]] = {}
    for seg in segments:
        fields = parse_segment(seg)
        name = fields[0]
        parsed.setdefault(name, []).append(fields)
    return parsed


def adt_from_message(raw: str) -> ADTEvent:
    parsed = parse_hl7_message(raw)
    msh = parsed.get("MSH", [[]])[0]
    pid = parsed.get("PID", [[]])[0]
    pv1 = parsed.get("PV1", [[]])[0]
    msg_type = msh[8] if len(msh) > 8 else ""
    patient_id = pid[3].split("^")[0] if len(pid) > 3 else ""
    name_parts = pid[5].split("^") if len(pid) > 5 else ["", ""]
    return ADTEvent(
        message_type=msg_type,
        patient_id=patient_id,
        family_name=name_parts[0],
        given_name=name_parts[1] if len(name_parts) > 1 else "",
        birth_date=pid[7] if len(pid) > 7 else "",
        sex=pid[8] if len(pid) > 8 else "",
        visit_number=pv1[19] if len(pv1) > 19 else "",
        patient_class=pv1[2] if len(pv1) > 2 else "",
        admit_datetime=pv1[44] if len(pv1) > 44 else "",
        sending_facility=msh[3] if len(msh) > 3 else "",
    )


def adt_to_hl7(event: ADTEvent, trigger: str = "A01") -> str:
    """Rebuild a simplified ADT^trigger message from structured fields."""
    ts = event.admit_datetime or "20240101120000"
    lines = [
        f"MSH|^~\\&|SYNTH_APP|{event.sending_facility}|SYNTH_FHIR|LAB|{ts}||ADT^{trigger}|MSG001|P|2.5",
        f"EVN|{trigger}|{ts}",
        f"PID|1||{event.patient_id}^^^SYNTH||{event.family_name}^{event.given_name}||{event.birth_date}|{event.sex}",
        f"PV1|1|{event.patient_class}|||||||{event.visit_number}|||||||||||||||||||||||||{ts}",
    ]
    return "\n".join(lines) + "\n"
