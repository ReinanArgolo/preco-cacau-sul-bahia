from __future__ import annotations

import argparse
import json
import logging
from datetime import date
from pathlib import Path

from cocoa_data.analysis import build_analysis_dataset, render_notebook
from cocoa_data.database import Repository, SupabaseRestRepository
from cocoa_data.modeling.readiness import evaluate_model_readiness
from cocoa_data.pipeline import (
    EssentialSourceError,
    Pipeline,
    enabled_sources,
    sanitize_public_message,
)
from cocoa_data.quality import run_quality_checks
from cocoa_data.settings import Settings


def _date(value: str | None) -> date | None:
    return date.fromisoformat(value) if value else None


def _write_status(path: str | None, payload: dict | list) -> str:
    serialized = json.dumps(payload, default=str, ensure_ascii=False, indent=2)
    if path:
        status_path = Path(path)
        status_path.parent.mkdir(parents=True, exist_ok=True)
        status_path.write_text(serialized, encoding="utf-8")
    return serialized


def _repository(settings: Settings) -> Repository:
    if not settings.database_url:
        raise SystemExit("SUPABASE_DB_URL não está configurada. Consulte .env.example.")
    repository = Repository(settings.database_url)
    repository.migrate(settings.root / "migrations")
    return repository


def _analysis_repository(settings: Settings):
    if settings.database_url:
        return _repository(settings)
    if settings.supabase_url and settings.supabase_publishable_key:
        return SupabaseRestRepository(
            settings.supabase_url,
            settings.supabase_publishable_key,
            settings.timeout,
        )
    raise SystemExit(
        "Configure SUPABASE_DB_URL ou as variáveis públicas do Supabase para gerar a análise."
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cocoa-data")
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("collect", "backfill"):
        item = sub.add_parser(command)
        item.add_argument("--source", default="all")
        item.add_argument("--start")
        item.add_argument("--end")
        item.add_argument("--status-file")
    sub.add_parser("migrate")
    sub.add_parser("supabase-check")
    quality = sub.add_parser("quality-check")
    quality.add_argument("--status-file")
    sub.add_parser("build-analysis-dataset")
    sub.add_parser("render-report")
    sub.add_parser("model-readiness")
    return parser


def main() -> None:
    settings = Settings.load()
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    args = build_parser().parse_args()
    if args.command == "render-report":
        print(render_notebook(settings.root))
        return
    if args.command == "build-analysis-dataset":
        paths = build_analysis_dataset(_analysis_repository(settings), settings)
        print("\n".join(f"{name}: {path}" for name, path in paths.items()))
        return

    if args.command == "model-readiness":
        result = evaluate_model_readiness(_analysis_repository(settings))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if not result["ready"]:
            raise SystemExit(2)
        return

    if args.command in {"collect", "backfill"}:
        sources = enabled_sources(settings) if args.source == "all" else [args.source]
        exit_code = 0
        try:
            repository = _repository(settings)
            try:
                batches, failures = Pipeline(settings, repository).run(
                    sources, args.command, _date(args.start), _date(args.end)
                )
            except EssentialSourceError as exc:
                batches, failures, exit_code = exc.batches, exc.failures, 1
            result = {
                "sources": {batch.source: batch.coverage for batch in batches},
                "failures": [
                    {"source": source, "message": message} for source, message in failures
                ],
            }
        except Exception as exc:
            exit_code = 1
            result = {
                "sources": {},
                "failures": [
                    {"source": "pipeline", "message": sanitize_public_message(str(exc))}
                ],
            }
            logging.exception("Falha inesperada na coleta")
        print(_write_status(args.status_file, result))
        if exit_code:
            raise SystemExit(exit_code)
        return

    repository = _repository(settings)
    if args.command == "migrate":
        print("Migrações aplicadas.")
    elif args.command == "supabase-check":
        result = repository.check_connection()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if not result["schema_ready"]:
            raise SystemExit(1)
    elif args.command == "quality-check":
        events = run_quality_checks(repository, settings)
        print(_write_status(args.status_file, events))
        if any(event["severity"] == "error" for event in events):
            raise SystemExit(1)


if __name__ == "__main__":
    main()
