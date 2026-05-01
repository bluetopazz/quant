from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

import pandas as pd

from .config.pairs import PairConfig, get_pair_config
from .config.settings import Settings
from .contracts import (
    AnalystMemo,
    ChartPayload,
    FeatureSnapshot,
    JournalEntryPreview,
    PairRunResult,
    ParsedSignal,
    RiskTicket,
    RunWarning,
)
from .data import fetch_fred_series, fetch_snb_sight_deposits, fetch_yfinance_prices, merge_frames_ffill
from .features import (
    add_historical_volatility,
    add_iv_rank,
    add_pct_change_columns,
    add_rolling_correlation,
    add_signal_velocity,
    add_vrp,
    apply_pair_specific_features,
    full_sample_zscore_frame,
)
from .llm import ALLOWED_STRATEGIES, ask_llm, build_analyst_prompt, build_single_strategy_parser_prompt
from .llm.parser import parse_routed_strategies, validate_strategy_name
from .llm.prompts import PROMPT_VERSION
from .risk import size_pair_strategies, size_single_strategy


ENGINE_VERSION = "platform_engine_v1"
DEFAULT_ACCOUNT_VALUE = 100000.0
DEFAULT_RISK_BPS_PER_TRADE = 50.0


PAIR_RUNTIME_SETTINGS: dict[str, dict[str, Any]] = {
    "ZB_GC": {
        "spread_column": "GLD_TLT_Spread_Norm",
        "ratio_column": "GLD_TLT_Ratio",
        "return_columns": ("GLD", "TLT"),
        "hv_columns": {"GLD_pct": "GLD_HV_30D", "TLT_pct": "TLT_HV_30D"},
        "ivr_columns": {"GVZCLS": "GVZ_IVR_252D", "VIXCLS": "TYVIX_IVR_252D"},
        "vrp_columns": {
            "GLD_VRP": ("GVZCLS", "GLD_HV_30D"),
            "TLT_VRP": ("VIXCLS", "TLT_HV_30D"),
        },
        "core_labels": ("GLD", "TLT"),
    },
    "BZ_GC": {
        "spread_column": "GLD_BNO_Spread_Norm",
        "ratio_column": "GLD_BNO_Ratio",
        "return_columns": ("GLD", "BNO"),
        "hv_columns": {"GLD_pct": "GLD_HV_30D", "BNO_pct": "BNO_HV_30D"},
        "ivr_columns": {"GVZCLS": "GVZ_IVR_252D", "OVXCLS": "OVX_IVR_252D"},
        "vrp_columns": {
            "GLD_VRP": ("GVZCLS", "GLD_HV_30D"),
            "BNO_VRP": ("OVXCLS", "BNO_HV_30D"),
        },
        "core_labels": ("GLD", "BNO"),
    },
    "CHF_EUR": {
        "spread_column": "CHF_EUR_Spread_Norm",
        "ratio_column": "CHF_EUR_Ratio",
        "return_columns": ("FXF", "FXE"),
        "hv_columns": {"FXF_pct": "FXF_HV_30D", "FXE_pct": "FXE_HV_30D"},
        "ivr_columns": {"VIXCLS": "VIX_IVR_252D"},
        "vrp_columns": {
            "FXE_VRP": ("VIXCLS", "FXE_HV_30D"),
            "FXF_VRP": ("VIXCLS", "FXF_HV_30D"),
        },
        "core_labels": ("FXF", "FXE"),
    },
    "CHF_GC": {
        "spread_column": "CHF_GLD_Spread_Norm",
        "ratio_column": "CHF_GLD_Ratio",
        "return_columns": ("FXF", "GLD"),
        "hv_columns": {"FXF_pct": "FXF_HV_30D", "GLD_pct": "GLD_HV_30D"},
        "ivr_columns": {"GVZCLS": "GVZ_IVR_252D", "VIXCLS": "VIX_IVR_252D"},
        "vrp_columns": {
            "GLD_VRP": ("GVZCLS", "GLD_HV_30D"),
            "FXF_VRP": ("VIXCLS", "FXF_HV_30D"),
        },
        "core_labels": ("FXF", "GLD"),
    },
}


def _to_python(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            return value
    return value


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _date_window(lookback_years: int) -> tuple[pd.Timestamp, pd.Timestamp]:
    end_date = pd.Timestamp.utcnow().tz_localize(None).normalize()
    start_date = end_date - pd.Timedelta(days=365 * lookback_years)
    return start_date, end_date


def _serialize_chart(
    *,
    chart_id: str,
    pair_id: str,
    family: str,
    title: str,
    render_kind: str,
    source: pd.DataFrame,
    columns: list[tuple[str, str, str | None]],
    limit: int = 260,
) -> ChartPayload:
    trimmed = source.copy().dropna(how="all").tail(limit)
    x_values = [pd.Timestamp(idx).strftime("%Y-%m-%d") for idx in trimmed.index]
    series = []
    for column_name, label, axis in columns:
        if column_name not in trimmed.columns:
            continue
        series.append(
            {
                "series_id": column_name,
                "label": label,
                "axis": axis,
                "values": [_to_python(value) for value in trimmed[column_name].tolist()],
            }
        )
    return ChartPayload(
        chart_id=chart_id,
        pair_id=pair_id,
        family=family,
        title=title,
        render_kind=render_kind,
        x_axis={"label": "Date", "values": x_values},
        series=series,
    )


def _build_chart_payloads(
    pair_config: PairConfig,
    raw_df: pd.DataFrame,
    normalized_df: pd.DataFrame,
    enriched_df: pd.DataFrame,
) -> list[ChartPayload]:
    runtime = PAIR_RUNTIME_SETTINGS[pair_config.pair_id]
    left_label, right_label = runtime["core_labels"]
    ratio_column = runtime["ratio_column"]
    spread_column = runtime["spread_column"]
    pair_id = pair_config.pair_id

    charts: list[ChartPayload] = []
    core_source = normalized_df[[left_label, right_label]].join(enriched_df[[ratio_column, spread_column]], how="inner")
    charts.append(
        _serialize_chart(
            chart_id=f"{pair_id}_core_normalized",
            pair_id=pair_id,
            family="core_normalized",
            title=f"{pair_id} Normalized Pair",
            render_kind="line",
            source=core_source,
            columns=[(left_label, left_label, None), (right_label, right_label, None)],
        )
    )
    charts.append(
        _serialize_chart(
            chart_id=f"{pair_id}_core_ratio",
            pair_id=pair_id,
            family="core_ratio",
            title=f"{pair_id} Ratio",
            render_kind="line",
            source=core_source[[ratio_column]],
            columns=[(ratio_column, ratio_column, None)],
        )
    )
    charts.append(
        _serialize_chart(
            chart_id=f"{pair_id}_core_spread",
            pair_id=pair_id,
            family="core_spread",
            title=f"{pair_id} Spread",
            render_kind="line",
            source=core_source[[spread_column]],
            columns=[(spread_column, spread_column, None)],
        )
    )

    if pair_id == "ZB_GC":
        charts.append(
            _serialize_chart(
                chart_id="ZB_GC_causal_real_yields",
                pair_id=pair_id,
                family="causal_driver",
                title="Gold vs Real Yields",
                render_kind="line",
                source=enriched_df[["GLD_TLT_Spread_Norm", "DFII10"]],
                columns=[("GLD_TLT_Spread_Norm", "GLD_TLT_Spread_Norm", "left"), ("DFII10", "DFII10", "right")],
            )
        )
    elif pair_id == "BZ_GC":
        charts.append(
            _serialize_chart(
                chart_id="BZ_GC_causal_growth",
                pair_id=pair_id,
                family="causal_driver",
                title="Ratio vs Growth Proxy",
                render_kind="line",
                source=enriched_df[["GLD_BNO_Ratio", "IPMAN"]],
                columns=[("GLD_BNO_Ratio", "GLD_BNO_Ratio", "left"), ("IPMAN", "IPMAN", "right")],
            )
        )
    elif pair_id == "CHF_EUR":
        charts.append(
            _serialize_chart(
                chart_id="CHF_EUR_causal_eu_risk",
                pair_id=pair_id,
                family="causal_driver",
                title="Ratio vs EU Risk Spread",
                render_kind="line",
                source=enriched_df[["CHF_EUR_Ratio", "EU_Risk_Spread"]],
                columns=[("CHF_EUR_Ratio", "CHF_EUR_Ratio", "left"), ("EU_Risk_Spread", "EU_Risk_Spread", "right")],
            )
        )
        charts.append(
            _serialize_chart(
                chart_id="CHF_EUR_causal_inflation_diff",
                pair_id=pair_id,
                family="causal_driver",
                title="Ratio vs Inflation Differential",
                render_kind="line",
                source=enriched_df[["CHF_EUR_Ratio", "Inflation_Differential"]],
                columns=[
                    ("CHF_EUR_Ratio", "CHF_EUR_Ratio", "left"),
                    ("Inflation_Differential", "Inflation_Differential", "right"),
                ],
            )
        )
    else:
        charts.append(
            _serialize_chart(
                chart_id="CHF_GC_causal_intervention",
                pair_id=pair_id,
                family="causal_driver",
                title="Ratio vs SNB Intervention",
                render_kind="bar",
                source=enriched_df[["CHF_GLD_Ratio", "SNB_Intervention_WoW"]],
                columns=[
                    ("CHF_GLD_Ratio", "CHF_GLD_Ratio", "left"),
                    ("SNB_Intervention_WoW", "SNB_Intervention_WoW", "right"),
                ],
            )
        )

    correlation_columns = [column for column in ("Corr_30D", "Corr_90D") if column in enriched_df.columns]
    if correlation_columns:
        charts.append(
            _serialize_chart(
                chart_id=f"{pair_id}_correlation",
                pair_id=pair_id,
                family="correlation",
                title="Rolling Correlation",
                render_kind="line",
                source=enriched_df[correlation_columns],
                columns=[(column, column, None) for column in correlation_columns],
            )
        )

    vol_columns = [column for column in enriched_df.columns if column.endswith("_IVR_252D") or column.endswith("_VRP")]
    if vol_columns:
        charts.append(
            _serialize_chart(
                chart_id=f"{pair_id}_volatility",
                pair_id=pair_id,
                family="volatility",
                title="Volatility Dashboard",
                render_kind="line",
                source=enriched_df[vol_columns],
                columns=[(column, column, None) for column in vol_columns],
            )
        )
    return charts


def _apply_common_features(pair_id: str, df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    runtime = PAIR_RUNTIME_SETTINGS[pair_id]
    normalized_df = full_sample_zscore_frame(df)
    enriched = apply_pair_specific_features(pair_id, df, normalized_df)
    enriched = add_pct_change_columns(enriched, list(runtime["return_columns"]))
    left_return = f"{runtime['return_columns'][0]}_pct"
    right_return = f"{runtime['return_columns'][1]}_pct"
    enriched = add_rolling_correlation(enriched, left_return, right_return)
    enriched = add_historical_volatility(enriched, runtime["hv_columns"])
    enriched = add_iv_rank(enriched, runtime["ivr_columns"])
    enriched = add_vrp(enriched, runtime["vrp_columns"])
    enriched = add_signal_velocity(enriched, runtime["spread_column"], "Signal_Velocity_5D")
    return normalized_df, enriched


def _derive_signal_context(pair_id: str, latest_data: pd.Series) -> dict[str, Any]:
    if pair_id == "ZB_GC":
        target_asset = "GLD" if latest_data["GLD_TLT_Spread_Norm"] > 0 else "TLT"
        return {"target_asset": target_asset}
    if pair_id == "CHF_EUR":
        if latest_data["CHF_EUR_Spread_Norm"] > 0:
            return {"target_asset": "FXE (via Short EUR)", "directional_bias": "Bearish"}
        return {"target_asset": "FXE (via Long EUR)", "directional_bias": "Bullish"}
    if pair_id == "BZ_GC":
        bias = "Long GLD / Short BNO" if latest_data["GLD_BNO_Spread_Norm"] > 0 else "Long BNO / Short GLD"
        return {"directional_bias": bias}
    if pair_id == "CHF_GC":
        bias = "Long GLD / Short FXF" if latest_data["CHF_GLD_Spread_Norm"] < 0 else "Long FXF / Short GLD"
        return {"directional_bias": bias}
    raise KeyError(f"Unknown pair_id: {pair_id}")


def _build_feature_snapshot(pair_id: str, latest_timestamp: pd.Timestamp, latest_data: pd.Series) -> FeatureSnapshot:
    runtime = PAIR_RUNTIME_SETTINGS[pair_id]
    core_metrics = {
        "signal_zscore": _to_python(latest_data.get(runtime["spread_column"])),
        "signal_velocity_5d": _to_python(latest_data.get("Signal_Velocity_5D")),
        "corr_30d": _to_python(latest_data.get("Corr_30D")),
        "corr_90d": _to_python(latest_data.get("Corr_90D")),
        "ratio": _to_python(latest_data.get(runtime["ratio_column"])),
        "spread_value": _to_python(latest_data.get(runtime["spread_column"])),
        "left_leg_last": _to_python(latest_data.get(runtime["core_labels"][0])),
        "right_leg_last": _to_python(latest_data.get(runtime["core_labels"][1])),
    }

    if pair_id == "ZB_GC":
        pair_extensions = {
            "dfii10": _to_python(latest_data.get("DFII10")),
            "t10yie": _to_python(latest_data.get("T10YIE")),
            "dtwexbgs": _to_python(latest_data.get("DTWEXBGS")),
            "gld_ivr": _to_python(latest_data.get("GVZ_IVR_252D")),
            "tlt_ivr": _to_python(latest_data.get("TYVIX_IVR_252D")),
            "gld_vrp": _to_python(latest_data.get("GLD_VRP")),
            "tlt_vrp": _to_python(latest_data.get("TLT_VRP")),
            "target_asset_candidate": "GLD" if latest_data.get("GLD_TLT_Spread_Norm", 0) > 0 else "TLT",
        }
    elif pair_id == "BZ_GC":
        pair_extensions = {
            "ipman": _to_python(latest_data.get("IPMAN")),
            "cpilfesl": _to_python(latest_data.get("CPILFESL")),
            "gld_ivr": _to_python(latest_data.get("GVZ_IVR_252D")),
            "bno_ivr": _to_python(latest_data.get("OVX_IVR_252D")),
            "gld_vrp": _to_python(latest_data.get("GLD_VRP")),
            "bno_vrp": _to_python(latest_data.get("BNO_VRP")),
            "directional_bias_candidate": "Long GLD / Short BNO"
            if latest_data.get("GLD_BNO_Spread_Norm", 0) > 0
            else "Long BNO / Short GLD",
        }
    elif pair_id == "CHF_EUR":
        pair_extensions = {
            "eu_risk_spread": _to_python(latest_data.get("EU_Risk_Spread")),
            "inflation_differential": _to_python(latest_data.get("Inflation_Differential")),
            "vix_ivr": _to_python(latest_data.get("VIX_IVR_252D")),
            "fxe_vrp": _to_python(latest_data.get("FXE_VRP")),
            "fxf_vrp": _to_python(latest_data.get("FXF_VRP")),
            "target_asset_candidate": "FXE (via Short EUR)"
            if latest_data.get("CHF_EUR_Spread_Norm", 0) > 0
            else "FXE (via Long EUR)",
            "directional_bias_candidate": "Bearish"
            if latest_data.get("CHF_EUR_Spread_Norm", 0) > 0
            else "Bullish",
        }
    else:
        pair_extensions = {
            "snb_intervention_wow": _to_python(latest_data.get("SNB_Intervention_WoW")),
            "dfii10": _to_python(latest_data.get("DFII10")),
            "gld_ivr": _to_python(latest_data.get("GVZ_IVR_252D")),
            "chf_vix_ivr": _to_python(latest_data.get("VIX_IVR_252D")),
            "gld_vrp": _to_python(latest_data.get("GLD_VRP")),
            "fxf_vrp": _to_python(latest_data.get("FXF_VRP")),
            "directional_bias_candidate": "Long GLD / Short FXF"
            if latest_data.get("CHF_GLD_Spread_Norm", 0) < 0
            else "Long FXF / Short GLD",
        }

    return FeatureSnapshot(
        pair_id=pair_id,
        as_of_date=latest_timestamp.strftime("%Y-%m-%d"),
        core_metrics=core_metrics,
        pair_extensions=pair_extensions,
        normalization_mode="full_sample_zscore",
    )


def _parse_and_size(
    pair_id: str,
    settings: Settings,
    memo: AnalystMemo,
    latest_data: pd.Series,
) -> tuple[ParsedSignal, RiskTicket]:
    context = _derive_signal_context(pair_id, latest_data)

    if pair_id in {"ZB_GC", "CHF_EUR"}:
        parser_prompt = build_single_strategy_parser_prompt(memo.content, ALLOWED_STRATEGIES)
        parsed_strategy_raw = ask_llm(
            parser_prompt,
            base_url=settings.llm_base_url,
            model=settings.llm_model,
            temperature=0.0,
            timeout_seconds=settings.request_timeout_seconds,
        )
        strategy = validate_strategy_name(parsed_strategy_raw)
        parsed_signal = ParsedSignal(
            pair_id=pair_id,
            signal_style="single_strategy",
            parser_style="llm_second_pass",
            parser_version="parser_v1",
            parse_status="parsed_with_fallback" if strategy != parsed_strategy_raw.strip().strip("*") else "parsed",
            directional_bias=context.get("directional_bias"),
            target_asset=context.get("target_asset"),
            strategy=strategy,
            parser_input_memo_id=memo.memo_id,
            used_llm_second_pass=True,
            fallback_reason=None if strategy == parsed_strategy_raw.strip().strip("*") else "strategy_name_normalized",
            raw_parser_output=parsed_strategy_raw,
        )
        sizing = size_single_strategy(
            strategy,
            account_value=DEFAULT_ACCOUNT_VALUE,
            risk_bps_per_trade=DEFAULT_RISK_BPS_PER_TRADE,
        )
        risk_ticket = RiskTicket(
            pair_id=pair_id,
            sizing_mode="single_strategy",
            account_value_assumption=DEFAULT_ACCOUNT_VALUE,
            risk_bps_per_trade=DEFAULT_RISK_BPS_PER_TRADE,
            total_risk_budget_usd=_to_python(sizing.get("risk_budget_usd")),
            target_asset=context.get("target_asset"),
            strategy=strategy,
            contracts=int(sizing.get("contracts", 0)),
            risk_budget_usd=_to_python(sizing.get("risk_budget_usd")),
            strategy_risk_table_version="risk_table_v1",
            heuristic_name="fixed_bps_single_strategy",
            sizing_assumptions={
                "account_value": DEFAULT_ACCOUNT_VALUE,
                "risk_bps_per_trade": DEFAULT_RISK_BPS_PER_TRADE,
            },
        )
        return parsed_signal, risk_ticket

    if pair_id == "BZ_GC":
        parsed = parse_routed_strategies(memo.content, ("ROUTED_STRATEGY_GLD", "ROUTED_STRATEGY_BNO"))
        sizing = size_pair_strategies(
            parsed["ROUTED_STRATEGY_GLD"],
            parsed["ROUTED_STRATEGY_BNO"],
            account_value=DEFAULT_ACCOUNT_VALUE,
            risk_bps_per_trade=DEFAULT_RISK_BPS_PER_TRADE,
        )
        parsed_signal = ParsedSignal(
            pair_id=pair_id,
            signal_style="pair_routed",
            parser_style="routed_lines",
            parser_version="parser_v1",
            parse_status="parsed",
            directional_bias=context["directional_bias"],
            left_leg_label="GLD",
            right_leg_label="BNO",
            left_strategy=parsed["ROUTED_STRATEGY_GLD"],
            right_strategy=parsed["ROUTED_STRATEGY_BNO"],
            used_llm_second_pass=False,
        )
        risk_ticket = RiskTicket(
            pair_id=pair_id,
            sizing_mode="pair_routed",
            account_value_assumption=DEFAULT_ACCOUNT_VALUE,
            risk_bps_per_trade=DEFAULT_RISK_BPS_PER_TRADE,
            total_risk_budget_usd=_to_python(sizing.get("total_budget_usd")),
            left_strategy=parsed["ROUTED_STRATEGY_GLD"],
            right_strategy=parsed["ROUTED_STRATEGY_BNO"],
            left_contracts=int(sizing.get("left_contracts", 0)),
            right_contracts=int(sizing.get("right_contracts", 0)),
            per_leg_budget_usd=_to_python(sizing.get("per_leg_budget_usd")),
            total_budget_usd=_to_python(sizing.get("total_budget_usd")),
            strategy_risk_table_version="risk_table_v1",
            heuristic_name="fixed_bps_pair_routed",
            sizing_assumptions={
                "account_value": DEFAULT_ACCOUNT_VALUE,
                "risk_bps_per_trade": DEFAULT_RISK_BPS_PER_TRADE,
            },
        )
        return parsed_signal, risk_ticket

    parsed = parse_routed_strategies(memo.content, ("ROUTED_STRATEGY_GLD", "ROUTED_STRATEGY_FXF"))
    sizing = size_pair_strategies(
        parsed["ROUTED_STRATEGY_GLD"],
        parsed["ROUTED_STRATEGY_FXF"],
        account_value=DEFAULT_ACCOUNT_VALUE,
        risk_bps_per_trade=DEFAULT_RISK_BPS_PER_TRADE,
    )
    parsed_signal = ParsedSignal(
        pair_id=pair_id,
        signal_style="pair_routed",
        parser_style="routed_lines",
        parser_version="parser_v1",
        parse_status="parsed",
        directional_bias=context["directional_bias"],
        left_leg_label="GLD",
        right_leg_label="FXF",
        left_strategy=parsed["ROUTED_STRATEGY_GLD"],
        right_strategy=parsed["ROUTED_STRATEGY_FXF"],
        used_llm_second_pass=False,
    )
    risk_ticket = RiskTicket(
        pair_id=pair_id,
        sizing_mode="pair_routed",
        account_value_assumption=DEFAULT_ACCOUNT_VALUE,
        risk_bps_per_trade=DEFAULT_RISK_BPS_PER_TRADE,
        total_risk_budget_usd=_to_python(sizing.get("total_budget_usd")),
        left_strategy=parsed["ROUTED_STRATEGY_GLD"],
        right_strategy=parsed["ROUTED_STRATEGY_FXF"],
        left_contracts=int(sizing.get("left_contracts", 0)),
        right_contracts=int(sizing.get("right_contracts", 0)),
        per_leg_budget_usd=_to_python(sizing.get("per_leg_budget_usd")),
        total_budget_usd=_to_python(sizing.get("total_budget_usd")),
        strategy_risk_table_version="risk_table_v1",
        heuristic_name="fixed_bps_pair_routed",
        sizing_assumptions={
            "account_value": DEFAULT_ACCOUNT_VALUE,
            "risk_bps_per_trade": DEFAULT_RISK_BPS_PER_TRADE,
        },
    )
    return parsed_signal, risk_ticket


def _build_journal_entry_preview(
    pair_id: str,
    latest_timestamp: pd.Timestamp,
    latest_data: pd.Series,
    memo: AnalystMemo,
    parsed_signal: ParsedSignal,
    risk_ticket: RiskTicket,
) -> JournalEntryPreview:
    if pair_id == "ZB_GC":
        payload = {
            "Date": latest_timestamp.strftime("%Y-%m-%d"),
            "Pair": "ZB_GC",
            "Theme": "Sovereign_Risk",
            "Target_Asset": parsed_signal.target_asset,
            "Strategy": parsed_signal.strategy,
            "Contracts_Sized": risk_ticket.contracts,
            "Signal_ZScore": _to_python(latest_data.get("GLD_TLT_Spread_Norm")),
            "Signal_Velocity_5D": _to_python(latest_data.get("Signal_Velocity_5D")),
            "Corr_90D": _to_python(latest_data.get("Corr_90D")),
            "GLD_IVR": _to_python(latest_data.get("GVZ_IVR_252D")),
            "TLT_IVR": _to_python(latest_data.get("TYVIX_IVR_252D")),
            "GLD_VRP": _to_python(latest_data.get("GLD_VRP")),
            "TLT_VRP": _to_python(latest_data.get("TLT_VRP")),
            "DFII10": _to_python(latest_data.get("DFII10")),
            "T10YIE": _to_python(latest_data.get("T10YIE")),
            "DTWEXBGS": _to_python(latest_data.get("DTWEXBGS")),
            "Analyst_Reasoning": memo.content,
        }
    elif pair_id == "CHF_EUR":
        payload = {
            "Date": latest_timestamp.strftime("%Y-%m-%d"),
            "Pair": "CHF_EUR",
            "Theme": "European_Divergence",
            "Target_Asset": parsed_signal.target_asset,
            "Strategy": parsed_signal.strategy,
            "Contracts_Sized": risk_ticket.contracts,
            "Signal_ZScore": _to_python(latest_data.get("CHF_EUR_Spread_Norm")),
            "Signal_Velocity_5D": _to_python(latest_data.get("Signal_Velocity_5D")),
            "Corr_90D": _to_python(latest_data.get("Corr_90D")),
            "VIX_IVR": _to_python(latest_data.get("VIX_IVR_252D")),
            "FXE_VRP": _to_python(latest_data.get("FXE_VRP")),
            "FXF_VRP": _to_python(latest_data.get("FXF_VRP")),
            "EU_Risk_Spread": _to_python(latest_data.get("EU_Risk_Spread")),
            "Inflation_Differential": _to_python(latest_data.get("Inflation_Differential")),
            "Analyst_Reasoning": memo.content,
        }
    elif pair_id == "BZ_GC":
        payload = {
            "Date": latest_timestamp.strftime("%Y-%m-%d"),
            "Pair": "BZ_GC",
            "Theme": "Growth_vs_Haven",
            "Directional_Bias": parsed_signal.directional_bias,
            "Strategy_GLD": parsed_signal.left_strategy,
            "Contracts_GLD": risk_ticket.left_contracts,
            "Strategy_BNO": parsed_signal.right_strategy,
            "Contracts_BNO": risk_ticket.right_contracts,
            "Signal_ZScore": _to_python(latest_data.get("GLD_BNO_Spread_Norm")),
            "Signal_Velocity_5D": _to_python(latest_data.get("Signal_Velocity_5D")),
            "Corr_90D": _to_python(latest_data.get("Corr_90D")),
            "GLD_IVR": _to_python(latest_data.get("GVZ_IVR_252D")),
            "BNO_IVR": _to_python(latest_data.get("OVX_IVR_252D")),
            "GLD_VRP": _to_python(latest_data.get("GLD_VRP")),
            "BNO_VRP": _to_python(latest_data.get("BNO_VRP")),
            "IPMAN": _to_python(latest_data.get("IPMAN")),
            "CPILFESL": _to_python(latest_data.get("CPILFESL")),
            "Analyst_Reasoning": memo.content,
        }
    else:
        payload = {
            "Date": latest_timestamp.strftime("%Y-%m-%d"),
            "Pair": "CHF_GC",
            "Theme": "Managed_vs_Unmanaged_Haven",
            "Directional_Bias": parsed_signal.directional_bias,
            "Strategy_GLD": parsed_signal.left_strategy,
            "Contracts_GLD": risk_ticket.left_contracts,
            "Strategy_FXF": parsed_signal.right_strategy,
            "Contracts_FXF": risk_ticket.right_contracts,
            "Signal_ZScore": _to_python(latest_data.get("CHF_GLD_Spread_Norm")),
            "Signal_Velocity_5D": _to_python(latest_data.get("Signal_Velocity_5D")),
            "Corr_90D": _to_python(latest_data.get("Corr_90D")),
            "GLD_IVR": _to_python(latest_data.get("GVZ_IVR_252D")),
            "CHF_VIX_IVR": _to_python(latest_data.get("VIX_IVR_252D")),
            "GLD_VRP": _to_python(latest_data.get("GLD_VRP")),
            "FXF_VRP": _to_python(latest_data.get("FXF_VRP")),
            "DFII10": _to_python(latest_data.get("DFII10")),
            "SNB_Intervention_WoW": _to_python(latest_data.get("SNB_Intervention_WoW")),
            "Analyst_Reasoning": memo.content,
        }
    return JournalEntryPreview(
        pair_id=pair_id,
        journal_schema_version="csv_legacy_v1",
        journal_mode="csv_legacy_compatible",
        preview_payload=payload,
    )


def _build_warnings(
    market_failures: list[tuple[str, str]],
    fred_failures: list[tuple[str, str]],
    pair_id: str,
) -> list[RunWarning]:
    warnings: list[RunWarning] = []
    for source, message in market_failures:
        warnings.append(
            RunWarning(
                warning_code="MARKET_DATA_PARTIAL_FAILURE",
                stage="fetching_market_data",
                message=message,
                source=source,
                severity="medium",
            )
        )
    for source, message in fred_failures:
        warnings.append(
            RunWarning(
                warning_code="MACRO_DATA_PARTIAL_FAILURE",
                stage="fetching_macro_data",
                message=message,
                source=source,
                severity="medium",
            )
        )
    return warnings


def run_pair_analysis(
    pair_id: str,
    *,
    settings: Settings | None = None,
    lookback_years: int = 5,
) -> PairRunResult:
    settings = settings or Settings.from_env()
    pair_config = get_pair_config(pair_id)
    runtime = PAIR_RUNTIME_SETTINGS[pair_id]
    start_date, end_date = _date_window(lookback_years)

    market_df, market_failures = fetch_yfinance_prices(pair_config.yfinance_tickers, start_date, end_date)
    fred_df, fred_failures = fetch_fred_series(
        pair_config.fred_series_ids,
        start_date,
        end_date,
        api_key=settings.require_fred_api_key(),
    )

    extra_frames: list[pd.DataFrame] = []
    if "SNB" in pair_config.external_apis:
        extra_frames.append(fetch_snb_sight_deposits(start_date, end_date, timeout_seconds=30))

    merged = merge_frames_ffill(
        [market_df, fred_df, *extra_frames],
        required_columns=list(pair_config.yfinance_tickers),
    )
    if merged.empty:
        error_messages = [f"{name}: {message}" for name, message in [*market_failures, *fred_failures]]
        raise RuntimeError(f"Could not build analysis frame for {pair_id}. Failures: {error_messages}")

    normalized_df, enriched = _apply_common_features(pair_id, merged)
    analysis_df = enriched.dropna(subset=[runtime["spread_column"], "Signal_Velocity_5D", "Corr_90D"])
    if analysis_df.empty:
        raise RuntimeError(f"No complete analysis rows were produced for {pair_id}.")

    latest_timestamp = pd.Timestamp(analysis_df.index[-1])
    latest_data = analysis_df.iloc[-1].copy()
    memo_content = ask_llm(
        build_analyst_prompt(pair_id, latest_data),
        base_url=settings.llm_base_url,
        model=settings.llm_model,
        temperature=0.1,
        timeout_seconds=settings.request_timeout_seconds,
    )
    memo = AnalystMemo(
        memo_id=f"memo_{uuid4().hex}",
        pair_id=pair_id,
        content=memo_content,
        model_name=settings.llm_model,
        prompt_version=PROMPT_VERSION,
        prompt_style=pair_config.prompt_style,
        prompt_template_id=f"{pair_id.lower()}_prompt",
        system_role="Independent Intelligence Desk Analyst",
        temperature=0.1,
        timeout_seconds=settings.request_timeout_seconds,
        generated_at=_now_utc().isoformat(),
        source_summary={
            "market_tickers": list(pair_config.yfinance_tickers),
            "fred_series_ids": list(pair_config.fred_series_ids),
            "external_apis": list(pair_config.external_apis),
        },
    )

    parsed_signal, risk_ticket = _parse_and_size(pair_id, settings, memo, latest_data)
    feature_snapshot = _build_feature_snapshot(pair_id, latest_timestamp, latest_data)
    charts = _build_chart_payloads(pair_config, merged, normalized_df, enriched)
    journal_preview = _build_journal_entry_preview(pair_id, latest_timestamp, latest_data, memo, parsed_signal, risk_ticket)
    warnings = _build_warnings(market_failures, fred_failures, pair_id)

    status = "degraded_success" if warnings else "success"
    run_timestamp = _now_utc().isoformat()
    return PairRunResult(
        run_id=f"run_{uuid4().hex}",
        pair_id=pair_id,
        status=status,
        run_timestamp=run_timestamp,
        feature_snapshot=feature_snapshot,
        charts=charts,
        analyst_memo=memo,
        parsed_signal=parsed_signal,
        risk_ticket=risk_ticket,
        journal_entry_preview=journal_preview,
        warnings=warnings,
        error=None,
        notebook_reference=pair_config.notebook_name,
        theme=pair_config.theme,
        relationship=pair_config.relationship,
        pair_prompt_style=pair_config.prompt_style,
        pair_signal_style=pair_config.signal_shape,
        prompt_version=PROMPT_VERSION,
        engine_version=ENGINE_VERSION,
    )
