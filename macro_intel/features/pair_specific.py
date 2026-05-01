from __future__ import annotations

import pandas as pd

from .core import add_ratio, add_spread


def build_zbgc_features(df: pd.DataFrame, normalized_df: pd.DataFrame) -> pd.DataFrame:
    result = add_ratio(df, "GLD", "TLT", "GLD_TLT_Ratio")
    result = add_spread(result, normalized_df, "GLD", "TLT", "GLD_TLT_Spread_Norm")
    result = add_spread(result, normalized_df, "GLD", "DFII10", "GLD_DFII10_Spread_Norm")
    return result


def build_bzgc_features(df: pd.DataFrame, normalized_df: pd.DataFrame) -> pd.DataFrame:
    result = add_ratio(df, "GLD", "BNO", "GLD_BNO_Ratio")
    result = add_spread(result, normalized_df, "GLD", "BNO", "GLD_BNO_Spread_Norm")
    return result


def build_chfeur_features(df: pd.DataFrame, normalized_df: pd.DataFrame) -> pd.DataFrame:
    result = add_ratio(df, "FXF", "FXE", "CHF_EUR_Ratio")
    result = add_spread(result, normalized_df, "FXF", "FXE", "CHF_EUR_Spread_Norm")
    result["EU_Risk_Spread"] = (result["IRLTLT01ITM156N"] - result["IRLTLT01DEM156N"]) * 100
    result["Inflation_Differential"] = result["CPALTT01CHM657N"] - result["CP0000EZ19M086NEST"]
    return result


def build_chfgc_features(df: pd.DataFrame, normalized_df: pd.DataFrame) -> pd.DataFrame:
    result = add_ratio(df, "FXF", "GLD", "CHF_GLD_Ratio")
    result = add_spread(result, normalized_df, "FXF", "GLD", "CHF_GLD_Spread_Norm")
    result["SNB_Intervention_WoW"] = result["SNB_Sight_Deposits"].diff(7)
    return result


def apply_pair_specific_features(pair_id: str, df: pd.DataFrame, normalized_df: pd.DataFrame) -> pd.DataFrame:
    if pair_id == "ZB_GC":
        return build_zbgc_features(df, normalized_df)
    if pair_id == "BZ_GC":
        return build_bzgc_features(df, normalized_df)
    if pair_id == "CHF_EUR":
        return build_chfeur_features(df, normalized_df)
    if pair_id == "CHF_GC":
        return build_chfgc_features(df, normalized_df)
    raise KeyError(f"Unknown pair_id: {pair_id}")
