#!/usr/bin/env python3
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.pipeline import walk_message

DATA = ROOT / "data"
OUTPUT = ROOT / "output"


def main() -> None:
    OUTPUT.mkdir(exist_ok=True)
    sample = (DATA / "sample_adt_a01.hl7").read_text(encoding="utf-8")
    walked = walk_message(sample)
    print("=== Warehouse row for MSG00042 ===")
    print(json.dumps(walked["warehouse_row"], indent=2))

    batch_path = DATA / "adt_batch.hl7"
    rows = []
    if batch_path.exists():
        # Binary read preserves CR segment separators; text mode would turn them into LF.
        raw_batch = batch_path.read_bytes().decode("utf-8")
        for block in raw_batch.split("\n"):
            block = block.strip()
            if not block:
                continue
            try:
                rows.append(walk_message(block)["warehouse_row"])
            except Exception as exc:  # noqa: BLE001
                rows.append({"error": str(exc), "raw_preview": block[:80]})
    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT / "adt_warehouse_rows.csv", index=False)
    print(f"Batch warehouse rows: {len(df)}")


if __name__ == "__main__":
    main()
