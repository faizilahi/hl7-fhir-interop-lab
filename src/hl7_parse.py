"""Minimal HL7v2 pipe parser for ADT messages."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class HL7Message:
    segments: dict[str, list[str]] = field(default_factory=dict)
    raw: str = ""

    def field(self, segment: str, index: int, default: str = "") -> str:
        """1-based field index after segment name (PID.3 => index 3)."""
        rows = self.segments.get(segment)
        if not rows:
            return default
        parts = rows[0].split("|")
        # parts[0] is segment id
        if index >= len(parts):
            return default
        return parts[index]

    def component(self, segment: str, field_index: int, component_index: int) -> str:
        val = self.field(segment, field_index)
        comps = val.split("^")
        if component_index - 1 >= len(comps):
            return ""
        return comps[component_index - 1]


def parse_hl7(raw: str) -> HL7Message:
    text = raw.replace("\r\n", "\n").replace("\r", "\n")
    msg = HL7Message(raw=raw)
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        seg = line.split("|", 1)[0]
        msg.segments.setdefault(seg, []).append(line)
    return msg


def is_adt_a01(msg: HL7Message) -> bool:
    msh9 = msg.field("MSH", 8)  # in MSH, field indices shift because MSH.1 is encoding chars
    # MSH|^~\&|... field list: [MSH, ^~\&, sending, ..., ADT^A01, ...]
    # Depending on split, message type is typically at index 8
    if "ADT^A01" in msh9:
        return True
    # Fallback scan
    for line in msg.segments.get("MSH", []):
        if "ADT^A01" in line:
            return True
    return False
