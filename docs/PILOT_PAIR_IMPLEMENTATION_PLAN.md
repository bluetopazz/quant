# PILOT_PAIR_IMPLEMENTATION_PLAN.md

## 1. Purpose

This document defines the exact pilot implementation plan for one end-to-end pair flow using `CHF_EUR`.

Scope:

- FastAPI backend
- database-backed run storage
- Next.js pair page
- journal/history display

Out of scope:

- all-four-pair implementation
- backtest migration
- redesign of macro theses
- redesign of signal semantics
- full production hardening beyond what is needed for the pilot

## 2. Why `CHF_EUR` Is the Pilot

`CHF_EUR` is the correct first pilot because:

- it already has the strongest migrated runtime proof in `docs/MIGRATION_STATUS.md`
- it exercises the single-leg parser path
- it avoids the extra SNB dependency branch
- it already maps cleanly onto the current scaffolded pair-page flow
- it preserves a differentiated macro identity: European divergence and Swiss credibility

## 3. Pilot Objective

Implement one trustworthy `CHF_EUR` platform flow that allows an authenticated user to:

1. open the `CHF_EUR` pair page
2. trigger a run
3. view current feature state
4. inspect chart payloads
5. read the analyst memo
6. inspect the parsed signal
7. inspect sizing output
8. view journal-compatible preview data
9. browse recent platform runs and journal history

The pilot is successful when the platform output is meaningfully parity-checked against the notebook and preserves current semantics.

## 4. Non-Negotiable Semantics To Preserve

The pilot must preserve:

- current causal drivers:
  - `EU_Risk_Spread`
  - `Inflation_Differential`
- current prompt framing:
  - European divergence
  - strong divergence vs correlated chop
  - broad-USD vs genuine divergence distinction
- current signal semantics:
  - `FXE (via Short EUR)`
  - `FXE (via Long EUR)`
- current sizing semantics:
  - current single-leg heuristic from `macro_intel.risk.size_single_strategy`
- current journal field meaning:
  - `Target_Asset`
  - `Strategy`
  - `Contracts_Sized`
  - `Signal_ZScore`
  - `Signal_Velocity_5D`
  - `Corr_90D`
  - `VIX_IVR`
  - `FXE_VRP`
  - `FXF_VRP`
  - `EU_Risk_Spread`
  - `Inflation_Differential`
  - `Analyst_Reasoning`

## 5. Required Backend Endpoints

### Existing endpoints to keep/refine

- `POST /auth/login`
- `GET /auth/me`
- `GET /pairs`
- `GET /pairs/{pair_id}`
- `POST /pairs/{pair_id}/run`
- `GET /pairs/{pair_id}/latest`
- `GET /pairs/{pair_id}/history`
- `GET /pairs/{pair_id}/charts`
- `GET /journals/{pair_id}`
- `POST /journals/{pair_id}`

### Pilot-specific expectations for `CHF_EUR`

#### `POST /pairs/CHF_EUR/run`

Must:

- validate pair id
- create/persist run lifecycle state
- execute `CHF_EUR` pair analysis through the structured contract
- store completed run result in DB
- optionally append journal-compatible entry
- return the canonical `PairRunResult`

#### `GET /pairs/CHF_EUR/latest`

Must return:

- the latest successful, degraded-success, or error run with structured objects

#### `GET /pairs/CHF_EUR/history`

Must return:

- recent run summaries with status and timestamps

#### `GET /journals/CHF_EUR`

Must return:

- current pair journal history
- transitional support may still read CSV-backed history

## 6. Required Backend Services

### A. `CHF_EUR` pair policy/service

Add an explicit pair-aware service layer that owns:

- target-asset selection
- prompt context assembly
- feature extraction for API payloads
- chart payload composition
- journal preview serialization

This can be implemented as:

- a pair-specific adapter module
- or a registry-driven policy object

But the `CHF_EUR` logic must remain explicit.

### B. Run orchestration service

Must own:

- lifecycle status transitions
- source fetch orchestration
- `macro_intel` invocation
- warning/error classification
- persistence coordination

### C. Prompt/template service

Must own:

- authoritative `CHF_EUR` prompt template
- prompt version id
- prompt metadata stored with run

### D. Chart payload service

Must own:

- core chart payload
- EU risk chart payload
- inflation-differential chart payload
- correlation payload
- volatility payload

### E. Journal preview serializer

Must own:

- `CHF_EUR` journal preview payload in canonical form
- legacy CSV-compatible field mapping

### F. Run history/journal history service

Must own:

- recent platform runs from DB
- current journal history
- response serialization

## 7. Required Database Tables / Entities

The pilot should use database-backed run storage with explicit logical entities.

### Minimum required entities

#### `pair_runs`

Fields:

- `id`
- `pair_id`
- `status`
- `run_timestamp`
- `requested_by_user_id`
- `trigger_source`
- `prompt_version`
- `engine_version`
- `warning_count`
- `error_code`

#### `pair_run_feature_snapshots`

Fields:

- `id`
- `pair_run_id`
- `pair_id`
- `as_of_date`
- `core_metrics_json`
- `pair_extensions_json`

#### `pair_run_memos`

Fields:

- `id`
- `pair_run_id`
- `pair_id`
- `content`
- `model_name`
- `prompt_version`
- `prompt_style`
- `metadata_json`

#### `pair_run_signals`

Fields:

- `id`
- `pair_run_id`
- `pair_id`
- `signal_style`
- `parser_style`
- `parser_version`
- `parse_status`
- `target_asset`
- `strategy`
- `directional_bias`
- `metadata_json`

#### `pair_run_risk_tickets`

Fields:

- `id`
- `pair_run_id`
- `pair_id`
- `sizing_mode`
- `account_value_assumption`
- `risk_bps_per_trade`
- `contracts`
- `risk_budget_usd`
- `metadata_json`

#### `pair_run_chart_payloads`

Fields:

- `id`
- `pair_run_id`
- `pair_id`
- `chart_id`
- `family`
- `title`
- `render_kind`
- `payload_json`

#### `journal_entries`

Fields:

- `id`
- `pair_run_id`
- `pair_id`
- `journal_schema_version`
- `journal_mode`
- `payload_json`
- `csv_path`
- `created_at`

### Transitional note

The current `backend/app/db/models.py` can be evolved from its existing JSON-heavy shape, but the pilot should separate logical concerns enough that the run is no longer just one oversized JSON blob.

## 8. Required Frontend Routes and Components

### Required routes

- `/login`
- `/dashboard`
- `/pairs/CHF_EUR`
- `/journals`

### Required `CHF_EUR` page components

#### Pair header

Shows:

- pair id
- theme
- relationship
- latest run status
- run timestamp

#### Run controls

Actions:

- run analysis
- refresh
- append journal entry

#### Current state section

Shows:

- signal z-score
- signal velocity
- `Corr_90D`
- target-asset candidate
- key driver values

#### Chart stack

Must include:

- core normalized pair
- ratio/spread
- EU risk causal chart
- inflation differential causal chart
- correlation
- volatility

#### Analyst memo section

Shows:

- memo text
- prompt version
- model identity

#### Parsed signal section

Shows:

- target asset
- strategy
- parser style / parse status if useful

#### Sizing section

Shows:

- contracts
- risk budget
- sizing assumption metadata

#### Journal/history section

Shows:

- recent journal records
- current-run journal preview or append confirmation

## 9. Required Notebook Parity Checks

The pilot is not complete until `CHF_EUR` platform output is compared against `chfeur.ipynb`.

### Required parity checks

#### A. Feature parity

Confirm the platform computes the same or intentionally equivalent:

- `CHF_EUR_Spread_Norm`
- `Signal_Velocity_5D`
- `Corr_90D`
- `EU_Risk_Spread`
- `Inflation_Differential`
- `VIX_IVR`
- `FXE_VRP`
- `FXF_VRP`

#### B. Prompt parity

Confirm the backend prompt preserves:

- European divergence framing
- strong divergence vs correlated chop logic
- target-asset semantics

#### C. Signal parity

Confirm parsed strategy semantics still match notebook intent:

- single-leg
- EUR expression preserved

#### D. Sizing parity

Confirm sizing is still based on the current heuristic:

- `size_single_strategy`
- current account/risk-bps assumption model

#### E. Journal parity

Confirm journal preview payload matches current CSV field meaning exactly

## 10. Failure States

The pilot must define explicit operator-visible failure states.

### Request/validation failures

- invalid pair id
- missing auth
- malformed request

### Runtime failures

- Yahoo market data unavailable
- FRED key missing or FRED series unavailable
- feature build failure
- LLM offline
- memo timeout
- parser failure
- persistence failure

### Degraded-success cases

- some macro data missing but minimum `CHF_EUR` run still usable
- journal append failed after successful run persistence
- chart payload partially available but memo/signal/risk still valid

### Frontend-visible behavior

Each failure/degraded state should show:

- run status
- human-readable message
- whether the run is retryable
- whether any partial result is still trustworthy

## 11. Success Criteria

The pilot is successful when all of the following are true:

1. An authenticated user can run `CHF_EUR` end-to-end from the platform
2. The backend persists structured run results
3. The pair page renders the full `CHF_EUR` object set:
   - feature snapshot
   - charts
   - memo
   - parsed signal
   - risk ticket
   - journal preview/history
4. Pair-specific semantics are preserved
5. Notebook parity checks pass at an acceptable level
6. Failure and degraded-success states are explicit and operator-usable

## 12. Suggested Implementation Sequence

1. Formalize the `PairRun` contract in code from `docs/PAIR_RUN_CONTRACT.md`
2. Extract the authoritative `CHF_EUR` prompt into backend-owned template/config
3. Refactor `macro_intel.engine` output for `CHF_EUR` into canonical objects
4. Add/adjust DB entities for structured run storage
5. Refine FastAPI `CHF_EUR` run/latest/history/journal routes
6. Refine the `CHF_EUR` pair page to consume the canonical contract
7. Run notebook/platform parity checks
8. Only after pilot success, decide how to roll the pattern to `ZB_GC`, `BZ_GC`, and `CHF_GC`

## 13. What This Pilot Should Not Do

The pilot should not:

- redesign `CHF_EUR` thesis logic
- redesign journal semantics
- migrate backtest
- introduce all-four-pair orchestration
- depend on the current frontend scaffold as final UX truth
- erase explicit pair-specific logic behind vague generic services
