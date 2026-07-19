from datetime import date
from decimal import Decimal

import polars as pl

from cocoa_data.analysis.dataset import build_analysis_dataset
from cocoa_data.settings import Settings


class FakeRepository:
    def read_table(self, name: str):
        rows = {
            "market_prices_daily": [
                {"source": "seagri", "observation_date": date(2026, 7, 17), "price": Decimal("330")},
                {"source": "icco", "observation_date": date(2026, 7, 17), "price": Decimal("4500")},
            ],
            "exchange_rates_daily": [
                {"source": "bcb", "observation_date": date(2026, 7, 17), "sell_rate": Decimal("5.20")}
            ],
            "weather_daily": [],
            "producer_prices_monthly": [],
            "municipal_production_annual": [],
            "production_costs": [],
        }
        return rows[name]


def test_build_analysis_dataset_calculates_parity(tmp_path) -> None:
    settings = Settings.load()
    settings = type(settings)(
        root=tmp_path,
        database_url=None,
        supabase_url=None,
        supabase_publishable_key=None,
        timeout=settings.timeout,
        log_level=settings.log_level,
        sources=settings.sources,
        locations=settings.locations,
        quality=settings.quality,
    )
    paths = build_analysis_dataset(FakeRepository(), settings)  # type: ignore[arg-type]
    frame = pl.read_parquet(paths["analysis_daily"])
    assert frame["international_parity_brl_arroba"][0] == 351.0
    assert frame["ilheus_basis_brl_arroba"][0] == -21.0
