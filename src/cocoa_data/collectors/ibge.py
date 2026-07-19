from __future__ import annotations

import re
from datetime import date
from decimal import Decimal, InvalidOperation

from cocoa_data.collectors.base import BaseCollector, CollectorError
from cocoa_data.models import CollectionBatch, Observation


VARIABLE_MAP = {
    "Área destinada à colheita": "planted_area_ha",
    "Área colhida": "harvested_area_ha",
    "Quantidade produzida": "production_tonne",
    "Rendimento médio": "yield_kg_ha",
    "Valor da produção": "production_value_thousand_brl",
}


def _decimal(value: str) -> Decimal | None:
    try:
        return Decimal(re.sub(r"[^0-9,.-]", "", value).replace(",", "."))
    except (InvalidOperation, ValueError):
        return None


class IBGECollector(BaseCollector):
    name = "ibge"

    def collect(self, start: date, end: date) -> CollectionBatch:
        locations = [item for item in self.settings.locations if item.get("ibge_code")]
        codes = ",".join(item["ibge_code"] for item in locations)
        periods = f"{start.year}-{end.year}"
        url = f"{self.config['url']}/n6/{codes}/v/all/p/{periods}/c82/2722"
        rows = self.get(url, params={"formato": "json"}).json()
        if not rows:
            raise CollectorError("ibge: SIDRA não retornou dados")
        headers = rows[0]
        grouped: dict[tuple[str, int], dict] = {}
        for raw in rows[1:]:
            row = {headers.get(key, key): value for key, value in raw.items()}
            text = " ".join(str(value) for value in row.values())
            if "cacau" not in text.lower():
                continue
            municipality = raw.get("D1C", "")
            year_text = raw.get("D3N")
            if not year_text:
                continue
            year = int(year_text)
            variable_name = raw.get("D2N", "")
            field = next((target for label, target in VARIABLE_MAP.items() if label in variable_name), None)
            if field is None:
                field = None
            if field is None:
                continue
            key = (municipality, year)
            grouped.setdefault(key, {})[field] = _decimal(raw.get("V", ""))
            grouped[key]["municipality_name"] = raw.get("D1N", municipality)
        records = []
        for (municipality, year), values in grouped.items():
            records.append(
                Observation(
                    table="municipal_production_annual",
                    natural_key={
                        "source": "ibge_sidra",
                        "municipality_code": municipality,
                        "year": year,
                        "product": "cacau_amendoa",
                    },
                    values=values,
                    source_url=url,
                    observed_at=date(year, 12, 31),
                )
            )
        if not records:
            raise CollectorError("ibge: não foi possível identificar cacau em amêndoa na resposta SIDRA")
        return CollectionBatch(source=self.name, requested_start=start, requested_end=end, records=records)
