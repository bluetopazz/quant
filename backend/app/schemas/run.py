from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class PairRunRequest(BaseModel):
    pair_id: str | None = None
    requested_by_user_id: str | None = None
    trigger_source: str | None = "ui_manual"
    persist_journal: bool = False
    lookback_years: int | None = None
    as_of_date: str | None = None
    runtime_overrides: dict[str, Any] | None = None


class PairRunStatus(BaseModel):
    run_id: str
    pair_id: str
    status: Literal["queued", "running", "success", "degraded_success", "error", "cancelled"]
    created_at: str | None = None
    started_at: str | None = None
    completed_at: str | None = None
    progress_stage: str | None = None
    progress_message: str | None = None
    warning_count: int = 0
    error_code: str | None = None


class RunWarning(BaseModel):
    warning_code: str
    stage: str
    message: str
    source: str | None = None
    field: str | None = None
    severity: str | None = None
    recoverable: bool = True


class RunError(BaseModel):
    error_code: str
    stage: str
    message: str
    source: str | None = None
    retryable: bool = False
    details: dict[str, Any] | None = None


class FeatureSnapshot(BaseModel):
    pair_id: str
    as_of_date: str
    core_metrics: dict[str, Any] = Field(default_factory=dict)
    pair_extensions: dict[str, Any] = Field(default_factory=dict)
    normalization_mode: str = "full_sample_zscore"
    source_freshness: dict[str, Any] | None = None


class ChartPayload(BaseModel):
    chart_id: str
    pair_id: str
    family: str
    title: str
    render_kind: str
    x_axis: dict[str, Any] = Field(default_factory=dict)
    series: list[dict[str, Any]] = Field(default_factory=list)


class AnalystMemo(BaseModel):
    memo_id: str
    pair_id: str
    content: str
    model_name: str
    prompt_version: str
    prompt_style: str | None = None
    prompt_template_id: str | None = None
    system_role: str | None = None
    temperature: float | None = None
    timeout_seconds: int | None = None
    generated_at: str | None = None
    source_summary: dict[str, Any] | None = None


class ParsedSignal(BaseModel):
    pair_id: str
    signal_style: str
    parser_style: str
    parser_version: str
    parse_status: str
    directional_bias: str | None = None
    confidence: str | None = None
    notes: str | None = None
    target_asset: str | None = None
    strategy: str | None = None
    left_leg_label: str | None = None
    right_leg_label: str | None = None
    left_strategy: str | None = None
    right_strategy: str | None = None
    parser_input_memo_id: str | None = None
    used_llm_second_pass: bool = False
    fallback_reason: str | None = None
    raw_parser_output: str | None = None


class RiskTicket(BaseModel):
    pair_id: str
    sizing_mode: str
    account_value_assumption: float
    risk_bps_per_trade: float
    total_risk_budget_usd: float | None = None
    sizing_status: str = "sized"
    notes: str | None = None
    target_asset: str | None = None
    strategy: str | None = None
    contracts: int | None = None
    risk_budget_usd: float | None = None
    left_strategy: str | None = None
    right_strategy: str | None = None
    left_contracts: int | None = None
    right_contracts: int | None = None
    per_leg_budget_usd: float | None = None
    total_budget_usd: float | None = None
    strategy_risk_table_version: str | None = None
    heuristic_name: str | None = None
    sizing_assumptions: dict[str, Any] | None = None


class JournalEntryPreview(BaseModel):
    pair_id: str
    journal_schema_version: str
    journal_mode: str
    preview_payload: dict[str, Any] = Field(default_factory=dict)


class PairRunResult(BaseModel):
    run_id: str
    pair_id: str
    status: str
    run_timestamp: str
    feature_snapshot: FeatureSnapshot
    charts: list[ChartPayload] = Field(default_factory=list)
    analyst_memo: AnalystMemo | None = None
    parsed_signal: ParsedSignal | None = None
    risk_ticket: RiskTicket | None = None
    journal_entry_preview: JournalEntryPreview | None = None
    warnings: list[RunWarning] = Field(default_factory=list)
    error: RunError | None = None
    notebook_reference: str | None = None
    theme: str | None = None
    relationship: str | None = None
    pair_prompt_style: str | None = None
    pair_signal_style: str | None = None
    requested_by_user_id: str | None = None
    trigger_source: str | None = None
    prompt_version: str | None = None
    engine_version: str | None = None
    persistence_summary: dict[str, Any] | None = None


class PairRunSummary(BaseModel):
    run_id: str
    pair_id: str
    status: str
    run_timestamp: str
    warning_count: int = 0
    error_code: str | None = None
    error_message: str | None = None
