from __future__ import annotations

import pandas as pd


def five_year_window(end_date: pd.Timestamp | None = None) -> tuple[pd.Timestamp, pd.Timestamp]:
    end = pd.Timestamp.today().normalize() if end_date is None else pd.Timestamp(end_date)
    start = end - pd.Timedelta(days=5 * 365)
    return start, end


def next_available_index(index: pd.Index, dt: pd.Timestamp) -> pd.Timestamp | None:
    ts = pd.Timestamp(dt)
    position = index.searchsorted(ts, side="left")
    if position >= len(index):
        return None
    return index[position]
