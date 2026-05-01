# PAIR_RUN_CONTRACT.md

## 1. Purpose

This document defines the canonical structured object model for the Macro Relative-Value Intelligence Suite.

It is the contract between:

- `macro_intel`
- the FastAPI backend
- the Next.js frontend

It is intentionally pair-centric. It does not flatten pair-specific logic into a generic asset-analysis schema.

## 2. Contract Principles

- `macro_intel` is the intelligence engine and should emit structured pair-run objects
- FastAPI should orchestrate, validate, persist, and expose those objects without re-inventing pair logic
- Next.js should render the objects and trigger runs, but should not compute pair intelligence
- all pair runs should share one core contract with explicit pair-specific extension points
- degraded-success states must be first-class and not hidden inside free-form warnings only

## 3. Core Object Graph

The canonical pair-run graph is:

```text
PairRunRequest
   -> PairRunStatus
   -> PairRunResult
      -> FeatureSnapshot
      -> ChartPayload[]
      -> AnalystMemo
      -> ParsedSignal
      -> RiskTicket
      -> JournalEntryPreview
      -> RunWarning[]
      -> RunError?
```

## 4. `PairRunRequest`

### Purpose

Represents a user-initiated or system-initiated request to run one pair analysis.

### Required fields

- `pair_id: string`
  - canonical pair code
  - allowed values for current universe:
    - `ZB_GC`
    - `BZ_GC`
    - `CHF_EUR`
    - `CHF_GC`

### Optional fields

- `requested_by_user_id: string | null`
  - platform user identity when authenticated
- `trigger_source: string | null`
  - examples:
    - `ui_manual`
    - `api_manual`
    - `scheduled`
    - `replay`
- `persist_journal: boolean`
  - whether the platform should append journal-compatible history as part of the run flow
- `lookback_years: integer | null`
  - default engine lookback if omitted
- `as_of_date: string | null`
  - optional future backfill/replay support
- `runtime_overrides: object | null`
  - controlled overrides such as model selection or timeout profile

### Notes

- `PairRunRequest` is the API/backend trigger object
- it is not a notebook-only config object
- it should be persisted for auditability if asynchronous execution is introduced

## 5. `PairRunStatus`

### Purpose

Represents the lifecycle state of a pair run independent of full result payload availability.

### Required fields

- `run_id: string`
- `pair_id: string`
- `status: string`

### Allowed statuses

- `queued`
- `running`
- `success`
- `degraded_success`
- `error`
- `cancelled`

### Optional fields

- `created_at: string`
- `started_at: string | null`
- `completed_at: string | null`
- `progress_stage: string | null`
- `progress_message: string | null`
- `warning_count: integer`
- `error_code: string | null`

### Current-stage progress stages

- `request_accepted`
- `fetching_market_data`
- `fetching_macro_data`
- `building_features`
- `building_charts`
- `generating_memo`
- `parsing_signal`
- `sizing_risk`
- `building_journal_preview`
- `persisting_run`
- `persisting_journal`
- `complete`

## 6. `PairRunResult`

### Purpose

Represents the completed output of a pair analysis run.

### Required fields

- `run_id: string`
- `pair_id: string`
- `status: string`
- `run_timestamp: string`
- `feature_snapshot: FeatureSnapshot`
- `charts: ChartPayload[]`
- `analyst_memo: AnalystMemo | null`
- `parsed_signal: ParsedSignal | null`
- `risk_ticket: RiskTicket | null`
- `journal_entry_preview: JournalEntryPreview | null`
- `warnings: RunWarning[]`
- `error: RunError | null`

### Optional fields

- `notebook_reference: string | null`
  - source notebook identity retained for parity/reference
- `theme: string | null`
- `relationship: string | null`
- `pair_prompt_style: string | null`
- `pair_signal_style: string | null`
- `requested_by_user_id: string | null`
- `trigger_source: string | null`
- `prompt_version: string | null`
- `engine_version: string | null`
- `persistence_summary: object | null`

### Status rules

- `success`
  - all core run stages completed
  - memo, parsed signal, sizing, and journal preview are present
- `degraded_success`
  - a usable run completed, but one or more non-fatal issues occurred
  - examples:
    - some FRED series missing, but pair still computed
    - chart payload missing one secondary series
    - journal append skipped after successful run persistence
- `error`
  - pair run did not reach a usable result state

## 7. `FeatureSnapshot`

### Purpose

Represents the current state of the pair at run time.

### Required fields

- `pair_id: string`
- `as_of_date: string`
- `core_metrics: object`

### Required `core_metrics` fields

- `signal_zscore: number | null`
- `signal_velocity_5d: number | null`
- `corr_30d: number | null`
- `corr_90d: number | null`

### Optional shared fields

- `ratio: number | null`
- `spread_value: number | null`
- `left_leg_last: number | null`
- `right_leg_last: number | null`
- `normalization_mode: string`
  - examples:
    - `full_sample_zscore`
    - `rolling_zscore`
- `source_freshness: object | null`

### Pair-specific extension fields

#### `ZB_GC`

- `dfii10: number | null`
- `t10yie: number | null`
- `dtwexbgs: number | null`
- `gld_ivr: number | null`
- `tlt_ivr: number | null`
- `gld_vrp: number | null`
- `tlt_vrp: number | null`
- `target_asset_candidate: string | null`

#### `BZ_GC`

- `ipman: number | null`
- `cpilfesl: number | null`
- `gld_ivr: number | null`
- `bno_ivr: number | null`
- `gld_vrp: number | null`
- `bno_vrp: number | null`
- `directional_bias_candidate: string | null`

#### `CHF_EUR`

- `eu_risk_spread: number | null`
- `inflation_differential: number | null`
- `vix_ivr: number | null`
- `fxe_vrp: number | null`
- `fxf_vrp: number | null`
- `target_asset_candidate: string | null`
- `directional_bias_candidate: string | null`

#### `CHF_GC`

- `snb_intervention_wow: number | null`
- `dfii10: number | null`
- `gld_ivr: number | null`
- `chf_vix_ivr: number | null`
- `gld_vrp: number | null`
- `fxf_vrp: number | null`
- `directional_bias_candidate: string | null`

## 8. `ChartPayload`

### Purpose

Represents one backend-generated chart data object for frontend rendering.

### Required fields

- `chart_id: string`
- `pair_id: string`
- `family: string`
- `title: string`
- `render_kind: string`
- `x_axis: object`
- `series: object[]`

### Allowed `family` values

- `core_normalized`
- `core_ratio`
- `core_spread`
- `causal_driver`
- `correlation`
- `volatility`
- `delta` later
- `history` later

### Allowed `render_kind` values

- `line`
- `bar`
- `dual_axis_line`
- `dual_axis_split`

### `x_axis`

- `label: string`
- `values: string[]`

### `series[]`

Each series object requires:

- `series_id: string`
- `label: string`
- `values: array<number | null>`

Optional:

- `axis: string | null`
  - `left`
  - `right`
- `unit: string | null`
- `color_hint: string | null`

### Notes

- backend owns semantic chart definition
- frontend owns visual rendering
- chart payloads should remain pair-aware, not generic data dumps

## 9. `AnalystMemo`

### Purpose

Represents the narrative memo produced by the intelligence engine.

### Required fields

- `memo_id: string`
- `pair_id: string`
- `content: string`
- `model_name: string`
- `prompt_version: string`

### Optional fields

- `prompt_style: string | null`
- `prompt_template_id: string | null`
- `system_role: string | null`
- `temperature: number | null`
- `timeout_seconds: integer | null`
- `generated_at: string`
- `source_summary: object | null`

### Memo metadata requirements

- every memo must preserve:
  - model identity
  - prompt version
  - prompt style
- memo provenance must be traceable to the exact pair prompt used

## 10. `ParsedSignal`

### Purpose

Represents the normalized machine-readable strategy interpretation of the memo.

### Required fields

- `pair_id: string`
- `signal_style: string`
- `parser_style: string`
- `parser_version: string`
- `parse_status: string`

### Allowed `signal_style` values

- `single_strategy`
- `pair_routed`

### Allowed `parse_status` values

- `parsed`
- `parsed_with_fallback`
- `not_parsed`

### Shared optional fields

- `directional_bias: string | null`
- `confidence: string | null`
- `notes: string | null`

### Single-strategy fields

- `target_asset: string | null`
- `strategy: string | null`

### Pair-routed fields

- `left_leg_label: string | null`
- `right_leg_label: string | null`
- `left_strategy: string | null`
- `right_strategy: string | null`

### Parser metadata

- `parser_input_memo_id: string | null`
- `used_llm_second_pass: boolean`
- `fallback_reason: string | null`
- `raw_parser_output: string | null`

### Pair-specific semantics

- `ZB_GC`
  - single-strategy
  - `target_asset` maps to `GLD` or `TLT`
- `CHF_EUR`
  - single-strategy
  - `target_asset` preserves current `FXE (via Short EUR)` / `FXE (via Long EUR)` semantics
- `BZ_GC`
  - pair-routed
  - routes remain explicit by leg
- `CHF_GC`
  - pair-routed
  - routes remain explicit by leg

## 11. `RiskTicket`

### Purpose

Represents the structured output of the platform sizing heuristic.

### Required fields

- `pair_id: string`
- `sizing_mode: string`
- `account_value_assumption: number`
- `risk_bps_per_trade: number`

### Shared optional fields

- `total_risk_budget_usd: number | null`
- `sizing_status: string`
- `notes: string | null`

### Single-strategy fields

- `target_asset: string | null`
- `strategy: string | null`
- `contracts: integer | null`
- `risk_budget_usd: number | null`

### Pair-routed fields

- `left_strategy: string | null`
- `right_strategy: string | null`
- `left_contracts: integer | null`
- `right_contracts: integer | null`
- `per_leg_budget_usd: number | null`
- `total_budget_usd: number | null`

### Sizing metadata

- `strategy_risk_table_version: string | null`
- `heuristic_name: string | null`
- `sizing_assumptions: object | null`

### Notes

- this is an idea-sizing object, not an execution-ready order ticket

## 12. `JournalEntryPreview`

### Purpose

Represents the exact journal-compatible record that would be persisted if the run is journaled.

### Required fields

- `pair_id: string`
- `journal_schema_version: string`
- `journal_mode: string`
- `preview_payload: object`

### Allowed `journal_mode` values

- `csv_legacy_compatible`
- `db_native`
- `dual_write`

### Shared semantics

- `preview_payload` must preserve current field meaning, not just field names
- field order may matter only for legacy CSV compatibility, not for canonical DB models

### Pair-specific preview payload expectations

- `ZB_GC`
  - includes `Target_Asset` and single-strategy fields
- `BZ_GC`
  - includes `Directional_Bias`, `Strategy_GLD`, `Strategy_BNO`, per-leg contracts
- `CHF_EUR`
  - includes current target-asset semantics and key driver fields
- `CHF_GC`
  - includes intervention and two-leg fields

### Journal-preview semantics

- a preview is created during a successful or degraded-success run
- a preview is not proof that persistence happened
- the persistence outcome should be tracked separately in run metadata/status

## 13. `RunWarning`

### Purpose

Represents a non-fatal issue encountered during the run.

### Required fields

- `warning_code: string`
- `stage: string`
- `message: string`

### Optional fields

- `source: string | null`
- `field: string | null`
- `severity: string | null`
- `recoverable: boolean`

### Typical warning categories

- partial data-source failure
- stale macro series
- parser fallback used
- journal append skipped
- missing secondary chart series

## 14. `RunError`

### Purpose

Represents a fatal run failure.

### Required fields

- `error_code: string`
- `stage: string`
- `message: string`

### Optional fields

- `source: string | null`
- `retryable: boolean`
- `details: object | null`

### Suggested error codes

- `PAIR_NOT_FOUND`
- `MARKET_DATA_UNAVAILABLE`
- `MACRO_DATA_UNAVAILABLE`
- `SNB_DATA_UNAVAILABLE`
- `FEATURE_BUILD_FAILED`
- `CHART_BUILD_FAILED`
- `LLM_UNAVAILABLE`
- `MEMO_GENERATION_FAILED`
- `SIGNAL_PARSE_FAILED`
- `RISK_SIZING_FAILED`
- `JOURNAL_PREVIEW_FAILED`
- `RUN_PERSIST_FAILED`

## 15. Pair-Specific Extension Model

The platform should use one core contract plus pair-specific extension groups.

Recommended pattern:

- `FeatureSnapshot.core_metrics`
- `FeatureSnapshot.pair_extensions`
- `JournalEntryPreview.preview_payload`
- `ParsedSignal` fields determined by signal style

Pair-specific extensions must remain explicit and versioned. They should not be hidden inside unnamed JSON blobs without schema ownership.

## 16. Status Transitions

Canonical lifecycle:

```text
queued
  -> running
     -> success
     -> degraded_success
     -> error
     -> cancelled
```

### Transition rules

- `queued -> running`
  - request accepted and execution started
- `running -> success`
  - all critical run stages completed
- `running -> degraded_success`
  - core result usable, but one or more non-fatal issues remain
- `running -> error`
  - no usable pair result available
- `running -> cancelled`
  - operator or system cancellation

## 17. Degraded-Success Behavior

Degraded success is required when:

- the operator can still inspect a useful pair state
- memo/signal/risk/journal-preview are still present or intentionally downgraded with clear warnings

Examples:

- some non-critical source series failed, but required pair features still built
- journal append failed after result persistence
- one chart family failed while others succeeded

Degraded success should not be used when:

- the pair state itself cannot be trusted
- core features are missing
- memo generation failed and there is no valid fallback behavior defined

## 18. Recommended FastAPI / `macro_intel` / Next.js Boundary

### `macro_intel`

Should emit:

- `FeatureSnapshot`
- `ChartPayload[]`
- `AnalystMemo`
- `ParsedSignal`
- `RiskTicket`
- `JournalEntryPreview`
- warning/error details

### FastAPI

Should add:

- `PairRunRequest`
- `PairRunStatus`
- persistence ids
- auth context
- API serialization

### Next.js

Should consume:

- `PairRunStatus`
- `PairRunResult`
- charts
- memo
- parsed signal
- sizing
- journal preview/history

## 19. Immediate Adoption Guidance

The next implementation phase should:

1. refit `macro_intel.engine.PairRunResult` to match this contract
2. split current wide JSON fields in backend persistence by logical object
3. make `CHF_EUR` the first pair to conform fully end-to-end
