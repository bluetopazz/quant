from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class JournalAppendRequest(BaseModel):
    run_id: str


class JournalEntryResponse(BaseModel):
    id: int | None = None
    pair_id: str
    run_id: str | None = None
    appended_at: str | None = None
    csv_path: str | None = None
    payload: dict[str, Any]
