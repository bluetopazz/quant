from __future__ import annotations

import pandas as pd


def require_columns(df: pd.DataFrame, columns: list[str] | tuple[str, ...]) -> None:
    missing = [column for column in columns if column not in df.columns]
    if missing:
        raise KeyError(f"Missing required columns: {missing}")


def validate_non_empty_frame(df: pd.DataFrame, *, label: str) -> None:
    if df is None or df.empty:
        raise ValueError(f"{label} is empty")
