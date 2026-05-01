from __future__ import annotations

import pandas as pd


def full_sample_zscore(series: pd.Series) -> pd.Series:
    s = pd.to_numeric(series, errors="coerce")
    std = s.std(ddof=0)
    if pd.isna(std) or std == 0:
        return pd.Series(index=s.index, dtype=float)
    return (s - s.mean()) / std


def full_sample_zscore_frame(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame({column: full_sample_zscore(df[column]) for column in df.columns}, index=df.index)


def rolling_zscore(series: pd.Series, window: int = 126, min_periods: int | None = None) -> pd.Series:
    s = pd.to_numeric(series, errors="coerce")
    if min_periods is None:
        min_periods = max(20, window // 3)
    mean = s.rolling(window=window, min_periods=min_periods).mean()
    std = s.rolling(window=window, min_periods=min_periods).std(ddof=0)
    z = (s - mean) / std
    return z.replace([float("inf"), float("-inf")], pd.NA)


def add_ratio(df: pd.DataFrame, numerator: str, denominator: str, output_column: str) -> pd.DataFrame:
    result = df.copy()
    result[output_column] = result[numerator] / result[denominator]
    return result


def add_spread(
    df: pd.DataFrame,
    normalized_df: pd.DataFrame,
    left_column: str,
    right_column: str,
    output_column: str,
) -> pd.DataFrame:
    result = df.copy()
    result[output_column] = normalized_df[left_column] - normalized_df[right_column]
    return result


def add_signal_velocity(df: pd.DataFrame, spread_column: str, output_column: str, lookback: int = 5) -> pd.DataFrame:
    result = df.copy()
    result[output_column] = result[spread_column].diff(lookback)
    return result
