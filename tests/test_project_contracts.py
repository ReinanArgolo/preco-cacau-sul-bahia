import json
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def test_notebook_is_valid_json() -> None:
    notebook = json.loads(
        (ROOT / "notebooks" / "01_analise_integrada_cacau.ipynb").read_text(encoding="utf-8")
    )
    assert notebook["nbformat"] == 4
    headings = "\n".join(
        "".join(cell.get("source", [])) for cell in notebook["cells"] if cell["cell_type"] == "markdown"
    )
    assert "paridade" in headings.lower()
    assert "clima" in headings.lower()
    assert "produção municipal" in headings.lower()


def test_all_enabled_sources_have_collectors() -> None:
    from cocoa_data.pipeline import COLLECTORS

    config = yaml.safe_load((ROOT / "configs" / "sources.yaml").read_text(encoding="utf-8"))
    enabled = {name for name, item in config["sources"].items() if item.get("enabled")}
    assert enabled <= set(COLLECTORS)


def test_all_enabled_sources_have_a_reproducible_backfill_start() -> None:
    config = yaml.safe_load((ROOT / "configs" / "sources.yaml").read_text(encoding="utf-8"))
    enabled = [item for item in config["sources"].values() if item.get("enabled")]
    assert all(item.get("backfill_start") for item in enabled)


def test_supabase_schema_protects_every_public_table_with_rls() -> None:
    migration = (ROOT / "migrations" / "001_initial.sql").read_text(encoding="utf-8")
    tables = {
        "ingestion_runs",
        "market_prices_daily",
        "exchange_rates_daily",
        "weather_daily",
        "producer_prices_monthly",
        "production_costs",
        "municipal_production_annual",
        "data_quality_events",
    }
    for table in tables:
        assert f"alter table {table} enable row level security" in migration


def test_temporal_migration_exposes_only_sanitized_source_status() -> None:
    migration = (ROOT / "migrations" / "003_temporality_and_source_status.sql").read_text(
        encoding="utf-8"
    )
    for field in ("published_at", "available_at", "revision", "information_set"):
        assert field in migration
    assert "alter table source_status enable row level security" in migration
    assert "grant select on source_status to anon, authenticated" in migration
    assert "revoke insert, update, delete" in migration


def test_frontend_never_declares_a_private_supabase_key() -> None:
    files = [
        *list((ROOT / "web" / "app").rglob("*.ts")),
        *list((ROOT / "web" / "app").rglob("*.tsx")),
        *list((ROOT / "web" / "lib").rglob("*.ts")),
        ROOT / "web" / "proxy.ts",
        ROOT / "web" / ".env.example",
    ]
    content = "\n".join(path.read_text(encoding="utf-8") for path in files)
    assert "SUPABASE_SERVICE_ROLE_KEY" not in content
    assert "SUPABASE_SECRET_KEY" not in content


def test_data_api_is_explicitly_read_only() -> None:
    hardening = (ROOT / "migrations" / "002_harden_data_api.sql").read_text(
        encoding="utf-8"
    )
    assert "revoke insert, update, delete" in hardening
    assert "alter default privileges" in hardening
    assert "from anon, authenticated" in hardening
