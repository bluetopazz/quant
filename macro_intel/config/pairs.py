from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class PairConfig:
    pair_id: str
    notebook_name: str
    theme: str
    relationship: str
    yfinance_tickers: tuple[str, ...]
    fred_series_ids: tuple[str, ...]
    journal_file: str
    external_apis: tuple[str, ...] = ()
    feature_flags: tuple[str, ...] = ()
    prompt_style: str = "single_leg"
    parser_style: str = "llm_parser"
    signal_shape: str = "single_strategy"
    chart_metadata: dict[str, str] = field(default_factory=dict)
    special_handling_rules: tuple[str, ...] = ()


PAIR_REGISTRY: dict[str, PairConfig] = {
    "ZB_GC": PairConfig(
        pair_id="ZB_GC",
        notebook_name="10yrgc.ipynb",
        theme="Sovereign_Risk",
        relationship="GLD over TLT",
        yfinance_tickers=("GLD", "TLT"),
        fred_series_ids=("DFII10", "T10YIE", "DTWEXBGS", "GVZCLS", "VIXCLS"),
        journal_file="journal_zb_gc.csv",
        feature_flags=("ratio", "spread", "real_yield_driver", "volatility_dashboard"),
        prompt_style="single_leg",
        parser_style="llm_parser",
        signal_shape="single_strategy",
        chart_metadata={
            "core_title": "ZB/GC Thesis: Price Divergence & Ratio",
            "causal_title": "ZB/GC Causal Driver: Gold vs. Real Yields",
        },
        special_handling_rules=(
            "target asset chosen from sign of GLD_TLT_Spread_Norm",
            "uses VIX as current Treasury-vol proxy",
        ),
    ),
    "BZ_GC": PairConfig(
        pair_id="BZ_GC",
        notebook_name="crudegc.ipynb",
        theme="Growth_vs_Haven",
        relationship="GLD over BNO",
        yfinance_tickers=("GLD", "BNO"),
        fred_series_ids=("IPMAN", "CPILFESL", "DTWEXBGS", "GVZCLS", "OVXCLS"),
        journal_file="journal_bz_gc.csv",
        feature_flags=("ratio", "spread", "growth_driver", "two_leg_routing"),
        prompt_style="two_leg",
        parser_style="routed_lines",
        signal_shape="pair_routed",
        chart_metadata={
            "core_title": "BZ/GC Thesis: Price Divergence & Ratio",
            "causal_title": "BZ/GC Causal Driver: Ratio vs. Growth Proxy",
        },
        special_handling_rules=("conclude with ROUTED_STRATEGY_GLD and ROUTED_STRATEGY_BNO",),
    ),
    "CHF_EUR": PairConfig(
        pair_id="CHF_EUR",
        notebook_name="chfeur.ipynb",
        theme="European_Divergence",
        relationship="FXF over FXE",
        yfinance_tickers=("FXF", "FXE"),
        fred_series_ids=(
            "IRLTLT01ITM156N",
            "IRLTLT01DEM156N",
            "CPALTT01CHM657N",
            "CP0000EZ19M086NEST",
            "VIXCLS",
        ),
        journal_file="journal_chf_eur.csv",
        feature_flags=("ratio", "spread", "eu_risk_spread", "inflation_differential"),
        prompt_style="single_leg",
        parser_style="llm_parser",
        signal_shape="single_strategy",
        chart_metadata={
            "core_title": "CHF/EUR Thesis: Price Divergence & Ratio",
            "causal_title": "CHF/EUR Causal Drivers",
        },
        special_handling_rules=("target asset expressed through FXE direction strings",),
    ),
    "CHF_GC": PairConfig(
        pair_id="CHF_GC",
        notebook_name="chfgc.ipynb",
        theme="Managed_vs_Unmanaged_Haven",
        relationship="FXF over GLD",
        yfinance_tickers=("FXF", "GLD"),
        fred_series_ids=("DFII10", "GVZCLS", "VIXCLS"),
        journal_file="journal_chf_gc.csv",
        external_apis=("SNB",),
        feature_flags=("ratio", "spread", "snb_intervention", "two_leg_routing"),
        prompt_style="two_leg",
        parser_style="routed_lines",
        signal_shape="pair_routed",
        chart_metadata={
            "core_title": "CHF/GC Thesis: Price Divergence & Ratio",
            "causal_title": "CHF/GC Causal Driver: Ratio vs. SNB Intervention",
        },
        special_handling_rules=(
            "fetch SNB sight deposits directly",
            "conclude with ROUTED_STRATEGY_GLD and ROUTED_STRATEGY_FXF",
        ),
    ),
}


def get_pair_config(pair_id: str) -> PairConfig:
    try:
        return PAIR_REGISTRY[pair_id]
    except KeyError as exc:
        raise KeyError(f"Unknown pair_id: {pair_id}") from exc
