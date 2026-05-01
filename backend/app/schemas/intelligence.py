from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AttentionFlag(BaseModel):
    pair_id: str
    severity: str
    title: str
    reason: str
    metric_key: str | None = None
    metric_value: float | None = None
    pair_ids: list[str] = Field(default_factory=list)


class ChangeSummary(BaseModel):
    pair_id: str
    title: str
    description: str
    changed_at: str | None = None
    absolute_zscore_change: float | None = None
    velocity_change: float | None = None
    corr_90d_change: float | None = None
    driver_change_key: str | None = None
    driver_change_value: float | None = None
    attention_score: float | None = None


class PairStateSnapshot(BaseModel):
    snapshot_id: str
    pair_id: str
    source_run_id: str
    snapshot_timestamp: str
    run_timestamp: str | None = None
    as_of_date: str
    status: str
    staleness_status: str
    theme: str | None = None
    relationship: str | None = None
    signal_zscore: float | None = None
    signal_velocity_5d: float | None = None
    corr_30d: float | None = None
    corr_90d: float | None = None
    ratio: float | None = None
    spread_value: float | None = None
    directional_bias: str | None = None
    confidence: str | None = None
    regime_label: str | None = None
    vol_regime: str | None = None
    driver_label: str | None = None
    driver_value: float | None = None
    secondary_driver_label: str | None = None
    secondary_driver_value: float | None = None
    attention_score: float = 0.0
    warning_count: int = 0
    pair_extensions: dict[str, Any] = Field(default_factory=dict)
    source_freshness: dict[str, Any] | None = None


class PairTrajectoryPoint(BaseModel):
    pair_id: str
    run_id: str
    run_timestamp: str
    x_value: float | None = None
    y_value: float | None = None
    color_value: float | None = None
    regime_label: str | None = None
    region_label: str | None = None
    motion_label: str | None = None
    directional_bias: str | None = None
    confidence: str | None = None
    status: str
    x_label: str = "z-score"
    y_label: str = "velocity"
    current: bool = False


class CouplingSnapshot(BaseModel):
    snapshot_timestamp: str
    pair_ids: list[str] = Field(default_factory=list)
    matrix_metric: str
    matrix: list[list[float | None]] = Field(default_factory=list)
    coherence_score: float | None = None
    fragmentation_score: float | None = None
    coherence_delta: float | None = None
    fragmentation_delta: float | None = None


class DeskHistoryPoint(BaseModel):
    snapshot_timestamp: str
    coherence_score: float | None = None
    fragmentation_score: float | None = None
    stress_score: float | None = None
    dominant_regime: str | None = None


class RefreshStatus(BaseModel):
    refresh_id: str | None = None
    status: str
    trigger_source: str | None = None
    started_at: str | None = None
    completed_at: str | None = None
    total_pairs: int = 0
    success_count: int = 0
    degraded_count: int = 0
    failed_count: int = 0
    warning_count: int = 0
    last_successful_snapshot_at: str | None = None
    warnings: list[str] = Field(default_factory=list)
    error_message: str | None = None


class DeskStateSnapshot(BaseModel):
    snapshot_id: str
    snapshot_timestamp: str
    latest_common_run_timestamp: str | None = None
    dominant_regime: str | None = None
    coherence_score: float | None = None
    fragmentation_score: float | None = None
    stress_score: float | None = None
    state_dispersion: float | None = None
    attention_pair_id: str | None = None
    coverage_ratio: float = 0.0
    stale_pair_ids: list[str] = Field(default_factory=list)
    freshness_status: str = "unknown"
    degraded: bool = False
    refresh_status: RefreshStatus | None = None
    pair_states: list[PairStateSnapshot] = Field(default_factory=list)
    coupling: CouplingSnapshot | None = None
    change_summaries: list[ChangeSummary] = Field(default_factory=list)
    attention_flags: list[AttentionFlag] = Field(default_factory=list)
    desk_history: list[DeskHistoryPoint] = Field(default_factory=list)


class IntelligenceOverviewResponse(BaseModel):
    desk: DeskStateSnapshot
    trajectories: dict[str, list[PairTrajectoryPoint]] = Field(default_factory=dict)
