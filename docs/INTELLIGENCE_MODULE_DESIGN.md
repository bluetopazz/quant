# INTELLIGENCE_MODULE_DESIGN.md

## 1. Executive Summary

The intelligence module is the platform’s always-on observatory layer. It turns the suite from a run-triggered analysis surface into a persistent desk-state view that is useful immediately at login.

Unlike the current pair command-center pages, this module is not centered on a single fresh run. It is centered on persisted state: latest pair states, recent pair trajectories, cross-pair coupling, and change summaries derived from the platform’s existing run history.

In the platform, it fits beside the pair pages:

- pair pages answer “run this pair and inspect it deeply”
- the intelligence page answers “what is the four-pair system doing right now, what changed, and where should I focus first?”

## 2. Current Platform Capabilities Relevant to Intelligence Mode

- Current backend outputs already available:
  - canonical `PairRunResult`
  - persisted feature snapshots
  - persisted parsed signals
  - persisted risk tickets
  - persisted chart payloads
  - persisted run history by pair
- Current persistence already available:
  - `pair_runs`
  - `pair_run_feature_snapshots`
  - `pair_run_memos`
  - `pair_run_signals`
  - `pair_run_risk_tickets`
  - `pair_run_chart_payloads`
  - `journal_entries`
- `macro_intel` reuse:
  - feature snapshot metrics already contain usable state coordinates
  - pair-specific extension metrics already preserve pair ontology
  - parsed signal output already provides directional and confidence context
- Frontend concept reuse:
  - dashboard proves multi-pair summary layout
  - pair page proves charts/memo/signal/risk presentation
  - existing styling and `recharts` dependency are sufficient for MVP 2D state-space views
- Current snapshot population path before this upgrade:
  - intelligence state was derived mostly from previously persisted successful pair runs
  - `/intelligence` could materialize observatory state on read, but did not have a real refresh lifecycle
  - stale coverage therefore reflected run recency more than desk recency
- What can be reused directly:
  - persisted `feature_snapshot_json` from pair runs
  - persisted parsed signal confidence and directional bias
  - per-pair latest/previous run history for delta calculations
  - existing pair metadata and ontology from `macro_intel.config.pairs`
- What was missing:
  - background or operator-triggerable refresh job
  - persisted refresh status and warnings
  - a best-available fallback path when the latest run failed
  - explicit desk freshness and degraded-state semantics

## 3. Intelligence Questions the Module Should Answer

- What is the desk signaling right now?
- What is the current state of each pair?
- Which pair is most unusual?
- Which pair has changed most?
- Are pairs coherent or fragmented?
- What regime is the system in?
- What deserves attention?
- Which persisted states are stale versus fresh?

## 4. State Model

### `PairStateSnapshot`

- Purpose:
  - current pair-local state for observatory use
- Fields:
  - pair id, source run id, timestamps
  - spread z-score
  - spread velocity
  - rolling correlations
  - ratio/spread values
  - directional bias
  - confidence
  - regime label
  - vol regime
  - primary and secondary driver
  - attention score
  - staleness status
  - pair-specific extensions
- Computation:
  - derived from latest persisted successful/degraded pair run
- Persisted:
  - yes
- Backend ownership:
  - `backend.app.services.intelligence_service`

### `DeskStateSnapshot`

- Purpose:
  - desk-level summary of the four-pair system
- Fields:
  - dominant regime
  - coherence score
  - fragmentation score
  - stress score
  - state dispersion
  - attention pair
  - coverage ratio
  - stale pair ids
  - freshness status
  - degraded flag
  - latest refresh status
  - short desk history trail
  - embedded change summaries and attention flags
- Computation:
  - derived from current pair state snapshots
- Persisted:
  - yes
- Backend ownership:
  - `backend.app.services.intelligence_service`

### `PairTrajectoryPoint`

- Purpose:
  - historical motion of one pair through state space
- Fields:
  - pair id
  - run id
  - timestamp
  - x = pair-aware state coordinate
  - y = pair-aware state coordinate
  - color = sequence index
  - regime label
  - region label
  - motion label
  - axis labels
  - current-point marker
  - directional bias
  - confidence
- Computation:
  - derived from persisted pair-run history
- Persisted:
  - no for MVP; derived on read from existing runs
- Backend ownership:
  - `backend.app.services.intelligence_service`

### `CouplingSnapshot`

- Purpose:
  - quantify how similar the four pair states are right now
- Fields:
  - pair ids
  - similarity matrix
  - coherence score
  - fragmentation score
- Computation:
  - Euclidean-distance-based similarity over `[z-score, velocity, corr_90d]`
- Persisted:
  - yes
- Backend ownership:
  - `backend.app.services.intelligence_service`

### `ChangeSummary`

- Purpose:
  - summarize what changed versus the previous persisted run
- Fields:
  - pair id
  - z-score delta
  - velocity delta
  - correlation delta
  - biggest driver delta
  - timestamp
  - attention score
- Computation:
  - compare latest and previous persisted pair runs
- Persisted:
  - embedded inside desk snapshot summary for MVP
- Backend ownership:
  - `backend.app.services.intelligence_service`

### `AttentionFlag`

- Purpose:
  - identify what deserves operator attention now
- Fields:
  - pair id
  - severity
  - title
  - reason
  - optional metric key/value
- Computation:
  - attention score ranking, staleness checks, and biggest change checks
- Persisted:
  - embedded inside desk snapshot summary for MVP
- Backend ownership:
  - `backend.app.services.intelligence_service`

### `RefreshStatus`

- Purpose:
  - expose whether observatory freshness comes from a recent successful refresh cycle or from fallback persisted runs
- Fields:
  - refresh id
  - trigger source
  - lifecycle timestamps
  - per-pair success / degraded / failure counts
  - warning count and warning messages
  - terminal error message if the refresh cycle failed
- Computation:
  - derived from `IntelligenceRefreshJob`
- Persisted:
  - yes
- Backend ownership:
  - `backend.app.services.intelligence_service`

## 5. Candidate State Variables

- Shared core variables:
  - `signal_zscore`
  - `signal_velocity_5d`
  - `corr_30d`
  - `corr_90d`
  - ratio
  - spread value
- `ZB_GC`
  - `dfii10`
  - `t10yie`
  - `dtwexbgs`
  - `gld_ivr`, `tlt_ivr`
  - `gld_vrp`, `tlt_vrp`
- `BZ_GC`
  - `ipman`
  - `cpilfesl`
  - `gld_ivr`, `bno_ivr`
  - `gld_vrp`, `bno_vrp`
- `CHF_EUR`
  - `eu_risk_spread`
  - `inflation_differential`
  - `vix_ivr`
  - `fxe_vrp`, `fxf_vrp`
- `CHF_GC`
  - `snb_intervention_wow`
  - `dfii10`
  - `gld_ivr`
  - `chf_vix_ivr`
  - `gld_vrp`, `fxf_vrp`
- Pair-specific trajectory coordinate choices for the upgraded observatory:
  - `ZB_GC`
    - x = `signal_zscore`
    - y = `dfii10`
    - why: the observatory should show whether sovereign-confidence stress is pushing the pair away from its norm while real yields confirm or resist the move
  - `BZ_GC`
    - x = `signal_zscore`
    - y = `ipman`
    - why: this keeps growth-vs-haven logic explicit instead of treating crude/gold as a generic spread
  - `CHF_EUR`
    - x = `eu_risk_spread`
    - y = `inflation_differential`
    - why: Europe fragmentation vs Swiss credibility is best read through these causal coordinates, not just raw spread motion
  - `CHF_GC`
    - x = `signal_zscore`
    - y = `snb_intervention_wow`
    - why: the pair’s defining question is managed vs unmanaged haven preference, so intervention pressure must stay visible in state space

## 6. Desk-Level Derived Metrics

- coherence score
  - average off-diagonal state similarity
- fragmentation score
  - `1 - coherence`
- stress score
  - average of absolute z-score plus absolute velocity
- dominant regime
  - most common pair regime label across the four pairs
- attention pair
  - highest current attention score
- state dispersion
  - average pairwise distance in state space
- pair coupling matrix
  - similarity matrix over current pair state vectors
- desk regime summary definition
  - computed as the mode of current pair regime labels, with tie-breaks resolved by the highest aggregate attention score among tied regimes
- coherence / fragmentation definition
  - coherence measures average similarity across pair state vectors
  - fragmentation is `1 - coherence` and is elevated when the desk tells multiple inconsistent macro stories simultaneously
- attention flag framework
  - pair-local attention comes from large absolute displacement, large recent delta, elevated volatility/risk context, and staleness penalties
  - desk-level attention additionally fires when fragmentation spikes or coverage degrades
- change-summary framework
  - compare the latest usable pair run to the immediately prior usable run
  - surface largest z-score move, velocity change, regime shift, and dominant driver movement
  - roll pair-level changes into one desk “what changed” panel for login-time usefulness

## 7. Visualization Model

### Pair state matrix

- Purpose:
  - compact view of all four current pair states
- Data needed:
  - `PairStateSnapshot[]`
- Responsibility:
  - backend computes state
  - frontend renders cards/matrix
- MVP:
  - yes

### Pair trajectory / state-space charts

- Purpose:
  - show motion through state space over recent runs
- Data needed:
  - `PairTrajectoryPoint[]`
- Responsibility:
  - backend derives trajectory points
  - frontend renders scatter charts
- MVP:
  - yes

### Cross-pair coupling view

- Purpose:
  - show coherence vs fragmentation and pair-to-pair similarity
- Data needed:
  - `CouplingSnapshot`
- Responsibility:
  - backend computes matrix
  - frontend renders heatmap/table
- MVP:
  - yes

### Traditional market views

- Purpose:
  - remain accessible from pair pages, not duplicated in full here
- Data needed:
  - existing chart payloads
- Responsibility:
  - existing pair pages
- MVP:
  - partial only; observatory focuses on state and change first

### Change monitor

- Purpose:
  - show recent deltas and attention cues immediately on login
- Data needed:
  - `ChangeSummary[]`, `AttentionFlag[]`
- Responsibility:
  - backend computes
  - frontend renders
- MVP:
  - yes

Plotting choice for MVP:

- library: `recharts`
- why:
  - already in the repo
  - sufficient for readable 2D scatter/state-space views
  - low integration risk
  - matches the current frontend stack
- views powered:
  - pair trajectory small multiples
- observatory upgrade views powered:
  - regime-colored trajectory points
  - desk trend strip for coherence / fragmentation / stress through recent snapshots
- coupling heatmap:
  - rendered with standard HTML/CSS for clarity and zero extra dependency risk
- cross-pair system-view design:
  - MVP uses a coupling heatmap plus desk trend strip
  - the heatmap answers “are the four pairs aligned right now?”
  - the desk trend strip answers “is coherence improving or breaking down through recent snapshots?”

## 8. Snapshot Refresh Model

- Freshness model:
  - `fresh`: latest successful refresh is within the configured observatory window and full desk coverage is available
  - `watch`: usable snapshots exist, but some pairs are aging or the latest refresh was incomplete
  - `stale`: the desk is relying on clearly old pair state or materially incomplete coverage
- Snapshot ownership:
  - pair state snapshot generation: `backend.app.services.intelligence_service.refresh_intelligence_snapshots`
  - desk state snapshot generation: same service
  - coupling snapshot generation: same service
  - refresh orchestration and job tracking: `trigger_intelligence_refresh` / `_run_refresh_cycle`
- Current upgraded model:
  - read-through observatory assembly still exists
  - plus a lightweight refresh job that can re-run all four pairs without visiting pair pages
- background refresh vs on-demand:
  - on-demand manual refresh is exposed now
  - optional background loop is enabled by backend config for periodic refresh
- snapshot cadence:
  - configurable interval, defaulting to a lightweight periodic desk refresh rather than per-request live recomputation
- source of truth:
  - pair runs remain the source of analytical state
  - intelligence snapshots are observatory-oriented derived persistence
- stale/partial handling:
  - pair states are marked `fresh`, `watch`, or `stale`
  - latest usable successful/degraded pair run can be reused if the newest run failed
  - refresh jobs persist warnings and failed pairs
  - coverage ratio, stale pair ids, refresh status, and degraded flags are surfaced to the UI
- login usefulness:
  - page is useful immediately if the platform has persisted runs
  - if the desk is stale, the page can trigger a lightweight refresh path
  - if no runs exist, the module still reports missing coverage cleanly instead of hiding the desk state
- degraded-state handling:
  - a partial refresh must never blank the page
  - best available prior usable state is preserved
  - the desk header explicitly reports degraded freshness, warning messages, and failed pair counts

## 9. MVP Scope

- persisted `PairStateSnapshot`
- persisted `DeskStateSnapshot`
- persisted `CouplingSnapshot`
- persisted `IntelligenceRefreshJob`
- derived trajectory points from pair-run history
- `/intelligence` backend endpoint
- `/intelligence/refresh` backend endpoint
- `/intelligence` frontend page
- desk-state header
- pair-state matrix
- trajectory small multiples
- coupling heatmap
- change monitor
- desk trend strip
- freshness indicators and degraded-state warnings

## 10. Future Extensions

- 3D state space
- analog engine
- regime strip over time
- latent system map
- lead-lag analysis
- network graph
- anomaly detection
- background scheduler / periodic snapshot job
- pair-driver delta sparklines

## 11. Recommended Implementation Plan

1. Reuse latest persisted pair runs as current-state inputs
2. Add intelligence snapshot persistence tables
3. Add refresh-job persistence and freshness semantics
4. Implement backend state derivation, change summaries, attention flags, and coupling logic
5. Expose consolidated observatory endpoints plus a manual refresh trigger
6. Build the observatory page with desk header, state matrix, state-space trajectories, coupling view, and change monitor
7. Validate page usefulness without manual pair-page runs
8. Enable lightweight background refresh only after the refresh job path is stable
