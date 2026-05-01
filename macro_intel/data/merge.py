from __future__ import annotations

import pandas as pd


def merge_frames_ffill(
    frames: list[pd.DataFrame],
    *,
    required_columns: list[str] | tuple[str, ...] | None = None,
    drop_initial_na: bool = True,
) -> pd.DataFrame:
    """Concatenate frames on the index, forward-fill slower data, and optionally require core columns."""

    usable_frames = [frame for frame in frames if frame is not None and not frame.empty]
    if not usable_frames:
        return pd.DataFrame()

    merged = pd.concat(usable_frames, axis=1).sort_index().ffill()
    if required_columns:
        merged = merged.dropna(subset=list(required_columns))
    elif drop_initial_na:
        merged = merged.dropna()
    return merged
