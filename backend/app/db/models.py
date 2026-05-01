from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship as orm_relationship

from backend.app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(512))
    role: Mapped[str] = mapped_column(String(50), default="operator")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class PairRun(Base):
    __tablename__ = "pair_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    pair_id: Mapped[str] = mapped_column(String(50), index=True)
    status: Mapped[str] = mapped_column(String(50), index=True)
    notebook_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    theme: Mapped[str | None] = mapped_column(String(120), nullable=True)
    relationship: Mapped[str | None] = mapped_column(String(120), nullable=True)
    pair_prompt_style: Mapped[str | None] = mapped_column(String(50), nullable=True)
    pair_signal_style: Mapped[str | None] = mapped_column(String(50), nullable=True)
    prompt_version: Mapped[str | None] = mapped_column(String(120), nullable=True)
    engine_version: Mapped[str | None] = mapped_column(String(120), nullable=True)
    requested_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    trigger_source: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    run_timestamp: Mapped[datetime | None] = mapped_column(DateTime, index=True, nullable=True)
    warning_count: Mapped[int] = mapped_column(Integer, default=0)
    error_code: Mapped[str | None] = mapped_column(String(120), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    persistence_summary: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    journal_schema_version: Mapped[str | None] = mapped_column(String(120), nullable=True)
    journal_preview_mode: Mapped[str | None] = mapped_column(String(50), nullable=True)
    journal_preview_payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    feature_snapshot: Mapped["PairRunFeatureSnapshot | None"] = orm_relationship(back_populates="pair_run", uselist=False)
    memo: Mapped["PairRunMemo | None"] = orm_relationship(back_populates="pair_run", uselist=False)
    signal: Mapped["PairRunSignal | None"] = orm_relationship(back_populates="pair_run", uselist=False)
    risk_ticket: Mapped["PairRunRiskTicket | None"] = orm_relationship(back_populates="pair_run", uselist=False)
    charts: Mapped[list["PairRunChartPayload"]] = orm_relationship(back_populates="pair_run", cascade="all, delete-orphan")
    journal_entries: Mapped[list["JournalEntry"]] = orm_relationship(back_populates="pair_run", cascade="all, delete-orphan")


class PairRunFeatureSnapshot(Base):
    __tablename__ = "pair_run_feature_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pair_run_id: Mapped[int] = mapped_column(ForeignKey("pair_runs.id"), unique=True, index=True)
    pair_id: Mapped[str] = mapped_column(String(50), index=True)
    as_of_date: Mapped[str] = mapped_column(String(20))
    normalization_mode: Mapped[str] = mapped_column(String(80), default="full_sample_zscore")
    core_metrics_json: Mapped[dict] = mapped_column(JSON)
    pair_extensions_json: Mapped[dict] = mapped_column(JSON)
    source_freshness_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    pair_run: Mapped[PairRun] = orm_relationship(back_populates="feature_snapshot")


class PairRunMemo(Base):
    __tablename__ = "pair_run_memos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pair_run_id: Mapped[int] = mapped_column(ForeignKey("pair_runs.id"), unique=True, index=True)
    memo_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    pair_id: Mapped[str] = mapped_column(String(50), index=True)
    content: Mapped[str] = mapped_column(Text)
    model_name: Mapped[str] = mapped_column(String(120))
    prompt_version: Mapped[str] = mapped_column(String(120))
    prompt_style: Mapped[str | None] = mapped_column(String(50), nullable=True)
    prompt_template_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    system_role: Mapped[str | None] = mapped_column(String(120), nullable=True)
    temperature: Mapped[float | None] = mapped_column(Float, nullable=True)
    timeout_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    generated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    source_summary_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    pair_run: Mapped[PairRun] = orm_relationship(back_populates="memo")


class PairRunSignal(Base):
    __tablename__ = "pair_run_signals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pair_run_id: Mapped[int] = mapped_column(ForeignKey("pair_runs.id"), unique=True, index=True)
    pair_id: Mapped[str] = mapped_column(String(50), index=True)
    signal_style: Mapped[str] = mapped_column(String(50))
    parser_style: Mapped[str] = mapped_column(String(80))
    parser_version: Mapped[str] = mapped_column(String(80))
    parse_status: Mapped[str] = mapped_column(String(50))
    directional_bias: Mapped[str | None] = mapped_column(String(120), nullable=True)
    confidence: Mapped[str | None] = mapped_column(String(50), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    target_asset: Mapped[str | None] = mapped_column(String(120), nullable=True)
    strategy: Mapped[str | None] = mapped_column(String(80), nullable=True)
    left_leg_label: Mapped[str | None] = mapped_column(String(50), nullable=True)
    right_leg_label: Mapped[str | None] = mapped_column(String(50), nullable=True)
    left_strategy: Mapped[str | None] = mapped_column(String(80), nullable=True)
    right_strategy: Mapped[str | None] = mapped_column(String(80), nullable=True)
    parser_input_memo_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    used_llm_second_pass: Mapped[bool] = mapped_column(Boolean, default=False)
    fallback_reason: Mapped[str | None] = mapped_column(String(120), nullable=True)
    raw_parser_output: Mapped[str | None] = mapped_column(Text, nullable=True)

    pair_run: Mapped[PairRun] = orm_relationship(back_populates="signal")


class PairRunRiskTicket(Base):
    __tablename__ = "pair_run_risk_tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pair_run_id: Mapped[int] = mapped_column(ForeignKey("pair_runs.id"), unique=True, index=True)
    pair_id: Mapped[str] = mapped_column(String(50), index=True)
    sizing_mode: Mapped[str] = mapped_column(String(50))
    account_value_assumption: Mapped[float] = mapped_column(Float)
    risk_bps_per_trade: Mapped[float] = mapped_column(Float)
    total_risk_budget_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
    sizing_status: Mapped[str] = mapped_column(String(50), default="sized")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    target_asset: Mapped[str | None] = mapped_column(String(120), nullable=True)
    strategy: Mapped[str | None] = mapped_column(String(80), nullable=True)
    contracts: Mapped[int | None] = mapped_column(Integer, nullable=True)
    risk_budget_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
    left_strategy: Mapped[str | None] = mapped_column(String(80), nullable=True)
    right_strategy: Mapped[str | None] = mapped_column(String(80), nullable=True)
    left_contracts: Mapped[int | None] = mapped_column(Integer, nullable=True)
    right_contracts: Mapped[int | None] = mapped_column(Integer, nullable=True)
    per_leg_budget_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_budget_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
    strategy_risk_table_version: Mapped[str | None] = mapped_column(String(80), nullable=True)
    heuristic_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    sizing_assumptions_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    pair_run: Mapped[PairRun] = orm_relationship(back_populates="risk_ticket")


class PairRunChartPayload(Base):
    __tablename__ = "pair_run_chart_payloads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pair_run_id: Mapped[int] = mapped_column(ForeignKey("pair_runs.id"), index=True)
    pair_id: Mapped[str] = mapped_column(String(50), index=True)
    chart_id: Mapped[str] = mapped_column(String(120), index=True)
    family: Mapped[str] = mapped_column(String(80), index=True)
    title: Mapped[str] = mapped_column(String(255))
    render_kind: Mapped[str] = mapped_column(String(80))
    payload_json: Mapped[dict] = mapped_column(JSON)

    pair_run: Mapped[PairRun] = orm_relationship(back_populates="charts")


class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pair_run_id: Mapped[int] = mapped_column(ForeignKey("pair_runs.id"), index=True)
    pair_id: Mapped[str] = mapped_column(String(50), index=True)
    run_id: Mapped[str] = mapped_column(String(64), index=True)
    journal_schema_version: Mapped[str] = mapped_column(String(120))
    journal_mode: Mapped[str] = mapped_column(String(50))
    payload_json: Mapped[dict] = mapped_column(JSON)
    csv_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    pair_run: Mapped[PairRun] = orm_relationship(back_populates="journal_entries")


class PairStateSnapshot(Base):
    __tablename__ = "pair_state_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    snapshot_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    pair_id: Mapped[str] = mapped_column(String(50), index=True)
    source_run_id: Mapped[str] = mapped_column(String(64), index=True)
    source_pair_run_id: Mapped[int | None] = mapped_column(ForeignKey("pair_runs.id"), nullable=True)
    snapshot_timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    run_timestamp: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, index=True)
    as_of_date: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(50), index=True)
    staleness_status: Mapped[str] = mapped_column(String(50), default="fresh")
    theme: Mapped[str | None] = mapped_column(String(120), nullable=True)
    relationship: Mapped[str | None] = mapped_column(String(120), nullable=True)
    signal_zscore: Mapped[float | None] = mapped_column(Float, nullable=True)
    signal_velocity_5d: Mapped[float | None] = mapped_column(Float, nullable=True)
    corr_30d: Mapped[float | None] = mapped_column(Float, nullable=True)
    corr_90d: Mapped[float | None] = mapped_column(Float, nullable=True)
    ratio: Mapped[float | None] = mapped_column(Float, nullable=True)
    spread_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    directional_bias: Mapped[str | None] = mapped_column(String(120), nullable=True)
    confidence: Mapped[str | None] = mapped_column(String(50), nullable=True)
    regime_label: Mapped[str | None] = mapped_column(String(120), nullable=True)
    vol_regime: Mapped[str | None] = mapped_column(String(80), nullable=True)
    driver_label: Mapped[str | None] = mapped_column(String(120), nullable=True)
    driver_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    secondary_driver_label: Mapped[str | None] = mapped_column(String(120), nullable=True)
    secondary_driver_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    attention_score: Mapped[float] = mapped_column(Float, default=0.0)
    warning_count: Mapped[int] = mapped_column(Integer, default=0)
    state_payload_json: Mapped[dict] = mapped_column(JSON)
    pair_extensions_json: Mapped[dict] = mapped_column(JSON)
    source_freshness_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class DeskStateSnapshot(Base):
    __tablename__ = "desk_state_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    snapshot_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    snapshot_key: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    snapshot_timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    latest_common_run_timestamp: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    dominant_regime: Mapped[str | None] = mapped_column(String(120), nullable=True)
    coherence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    fragmentation_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    stress_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    state_dispersion: Mapped[float | None] = mapped_column(Float, nullable=True)
    attention_pair_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    coverage_ratio: Mapped[float] = mapped_column(Float, default=0.0)
    stale_pair_ids_json: Mapped[list | None] = mapped_column(JSON, nullable=True)
    summary_json: Mapped[dict] = mapped_column(JSON)

    coupling_snapshots: Mapped[list["CouplingSnapshot"]] = orm_relationship(
        back_populates="desk_state_snapshot",
        cascade="all, delete-orphan",
    )


class CouplingSnapshot(Base):
    __tablename__ = "coupling_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    desk_state_snapshot_id: Mapped[int] = mapped_column(ForeignKey("desk_state_snapshots.id"), index=True)
    snapshot_timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    matrix_metric: Mapped[str] = mapped_column(String(80), default="state_similarity")
    coherence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    fragmentation_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    matrix_json: Mapped[dict] = mapped_column(JSON)
    payload_json: Mapped[dict] = mapped_column(JSON)

    desk_state_snapshot: Mapped[DeskStateSnapshot] = orm_relationship(back_populates="coupling_snapshots")


class IntelligenceRefreshJob(Base):
    __tablename__ = "intelligence_refresh_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    refresh_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    trigger_source: Mapped[str] = mapped_column(String(80), index=True)
    status: Mapped[str] = mapped_column(String(50), index=True)
    requested_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    total_pairs: Mapped[int] = mapped_column(Integer, default=0)
    success_count: Mapped[int] = mapped_column(Integer, default=0)
    degraded_count: Mapped[int] = mapped_column(Integer, default=0)
    failed_count: Mapped[int] = mapped_column(Integer, default=0)
    warning_count: Mapped[int] = mapped_column(Integer, default=0)
    last_successful_snapshot_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    pair_results_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    warnings_json: Mapped[list | None] = mapped_column(JSON, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
