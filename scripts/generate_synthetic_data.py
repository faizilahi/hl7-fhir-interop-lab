"""Generate synthetic HL7 ADT messages and a manifest CSV."""

from __future__ import annotations

import csv
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
random.seed(13)

N_MESSAGES = 500
TRIGGERS = ["A01", "A03", "A08"]
NAMES = [
    ("DOE", "JANE"),
    ("SMITH", "ALEX"),
    ("GARCIA", "MARIA"),
    ("NGUYEN", "MINH"),
    ("PATEL", "PRIYA"),
]


def build_message(seq: int, trigger: str) -> str:
    fam, given = random.choice(NAMES)
    pid = f"SYN{seq:05d}"
    visit = f"V{seq:06d}"
    sex = random.choice(["F", "M"])
    birth = random.choice(["19800315", "19750622", "19901201", "19551130"])
    ts = f"2024{random.randint(1,12):02d}{random.randint(1,28):02d}{random.randint(8,18):02d}0000"
    cls = random.choice(["I", "E", "O"])
    return (
        f"MSH|^~\\&|SYNTH_ADT|FAC-EDU|SYNTH_FHIR|LAB|{ts}||ADT^{trigger}|MSG{seq:05d}|P|2.5\r"
        f"EVN|{trigger}|{ts}\r"
        f"PID|1||{pid}^^^SYNTH||{fam}^{given}||{birth}|{sex}\r"
        f"PV1|1|{cls}|||||||{visit}|||||||||||||||||||||||||{ts}\r"
    )


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    blocks = [build_message(i, random.choice(TRIGGERS)) for i in range(1, N_MESSAGES + 1)]
    hl7_path = DATA_DIR / "sample_adt_messages.hl7"
    hl7_path.write_text("\n\n".join(blocks), encoding="utf-8")

    manifest = DATA_DIR / "message_manifest.csv"
    with manifest.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["message_index", "trigger", "patient_id"])
        writer.writeheader()
        for i, block in enumerate(blocks, start=1):
            trigger = block.split("ADT^")[1].split("|")[0]
            pid = block.split("PID|1||")[1].split("^")[0]
            writer.writerow({"message_index": i, "trigger": trigger, "patient_id": pid})

    print(f"Wrote {N_MESSAGES} HL7 messages to {hl7_path} and manifest {manifest}")


if __name__ == "__main__":
    main()
