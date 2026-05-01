from __future__ import annotations

import math


STRATEGY_RISK_PER_CONTRACT = {
    "Bull_Put_Spread": 350,
    "Bear_Call_Spread": 350,
    "Iron_Condor": 300,
    "Calendar_Spread": 150,
    "Diagonal_Spread": 200,
    "Double_Diagonal_Spread": 100,
    "No_Trade": 0,
}


def _size_from_budget(strategy_name: str, risk_budget_usd: float) -> int:
    if strategy_name == "No_Trade" or strategy_name not in STRATEGY_RISK_PER_CONTRACT:
        return 0
    risk_per_unit = STRATEGY_RISK_PER_CONTRACT[strategy_name]
    if risk_per_unit <= 0:
        return 0
    return max(1, math.floor(risk_budget_usd / risk_per_unit))


def size_single_strategy(
    strategy_name: str,
    *,
    account_value: float = 100000.0,
    risk_bps_per_trade: float = 50.0,
) -> dict[str, float | int | str]:
    risk_budget_usd = account_value * (risk_bps_per_trade / 10000.0)
    contracts = _size_from_budget(strategy_name, risk_budget_usd)
    return {
        "strategy": strategy_name,
        "contracts": contracts,
        "risk_budget_usd": risk_budget_usd,
    }


def size_pair_strategies(
    left_strategy: str,
    right_strategy: str,
    *,
    account_value: float = 100000.0,
    risk_bps_per_trade: float = 50.0,
) -> dict[str, float | int | str]:
    per_leg_bps = risk_bps_per_trade / 2.0
    per_leg_budget = account_value * (per_leg_bps / 10000.0)
    left_contracts = _size_from_budget(left_strategy, per_leg_budget)
    right_contracts = _size_from_budget(right_strategy, per_leg_budget)
    return {
        "left_strategy": left_strategy,
        "right_strategy": right_strategy,
        "left_contracts": left_contracts,
        "right_contracts": right_contracts,
        "per_leg_budget_usd": per_leg_budget,
        "total_budget_usd": per_leg_budget * 2,
    }
