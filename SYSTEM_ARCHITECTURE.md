# System Architecture

## 1. Executive Summary

This repository is a notebook-centric research and decision-support system for a small set of macro relative-value trades. Its current core is still four Jupyter notebooks, each dedicated to one pair:

- `10yrgc.ipynb`: 10-year Treasury proxy vs. gold
- `crudegc.ipynb`: Brent proxy vs. gold
- `chfeur.ipynb`: Swiss franc proxy vs. euro proxy
- `chfgc.ipynb`: Swiss franc proxy vs. gold

Those notebooks now sit on top of a shared local package, `macro_intel`, which centralizes configuration, data loading, feature helpers, chart helpers, LLM access, sizing logic, and journal writes while leaving pair-specific prompt framing and notebook orchestration in place.

Each notebook still follows the same high-level pattern:

1. Pull live market and macro data from public sources.
2. Merge and normalize the data into pair-specific features.
3. Visualize the pair and its causal drivers.
4. Ask a local LLM to synthesize the current regime and choose an options-style strategy.
5. Convert that strategy into a rough position size.
6. Append the result to a CSV journal.

The operating model is explicitly human-in-the-loop. The notebooks do not place trades, do not schedule themselves, and do not persist raw source snapshots. They support discretionary idea generation and journaling, not automated execution.

The repository is at an early-to-mid prototype stage. It has moved beyond a pure notebook collection because the shared `macro_intel/` package now exists and materially powers the pair notebooks. Even so, the system remains fragile in several important ways:

- prompts and some pair-specific orchestration still live inline inside notebooks
- journal schemas are still pair-specific and there is still a malformed legacy `trade_journal.csv`
- `backtest.ipynb` is not yet aligned to the same feature engine as the live notebooks
- `quant.ipynb` remains a separate MongoDB and embeddings prototype that is not integrated with the main pair workflow
- an initial FastAPI + Next.js platform scaffold now exists, but it is still a first-pass interface layer rather than a production deployment

## 2. Repository Overview

### Current Repository Structure

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
├── docs/
├── journal_zb_gc.csv
├── journal_bz_gc.csv
├── journal_chf_eur.csv
├── journal_chf_gc.csv
├── backtest_results.csv
├── backtest_pair_summary.csv
├── trade_journal.csv
├── requirements.txt
└── README.md
```

### Major Files and Their Roles

| File | Role | Notes |
| --- | --- | --- |
| `10yrgc.ipynb` | Production-style pair notebook for sovereign-risk thesis | Single-leg strategy output |
| `crudegc.ipynb` | Production-style pair notebook for growth-vs-haven thesis | Two-leg strategy output |
| `chfeur.ipynb` | Production-style pair notebook for European divergence thesis | Single-leg strategy output |
| `chfgc.ipynb` | Production-style pair notebook for managed-vs-unmanaged haven thesis | Two-leg strategy output, includes SNB API |
| `backend/` | FastAPI platform scaffold | Wraps `macro_intel` with auth, pair-run, journal, and health endpoints |
| `frontend/` | Next.js operator UI scaffold | Provides login, dashboard, pair, journal, and settings pages |
| `macro_intel/` | Shared suite engine used by the pair notebooks | Holds config, data, features, LLM, risk, journal, reporting, and utility modules |
| `docs/` | Focused support documentation | Environment and migration/runtime status |
| `backtest.ipynb` | Historical proxy backtest and synthetic signal engine | Consumes per-pair journals, exports diagnostics |
| `quant.ipynb` | Separate prototype notebook using MongoDB, embeddings, mock data, and partial live data | Not integrated with current journal/backtest path |
| `journal_*.csv` | Current per-pair append-only trade journals | Headered, pair-specific schemas |
| `backtest_results.csv` | Exported trade-level backtest results | Produced by `backtest.ipynb` |
| `backtest_pair_summary.csv` | Exported pair-level backtest summary | Produced by `backtest.ipynb` |
| `trade_journal.csv` | Legacy aggregate journal artifact | Malformed and not written by current notebooks |
| `requirements.txt` | Runtime dependency manifest | Covers the shared package, pair notebooks, and current backtest path |
| `README.md` | Repo overview | High-level guide to the current system and retained docs |

### Primary Execution Artifacts

The actual execution surfaces today are:

- the four pair notebooks
- the `macro_intel/` shared package those notebooks import
- the FastAPI backend scaffold in `backend/`
- the Next.js frontend scaffold in `frontend/`
- `backtest.ipynb`
- `quant.ipynb`

There is now a real local package and a real dependency manifest, but the repo is still intentionally lightweight:

- no CLI entrypoint
- no scheduler
- no broker execution layer
- no service wrapper around the desk workflow

### Documentation Set

The current retained markdown set is:

- `README.md` for the repo overview
- `SYSTEM_ARCHITECTURE.md` for the current-state architecture baseline
- `ROADMAP.md` for ordered future work
- `docs/ENVIRONMENT.md` for environment setup and runtime assumptions
- `docs/MIGRATION_STATUS.md` for notebook migration and runtime validation status
- `docs/API_CONTRACT.md` for the first platform API and pilot rollout contract

The previously separate pair-notebook deep dives, synthesis notes, and refactor logs have been consolidated into this architecture document and the migration-status record.

## 3. System Purpose and Operating Model

### Intended User

The intended operator is a human discretionary macro trader or researcher who wants:

- live public data on a narrow set of relative-value pairs
- chart-based context before making a decision
- LLM-generated second-opinion analysis
- a journaled trade idea with rough position sizing

### Operating Frequency

The notebooks are structured like weekly or periodic review tools, not intraday execution systems. They fetch five years of data on each run, compute a current regime snapshot, and log one dated trade idea per run.

### Decision-Support vs. Automation

This is a decision-support desk, not an execution platform.

Manual responsibilities still include:

- launching the notebook
- running cells in order
- reviewing the charts
- deciding whether to trust the LLM analysis
- deciding whether to run the journaling cell
- manually placing any paper or live trade outside the notebook

There is no:

- broker API integration
- order management
- automated scheduling
- portfolio-level risk aggregation
- centralized state manager

## 4. Current Functional Architecture

### Layer 1: Data Acquisition

Inputs:

- ETF price proxies from `yfinance`
- macro and volatility series from FRED via `fredapi`
- SNB sight deposits from the SNB API in `chfgc.ipynb` and `backtest.ipynb`
- MongoDB and Ollama endpoints in `quant.ipynb`

Outputs:

- in-memory pandas DataFrames such as `df_yf`, `df_fred`, `df_snb`, `df`, and `df_hist`

Implementation locations:

- `macro_intel.data.market`, `macro_intel.data.fred`, `macro_intel.data.snb`, and `macro_intel.data.merge`
- pair notebooks as orchestration cells that call those helpers
- `backtest.ipynb`: Cells 2-4
- `quant.ipynb`: Cells 0a-0d and 16-17

Dependencies:

- `yfinance`
- `fredapi`
- `requests`
- `pymongo` in `quant.ipynb`

Notable issues:

- all source data is fetched live with no caching or snapshotting
- API keys and endpoint defaults are still partially embedded in notebooks
- Yahoo Finance remains externally fragile even after the shared loader consolidation
- there is limited validation in pair notebooks compared with `backtest.ipynb`

### Layer 2: Feature Engineering

Inputs:

- merged market and macro DataFrames

Outputs:

- normalized price series
- pair spreads and ratios
- rolling correlations
- historical volatility
- implied-volatility rank
- volatility risk premium
- signal velocity
- pair-specific causal features such as EU risk spread or SNB intervention

Implementation locations:

- `macro_intel.features.core`, `macro_intel.features.correlations`, `macro_intel.features.volatility`, and `macro_intel.features.pair_specific`
- pair notebooks as orchestration cells that apply shared helpers and preserve pair-specific framing
- `backtest.ipynb`: Cell 4 for rolling z-score spread oracle, Cell 12 for synthetic historical signal features
- `quant.ipynb`: Cells 10-14

Notable issues:

- pair notebooks use full-sample z-scoring, which bakes future information into the current normalized series
- `backtest.ipynb` deliberately switches to rolling z-scores to avoid look-ahead bias, so live notebooks and backtest are not using identical signal construction
- pair-specific prompt semantics and some final field mapping still live inline instead of being fully parameterized

### Layer 3: Visualization

Inputs:

- engineered DataFrames

Outputs:

- matplotlib charts rendered inside notebooks

Implementation locations:

- `macro_intel.reporting.charts` for shared chart scaffolding
- pair notebooks for pair-specific causal plots and final layout choices
- `backtest.ipynb`: Cell 8 and Cell 13
- `quant.ipynb`: Cells 15 and 17

Notable issues:

- charting duplication is reduced but not eliminated
- no charts are saved to disk as named artifacts
- there is no common plotting library or style system

### Layer 4: LLM Analysis

Inputs:

- latest feature row
- notebook-specific inline prompt text
- local Ollama `/api/chat` endpoint

Outputs:

- free-form analyst reasoning
- in some notebooks, parsable strategy lines embedded in that reasoning
- in `backtest.ipynb`, a critique of backtest performance

Implementation locations:

- `macro_intel.llm.client` for transport and settings
- pair notebooks for prompt construction and memo framing
- `backtest.ipynb`: Cell 9
- `quant.ipynb`: Cells 0b, 0d

Notable issues:

- prompts are still inline and unversioned
- pair notebooks intentionally retain different parser architectures
- there is no schema enforcement for LLM output beyond ad hoc checks
- runtime still depends on local Ollama health and model latency

### Layer 5: Parsing / Strategy Extraction

Inputs:

- LLM analyst output

Outputs:

- strategy name or per-leg strategy names stored in `latest_trade_rec`

Implementation locations:

- `macro_intel.llm.parser` plus notebook-specific parser orchestration
- `10yrgc.ipynb`: second LLM pass to extract one strategy
- `chfeur.ipynb`: second LLM pass to extract one strategy
- `crudegc.ipynb`: routed-line parsing of `ROUTED_STRATEGY_*` lines
- `chfgc.ipynb`: routed-line parsing of `ROUTED_STRATEGY_*` lines

Notable issues:

- parser behavior is inconsistent across notebooks
- string parsing depends on exact line labels in model output
- second-pass LLM parsing adds latency and another failure point

### Layer 6: Risk Sizing

Inputs:

- parsed strategy
- fixed account value and basis-point risk rules
- hard-coded per-strategy risk-per-contract estimates

Outputs:

- contract count per trade or per leg
- printed trade ticket

Implementation locations:

- `macro_intel.risk.sizing`
- pair notebooks for final ticket display wording
- `quant.ipynb`: Cell 14

Notable issues:

- sizing is approximate and not instrument-specific
- there is no strike selection, expiry selection, or premium calculation
- pair notebooks split risk across legs, but backtest does not preserve both leg sizes cleanly

### Layer 7: Journaling / Persistence

Inputs:

- latest feature row
- parsed strategy result
- LLM analyst report

Outputs:

- appended CSV row in pair-specific journal

Implementation locations:

- `macro_intel.journal.schema`, `macro_intel.journal.writer`, and `macro_intel.journal.reader`
- pair notebooks for final row assembly and pair-specific field mapping
- `backtest.ipynb`: Cell 10 for export outputs

Notable issues:

- schemas differ by notebook
- rerunning the log cell creates duplicates
- there is no unique trade ID, schema version, prompt version, or model metadata
- the legacy aggregate `trade_journal.csv` no longer matches current write logic

### Layer 8: Backtesting

Inputs:

- per-pair journal CSVs
- freshly refetched historical data

Outputs:

- trade-level proxy PnL results
- pair summary CSV
- LLM critique
- optional synthetic historical signal grid

Implementation locations:

- `backtest.ipynb`

Notable issues:

- this is a spread-z-score proxy backtest, not a real options PnL model
- the notebook consumes only a normalized representation of journal output
- it simplifies two-leg trades into a single standardized trade row

## 5. Notebook-by-Notebook Review

The reviews below describe the notebooks as they exist now: materially rewired onto `macro_intel`, but still preserving notebook-local prompt text, pair-specific chart composition, and pair-specific journal row assembly where that behavior is part of the strategy semantics.

### `10yrgc.ipynb`

Business purpose:

- expresses the “sovereign risk / de-dollarization” thesis as gold outperforming long-duration Treasuries

Covered instruments:

- market proxies: `GLD`, `TLT`
- macro/vol series: `DFII10`, `T10YIE`, `DTWEXBGS`, `GVZCLS`, `VIXCLS`

Cell structure:

- Cell 1: Markdown thesis description and driver list
- Cell 2: Imports
- Cell 3: Configures FRED key, Ollama endpoint, model name, `ask_llm`, tickers, series IDs, and 5-year date range
- Cell 4: Downloads price history from `yfinance`
- Cell 5: Pulls FRED series
- Cell 6: Merges and forward-fills market and macro data
- Cell 7: Full-sample z-score normalization with `scipy.stats.zscore`
- Cell 8: Computes `GLD_TLT_Ratio`, `GLD_TLT_Spread_Norm`, and `GLD_DFII10_Spread_Norm`
- Cell 9: Computes 30-day and 90-day rolling return correlations
- Cell 10: Computes 30-day historical volatility for GLD and TLT
- Cell 11: Computes IV rank using `GVZCLS` and `VIXCLS`
- Cell 12: Computes volatility risk premium and 5-day signal velocity, then drops NaNs
- Cells 13-16: Plots pair divergence, causal driver, rolling correlation, and volatility dashboard
- Cell 17: Builds inline analyst prompt and calls the local LLM
- Cell 18: Calls the LLM again as a parser to choose one strategy
- Cell 19: Sizes the trade using a flat account/risk model
- Cell 20: Appends the result to `journal_zb_gc.csv`

Operational flow:

- this notebook is effectively a single-leg recommendation notebook
- it computes which asset is the “target” based on spread sign
- it chooses one strategy for that target asset
- it does not explicitly model a paired options structure on both sides

Files read/written:

- reads live yfinance and FRED data
- writes `journal_zb_gc.csv`

Duplicated logic:

- imports, environment config, LLM helper, merge logic, z-score logic, HV/IVR/VRP logic, sizing model, and journal append logic all resemble the other pair notebooks

Notebook-specific quirks and risks:

- uses `VIXCLS` as a stand-in for Treasury volatility while naming derived fields `TYVIX_*`
- if the target asset becomes `TLT`, Cell 17 references `latest_data['TYVIXCLS']`, which does not exist; that branch will fail
- uses full-sample normalization instead of rolling normalization
- parser depends on a second LLM call

### `crudegc.ipynb`

Business purpose:

- expresses the “growth vs. haven” trade as gold versus Brent/oil divergence

Covered instruments:

- market proxies: `GLD`, `BNO`
- macro/vol series: `IPMAN`, `CPILFESL`, `DTWEXBGS`, `GVZCLS`, `OVXCLS`

Cell structure:

- Cell 1: Markdown thesis description
- Cell 2: Imports
- Cell 3: Configures FRED, Ollama, tickers, series IDs, and date range
- Cell 4: Downloads `GLD` and `BNO`
- Cell 5: Loads FRED drivers
- Cell 6: Merges and forward-fills
- Cell 7: Full-sample normalization
- Cell 8: Computes `GLD_BNO_Ratio` and `GLD_BNO_Spread_Norm`
- Cell 9: Rolling return correlations
- Cell 10: Historical volatility
- Cell 11: IV rank from `GVZCLS` and `OVXCLS`
- Cell 12: VRP and signal velocity
- Cells 13-16: Core, causal, correlation, and volatility charts
- Cell 17: LLM analyst prompt for a two-leg pairs trade
- Cell 18: String parser for `ROUTED_STRATEGY_GLD` and `ROUTED_STRATEGY_BNO`
- Cell 19: Risk split across both legs
- Cell 20: Appends to `journal_bz_gc.csv`
- Cell 21: Empty stray code cell

Operational flow:

- unlike `10yrgc.ipynb`, this notebook routes a strategy for each leg
- the prompt tells the model to end with two parsable lines
- the parser uses direct string matching rather than a second LLM

Files read/written:

- reads live yfinance and FRED data
- writes `journal_bz_gc.csv`

Duplicated logic:

- almost all scaffolding is duplicated from the other pair notebooks, with different symbols and prompt text

Notebook-specific quirks and risks:

- yfinance fetch uses the simpler multi-ticker `yf.download` path without the extra handling used in `10yrgc.ipynb` or `backtest.ipynb`
- string parsing assumes exact routed-line labels and does not validate against a whitelist
- there is a blank trailing code cell, which suggests notebook hygiene drift

### `chfeur.ipynb`

Business purpose:

- expresses the “European divergence” thesis as Swiss franc strength versus euro weakness during EU-specific stress or policy divergence

Covered instruments:

- market proxies: `FXF`, `FXE`
- macro/vol series: Italian 10Y yield, German 10Y yield, Swiss CPI, Euro-area HICP, `VIXCLS`

Cell structure:

- Cell 1: Markdown thesis description
- Cell 2: Imports
- Cell 3: Configures FRED, Ollama, tickers, series IDs, and date range
- Cell 4: Downloads `FXF` and `FXE`
- Cell 5: Loads FRED series
- Cell 6: Merges and forward-fills
- Cell 7: Full-sample normalization
- Cell 8: Computes `CHF_EUR_Ratio`, `CHF_EUR_Spread_Norm`, `EU_Risk_Spread`, and `Inflation_Differential`
- Cell 9: Rolling return correlations
- Cell 10: Historical volatility
- Cell 11: IV rank from `VIXCLS`
- Cell 12: VRP and signal velocity
- Cells 13-16: Core, causal, correlation, and volatility charts
- Cell 17: LLM analyst prompt for one strategy on `FXE`
- Cell 18: Second LLM pass to parse one strategy
- Cell 19: Single-leg risk sizing
- Cell 20: Appends to `journal_chf_eur.csv`

Operational flow:

- this notebook treats the trade as a directional strategy on `FXE`, with the target asset phrased as `FXE (via Short EUR)` or `FXE (via Long EUR)`
- the pair logic is therefore encoded through the target label rather than separate legs

Files read/written:

- reads live yfinance and FRED data
- writes `journal_chf_eur.csv`

Duplicated logic:

- same scaffold as `10yrgc.ipynb`, with pair-specific features and prompt language

Notebook-specific quirks and risks:

- comments call `VIXCLS` a euro FX volatility index, but the notebook is actually using it as a broad/global risk proxy
- parser architecture is again a second LLM call instead of deterministic local parsing
- the backtester has to interpret `Target_Asset` strings heuristically because the journal does not record an explicit spread direction

### `chfgc.ipynb`

Business purpose:

- expresses the “managed vs. unmanaged haven” thesis as Swiss franc versus gold, with SNB sight deposits used as the intervention proxy

Covered instruments:

- market proxies: `FXF`, `GLD`
- macro/vol series: `DFII10`, `GVZCLS`, `VIXCLS`
- direct external source: SNB sight deposits API

Cell structure:

- Cell 1: Markdown thesis description
- Cell 2: Imports
- Cell 3: Configures FRED, Ollama, tickers, FRED series, and date range
- Cell 4: Fetches SNB weekly sight deposits directly from the SNB API
- Cell 5: Downloads `FXF` and `GLD`
- Cell 6: Loads FRED series
- Cell 7: Merges yfinance, FRED, and SNB data and forward-fills all of it
- Cell 8: Full-sample normalization
- Cell 9: Computes `CHF_GLD_Ratio`, `CHF_GLD_Spread_Norm`, and `SNB_Intervention_WoW`
- Cell 10: Rolling return correlations
- Cell 11: Historical volatility
- Cell 12: IV rank for gold and VIX proxy
- Cell 13: VRP and signal velocity
- Cells 14-17: Core, intervention, correlation, and volatility charts
- Cell 18: LLM analyst prompt with explicit routing examples and required routed lines
- Cell 19: String parser for `ROUTED_STRATEGY_GLD` and `ROUTED_STRATEGY_FXF`
- Cell 20: Pair risk sizing with split basis-point budget
- Cell 21: Appends to `journal_chf_gc.csv`

Operational flow:

- this is the only production notebook with a third external data source beyond yfinance and FRED
- it uses the latest SNB intervention signal in the prompt and logs it to the journal

Files read/written:

- reads live yfinance, FRED, and SNB data
- writes `journal_chf_gc.csv`

Duplicated logic:

- most scaffolding still duplicates the other notebooks

Notebook-specific quirks and risks:

- SNB weekly data is forward-filled into a daily frame and then differenced with `.diff(7)`, which approximates week-over-week change but is tightly coupled to the daily forward-fill behavior
- VIX is used as a CHF vol proxy
- routed-line parsing is fragile if the LLM changes formatting

### `backtest.ipynb`

Business purpose:

- evaluates the historical directional thesis behind journaled trades
- creates a separate historical signal engine for threshold and holding-period sweeps

Cell structure:

- Cell 1: Intro describing a relative-value proxy backtest
- Cell 2: Imports
- Cell 3: Configures keys, journal file list, holding period, z-score point value, rolling z window, and data universe
- Cell 4: Robust fetchers for yfinance, FRED, and SNB with retries and validation
- Cell 5: Builds a “historical oracle” DataFrame with rolling z-scores and four spread columns
- Cell 6: Loads and standardizes per-pair journals
- Cell 7: Helper functions for spread mapping and trading-day alignment
- Cell 8: Runs the actual backtest loop
- Cell 9: Computes summary statistics and draws an equity curve
- Cell 10: Sends summary metrics to the local LLM for critique
- Cell 11: Exports `backtest_results.csv` and `backtest_pair_summary.csv`
- Cell 12: Generates synthetic historical signals directly from `df_hist`
- Cell 13: Summarizes synthetic historical signals

Files read/written:

- reads `journal_zb_gc.csv`, `journal_bz_gc.csv`, `journal_chf_eur.csv`, `journal_chf_gc.csv`
- writes `backtest_results.csv` and `backtest_pair_summary.csv`

Current behavior:

- uses rolling z-scores rather than full-sample normalization
- aligns signal dates to the next available trading day
- skips trades whose exits extend beyond available historical data
- models PnL as `z-score change * direction * contracts * point value`

Backtest-specific quirks and risks:

- the intro still describes `trade_journal.csv` as the input, but the code actually reads the four per-pair journals
- a legacy `JOURNAL_FILE = "quant/trade_journal.csv"` constant remains but is unused and points to a non-existent path in this repo
- pair journals are standardized into a single row representation; for pair notebooks the standardizer keeps `Strategy_GLD` and `Contracts_GLD`, so second-leg strategy details are lost in the main backtest table
- the PnL model is a directional spread proxy, not a real options or futures mark-to-market

### `quant.ipynb`

Business purpose:

- prototypes a different architecture centered on MongoDB, embeddings, mock NoSQL collections, and a Swiss-franc-focused strategy router

Cell structure:

- Cell 1: Tries to connect to MongoDB
- Cell 2: Markdown overview
- Cell 3: Sets `MONGO_URI`, `MONGO_DB`, Ollama variables, and connects to MongoDB
- Cell 4: Defines Ollama embedding and chat interfaces
- Cell 5: Defines MongoDB embedding persistence helpers
- Cell 6: Sends an example macro summary prompt to the LLM
- Cell 7: Imports analysis libraries
- Cell 8: Markdown schema description
- Cell 9: Builds a `mock_db` with synthetic market, macro, event, and sentiment data
- Cells 10-14: Loads mock data, engineers features, classifies regime, routes strategy, and sizes trades
- Cell 15: Prints the latest strategy decision and plots key features
- Cell 16: Pulls some live yfinance and FRED data into `mock_db`, with placeholder random IV values
- Cell 17: Loads and plots that live data
- Cell 18: Markdown conclusion

Files read/written:

- reads local MongoDB if available
- reads live yfinance and FRED data in later cells
- does not write to the current pair journals or backtest exports

Role in the repository:

- this notebook is not part of the current pair-journal workflow
- it looks like an exploratory prototype rather than a maintained production path

Notebook-specific quirks and risks:

- depends on `pymongo`, which is not documented in the README and cannot be installed from a missing `requirements.txt`
- mixes mock data and live data in the same notebook
- uses placeholder random IV values in the “real data” section
- uses a separate strategy ontology from the four pair notebooks

## 6. Data Sources and External Dependencies

### Market Data via `yfinance`

Usage:

- `10yrgc.ipynb`: `GLD`, `TLT`
- `crudegc.ipynb`: `GLD`, `BNO`
- `chfeur.ipynb`: `FXF`, `FXE`
- `chfgc.ipynb`: `FXF`, `GLD`
- `backtest.ipynb`: `GLD`, `TLT`, `BNO`, `FXF`, `FXE`
- `quant.ipynb`: `6S=F`, `6E=F`

Access method:

- direct library calls through `yf.download(...)` in pair notebooks
- `yf.Ticker(...).history(...)` in `backtest.ipynb`

Config assumptions:

- no credentials required
- internet access required at notebook run time

Failure points:

- rate limiting
- schema variation between single- and multi-ticker results
- inconsistent use of `auto_adjust`

Usage classification:

- direct

### Macro and Volatility Data via FRED

Usage:

- pair-specific macro drivers and volatility proxies
- full historical oracle in `backtest.ipynb`
- partial prototype feed in `quant.ipynb`

Access method:

- `fredapi.Fred(api_key=...)`
- `fred.get_series(...)`

Credentials/config assumptions:

- requires `FRED_API_KEY`
- every notebook sets a default hard-coded key with `os.environ.setdefault(...)`

Failure points:

- invalid or revoked API key
- unavailable series IDs
- lower-frequency series that require forward fill

Usage classification:

- direct

### SNB API

Usage:

- CHF/gold intervention signal in `chfgc.ipynb`
- historical oracle input in `backtest.ipynb`

Access method:

- direct HTTP GET to `https://data.snb.ch/api/cube/snbgwdchfsgw/data/json/en`
- parameter `dimSel=D0(GI,UEB,TG)`

Credentials/config assumptions:

- no credential required

Failure points:

- response schema changes
- target series label changes
- weekly frequency requiring forward-fill assumptions

Usage classification:

- direct

### Local LLM Endpoint

Usage:

- analyst synthesis in all four pair notebooks
- parser pass in `10yrgc.ipynb` and `chfeur.ipynb`
- backtest critique in `backtest.ipynb`
- chat plus embeddings in `quant.ipynb`

Access method:

- `POST {LLM_BASE_URL}/api/chat`
- `POST {LLM_BASE_URL}/api/embeddings` in `quant.ipynb`

Credentials/config assumptions:

- expects a local Ollama server at `http://127.0.0.1:11434`
- default model is `qwen2.5:7b`
- `quant.ipynb` also expects embedding model `avr/sfr-embedding-mistral`

Failure points:

- Ollama not running
- model not installed
- response schema drift
- parser prompts producing non-conforming output

Usage classification:

- direct local service call

### MongoDB

Usage:

- only `quant.ipynb`

Access method:

- `pymongo.MongoClient`

Credentials/config assumptions:

- default `MONGO_URI=mongodb://localhost:27017/`
- default database `quant_macro`

Failure points:

- MongoDB not running
- missing `pymongo`

Usage classification:

- direct

### Third-Party Python Dependencies Actually Used

Observed third-party imports across notebooks:

- `pandas`
- `numpy`
- `matplotlib`
- `scipy`
- `yfinance`
- `fredapi`
- `requests`
- `pymongo`

Repo issue:

- there is no actual dependency manifest in the repository root

### Environment Variables Used

Used in current notebooks:

- `FRED_API_KEY`
- `LLM_BASE_URL`
- `LLM_MODEL`
- `MONGO_URI`
- `MONGO_DB`
- `EMBED_MODEL`

Important note:

- risk parameters are not externalized; they are hard-coded in notebook cells

## 7. Data Flow and Control Flow

The current pipeline can be described as:

1. A notebook defines its pair-specific market tickers, macro drivers, and a five-year date range.
2. It downloads daily market data from `yfinance`.
3. It downloads macro and volatility series from FRED.
4. In the CHF/gold case, it also pulls SNB sight deposits directly from the SNB API.
5. It outer-joins all series into one DataFrame, forward-fills slower series, and drops early rows with insufficient data.
6. It computes normalized price series, pair spreads, rolling correlations, 30-day historical volatility, implied-volatility rank, volatility risk premium, and 5-day spread velocity.
7. It renders charts for the operator:
   - core pair divergence
   - causal driver charts
   - rolling correlation
   - volatility dashboard
8. It takes the latest row of the engineered DataFrame and formats an inline LLM prompt describing:
   - thematic bias
   - signal strength
   - signal velocity
   - correlation regime
   - pair-specific drivers
   - current volatility state
9. The notebook sends that prompt to the local Ollama `/api/chat` endpoint and receives a free-form analyst report.
10. A parser stage converts the free-form report into a strategy signal:
   - either a second LLM parsing call for single-strategy notebooks
   - or local string matching of required routed lines for two-leg notebooks
11. The sizing cell maps the parsed strategy into an approximate contract count using:
   - `ACCOUNT_VALUE = 100000`
   - `RISK_BPS_PER_TRADE = 50`
   - a fixed dictionary of risk-per-contract assumptions
12. The logging cell appends a single dated CSV row containing:
   - pair metadata
   - strategy choice
   - contract count
   - key feature values
   - full analyst reasoning
13. `backtest.ipynb` later reloads the per-pair journal files, standardizes them, reconstructs rolling z-score spreads from fresh historical data, and simulates a directional PnL proxy over a fixed hold horizon.

Persistence boundaries:

- raw source pulls are not saved
- intermediate DataFrames are not saved
- only the final journal row, notebook outputs, and backtest exports persist

## 8. LLM and Prompt Architecture

### Prompt Locations

All prompts live inline inside notebook code cells.

- pair notebooks: Cell 12
- parser prompts in `10yrgc.ipynb` and `chfeur.ipynb`: Cell 13
- backtest critique prompt: `backtest.ipynb` Cell 9
- example macro brief prompt: `quant.ipynb` Cell 0d

### Current Prompt Types

#### Analyst prompts in `10yrgc.ipynb` and `chfeur.ipynb`

These prompts ask the model for a three-part recommendation:

- volatility regime
- thematic regime
- strategy route

They do not force a parsable final line. The notebook therefore makes a second LLM call to extract one strategy name.

#### Analyst prompts in `crudegc.ipynb` and `chfgc.ipynb`

These prompts ask the model for a detailed pairs-trade recommendation and explicitly require final lines such as:

- `ROUTED_STRATEGY_GLD: ...`
- `ROUTED_STRATEGY_BNO: ...`
- `ROUTED_STRATEGY_FXF: ...`

The notebooks then parse those lines locally with string matching.

#### Backtest critique prompt

This prompt asks the model to critique backtest metrics in three bullets:

- performance critique
- biggest flaw
- next step

### Prompt Inputs

The prompts are built from the latest engineered row and include combinations of:

- signal z-score
- signal velocity
- 90-day correlation
- macro drivers such as PMI, inflation differential, or SNB intervention
- IV rank
- VRP
- pair-specific target asset or directional bias
- allowed strategy list

### Expected Outputs

Expected output families:

- free-form analyst reasoning
- single strategy token from a parser call
- or per-leg strategy lines for direct parsing

### Structured vs. Unstructured Stages

The workflow is intentionally two-stage:

1. unstructured reasoning for the human
2. structured strategy extraction for the machine

This is a sound conceptual split, but it is implemented inconsistently across notebooks.

### Coupling and Fragility

Current coupling points:

- strategy names must exactly match the hard-coded risk dictionary
- string parsing depends on exact routed-line labels
- second-pass parser prompts depend on the first LLM output being interpretable
- journal schemas depend on local variable names in the notebook

Known fragility:

- no prompt versioning
- no output schema validation beyond membership checks or string prefixes
- model upgrades could silently break parser assumptions
- there is no regression suite for prompts or parser behavior

## 9. Risk Management and Trade Construction Logic

### Shared Risk Assumptions

The four main notebooks all use:

- `ACCOUNT_VALUE = 100000.00`
- `RISK_BPS_PER_TRADE = 50`

Single-leg notebooks:

- allocate the full 50 bps to one strategy

Two-leg notebooks:

- split the 50 bps into 25 bps per leg

### Risk-per-Contract Mapping

The notebooks use a fixed strategy-to-risk lookup:

- `Bull_Put_Spread`: 350
- `Bear_Call_Spread`: 350
- `Iron_Condor`: 300
- `Calendar_Spread`: 150
- `Diagonal_Spread`: 200
- `Double_Diagonal_Spread`: 100
- `No_Trade`: 0

Sizing rule:

- `contracts = floor(risk_budget / risk_per_contract)`
- minimum size is forced to 1 contract for non-zero strategies

### Output Ticket Structure

Single-leg notebooks print:

- date
- theme
- target asset
- strategy
- contracts
- max risk budget

Two-leg notebooks print:

- date
- theme
- directional bias
- total risk budget
- strategy and size for each leg

### Gaps Between Signal Generation and Executable Trade Expression

The current “trade ticket” is conceptual, not executable. It does not specify:

- underlying symbol to trade at the broker
- option expiry
- strike selection
- delta target
- spread width
- premium received/paid
- stop/exit rules

The risk model is therefore best interpreted as a notebook-level rough sizing convention, not a broker-ready risk engine.

## 10. Persistence, State, and Artifacts

### Per-Pair Journals

Current journals written by notebooks:

- `journal_zb_gc.csv`
- `journal_bz_gc.csv`
- `journal_chf_eur.csv`
- `journal_chf_gc.csv`

Observed characteristics:

- each currently has 2 rows
- observed dates are `2025-11-03` and `2026-04-02`
- schemas are pair-specific rather than universal
- each row stores the full analyst reasoning text

### Legacy Aggregate Journal

`trade_journal.csv` is a legacy artifact and is currently problematic:

- it has no header row
- row widths vary
- it mixes multiple schema shapes in one file
- current notebooks do not write to it
- the README still describes it as the canonical journal

This file should not be treated as a reliable system-of-record artifact in the repo’s current state.

### Backtest Artifacts

- `backtest_results.csv`: 4 completed trades
- `backtest_pair_summary.csv`: 4 pair-level summary rows

These are export outputs from `backtest.ipynb`, not source data.

### Notebook State

Notebook outputs are committed to the repository. Consequences:

- notebook files are large
- output state becomes part of version control
- merge conflicts become more likely
- execution history and current outputs can diverge from source logic

### Reproducibility Implications

The system is only partially reproducible because:

- raw source data is not snapshotted
- normalization differs between live notebooks and backtest
- LLM outputs are non-deterministic at analyst stage
- parser behavior depends on local LLM availability and formatting
- repeated log-cell runs create duplicate rows without deduplication

## 11. Architecture Strengths

- The repository has a clear, narrow thesis rather than an unfocused platform ambition.
- The four production notebooks now share a real local engine in `macro_intel`, which materially reduces duplicated scaffolding.
- Each pair ties price behavior to explicit macro drivers instead of pure price action alone.
- The operator workflow is appropriately human-in-the-loop for a research-stage macro desk.
- The newer per-pair journals are cleaner than the legacy aggregate journal and are explicit about pair context.
- The repo now has an actual dependency manifest and environment documentation.
- `backtest.ipynb` already recognizes look-ahead bias and uses rolling z-scores instead of full-sample normalization.
- The local LLM setup keeps the reasoning workflow self-contained and compatible with offline or privacy-sensitive usage.
- Runtime validation has already proven one single-leg and one two-leg notebook end-to-end after migration.

## 12. Architecture Weaknesses and Technical Debt

- Prompts, some pair-specific orchestration, and some final journal row mapping still live inline in notebooks.
- Secrets and environment defaults are still partially hard-coded inline in notebooks.
- Journal schemas differ by notebook, and a legacy malformed journal remains in the repo.
- Live notebooks and backtest use different normalization logic, so the signal definition is not fully consistent end-to-end.
- LLM parsing is inconsistent across notebooks and fragile.
- Notebook execution order is stateful and implicit; cells rely on in-memory variables from prior cells.
- There is no validation layer for journal rows, prompt outputs, or configuration completeness.
- `quant.ipynb` introduces a second architecture direction that is not integrated with the current desk workflow.
- Backtest standardization compresses multi-leg journals into a simplified single standardized row, losing fidelity.
- There is no raw data provenance layer or cached data storage.
- External runtime reliability still depends heavily on Yahoo Finance and local Ollama availability.

## 13. Key Gaps Blocking Scale-Up

- No authoritative system-of-record journal schema.
- No parity between live signal construction and backtest signal construction.
- No prompt contract or schema-tested output layer.
- No raw-data snapshotting or provenance store.
- No explicit decision on the fate of `trade_journal.csv` and `quant.ipynb`.
- No stable, environment-independent validation harness for market-data-dependent notebooks.

## 14. Open Questions / Unknowns

- Is `trade_journal.csv` intended to be retired, repaired, or migrated into the new per-pair journal model?
- Is `quant.ipynb` intended to become the future architecture base, or is it now archival prototype material?
- Should Treasury and CHF volatility continue using broad proxies like `VIXCLS`, or were more specific vol series intended but not completed?
- Do the hard-coded risk-per-contract numbers correspond to any real option structures, or are they purely placeholder heuristics?
- Should pair notebooks ultimately express both legs explicitly, or are the single-leg notebooks intentionally directional-only?

## 15. Recommended Target Architecture Direction

The next architecture should stay lightweight and preserve the current research workflow. It should build on the existing `macro_intel` package rather than replacing it.

Directional recommendations:

- continue thinning notebooks so more orchestration lives in `macro_intel`
- preserve pair configuration objects for tickers, FRED series, prompt variables, journal schema, and plotting metadata
- move LLM prompts into reusable templates with simple versioning
- standardize journal writes into one canonical schema with pair-specific extension fields if needed
- keep notebooks as operator-facing orchestration and visualization surfaces
- make the backtester consume the same feature definitions as the live notebooks
- add configuration, validation, and logging before adding dashboards or execution

The right target is not a heavy platform. It is a cleaner, testable research desk with notebooks on top of shared, explicit utilities.

## 16. Current Migration Status

The repository is no longer just a set of standalone notebooks.

Current migration state:

- all four pair notebooks now import and rely materially on `macro_intel`
- shared layers now exist for config, data access, feature engineering, chart helpers, LLM transport, parser helpers, sizing, and journal IO
- runtime validation has already proven:
  - `chfeur.ipynb` end-to-end
  - `chfgc.ipynb` end-to-end
- runtime validation for `10yrgc.ipynb` was partially successful but hit an LLM timeout during the analyst stage
- runtime validation for `crudegc.ipynb` remains environment-constrained by Yahoo Finance rate limiting

The detailed migration and runtime record now lives in `docs/MIGRATION_STATUS.md`.
