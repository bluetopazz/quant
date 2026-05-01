from __future__ import annotations

import pandas as pd


PROMPT_VERSION = "pair_prompts_v2"


def build_single_strategy_parser_prompt(report: str, strategy_list: list[str] | tuple[str, ...]) -> str:
    return f"""
You are a simple parsing bot. Read the following analyst report. Your only job is to identify which strategy from the provided list was recommended.

Strategy List: {", ".join(strategy_list)}

Analyst Report:
\"\"\"{report}\"\"\"

Respond with only the single exact strategy name from the list.
""".strip()


def _build_zbgc_prompt(latest_data: pd.Series) -> str:
    target_asset = "GLD" if latest_data["GLD_TLT_Spread_Norm"] > 0 else "TLT"
    macro_summary = f"""
--- MACRO THEME (Pair: ZB/GC) ---
- **Thematic Bias:** Sovereign Risk (GLD outperforming TLT)
- **Signal Strength (Z-Score):** {latest_data['GLD_TLT_Spread_Norm']:.2f}
- **Signal Velocity (5D Change):** {latest_data['Signal_Velocity_5D']:.2f}
- **Regime Type (90D Corr):** {latest_data['Corr_90D']:.3f} (Low/Negative = Trend, High = Range)
"""

    if target_asset == "GLD":
        vol_summary = f"""
--- VOLATILITY DASHBOARD (Asset: GLD) ---
- **Implied Vol (GVZCLS):** {latest_data['GVZCLS']:.2f}
- **IV Rank (1-Year):** {latest_data['GVZ_IVR_252D']:.1f}%
- **Vol Risk Premium (IV vs HV):** {latest_data['GLD_VRP']:.2f} (Positive = "Expensive", Negative = "Cheap")
"""
    else:
        vol_summary = f"""
--- VOLATILITY DASHBOARD (Asset: TLT) ---
- **Implied Vol (VIX Proxy):** {latest_data['VIXCLS']:.2f}
- **IV Rank (1-Year):** {latest_data['TYVIX_IVR_252D']:.1f}%
- **Vol Risk Premium (IV vs HV):** {latest_data['TLT_VRP']:.2f} (Positive = "Expensive", Negative = "Cheap")
"""

    return f"""
**Role:** You are an Independent Intelligence Desk Analyst.

**Your Available Strategies:**
* Bull_Put_Spread, Bear_Call_Spread, Iron_Condor (Sell Premium)
* Calendar_Spread, Diagonal_Spread, Double_Diagonal_Spread (Buy Vega)
* No_Trade

**Latest OSINT Data:**
{macro_summary}
{vol_summary}

**Your Task (Provide a 3-part recommendation):**
1. **Volatility Regime:** Based on IV Rank and VRP, is volatility "High/Expensive" or "Low/Cheap"? Explain why this favors selling premium or buying vega.
2. **Thematic Regime:** Based on Signal Strength, Velocity, and Correlation, is the macro theme a "Strong Trend," a "Weak Trend," or a "Range/Chop"? Explain your reasoning.
3. **Strategy Route:** Combine these two analyses to select the optimal strategy for {target_asset}. Explain why this strategy is the best fit for the current macro and volatility regime.
""".strip()


def _build_bzgc_prompt(latest_data: pd.Series) -> str:
    directional_bias = "Long GLD / Short BNO" if latest_data["GLD_BNO_Spread_Norm"] > 0 else "Long BNO / Short GLD"
    return f"""
**Role:** You are an Independent Intelligence Desk Analyst.

**Your Available Strategies:**
* Bull_Put_Spread, Bear_Call_Spread, Iron_Condor (Sell Premium)
* Calendar_Spread, Diagonal_Spread, Double_Diagonal_Spread (Buy Vega)
* No_Trade

**Latest OSINT Data:**
--- MACRO THEME (Pair: BZ/GC) ---
- **Thematic Bias:** Growth vs. Haven
- **Signal Strength (Z-Score):** {latest_data['GLD_BNO_Spread_Norm']:.2f}
- **Signal Velocity (5D Change):** {latest_data['Signal_Velocity_5D']:.2f}
- **Regime Type (90D Corr):** {latest_data['Corr_90D']:.3f} (Negative = Recession, Positive = Inflation/Geo)
- **Growth Driver (ISM PMI):** {latest_data['IPMAN']:.1f} (Critical level: 50)
- **Inflation Driver (Core CPI):** {latest_data['CPILFESL']:.2f}%

--- VOLATILITY DASHBOARD ---
- **Gold (GLD) IV Rank:** {latest_data['GVZ_IVR_252D']:.1f}%
- **Gold (GLD) VRP:** {latest_data['GLD_VRP']:.2f} (Positive = "Expensive")
- **Oil (BNO) IV Rank:** {latest_data['OVX_IVR_252D']:.1f}%
- **Oil (BNO) VRP:** {latest_data['BNO_VRP']:.2f} (Positive = "Expensive")

**Your Task (Provide a detailed 3-part recommendation):**
1. **Macro Thesis Check:** What is the primary thematic driver?
   * Is this a Recession Signal (`90D Corr` < 0, `IPMAN` < 50)?
   * Is this a Stagflation Signal (`IPMAN` < 50, `Core CPI` high)?
   * Or is this an Inflation/Geo Signal (`90D Corr` > 0)?
   * The current thematic bias based on the Z-Score is **{directional_bias}**.
   * Explain your reasoning in detail.
2. **Volatility Regimes:** Analyze volatility for both legs.
3. **Strategy Route (Pairs Trade):** Build the optimal pairs trade for **{directional_bias}** and explain each leg.

**CRITICAL:** Conclude your entire analysis with two, single, parsable lines:
ROUTED_STRATEGY_GLD: [strategy_name_for_GLD_leg]
ROUTED_STRATEGY_BNO: [strategy_name_for_BNO_leg]
(If a leg is not traded, use: No_Trade)
""".strip()


def _build_chfeur_prompt(latest_data: pd.Series) -> str:
    target_asset = "FXE (via Short EUR)" if latest_data["CHF_EUR_Spread_Norm"] > 0 else "FXE (via Long EUR)"
    directional_bias = "Bearish" if latest_data["CHF_EUR_Spread_Norm"] > 0 else "Bullish"
    return f"""
**Role:** You are an Independent Intelligence Desk Analyst.

**Your Available Strategies:**
* Bull_Put_Spread, Bear_Call_Spread, Iron_Condor (Sell Premium)
* Calendar_Spread, Diagonal_Spread, Double_Diagonal_Spread (Buy Vega)
* No_Trade

**Latest OSINT Data:**
--- MACRO THEME (Pair: CHF/EUR) ---
- **Thematic Bias:** European Divergence
- **Signal Strength (Z-Score):** {latest_data['CHF_EUR_Spread_Norm']:.2f}
- **Signal Velocity (5D Change):** {latest_data['Signal_Velocity_5D']:.2f}
- **Regime Type (90D Corr):** {latest_data['Corr_90D']:.3f} (High = USD-Driven, Low = Divergence)
- **EU Risk Driver (BTP-Bund):** {latest_data['EU_Risk_Spread']:.2f} bps
- **Policy Driver (Infl. Diff):** {latest_data['Inflation_Differential']:.2f}%

--- VOLATILITY DASHBOARD (Global Risk Proxy: VIX) ---
- **Implied Vol (VIXCLS):** {latest_data['VIXCLS']:.2f}
- **IV Rank (1-Year):** {latest_data['VIX_IVR_252D']:.1f}%
- **FXE VRP (VIX - HV):** {latest_data['FXE_VRP']:.2f} (Positive = "Expensive")
- **FXF VRP (VIX - HV):** {latest_data['FXF_VRP']:.2f} (Positive = "Expensive")

**Your Task (Provide a 3-part recommendation):**
1. **Volatility Regime:** Based on the VIX IV Rank, is global risk volatility "High/Expensive" or "Low/Cheap"? Explain why this favors selling premium or buying vega.
2. **Thematic Regime:** Based on Signal Strength, Correlation, and the `EU_Risk_Spread`, is the macro theme a "Strong Divergence" (Strong Trend) or a "Correlated Chop" (Range)? Explain your reasoning.
3. **Strategy Route:** Combine these two analyses to select the optimal strategy. The macro theme gives a **{directional_bias}** bias on **{target_asset}**. Explain why this strategy is the best fit.

**Routing Logic:**
* **High IVR (>50) + Strong Trend:** Use a directionally-biased credit spread.
* **High IVR (>50) + Range/Chop:** Use a neutral credit strategy.
* **Low IVR (<50) + Strong Trend:** Use a directionally-biased debit/vega strategy.
* **Low IVR (<50) + Range/Chop:** Use a neutral vega strategy or No_Trade.
""".strip()


def _build_chfgc_prompt(latest_data: pd.Series) -> str:
    directional_bias = "Long GLD / Short FXF" if latest_data["CHF_GLD_Spread_Norm"] < 0 else "Long FXF / Short GLD"
    return f"""
**Role:** You are an Independent Intelligence Desk Analyst.

**Your Available Strategies:**
* Bull_Put_Spread, Bear_Call_Spread, Iron_Condor (Sell Premium)
* Calendar_Spread, Diagonal_Spread, Double_Diagonal_Spread (Buy Vega)
* No_Trade

**Latest OSINT Data:**
--- MACRO THEME (Pair: CHF/GC) ---
- **Thematic Bias:** Managed vs. Unmanaged Haven
- **Signal Strength (Z-Score):** {latest_data['CHF_GLD_Spread_Norm']:.2f}
- **Signal Velocity (5D Change):** {latest_data['Signal_Velocity_5D']:.2f}
- **Regime Type (90D Corr):** {latest_data['Corr_90D']:.3f} (Positive = Correlated Haven, Low/Neg = Divergence)
- **SNB Intervention (WoW Change):** {latest_data['SNB_Intervention_WoW'] / 1e9:.2f} Billion

--- VOLATILITY DASHBOARD ---
- **Gold (GLD) IV Rank:** {latest_data['GVZ_IVR_252D']:.1f}%
- **Gold (GLD) VRP:** {latest_data['GLD_VRP']:.2f} (Positive = "Expensive")
- **CHF (FXF) IV Rank (VIX Proxy):** {latest_data['VIX_IVR_252D']:.1f}%
- **CHF (FXF) VRP:** {latest_data['FXF_VRP']:.2f} (Positive = "Expensive")

**Your Task (Provide a detailed 3-part recommendation):**
1. **Macro Thesis Check:** Is the SNB intervention signal active, or is this a simple correlated-haven trade? The current thematic bias is **{directional_bias}**. Explain in detail.
2. **Volatility Regimes:** Analyze volatility for both legs and explain why the combination matters for a pairs trade.
3. **Strategy Route (Pairs Trade):** Build the optimal pairs trade and explain each leg.

**CRITICAL:** Conclude your entire analysis with two, single, parsable lines:
ROUTED_STRATEGY_GLD: [strategy_name_for_GLD_leg]
ROUTED_STRATEGY_FXF: [strategy_name_for_FXF_leg]
(If a leg is not traded, use: No_Trade)
""".strip()


def build_analyst_prompt(pair_id: str, latest_data: pd.Series) -> str:
    if pair_id == "ZB_GC":
        return _build_zbgc_prompt(latest_data)
    if pair_id == "BZ_GC":
        return _build_bzgc_prompt(latest_data)
    if pair_id == "CHF_EUR":
        return _build_chfeur_prompt(latest_data)
    if pair_id == "CHF_GC":
        return _build_chfgc_prompt(latest_data)
    raise KeyError(f"Unknown pair_id: {pair_id}")
