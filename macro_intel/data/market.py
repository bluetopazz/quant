from __future__ import annotations

import random
import time

import pandas as pd
import yfinance as yf


def _extract_close_frame(raw: pd.DataFrame, tickers: list[str] | tuple[str, ...]) -> pd.DataFrame:
    if raw is None or raw.empty:
        return pd.DataFrame()

    frame = raw.copy()
    if isinstance(frame.columns, pd.MultiIndex):
        level0 = set(frame.columns.get_level_values(0))
        if "Close" in level0:
            frame = frame.xs("Close", level=0, axis=1)
        elif "Adj Close" in level0:
            frame = frame.xs("Adj Close", level=0, axis=1)
    elif len(tickers) == 1:
        candidate_name = tickers[0]
        if "Close" in frame.columns:
            frame = frame[["Close"]].rename(columns={"Close": candidate_name})
        elif "Adj Close" in frame.columns:
            frame = frame[["Adj Close"]].rename(columns={"Adj Close": candidate_name})

    frame.index = pd.to_datetime(frame.index).tz_localize(None)
    frame = frame.sort_index()
    keep = [ticker for ticker in tickers if ticker in frame.columns]
    return frame[keep] if keep else pd.DataFrame(index=frame.index)


def fetch_yf_batch(
    tickers: list[str] | tuple[str, ...],
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
) -> pd.DataFrame:
    raw = yf.download(
        list(tickers),
        start=start_date,
        end=end_date + pd.Timedelta(days=1),
        auto_adjust=True,
        progress=False,
        group_by="column",
        threads=False,
    )
    return _extract_close_frame(raw, tickers)


def fetch_yf_single_ticker(
    ticker: str,
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
    *,
    max_retries: int = 5,
    sleep_seconds: int = 8,
    auto_adjust: bool = True,
) -> pd.Series:
    """Fetch one ticker robustly using the pattern already proven in backtest.ipynb."""

    last_error: Exception | None = None
    for attempt in range(1, max_retries + 1):
        try:
            data = yf.Ticker(ticker).history(
                start=start_date,
                end=end_date + pd.Timedelta(days=1),
                interval="1d",
                auto_adjust=auto_adjust,
                actions=False,
                repair=True,
            )
            if data is None or data.empty:
                raise RuntimeError("empty yfinance response")
            if "Close" not in data.columns:
                raise RuntimeError(f"missing Close column for {ticker}")
            series = data["Close"].copy()
            series.index = pd.to_datetime(series.index).tz_localize(None)
            series.name = ticker
            if series.dropna().empty:
                raise RuntimeError(f"all values NaN for {ticker}")
            return series
        except Exception as exc:  # pragma: no cover - network behavior
            last_error = exc
            if attempt < max_retries:
                message = str(exc).lower()
                if "too many requests" in message or "rate limited" in message:
                    wait_seconds = sleep_seconds * (attempt + 1) * 2 + random.uniform(0, 2.0)
                else:
                    wait_seconds = sleep_seconds * attempt + random.uniform(0, 1.5)
                time.sleep(wait_seconds)
    raise RuntimeError(f"{ticker} failed after {max_retries} attempts: {last_error}")


def fetch_yfinance_prices(
    tickers: list[str] | tuple[str, ...],
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
    *,
    pause_between_tickers_seconds: float = 2.0,
) -> tuple[pd.DataFrame, list[tuple[str, str]]]:
    """Fetch tickers one by one and combine them into a single DataFrame."""

    try:
        batch = fetch_yf_batch(tickers, start_date, end_date)
        if not batch.empty:
            missing_from_batch = [ticker for ticker in tickers if ticker not in batch.columns or batch[ticker].dropna().empty]
            if not missing_from_batch:
                return batch, []
        else:
            missing_from_batch = list(tickers)
    except Exception as exc:  # pragma: no cover - network behavior
        batch = pd.DataFrame()
        missing_from_batch = list(tickers)
        batch_error = str(exc)
    else:
        batch_error = ""

    series_list: list[pd.Series] = []
    failures: list[tuple[str, str]] = []

    for ticker in missing_from_batch:
        try:
            series = fetch_yf_single_ticker(ticker, start_date, end_date)
            series_list.append(series)
        except Exception as exc:  # pragma: no cover - network behavior
            failures.append((ticker, str(exc)))
        if pause_between_tickers_seconds > 0:
            time.sleep(pause_between_tickers_seconds + random.uniform(0, 0.75))

    if not series_list and batch.empty:
        if batch_error:
            failures.insert(0, ("batch_download", batch_error))
        return pd.DataFrame(), failures

    fallback = pd.concat(series_list, axis=1).sort_index() if series_list else pd.DataFrame()
    if batch.empty:
        return fallback, failures

    combined = pd.concat([batch, fallback], axis=1)
    combined = combined.loc[:, ~combined.columns.duplicated(keep="first")].sort_index()
    return combined, failures
