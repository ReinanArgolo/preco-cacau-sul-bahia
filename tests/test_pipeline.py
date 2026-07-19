from contextlib import contextmanager
from datetime import date
from uuid import uuid4

import pytest

from cocoa_data.models import CollectionBatch
from cocoa_data.pipeline import COLLECTORS, Pipeline, sanitize_public_message


def test_public_source_message_removes_urls_and_secrets() -> None:
    message = "GET https://example.test/path?token=abc password=hunter2 falhou"
    cleaned = sanitize_public_message(message)
    assert "https://" not in cleaned
    assert "hunter2" not in cleaned


def test_missing_backfill_start_has_an_actionable_error() -> None:
    settings = type("Settings", (), {"sources": {"example": {"enabled": True}}})()
    pipeline = Pipeline(settings, repository=object())

    with pytest.raises(ValueError, match="example: backfill_start não configurado"):
        pipeline.resolve_period("example", "backfill", None, date(2026, 7, 19))


def test_source_configuration_failure_does_not_stop_following_sources(monkeypatch) -> None:
    class RepositoryStub:
        @contextmanager
        def pipeline_lock(self):
            yield True

        def latest_date(self, source):
            return None

        def start_run(self, source, start, end):
            return uuid4()

        def upsert_batch(self, batch):
            return 0

        def finish_run(self, run_id, status, batch=None, error=None):
            return None

        def update_source_status(self, **values):
            return None

    class CollectorStub:
        def __init__(self, settings):
            self.settings = settings

        def collect(self, start, end):
            return CollectionBatch(
                source="valid", requested_start=start, requested_end=end
            )

    settings = type(
        "Settings",
        (),
        {
            "sources": {
                "broken": {"enabled": True, "essential": False},
                "valid": {
                    "enabled": True,
                    "essential": False,
                    "backfill_start": "2026-01-01",
                },
            }
        },
    )()
    monkeypatch.setitem(COLLECTORS, "valid", CollectorStub)

    batches, failures = Pipeline(settings, RepositoryStub()).run(
        ["broken", "valid"], "backfill", end=date(2026, 7, 19)
    )

    assert [batch.source for batch in batches] == ["valid"]
    assert failures == [("broken", "broken: backfill_start não configurado")]
