from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from backend.app.core.config import settings as app_settings
from backend.app.db.models import JournalEntry, PairRun
from backend.app.services.pair_runner import normalize_pair_id
from macro_intel import PAIR_REGISTRY, get_pair_config
from macro_intel.journal import append_pair_journal, read_all_pair_journals, read_journal


def _frame_to_records(frame) -> list[dict[str, Any]]:
    records = []
    if frame.empty:
        return records
    for row in frame.to_dict(orient="records"):
        normalized = {}
        for key, value in row.items():
            if hasattr(value, "isoformat"):
                normalized[key] = value.isoformat()
            elif hasattr(value, "item"):
                try:
                    normalized[key] = value.item()
                except Exception:
                    normalized[key] = value
            else:
                normalized[key] = value
        records.append(normalized)
    return records


def _serialize_entry(entry: JournalEntry) -> dict[str, Any]:
    return {
        "id": entry.id,
        "pair_id": entry.pair_id,
        "run_id": entry.run_id,
        "appended_at": entry.created_at.isoformat() if entry.created_at else None,
        "csv_path": entry.csv_path,
        "payload": entry.payload_json,
    }


def get_pair_journal_history(db: Session, pair_id: str, *, limit: int = 20) -> list[dict[str, Any]]:
    canonical = normalize_pair_id(pair_id)
    records = (
        db.query(JournalEntry)
        .filter(JournalEntry.pair_id == canonical)
        .order_by(JournalEntry.created_at.desc(), JournalEntry.id.desc())
        .limit(limit)
        .all()
    )
    if records:
        return [_serialize_entry(record) for record in records]

    path = get_pair_config(canonical).journal_file
    frame = read_journal(path, parse_dates=["Date"]).tail(limit)
    return [
        {
            "id": None,
            "pair_id": row.get("Pair", canonical),
            "run_id": None,
            "appended_at": None,
            "csv_path": path,
            "payload": row,
        }
        for row in _frame_to_records(frame.iloc[::-1].reset_index(drop=True))
    ]


def get_all_journal_history(db: Session, *, limit: int = 50) -> list[dict[str, Any]]:
    records = db.query(JournalEntry).order_by(JournalEntry.created_at.desc(), JournalEntry.id.desc()).limit(limit).all()
    if records:
        return [_serialize_entry(record) for record in records]

    paths = [config.journal_file for config in PAIR_REGISTRY.values()]
    frame = read_all_pair_journals(paths).tail(limit)
    return [
        {
            "id": None,
            "pair_id": row.get("Pair", "UNKNOWN"),
            "run_id": None,
            "appended_at": None,
            "csv_path": row.get("Source_File"),
            "payload": row,
        }
        for row in _frame_to_records(frame.iloc[::-1].reset_index(drop=True))
    ]


def append_run_to_journal(db: Session, pair_id: str, run_id: str) -> JournalEntry:
    canonical = normalize_pair_id(pair_id)
    run = db.query(PairRun).filter(PairRun.run_id == run_id, PairRun.pair_id == canonical).one_or_none()
    if run is None:
        raise ValueError(f"Run {run_id} was not found for {canonical}")
    if run.status not in {"success", "degraded_success"}:
        raise ValueError("Only successful or degraded-success runs can be journaled")
    if not run.journal_preview_payload:
        raise ValueError("Run does not contain a journal preview payload")

    existing = db.query(JournalEntry).filter(JournalEntry.run_id == run_id, JournalEntry.pair_id == canonical).one_or_none()
    if existing is not None:
        return existing

    csv_path = None
    if app_settings.enable_csv_journaling:
        csv_path = append_pair_journal(canonical, run.journal_preview_payload)

    entry = JournalEntry(
        pair_run_id=run.id,
        pair_id=canonical,
        run_id=run.run_id,
        journal_schema_version=run.journal_schema_version or "csv_legacy_v1",
        journal_mode=run.journal_preview_mode or "csv_legacy_compatible",
        payload_json=run.journal_preview_payload,
        csv_path=csv_path,
        created_at=datetime.utcnow(),
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry
