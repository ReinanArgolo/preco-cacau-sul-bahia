from __future__ import annotations

import hashlib
import json
from datetime import date, datetime, time, timedelta, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field, computed_field


class Observation(BaseModel):
    table: Literal[
        "market_prices_daily",
        "exchange_rates_daily",
        "weather_daily",
        "producer_prices_monthly",
        "production_costs",
        "municipal_production_annual",
    ]
    natural_key: dict[str, Any]
    values: dict[str, Any]
    source_url: str
    observed_at: date
    published_at: datetime | None = None
    available_at: datetime | None = None
    revision: int = Field(default=1, ge=1)
    information_set: Literal[
        "historical_observation",
        "reanalysis",
        "publication_date_unknown",
    ] = "historical_observation"
    metadata: dict[str, Any] = Field(default_factory=dict)

    def temporal_values(self, collected_at: datetime) -> dict[str, Any]:
        """Return conservative point-in-time metadata for persistence."""
        published_at = self.published_at
        available_at = self.available_at
        information_set = self.information_set
        if self.table == "exchange_rates_daily" and self.values.get("quoted_at"):
            published_at = published_at or datetime.fromisoformat(str(self.values["quoted_at"]))
            available_at = available_at or published_at
        elif self.table == "weather_daily":
            information_set = "reanalysis"
            available_at = available_at or collected_at
        elif self.table in {
            "producer_prices_monthly",
            "production_costs",
            "municipal_production_annual",
        }:
            information_set = "publication_date_unknown"
            available_at = available_at or collected_at
        else:
            # When the source does not publish a reliable time, treat the value
            # as known only at midnight in Bahia on the following day (UTC-03).
            bahia_midnight_utc = datetime.combine(
                self.observed_at + timedelta(days=1), time(hour=3), tzinfo=timezone.utc
            )
            available_at = available_at or bahia_midnight_utc
        return {
            "published_at": published_at,
            "available_at": available_at,
            "revision": self.revision,
            "information_set": information_set,
        }


class CollectionBatch(BaseModel):
    source: str
    requested_start: date
    requested_end: date
    records: list[Observation] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    collected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @computed_field
    @property
    def checksum(self) -> str:
        payload = [record.model_dump(mode="json") for record in self.records]
        return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()

    @computed_field
    @property
    def coverage(self) -> dict[str, str | int | None]:
        dates = sorted(record.observed_at for record in self.records)
        return {
            "rows": len(self.records),
            "minimum": dates[0].isoformat() if dates else None,
            "maximum": dates[-1].isoformat() if dates else None,
        }
