from __future__ import annotations

import re
from datetime import date, datetime
from decimal import Decimal

import html as html_module
import json

from bs4 import BeautifulSoup

from cocoa_data.collectors.base import BaseCollector
from cocoa_data.models import CollectionBatch, Observation


def _number(value: str) -> Decimal:
    return Decimal(re.sub(r"[^0-9.-]", "", value.replace(",", "")))


def parse_icco_html(html: str, source_url: str, start: date, end: date) -> list[Observation]:
    soup = BeautifulSoup(html, "lxml")
    records: list[Observation] = []
    for row in soup.select("table tr"):
        cells = [cell.get_text(" ", strip=True) for cell in row.select("td")]
        if len(cells) < 5:
            continue
        offset = 1 if cells[0].isdigit() else 0
        try:
            observed = datetime.strptime(cells[offset], "%d/%m/%Y").date()
            london, new_york, icco_usd, icco_eur = map(_number, cells[offset + 1 : offset + 5])
        except (ValueError, IndexError):
            continue
        if not start <= observed <= end:
            continue
        records.append(
            Observation(
                table="market_prices_daily",
                natural_key={
                    "source": "icco",
                    "series": "icco_daily",
                    "market": "GLOBAL",
                    "observation_date": observed,
                },
                values={
                    "price": icco_usd,
                    "currency": "USD",
                    "unit": "metric_tonne",
                    "london_futures_gbp_tonne": london,
                    "new_york_futures_usd_tonne": new_york,
                    "icco_eur_tonne": icco_eur,
                },
                source_url=source_url,
                observed_at=observed,
            )
        )
    return records


class ICCOCollector(BaseCollector):
    name = "icco"

    def collect(self, start: date, end: date) -> CollectionBatch:
        response = self.get(self.config["url"])
        soup = BeautifulSoup(response.text, "lxml")
        table = soup.select_one("table[data-wpdatatable_id]")
        descriptor = soup.select_one(f"#{table.get('data-described-by')}") if table else None
        nonce = soup.select_one("input[id^='wdtNonceFrontendServerSide_']")
        records: list[Observation] = []
        if table and descriptor and nonce:
            description = json.loads(html_module.unescape(descriptor["value"]))
            table_id = description["tableWpId"]
            ajax_url = f"https://www.icco.org/wp-admin/admin-ajax.php?action=get_wdtable&table_id={table_id}"
            columns = [item["name"] for item in description["dataTableParams"]["columnDefs"]]
            offset = 0
            while offset < 20_000:
                form = {
                    "draw": "1",
                    "start": str(offset),
                    "length": "500",
                    "search[value]": "",
                    "search[regex]": "false",
                    "order[0][column]": "1",
                    "order[0][dir]": "desc",
                    "wdtNonce": nonce["value"],
                }
                for index, name in enumerate(columns):
                    form.update(
                        {
                            f"columns[{index}][data]": str(index),
                            f"columns[{index}][name]": name,
                            f"columns[{index}][searchable]": "true",
                            f"columns[{index}][orderable]": "true",
                            f"columns[{index}][search][value]": "",
                            f"columns[{index}][search][regex]": "false",
                        }
                    )
                page = self.client.post(
                    ajax_url,
                    data=form,
                    headers={"Referer": str(response.url), "X-Requested-With": "XMLHttpRequest"},
                    timeout=max(self.settings.timeout, 120),
                )
                page.raise_for_status()
                rows = page.json().get("data", [])
                if not rows:
                    break
                page_html = "<table>" + "".join(
                    "<tr>" + "".join(f"<td>{value}</td>" for value in row) + "</tr>" for row in rows
                ) + "</table>"
                records.extend(parse_icco_html(page_html, ajax_url, start, end))
                page_dates = []
                for row in rows:
                    try:
                        page_dates.append(datetime.strptime(row[1], "%d/%m/%Y").date())
                    except (ValueError, IndexError):
                        pass
                if len(rows) < 500 or (page_dates and min(page_dates) < start):
                    break
                offset += len(rows)
        else:
            records = parse_icco_html(response.text, str(response.url), start, end)
        warnings = ["O histórico ICCO anterior à cobertura pública atual não é contornado."]
        if not records:
            warnings.append("A ICCO não retornou observações dentro do período solicitado.")
        return CollectionBatch(
            source=self.name,
            requested_start=start,
            requested_end=end,
            records=records,
            warnings=warnings,
        )
