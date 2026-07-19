from __future__ import annotations

import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from bs4 import BeautifulSoup

from cocoa_data.collectors.base import BaseCollector
from cocoa_data.models import CollectionBatch, Observation


def parse_brl(value: str) -> Decimal:
    cleaned = re.sub(r"[^0-9,.-]", "", value).replace(".", "").replace(",", ".")
    return Decimal(cleaned)


def parse_seagri_html(html: str, source_url: str) -> list[Observation]:
    soup = BeautifulSoup(html, "lxml")
    records: list[Observation] = []
    for row in soup.select("table tbody tr"):
        cells = [cell.get_text(" ", strip=True) for cell in row.select("td")]
        if len(cells) < 6:
            continue
        day, product, market, kind, unit, price = cells[:6]
        normalized = " ".join(cells).upper()
        if "CACAU" not in normalized or "ILHEUS" not in normalized or "ARROBA" not in normalized:
            continue
        observed = datetime.strptime(day, "%d/%m/%Y").date()
        try:
            value = parse_brl(price)
        except InvalidOperation:
            # A fonte publica linhas com "Sem cotação"; ausência não é preço zero.
            continue
        records.append(
            Observation(
                table="market_prices_daily",
                natural_key={
                    "source": "seagri",
                    "series": "cacau_comum",
                    "market": "ILHEUS",
                    "observation_date": observed,
                },
                values={
                    "price": value,
                    "currency": "BRL",
                    "unit": "arroba_15kg",
                    "quality_type": kind.strip("() ") or "comum",
                },
                source_url=source_url,
                observed_at=observed,
                metadata={"product_label": product},
            )
        )
    return records


class SeagriCollector(BaseCollector):
    name = "seagri"

    def collect(self, start: date, end: date) -> CollectionBatch:
        url = self.config["url"]
        records: list[Observation] = []
        warnings: list[str] = []
        page = 0
        seen: set[tuple[str, str]] = set()
        while page < 500:
            params = {
                "data[min][date]": start.isoformat(),
                "data[max][date]": end.isoformat(),
                "produto": "37",
                "praca": "229",
                "tipo": "All",
                "page": page,
            }
            response = self.get(url, params=params)
            page_records = parse_seagri_html(response.text, str(response.url))
            unique = []
            for record in page_records:
                key = (str(record.natural_key), str(record.values))
                if key not in seen:
                    seen.add(key)
                    unique.append(record)
            records.extend(unique)
            soup = BeautifulSoup(response.text, "lxml")
            next_link = soup.select_one('a[rel="next"], .pager__item--next a')
            if not next_link:
                break
            page += 1
        if not records:
            warnings.append("A Seagri não publicou cotação de cacau em Ilhéus no período solicitado.")
        return CollectionBatch(
            source=self.name,
            requested_start=start,
            requested_end=end,
            records=records,
            warnings=warnings,
        )
