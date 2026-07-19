from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from cocoa_data.collectors.base import BaseCollector
from cocoa_data.models import CollectionBatch, Observation


PTAX_TIMEZONE = ZoneInfo("America/Sao_Paulo")


def ptax_timestamp(value: str) -> datetime:
    """BCB publica dataHoraCotacao no horário oficial de Brasília, sem offset."""
    return datetime.fromisoformat(value).replace(tzinfo=PTAX_TIMEZONE)


class BCBCollector(BaseCollector):
    name = "bcb"

    def collect(self, start: date, end: date) -> CollectionBatch:
        endpoint = f"{self.config['url']}/CotacaoDolarPeriodo(dataInicial=@inicio,dataFinalCotacao=@fim)"
        payload = []
        cursor = start
        while cursor <= end:
            chunk_end = min(date(cursor.year, 12, 31), end)
            params = {
                "@inicio": f"'{cursor.strftime('%m-%d-%Y')}'",
                "@fim": f"'{chunk_end.strftime('%m-%d-%Y')}'",
                "$format": "json",
                "$select": "cotacaoCompra,cotacaoVenda,dataHoraCotacao",
            }
            payload.extend(self.get(endpoint, params=params).json().get("value", []))
            cursor = chunk_end + timedelta(days=1)
        closings: dict[date, dict] = {}
        for item in payload:
            timestamp = ptax_timestamp(item["dataHoraCotacao"])
            day = timestamp.date()
            current = closings.get(day)
            if current is None or timestamp >= ptax_timestamp(current["dataHoraCotacao"]):
                closings[day] = item
        if not closings:
            return CollectionBatch(
                source=self.name,
                requested_start=start,
                requested_end=end,
                warnings=["A API PTAX não retornou fechamento no período solicitado."],
            )
        records = [
            Observation(
                table="exchange_rates_daily",
                natural_key={"source": "bcb", "currency_pair": "USD_BRL", "observation_date": day},
                values={
                    "buy_rate": Decimal(str(item["cotacaoCompra"])),
                    "sell_rate": Decimal(str(item["cotacaoVenda"])),
                    "bulletin_type": item.get("tipoBoletim", "Fechamento"),
                    "quoted_at": ptax_timestamp(item["dataHoraCotacao"]).isoformat(),
                },
                source_url=endpoint,
                observed_at=day,
            )
            for day, item in sorted(closings.items())
        ]
        return CollectionBatch(source=self.name, requested_start=start, requested_end=end, records=records)
