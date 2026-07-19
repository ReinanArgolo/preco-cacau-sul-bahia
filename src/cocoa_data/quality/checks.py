from __future__ import annotations

from datetime import date
from statistics import mean, stdev
from typing import Any

from sqlalchemy import func, select

from cocoa_data.database import Repository
from cocoa_data.settings import Settings


def _event(
    source: str,
    check_name: str,
    severity: str,
    message: str,
    observation_date: date | None = None,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "source": source,
        "check_name": check_name,
        "severity": severity,
        "message": message,
        "observation_date": observation_date,
        "details": details or {},
    }


def extreme_movements(rows: list[tuple[date, float]], z_limit: float = 3.0) -> list[dict[str, Any]]:
    """Flag daily returns whose absolute z-score is above the configured limit."""
    ordered = sorted(rows)
    changes = [
        (day, (value / previous) - 1)
        for (day, value), (_, previous) in zip(ordered[1:], ordered[:-1], strict=False)
        if previous > 0
    ]
    if len(changes) < 3:
        return []
    values = [change for _, change in changes]
    sigma = stdev(values)
    if sigma == 0:
        return []
    center = mean(values)
    return [
        {"date": day, "change": change, "z_score": (change - center) / sigma}
        for day, change in changes
        if abs((change - center) / sigma) > z_limit
    ]


def run_quality_checks(repository: Repository, settings: Settings) -> list[dict[str, Any]]:
    repository.reflect()
    events: list[dict[str, Any]] = []
    today = date.today()
    checks = [
        ("market_prices_daily", "seagri", "observation_date"),
        ("market_prices_daily", "icco", "observation_date"),
        ("exchange_rates_daily", "bcb", "observation_date"),
        ("weather_daily", "open_meteo", "observation_date"),
        ("producer_prices_monthly", "conab", "reference_month"),
        ("municipal_production_annual", "ibge_sidra", "year"),
    ]
    with repository.engine.connect() as connection:
        for table_name, source, date_column in checks:
            table = repository.metadata.tables[table_name]
            latest = connection.scalar(
                select(func.max(getattr(table.c, date_column))).where(table.c.source == source)
            )
            if isinstance(latest, int):
                latest = date(latest, 12, 31)
            max_age = settings.quality["maximum_age_days"].get(
                "ibge" if source == "ibge_sidra" else "weather" if source == "open_meteo" else source,
                30,
            )
            if latest is None or (today - latest).days > max_age:
                severity = "error" if source in {"seagri", "bcb", "icco"} else "warning"
                events.append(
                    _event(
                        source,
                        "freshness",
                        severity,
                        f"Último dado: {latest or 'ausente'}; limite: {max_age} dias",
                        latest,
                        {"maximum_age_days": max_age},
                    )
                )

            if "available_at" in table.c:
                missing_temporality = connection.scalar(
                    select(func.count()).select_from(table).where(
                        (table.c.source == source) & table.c.available_at.is_(None)
                    )
                )
                if missing_temporality:
                    events.append(
                        _event(
                            source,
                            "temporal_completeness",
                            "error",
                            f"{missing_temporality} registros sem available_at",
                            details={"missing_rows": missing_temporality},
                        )
                    )

        market = repository.metadata.tables["market_prices_daily"]
        invalid = connection.execute(
            select(market.c.source, market.c.observation_date, market.c.price).where(
                (market.c.source == "seagri")
                & (
                    (market.c.price < settings.quality["price_min_brl_arroba"])
                    | (market.c.price > settings.quality["price_max_brl_arroba"])
                )
            )
        )
        for row in invalid:
            events.append(
                _event(
                    row.source,
                    "price_range",
                    "warning",
                    f"Preço fora da faixa operacional: {row.price}",
                    row.observation_date,
                )
            )

        local_rows = [
            (row.observation_date, float(row.price))
            for row in connection.execute(
                select(market.c.observation_date, market.c.price)
                .where(market.c.source == "seagri")
                .order_by(market.c.observation_date)
            )
        ]
        for movement in extreme_movements(local_rows):
            events.append(
                _event(
                    "seagri",
                    "extreme_movement_manual_review",
                    "warning",
                    f"Movimento local extremo de {movement['change']:.1%}; requer conferência na fonte",
                    movement["date"],
                    {"z_score": round(movement["z_score"], 3), "reviewed": False},
                )
            )

        fx = repository.metadata.tables["exchange_rates_daily"]
        invalid_fx = connection.scalar(
            select(func.count()).select_from(fx).where(
                (fx.c.source == "bcb")
                & (
                    (fx.c.sell_rate < settings.quality["ptax_min"])
                    | (fx.c.sell_rate > settings.quality["ptax_max"])
                )
            )
        )
        if invalid_fx:
            events.append(
                _event("bcb", "exchange_rate_range", "error", f"{invalid_fx} taxas fora da faixa")
            )

    repository.add_quality_events(events)
    return events
