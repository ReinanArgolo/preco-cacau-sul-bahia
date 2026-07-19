from __future__ import annotations

import json
import warnings
from pathlib import Path

import pandas as pd
import polars as pl

from cocoa_data.settings import Settings


def _frame(repository, name: str) -> pd.DataFrame:
    rows = repository.read_table(name)
    return pd.DataFrame(rows).copy()


def build_analysis_dataset(repository, settings: Settings) -> dict[str, Path]:
    output = settings.root / "data" / "processed"
    output.mkdir(parents=True, exist_ok=True)
    market = _frame(repository, "market_prices_daily")
    fx = _frame(repository, "exchange_rates_daily")
    weather = _frame(repository, "weather_daily")
    conab = _frame(repository, "producer_prices_monthly")
    production = _frame(repository, "municipal_production_annual")
    costs = _frame(repository, "production_costs")

    if market.empty:
        daily = pd.DataFrame(columns=["date"])
    else:
        market = market.copy()
        market.loc[:, "observation_date"] = pd.to_datetime(market["observation_date"])
        seagri = market[market["source"] == "seagri"][["observation_date", "price"]].rename(
            columns={"observation_date": "date", "price": "ilheus_brl_arroba"}
        )
        icco = market[market["source"] == "icco"][["observation_date", "price"]].rename(
            columns={"observation_date": "date", "price": "icco_usd_tonne"}
        )
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message="Dtype inference on a pandas object.*",
                category=FutureWarning,
            )
            daily = (
                pd.concat(
                    [seagri.set_index("date"), icco.set_index("date")],
                    axis=1,
                    join="outer",
                )
                .sort_index()
                .reset_index()
            )
        if not fx.empty:
            fx = fx.copy()
            fx.loc[:, "observation_date"] = pd.to_datetime(fx["observation_date"])
            fx_small = fx[["observation_date", "sell_rate"]].rename(
                columns={"observation_date": "date", "sell_rate": "ptax_sell"}
            )
            with warnings.catch_warnings():
                warnings.filterwarnings(
                    "ignore",
                    message="Dtype inference on a pandas object.*",
                    category=FutureWarning,
                )
                daily = (
                    pd.concat(
                        [daily.set_index("date"), fx_small.set_index("date")],
                        axis=1,
                        join="outer",
                    )
                    .sort_index()
                    .reset_index()
                )
        for column in ("icco_usd_tonne", "ptax_sell"):
            if column in daily:
                daily = daily.assign(
                    **{column: pd.to_numeric(daily[column], errors="coerce").ffill(limit=3)}
                )
        if {"icco_usd_tonne", "ptax_sell"}.issubset(daily.columns):
            daily = daily.assign(
                international_parity_brl_arroba=(
                    daily["icco_usd_tonne"] * daily["ptax_sell"] * 0.015
                )
            )
            daily = daily.assign(
                ilheus_basis_brl_arroba=(
                    pd.to_numeric(daily.get("ilheus_brl_arroba"), errors="coerce")
                    - daily["international_parity_brl_arroba"]
                )
            )
            daily = daily.assign(
                ilheus_basis_percent=(
                    daily["ilheus_basis_brl_arroba"]
                    / daily["international_parity_brl_arroba"]
                    * 100
                )
            )

    paths: dict[str, Path] = {}
    frames = {
        "analysis_daily": daily,
        "weather_daily": weather,
        "producer_prices_monthly": conab,
        "municipal_production_annual": production,
        "production_costs": costs,
    }
    for name, frame in frames.items():
        path = output / f"{name}.parquet"
        if frame.empty:
            pl.DataFrame({"empty": []}).write_parquet(path)
        else:
            normalized = {
                str(column): frame[column].where(frame[column].notna(), None).tolist()
                for column in frame.columns
            }
            pl.DataFrame(normalized, strict=False).write_parquet(path)
        paths[name] = path
    summary = {
        name: {"rows": len(frame), "columns": list(frame.columns)} for name, frame in frames.items()
    }
    summary_path = output / "dataset_summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    paths["summary"] = summary_path
    return paths
