from __future__ import annotations

import hashlib
import json
import uuid
from contextlib import contextmanager
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from sqlalchemy import MetaData, Table, create_engine, func, inspect, select, text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Engine

from cocoa_data.models import CollectionBatch, Observation


REQUIRED_TABLES = {
    "ingestion_runs",
    "market_prices_daily",
    "exchange_rates_daily",
    "weather_daily",
    "producer_prices_monthly",
    "production_costs",
    "municipal_production_annual",
    "data_quality_events",
    "source_status",
}


def _json_default(value: Any) -> str:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return str(value)


def observation_checksum(record: Observation) -> str:
    payload = {"values": record.values, "metadata": record.metadata, "source_url": record.source_url}
    return hashlib.sha256(
        json.dumps(payload, default=_json_default, sort_keys=True).encode()
    ).hexdigest()


class Repository:
    def __init__(self, database_url: str) -> None:
        self.engine: Engine = create_engine(database_url, pool_pre_ping=True)
        self.metadata = MetaData()

    def migrate(self, migration_dir: Path) -> None:
        scripts = sorted(migration_dir.glob("*.sql"))
        with self.engine.begin() as connection:
            for script in scripts:
                statements = script.read_text(encoding="utf-8").split(";")
                for statement in statements:
                    if statement.strip():
                        connection.exec_driver_sql(statement)
        self.metadata.reflect(bind=self.engine)

    def reflect(self) -> None:
        if not self.metadata.tables:
            self.metadata.reflect(bind=self.engine)

    def check_connection(self) -> dict[str, Any]:
        with self.engine.connect() as connection:
            connection.execute(text("select 1"))
        available = set(inspect(self.engine).get_table_names(schema="public"))
        missing = sorted(REQUIRED_TABLES - available)
        return {
            "connected": True,
            "schema_ready": not missing,
            "required_tables": len(REQUIRED_TABLES),
            "missing_tables": missing,
        }

    @contextmanager
    def pipeline_lock(self):
        """Manté lock e unlock na mesma sessão PostgreSQL do pool."""
        with self.engine.connect() as connection:
            acquired = bool(connection.scalar(text("select pg_try_advisory_lock(20260718)")))
            try:
                yield acquired
            finally:
                if acquired:
                    connection.execute(text("select pg_advisory_unlock(20260718)"))

    def start_run(self, source: str, start: date, end: date) -> uuid.UUID:
        self.reflect()
        run_id = uuid.uuid4()
        table = self.metadata.tables["ingestion_runs"]
        with self.engine.begin() as connection:
            connection.execute(
                table.insert().values(
                    id=run_id,
                    source=source,
                    requested_start=start,
                    requested_end=end,
                    status="running",
                )
            )
        return run_id

    def finish_run(
        self,
        run_id: uuid.UUID,
        status: str,
        batch: CollectionBatch | None = None,
        error: str | None = None,
    ) -> None:
        self.reflect()
        values: dict[str, Any] = {
            "status": status,
            "error": error,
            "finished_at": datetime.now(timezone.utc),
        }
        if batch:
            values.update(
                row_count=len(batch.records),
                coverage_start=batch.coverage["minimum"],
                coverage_end=batch.coverage["maximum"],
                checksum=batch.checksum,
                warnings=batch.warnings,
            )
        table = self.metadata.tables["ingestion_runs"]
        with self.engine.begin() as connection:
            connection.execute(table.update().where(table.c.id == run_id).values(**values))

    def upsert_batch(self, batch: CollectionBatch) -> int:
        self.reflect()
        grouped: dict[str, list[Observation]] = {}
        for record in batch.records:
            grouped.setdefault(record.table, []).append(record)
        total = 0
        with self.engine.begin() as connection:
            for table_name, records in grouped.items():
                table = self.metadata.tables[table_name]
                primary_keys = [column.name for column in table.primary_key.columns]
                for record in records:
                    checksum = observation_checksum(record)
                    row = {
                        **record.natural_key,
                        **record.values,
                        "source_url": record.source_url,
                        "metadata": record.metadata,
                        "content_checksum": checksum,
                        **record.temporal_values(batch.collected_at),
                        "last_collected_at": datetime.now(timezone.utc),
                    }
                    row = {key: value for key, value in row.items() if key in table.c}
                    statement = insert(table).values(**row)
                    excluded = statement.excluded
                    updates = {
                        key: getattr(excluded, key)
                        for key in row
                        if key not in primary_keys and key not in {"first_collected_at"}
                    }
                    updates["previous_checksum"] = table.c.content_checksum
                    statement = statement.on_conflict_do_update(
                        index_elements=primary_keys,
                        set_=updates,
                        where=table.c.content_checksum != excluded.content_checksum,
                    )
                    connection.execute(statement)
                    total += 1
        return total

    def latest_date(self, source: str) -> date | None:
        self.reflect()
        candidates = []
        source_map = {
            "seagri": [("market_prices_daily", "seagri", "observation_date")],
            "icco": [("market_prices_daily", "icco", "observation_date")],
            "bcb": [("exchange_rates_daily", "bcb", "observation_date")],
            "weather": [("weather_daily", "open_meteo", "observation_date")],
            "conab": [
                ("producer_prices_monthly", "conab", "reference_month"),
                ("production_costs", "conab", "reference_year"),
            ],
            "ibge": [("municipal_production_annual", "ibge_sidra", "year")],
        }
        for table_name, stored_source, date_column in source_map.get(source, []):
            table = self.metadata.tables[table_name]
            with self.engine.connect() as connection:
                value = connection.scalar(
                    select(func.max(getattr(table.c, date_column))).where(table.c.source == stored_source)
                )
                if value:
                    if isinstance(value, int):
                        value = date(value, 12, 31)
                    candidates.append(value)
        return max(candidates) if candidates else None

    def update_source_status(
        self,
        source: str,
        display_name: str,
        status: str,
        essential: bool,
        latest_observation_date: date | None,
        row_count: int,
        message: str | None = None,
    ) -> None:
        self.reflect()
        table = self.metadata.tables["source_status"]
        now = datetime.now(timezone.utc)
        values = {
            "source": source,
            "display_name": display_name,
            "status": status,
            "essential": essential,
            "last_run_at": now,
            "latest_observation_date": latest_observation_date,
            "row_count": row_count,
            "message": message,
            "updated_at": now,
        }
        if status in {"healthy", "degraded"}:
            values["last_success_at"] = now
        statement = insert(table).values(**values)
        excluded = statement.excluded
        updates = {key: getattr(excluded, key) for key in values if key != "source"}
        if status not in {"healthy", "degraded"}:
            updates.pop("last_success_at", None)
        with self.engine.begin() as connection:
            connection.execute(
                statement.on_conflict_do_update(index_elements=["source"], set_=updates)
            )

    def read_table(self, table_name: str) -> list[dict[str, Any]]:
        self.reflect()
        table: Table = self.metadata.tables[table_name]
        with self.engine.connect() as connection:
            return [dict(row._mapping) for row in connection.execute(select(table))]

    def add_quality_events(self, events: Iterable[dict[str, Any]]) -> None:
        self.reflect()
        rows = list(events)
        if not rows:
            return
        with self.engine.begin() as connection:
            connection.execute(self.metadata.tables["data_quality_events"].insert(), rows)
