# PILOT_VALIDATION.md

## 1. Pilot Pair

- pair: `CHF_EUR`
- notebook reference: `chfeur.ipynb`
- platform target:
  - FastAPI backend
  - database-backed run persistence
  - Next.js pair page

## 2. Backend Contract Proof

### Implemented backend objects

The pilot now has real backend contract implementations for:

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

### Implemented backend routes

- `POST /auth/login`
- `GET /auth/me`
- `GET /health`
- `GET /pairs`
- `GET /pairs/CHF_EUR`
- `POST /pairs/CHF_EUR/run`
- `GET /pairs/CHF_EUR/latest`
- `GET /pairs/CHF_EUR/history`
- `GET /pairs/CHF_EUR/charts`
- `GET /journals/CHF_EUR`
- `POST /journals/CHF_EUR`

## 3. Frontend Rendering Proof

### Implemented frontend surfaces

- login page
- protected layout
- dashboard with four pair cards
- dynamic pair page for `CHF_EUR`
- journal/history display

### `CHF_EUR` pair page now renders

- pair metadata
- current feature state
- chart payload panels
- analyst memo
- parsed signal
- sizing/risk ticket
- recent platform run history
- journal preview/history
- run action

## 4. Parity Preservation Check

### A. Pair metadata

Preserved:

- pair id: `CHF_EUR`
- theme: `European_Divergence`
- relationship: `FXF over FXE`
- single-strategy signal shape
- single-leg prompt style

### B. Causal-driver interpretation

Preserved:

- `EU_Risk_Spread` as one causal driver
- `Inflation_Differential` as the second causal driver
- divergence vs correlated USD-driven chop framing

### C. Chart family structure

Preserved as platform chart payload families:

- core normalized pair
- ratio
- spread
- causal driver: EU risk spread
- causal driver: inflation differential
- correlation
- volatility dashboard

### D. Memo framing

Preserved in centralized prompt source:

- European divergence framing
- strong divergence vs correlated chop logic
- directional bias via EUR expression

### E. Signal style

Preserved:

- single-strategy signal
- target-asset semantics:
  - `FXE (via Short EUR)`
  - `FXE (via Long EUR)`

### F. Sizing semantics

Preserved:

- `size_single_strategy`
- fixed account-value / risk-bps heuristic model

### G. Journal field meaning

Preserved in `JournalEntryPreview`:

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

## 5. Runtime Validation Executed

### Validated directly

- backend API metadata flow:
  - login
  - pair listing
  - pair metadata
- frontend build and route typing
- mocked CHF/EUR backend run flow:
  - run execution route
  - DB persistence
  - latest retrieval
  - history retrieval
  - journal append/history retrieval

### Mocked run result proof

Validated that `POST /pairs/CHF_EUR/run` can:

- accept a run request
- persist a structured pair run
- return a structured `PairRunResult`
- support `latest`, `history`, and journal retrieval

### Live run attempt

Attempted:

- real `POST /pairs/CHF_EUR/run` against live source path

Observed:

- Yahoo Finance rate-limit backoff caused the request to hang in retry behavior

Interpretation:

- platform code path exists
- live-source proof in this environment remains blocked by known Yahoo instability

## 6. Known Differences vs Notebook

### Intentional differences

- charts are now backend-generated payloads for frontend rendering rather than matplotlib notebook plots
- run output is now persisted as platform entities rather than only CSV rows
- memo, signal, risk, and chart payloads are separated into structured objects

### Not yet fully proven live

- end-to-end live semantic equivalence of `CHF_EUR` memo output in this sandbox environment
- live timing/freshness behavior under real Yahoo/FRED/LLM conditions

## 7. Current Pilot Verdict

### Passed

- backend contract implementation
- database-backed run persistence pattern
- frontend operator surface
- pair-specific semantic preservation in code structure
- mocked end-to-end `CHF_EUR` platform flow

### Partially passed

- live `CHF_EUR` run validation

Reason:

- blocked by live-source retry/rate-limit behavior rather than contract or routing failure

## 8. Next Pilot Hardening Priorities

1. add source/runtime controls around Yahoo retries and timeout behavior
2. add explicit degraded-success handling for partial source availability
3. run `CHF_EUR` parity validation in an environment with stable market/FRED/LLM connectivity
