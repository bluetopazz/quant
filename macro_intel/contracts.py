from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class PairRunRequest:
    pair_id: str
    requested_by_user_id: str | None = None
    trigger_source: str | None = None
    persist_journal: bool = False
    lookback_years: int | None = None
    as_of_date: str | None = None
    runtime_overrides: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PairRunStatus:
    run_id: str
    pair_id: str
    status: str
    created_at: str | None = None
    started_at: str | None = None
    completed_at: str | None = None
    progress_stage: str | None = None
    progress_message: str | None = None
    warning_count: int = 0
    error_code: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RunWarning:
    warning_code: str
    stage: str
    message: str
    source: str | None = None
    field: str | None = None
    severity: str | None = None
    recoverable: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RunError:
    error_code: str
    stage: str
    message: str
    source: str | None = None
    retryable: bool = False
    details: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class FeatureSnapshot:
    pair_id: str
    as_of_date: str
    core_metrics: dict[str, Any]
    pair_extensions: dict[str, Any] = field(default_factory=dict)
    normalization_mode: str = "full_sample_zscore"
    source_freshness: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ChartPayload:
    chart_id: str
    pair_id: str
    family: str
    title: str
    render_kind: str
    x_axis: dict[str, Any]
    series: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AnalystMemo:
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

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ParsedSignal:
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

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RiskTicket:
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

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class JournalEntryPreview:
    pair_id: str
    journal_schema_version: str
    journal_mode: str
    preview_payload: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PairRunResult:
    run_id: str
    pair_id: str
    status: str
    run_timestamp: str
    feature_snapshot: FeatureSnapshot
    charts: list[ChartPayload]
    analyst_memo: AnalystMemo | None
    parsed_signal: ParsedSignal | None
    risk_ticket: RiskTicket | None
    journal_entry_preview: JournalEntryPreview | None
    warnings: list[RunWarning] = field(default_factory=list)
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

    def to_dict(self) -> dict[str, Any]:
        return {
            **asdict(self),
            "feature_snapshot": self.feature_snapshot.to_dict(),
            "charts": [chart.to_dict() for chart in self.charts],
            "analyst_memo": self.analyst_memo.to_dict() if self.analyst_memo else None,
            "parsed_signal": self.parsed_signal.to_dict() if self.parsed_signal else None,
            "risk_ticket": self.risk_ticket.to_dict() if self.risk_ticket else None,
            "journal_entry_preview": self.journal_entry_preview.to_dict() if self.journal_entry_preview else None,
            "warnings": [warning.to_dict() for warning in self.warnings],
            "error": self.error.to_dict() if self.error else None,
        }
