from __future__ import annotations

import os

import pandas as pd


def read_journal(path: str, *, parse_dates: list[str] | None = None) -> pd.DataFrame:
    if not os.path.isfile(path):
        raise FileNotFoundError(f"{path} does not exist")
    if os.path.getsize(path) == 0:
        raise ValueError(f"{path} is empty")
    return pd.read_csv(path, parse_dates=parse_dates)


def standardize_trade_journal(df_log: pd.DataFrame, source_file: str) -> pd.DataFrame:
    """Normalize current per-pair journal shapes into the backtest-ready common schema."""

    required = {"Date", "Pair", "Signal_ZScore"}
    missing = required - set(df_log.columns)
    if missing:
        raise KeyError(f"{source_file}: missing required columns {sorted(missing)}")

    df_std = pd.DataFrame(index=df_log.index)
    df_std["Date"] = pd.to_datetime(df_log["Date"], errors="coerce")
    df_std["Pair"] = df_log["Pair"].astype(str).str.strip()
    df_std["Signal_ZScore"] = pd.to_numeric(df_log["Signal_ZScore"], errors="coerce")

    if "Strategy" in df_log.columns:
        df_std["Strategy"] = df_log["Strategy"].astype(str).str.strip()
        if "Contracts_Sized" in df_log.columns:
            df_std["Contracts"] = pd.to_numeric(df_log["Contracts_Sized"], errors="coerce")
        else:
            df_std["Contracts"] = 1
        if "Directional_Bias" in df_log.columns:
            df_std["Directional_Bias"] = df_log["Directional_Bias"].astype(str).str.strip()
        elif "Target_Asset" in df_log.columns:
            df_std["Directional_Bias"] = df_log["Target_Asset"].astype(str).str.strip()
        else:
            df_std["Directional_Bias"] = df_std["Strategy"]
    else:
        if "Strategy_GLD" in df_log.columns:
            df_std["Strategy"] = df_log["Strategy_GLD"].astype(str).str.strip()
        else:
            df_std["Strategy"] = "Unknown"
        if "Contracts_GLD" in df_log.columns:
            df_std["Contracts"] = pd.to_numeric(df_log["Contracts_GLD"], errors="coerce")
        else:
            df_std["Contracts"] = 1
        if "Directional_Bias" in df_log.columns:
            df_std["Directional_Bias"] = df_log["Directional_Bias"].astype(str).str.strip()
        else:
            df_std["Directional_Bias"] = df_std["Strategy"]

    df_std["Contracts"] = df_std["Contracts"].fillna(1).clip(lower=0)
    df_std["Source_File"] = source_file
    df_std = df_std.dropna(subset=["Date", "Pair", "Signal_ZScore"])
    df_std = df_std[df_std["Strategy"].fillna("No_Trade") != "No_Trade"]
    return df_std.reset_index(drop=True)


def read_all_pair_journals(paths: list[str] | tuple[str, ...]) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for path in paths:
        df_log = read_journal(path, parse_dates=["Date"])
        frames.append(standardize_trade_journal(df_log, path))
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, axis=0).sort_values(["Date", "Pair"]).reset_index(drop=True)
