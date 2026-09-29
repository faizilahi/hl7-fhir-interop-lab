#!/usr/bin/env python3
"""Generate a small batch of synthetic ADT^A01 messages."""
from __future__ import annotations

import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)
RNG = random.Random(42)
CR = chr(13)


def build_message(i: int) -> str:
    ts = f"20241112{i:02d}{i % 60:02d}00"
    family = RNG.choice(["DOE", "LEE", "PATEL", "GARCIA", "KIM"])
    given = RNG.choice(["JANE", "JOHN", "SAM", "AVA", "OMAR"])
    dob = f"{RNG.randint(1940, 2005)}{RNG.randint(1, 12):02d}{RNG.randint(1, 28):02d}"
    sex = RNG.choice(["F", "M"])
    poc = RNG.choice(["ICU", "MED", "ED", "SURG"])
    room = RNG.randint(100, 400)
    # PV1-19 = visit number, PV1-44 = admit datetime (classic field positions)
    segs = [
        f"MSH|^~\\&|EPIC|HOSP|DEST|HOSP|{ts}||ADT^A01|MSG{i:05d}|P|2.5",
        f"EVN|A01|{ts}",
        (
            f"PID|1||MRN{70000 + i}^^^HOSP^MR||{family}^{given}^A||{dob}|{sex}"
            "|||123 MAIN ST^^BOSTON^MA^02108"
        ),
        (
            f"PV1|1|I|{poc}^{room}^1^HOSP||||ATTENDING^SMITH^ALAN^^^^^^^^^NPI|"
            f"REF^LEE^SUE|||||||||||ENC-{40000 + i}|||||||||||||||||||||||||{ts}"
        ),
    ]
    return CR.join(segs)


def main() -> None:
    messages = [build_message(i) for i in range(1, 81)]
    (DATA / "adt_batch.hl7").write_bytes(("\n".join(messages) + "\n").encode("utf-8"))
    print(f"Wrote {len(messages)} ADT messages to {DATA / 'adt_batch.hl7'}")


if __name__ == "__main__":
    main()
