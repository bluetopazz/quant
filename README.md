

-----

```markdown
# Macro Relative-Value Intelligence Desk

A Python-based OSINT framework for analyzing and trading macro relative-value (RV) pairs. This project is built on the thesis of operating as an "Independent Intelligence Desk," fusing open-source data (OSINT) with a volatility-based options strategy router.

The core principle is to move from raw, public data (from central banks, exchanges) to a fully-sized, journaled trade idea, with a human-in-the-loop (you) to analyze the LLM-generated reasoning.

## 🏛️ Core Thesis

This system is designed to execute a specific thesis:
> "Define your edge. Your stack = science/tech + commodities + FX + politics. Turn that into repeatable hypotheses you can trade and publish. Every trade idea must tie to a causal chain you can sketch."

This project provides the tools to build and test those causal chains.

## ✨ Features

* **4 Core Macro Pairs:** Deep analysis for four specific RV pairs:
    1.  **Sovereign Risk:** 10-Yr Treasuries vs. Gold (ZB/GC)
    2.  **Growth vs. Haven:** Brent Crude vs. Gold (BZ/GC)
    3.  **European Divergence:** Swiss Franc vs. Euro (CHF/EUR)
    4.  **Managed vs. Unmanaged Haven:** Swiss Franc vs. Gold (CHF/GC)
* **OSINT Data Pipeline:** Automatically pulls and merges data from:
    * `yfinance` (ETF/Asset Prices)
    * `fredapi` (Causal Drivers: Real Yields, Volatility Indexes, CPI, PMI)
    * `SNB API` (Direct pull of Swiss National Bank intervention data)
* **Volatility-Regime Routing:** Goes beyond price to analyze the *volatility* regime:
    * **Implied Volatility Rank (IVR):** Calculates 1-year IV Rank to determine if options are "cheap" or "expensive."
    * **Volatility Risk Premium (VRP):** Compares Implied Vol (IV) to Historical Vol (HV) to find premium-selling opportunities.
* **LLM Analyst Synthesis:** A core 5-cell workflow in each notebook:
    1.  **`Cell 12` (The Analyst):** A verbose LLM prompt generates a human-readable "Analyst Report" explaining the "why" (thematic drivers) and the "when" (volatility regime).
    2.  **`Cell 13` (The Parser):** A second, zero-temperature LLM prompt parses the analyst's report into a clean, machine-readable strategy signal (e.g., `Bull_Put_Spread`).
    3.  **`Cell 14` (The Risk Manager):** Takes the clean signal and applies your thesis's risk rules (e.g., 50bps fixed-fractional risk) to output a final, sized trade ticket.
    4.  **`Cell 15` (The Journal):** Logs the entire trade (date, pair, strategy, size, and all causal/vol drivers) to a master `trade_journal.csv` file.

---

## 🏗️ Project Structure

```

.
├── Notebook\_01\_ZB\_GC.ipynb
├── Notebook\_02\_BZ\_GC.ipynb
├── Notebook\_03\_CHF\_EUR.ipynb
├── Notebook\_04\_CHF\_GC.ipynb
├── trade\_journal.csv
├── requirements.txt
└── README.md

````

---

## 🛠️ Technology Stack

* **Core:** Python 3.10+, Jupyter Notebook
* **Data & Analysis:** `pandas`, `numpy`, `yfinance`, `fredapi`, `requests`, `scipy`
* **AI / LLM:** A local LLM server (e.g., [Ollama](https://ollama.com/))
* **Visualization:** `matplotlib`

---

## 🚀 Setup & Installation

### 1. Install Requirements

Create a virtual environment, activate it, and install the necessary libraries.

**`requirements.txt`:**
```txt
pandas
numpy
jupyter
yfinance
fredapi
requests
scipy
matplotlib
````

Run the installation:

```bash
pip install -r requirements.txt
```

### 2\. Set Up Local LLM (Ollama)

This project requires a local LLM server. The prompts are optimized for models like `qwen2.5:7b` or `llama3`.

1.  Download and install [Ollama](https://ollama.com/).
2.  Pull your model of choice. (e.g., `ollama pull qwen2.5:7b`)
3.  Ensure Ollama is running in the background. The scripts are hard-coded to hit `http://127.0.0.1:11434`.

### 3\. Set FRED API Key

The notebooks require a FRED (Federal Reserve Economic Data) API key.

1.  Get your free key here: [https://fred.stlouisfed.org/](https://fred.stlouisfed.org/)
2.  Open **`Cell 2`** in any notebook.
3.  Paste your key into the `os.environ.setdefault("FRED_API_KEY", "YOUR_KEY_HERE")` line.

### 4\. Set Risk Parameters

Open **`Cell 14`** in any notebook to configure your trading risk.

  * `ACCOUNT_VALUE = 100000.00` (Set your total paper-trading capital)
  * `RISK_BPS_PER_TRADE = 50` (Set your risk per idea in basis points)

-----

## workflow (How to Use)

This system is designed for **manual, discretionary swing trading**, not high-frequency automation. You are the "Intelligence Desk" operator.

Your weekly/monthly workflow is:

1.  **Open a Notebook** (e.g., `Notebook_01_ZB_GC.ipynb`).
2.  **Run Cells 1-11a:** This fetches all new data and generates the causal and volatility charts.
3.  **Analyze the Charts:** Form your own human opinion. *Do you agree with the charts?*
4.  **Run `Cell 12` (The Analyst):** Read the LLM's full-text synthesis. This is your "second opinion" and reasoning.
5.  **Run `Cell 13` (The Parser):** This confirms the machine-readable signal (e.g., `Bull_Put_Spread`).
6.  **Run `Cell 14` (The Risk Manager):** This outputs the final, sized trade ticket (e.g., "Sell 2 contracts...").
7.  **Run `Cell 15` (The Journal):** This saves the entire trade idea to your `trade_journal.csv`.
8.  **Execute (Paper Trade):** Manually place the trade from `Cell 14` in your paper-trading account.
9.  **Repeat** for the other 3 notebooks as needed.

Over time, your `trade_journal.csv` becomes the data source for your 12-month track record.

## 🔮 Future Work

  * **Backtesting:** Build `Notebook_05_Backtester.ipynb` to load `trade_journal.csv` and analyze the historical performance of the LLM's recommendations.
  * **Execution:** Connect the `Cell 14` trade ticket output to a broker's API for automated paper-trade execution.
  * **Dashboarding:** Consolidate the four notebooks into a single `main.py` script that feeds a web dashboard (e.g., Streamlit or Dash).

<!-- end list -->

```
```