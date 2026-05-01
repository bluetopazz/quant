from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.dependencies import get_current_user, get_db
from backend.app.db.models import User
from backend.app.schemas.pair import PairCardResponse, PairDetailResponse
from backend.app.schemas.run import ChartPayload, PairRunRequest, PairRunResult, PairRunSummary
from backend.app.services.journal_service import append_run_to_journal
from backend.app.services.pair_runner import (
    build_pair_summary,
    execute_pair_run,
    history_for_pair,
    latest_run_for_pair,
    normalize_pair_id,
    serialize_pair_run,
)
from macro_intel import PAIR_REGISTRY, get_pair_config


router = APIRouter(prefix="/pairs", tags=["pairs"])


@router.get("", response_model=list[PairCardResponse])
def list_pairs(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[PairCardResponse]:
    cards: list[PairCardResponse] = []
    for pair_id, config in PAIR_REGISTRY.items():
        latest = latest_run_for_pair(db, pair_id)
        cards.append(
            PairCardResponse(
                pair_id=pair_id,
                notebook_name=config.notebook_name,
                theme=config.theme,
                relationship=config.relationship,
                prompt_style=config.prompt_style,
                parser_style=config.parser_style,
                signal_shape=config.signal_shape,
                latest_run=PairRunSummary(**build_pair_summary(latest)) if latest else None,
            )
        )
    return cards


@router.get("/{pair_id}", response_model=PairDetailResponse)
def get_pair(
    pair_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> PairDetailResponse:
    try:
        canonical = normalize_pair_id(pair_id)
        config = get_pair_config(canonical)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    latest = latest_run_for_pair(db, canonical)
    return PairDetailResponse(
        pair_id=config.pair_id,
        notebook_name=config.notebook_name,
        theme=config.theme,
        relationship=config.relationship,
        yfinance_tickers=list(config.yfinance_tickers),
        fred_series_ids=list(config.fred_series_ids),
        prompt_style=config.prompt_style,
        parser_style=config.parser_style,
        signal_shape=config.signal_shape,
        external_apis=list(config.external_apis),
        feature_flags=list(config.feature_flags),
        special_handling_rules=list(config.special_handling_rules),
        chart_metadata=dict(config.chart_metadata),
        latest_run=PairRunSummary(**build_pair_summary(latest)) if latest else None,
    )


@router.post("/{pair_id}/run", response_model=PairRunResult)
def run_pair(
    pair_id: str,
    payload: PairRunRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PairRunResult:
    try:
        canonical = normalize_pair_id(pair_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    run = execute_pair_run(
        db,
        canonical,
        requested_by_user_id=current_user.id,
        trigger_source=payload.trigger_source or "ui_manual",
        persist_journal=payload.persist_journal,
    )
    return PairRunResult(**serialize_pair_run(run))


@router.get("/{pair_id}/latest", response_model=PairRunResult)
def latest_pair_run(
    pair_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> PairRunResult:
    try:
        run = latest_run_for_pair(db, pair_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    if run is None:
        raise HTTPException(status_code=404, detail="No runs recorded yet")
    return PairRunResult(**serialize_pair_run(run))


@router.get("/{pair_id}/history", response_model=list[PairRunSummary])
def pair_history(
    pair_id: str,
    limit: int = 20,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[PairRunSummary]:
    try:
        runs = history_for_pair(db, pair_id, limit=limit)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return [PairRunSummary(**build_pair_summary(run)) for run in runs]


@router.get("/{pair_id}/charts", response_model=list[ChartPayload])
def pair_charts(
    pair_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[ChartPayload]:
    try:
        run = latest_run_for_pair(db, pair_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    if run is None:
        raise HTTPException(status_code=404, detail="No runs recorded yet")
    serialized = serialize_pair_run(run)
    return [ChartPayload(**chart) for chart in serialized.get("charts", [])]


@router.post("/{pair_id}/journal", response_model=dict)
def journal_latest_run(
    pair_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> dict:
    run = latest_run_for_pair(db, pair_id)
    if run is None:
        raise HTTPException(status_code=404, detail="No runs recorded yet")
    try:
        record = append_run_to_journal(db, run.pair_id, run.run_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"id": record.id, "run_id": record.run_id, "pair_id": record.pair_id}
