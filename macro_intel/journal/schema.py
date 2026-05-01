from __future__ import annotations

from dataclasses import dataclass


CANONICAL_BASE_FIELDS = (
    "Date",
    "Pair",
    "Theme",
    "Signal_ZScore",
    "Signal_Velocity_5D",
    "Corr_90D",
    "Analyst_Reasoning",
)


@dataclass(frozen=True)
class JournalSchema:
    pair_id: str
    log_file: str
    fieldnames: tuple[str, ...]


PAIR_JOURNAL_SCHEMAS = {
    "ZB_GC": JournalSchema(
        pair_id="ZB_GC",
        log_file="journal_zb_gc.csv",
        fieldnames=(
            "Date",
            "Pair",
            "Theme",
            "Target_Asset",
            "Strategy",
            "Contracts_Sized",
            "Signal_ZScore",
            "Signal_Velocity_5D",
            "Corr_90D",
            "GLD_IVR",
            "TLT_IVR",
            "GLD_VRP",
            "TLT_VRP",
            "DFII10",
            "T10YIE",
            "DTWEXBGS",
            "Analyst_Reasoning",
        ),
    ),
    "BZ_GC": JournalSchema(
        pair_id="BZ_GC",
        log_file="journal_bz_gc.csv",
        fieldnames=(
            "Date",
            "Pair",
            "Theme",
            "Directional_Bias",
            "Strategy_GLD",
            "Contracts_GLD",
            "Strategy_BNO",
            "Contracts_BNO",
            "Signal_ZScore",
            "Signal_Velocity_5D",
            "Corr_90D",
            "GLD_IVR",
            "BNO_IVR",
            "GLD_VRP",
            "BNO_VRP",
            "IPMAN",
            "CPILFESL",
            "Analyst_Reasoning",
        ),
    ),
    "CHF_EUR": JournalSchema(
        pair_id="CHF_EUR",
        log_file="journal_chf_eur.csv",
        fieldnames=(
            "Date",
            "Pair",
            "Theme",
            "Target_Asset",
            "Strategy",
            "Contracts_Sized",
            "Signal_ZScore",
            "Signal_Velocity_5D",
            "Corr_90D",
            "VIX_IVR",
            "FXE_VRP",
            "FXF_VRP",
            "EU_Risk_Spread",
            "Inflation_Differential",
            "Analyst_Reasoning",
        ),
    ),
    "CHF_GC": JournalSchema(
        pair_id="CHF_GC",
        log_file="journal_chf_gc.csv",
        fieldnames=(
            "Date",
            "Pair",
            "Theme",
            "Directional_Bias",
            "Strategy_GLD",
            "Contracts_GLD",
            "Strategy_FXF",
            "Contracts_FXF",
            "Signal_ZScore",
            "Signal_Velocity_5D",
            "Corr_90D",
            "GLD_IVR",
            "CHF_VIX_IVR",
            "GLD_VRP",
            "FXF_VRP",
            "DFII10",
            "SNB_Intervention_WoW",
            "Analyst_Reasoning",
        ),
    ),
}


def get_pair_journal_schema(pair_id: str) -> JournalSchema:
    try:
        return PAIR_JOURNAL_SCHEMAS[pair_id]
    except KeyError as exc:
        raise KeyError(f"Unknown pair journal schema: {pair_id}") from exc
