from __future__ import annotations

from typing import Any

import httpx

from cocoa_data.database.repository import REQUIRED_TABLES


PUBLIC_ANALYTICAL_TABLES = REQUIRED_TABLES - {"ingestion_runs", "data_quality_events"}


class SupabaseRestRepository:
    """Leitura paginada da Data API, sem credencial privilegiada."""

    def __init__(self, url: str, publishable_key: str, timeout: float = 45) -> None:
        self.base_url = f"{url.rstrip('/')}/rest/v1"
        self.client = httpx.Client(
            headers={
                "apikey": publishable_key,
                "Authorization": f"Bearer {publishable_key}",
            },
            timeout=timeout,
        )

    def read_table(self, table_name: str) -> list[dict[str, Any]]:
        if table_name not in PUBLIC_ANALYTICAL_TABLES:
            raise ValueError(f"Tabela não permitida para leitura pública: {table_name}")
        rows: list[dict[str, Any]] = []
        page_size = 1_000
        while True:
            response = self.client.get(
                f"{self.base_url}/{table_name}",
                params={"select": "*", "offset": len(rows), "limit": page_size},
            )
            response.raise_for_status()
            page = response.json()
            rows.extend(page)
            if len(page) < page_size:
                return rows
