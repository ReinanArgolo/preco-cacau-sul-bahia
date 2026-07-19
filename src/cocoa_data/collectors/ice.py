from datetime import date

from cocoa_data.collectors.base import BaseCollector, CollectorError
from cocoa_data.models import CollectionBatch


class ICECollector(BaseCollector):
    name = "ice"

    def collect(self, start: date, end: date) -> CollectionBatch:
        raise CollectorError(
            "ice: coletor desabilitado; configure uma licença de dados ICE antes de ativá-lo"
        )
