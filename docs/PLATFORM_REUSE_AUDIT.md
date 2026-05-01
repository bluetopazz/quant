# PLATFORM_REUSE_AUDIT.md

## 1. Executive Summary

The current system is a notebook-first macro relative-value research desk centered on four pairs: `ZB_GC`, `BZ_GC`, `CHF_EUR`, and `CHF_GC`. The notebooks remain the real operator surfaces today: they fetch live data, build pair features, render causal charts, generate an LLM memo, parse a strategy, apply rough sizing, and append a row to a pair-specific CSV journal. Underneath them, the repository now has a materially useful shared engine in `macro_intel/`, plus an early FastAPI + Next.js scaffold in `backend/` and `frontend/`.

The target platform is a login-based Macro Relative-Value Intelligence Suite with a Next.js frontend, FastAPI backend, and `macro_intel` as the intelligence engine. That direction is already partially supported. The strongest reuse opportunity is that the repository already has:

- a pair registry and identity model in `macro_intel.config.pairs`
- reusable data loaders and feature builders in `macro_intel.data` and `macro_intel.features`
- an engine entrypoint, `macro_intel.engine.run_pair_analysis`, that already returns API-friendly run objects
- journal read/write utilities and pair-specific journal schema definitions
- a first backend persistence model for pair runs and journal appends
- a first frontend concept map for dashboard, pair page, memo, charts, signal, and journal views

The main blockers are not missing ideas; they are runtime maturity and interface discipline:

- prompts are still inline in the notebooks and duplicated again in `macro_intel.llm.prompts`
- the notebooks and backtest do not share one canonical normalization/live-history semantics
- journal schemas are still pair-specific CSV contracts rather than a stable platform model
- runtime reliability still depends on live Yahoo and local Ollama behavior
- run results are only partially validated and error handling is thin
- backend/job orchestration is synchronous and brittle for long-running LLM/data-fetch paths

Bottom line: `macro_intel` is already strong enough to anchor the FastAPI backend, but only if the next phase focuses on hardening, prompt extraction discipline, structured run schemas, and persistence normalization rather than premature full-product buildout.

## 2. Target Product Interpretation

The intended future product is a pair-centric intelligence suite, not a generic quant platform and not a broker execution stack.

The architecture should be interpreted as:

- `frontend/` or its successor Next.js app owns authentication UX, dashboards, pair pages, charts, memo display, signal display, sizing display, history browsing, and run controls
- `backend/` or its successor FastAPI app owns API delivery, run orchestration, persistence, auth integration, and platform health/status
- `macro_intel/` remains the pair-intelligence engine for config, data acquisition, features, chart payload assembly, memo generation, parsing, sizing, and journal payload preparation
- the four pair notebooks remain during transition as:
  - reference implementations
  - operator fallback surfaces
  - truth surfaces for pair-specific prompt framing and causal presentation

The suite’s identity is the narrow ownership of four macro RV relationships:

- `10yrgc.ipynb` / `ZB_GC`: sovereign confidence and hard-asset vs duration preference
- `crudegc.ipynb` / `BZ_GC`: growth/inflation stress vs haven preference
- `chfeur.ipynb` / `CHF_EUR`: European fragmentation vs convergence and Swiss credibility
- `chfgc.ipynb` / `CHF_GC`: managed fiat refuge vs unmanaged monetary refuge

That pair ontology should survive the platform transition intact.

## 3. Current System Reuse Map

### A. Reusable as-is

- `macro_intel/config/pairs.py`
  - Strong pair registry with first-class pair metadata, prompt/parser styles, signal shape, feature flags, chart metadata, and special rules.
- `macro_intel/data/fred.py`
  - Acceptable FRED loader with partial-failure handling.
- `macro_intel/data/merge.py`
  - Clean shared merge/ffill helper for backend use.
- `macro_intel/features/core.py`
  - Core feature primitives are simple and backend-safe.
- `macro_intel/features/correlations.py`
  - Reusable rolling return/correlation helpers.
- `macro_intel/features/pair_specific.py`
  - Pair ontology is explicit and maps cleanly into backend logic.
- `macro_intel/risk/sizing.py`
  - Lightweight but backend-safe sizing helper.
- `macro_intel/journal/schema.py`
  - Valuable as a transitional compatibility contract for legacy CSV journaling.
- `macro_intel/journal/reader.py`
  - Reusable for history ingestion and migration tooling.
- `macro_intel/engine.PairRunResult`
  - Good seed for a platform run-result contract.
- `backend/app/schemas/*.py`
  - Good first-pass API schemas for the current scaffold.
- `frontend/lib/types.ts`
  - Useful current UI contract mirror.

### B. Reusable with adaptation

- `macro_intel/engine.py`
  - Strong core orchestration, but needs runtime hardening, structured error states, and prompt extraction cleanup.
- `macro_intel/data/market.py`
  - Valuable loader logic, but Yahoo dependence and blocking sleeps need stronger runtime controls.
- `macro_intel/data/snb.py`
  - Reusable, but needs retry/timeout/error normalization.
- `macro_intel/features/volatility.py`
  - Reusable, but needs divide-by-zero handling and schema validation.
- `macro_intel/llm/client.py`
  - Reusable transport, but needs retries, status classification, and LLM availability handling.
- `macro_intel/llm/parser.py`
  - Useful transitional parser layer, but too shallow for platform-grade confidence.
- `macro_intel/llm/prompts.py`
  - Good extraction target, but currently incomplete relative to notebook-era richness.
- `macro_intel/reporting/charts.py`
  - Reusable conceptually for chart families, but notebook-matplotlib output should become backend payload generation, not frontend chart rendering code.
- `macro_intel/journal/writer.py`
  - Reusable for transition compatibility, but CSV append should become optional legacy persistence.
- `backend/app/services/pair_runner.py`
  - Good wrapper around `run_pair_analysis`, but needs async/job-ready orchestration and stricter failure semantics.
- `backend/app/services/journal_service.py`
  - Useful transition wrapper, but currently tied to CSV and contains at least one correctness issue (`datetime` used without import).
- `backend/app/db/models.py`
  - Solid pilot persistence seed, but too generic and JSON-heavy for long-term analytics.
- `frontend/`
  - High concept reuse, low durable code reuse. Current UX scaffold is useful as a pilot reference, not final product.

### C. Reference-only / notebook-only

- Inline pair prompts inside:
  - `10yrgc.ipynb`
  - `crudegc.ipynb`
  - `chfeur.ipynb`
  - `chfgc.ipynb`
  These remain the richest expression of pair-specific narrative framing today.
- Notebook-local causal chart composition and commentary
  - especially dual-axis/stacked driver layouts in `chfeur.ipynb` and `chfgc.ipynb`
- Notebook print-oriented operator messaging and trade-ticket narration
- `backtest.ipynb` historical signal engine
  - useful as reference logic and validation surface, not ready as platform API logic
- `quant.ipynb`
  - separate prototype track; reference-only unless intentionally re-scoped later

### D. Should be replaced

- `trade_journal.csv`
  - Legacy malformed artifact, not the current journal-of-record.
- Hard-coded notebook environment defaults
  - especially inline `FRED_API_KEY` defaults in notebooks.
- Second-pass LLM parser dependence for single-leg notebooks
  - workable for notebook flow, but not ideal platform-grade parsing.
- Matplotlib-bound reporting path as a platform rendering approach
  - frontend should render charts; backend should send payloads.
- Synchronous run path in `POST /pairs/{pair_id}/run`
  - too fragile for long fetch/LLM operations.

### E. Legacy / deprecate

- `trade_journal.csv`
- any backtest logic that assumes the legacy aggregate journal
- duplicated helper definitions inside `backtest.ipynb` already present in `macro_intel`
- `quant.ipynb` as a candidate production direction for the pair suite
- `backend/app.db` as a durable architecture choice; fine for pilot, not ideal as the platform persistence end state

## 4. Repository Component Audit

### `macro_intel/`

What it does today:

- holds the shared pair engine beneath the four migrated notebooks
- defines pair identities, loaders, features, prompts, parsers, sizing, chart payloads, and journal helpers

Reusable:

- yes, this is the core reuse anchor

Future architecture home:

- backend intelligence engine

Required changes:

- extract authoritative prompts into package-managed assets/templates
- strengthen runtime validation and failure typing
- formalize structured API-safe outputs and persistence-oriented models

### `10yrgc.ipynb`

What it does today:

- sovereign-risk pair notebook for `GLD` vs `TLT`
- fetches Yahoo and FRED data
- builds GLD/TLT spread, real-yield driver, volatility dashboard
- generates single-leg analyst memo, second-pass parses one strategy, sizes one target asset, appends to `journal_zb_gc.csv`

Reusable:

- yes, as a reference and extraction source for pair-specific logic

Future architecture home:

- prompt semantics, target-asset logic, and causal chart definitions move into backend pair policy/config
- output layout concepts inform pair detail page UX

Required changes:

- eliminate notebook-only prompt/source-of-truth drift
- move journal field assembly into structured backend serializers

### `crudegc.ipynb`

What it does today:

- growth-vs-haven pair notebook for `GLD` vs `BNO`
- uses pair-routed memo output with two parsable strategy lines
- logs directional bias plus per-leg strategy/contracts to `journal_bz_gc.csv`

Reusable:

- yes, strongly for pair-specific routed-strategy logic

Future architecture home:

- pair-specific bias logic, routed-leg semantics, and causal chart definitions move to backend pair services

Required changes:

- preserve pair-specific thematic framing instead of generic pair abstraction
- separate memo richness from parse contract more cleanly

### `chfeur.ipynb`

What it does today:

- European divergence notebook for `FXF` vs `FXE`
- defines target-asset semantics through `FXE (via Short EUR)` and `FXE (via Long EUR)`
- uses EU risk spread and inflation differential as causal drivers
- logs to `journal_chf_eur.csv`

Reusable:

- yes, and it is the best current pilot candidate

Future architecture home:

- backend pilot pair for first robust web flow

Required changes:

- normalize directional semantics into structured fields
- preserve dual-driver causal interpretation and not flatten it into generic “FX divergence”

### `chfgc.ipynb`

What it does today:

- managed-vs-unmanaged haven notebook for `FXF` vs `GLD`
- includes SNB sight deposits and weekly intervention proxy
- uses routed two-leg strategy output
- logs to `journal_chf_gc.csv`

Reusable:

- yes, but less mature operationally than `CHF_EUR` because of extra SNB dependency branch

Future architecture home:

- backend pair service with explicit SNB dependency and haven-divergence semantics

Required changes:

- preserve intervention-specific prompt framing
- add stronger handling for stale/weekly SNB data and mixed-frequency timing

### `backtest.ipynb`

What it does today:

- loads all per-pair journals
- standardizes rows into a common schema
- builds a rolling-z-score historical oracle
- runs a signal-direction proxy PnL backtest
- includes a synthetic historical signal engine
- exports `backtest_results.csv` and `backtest_pair_summary.csv`

Reusable:

- partially

Future architecture home:

- validation harness, research reference, and later offline analytics service

Required changes:

- align live and backtest semantics
- move shared reader/helper logic into importable modules
- decide whether historical signal engine becomes future analog/regime tooling or remains research-only

### `quant.ipynb`

What it does today:

- separate prototype using MongoDB, embeddings, mock data, and ad hoc LLM utilities
- explores a knowledge/embedding architecture unrelated to the current pair-run flow

Reusable:

- conceptually only

Future architecture home:

- reference for future knowledge archive / analog engine ideas, not part of phase-one platform foundation

Required changes:

- explicit scoping decision before any reuse

### Current journals

What they do today:

- store append-only per-pair idea history
- preserve memo text and key feature snapshot fields

Reusable:

- yes, as legacy data and as schema-discovery artifacts

Future architecture home:

- transitional source data for migration into database-backed run/journal tables

Required changes:

- define canonical core entities and map pair-specific extensions explicitly

### Migration and architecture docs

Reviewed:

- `README.md`
- `SYSTEM_ARCHITECTURE.md`
- `ROADMAP.md`
- `docs/MIGRATION_STATUS.md`
- `docs/API_CONTRACT.md`
- `docs/ENVIRONMENT.md`

What they do today:

- provide mostly accurate repo truth
- document migration state, runtime validation, and first platform contract

Reusable:

- yes

Future architecture home:

- architecture baseline and transition reference

Required changes:

- keep synchronized with code; note that `docs/REFACTOR_PROGRESS.md` referenced in the IDE context is not present in the repository and should not be treated as repo truth

### Dependency/bootstrap artifacts

Reviewed:

- `requirements.txt`
- notebook inline env defaults
- backend env config in `backend/app/core/config.py`

What they do today:

- provide minimal bootstrap for notebooks and backend

Reusable:

- partially

Future architecture home:

- refined environment contracts for backend runtime and local dev

Required changes:

- add stricter environment validation, remove inline secrets/default keys, and make runtime modes explicit

### `README.md`

What it does today:

- accurately describes the current repo as notebook-first with a shared package and early platform scaffold

Reusable:

- yes

Future architecture home:

- repo-level orientation

Required changes:

- update after this audit so platform transition guidance and artifact status stay aligned

## 5. `macro_intel` Reuse Audit

### `config`

Current maturity:

- medium-high

Reuse rating:

- strong

What works now:

- `PairConfig` and `PAIR_REGISTRY` already encode first-class pair identity, signal shape, prompt style, chart metadata, and special rules
- `Settings.from_env()` centralizes core engine runtime settings

What needs change:

- `Settings` should separate notebook defaults from backend deployment defaults
- pair config should eventually own prompt template ids, chart family ids, journal serializer ids, and pair capability flags more explicitly

Likely backend destination:

- pair registry dependency, metadata endpoints, pair orchestration policy layer

### `data`

Current maturity:

- medium

Reuse rating:

- good with hardening

What works now:

- FRED loader tolerates per-series failures
- yfinance loader already improved beyond notebook-era single fetches
- merge helper is clean
- SNB fetcher is isolated

What needs change:

- add structured retry metadata, timeout control, stale-data warnings, and source-specific error classes
- normalize mixed-frequency freshness handling
- consider snapshot/cache layer before production-like use

Likely backend destination:

- backend service dependencies for fetch/orchestration

### `features`

Current maturity:

- medium-high

Reuse rating:

- strong

What works now:

- core features are isolated and deterministic
- pair-specific feature builders preserve the macro theses explicitly
- rolling correlations, VRP, IV rank, signal velocity are backend-safe computations

What needs change:

- clarify canonical live normalization policy
- add schema validation on required inputs/outputs
- protect against divide-by-zero/empty rolling windows in volatility helpers

Likely backend destination:

- core feature engine invoked inside pair-run service

### `reporting`

Current maturity:

- medium

Reuse rating:

- conceptually strong, code-level partial

What works now:

- chart family boundaries are already visible: core pair, causal driver, correlation, volatility

What needs change:

- matplotlib plotting helpers should not be the web-platform reporting abstraction
- backend should standardize payload builders like those in `engine._build_chart_payloads`
- pair-specific causal layouts need declarative chart definitions, not notebook-local plotting code only

Likely backend destination:

- chart payload assembly service, not direct web rendering

### `llm`

Current maturity:

- medium-low for platform use

Reuse rating:

- reusable with substantial adaptation

What works now:

- `ask_llm()` gives a single transport path
- parser utilities support both notebook parsing styles
- `prompts.py` contains an extracted first pass

What needs change:

- make prompt sources authoritative and versioned
- eliminate divergence between notebook prompts and package prompts
- add timeout/retry handling, model availability checks, parsing confidence, and partial-failure semantics
- replace fragile second-pass parsing with more structured outputs where possible

Likely backend destination:

- memo-generation and signal-extraction service layer

### `risk`

Current maturity:

- medium

Reuse rating:

- strong for current scope

What works now:

- single-leg and two-leg sizing helpers are clean and deterministic

What needs change:

- expose assumptions explicitly in API payloads
- eventually separate “idea sizing heuristic” from any future production risk model

Likely backend destination:

- risk ticket builder in pair-run orchestration

### `journal`

Current maturity:

- medium

Reuse rating:

- strong transitional reuse

What works now:

- pair-specific CSV compatibility is explicit
- reader standardization is useful for history and backtest ingestion

What needs change:

- journal payload building should move from notebook/engine branching into canonical serializers
- CSV append should become an optional compatibility sink, not primary persistence
- canonical core schema should be formalized independently of CSV field order

Likely backend destination:

- migration adapters, journal history service, transitional persistence compatibility layer

### `utils`

Current maturity:

- medium

Reuse rating:

- solid

What works now:

- date windowing and minimal validation helpers

What needs change:

- expand validation into runtime contracts for feature frames, run outputs, and external-source freshness

Likely backend destination:

- shared validation helpers across services

Overall answer to the key question:

`macro_intel` is already good enough to anchor the FastAPI backend if the backend treats it as an intelligence engine plus adapters, not as a finished production service layer.

## 6. Pair Notebook Reuse Audit

### `10yrgc.ipynb` (`ZB_GC`)

Reusable pair-specific prompt logic:

- sovereign-risk framing
- target-asset selection between `GLD` and `TLT`
- distinction between strong trend / weak trend / range-chop in haven-vs-duration behavior

Reusable causal chart definitions:

- `GLD` vs `DFII10` causal chart

Reusable journal field mappings:

- `Target_Asset`, `GLD_IVR`, `TLT_IVR`, `GLD_VRP`, `TLT_VRP`, `DFII10`, `T10YIE`, `DTWEXBGS`

Reusable bias/directional logic:

- sign of `GLD_TLT_Spread_Norm` chooses target asset

Reusable feature interpretation:

- negative/low correlation as sovereign-risk regime vs high/positive as classic haven regime

Notebook-only:

- matplotlib display code
- print-style trade ticket narration

Backend vs frontend vs reference:

- backend: target selection, memo context, chart payload definition, journal serializer
- frontend: memo section, signal section, chart layout
- reference-only: notebook prose and operator phrasing

### `crudegc.ipynb` (`BZ_GC`)

Reusable pair-specific prompt logic:

- growth-vs-haven framing
- recession vs stagflation vs inflation/geopolitics routing
- routed-leg instruction contract

Reusable causal chart definitions:

- `GLD_BNO_Ratio` vs `IPMAN`

Reusable journal field mappings:

- `Directional_Bias`, `Strategy_GLD`, `Strategy_BNO`, `IPMAN`, `CPILFESL`, per-leg IVR/VRP fields

Reusable bias/directional logic:

- sign of `GLD_BNO_Spread_Norm` => `Long GLD / Short BNO` vs inverse

Reusable feature interpretation:

- `Corr_90D < 0` as recession-like
- positive correlation as inflation/geo regime candidate

Notebook-only:

- verbose narrative examples inside the prompt
- display-oriented final pairs ticket

Backend vs frontend vs reference:

- backend: routed-signal builder and pair-specific macro-thesis routing
- frontend: two-leg signal/sizing display and pair command-center structure
- reference-only: notebook explanatory narration

### `chfeur.ipynb` (`CHF_EUR`)

Reusable pair-specific prompt logic:

- European divergence framing
- distinction between strong divergence and correlated USD-driven chop
- `FXE (via Short EUR)` vs `FXE (via Long EUR)` target semantics

Reusable causal chart definitions:

- `CHF_EUR_Ratio` vs `EU_Risk_Spread`
- `CHF_EUR_Ratio` vs `Inflation_Differential`

Reusable journal field mappings:

- `Target_Asset`, `VIX_IVR`, `FXE_VRP`, `FXF_VRP`, `EU_Risk_Spread`, `Inflation_Differential`

Reusable bias/directional logic:

- sign of `CHF_EUR_Spread_Norm` chooses bearish/bullish EUR framing

Reusable feature interpretation:

- high correlation as broad-USD regime
- falling/lower correlation as genuine divergence regime

Notebook-only:

- notebook-local dual-axis layout details
- local print narrative

Backend vs frontend vs reference:

- backend: pilot pair-run service, prompt context, chart payload definitions
- frontend: likely first full pair page because this pair already has strongest runtime proof
- reference-only: notebook-specific exposition

### `chfgc.ipynb` (`CHF_GC`)

Reusable pair-specific prompt logic:

- managed-vs-unmanaged haven framing
- SNB intervention active/inactive logic
- divergence vs correlated haven logic
- routed-leg output requirement

Reusable causal chart definitions:

- `CHF_GLD_Ratio` vs `SNB_Intervention_WoW`

Reusable journal field mappings:

- `Directional_Bias`, `Strategy_GLD`, `Strategy_FXF`, `CHF_VIX_IVR`, `SNB_Intervention_WoW`

Reusable bias/directional logic:

- sign of `CHF_GLD_Spread_Norm` picks `Long GLD / Short FXF` vs inverse

Reusable feature interpretation:

- positive correlation as classic risk-off haven alignment
- falling/negative correlation as intervention or haven-divergence signal

Notebook-only:

- SNB-specific display formatting and ticket narration

Backend vs frontend vs reference:

- backend: explicit pair service branch with SNB freshness semantics
- frontend: pair page should expose intervention-specific state and data freshness
- reference-only: notebook-specific explanatory examples

Answer to the section’s core question:

Across all four notebooks, the backend should absorb the pair-specific prompt context, bias logic, journal serialization rules, and declarative chart definitions; the frontend should absorb the page structure and information architecture; the notebooks should remain as truth/reference surfaces until backend outputs are demonstrably equivalent.

## 7. Backend Reuse Plan

What can directly power a FastAPI backend now:

- pair registry and metadata endpoints
  - already mostly present via `PAIR_REGISTRY`, `GET /pairs`, and `GET /pairs/{pair_id}`
- pair run orchestration
  - already present in `macro_intel.engine.run_pair_analysis` and `backend/app/services/pair_runner.py`
- latest pair snapshot endpoint
  - already present in `GET /pairs/{pair_id}/latest`
- chart data endpoint
  - already present in `GET /pairs/{pair_id}/charts`
- journal/history endpoint
  - already present in `backend/app/services/journal_service.py`
- health/status endpoint
  - already present in `GET /health`

What current code can be wrapped with minimal disruption:

- `macro_intel.engine.run_pair_analysis`
  - wrap as a pair-run service operation
- `macro_intel.config.pairs`
  - wrap as metadata/detail service
- `macro_intel.journal.reader`
  - wrap as current journal history adapter
- `macro_intel.engine.PairRunResult`
  - convert into canonical API DTO + persistence DTO

Missing backend-specific abstractions:

- request/response schemas that distinguish:
  - run request
  - run status
  - run completion
  - run failure
  - journal append result
- service layer wrappers for:
  - prompt assembly
  - feature snapshot normalization
  - chart payload assembly
  - journal serialization
- structured run-result entities instead of wide JSON blobs only
- normalized database models for:
  - `PairRun`
  - `Memo`
  - `Signal`
  - `RiskTicket`
  - `JournalEntry`
- run status tracking beyond synchronous request lifecycle
- exception classes for source fetch failure, LLM failure, parse failure, and validation failure
- async/job handling or background work queue for long runs

Auth-adjacent needs:

- current auth is acceptable only as a pilot/dev scaffold
- production transition needs:
  - secret management
  - stronger token/session model
  - operator/user audit fields on runs and journal appends

Persistence integration needs:

- stop relying on JSON blob fields as the only long-term store
- keep CSV journaling as optional transitional sink
- migrate historical CSVs into database-backed run/journal records with pair-specific extension payloads

## 8. Frontend Reuse Plan

The frontend will be new, but current notebooks provide strong concept reuse.

Notebook structure -> pair page structure:

- data/feature status -> state summary card
- core thesis chart -> main pair chart block
- causal driver chart -> “why now” section
- correlation chart -> regime section
- volatility dashboard -> expression/risk section
- analyst memo -> memo section
- parsed strategy and sizing -> signal/ticket section
- journal append -> archive/history action

Current notebook workflow -> future product UX:

- dashboard
  - current `frontend/app/dashboard/page.tsx` is already close conceptually: four pair cards with latest run status
- pair detail page
  - current `frontend/app/pairs/[pairId]/page.tsx` is a good first pass for command-center layout
- memo section
  - maps directly from notebook “LLM Analyst Synthesis”
- signal section
  - maps directly from parsed strategy output
- sizing section
  - maps from notebook trade ticket output
- history section
  - maps from per-pair journal CSV history
- action controls
  - maps from “Run Analysis”, “Refresh”, and “Journal Current Idea”

What should influence future UI strongly:

- notebooks are already organized around “what / why / regime / vol / memo / action”
- pair-specific chart groups should remain distinct
- pair identity text matters; the UI should show the macro thesis, not just ticker pairs

Concept reuse vs code reuse:

- code reuse from current frontend should be limited
- concept reuse should be high
- the current frontend already proves the right product boundary: UI displays, backend computes

## 9. Persistence and Data Model Reuse Audit

What journal fields are already valuable and should survive:

- shared core:
  - `Date`
  - `Pair`
  - `Theme`
  - `Signal_ZScore`
  - `Signal_Velocity_5D`
  - `Corr_90D`
  - `Analyst_Reasoning`
- single-leg fields:
  - `Target_Asset`
  - `Strategy`
  - `Contracts_Sized`
- two-leg fields:
  - `Directional_Bias`
  - `Strategy_GLD`
  - `Contracts_GLD`
  - second-leg strategy/contract field
- feature snapshot fields:
  - IVR, VRP, driver values

What are pair-specific extensions:

- `ZB_GC`: `DFII10`, `T10YIE`, `DTWEXBGS`
- `BZ_GC`: `IPMAN`, `CPILFESL`
- `CHF_EUR`: `EU_Risk_Spread`, `Inflation_Differential`
- `CHF_GC`: `SNB_Intervention_WoW`, `CHF_VIX_IVR`

How current artifacts map to future entities:

- `PairRun`
  - run timestamp, pair id, status, warnings, latest feature snapshot
- `Memo`
  - full analyst reasoning text, model, prompt version
- `Signal`
  - normalized directional bias, strategy shape, parsed signal fields
- `RiskTicket`
  - sizing output and assumptions
- `JournalEntry`
  - persistent operator-facing run record plus stable summary fields

What should be discarded from the CSV era:

- field-order-as-schema assumptions
- notebook-specific narrative formatting as persistence structure
- malformed aggregate `trade_journal.csv`

How legacy data should be classified:

- `journal_*.csv`
  - authoritative historical legacy journal data
- `trade_journal.csv`
  - legacy/deprecated artifact, not authoritative
- `backtest_results.csv`, `backtest_pair_summary.csv`
  - derived analytics exports, not core run/journal records

## 10. Chart and Visualization Reuse Audit

Chart families that should survive:

- core pair state
  - normalized pair lines
  - ratio
  - spread
- causal driver
  - pair-specific, thesis-defining driver views
- rolling correlation
  - regime indicator
- volatility dashboard
  - expression/risk context

Backend-generated data vs frontend-rendered visuals:

- backend should generate:
  - time-axis series payloads
  - chart titles, chart family ids, and pair-specific metadata
- frontend should render:
  - line/bar visuals
  - interactivity
  - responsive layouts

Generic vs pair-specific:

- generic chart families:
  - core
  - correlation
  - volatility
- pair-specific charts:
  - `ZB_GC`: GLD vs real yields
  - `BZ_GC`: ratio vs PMI
  - `CHF_EUR`: ratio vs EU risk and inflation differential
  - `CHF_GC`: ratio vs SNB intervention

Reusable feature payloads needed:

- spread
- ratio
- normalized legs
- rolling correlations
- IVR
- VRP
- pair-specific drivers

Is `macro_intel.reporting` adequate?

- not as the final platform chart layer
- yes as a clue to chart-family taxonomy
- `macro_intel.engine._build_chart_payloads` is closer to the real reusable backend pattern than `macro_intel.reporting.charts`

What current charts should become in the platform:

- pair dashboard components
  - all four chart families
- backend chart payload generators
  - especially core/causal/correlation/volatility payload builders
- shared frontend visualization components
  - chart containers, legends, tooltips, time-series renderers

## 11. Prompt / Memo / Signal Reuse Audit

What can be kept:

- the pair-specific prompt framing itself is valuable and should survive
- the notion of memo first, then signal extraction, is useful for operator traceability
- routed-line parsing for two-leg pairs is simple and serviceable as a transitional contract

Prompt location problem:

- prompts exist in two places:
  - richer notebook inline prompts
  - simplified package prompts in `macro_intel/llm/prompts.py`
- this is a major transition risk because notebook truth and backend truth can drift

Inline prompt extraction candidates:

- the notebook prompts should become authoritative template assets or config-bound prompt builders
- pair prompt versions should be explicit and stored with every run

Single-leg parser flow:

- current flow:
  - free-form memo
  - second LLM call with parser prompt
  - `validate_strategy_name`
- keep short term:
  - yes, as transitional compatibility
- platform-grade issue:
  - too fragile, adds latency and another failure point

Routed-line parser flow:

- current flow:
  - memo ends with two required lines
  - `parse_routed_strategies()` extracts them
- keep short term:
  - yes, this is cleaner than second-pass parsing
- platform-grade issue:
  - still string-fragile and confidence-free

Structured result expectations:

- memo payload
  - full text, prompt version, model metadata
- parsed signal payload
  - strategy family, directional bias, per-leg routes if applicable
- parse diagnostics
  - parser type, validation result, fallback usage

API-safe memo and signal payload design:

- memo should be stored/displayed as text plus metadata
- parsed signal should be normalized into explicit fields, not inferred later from prose

Runtime reliability needs:

- detect LLM offline vs timeout vs malformed response
- add parse fallback behavior with explicit warnings
- store prompt version and parser version separately

Answer to the key question:

Keep the current pair-specific memo-generation and strategy-extraction concepts, but make prompt sources authoritative, versioned, and backend-owned. The current system is good enough to carry forward the pair edge, but not good enough yet for platform-grade reliability without prompt/source unification and stricter parse contracts.

## 12. Runtime Hardening Gaps

Concrete gaps between current system and usable backend platform:

- source retries
  - FRED partial failures are tolerated, but source retry logic is inconsistent
- timeouts
  - LLM timeout is configurable, but source fetch timeouts are not uniformly managed
- result validation
  - feature outputs and chart payloads are not fully schema-validated
- schema enforcement
  - run results and journal payloads rely heavily on convention
- run error states
  - backend records `status="error"` but with coarse `error_message` only
- partial-failure handling
  - warnings exist, but there is no formal degraded-success contract
- observability
  - no structured logging, run metrics, or source-level telemetry
- rate-limit behavior
  - Yahoo mitigation exists but remains fragile and blocking
- local LLM availability handling
  - health only reports configured base URL/model, not real readiness
- deterministic outputs where required
  - single-leg parsing still requires another model call
- mixed-frequency freshness
  - SNB and macro series staleness are not surfaced explicitly
- security/runtime hygiene
  - notebooks still embed default FRED key values
- backend execution model
  - synchronous run endpoint is exposed directly to user-triggered web requests

## 13. Transition Architecture

What remains in place during transition:

- four notebooks as reference/operator surfaces
- `macro_intel` as core engine
- CSV journals as transitional journal-of-record
- FastAPI/Next.js scaffold as pilot platform surface

What gets wrapped first:

- `CHF_EUR` pair run path through backend
- `macro_intel.engine.run_pair_analysis` into a hardened service wrapper
- pair metadata and latest-run views
- current journal history adapters

What can be deferred:

- full database normalization beyond pilot run storage
- historical analog engine
- cross-pair desk intelligence page
- knowledge archive/embedding ideas from `quant.ipynb`
- backtest migration into the live platform

How notebooks continue serving as reference:

- they remain the semantic truth for pair framing until backend prompts and serializers are proven equivalent
- they remain fallback operator tools when web/backend runtime is unstable
- they remain validation surfaces when hardening changes are introduced

What should be proven before full UI rollout:

- backend outputs match notebook outputs closely for at least the pilot pair
- prompt source is unified
- run failures are explicit and actionable
- journal append path is trustworthy
- chart payloads are stable enough for frontend consumption

## 14. Reuse Recommendations by Priority

1. `macro_intel.config.pairs`
   - Why: already encodes pair identity and preserves the pair edge
   - Fit: backend metadata, orchestration, UI identity
   - Prep: extend with template/chart/serializer ids

2. `macro_intel.engine.run_pair_analysis`
   - Why: already performs end-to-end pair analysis and returns structured output
   - Fit: backend pair-run service foundation
   - Prep: harden failures, unify prompts, add validation

3. `macro_intel.features.*`
   - Why: clean deterministic logic and clear pair-specific feature functions
   - Fit: engine/core backend computations
   - Prep: settle canonical normalization policy

4. Current per-pair journal schemas and CSV histories
   - Why: they preserve real historical operator output and field semantics
   - Fit: migration mapping to platform data model
   - Prep: define canonical core entities plus pair-specific extensions

5. Notebook pair prompt framing
   - Why: richest current source of the actual intelligence edge
   - Fit: backend prompt templates and memo schema
   - Prep: extract/version without flattening pair differences

6. Existing backend scaffold
   - Why: proves the platform boundary and already wraps the engine
   - Fit: pilot FastAPI surface
   - Prep: fix correctness gaps, add async/job handling, tighten schemas

7. Existing frontend scaffold
   - Why: strong concept map for dashboard/pair/journal/status pages
   - Fit: UX prototype and IA reference
   - Prep: evolve around hardened backend outputs rather than notebook assumptions

## 15. Blockers and Risks

- runtime instability from Yahoo Finance
- Ollama dependency and local model availability
- prompt truth split between notebooks and `macro_intel.llm.prompts`
- pair-specific journal drift
- lack of one canonical structured run object persisted end-to-end
- backtest/live semantic mismatch from rolling vs full-sample normalization
- notebook logic still acting as semantic reference truth
- synchronous backend run execution under slow data/LLM conditions
- JSON-blob-heavy persistence masking schema drift
- hidden correctness issues in the early backend scaffold
  - example: `backend/app/services/journal_service.py` uses `datetime.utcnow()` without importing `datetime`
- stale/weekly macro series not surfaced clearly in pair state
- risk of over-generalizing pair logic and erasing sovereign-risk / haven / intervention framing

## 16. Recommended Immediate Next Steps

The next phase should not be “build the full app.” It should be a tight platform-foundation package with four concrete deliverables:

1. Make prompt truth authoritative
   - extract the notebook-rich pair prompts into versioned backend-owned templates/config
   - remove the notebook/package prompt split

2. Formalize the canonical pair run contract
   - define structured schemas for `PairRun`, `Memo`, `Signal`, `RiskTicket`, and `JournalEntry`
   - make `macro_intel.engine` emit that contract explicitly

3. Harden one pilot pair end-to-end
   - use `CHF_EUR` first because it already has the strongest migrated runtime proof
   - prove notebook/backend parity for state, memo, parsed signal, sizing, charts, and journal preview

4. Convert CSV journaling into transitional compatibility, not primary architecture
   - keep reading/writing current journal CSVs during transition
   - add normalized database-backed records as the platform source of truth

If those four steps are completed first, the Next.js + FastAPI platform can grow on a stable intelligence core without losing the pair-specific edge that gives the suite its identity.
