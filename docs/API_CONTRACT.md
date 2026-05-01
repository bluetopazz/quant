# API Contract

## Scope

This document defines the first FastAPI contract for the intelligence-platform transition.

Architecture:

```text
Next.js UI
   -> FastAPI API
   -> macro_intel engine
   -> data sources / journal CSVs / local DB / Ollama
```

The current pilot pattern is pair-centric. The UI does not compute signals or features itself.

## Core Rules

- frontend renders, triggers, and displays
- backend orchestrates
- `macro_intel` remains the business-logic engine
- notebooks remain available as the original validation interfaces

## Authentication

### `POST /auth/login`

Request:

```json
{
  "username": "operator",
  "password": "change-me"
}
```

Response:

```json
{
  "access_token": "token",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "operator",
    "role": "operator"
  }
}
```

### `POST /auth/logout`

Response:

```json
{
  "status": "ok"
}
```

### `GET /auth/me`

Response:

```json
{
  "id": 1,
  "username": "operator",
  "role": "operator"
}
```

## Health

### `GET /health`

Response shape:

```json
{
  "status": "ok",
  "timestamp": "2026-04-25T12:00:00+00:00",
  "llm": {
    "base_url": "http://127.0.0.1:11434",
    "model": "qwen2.5:7b"
  }
}
```

## Pair Metadata

### `GET /pairs`

Returns all registered pairs plus latest run summary when available.

Response shape:

```json
[
  {
    "pair_id": "CHF_EUR",
    "notebook_name": "chfeur.ipynb",
    "theme": "European_Divergence",
    "relationship": "FXF over FXE",
    "prompt_style": "single_leg",
    "signal_shape": "single_strategy",
    "latest_run": {
      "id": 4,
      "pair_id": "CHF_EUR",
      "run_timestamp": "2026-04-25T12:00:00",
      "status": "success",
      "error_message": null
    }
  }
]
```

### `GET /pairs/{pair_id}`

Returns pair metadata and configuration-facing details needed by the UI.

## Pair Runs

### `POST /pairs/{pair_id}/run`

Runs the pair through the current engine path:

1. fetch current data
2. build features
3. build chart payloads
4. generate analyst memo
5. parse signal
6. size opportunity
7. persist a `pair_runs` record

Request:

```json
{
  "persist_journal": false
}
```

Response shape:

```json
{
  "id": 7,
  "pair_id": "CHF_EUR",
  "notebook_name": "chfeur.ipynb",
  "theme": "European_Divergence",
  "relationship": "FXF over FXE",
  "run_timestamp": "2026-04-25T12:00:00+00:00",
  "status": "success",
  "model_name": "qwen2.5:7b",
  "prompt_version": "macro_intel_inline_v1",
  "latest_features": {},
  "charts": {},
  "analyst_memo": "memo text",
  "parsed_signal": {},
  "risk_ticket": {},
  "journal_entry_preview": {},
  "warnings": [],
  "error_message": null
}
```

Notes:

- if `persist_journal` is `true`, the route attempts to append the run’s journal preview immediately
- failures are stored as `pair_runs` rows with `status = "error"`

### `GET /pairs/{pair_id}/latest`

Returns the latest persisted platform run for the pair.

### `GET /pairs/{pair_id}/history`

Returns recent run summaries.

### `GET /pairs/{pair_id}/charts`

Returns chart payloads for the latest run.

### `GET /pairs/{pair_id}/features/latest`

Returns the latest feature snapshot for the pair.

## Journals

### `GET /journals`

Returns recent journal rows across all pairs, sourced from the current journal artifacts.

### `GET /journals/{pair_id}`

Returns recent journal history for one pair.

### `POST /journals/{pair_id}`

Appends a successful platform run to the existing pair journal and stores a `journal_records` row.

Request:

```json
{
  "run_id": 7
}
```

Response shape:

```json
{
  "id": 3,
  "pair_id": "CHF_EUR",
  "appended_at": "2026-04-25T12:00:00",
  "csv_path": "journal_chf_eur.csv",
  "payload": {}
}
```

## Pilot Pair

The first pilot pair for the web-platform pattern is:

- `CHF_EUR`

Why:

- it already has end-to-end runtime proof in the migrated notebook path
- it exercises the single-leg parser flow
- it avoids the additional SNB dependency branch

## Pilot Flow

The intended first working flow is:

1. login through `/auth/login`
2. load `/dashboard`
3. open `/pairs/CHF_EUR`
4. trigger `POST /pairs/CHF_EUR/run`
5. render:
   - latest features
   - chart payloads
   - analyst memo
   - parsed signal
   - sizing output
6. optionally append the run to the journal through `POST /journals/CHF_EUR`

## Rollout Across All Four Pairs

After the pilot flow is stable, roll the same platform pattern across:

1. `CHF_EUR`
2. `ZB_GC`
3. `BZ_GC`
4. `CHF_GC`

That order keeps rollout risk lower:

- one validated single-leg pair first
- then the other single-leg pair
- then the routed two-leg pair
- then the routed pair with the extra SNB branch
