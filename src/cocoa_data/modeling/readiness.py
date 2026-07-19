from __future__ import annotations

from datetime import date
from typing import Any


MIN_LOCAL_DATES = 750
MIN_SPAN_DAYS = 1_095


def evaluate_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    valid = [
        row
        for row in rows
        if row.get("source") == "seagri"
        and row.get("price") is not None
        and row.get("available_at") is not None
        and row.get("information_set") == "historical_observation"
    ]
    dates = sorted({date.fromisoformat(str(row["observation_date"])[:10]) for row in valid})
    span_days = (dates[-1] - dates[0]).days if len(dates) > 1 else 0
    checks = {
        "minimum_local_dates": len(dates) >= MIN_LOCAL_DATES,
        "minimum_calendar_span": span_days >= MIN_SPAN_DAYS,
        "temporal_availability_known": len(valid) == len(
            [row for row in rows if row.get("source") == "seagri" and row.get("price") is not None]
        ),
    }
    return {
        "ready": all(checks.values()),
        "checks": checks,
        "local_valid_dates": len(dates),
        "required_local_dates": MIN_LOCAL_DATES,
        "span_days": span_days,
        "required_span_days": MIN_SPAN_DAYS,
        "first_date": dates[0].isoformat() if dates else None,
        "last_date": dates[-1].isoformat() if dates else None,
        "message": (
            "Gate liberado para baselines temporais."
            if all(checks.values())
            else "Modelagem bloqueada: amplie o histórico local auditável antes de treinar."
        ),
    }


def evaluate_model_readiness(repository) -> dict[str, Any]:
    return evaluate_rows(repository.read_table("market_prices_daily"))
