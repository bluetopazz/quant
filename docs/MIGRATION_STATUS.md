# Migration Status

## Scope

This document is the retained status record for the notebook-to-`macro_intel` migration. It replaces the older refactor log and separate runtime-validation note.

It covers:

- what was extracted into `macro_intel`
- which notebooks are materially migrated
- what runtime validation was actually completed
- what remains unresolved

## Current State

The current pair-suite architecture is:

- operator-facing pair notebooks for review, memo generation, sizing, and journaling
- a shared `macro_intel/` package providing the reusable engine underneath those notebooks
- per-pair journal CSVs as the current journal-of-record artifacts

The four pair notebooks are materially migrated:

- `10yrgc.ipynb`
- `chfeur.ipynb`
- `crudegc.ipynb`
- `chfgc.ipynb`

Not yet migrated into the shared engine:

- `backtest.ipynb`
- `quant.ipynb`

## What Lives In `macro_intel`

Shared package layers now include:

- `macro_intel.config`
  - pair registry
  - runtime settings
- `macro_intel.data`
  - market fetch helpers
  - FRED fetch helpers
  - SNB fetch helpers
  - merge and forward-fill helpers
- `macro_intel.features`
  - normalization helpers
  - ratios and spreads
  - rolling correlations
  - historical volatility
  - IV rank
  - VRP
  - signal velocity
  - pair-specific feature builders
- `macro_intel.reporting`
  - shared chart helpers
- `macro_intel.llm`
  - local Ollama-compatible client
  - parser helpers
  - parser-prompt helpers
- `macro_intel.risk`
  - shared sizing logic
- `macro_intel.journal`
  - schema helpers
  - journal writer
  - journal reader
- `macro_intel.utils`
  - validation and date helpers

## What Still Stays In The Notebooks

The notebooks are intentionally not empty wrappers. The following still remain inline where they express actual pair semantics:

- pair-specific analyst prompt text
- pair-specific causal chart composition
- target-asset or directional-bias logic
- pair-specific journal row assembly
- notebook-local display and operator messaging

## Functional Preservation Summary

The migration preserved:

- the current pair universe and macro theses
- the current prompt styles
- both parser styles:
  - second-pass single-strategy parsing
  - routed-line two-leg parsing
- the rough sizing convention
- pair-specific journal field mappings

## Notebook Migration Summary

### `10yrgc.ipynb`

- Uses shared settings, pair config, yfinance/FRED loaders, merge logic, feature helpers, chart helpers, LLM client, parser-prompt helper, sizing helper, and journal writer.
- Preserves:
  - sovereign-risk prompt framing
  - target-asset selection semantics
  - notebook-specific causal chart
  - existing `journal_zb_gc.csv` row mapping
- Intentional fix already applied:
  - removed the broken `TYVIXCLS` prompt reference in favor of the actual proxy field path

### `chfeur.ipynb`

- Uses shared settings, pair config, yfinance/FRED loaders, merge logic, feature helpers, chart helpers, LLM client, parser-prompt helper, sizing helper, and journal writer.
- Preserves:
  - CHF/EUR divergence prompt framing
  - `FXE (via Short EUR)` / `FXE (via Long EUR)` target semantics
  - notebook-specific dual-driver causal chart
  - existing `journal_chf_eur.csv` row mapping

### `crudegc.ipynb`

- Uses shared settings, pair config, yfinance/FRED loaders, merge logic, feature helpers, chart helpers, LLM client, routed-line parser helper, pair sizing helper, and journal writer.
- Preserves:
  - two-leg growth-vs-haven prompt framing
  - routed strategy contract
  - notebook-specific PMI causal chart
  - existing `journal_bz_gc.csv` row mapping

### `chfgc.ipynb`

- Uses shared settings, pair config, SNB/yfinance/FRED loaders, merge logic, feature helpers, chart helpers, LLM client, routed-line parser helper, pair sizing helper, and journal writer.
- Preserves:
  - SNB-intervention prompt framing
  - routed strategy contract
  - notebook-specific SNB causal chart
  - existing `journal_chf_gc.csv` row mapping

## Runtime Validation

### Validation Environment

- Python:
  - `/opt/anaconda3/bin/python`
- Python version:
  - `3.11.5`
- Dependency bootstrap:
  - `requirements.txt`
  - `fredapi` installed into the same environment used for validation
- LLM endpoint:
  - local Ollama at `http://127.0.0.1:11434`
- Validation mode:
  - isolated temporary notebook execution via `nbclient`
  - headless `Agg` matplotlib backend

### Results By Notebook

#### `10yrgc.ipynb`

- Imports and execution path:
  - notebook executed through the migrated structure
- Market and FRED fetch:
  - successful on the main validation pass
- Feature build:
  - successful
- Chart cells:
  - executed without plot exceptions
- LLM path:
  - reached but timed out during analyst generation on the main pass
- Parser:
  - not completed because the analyst stage failed
- Journal append:
  - not completed
- Validation status:
  - partial live proof

#### `chfeur.ipynb`

- Imports and execution path:
  - successful
- Market and FRED fetch:
  - successful
- Feature build:
  - successful
- Chart cells:
  - executed without plot exceptions
- LLM path:
  - successful
- Parser:
  - successful
- Journal append:
  - successful
  - temporary validation copy of `journal_chf_eur.csv` increased from 2 rows to 3 rows
- Validation status:
  - end-to-end live proof

#### `crudegc.ipynb`

- Imports and execution path:
  - notebook executed through the migrated structure
- Market fetch:
  - blocked by Yahoo rate limiting in the validation environment
- FRED fetch:
  - successful
- Feature build:
  - not fully validated end-to-end because the market-data frame did not build cleanly
- Chart cells:
  - not meaningfully validated end-to-end
- LLM path:
  - not meaningfully validated end-to-end
- Parser:
  - not meaningfully validated end-to-end
- Journal append:
  - not completed
- Validation status:
  - structurally migrated, live market-data validation deferred by environment

#### `chfgc.ipynb`

- Imports and execution path:
  - successful
- Market, FRED, and SNB fetch:
  - successful
- Feature build:
  - successful
- Chart cells:
  - executed without plot exceptions
- LLM path:
  - successful
- Parser:
  - successful
- Journal append:
  - successful
  - temporary validation copy of `journal_chf_gc.csv` increased from 2 rows to 3 rows
- Validation status:
  - end-to-end live proof

### Environment Constraint Note

Yahoo Finance was not stable in this environment. That constraint should be read as a validation-environment limitation, not as evidence that the `macro_intel` migration failed.

The strongest runtime proof therefore comes from:

- `chfeur.ipynb`
- `chfgc.ipynb`

## Runtime-Oriented Fixes Applied During Validation

- `macro_intel.config.settings.Settings`
  - default request timeout increased from 60 to 180 seconds
- `macro_intel.data.market.fetch_yfinance_prices(...)`
  - now attempts batch download first
  - falls back to per-ticker fetches only when needed
  - uses slower backoff on explicit rate-limit errors
  - pauses between ticker attempts

## Known Open Issues

- live notebooks still use full-sample normalization while `backtest.ipynb` uses rolling z-scores
- prompts are still inline and unversioned
- journal schemas remain pair-specific
- `trade_journal.csv` is still unresolved legacy baggage
- `quant.ipynb` still sits outside the pair-suite architecture
- runtime reliability still depends on Yahoo Finance and local Ollama behavior

## Recommended Next Documentation/Engineering Step

The next focused step should be:

- README and artifact cleanup
- explicit artifact classification for current vs legacy files
- backtest migration planning against the shared feature engine

That work should build on the current migration baseline rather than reopening notebook-level redesign.

## Platform Transition Baseline

The repo now also contains an initial web-platform scaffold:

- `backend/` with FastAPI routes for auth, health, pairs, runs, and journals
- `frontend/` with a Next.js operator shell for login, dashboard, pair detail, journals, and settings

That platform layer is designed to sit above `macro_intel`, not replace it.

## Platform Scaffold Validation

The initial platform scaffold has partial local validation already:

- backend Python code:
  - `PYTHONPYCACHEPREFIX=/tmp/quant_pyc python3 -m compileall backend macro_intel` passed
- backend import check:
  - `PYTHONPATH=/Users/ronnie/Desktop/quant /opt/anaconda3/bin/python -c "import backend.app.main"` succeeded
- backend API smoke test:
  - `GET /health` succeeded
  - `POST /auth/login` succeeded
  - `GET /pairs` succeeded
  - `GET /pairs/CHF_EUR` succeeded
  - `GET /journals/CHF_EUR` succeeded

Current platform validation limits:

- frontend runtime was not executed in this shell because Node.js is not available in the current environment
- full web-triggered pair runs are still environment-constrained by missing `FRED_API_KEY` and unstable Yahoo reachability
