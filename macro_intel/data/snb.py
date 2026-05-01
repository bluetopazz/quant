from __future__ import annotations

import pandas as pd
import requests


SNB_SIGHT_DEPOSITS_URL = "https://data.snb.ch/api/cube/snbgwdchfsgw/data/json/en"
SNB_TARGET_LABEL = "Total sight deposits in Swiss francs at the SNB"


def fetch_snb_sight_deposits(
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
    *,
    timeout_seconds: int = 30,
) -> pd.DataFrame:
    """Fetch SNB total sight deposits and return a single-column DataFrame."""

    params = {
        "dimSel": "D0(GI,UEB,TG)",
        "fromDate": start_date.strftime("%Y-%m-%d"),
        "toDate": end_date.strftime("%Y-%m-%d"),
    }

    response = requests.get(SNB_SIGHT_DEPOSITS_URL, params=params, timeout=timeout_seconds)
    response.raise_for_status()
    payload = response.json()

    if "timeseries" not in payload:
        raise RuntimeError("SNB response missing 'timeseries'")

    target = None
    for timeseries in payload["timeseries"]:
        try:
            label = timeseries["header"][0]["dimItem"]
        except Exception:
            continue
        if label == SNB_TARGET_LABEL:
            target = timeseries
            break

    if target is None:
        raise RuntimeError(f"Could not find SNB target series: {SNB_TARGET_LABEL}")

    values = target.get("values", [])
    if not values:
        raise RuntimeError("SNB target series contained no values")

    frame = pd.DataFrame(values)
    if "date" not in frame.columns or "value" not in frame.columns:
        raise RuntimeError(f"Unexpected SNB schema: {list(frame.columns)}")

    frame["date"] = pd.to_datetime(frame["date"])
    frame["value"] = pd.to_numeric(frame["value"], errors="coerce")
    frame = frame.set_index("date").rename(columns={"value": "SNB_Sight_Deposits"}).sort_index()
    return frame
