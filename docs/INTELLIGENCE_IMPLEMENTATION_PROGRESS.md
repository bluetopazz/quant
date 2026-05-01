# INTELLIGENCE_IMPLEMENTATION_PROGRESS.md

## Step 1 — Focused review and state-model definition

- Built:
  - intelligence module design grounded in current pair-run persistence and frontend surfaces
- Files changed:
  - `docs/INTELLIGENCE_MODULE_DESIGN.md`
- State variables chosen:
  - shared core: z-score, velocity, rolling correlation, ratio, spread
  - pair-aware drivers from existing `pair_extensions`
- Visualization choice:
  - `recharts` for MVP state-space scatter views
  - HTML/CSS heatmap for coupling
- Deferred:
  - 3D/state-latent views
  - advanced network/system graphs

## Step 2 — Backend snapshot persistence

- Built:
  - `PairStateSnapshot`
  - `DeskStateSnapshot`
  - `CouplingSnapshot`
  - `IntelligenceRefreshJob`
- Files changed:
  - `backend/app/db/models.py`
- Data model changes:
  - pair-local observatory snapshot table
  - desk-level snapshot table
  - persisted coupling matrix table
  - persisted refresh job table for observatory refresh lifecycle
- Notes:
  - trajectory history is derived from existing `pair_runs` for MVP rather than duplicated into a separate trajectory table

## Step 3 — Backend intelligence services and endpoints

- Built:
  - state-derivation service
  - regime labeling
  - vol-regime labeling
  - driver ranking
  - attention scoring
  - change summaries
  - coupling matrix
  - coupling deltas vs prior snapshot
  - freshness classification
  - best-available fallback to latest usable run when newest run fails
  - manual and optional background observatory refresh
  - consolidated intelligence overview response
- Files changed:
  - `backend/app/services/intelligence_service.py`
  - `backend/app/schemas/intelligence.py`
  - `backend/app/core/config.py`
  - `backend/app/api/routes/intelligence.py`
  - `backend/app/main.py`
- Endpoints added:
  - `GET /intelligence`
  - `GET /intelligence/pairs/{pair_id}/trajectory`
  - `POST /intelligence/refresh`
- Refresh semantics added:
  - manual refresh can re-run all four pairs without opening pair pages
  - optional background loop can refresh on a configured cadence
  - partial refresh failures are persisted as warnings instead of blanking the desk
- Pair-specific behavior preserved:
  - `ZB_GC` sovereign-confidence framing
  - `BZ_GC` growth-vs-haven framing
  - `CHF_EUR` Europe divergence framing
  - `CHF_GC` SNB / managed-haven framing

## Step 4 — Frontend intelligence observatory MVP

- Built:
  - top-level `/intelligence` page
  - desk state header
  - pair state matrix
  - pair trajectory small multiples
  - coupling heatmap
  - change monitor panel
  - desk trend strip for coherence / fragmentation / stress history
  - manual desk refresh action
  - freshness and degraded-state indicators
  - auto-refresh on page load when desk state is stale or incomplete
- Files changed:
  - `frontend/app/intelligence/page.tsx`
  - `frontend/components/intelligence/DeskSystemTrend.tsx`
  - `frontend/components/intelligence/DeskStateHeader.tsx`
  - `frontend/components/intelligence/PairStateMatrix.tsx`
  - `frontend/components/intelligence/PairTrajectoryGrid.tsx`
  - `frontend/components/intelligence/CouplingHeatmap.tsx`
  - `frontend/components/intelligence/ChangeSummaryPanel.tsx`
  - `frontend/components/layout/AppShell.tsx`
  - `frontend/lib/types.ts`
  - `frontend/lib/api.ts`
  - `frontend/app/globals.css`
- Navigation added:
  - top-level `Intelligence` entry in the operator sidebar
- State-space choices implemented:
  - `ZB_GC`: `signal_zscore` vs `dfii10`
  - `BZ_GC`: `signal_zscore` vs `ipman`
  - `CHF_EUR`: `eu_risk_spread` vs `inflation_differential`
  - `CHF_GC`: `signal_zscore` vs `snb_intervention_wow`
- Interpretation upgrades:
  - regime-colored trajectory points
  - region labels
  - motion labels
  - pair-aware axis labels

## Step 5 — Runtime validation

- Validated:
  - backend python compile
  - frontend production build
  - seeded backend smoke validation against a temporary SQLite database for:
    - `POST /auth/login`
    - `GET /intelligence`
    - `POST /intelligence/refresh`
    - `GET /intelligence/pairs/CHF_EUR/trajectory`
  - degraded refresh handling with one pair failing while best available desk state remains readable
  - pair-aware trajectory payload semantics for `CHF_EUR` (`EU Risk Spread` vs `Inflation Differential`)
- Runtime proof still environment-limited:
  - full live market-data-backed observatory quality still depends on source availability during refresh
  - local refresh cadence behavior was validated in request/response form, not as a long-running production daemon soak test

## Step 6 — Observability semantics added

- Desk-level heuristics introduced:
  - dominant regime as the mode of pair regimes
  - coherence as average state similarity
  - fragmentation as `1 - coherence`
  - stress from absolute displacement plus velocity pressure
  - desk attention from pair change severity plus fragmentation degradation
- Freshness heuristics introduced:
  - `fresh`, `watch`, `stale` desk status
  - degraded desk state when refresh succeeds only partially
  - stale pair ids and refresh warnings surfaced to the frontend
- What changed layer introduced:
  - pair move deltas
  - regime-shift candidates
  - coupling delta support
  - attention-pair emphasis for login-time scanning

## Current limitations

- Background refresh is lightweight and process-local, not yet a production scheduler/worker
- Intelligence quality still depends on data-source and LLM availability during refresh
- Coupling metric remains intentionally simple and interpretable rather than fully model-based
- Traditional market chart families remain on pair pages rather than fully replicated on `/intelligence`
- State regions are heuristic phase labels, not a calibrated scientific regime model

## Intentional deferrals

- analog engine
- anomaly detector
- lead-lag system view
- 3D state space
 - network graph / latent system map
