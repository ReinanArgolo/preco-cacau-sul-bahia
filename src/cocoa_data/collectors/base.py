from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import Any

import httpx

from cocoa_data.models import CollectionBatch
from cocoa_data.settings import Settings


class CollectorError(RuntimeError):
    """Falha contextualizada de uma fonte externa."""


class BaseCollector(ABC):
    name: str

    def __init__(self, settings: Settings, client: httpx.Client | None = None) -> None:
        self.settings = settings
        self.config: dict[str, Any] = settings.sources[self.name]
        self.client = client or httpx.Client(
            timeout=settings.timeout,
            follow_redirects=True,
            headers={"User-Agent": "cocoa-data/0.1 (+pesquisa; Sul da Bahia)"},
        )

    @abstractmethod
    def collect(self, start: date, end: date) -> CollectionBatch:
        raise NotImplementedError

    def get(self, url: str, **kwargs: Any) -> httpx.Response:
        last_error: Exception | None = None
        for attempt in range(3):
            try:
                response = self.client.get(url, **kwargs)
                response.raise_for_status()
                return response
            except (httpx.HTTPError, httpx.TimeoutException) as exc:
                last_error = exc
                if attempt == 2:
                    break
        raise CollectorError(f"{self.name}: falha ao consultar {url}: {last_error}")
