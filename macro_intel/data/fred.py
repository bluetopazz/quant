from __future__ import annotations

import pandas as pd
from fredapi import Fred


def fetch_fred_series(
    series_ids: list[str] | tuple[str, ...],
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
    api_key: str,
) -> tuple[pd.DataFrame, list[tuple[str, str]]]:
    """Fetch FRED series one by one and return a merged frame plus failures."""

    fred = Fred(api_key=api_key)
    frames: list[pd.Series] = []
    failures: list[tuple[str, str]] = []

    for series_id in series_ids:
        try:
            series = fred.get_series(
                series_id,
                observation_start=start_date,
                observation_end=end_date,
            )
            if series is None or len(series) == 0:
                raise RuntimeError("empty FRED response")
            s = pd.Series(series, name=series_id)
            s.index = pd.to_datetime(s.index)
            frames.append(s)
        except Exception as exc:  # pragma: no cover - network behavior
            failures.append((series_id, str(exc)))

    if not frames:
        return pd.DataFrame(), failures

    return pd.concat(frames, axis=1).sort_index(), failures
