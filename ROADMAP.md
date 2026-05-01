# Roadmap

## 1. Roadmap Principles

- Preserve the current research value before changing architecture.
- Stabilize the present notebook workflow before adding new features.
- Extract shared logic only after documenting what is truly common.
- Reduce notebook duplication without removing the operator-facing notebook experience.
- Separate analysis, parsing, sizing, journaling, and backtesting concerns.
- Keep the human operator in the loop.
- Prefer repo-grounded improvements over speculative platform redesign.

## 2. Current-State Summary

The repository already contains a workable but fragile research desk:

- four pair notebooks that fetch live data, chart it, ask a local LLM for a recommendation, size a trade, and append to per-pair journals
- a backtest notebook that consumes those per-pair journals and exports a proxy PnL report
- a separate `quant.ipynb` prototype that explores a MongoDB and embeddings-based direction
- a shared `macro_intel/` package that now powers the four pair notebooks materially

Roadmap work is needed because the current system has drifted:

- live notebooks and backtest do not use exactly the same signal construction
- prompts, parsers, and journal schemas are inconsistent
- `trade_journal.csv` and `quant.ipynb` still have unresolved roles
- external runtime reliability still depends on Yahoo Finance and local Ollama behavior

### Progress Checkpoint

The following baseline work is already complete:

- current-state architecture and repository audit documentation
- migration of the four pair notebooks onto `macro_intel`
- dependency bootstrap via `requirements.txt`
- environment documentation
- partial live runtime validation
- initial FastAPI and Next.js platform scaffolding around the pair suite

The roadmap below should be read as the next hardening and cleanup sequence from that baseline.

## 3. Immediate Priorities (Phase 0)

Focus: repository clarity and operational stabilization.

### Objectives

- identify the authoritative current workflow
- remove ambiguity around artifacts
- make the repo runnable by someone other than the current author

### Work Items

- Keep `README.md`, `SYSTEM_ARCHITECTURE.md`, and the retained docs synchronized with the actual repo state.
- Remove hard-coded secrets from notebooks and replace them with documented environment variable expectations plus an `.env.example`.
- Decide the status of `trade_journal.csv`:
  - retire it
  - repair it
  - or migrate it into the newer per-pair journal scheme
- Document `quant.ipynb` explicitly as either:
  - active prototype
  - or legacy exploration
- Define which notebook-generated CSVs are source-of-truth artifacts and which are derived exports.
- Normalize notebook headers, comments, and execution instructions so users know which cells to run and in what order.

### Completion Criteria

- a new user can identify the current workflow without reading notebook internals first
- dependencies and environment assumptions are explicit
- legacy vs. current artifacts are labeled clearly

## 4. Foundation Refactor (Phase 1)

Focus: extract genuinely shared components from the four production notebooks.

### Objectives

- reduce duplication
- make logic reusable
- preserve notebook usability

### Work Items

- Continue thinning the notebooks now that `macro_intel/` exists.
- Move inline prompt text into reusable prompt templates with simple versioning.
- Push more pair-safe chart composition into shared reporting helpers.
- Add stronger schema validation around journal writes and parser outputs.
- Add tests or smoke-check helpers around the shared loaders, LLM client, and feature functions.
- Keep pair notebooks as thin orchestrators that call shared code without flattening pair-specific semantics.

### Completion Criteria

- the four pair notebooks no longer duplicate their entire scaffolding
- shared behavior lives in importable code
- notebook logic is visibly thinner and easier to compare across pairs

## 5. Systemization (Phase 2)

Focus: make the desk consistent across pairs.

### Objectives

- unify pair definitions
- unify schemas
- reduce special-case logic

### Work Items

- Introduce pair configuration objects containing:
  - pair code
  - market tickers
  - macro series
  - causal feature definitions
  - chart labels
  - journal schema extensions
  - prompt inputs
- Define one canonical journal schema with a stable core:
  - `date`
  - `pair`
  - `directional_bias`
  - `strategy_primary`
  - `strategy_secondary`
  - `contracts_primary`
  - `contracts_secondary`
  - `signal_zscore`
  - `signal_velocity_5d`
  - `corr_90d`
  - `analyst_reasoning`
  - `model_name`
  - `prompt_version`
- Normalize naming conventions across notebooks and CSVs.
- Decide whether single-leg notebooks should remain single-leg or be upgraded to explicit two-leg representations for consistency.
- Make live notebooks and backtest use the same normalization and spread construction definitions.

### Completion Criteria

- all pair notebooks write rows that conform to one shared journal contract
- pair-specific differences are declarative rather than embedded in large code blocks
- backtest input assumptions are aligned with live notebook outputs

## 6. Validation and Control (Phase 3)

Focus: make outputs more trustworthy and failures easier to diagnose.

### Objectives

- catch silent errors early
- reduce parser fragility
- improve reproducibility

### Work Items

- Add environment validation at notebook start:
  - missing API key checks
  - missing local LLM checks
  - missing MongoDB check only for `quant.ipynb` if it remains active
- Add journal schema validation before append.
- Add duplicate-row detection for journaling cells.
- Add prompt/output contract checks using stored fixture outputs.
- Add parser validation against a strict strategy enum.
- Add notebook smoke tests that exercise shared code without requiring full notebook execution.
- Add data freshness and missing-series warnings.
- Add backtest integrity checks:
  - no missing spread mappings
  - no impossible direction labels
  - explicit handling of incomplete horizon trades

### Completion Criteria

- malformed journal rows are blocked before write
- parser failures degrade clearly rather than silently
- core logic can be validated without manually opening every notebook

## 7. Expansion Readiness (Phase 4)

Focus: only after stabilization and systemization.

### Objectives

- make future growth possible without re-breaking the core desk

### Work Items

- Improve the backtest from spread-z proxy toward a more realistic trade model.
- Add non-notebook script entrypoints for:
  - data refresh
  - signal generation
  - journal validation
  - backtest runs
- Add a lightweight dashboard if still desired.
- Add paper-trade integration only after journal schema and trade expression are stable.
- Add publication/report generation if the desk is meant to support written research output.

### Completion Criteria

- expansion features consume the stabilized shared modules rather than duplicating notebook code
- new interfaces do not become another parallel architecture

## 8. Priority Matrix

| Initiative | Impact | Effort | Dependency Order | Urgency |
| --- | --- | --- | --- | --- |
| README and repo truth cleanup | High | Low | First | Immediate |
| Dependency manifest and environment cleanup | High | Low | First | Immediate |
| Journal schema decision and legacy artifact handling | High | Medium | First | Immediate |
| Shared loader / feature / LLM extraction | High | Medium | After Phase 0 | High |
| Pair configuration abstraction | High | Medium | After shared extraction | High |
| Live/backtest signal parity | High | Medium | After shared extraction | High |
| Validation and parser hardening | High | Medium | After schema unification | High |
| Dashboard / CLI / broker work | Medium | Medium to High | Last | Low until core is stable |

## 9. Risks and Failure Modes

- Over-refactoring too early could break a workflow that already produces journaled ideas.
- Cleaning up prompts without contract tests could change strategy outputs silently.
- Migrating journals without a clear schema plan could lose historical context.
- Forcing all notebooks into one abstraction too quickly could erase pair-specific edge and nuance.
- Treating `quant.ipynb` as production without deciding its role could create a second permanent architecture fork.
- Expanding into execution or dashboards before validation would amplify current hidden assumptions.

## 10. Recommended Implementation Sequence

1. Fix repo-level truth: README, artifact status, dependency manifest, environment docs.
2. Decide the fate of `trade_journal.csv` and mark or migrate legacy artifacts.
3. Define the authoritative journal schema and field naming conventions.
4. Extract shared data-loading and LLM helper code.
5. Extract shared feature-engineering and sizing code.
6. Introduce declarative pair configuration objects.
7. Refit the four pair notebooks to use shared modules while preserving their operator workflow.
8. Align backtest feature construction and journal consumption with the refactored live path.
9. Add validation, parser hardening, duplicate detection, and smoke tests.
10. Reassess whether `quant.ipynb` should be integrated, archived, or rewritten against the new shared core.
11. Only then pursue dashboard, CLI, or execution-adjacent features.

## 11. Definition of Done by Phase

### Phase 0 Done

- README matches repository reality
- dependencies are installable from repo metadata
- secrets are no longer hard-coded defaults
- current vs. legacy artifacts are clearly identified

### Phase 1 Done

- shared code exists for loaders, features, LLM, sizing, and journaling
- notebooks import common utilities instead of copying full implementations

### Phase 2 Done

- pair behavior is configured declaratively
- journal outputs conform to one stable schema
- live signal construction and backtest signal construction match conceptually and numerically

### Phase 3 Done

- parser and journal failures are validated and surfaced clearly
- notebook smoke tests or equivalent checks exist
- duplicate logs and malformed rows are prevented

### Phase 4 Done

- any new interface such as a dashboard or script entrypoint uses the stabilized shared core
- expansion features do not introduce another independent logic path
