from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from backend.app.schemas.run import PairRunSummary


class PairCardResponse(BaseModel):
    pair_id: str
    notebook_name: str
    theme: str
    relationship: str
    prompt_style: str
    signal_shape: str
    parser_style: str
    latest_run: PairRunSummary | None = None


class PairDetailResponse(BaseModel):
    pair_id: str
    notebook_name: str
    theme: str
    relationship: str
    yfinance_tickers: list[str]
    fred_series_ids: list[str]
    prompt_style: str
    parser_style: str
    signal_shape: str
    external_apis: list[str]
    feature_flags: list[str]
    special_handling_rules: list[str]
    chart_metadata: dict[str, str] = Field(default_factory=dict)
    latest_run: PairRunSummary | None = None
