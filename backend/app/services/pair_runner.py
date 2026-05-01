from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from backend.app.db.models import (
    JournalEntry,
    PairRun,
    PairRunChartPayload,
    PairRunFeatureSnapshot,
    PairRunMemo,
    PairRunRiskTicket,
    PairRunSignal,
)
from macro_intel import PAIR_REGISTRY, get_pair_config
from macro_intel.config.settings import Settings
from macro_intel.contracts import PairRunResult as EnginePairRunResult
from macro_intel.engine import run_pair_analysis


def normalize_pair_id(pair_id: str) -> str:
    candidate = pair_id.replace("-", "_").upper()
    if candidate in PAIR_REGISTRY:
        return candidate
    raise KeyError(f"Unknown pair_id: {pair_id}")


def classify_error(exc: Exception) -> tuple[str, bool]:
    message = str(exc).lower()
    if "fred_api_key" in message:
        return "MACRO_DATA_UNAVAILABLE", False
    if "snb" in message:
        return "SNB_DATA_UNAVAILABLE", True
    if "llm" in message or "api/chat" in message:
        return "LLM_UNAVAILABLE", True
    if "analysis frame" in message or "market" in message or "yfinance" in message:
        return "MARKET_DATA_UNAVAILABLE", True
    return "PAIR_RUN_FAILED", False


def _iso_or_none(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


def _empty_feature_snapshot(pair_id: str) -> dict[str, Any]:
    return {
        "pair_id": pair_id,
        "as_of_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "core_metrics": {
            "signal_zscore": None,
            "signal_velocity_5d": None,
            "corr_30d": None,
            "corr_90d": None,
        },
        "pair_extensions": {},
        "normalization_mode": "unknown",
        "source_freshness": None,
    }


def build_pair_summary(run: PairRun) -> dict[str, Any]:
    return {
        "run_id": run.run_id,
        "pair_id": run.pair_id,
        "status": run.status,
        "run_timestamp": _iso_or_none(run.run_timestamp) or _iso_or_none(run.completed_at) or _iso_or_none(run.created_at),
        "warning_count": run.warning_count,
        "error_code": run.error_code,
        "error_message": run.error_message,
    }


def serialize_pair_run(run: PairRun) -> dict[str, Any]:
    feature_snapshot = (
        {
            "pair_id": run.feature_snapshot.pair_id,
            "as_of_date": run.feature_snapshot.as_of_date,
            "core_metrics": run.feature_snapshot.core_metrics_json or {},
            "pair_extensions": run.feature_snapshot.pair_extensions_json or {},
            "normalization_mode": run.feature_snapshot.normalization_mode,
            "source_freshness": run.feature_snapshot.source_freshness_json,
        }
        if run.feature_snapshot
        else _empty_feature_snapshot(run.pair_id)
    )
    charts = [chart.payload_json for chart in sorted(run.charts, key=lambda value: value.id)]
    memo = None
    if run.memo:
        memo = {
            "memo_id": run.memo.memo_id,
            "pair_id": run.memo.pair_id,
            "content": run.memo.content,
            "model_name": run.memo.model_name,
            "prompt_version": run.memo.prompt_version,
            "prompt_style": run.memo.prompt_style,
            "prompt_template_id": run.memo.prompt_template_id,
            "system_role": run.memo.system_role,
            "temperature": run.memo.temperature,
            "timeout_seconds": run.memo.timeout_seconds,
            "generated_at": _iso_or_none(run.memo.generated_at),
            "source_summary": run.memo.source_summary_json,
        }
    parsed_signal = None
    if run.signal:
        parsed_signal = {
            "pair_id": run.signal.pair_id,
            "signal_style": run.signal.signal_style,
            "parser_style": run.signal.parser_style,
            "parser_version": run.signal.parser_version,
            "parse_status": run.signal.parse_status,
            "directional_bias": run.signal.directional_bias,
            "confidence": run.signal.confidence,
            "notes": run.signal.notes,
            "target_asset": run.signal.target_asset,
            "strategy": run.signal.strategy,
            "left_leg_label": run.signal.left_leg_label,
            "right_leg_label": run.signal.right_leg_label,
            "left_strategy": run.signal.left_strategy,
            "right_strategy": run.signal.right_strategy,
            "parser_input_memo_id": run.signal.parser_input_memo_id,
            "used_llm_second_pass": run.signal.used_llm_second_pass,
            "fallback_reason": run.signal.fallback_reason,
            "raw_parser_output": run.signal.raw_parser_output,
        }
    risk_ticket = None
    if run.risk_ticket:
        risk_ticket = {
            "pair_id": run.risk_ticket.pair_id,
            "sizing_mode": run.risk_ticket.sizing_mode,
            "account_value_assumption": run.risk_ticket.account_value_assumption,
            "risk_bps_per_trade": run.risk_ticket.risk_bps_per_trade,
            "total_risk_budget_usd": run.risk_ticket.total_risk_budget_usd,
            "sizing_status": run.risk_ticket.sizing_status,
            "notes": run.risk_ticket.notes,
            "target_asset": run.risk_ticket.target_asset,
            "strategy": run.risk_ticket.strategy,
            "contracts": run.risk_ticket.contracts,
            "risk_budget_usd": run.risk_ticket.risk_budget_usd,
            "left_strategy": run.risk_ticket.left_strategy,
            "right_strategy": run.risk_ticket.right_strategy,
            "left_contracts": run.risk_ticket.left_contracts,
            "right_contracts": run.risk_ticket.right_contracts,
            "per_leg_budget_usd": run.risk_ticket.per_leg_budget_usd,
            "total_budget_usd": run.risk_ticket.total_budget_usd,
            "strategy_risk_table_version": run.risk_ticket.strategy_risk_table_version,
            "heuristic_name": run.risk_ticket.heuristic_name,
            "sizing_assumptions": run.risk_ticket.sizing_assumptions_json,
        }
    warnings = run.persistence_summary.get("warnings", []) if run.persistence_summary else []
    error = None
    if run.status == "error":
        error = {
            "error_code": run.error_code or "PAIR_RUN_FAILED",
            "stage": "pair_run",
            "message": run.error_message or "Pair run failed",
            "source": None,
            "retryable": False,
            "details": None,
        }
    return {
        "run_id": run.run_id,
        "pair_id": run.pair_id,
        "status": run.status,
        "run_timestamp": _iso_or_none(run.run_timestamp) or _iso_or_none(run.completed_at) or _iso_or_none(run.created_at),
        "feature_snapshot": feature_snapshot,
        "charts": charts,
        "analyst_memo": memo,
        "parsed_signal": parsed_signal,
        "risk_ticket": risk_ticket,
        "journal_entry_preview": {
            "pair_id": run.pair_id,
            "journal_schema_version": run.journal_schema_version,
            "journal_mode": run.journal_preview_mode,
            "preview_payload": run.journal_preview_payload or {},
        }
        if run.journal_preview_payload
        else None,
        "warnings": warnings,
        "error": error,
        "notebook_reference": run.notebook_reference,
        "theme": run.theme,
        "relationship": run.relationship,
        "pair_prompt_style": run.pair_prompt_style,
        "pair_signal_style": run.pair_signal_style,
        "requested_by_user_id": str(run.requested_by_user_id) if run.requested_by_user_id is not None else None,
        "trigger_source": run.trigger_source,
        "prompt_version": run.prompt_version,
        "engine_version": run.engine_version,
        "persistence_summary": run.persistence_summary,
    }


def latest_run_for_pair(db: Session, pair_id: str) -> PairRun | None:
    canonical = normalize_pair_id(pair_id)
    return (
        db.query(PairRun)
        .filter(PairRun.pair_id == canonical)
        .order_by(PairRun.created_at.desc(), PairRun.id.desc())
        .first()
    )


def history_for_pair(db: Session, pair_id: str, *, limit: int = 20) -> list[PairRun]:
    canonical = normalize_pair_id(pair_id)
    return (
        db.query(PairRun)
        .filter(PairRun.pair_id == canonical)
        .order_by(PairRun.created_at.desc(), PairRun.id.desc())
        .limit(limit)
        .all()
    )


def persist_engine_result(
    db: Session,
    run: PairRun,
    result: EnginePairRunResult,
) -> PairRun:
    run.run_id = result.run_id
    run.status = result.status
    run.notebook_reference = result.notebook_reference
    run.theme = result.theme
    run.relationship = result.relationship
    run.pair_prompt_style = result.pair_prompt_style
    run.pair_signal_style = result.pair_signal_style
    run.prompt_version = result.prompt_version
    run.engine_version = result.engine_version
    run.run_timestamp = datetime.fromisoformat(result.run_timestamp)
    run.completed_at = datetime.now(timezone.utc).replace(tzinfo=None)
    run.warning_count = len(result.warnings)
    run.persistence_summary = {"warnings": [warning.to_dict() for warning in result.warnings]}
    if result.journal_entry_preview:
        run.journal_schema_version = result.journal_entry_preview.journal_schema_version
        run.journal_preview_mode = result.journal_entry_preview.journal_mode
        run.journal_preview_payload = result.journal_entry_preview.preview_payload

    db.add(
        PairRunFeatureSnapshot(
            pair_run=run,
            pair_id=result.feature_snapshot.pair_id,
            as_of_date=result.feature_snapshot.as_of_date,
            normalization_mode=result.feature_snapshot.normalization_mode,
            core_metrics_json=result.feature_snapshot.core_metrics,
            pair_extensions_json=result.feature_snapshot.pair_extensions,
            source_freshness_json=result.feature_snapshot.source_freshness,
        )
    )
    if result.analyst_memo:
        db.add(
            PairRunMemo(
                pair_run=run,
                memo_id=result.analyst_memo.memo_id,
                pair_id=result.analyst_memo.pair_id,
                content=result.analyst_memo.content,
                model_name=result.analyst_memo.model_name,
                prompt_version=result.analyst_memo.prompt_version,
                prompt_style=result.analyst_memo.prompt_style,
                prompt_template_id=result.analyst_memo.prompt_template_id,
                system_role=result.analyst_memo.system_role,
                temperature=result.analyst_memo.temperature,
                timeout_seconds=result.analyst_memo.timeout_seconds,
                generated_at=datetime.fromisoformat(result.analyst_memo.generated_at) if result.analyst_memo.generated_at else None,
                source_summary_json=result.analyst_memo.source_summary,
            )
        )
    if result.parsed_signal:
        db.add(
            PairRunSignal(
                pair_run=run,
                pair_id=result.parsed_signal.pair_id,
                signal_style=result.parsed_signal.signal_style,
                parser_style=result.parsed_signal.parser_style,
                parser_version=result.parsed_signal.parser_version,
                parse_status=result.parsed_signal.parse_status,
                directional_bias=result.parsed_signal.directional_bias,
                confidence=result.parsed_signal.confidence,
                notes=result.parsed_signal.notes,
                target_asset=result.parsed_signal.target_asset,
                strategy=result.parsed_signal.strategy,
                left_leg_label=result.parsed_signal.left_leg_label,
                right_leg_label=result.parsed_signal.right_leg_label,
                left_strategy=result.parsed_signal.left_strategy,
                right_strategy=result.parsed_signal.right_strategy,
                parser_input_memo_id=result.parsed_signal.parser_input_memo_id,
                used_llm_second_pass=result.parsed_signal.used_llm_second_pass,
                fallback_reason=result.parsed_signal.fallback_reason,
                raw_parser_output=result.parsed_signal.raw_parser_output,
            )
        )
    if result.risk_ticket:
        db.add(
            PairRunRiskTicket(
                pair_run=run,
                pair_id=result.risk_ticket.pair_id,
                sizing_mode=result.risk_ticket.sizing_mode,
                account_value_assumption=result.risk_ticket.account_value_assumption,
                risk_bps_per_trade=result.risk_ticket.risk_bps_per_trade,
                total_risk_budget_usd=result.risk_ticket.total_risk_budget_usd,
                sizing_status=result.risk_ticket.sizing_status,
                notes=result.risk_ticket.notes,
                target_asset=result.risk_ticket.target_asset,
                strategy=result.risk_ticket.strategy,
                contracts=result.risk_ticket.contracts,
                risk_budget_usd=result.risk_ticket.risk_budget_usd,
                left_strategy=result.risk_ticket.left_strategy,
                right_strategy=result.risk_ticket.right_strategy,
                left_contracts=result.risk_ticket.left_contracts,
                right_contracts=result.risk_ticket.right_contracts,
                per_leg_budget_usd=result.risk_ticket.per_leg_budget_usd,
                total_budget_usd=result.risk_ticket.total_budget_usd,
                strategy_risk_table_version=result.risk_ticket.strategy_risk_table_version,
                heuristic_name=result.risk_ticket.heuristic_name,
                sizing_assumptions_json=result.risk_ticket.sizing_assumptions,
            )
        )
    for chart in result.charts:
        db.add(
            PairRunChartPayload(
                pair_run=run,
                pair_id=chart.pair_id,
                chart_id=chart.chart_id,
                family=chart.family,
                title=chart.title,
                render_kind=chart.render_kind,
                payload_json=chart.to_dict(),
            )
        )
    db.commit()
    db.refresh(run)
    return run


def execute_pair_run(
    db: Session,
    pair_id: str,
    *,
    requested_by_user_id: int | None = None,
    trigger_source: str | None = "ui_manual",
    persist_journal: bool = False,
) -> PairRun:
    canonical = normalize_pair_id(pair_id)
    pair_config = get_pair_config(canonical)
    run = PairRun(
        run_id=f"pending_{datetime.now(timezone.utc).timestamp()}",
        pair_id=canonical,
        status="running",
        notebook_reference=pair_config.notebook_name,
        theme=pair_config.theme,
        relationship=pair_config.relationship,
        pair_prompt_style=pair_config.prompt_style,
        pair_signal_style=pair_config.signal_shape,
        requested_by_user_id=requested_by_user_id,
        trigger_source=trigger_source,
        started_at=datetime.now(timezone.utc).replace(tzinfo=None),
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    try:
        result = run_pair_analysis(canonical, settings=Settings.from_env())
        run = persist_engine_result(db, run, result)
        if persist_journal:
            from backend.app.services.journal_service import append_run_to_journal

            append_run_to_journal(db, canonical, run.run_id)
            if run.persistence_summary is None:
                run.persistence_summary = {}
            run.persistence_summary["journal_persisted"] = True
            db.add(run)
            db.commit()
            db.refresh(run)
    except Exception as exc:
        error_code, _retryable = classify_error(exc)
        run.status = "error"
        run.error_code = error_code
        run.error_message = str(exc)
        run.completed_at = datetime.now(timezone.utc).replace(tzinfo=None)
        run.run_timestamp = run.completed_at
        run.persistence_summary = {"warnings": []}
        db.add(run)
        db.commit()
        db.refresh(run)
    return run
