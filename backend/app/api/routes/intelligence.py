from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.dependencies import get_current_user, get_db
from backend.app.db.models import User
from backend.app.schemas.intelligence import IntelligenceOverviewResponse, PairTrajectoryPoint
from backend.app.services.intelligence_service import (
    latest_intelligence_overview,
    trajectory_for_pair,
    trigger_intelligence_refresh,
)


router = APIRouter(prefix="/intelligence", tags=["intelligence"])


@router.get("", response_model=IntelligenceOverviewResponse)
def intelligence_overview(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> IntelligenceOverviewResponse:
    return latest_intelligence_overview(db)


@router.post("/refresh", response_model=IntelligenceOverviewResponse)
def refresh_intelligence(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> IntelligenceOverviewResponse:
    return trigger_intelligence_refresh(
        db,
        trigger_source="intelligence_manual_refresh",
        requested_by_user_id=current_user.id,
    )


@router.get("/pairs/{pair_id}/trajectory", response_model=list[PairTrajectoryPoint])
def pair_trajectory(
    pair_id: str,
    limit: int = 24,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[PairTrajectoryPoint]:
    try:
        return trajectory_for_pair(db, pair_id, limit=limit)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
