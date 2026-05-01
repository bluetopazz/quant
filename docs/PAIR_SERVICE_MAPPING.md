# PAIR_SERVICE_MAPPING.md

## 1. Purpose

This document maps each of the four current pairs into explicit platform responsibilities.

For each pair it defines what belongs in:

- pair config
- backend service logic
- prompt/template assets
- chart payload builders
- journal serializers
- frontend page sections

The goal is to preserve the edge of each pair explicitly rather than hiding it inside vague abstractions.

## 2. Mapping Rules

- shared platform layers should only absorb what is genuinely common
- pair-specific causal framing must remain explicit
- chart families can be shared, but pair driver definitions cannot be flattened
- signal style and prompt style should remain pair-owned
- invalidation and “what changed” should be pair-aware from the start

## 3. Shared Platform Layers

### Shared pair config concerns

- `pair_id`
- `notebook_name`
- `theme`
- `relationship`
- `yfinance_tickers`
- `fred_series_ids`
- `external_apis`
- `prompt_style`
- `parser_style`
- `signal_shape`
- `chart_metadata`
- `journal_schema_id`
- `feature_flags`

### Shared backend service concerns

- request validation
- source fetching orchestration
- shared feature computation
- result persistence
- memo generation transport
- chart payload serialization
- journal preview creation

### Shared frontend sections

- pair header
- current state block
- chart stack
- memo section
- signal section
- sizing section
- history section
- run controls

## 4. `ZB_GC` Mapping

### Pair identity

- thesis: sovereign confidence vs hard-asset refuge
- core question: is the market preferring sovereign duration safety or hard-asset monetary insurance?

### Pair config

Must remain explicit:

- pair code: `ZB_GC`
- theme: `Sovereign_Risk`
- relationship: `GLD over TLT`
- market tickers: `GLD`, `TLT`
- macro drivers:
  - `DFII10`
  - `T10YIE`
  - `DTWEXBGS`
  - `GVZCLS`
  - `VIXCLS`
- signal style: `single_strategy`
- prompt style: `single_leg`
- target-asset rule:
  - sign of `GLD_TLT_Spread_Norm` picks `GLD` or `TLT`

Can be shared:

- base feature pipeline
- single-strategy parse flow
- single-leg sizing pipeline

### Backend service logic

Must remain explicit:

- target-asset selection from spread sign
- sovereign-risk regime framing from spread, velocity, and correlation
- driver emphasis on real yields and inflation credibility

Can be shared:

- data fetch orchestration
- core feature build sequence
- memo transport
- single-strategy risk sizing

### Prompt/template assets

Must remain explicit:

- sovereign-risk framing
- hard-asset vs duration preference language
- real-yield and inflation-expectation context
- target-asset-aware prompt branch

### Chart payload builders

Chart families:

- core normalized pair
- pair ratio
- normalized spread
- causal driver: `GLD` vs `DFII10`
- correlation
- volatility dashboard

Must remain explicit:

- causal chart title and interpretation
- Treasury-vol proxy semantics

### Journal serializer

Shared core:

- date
- pair
- theme
- signal z-score
- velocity
- correlation
- memo

Pair extensions:

- `Target_Asset`
- `Strategy`
- `Contracts_Sized`
- `GLD_IVR`
- `TLT_IVR`
- `GLD_VRP`
- `TLT_VRP`
- `DFII10`
- `T10YIE`
- `DTWEXBGS`

### Frontend page sections

- pair summary
- state/regime
- sovereign-risk driver section
- memo
- strategy + target asset
- sizing
- history

### Invalidation candidates

- real-yield reversal
- inflation-credibility normalization
- Treasury demand reassertion
- broad USD impulse overwhelming the pair

### Delta / “what changed” candidates

- change in spread z-score
- change in `Corr_90D`
- change in `DFII10`
- change in target asset selection
- change in selected strategy

## 5. `BZ_GC` Mapping

### Pair identity

- thesis: growth-vs-haven / inflation-stress vs defensive demand
- core question: is the macro impulse growth/inflationary or defensive/stress-driven?

### Pair config

Must remain explicit:

- pair code: `BZ_GC`
- theme: `Growth_vs_Haven`
- relationship: `GLD over BNO`
- market tickers: `GLD`, `BNO`
- macro drivers:
  - `IPMAN`
  - `CPILFESL`
  - `GVZCLS`
  - `OVXCLS`
- signal style: `pair_routed`
- prompt style: `two_leg`
- directional-bias rule from `GLD_BNO_Spread_Norm`

Can be shared:

- routed parse flow
- pair sizing split

### Backend service logic

Must remain explicit:

- recession vs stagflation vs inflation/geo interpretation
- directional bias:
  - `Long GLD / Short BNO`
  - or inverse
- routed per-leg strategy output

Can be shared:

- base pair-run lifecycle
- routed strategy parse helper
- paired sizing heuristic

### Prompt/template assets

Must remain explicit:

- growth-vs-haven framing
- PMI threshold significance
- inflation/growth interaction
- two-line routed strategy requirement

### Chart payload builders

Chart families:

- core normalized pair
- ratio
- spread
- causal driver: `GLD_BNO_Ratio` vs `IPMAN`
- correlation
- volatility dashboard

Must remain explicit:

- correlation interpretation:
  - negative = recession-like
  - positive = inflation/geo-like

### Journal serializer

Shared core:

- core journal fields

Pair extensions:

- `Directional_Bias`
- `Strategy_GLD`
- `Contracts_GLD`
- `Strategy_BNO`
- `Contracts_BNO`
- `GLD_IVR`
- `BNO_IVR`
- `GLD_VRP`
- `BNO_VRP`
- `IPMAN`
- `CPILFESL`

### Frontend page sections

- pair summary
- macro regime section
- two-leg signal block
- per-leg sizing block
- growth/inflation causal driver section
- history

### Invalidation candidates

- PMI reacceleration against haven thesis
- oil supply normalization
- inflation impulse decoupling from growth slowdown
- correlation regime flipping back

### Delta / “what changed” candidates

- change in spread z-score
- change in `IPMAN`
- change in `Corr_90D`
- directional bias flip
- change in either leg’s routed strategy

## 6. `CHF_EUR` Mapping

### Pair identity

- thesis: European fragmentation vs convergence and Swiss credibility
- core question: is Europe converging or fragmenting, and is Swiss credibility reasserting itself over Euro risk?

### Pair config

Must remain explicit:

- pair code: `CHF_EUR`
- theme: `European_Divergence`
- relationship: `FXF over FXE`
- market tickers: `FXF`, `FXE`
- macro drivers:
  - Italy/Germany yield spread proxy
  - Swiss vs Euro inflation differential
  - `VIXCLS`
- signal style: `single_strategy`
- prompt style: `single_leg`
- target-asset semantics:
  - `FXE (via Short EUR)`
  - `FXE (via Long EUR)`

Can be shared:

- base single-strategy flow

### Backend service logic

Must remain explicit:

- strong divergence vs correlated broad-USD chop classification
- directional semantics preserved through EUR expression
- dual-driver causal logic:
  - EU stress
  - policy/inflation differential

Can be shared:

- fetch/build orchestration
- single-strategy parse flow
- single-leg sizing

### Prompt/template assets

Must remain explicit:

- CHF/EUR divergence framing
- EUR-targeted signal semantics
- broad-USD vs genuine divergence distinction

### Chart payload builders

Chart families:

- core normalized pair
- ratio
- spread
- causal driver 1: ratio vs `EU_Risk_Spread`
- causal driver 2: ratio vs `Inflation_Differential`
- correlation
- volatility dashboard

Must remain explicit:

- dual-driver chart grouping
- high correlation as broad-USD regime
- falling correlation as genuine divergence

### Journal serializer

Shared core:

- standard journal core

Pair extensions:

- `Target_Asset`
- `Strategy`
- `Contracts_Sized`
- `VIX_IVR`
- `FXE_VRP`
- `FXF_VRP`
- `EU_Risk_Spread`
- `Inflation_Differential`

### Frontend page sections

- pair summary
- current state
- EU stress driver section
- policy differential driver section
- memo
- signal
- sizing
- history

### Invalidation candidates

- EU spread compression
- inflation differential narrowing
- broad USD move dominating local Europe signal
- ECB repricing removing divergence pressure

### Delta / “what changed” candidates

- change in spread z-score
- change in `EU_Risk_Spread`
- change in `Inflation_Differential`
- change in correlation regime
- target-asset or strategy change

## 7. `CHF_GC` Mapping

### Pair identity

- thesis: managed fiat haven vs unmanaged monetary haven
- core question: in haven regimes, does capital prefer managed fiat credibility or unmanaged monetary neutrality?

### Pair config

Must remain explicit:

- pair code: `CHF_GC`
- theme: `Managed_vs_Unmanaged_Haven`
- relationship: `FXF over GLD`
- market tickers: `FXF`, `GLD`
- external API: `SNB`
- macro drivers:
  - `SNB_Sight_Deposits`
  - `SNB_Intervention_WoW`
  - `DFII10`
- signal style: `pair_routed`
- prompt style: `two_leg`

Can be shared:

- paired run orchestration
- routed parse flow
- paired sizing heuristic

### Backend service logic

Must remain explicit:

- intervention active/inactive interpretation
- correlated haven vs haven-divergence logic
- directional bias from `CHF_GLD_Spread_Norm`

Can be shared:

- standard run lifecycle
- routed parse helper
- chart payload serialization

### Prompt/template assets

Must remain explicit:

- SNB intervention framing
- managed vs unmanaged haven ontology
- routed per-leg output requirement

### Chart payload builders

Chart families:

- core normalized pair
- ratio
- spread
- causal driver: ratio vs `SNB_Intervention_WoW`
- correlation
- volatility dashboard

Must remain explicit:

- weekly intervention freshness semantics
- correlation interpretation tied to haven co-movement vs intervention divergence

### Journal serializer

Shared core:

- standard journal core

Pair extensions:

- `Directional_Bias`
- `Strategy_GLD`
- `Contracts_GLD`
- `Strategy_FXF`
- `Contracts_FXF`
- `GLD_IVR`
- `CHF_VIX_IVR`
- `GLD_VRP`
- `FXF_VRP`
- `DFII10`
- `SNB_Intervention_WoW`

### Frontend page sections

- pair summary
- intervention status section
- haven regime section
- two-leg signal block
- two-leg sizing block
- history

### Invalidation candidates

- SNB non-intervention during expected divergence
- haven correlation re-coupling
- gold refuge demand fading while CHF strengthens
- real-yield impulse overpowering haven preference framing

### Delta / “what changed” candidates

- change in spread z-score
- change in intervention reading
- change in correlation regime
- directional bias flip
- routed strategy changes by leg

## 8. Shared vs Explicit Logic Summary

### Logic that can be generic/shared

- request validation
- source fetch orchestration shell
- common feature primitives
- chart payload object structure
- memo transport
- persistence shell
- auth/session integration
- run lifecycle/status transitions

### Logic that must remain explicit by pair

- macro thesis framing
- driver definitions
- causal chart composition
- target-asset or directional-bias semantics
- parser style
- journal extension fields
- invalidation candidates
- delta explanation candidates

## 9. Signal Style Summary

| Pair | Signal Style | Prompt Style | Parser Style | Key Explicit Semantic |
| --- | --- | --- | --- | --- |
| `ZB_GC` | `single_strategy` | `single_leg` | second-pass parser | target asset selected from spread sign |
| `BZ_GC` | `pair_routed` | `two_leg` | routed lines | per-leg strategy routing |
| `CHF_EUR` | `single_strategy` | `single_leg` | second-pass parser | EUR-targeted directional semantics |
| `CHF_GC` | `pair_routed` | `two_leg` | routed lines | intervention-aware haven routing |

## 10. Frontend Section Summary by Pair

### Shared sections

- summary
- state
- charts
- memo
- signal
- sizing
- history
- run controls

### Pair-specific emphasis

- `ZB_GC`
  - sovereign confidence
  - real-yield driver
- `BZ_GC`
  - growth/inflation regime and two-leg routing
- `CHF_EUR`
  - EU stress vs policy differential
- `CHF_GC`
  - intervention state and haven divergence

## 11. Immediate Implementation Guidance

The next implementation phase should use this mapping to:

1. keep shared objects generic only where justified
2. encode pair-specific logic in explicit service/prompt/chart/serializer modules
3. use `CHF_EUR` as the first full pilot while preserving the mapping for the other three pairs
