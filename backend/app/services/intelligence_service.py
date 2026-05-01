from __future__ import annotations

from datetime import datetime, timezone
from math import sqrt
from threading import Lock, Thread
from time import sleep
from typing import Any
from uuid import uuid4

from sqlalchemy.orm import Session

from backend.app.core.config import settings as app_settings
from backend.app.db.models import CouplingSnapshot as CouplingSnapshotModel
from backend.app.db.models import DeskStateSnapshot as DeskStateSnapshotModel
from backend.app.db.models import IntelligenceRefreshJob
from backend.app.db.models import PairRun, PairStateSnapshot as PairStateSnapshotModel
from backend.app.db.session import SessionLocal
from backend.app.schemas.intelligence import (
    AttentionFlag,
    ChangeSummary,
    CouplingSnapshot,
    DeskHistoryPoint,
    DeskStateSnapshot,
    IntelligenceOverviewResponse,
    PairStateSnapshot,
    PairTrajectoryPoint,
    RefreshStatus,
)
from backend.app.services.pair_runner import execute_pair_run, history_for_pair, normalize_pair_id


PAIR_ORDER = ["ZB_GC", "BZ_GC", "CHF_EUR", "CHF_GC"]
PAIR_DRIVER_KEYS: dict[str, list[tuple[str, str]]] = {
    "ZB_GC": [("dfii10", "Real Yield"), ("t10yie", "Breakeven Inflation"), ("dtwexbgs", "Broad USD")],
    "BZ_GC": [("ipman", "Manufacturing Activity"), ("cpilfesl", "Core Inflation")],
    "CHF_EUR": [("eu_risk_spread", "EU Risk Spread"), ("inflation_differential", "Inflation Differential")],
    "CHF_GC": [("snb_intervention_wow", "SNB Intervention"), ("dfii10", "Real Yield")],
}
PAIR_TRAJECTORY_AXES: dict[str, dict[str, str]] = {
    "ZB_GC": {"x": "signal_zscore", "x_label": "Spread z-score", "y": "dfii10", "y_label": "Real Yield"},
    "BZ_GC": {"x": "signal_zscore", "x_label": "Spread z-score", "y": "ipman", "y_label": "Manufacturing Activity"},
    "CHF_EUR": {"x": "eu_risk_spread", "x_label": "EU Risk Spread", "y": "inflation_differential", "y_label": "Inflation Differential"},
    "CHF_GC": {"x": "signal_zscore", "x_label": "Spread z-score", "y": "snb_intervention_wow", "y_label": "SNB Intervention WoW"},
}

_refresh_lock = Lock()
_background_thread_started = False


def _iso_or_none(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


def _now_utc() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _safe_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _refresh_status_from_job(job: IntelligenceRefreshJob | None) -> RefreshStatus | None:
    if job is None:
        return None
    return RefreshStatus(
        refresh_id=job.refresh_id,
        status=job.status,
        trigger_source=job.trigger_source,
        started_at=_iso_or_none(job.started_at),
        completed_at=_iso_or_none(job.completed_at),
        total_pairs=job.total_pairs,
        success_count=job.success_count,
        degraded_count=job.degraded_count,
        failed_count=job.failed_count,
        warning_count=job.warning_count,
        last_successful_snapshot_at=_iso_or_none(job.last_successful_snapshot_at),
        warnings=[str(item) for item in (job.warnings_json or [])],
        error_message=job.error_message,
    )


def _freshness_status(run_timestamp: datetime | None, refresh_job: IntelligenceRefreshJob | None) -> str:
    if refresh_job is not None and refresh_job.status == "degraded":
        return "degraded"
    if run_timestamp is None:
        return "unknown"
    age_days = max(0.0, (_now_utc() - run_timestamp).total_seconds() / 86400.0)
    if age_days <= 2:
        return "fresh"
    if age_days <= 5:
        return "watch"
    return "stale"


def _staleness_status(run_timestamp: datetime | None) -> str:
    if run_timestamp is None:
        return "unknown"
    age_days = max(0.0, (_now_utc() - run_timestamp).total_seconds() / 86400.0)
    if age_days <= 3:
        return "fresh"
    if age_days <= 7:
        return "watch"
    return "stale"


def _regime_for_pair(pair_id: str, metrics: dict[str, Any], extensions: dict[str, Any]) -> str:
    zscore = _safe_float(metrics.get("signal_zscore")) or 0.0
    velocity = _safe_float(metrics.get("signal_velocity_5d")) or 0.0
    corr = _safe_float(metrics.get("corr_90d")) or 0.0
    if pair_id == "ZB_GC":
        if corr < 0 and zscore > 0.5:
            return "sovereign_distrust"
        if corr > 0.2 and abs(zscore) < 1.0:
            return "classic_haven_alignment"
        return "haven_transition"
    if pair_id == "BZ_GC":
        if corr < 0:
            return "defensive_growth_scare"
        if corr > 0.2 and zscore < 0:
            return "growth_heat"
        return "inflation_stress_transition"
    if pair_id == "CHF_EUR":
        eu_risk = _safe_float(extensions.get("eu_risk_spread")) or 0.0
        if corr < 0.5 or eu_risk > 0.8:
            return "europe_divergence"
        return "usd_beta_chop"
    snb = _safe_float(extensions.get("snb_intervention_wow")) or 0.0
    if corr < 0 or abs(snb) > 0.05:
        return "haven_fragmentation"
    if abs(velocity) < 0.1 and abs(zscore) < 0.75:
        return "managed_haven_balance"
    return "haven_alignment"


def _vol_regime_for_pair(pair_id: str, extensions: dict[str, Any]) -> str:
    candidates = {
        "ZB_GC": [extensions.get("gld_ivr"), extensions.get("tlt_ivr")],
        "BZ_GC": [extensions.get("gld_ivr"), extensions.get("bno_ivr")],
        "CHF_EUR": [extensions.get("vix_ivr")],
        "CHF_GC": [extensions.get("gld_ivr"), extensions.get("chf_vix_ivr")],
    }[pair_id]
    usable = [_safe_float(item) for item in candidates if _safe_float(item) is not None]
    if not usable:
        return "unknown"
    level = max(usable)
    if level >= 70:
        return "elevated"
    if level >= 40:
        return "active"
    return "contained"


def _driver_summary(pair_id: str, extensions: dict[str, Any]) -> tuple[str | None, float | None, str | None, float | None]:
    ranked: list[tuple[str, str, float]] = []
    for key, label in PAIR_DRIVER_KEYS.get(pair_id, []):
        value = _safe_float(extensions.get(key))
        if value is None:
            continue
        ranked.append((key, label, value))
    ranked.sort(key=lambda item: abs(item[2]), reverse=True)
    primary = ranked[0] if ranked else None
    secondary = ranked[1] if len(ranked) > 1 else None
    return (
        primary[1] if primary else None,
        primary[2] if primary else None,
        secondary[1] if secondary else None,
        secondary[2] if secondary else None,
    )


def _attention_score(metrics: dict[str, Any], warning_count: int, driver_value: float | None) -> float:
    zscore = abs(_safe_float(metrics.get("signal_zscore")) or 0.0)
    velocity = abs(_safe_float(metrics.get("signal_velocity_5d")) or 0.0)
    corr = _safe_float(metrics.get("corr_90d"))
    corr_penalty = abs(corr) if corr is not None else 0.0
    driver_component = abs(driver_value or 0.0)
    score = zscore * 1.7 + velocity * 4.0 + driver_component * 0.5 + max(0.0, 1.0 - corr_penalty) + warning_count * 0.75
    return round(score, 3)


def _latest_usable_run_for_pair(db: Session, pair_id: str) -> PairRun | None:
    canonical = normalize_pair_id(pair_id)
    runs = history_for_pair(db, canonical, limit=10)
    for run in runs:
        if run.feature_snapshot is not None and run.status in {"success", "degraded_success"}:
            return run
    return None


def _serialize_pair_state_model(model: PairStateSnapshotModel) -> PairStateSnapshot:
    return PairStateSnapshot(
        snapshot_id=model.snapshot_id,
        pair_id=model.pair_id,
        source_run_id=model.source_run_id,
        snapshot_timestamp=model.snapshot_timestamp.isoformat(),
        run_timestamp=_iso_or_none(model.run_timestamp),
        as_of_date=model.as_of_date,
        status=model.status,
        staleness_status=model.staleness_status,
        theme=model.theme,
        relationship=model.relationship,
        signal_zscore=model.signal_zscore,
        signal_velocity_5d=model.signal_velocity_5d,
        corr_30d=model.corr_30d,
        corr_90d=model.corr_90d,
        ratio=model.ratio,
        spread_value=model.spread_value,
        directional_bias=model.directional_bias,
        confidence=model.confidence,
        regime_label=model.regime_label,
        vol_regime=model.vol_regime,
        driver_label=model.driver_label,
        driver_value=model.driver_value,
        secondary_driver_label=model.secondary_driver_label,
        secondary_driver_value=model.secondary_driver_value,
        attention_score=model.attention_score,
        warning_count=model.warning_count,
        pair_extensions=model.pair_extensions_json or {},
        source_freshness=model.source_freshness_json,
    )


def _vector_from_state(state: PairStateSnapshot) -> list[float]:
    return [state.signal_zscore or 0.0, state.signal_velocity_5d or 0.0, state.corr_90d or 0.0]


def _average(values: list[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


def _pair_state_from_run(run: PairRun, *, refresh_job: IntelligenceRefreshJob | None = None) -> PairStateSnapshot:
    metrics = run.feature_snapshot.core_metrics_json if run.feature_snapshot else {}
    extensions = run.feature_snapshot.pair_extensions_json if run.feature_snapshot else {}
    primary_label, primary_value, secondary_label, secondary_value = _driver_summary(run.pair_id, extensions)
    regime_label = _regime_for_pair(run.pair_id, metrics, extensions)
    vol_regime = _vol_regime_for_pair(run.pair_id, extensions)
    direction = run.signal.directional_bias if run.signal else extensions.get("directional_bias_candidate")
    confidence = run.signal.confidence if run.signal else None
    run_time = run.run_timestamp or run.completed_at or run.created_at
    return PairStateSnapshot(
        snapshot_id=f"pair-state-{uuid4().hex[:12]}",
        pair_id=run.pair_id,
        source_run_id=run.run_id,
        snapshot_timestamp=_now_utc().isoformat(),
        run_timestamp=_iso_or_none(run_time),
        as_of_date=(run.feature_snapshot.as_of_date if run.feature_snapshot else _now_utc().strftime("%Y-%m-%d")),
        status=run.status,
        staleness_status=_staleness_status(run_time),
        theme=run.theme,
        relationship=run.relationship,
        signal_zscore=_safe_float(metrics.get("signal_zscore")),
        signal_velocity_5d=_safe_float(metrics.get("signal_velocity_5d")),
        corr_30d=_safe_float(metrics.get("corr_30d")),
        corr_90d=_safe_float(metrics.get("corr_90d")),
        ratio=_safe_float(metrics.get("ratio")),
        spread_value=_safe_float(metrics.get("spread_value")),
        directional_bias=direction,
        confidence=confidence,
        regime_label=regime_label,
        vol_regime=vol_regime,
        driver_label=primary_label,
        driver_value=primary_value,
        secondary_driver_label=secondary_label,
        secondary_driver_value=secondary_value,
        attention_score=_attention_score(metrics, run.warning_count, primary_value),
        warning_count=run.warning_count,
        pair_extensions=extensions or {},
        source_freshness=run.feature_snapshot.source_freshness_json if run.feature_snapshot else None,
    )


def get_or_create_pair_state_snapshot(db: Session, run: PairRun) -> PairStateSnapshotModel:
    existing = (
        db.query(PairStateSnapshotModel)
        .filter(PairStateSnapshotModel.source_run_id == run.run_id, PairStateSnapshotModel.pair_id == run.pair_id)
        .one_or_none()
    )
    if existing is not None:
        return existing
    state = _pair_state_from_run(run)
    model = PairStateSnapshotModel(
        snapshot_id=state.snapshot_id,
        pair_id=state.pair_id,
        source_run_id=state.source_run_id,
        source_pair_run_id=run.id,
        snapshot_timestamp=datetime.fromisoformat(state.snapshot_timestamp),
        run_timestamp=datetime.fromisoformat(state.run_timestamp) if state.run_timestamp else None,
        as_of_date=state.as_of_date,
        status=state.status,
        staleness_status=state.staleness_status,
        theme=state.theme,
        relationship=state.relationship,
        signal_zscore=state.signal_zscore,
        signal_velocity_5d=state.signal_velocity_5d,
        corr_30d=state.corr_30d,
        corr_90d=state.corr_90d,
        ratio=state.ratio,
        spread_value=state.spread_value,
        directional_bias=state.directional_bias,
        confidence=state.confidence,
        regime_label=state.regime_label,
        vol_regime=state.vol_regime,
        driver_label=state.driver_label,
        driver_value=state.driver_value,
        secondary_driver_label=state.secondary_driver_label,
        secondary_driver_value=state.secondary_driver_value,
        attention_score=state.attention_score,
        warning_count=state.warning_count,
        state_payload_json=state.model_dump(),
        pair_extensions_json=state.pair_extensions,
        source_freshness_json=state.source_freshness,
    )
    db.add(model)
    db.flush()
    return model


def _trajectory_region_label(pair_id: str, x_value: float | None, y_value: float | None, state: PairStateSnapshot) -> str | None:
    if pair_id == "ZB_GC":
        if (x_value or 0.0) > 0.5 and (y_value or 0.0) > 1.5:
            return "gold-over-duration stress zone"
        if abs(x_value or 0.0) < 0.5:
            return "balanced haven zone"
        return "transition zone"
    if pair_id == "BZ_GC":
        if (y_value or 0.0) < 50 and (x_value or 0.0) > 0:
            return "defensive slowdown zone"
        if (y_value or 0.0) > 50 and (x_value or 0.0) < 0:
            return "growth-heat zone"
        return "inflation transition zone"
    if pair_id == "CHF_EUR":
        if (x_value or 0.0) > 0.75:
            return "fragmentation zone"
        if abs(x_value or 0.0) < 0.25 and abs(y_value or 0.0) < 0.25:
            return "compression zone"
        return "divergence transition zone"
    if abs(y_value or 0.0) > 0.05:
        return "intervention-sensitive zone"
    if abs(x_value or 0.0) < 0.5:
        return "haven balance zone"
    return "haven divergence zone"


def _motion_label(points: list[PairTrajectoryPoint], x_value: float | None, y_value: float | None) -> str | None:
    if not points:
        return None
    previous = points[-1]
    dx = (x_value or 0.0) - (previous.x_value or 0.0)
    dy = (y_value or 0.0) - (previous.y_value or 0.0)
    if abs(dx) < 0.1 and abs(dy) < 0.1:
        return "compressing"
    if abs(dx) > 0.35 and abs(dy) > 0.2:
        return "accelerating"
    if abs(dx) > 0.35:
        return "displacing"
    return "drifting"


def _build_change_summary(
    latest: PairRun,
    previous: PairRun | None,
    pair_state: PairStateSnapshot,
    coupling_delta: float | None = None,
) -> ChangeSummary:
    latest_metrics = latest.feature_snapshot.core_metrics_json if latest.feature_snapshot else {}
    previous_metrics = previous.feature_snapshot.core_metrics_json if previous and previous.feature_snapshot else {}
    latest_extensions = latest.feature_snapshot.pair_extensions_json if latest.feature_snapshot else {}
    previous_extensions = previous.feature_snapshot.pair_extensions_json if previous and previous.feature_snapshot else {}
    z_change = (_safe_float(latest_metrics.get("signal_zscore")) or 0.0) - (_safe_float(previous_metrics.get("signal_zscore")) or 0.0)
    vel_change = (_safe_float(latest_metrics.get("signal_velocity_5d")) or 0.0) - (_safe_float(previous_metrics.get("signal_velocity_5d")) or 0.0)
    corr_change = (_safe_float(latest_metrics.get("corr_90d")) or 0.0) - (_safe_float(previous_metrics.get("corr_90d")) or 0.0)
    driver_key = None
    driver_change = None
    for key, _label in PAIR_DRIVER_KEYS.get(latest.pair_id, []):
        new_value = _safe_float(latest_extensions.get(key))
        old_value = _safe_float(previous_extensions.get(key))
        if new_value is None and old_value is None:
            continue
        delta = (new_value or 0.0) - (old_value or 0.0)
        if driver_change is None or abs(delta) > abs(driver_change):
            driver_change = delta
            driver_key = key
    fragments = [f"z-score Δ {z_change:+.2f}", f"velocity Δ {vel_change:+.2f}", f"corr Δ {corr_change:+.2f}"]
    if coupling_delta is not None:
        fragments.append(f"coupling Δ {coupling_delta:+.2f}")
    description = ", ".join(fragments) if previous is not None else "First persisted run for this pair in the platform observatory."
    return ChangeSummary(
        pair_id=latest.pair_id,
        title=f"{latest.pair_id} state change",
        description=description,
        changed_at=_iso_or_none(latest.run_timestamp or latest.completed_at or latest.created_at),
        absolute_zscore_change=round(abs(z_change), 4),
        velocity_change=round(vel_change, 4),
        corr_90d_change=round(corr_change, 4),
        driver_change_key=driver_key,
        driver_change_value=round(driver_change, 4) if driver_change is not None else None,
        attention_score=pair_state.attention_score,
    )


def build_pair_trajectory(db: Session, pair_id: str, *, limit: int = 24) -> list[PairTrajectoryPoint]:
    runs = [run for run in history_for_pair(db, pair_id, limit=limit) if run.feature_snapshot is not None]
    points: list[PairTrajectoryPoint] = []
    ordered = list(reversed(runs))
    axis_config = PAIR_TRAJECTORY_AXES[pair_id]
    for idx, run in enumerate(ordered):
        metrics = run.feature_snapshot.core_metrics_json or {}
        extensions = run.feature_snapshot.pair_extensions_json or {}
        state = _pair_state_from_run(run)
        x_value = _safe_float(metrics.get(axis_config["x"])) if axis_config["x"] in metrics else _safe_float(extensions.get(axis_config["x"]))
        y_value = _safe_float(metrics.get(axis_config["y"])) if axis_config["y"] in metrics else _safe_float(extensions.get(axis_config["y"]))
        points.append(
            PairTrajectoryPoint(
                pair_id=run.pair_id,
                run_id=run.run_id,
                run_timestamp=_iso_or_none(run.run_timestamp or run.completed_at or run.created_at) or "",
                x_value=x_value,
                y_value=y_value,
                color_value=float(idx + 1),
                regime_label=state.regime_label,
                region_label=_trajectory_region_label(pair_id, x_value, y_value, state),
                motion_label=_motion_label(points, x_value, y_value),
                directional_bias=state.directional_bias,
                confidence=state.confidence,
                status=run.status,
                x_label=axis_config["x_label"],
                y_label=axis_config["y_label"],
                current=idx == len(ordered) - 1,
            )
        )
    return points


def _compute_coupling(pair_states: list[PairStateSnapshot], previous: CouplingSnapshot | None = None) -> CouplingSnapshot:
    pair_ids = [state.pair_id for state in pair_states]
    vectors = [_vector_from_state(state) for state in pair_states]
    matrix: list[list[float | None]] = []
    off_diag: list[float] = []
    for i, left in enumerate(vectors):
        row: list[float | None] = []
        for j, right in enumerate(vectors):
            if i == j:
                row.append(1.0)
                continue
            distance = sqrt(sum((left[k] - right[k]) ** 2 for k in range(len(left))))
            similarity = max(0.0, 1.0 - min(distance / 6.0, 1.0))
            row.append(round(similarity, 4))
            off_diag.append(similarity)
        matrix.append(row)
    coherence = _average(off_diag) if off_diag else None
    fragmentation = None if coherence is None else 1.0 - coherence
    coherence_delta = None
    fragmentation_delta = None
    if previous is not None and previous.coherence_score is not None and coherence is not None:
        coherence_delta = round(coherence - previous.coherence_score, 4)
    if previous is not None and previous.fragmentation_score is not None and fragmentation is not None:
        fragmentation_delta = round(fragmentation - previous.fragmentation_score, 4)
    return CouplingSnapshot(
        snapshot_timestamp=_now_utc().isoformat(),
        pair_ids=pair_ids,
        matrix_metric="state_similarity",
        matrix=matrix,
        coherence_score=round(coherence, 4) if coherence is not None else None,
        fragmentation_score=round(fragmentation, 4) if fragmentation is not None else None,
        coherence_delta=coherence_delta,
        fragmentation_delta=fragmentation_delta,
    )


def _dominant_regime(pair_states: list[PairStateSnapshot]) -> str | None:
    if not pair_states:
        return None
    counts: dict[str, int] = {}
    for state in pair_states:
        if state.regime_label is None:
            continue
        counts[state.regime_label] = counts.get(state.regime_label, 0) + 1
    if not counts:
        return None
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))[0][0]


def _stress_score(pair_states: list[PairStateSnapshot]) -> float | None:
    values = [abs(state.signal_zscore or 0.0) + abs(state.signal_velocity_5d or 0.0) for state in pair_states]
    return round(_average(values), 4) if values else None


def _state_dispersion(pair_states: list[PairStateSnapshot]) -> float | None:
    if len(pair_states) < 2:
        return 0.0 if pair_states else None
    distances: list[float] = []
    vectors = [_vector_from_state(state) for state in pair_states]
    for idx in range(len(vectors)):
        for jdx in range(idx + 1, len(vectors)):
            left = vectors[idx]
            right = vectors[jdx]
            distances.append(sqrt(sum((left[k] - right[k]) ** 2 for k in range(len(left)))))
    return round(_average(distances), 4) if distances else None


def _attention_flags(
    pair_states: list[PairStateSnapshot],
    change_summaries: list[ChangeSummary],
    coupling: CouplingSnapshot,
) -> list[AttentionFlag]:
    flags: list[AttentionFlag] = []
    top_state = max(pair_states, key=lambda item: item.attention_score, default=None)
    if top_state:
        flags.append(
            AttentionFlag(
                pair_id=top_state.pair_id,
                severity="high" if top_state.attention_score >= 4.5 else "medium",
                title=f"{top_state.pair_id} requires attention",
                reason=f"Attention score {top_state.attention_score:.2f} driven by {top_state.regime_label or 'state transition'}",
                metric_key="attention_score",
                metric_value=top_state.attention_score,
            )
        )
    if coupling.fragmentation_score is not None and coupling.fragmentation_score > 0.45:
        flags.append(
            AttentionFlag(
                pair_id="DESK",
                severity="high",
                title="Desk fragmentation elevated",
                reason="Cross-pair state similarity has broken down enough to warrant a top-down coherence check.",
                metric_key="fragmentation_score",
                metric_value=coupling.fragmentation_score,
                pair_ids=[state.pair_id for state in pair_states],
            )
        )
    for state in pair_states:
        if state.staleness_status == "stale":
            flags.append(
                AttentionFlag(
                    pair_id=state.pair_id,
                    severity="medium",
                    title=f"{state.pair_id} snapshot is stale",
                    reason="Latest persisted usable run is older than the observatory freshness threshold.",
                    metric_key="staleness",
                    metric_value=None,
                )
            )
    if change_summaries:
        mover = max(change_summaries, key=lambda item: item.absolute_zscore_change or 0.0)
        flags.append(
            AttentionFlag(
                pair_id=mover.pair_id,
                severity="medium",
                title=f"{mover.pair_id} changed most",
                reason=mover.description,
                metric_key="absolute_zscore_change",
                metric_value=mover.absolute_zscore_change,
            )
        )
    return flags[:5]


def _desk_history(db: Session, *, limit: int = 12) -> list[DeskHistoryPoint]:
    rows = (
        db.query(DeskStateSnapshotModel)
        .order_by(DeskStateSnapshotModel.snapshot_timestamp.desc(), DeskStateSnapshotModel.id.desc())
        .limit(limit)
        .all()
    )
    history = [
        DeskHistoryPoint(
            snapshot_timestamp=row.snapshot_timestamp.isoformat(),
            coherence_score=row.coherence_score,
            fragmentation_score=row.fragmentation_score,
            stress_score=row.stress_score,
            dominant_regime=row.dominant_regime,
        )
        for row in reversed(rows)
    ]
    return history


def _latest_refresh_job(db: Session) -> IntelligenceRefreshJob | None:
    return (
        db.query(IntelligenceRefreshJob)
        .order_by(IntelligenceRefreshJob.started_at.desc(), IntelligenceRefreshJob.id.desc())
        .first()
    )


def _desk_state_from_models(
    db: Session,
    pair_states: list[PairStateSnapshot],
    latest_runs: list[PairRun],
    *,
    desk_model: DeskStateSnapshotModel,
    coupling: CouplingSnapshot,
    refresh_job: IntelligenceRefreshJob | None,
    change_summaries: list[ChangeSummary],
) -> DeskStateSnapshot:
    stale_pair_ids = [state.pair_id for state in pair_states if state.staleness_status == "stale"]
    latest_common = min([run.run_timestamp for run in latest_runs if run.run_timestamp is not None], default=None)
    return DeskStateSnapshot(
        snapshot_id=desk_model.snapshot_id,
        snapshot_timestamp=desk_model.snapshot_timestamp.isoformat(),
        latest_common_run_timestamp=_iso_or_none(latest_common or desk_model.latest_common_run_timestamp),
        dominant_regime=desk_model.dominant_regime,
        coherence_score=desk_model.coherence_score,
        fragmentation_score=desk_model.fragmentation_score,
        stress_score=desk_model.stress_score,
        state_dispersion=desk_model.state_dispersion,
        attention_pair_id=desk_model.attention_pair_id,
        coverage_ratio=desk_model.coverage_ratio,
        stale_pair_ids=stale_pair_ids,
        freshness_status=_freshness_status(latest_common, refresh_job),
        degraded=refresh_job.status == "degraded" if refresh_job is not None else False,
        refresh_status=_refresh_status_from_job(refresh_job),
        pair_states=pair_states,
        coupling=coupling,
        change_summaries=change_summaries,
        attention_flags=_attention_flags(pair_states, change_summaries, coupling),
        desk_history=_desk_history(db),
    )


def refresh_intelligence_snapshots(db: Session) -> IntelligenceOverviewResponse:
    latest_runs: list[PairRun] = []
    pair_states: list[PairStateSnapshot] = []
    change_summaries: list[ChangeSummary] = []

    previous_coupling_model = (
        db.query(CouplingSnapshotModel)
        .order_by(CouplingSnapshotModel.snapshot_timestamp.desc(), CouplingSnapshotModel.id.desc())
        .first()
    )
    previous_coupling = CouplingSnapshot(**previous_coupling_model.payload_json) if previous_coupling_model else None

    for pair_id in PAIR_ORDER:
        run = _latest_usable_run_for_pair(db, pair_id)
        if run is None:
            continue
        latest_runs.append(run)
        state_model = get_or_create_pair_state_snapshot(db, run)
        pair_state = _serialize_pair_state_model(state_model)
        pair_states.append(pair_state)
        previous_candidates = [item for item in history_for_pair(db, pair_id, limit=6) if item.run_id != run.run_id and item.feature_snapshot is not None]
        previous_run = previous_candidates[0] if previous_candidates else None
        change_summaries.append(_build_change_summary(run, previous_run, pair_state))

    pair_states.sort(key=lambda item: PAIR_ORDER.index(item.pair_id) if item.pair_id in PAIR_ORDER else 999)
    coupling = _compute_coupling(pair_states, previous=previous_coupling)
    change_summaries.sort(key=lambda item: item.absolute_zscore_change or 0.0, reverse=True)
    attention_pair = max(pair_states, key=lambda item: item.attention_score, default=None)
    latest_common = min([run.run_timestamp for run in latest_runs if run.run_timestamp is not None], default=None)
    coverage_ratio = round(len(pair_states) / len(PAIR_ORDER), 4) if PAIR_ORDER else 0.0
    snapshot_key = "|".join(sorted(run.run_id for run in latest_runs)) if latest_runs else "empty"

    refresh_job = _latest_refresh_job(db)
    desk_model = DeskStateSnapshotModel(
        snapshot_id=f"desk-state-{uuid4().hex[:12]}",
        snapshot_key=f"{snapshot_key}|{uuid4().hex[:8]}",
        snapshot_timestamp=_now_utc(),
        latest_common_run_timestamp=latest_common,
        dominant_regime=_dominant_regime(pair_states),
        coherence_score=coupling.coherence_score,
        fragmentation_score=coupling.fragmentation_score,
        stress_score=_stress_score(pair_states),
        state_dispersion=_state_dispersion(pair_states),
        attention_pair_id=attention_pair.pair_id if attention_pair else None,
        coverage_ratio=coverage_ratio,
        stale_pair_ids_json=[state.pair_id for state in pair_states if state.staleness_status == "stale"],
        summary_json={
            "refresh_status": _refresh_status_from_job(refresh_job).model_dump() if refresh_job else None,
        },
    )
    db.add(desk_model)
    db.flush()
    db.add(
        CouplingSnapshotModel(
            desk_state_snapshot_id=desk_model.id,
            snapshot_timestamp=_now_utc(),
            matrix_metric=coupling.matrix_metric,
            coherence_score=coupling.coherence_score,
            fragmentation_score=coupling.fragmentation_score,
            matrix_json={"pair_ids": coupling.pair_ids, "matrix": coupling.matrix},
            payload_json=coupling.model_dump(),
        )
    )
    db.commit()
    db.refresh(desk_model)

    desk = _desk_state_from_models(
        db,
        pair_states,
        latest_runs,
        desk_model=desk_model,
        coupling=coupling,
        refresh_job=refresh_job,
        change_summaries=change_summaries,
    )
    trajectories = {pair_id: build_pair_trajectory(db, pair_id) for pair_id in PAIR_ORDER}
    return IntelligenceOverviewResponse(desk=desk, trajectories=trajectories)


def _run_refresh_cycle(
    db: Session,
    *,
    trigger_source: str,
    requested_by_user_id: int | None = None,
) -> IntelligenceRefreshJob:
    job = IntelligenceRefreshJob(
        refresh_id=f"refresh-{uuid4().hex[:12]}",
        trigger_source=trigger_source,
        status="running",
        requested_by_user_id=requested_by_user_id,
        started_at=_now_utc(),
        total_pairs=len(PAIR_ORDER),
        pair_results_json={},
        warnings_json=[],
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    pair_results: dict[str, Any] = {}
    warnings: list[str] = []
    try:
        for pair_id in PAIR_ORDER:
            run = execute_pair_run(
                db,
                pair_id,
                requested_by_user_id=requested_by_user_id,
                trigger_source=trigger_source,
                persist_journal=False,
            )
            pair_results[pair_id] = {
                "run_id": run.run_id,
                "status": run.status,
                "warning_count": run.warning_count,
                "error_code": run.error_code,
                "error_message": run.error_message,
            }
            if run.status == "success":
                job.success_count += 1
            elif run.status == "degraded_success":
                job.degraded_count += 1
                warnings.append(f"{pair_id} completed in degraded-success mode")
            else:
                job.failed_count += 1
                warnings.append(f"{pair_id} refresh failed: {run.error_code or 'PAIR_RUN_FAILED'}")
        job.status = "success" if job.failed_count == 0 else ("degraded" if (job.success_count + job.degraded_count) > 0 else "error")
        job.warning_count = len(warnings)
        job.completed_at = _now_utc()
        job.pair_results_json = pair_results
        job.warnings_json = warnings
        if job.status in {"success", "degraded"}:
            job.last_successful_snapshot_at = job.completed_at
        db.add(job)
        db.commit()
        db.refresh(job)
    except Exception as exc:
        job.status = "error"
        job.completed_at = _now_utc()
        job.error_message = str(exc)
        job.pair_results_json = pair_results
        job.warnings_json = warnings
        db.add(job)
        db.commit()
        db.refresh(job)
    return job


def trigger_intelligence_refresh(
    db: Session,
    *,
    trigger_source: str = "intelligence_manual_refresh",
    requested_by_user_id: int | None = None,
) -> IntelligenceOverviewResponse:
    with _refresh_lock:
        _run_refresh_cycle(db, trigger_source=trigger_source, requested_by_user_id=requested_by_user_id)
        return refresh_intelligence_snapshots(db)


def latest_intelligence_overview(db: Session) -> IntelligenceOverviewResponse:
    return refresh_intelligence_snapshots(db)


def trajectory_for_pair(db: Session, pair_id: str, *, limit: int = 24) -> list[PairTrajectoryPoint]:
    canonical = normalize_pair_id(pair_id)
    return build_pair_trajectory(db, canonical, limit=limit)


def auto_refresh_loop() -> None:
    interval_seconds = max(300, app_settings.intelligence_refresh_interval_seconds)
    while True:
        try:
            db = SessionLocal()
            try:
                trigger_intelligence_refresh(db, trigger_source="intelligence_background")
            finally:
                db.close()
        except Exception:
            pass
        sleep(interval_seconds)


def ensure_background_refresh_started() -> None:
    global _background_thread_started
    if _background_thread_started or not app_settings.enable_intelligence_auto_refresh:
        return
    thread = Thread(target=auto_refresh_loop, daemon=True, name="intelligence-auto-refresh")
    thread.start()
    _background_thread_started = True
