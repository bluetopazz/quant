from __future__ import annotations

import numpy as np
import pandas as pd


def add_pct_change_columns(
    df: pd.DataFrame,
    columns: list[str] | tuple[str, ...],
    *,
    suffix: str = "_pct",
) -> pd.DataFrame:
    result = df.copy()
    for column in columns:
        result[f"{column}{suffix}"] = result[column].pct_change()
    return result


def add_rolling_correlation(
    df: pd.DataFrame,
    left_return_column: str,
    right_return_column: str,
    *,
    short_window: int = 30,
    long_window: int = 90,
    short_output: str = "Corr_30D",
    long_output: str = "Corr_90D",
) -> pd.DataFrame:
    result = df.copy()
    result[short_output] = result[left_return_column].rolling(window=short_window).corr(result[right_return_column])
    result[long_output] = result[left_return_column].rolling(window=long_window).corr(result[right_return_column])
    return result
