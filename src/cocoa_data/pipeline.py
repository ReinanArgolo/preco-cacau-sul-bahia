from __future__ import annotations

import logging
import re
import uuid
from datetime import date, timedelta
from typing import Iterable

from cocoa_data.collectors import (
    BCBCollector,
    ConabCollector,
    IBGECollector,
    ICCOCollector,
    ICECollector,
    SeagriCollector,
    WeatherCollector,
)
from cocoa_data.collectors.base import BaseCollector
from cocoa_data.database import Repository
from cocoa_data.models import CollectionBatch
from cocoa_data.settings import Settings


LOGGER = logging.getLogger(__name__)


class EssentialSourceError(RuntimeError):
    def __init__(self, batches: list[CollectionBatch], failures: list[tuple[str, str]]) -> None:
        self.batches = batches
        self.failures = failures
        detail = "; ".join(f"{name}: {error}" for name, error in failures)
        super().__init__(f"Fontes essenciais falharam: {detail}")


def sanitize_public_message(message: str) -> str:
    """Remove URLs and credential-like query values before public persistence."""
    cleaned = re.sub(r"https?://\S+", "[endereço omitido]", message)
    cleaned = re.sub(
        r"(?i)(token|key|password|secret|authorization)\s*[=:]\s*[^\s;]+",
        r"\1=[omitido]",
        cleaned,
    )
    return cleaned[:500]

COLLECTORS: dict[str, type[BaseCollector]] = {
    "seagri": SeagriCollector,
    "bcb": BCBCollector,
    "icco": ICCOCollector,
    "ice": ICECollector,
    "conab": ConabCollector,
    "weather": WeatherCollector,
    "ibge": IBGECollector,
}


def enabled_sources(settings: Settings) -> list[str]:
    return [name for name, config in settings.sources.items() if config.get("enabled", False)]


class Pipeline:
    def __init__(self, settings: Settings, repository: Repository) -> None:
        self.settings = settings
        self.repository = repository

    def resolve_period(
        self,
        source: str,
        mode: str,
        start: date | None,
        end: date | None,
    ) -> tuple[date, date]:
        final = end or date.today()
        if start:
            return start, final
        configured_start = self.settings.sources.get(source, {}).get("backfill_start")
        if not configured_start:
            raise ValueError(f"{source}: backfill_start não configurado")
        initial = date.fromisoformat(configured_start)
        if mode == "backfill":
            return initial, final
        latest = self.repository.latest_date(source)
        if latest:
            return latest - timedelta(days=7), final
        return max(final - timedelta(days=30), initial), final

    def run(
        self,
        sources: Iterable[str],
        mode: str,
        start: date | None = None,
        end: date | None = None,
    ) -> tuple[list[CollectionBatch], list[tuple[str, str]]]:
        batches: list[CollectionBatch] = []
        failures: list[tuple[str, str]] = []
        with self.repository.pipeline_lock() as acquired:
            if not acquired:
                raise RuntimeError("Já existe uma coleta em execução")
            for source in sources:
                run_id: uuid.UUID | None = None
                try:
                    period_start, period_end = self.resolve_period(source, mode, start, end)
                    run_id = self.repository.start_run(source, period_start, period_end)
                    collector = COLLECTORS[source](self.settings)
                    batch = collector.collect(period_start, period_end)
                    self.repository.upsert_batch(batch)
                    status = "degraded" if batch.warnings else "success"
                    self.repository.finish_run(run_id, status, batch=batch)
                    latest = max((item.observed_at for item in batch.records), default=None)
                    self.repository.update_source_status(
                        source=source,
                        display_name=self.settings.sources[source].get("name", source.upper()),
                        status="degraded" if batch.warnings else "healthy",
                        essential=bool(self.settings.sources[source].get("essential", False)),
                        latest_observation_date=latest,
                        row_count=len(batch.records),
                        message=sanitize_public_message("; ".join(batch.warnings)) or None,
                    )
                    batches.append(batch)
                    LOGGER.info("%s: %s registros (%s)", source, len(batch.records), status)
                except Exception as exc:
                    message = str(exc)
                    failures.append((source, message))
                    config = self.settings.sources.get(source, {})
                    if run_id is not None:
                        try:
                            self.repository.finish_run(run_id, "failed", error=message)
                        except Exception:
                            LOGGER.exception("Falha ao finalizar execução de %s", source)
                    latest = None
                    try:
                        latest = self.repository.latest_date(source)
                    except Exception:
                        LOGGER.exception("Falha ao consultar cobertura de %s", source)
                    try:
                        self.repository.update_source_status(
                            source=source,
                            display_name=config.get("name", source.upper()),
                            status="failed",
                            essential=bool(config.get("essential", False)),
                            latest_observation_date=latest,
                            row_count=0,
                            message=sanitize_public_message(message),
                        )
                    except Exception:
                        LOGGER.exception("Falha ao persistir diagnóstico de %s", source)
                    LOGGER.exception("Falha em %s", source)
        essential_failures = [
            item
            for item in failures
            if self.settings.sources.get(item[0], {}).get("essential", False)
        ]
        if essential_failures:
            raise EssentialSourceError(batches, essential_failures)
        return batches, failures
