from __future__ import annotations

from backend.app.db.models import PairRun


def latest_charts(run: PairRun | None) -> dict:
    if run is None or run.charts is None:
        return {}
    return run.charts
