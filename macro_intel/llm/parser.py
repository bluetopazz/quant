from __future__ import annotations

ALLOWED_STRATEGIES = (
    "Bull_Put_Spread",
    "Bear_Call_Spread",
    "Iron_Condor",
    "Calendar_Spread",
    "Diagonal_Spread",
    "Double_Diagonal_Spread",
    "No_Trade",
)


def validate_strategy_name(strategy_name: str, *, fallback: str = "No_Trade") -> str:
    cleaned = strategy_name.strip().strip("*")
    return cleaned if cleaned in ALLOWED_STRATEGIES else fallback


def parse_routed_strategies(report: str, labels: tuple[str, ...]) -> dict[str, str]:
    results = {label: "No_Trade" for label in labels}
    for line in report.splitlines():
        cleaned = line.strip(" *")
        for label in labels:
            prefix = f"{label}:"
            if cleaned.startswith(prefix):
                results[label] = validate_strategy_name(cleaned.split(":", 1)[1])
    return results
