from __future__ import annotations

from datetime import date
from decimal import Decimal

from cocoa_data.collectors.base import BaseCollector, CollectorError
from cocoa_data.models import CollectionBatch, Observation


DAILY_VARIABLES = [
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_sum",
    "et0_fao_evapotranspiration",
]


class WeatherCollector(BaseCollector):
    name = "weather"

    def collect(self, start: date, end: date) -> CollectionBatch:
        records: list[Observation] = []
        warnings: list[str] = []
        for location in self.settings.locations:
            params = {
                "latitude": location["latitude"],
                "longitude": location["longitude"],
                "start_date": start.isoformat(),
                "end_date": end.isoformat(),
                "daily": ",".join(DAILY_VARIABLES),
                "timezone": location["timezone"],
                "models": "era5_land",
            }
            payload = self.get(self.config["url"], params=params).json()
            daily = payload.get("daily", {})
            times = daily.get("time", [])
            if not times:
                warnings.append(f"Sem clima para {location['id']}")
                continue
            for index, stamp in enumerate(times):
                observed = date.fromisoformat(stamp)
                values = {
                    variable: (
                        Decimal(str(daily[variable][index]))
                        if daily.get(variable, [None] * len(times))[index] is not None
                        else None
                    )
                    for variable in DAILY_VARIABLES
                }
                records.append(
                    Observation(
                        table="weather_daily",
                        natural_key={
                            "source": "open_meteo",
                            "location_id": location["id"],
                            "observation_date": observed,
                        },
                        values={
                            **values,
                            "latitude": Decimal(str(location["latitude"])),
                            "longitude": Decimal(str(location["longitude"])),
                            "timezone": location["timezone"],
                            "model": "era5_land",
                        },
                        source_url=self.config["url"],
                        observed_at=observed,
                        metadata={"location_name": location["name"], "country": location["country"]},
                    )
                )
        if not records:
            raise CollectorError("weather: Open-Meteo não retornou observações")
        return CollectionBatch(
            source=self.name,
            requested_start=start,
            requested_end=end,
            records=records,
            warnings=warnings,
        )
