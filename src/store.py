"""Durable store writer: append warehouse rows with idempotent msg_control_id."""
from __future__ import annotations

from pathlib import Path

import pandas as pd


def upsert_rows(existing: pd.DataFrame | None, new_rows: pd.DataFrame, key: str = "msg_control_id") -> pd.DataFrame:
    if existing is None or existing.empty:
        return new_rows.copy()
    combined = pd.concat([existing, new_rows], ignore_index=True)
    return combined.drop_duplicates(subset=[key], keep="last")


def write_store(path: Path, rows: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows.to_csv(path, index=False)


def load_store(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)
