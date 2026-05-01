# Environment

## Python

- Tested runtime validation environment: Python `3.11.5`
- Recommended baseline: Python `3.11`

## Install

Create or activate a Python environment, then install the repo dependencies:

```bash
pip install -r requirements.txt
```

For the web platform scaffold:

- backend runtime is included in `requirements.txt`
- frontend dependencies live in `frontend/package.json`

## Required Environment Variables

The four pair notebooks currently set default values inline for the core variables below, but they are still part of the runtime contract:

- `FRED_API_KEY`
  - Required for FRED-backed data fetches.
- `LLM_BASE_URL`
  - Expected local Ollama base URL.
  - Default notebook assumption: `http://127.0.0.1:11434`
- `LLM_MODEL`
  - Expected local Ollama model name.
  - Default notebook assumption: `qwen2.5:7b`

Optional suite-level variables already supported by `macro_intel.config.Settings`:

- `MACRO_INTEL_TIMEOUT_SECONDS`
- `EMBED_MODEL`
- `MONGO_URI`
- `MONGO_DB`

## Local Ollama Requirement

The migrated pair notebooks still expect a local Ollama-compatible `/api/chat` endpoint for:

- analyst memo generation
- second-pass parser calls in single-leg notebooks
- routed-strategy memo generation in two-leg notebooks

Minimum local check:

```bash
curl -sS http://127.0.0.1:11434/api/tags
```

## Backend / Frontend Scaffold

Backend:

```bash
uvicorn backend.app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Relevant frontend environment variable:

- `NEXT_PUBLIC_API_BASE_URL`
  - default intended local value: `http://127.0.0.1:8000`

## Notebook Scope Covered By `requirements.txt`

The dependency set in `requirements.txt` covers:

- the four migrated pair notebooks
- the `macro_intel/` shared package
- the current `backtest.ipynb` dependency path

## Optional `quant.ipynb` Note

`quant.ipynb` is not part of the migrated pair-suite runtime path.

If you want to run it, you will also need:

- a local MongoDB instance
- `pymongo`

Example:

```bash
pip install pymongo
```
