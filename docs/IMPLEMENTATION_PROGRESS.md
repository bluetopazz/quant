# IMPLEMENTATION_PROGRESS.md

## 1. Scope

This log records the platform refactor implementation from notebook-era suite to login-based Macro Relative-Value Intelligence Suite.

This phase implemented:

- backend contract models
- backend persistence refactor
- backend pair-run services and endpoints
- frontend login/dashboard/pair-page operator flow
- CHF/EUR pilot pair path
- dynamic platform pattern for the remaining three pairs

This phase did not implement:

- backtest migration
- historical analog engine
- async job queue
- full production auth/session hardening

## 2. Implementation Summary

### Step 1 — Canonical engine contract implemented

Built:

- structured engine-side contract objects for pair runs
- centralized prompt source for all four pairs

Files changed:

- `macro_intel/contracts.py`
- `macro_intel/engine.py`
- `macro_intel/llm/prompts.py`
- `macro_intel/__init__.py`

What was preserved:

- four-pair universe
- pair-specific prompt styles
- single-leg vs routed strategy distinction
- pair-specific journal field semantics

What remains incomplete:

- richer parser confidence handling
- explicit source freshness metadata
- prompt asset versioning beyond string ids

Runtime validated:

- Python compile validation passed for `macro_intel`

### Step 2 — Backend contract schemas implemented

Built:

- FastAPI/Pydantic schemas for:
  - `PairRunRequest`
  - `PairRunResult`
  - `PairRunStatus`
  - `FeatureSnapshot`
  - `ChartPayload`
  - `AnalystMemo`
  - `ParsedSignal`
  - `RiskTicket`
  - `JournalEntryPreview`
  - `RunWarning`
  - `RunError`

Files changed:

- `backend/app/schemas/run.py`
- `backend/app/schemas/pair.py`
- `backend/app/schemas/journal.py`

What was preserved:

- pair-centric response model
- memo/signal/risk/history separation

What remains incomplete:

- no separate status polling endpoint yet
- request-status lifecycle is persisted synchronously, not asynchronously

Runtime validated:

- backend schema import/compile validation passed

### Step 3 — Backend persistence refactor implemented

Built:

- database-backed platform source of truth for:
  - users
  - pair runs
  - feature snapshots
  - memos
  - parsed signals
  - risk tickets
  - chart payloads
  - journal entries

Files changed:

- `backend/app/db/models.py`
- `backend/app/core/config.py`

What was preserved:

- CSV journaling compatibility path

What remains incomplete:

- no formal DB migration layer yet
- current model still uses JSON for some nested payloads pragmatically

Runtime validated:

- DB initialization via FastAPI startup worked in API smoke tests

### Step 4 — Backend service layer implemented

Built:

- pair-run orchestration service
- run serialization service
- pair history/latest retrieval
- journal history and append service

Files changed:

- `backend/app/services/pair_runner.py`
- `backend/app/services/journal_service.py`

What was preserved:

- `macro_intel` remains the intelligence engine
- routes do not own pair logic

What failed / was fixed:

- fixed prior journal-service correctness issue by importing/using `datetime` properly
- fixed SQLAlchemy `relationship` shadowing bug in `backend/app/db/models.py`

Runtime validated:

- API smoke validation for login, health, pair metadata, and journal/history plumbing

### Step 5 — FastAPI routes updated to real contract

Built:

- real structured routes for:
  - `POST /auth/login`
  - `GET /auth/me`
  - `GET /health`
  - `GET /pairs`
  - `GET /pairs/{pair_id}`
  - `POST /pairs/{pair_id}/run`
  - `GET /pairs/{pair_id}/latest`
  - `GET /pairs/{pair_id}/history`
  - `GET /pairs/{pair_id}/charts`
  - `GET /journals`
  - `GET /journals/{pair_id}`
  - `POST /journals/{pair_id}`

Files changed:

- `backend/app/api/routes/pairs.py`
- `backend/app/api/routes/journals.py`

What was preserved:

- pair registry semantics
- history/journal separation

What remains incomplete:

- no background-job execution path yet

Runtime validated:

- `GET /health` returned `200`
- `POST /auth/login` returned `200`
- `GET /pairs` returned all four pairs
- `GET /pairs/CHF_EUR` returned pilot pair metadata

### Step 6 — Frontend operator flow completed

Built:

- login flow
- protected layout
- dashboard with all four pairs
- dynamic pair page consuming backend contract
- chart rendering from structured chart payload array
- recent run history display
- journal/history display
- multi-pair sidebar navigation

Files changed:

- `frontend/lib/types.ts`
- `frontend/lib/api.ts`
- `frontend/components/charts/PairCharts.tsx`
- `frontend/components/pairs/PairRunPanel.tsx`
- `frontend/components/layout/AppShell.tsx`
- `frontend/hooks/useJournal.ts`
- `frontend/app/pairs/[pairId]/page.tsx`
- `frontend/components/ui/StatusPill.tsx`

What was preserved:

- dashboard/pair-page/journal-page operator workflow
- pair command-center shape
- UI renders intelligence, not pair logic

What failed / was fixed:

- fixed Next.js 15 route-param typing on `frontend/app/pairs/[pairId]/page.tsx`

Runtime validated:

- production frontend build succeeded via `npm run build`

### Step 7 — Generalized platform pattern across all four pairs

Built:

- engine contract supports:
  - `CHF_EUR`
  - `ZB_GC`
  - `BZ_GC`
  - `CHF_GC`
- frontend routing and navigation expose all four pairs

Files changed:

- `macro_intel/engine.py`
- `frontend/components/layout/AppShell.tsx`

What was preserved:

- `ZB_GC` target-asset semantics
- `BZ_GC` routed-leg semantics
- `CHF_GC` SNB-intervention semantics

What remains incomplete:

- live parity validation was only explicitly exercised for `CHF_EUR` as pilot
- remaining three pairs still need the same runtime proof discipline in a non-sandbox environment

## 3. Runtime Validation Summary

### Completed

- `python -m compileall macro_intel backend/app`
- frontend production build
- backend API smoke tests for:
  - health
  - login
  - pair listing
  - pair metadata
- mocked CHF/EUR backend run proof for:
  - persistence
  - latest retrieval
  - history retrieval
  - journal append/history retrieval

### Attempted but constrained

- live `CHF_EUR` run through backend

Observed issue:

- Yahoo Finance rate-limit backoff caused the live run attempt to stall in retry behavior inside `macro_intel.data.market`

Interpretation:

- this is consistent with the known repo/platform risk already documented in the audit
- the implementation path is in place, but live-source runtime proof remains environment-dependent

## 4. Pair-Specific Behavior Preserved

### `CHF_EUR`

- preserved European divergence framing
- preserved target semantics:
  - `FXE (via Short EUR)`
  - `FXE (via Long EUR)`
- preserved EU risk and inflation-differential drivers

### `ZB_GC`

- preserved sovereign-risk framing
- preserved target asset switching between `GLD` and `TLT`
- preserved real-yield driver chart

### `BZ_GC`

- preserved growth-vs-haven framing
- preserved routed two-leg strategy structure
- preserved PMI/inflation driver context

### `CHF_GC`

- preserved managed-vs-unmanaged haven framing
- preserved SNB-intervention dependency and semantics
- preserved routed two-leg strategy structure

## 5. Known Gaps After This Phase

- live-source runtime remains fragile because of Yahoo rate limits and local LLM dependency
- no async/background execution model yet
- no formal migration framework for DB schema changes
- no full notebook-vs-platform parity harness yet
- no platform-native replacement for CSV compatibility output yet

## 6. Recommended Next Engineering Step

The next code phase should focus on:

1. reducing live-source runtime fragility for pair runs
2. tightening notebook-vs-platform parity checks for `CHF_EUR`
3. introducing a background execution/status model for slow runs
