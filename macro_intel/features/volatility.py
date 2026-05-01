from __future__ import annotations

import numpy as np
import pandas as pd


def add_historical_volatility(
    df: pd.DataFrame,
    return_columns: dict[str, str],
    *,
    window: int = 30,
    annualization_factor: int = 252,
) -> pd.DataFrame:
    result = df.copy()
    for return_column, output_column in return_columns.items():
        result[output_column] = result[return_column].rolling(window=window).std() * np.sqrt(annualization_factor)
    return result


def add_iv_rank(
    df: pd.DataFrame,
    iv_columns: dict[str, str],
    *,
    window: int = 252,
) -> pd.DataFrame:
    result = df.copy()
    for iv_column, output_column in iv_columns.items():
        rolling_min = result[iv_column].rolling(window=window).min()
        rolling_max = result[iv_column].rolling(window=window).max()
        result[output_column] = 100 * (result[iv_column] - rolling_min) / (rolling_max - rolling_min)
    return result


def add_vrp(df: pd.DataFrame, iv_to_hv_columns: dict[str, tuple[str, str]]) -> pd.DataFrame:
    result = df.copy()
    for output_column, (iv_column, hv_column) in iv_to_hv_columns.items():
        result[output_column] = result[iv_column] - result[hv_column]
    return result
