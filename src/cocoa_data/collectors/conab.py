from __future__ import annotations

import io
import re
from datetime import date
from decimal import Decimal

import pandas as pd

from cocoa_data.collectors.base import BaseCollector, CollectorError
from cocoa_data.models import CollectionBatch, Observation


def parse_conab_prices_html(html: str, source_url: str, start: date, end: date) -> list[Observation]:
    records: list[Observation] = []
    try:
        tables = pd.read_html(io.StringIO(html), decimal=",", thousands=".")
    except ValueError:
        return records
    for table in tables:
        for _, row in table.iterrows():
            text = " ".join(str(value) for value in row.values)
            if "cacau" not in text.lower() or "bahia" not in text.lower():
                continue
            month_match = re.search(r"(0?[1-9]|1[0-2])[/\-](20\d{2})", text)
            numbers = [value for value in row.values if isinstance(value, (int, float)) and pd.notna(value)]
            if not month_match or not numbers:
                continue
            observed = date(int(month_match.group(2)), int(month_match.group(1)), 1)
            if start <= observed <= end:
                records.append(
                    Observation(
                        table="producer_prices_monthly",
                        natural_key={
                            "source": "conab",
                            "state": "BA",
                            "product": "cacau_cultivado",
                            "reference_month": observed,
                        },
                        values={"price_brl_kg": Decimal(str(numbers[-1])), "commercial_level": "produtor"},
                        source_url=source_url,
                        observed_at=observed,
                    )
                )
    return records


def parse_conab_costs_xlsx(content: bytes, source_url: str) -> list[Observation]:
    records: list[Observation] = []
    workbook = pd.ExcelFile(io.BytesIO(content))
    for sheet in workbook.sheet_names:
        frame = pd.read_excel(workbook, sheet_name=sheet, header=None)
        for row_index, row in frame.iterrows():
            year_values = [int(v) for v in row.values if isinstance(v, (int, float)) and 2000 <= v <= 2100]
            if not year_values:
                continue
            year = year_values[0]
            for column_index, value in enumerate(row.values):
                if not isinstance(value, (int, float)) or pd.isna(value) or value == year:
                    continue
                label = str(frame.iloc[row_index, max(0, column_index - 1)])
                records.append(
                    Observation(
                        table="production_costs",
                        natural_key={
                            "source": "conab",
                            "location": sheet[:80],
                            "reference_year": year,
                            "cost_item": label[:160],
                        },
                        values={"value_brl": Decimal(str(value)), "unit": "as_published"},
                        source_url=source_url,
                        observed_at=date(year, 12, 31),
                        metadata={"sheet": sheet, "row": int(row_index), "column": int(column_index)},
                    )
                )
    return records


class ConabCollector(BaseCollector):
    name = "conab"

    def collect(self, start: date, end: date) -> CollectionBatch:
        warnings: list[str] = []
        price_response = self.get(self.config["prices_url"])
        records = parse_conab_prices_html(price_response.text, str(price_response.url), start, end)
        if not records:
            warnings.append(
                "A consulta mensal da Conab exige parâmetros de sessão/exportação e não apresentou "
                "linhas de cacau na página inicial."
            )
        cost_response = self.get(self.config["costs_url"])
        try:
            costs = parse_conab_costs_xlsx(cost_response.content, str(cost_response.url))
            records.extend([item for item in costs if start.year <= item.observed_at.year <= end.year])
        except Exception as exc:
            warnings.append(f"Não foi possível interpretar a planilha de custos da Conab: {exc}")
        if not records:
            raise CollectorError("conab: nenhuma observação utilizável foi extraída")
        return CollectionBatch(
            source=self.name,
            requested_start=start,
            requested_end=end,
            records=records,
            warnings=warnings,
        )
