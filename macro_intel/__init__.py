"""Macro Relative-Value Intelligence Suite shared package."""

from .config.pairs import PAIR_REGISTRY, PairConfig, get_pair_config
from .config.settings import Settings
from .contracts import (
    AnalystMemo,
    ChartPayload,
    FeatureSnapshot,
    JournalEntryPreview,
    PairRunRequest,
    PairRunResult,
    PairRunStatus,
    ParsedSignal,
    RiskTicket,
    RunError,
    RunWarning,
)
from .engine import PairRunResult, run_pair_analysis

__all__ = [
    "PAIR_REGISTRY",
    "AnalystMemo",
    "ChartPayload",
    "FeatureSnapshot",
    "JournalEntryPreview",
    "PairConfig",
    "PairRunRequest",
    "PairRunResult",
    "PairRunStatus",
    "ParsedSignal",
    "RiskTicket",
    "RunError",
    "RunWarning",
    "Settings",
    "get_pair_config",
    "run_pair_analysis",
]
