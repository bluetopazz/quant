from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.app.core.dependencies import get_db
from backend.app.services.llm_service import llm_status


router = APIRouter(tags=["health"])


@router.get("/health")
def health(db: Session = Depends(get_db)) -> dict[str, object]:
    db.execute(text("SELECT 1"))
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "llm": llm_status(),
    }
