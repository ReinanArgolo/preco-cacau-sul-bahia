import httpx
import pytest
import respx

from cocoa_data.database import SupabaseRestRepository


@respx.mock
def test_rest_repository_reads_public_table_with_publishable_key() -> None:
    route = respx.get("https://project.supabase.co/rest/v1/market_prices_daily").mock(
        return_value=httpx.Response(200, json=[{"source": "seagri", "price": 410}])
    )
    repository = SupabaseRestRepository("https://project.supabase.co", "sb_publishable_test")

    assert repository.read_table("market_prices_daily") == [
        {"source": "seagri", "price": 410}
    ]
    assert route.calls[0].request.headers["apikey"] == "sb_publishable_test"


def test_rest_repository_rejects_internal_table() -> None:
    repository = SupabaseRestRepository("https://project.supabase.co", "sb_publishable_test")
    with pytest.raises(ValueError, match="não permitida"):
        repository.read_table("ingestion_runs")
