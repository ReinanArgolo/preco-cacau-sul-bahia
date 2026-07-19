from datetime import date, datetime, timezone

from cocoa_data.models import CollectionBatch, Observation


def observation(price: int) -> Observation:
    return Observation(
        table="market_prices_daily",
        natural_key={
            "source": "test",
            "series": "cocoa",
            "market": "X",
            "observation_date": date(2026, 7, 18),
        },
        values={"price": price},
        source_url="https://example.test",
        observed_at=date(2026, 7, 18),
    )


def test_batch_coverage_and_checksum_are_deterministic() -> None:
    first = CollectionBatch(
        source="test",
        requested_start=date(2026, 7, 1),
        requested_end=date(2026, 7, 31),
        records=[observation(100)],
    )
    second = CollectionBatch(
        source="test",
        requested_start=date(2026, 7, 1),
        requested_end=date(2026, 7, 31),
        records=[observation(100)],
    )
    assert first.coverage == {"rows": 1, "minimum": "2026-07-18", "maximum": "2026-07-18"}
    assert first.checksum == second.checksum


def test_daily_value_without_publication_time_is_available_next_day() -> None:
    values = observation(100).temporal_values(datetime(2026, 7, 18, 20, tzinfo=timezone.utc))
    assert values["available_at"] == datetime(2026, 7, 19, 3, tzinfo=timezone.utc)
    assert values["information_set"] == "historical_observation"


def test_reanalysis_is_never_backdated() -> None:
    record = Observation(
        table="weather_daily",
        natural_key={"source": "open_meteo", "location_id": "gandu", "observation_date": date(2020, 1, 1)},
        values={}, source_url="https://example.test", observed_at=date(2020, 1, 1),
    )
    collected = datetime(2026, 7, 19, tzinfo=timezone.utc)
    values = record.temporal_values(collected)
    assert values["available_at"] == collected
    assert values["information_set"] == "reanalysis"
