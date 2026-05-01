from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.dependencies import get_current_user, get_db
from backend.app.db.models import User
from backend.app.schemas.journal import JournalAppendRequest, JournalEntryResponse
from backend.app.services.journal_service import append_run_to_journal, get_all_journal_history, get_pair_journal_history


router = APIRouter(prefix="/journals", tags=["journals"])


@router.get("", response_model=list[JournalEntryResponse])
def list_journals(
    limit: int = 50,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[JournalEntryResponse]:
    rows = get_all_journal_history(db, limit=limit)
    return [JournalEntryResponse(**row) for row in rows]


@router.get("/{pair_id}", response_model=list[JournalEntryResponse])
def pair_journals(
    pair_id: str,
    limit: int = 20,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[JournalEntryResponse]:
    try:
        rows = get_pair_journal_history(db, pair_id, limit=limit)
    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return [JournalEntryResponse(**row) for row in rows]


@router.post("/{pair_id}", response_model=JournalEntryResponse)
def journal_pair_run(
    pair_id: str,
    payload: JournalAppendRequest,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> JournalEntryResponse:
    try:
        record = append_run_to_journal(db, pair_id, payload.run_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return JournalEntryResponse(
        id=record.id,
        pair_id=record.pair_id,
        run_id=record.run_id,
        appended_at=record.created_at.isoformat() if record.created_at else None,
        csv_path=record.csv_path,
        payload=record.payload_json,
    )
