from datetime import date
from decimal import Decimal

from cocoa_data.collectors.icco import parse_icco_html
from cocoa_data.collectors.bcb import ptax_timestamp
from cocoa_data.collectors.seagri import parse_brl, parse_seagri_html


def test_parse_brl() -> None:
    assert parse_brl("R$ 1.234,56") == Decimal("1234.56")


def test_ptax_timestamp_has_brasilia_offset() -> None:
    timestamp = ptax_timestamp("2026-07-17 13:10:18.709356")
    assert timestamp.isoformat() == "2026-07-17T13:10:18.709356-03:00"


def test_parse_seagri_filters_target() -> None:
    html = """
    <table><tbody>
      <tr><td>18/07/2026</td><td>Cacau (até 15:30h)</td><td>ILHEUS</td>
          <td>(comum)</td><td>arroba</td><td>330,00</td></tr>
      <tr><td>18/07/2026</td><td>Café</td><td>ILHEUS</td>
          <td>Duro</td><td>saca</td><td>2.000,00</td></tr>
    </tbody></table>
    """
    records = parse_seagri_html(html, "https://example.test")
    assert len(records) == 1
    assert records[0].natural_key["observation_date"] == date(2026, 7, 18)
    assert records[0].values["price"] == Decimal("330.00")
    assert records[0].values["unit"] == "arroba_15kg"


def test_parse_seagri_ignores_missing_quote() -> None:
    html = """
    <table><tbody>
      <tr><td>30/09/2025</td><td>Cacau (até 15:30h)</td><td>ILHEUS</td>
          <td>(comum)</td><td>arroba</td><td>Sem cotação</td></tr>
    </tbody></table>
    """
    assert parse_seagri_html(html, "https://example.test") == []


def test_parse_icco_table() -> None:
    html = """
    <table><tbody>
      <tr><td>1</td><td>17/07/2026</td><td>3,300.00</td><td>4,500.00</td>
          <td>4,420.50</td><td>3,820.25</td></tr>
    </tbody></table>
    """
    records = parse_icco_html(
        html, "https://example.test", date(2026, 7, 1), date(2026, 7, 31)
    )
    assert len(records) == 1
    assert records[0].values["price"] == Decimal("4420.50")
    assert records[0].values["new_york_futures_usd_tonne"] == Decimal("4500.00")
