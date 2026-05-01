# Macro Relative-Value Intelligence Desk

This repository is a notebook-first macro research system for a narrow set of relative-value pairs. It combines public market and macro data, pair-specific feature engineering, chart-based review, local LLM analysis, rough risk sizing, and CSV journaling.

The current operating model is discretionary and human-in-the-loop. The notebooks are operator interfaces, not execution bots.

## Current Pair Universe

- `10yrgc.ipynb`: 10-year Treasury proxy vs. gold
- `crudegc.ipynb`: crude proxy vs. gold
- `chfeur.ipynb`: Swiss franc proxy vs. euro proxy
- `chfgc.ipynb`: Swiss franc proxy vs. gold

## Current Architecture

The repo now has a shared local package, [`macro_intel/`](macro_intel), that sits underneath the four pair notebooks.

Shared package layers include:

- pair configuration
- data loaders for `yfinance`, FRED, and SNB
- merge and feature helpers
- chart helpers
- local LLM client and parser helpers
- sizing helpers
- journal read/write helpers

The notebooks still preserve pair-specific behavior such as:

- prompt framing
- pair-specific causal charts
- target-asset or directional-bias semantics
- pair-specific journal row mapping

## Repository Structure

```text
.
├── 10yrgc.ipynb
├── backend/
├── crudegc.ipynb
├── chfeur.ipynb
├── chfgc.ipynb
├── backtest.ipynb
├── frontend/
├── quant.ipynb
├── macro_intel/
├── journal_zb_gc.csv
├── journal_bz_gc.csv
├── journal_chf_eur.csv
├── journal_chf_gc.csv
├── backtest_results.csv
├── backtest_pair_summary.csv
├── trade_journal.csv
├── requirements.txt
├── SYSTEM_ARCHITECTURE.md
├── ROADMAP.md
└── docs/
```

## Workflow

The current pair notebooks follow the same operator workflow:

1. Fetch current market and macro data.
2. Merge and engineer pair-specific features.
3. Render causal and volatility charts.
4. Generate an analyst memo through a local Ollama-compatible LLM.
5. Parse the memo into a strategy signal.
6. Apply rough risk sizing.
7. Append the result to the pair journal CSV.

There is no broker integration, automated scheduling, or portfolio execution layer.

## Setup

See [docs/ENVIRONMENT.md](docs/ENVIRONMENT.md) for the runtime contract.

Quick start:

```bash
pip install -r requirements.txt
```

Required runtime assumptions:

- Python `3.11` recommended
- a valid `FRED_API_KEY`
- local Ollama running at `LLM_BASE_URL`
- a local model available for `LLM_MODEL`

Optional:

- MongoDB and `pymongo` only if you want to run `quant.ipynb`

## Documentation

The retained documentation set is intentionally small:

- [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md): current-state architecture and notebook-by-notebook system review
- [ROADMAP.md](ROADMAP.md): sequenced improvement roadmap
- [docs/API_CONTRACT.md](docs/API_CONTRACT.md): FastAPI and frontend contract for the platform transition
- [docs/ENVIRONMENT.md](docs/ENVIRONMENT.md): environment and bootstrap requirements
- [docs/MIGRATION_STATUS.md](docs/MIGRATION_STATUS.md): `macro_intel` migration status and runtime validation record

## Current Caveats

- The four pair notebooks are migrated onto `macro_intel`, but they still rely on inline prompt text and pair-specific notebook orchestration.
- The platform layer is now scaffolded with `backend/` and `frontend/`, but it is still an early first pass rather than a production deployment.
- `trade_journal.csv` is a legacy artifact and is not the current journal-of-record.
- Live notebooks still use full-sample normalization, while `backtest.ipynb` uses rolling z-scores.
- Yahoo Finance reliability is environment-dependent and can block live validation runs.
- `quant.ipynb` remains a separate prototype path and is not part of the current pair-suite workflow.
