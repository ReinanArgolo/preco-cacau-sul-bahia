from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    root: Path
    database_url: str | None
    supabase_url: str | None
    supabase_publishable_key: str | None
    timeout: float
    log_level: str
    sources: dict[str, Any]
    locations: list[dict[str, Any]]
    quality: dict[str, Any]

    @classmethod
    def load(cls, root: Path | None = None) -> "Settings":
        project_root = root or ROOT
        load_dotenv(project_root / ".env", override=False)
        load_dotenv(project_root / "web" / ".env.local", override=False)

        def read_yaml(name: str) -> dict[str, Any]:
            with (project_root / "configs" / name).open(encoding="utf-8") as handle:
                return yaml.safe_load(handle) or {}

        return cls(
            root=project_root,
            database_url=os.getenv("SUPABASE_DB_URL"),
            supabase_url=os.getenv("NEXT_PUBLIC_SUPABASE_URL"),
            supabase_publishable_key=os.getenv("NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY"),
            timeout=float(os.getenv("COCOA_HTTP_TIMEOUT", "45")),
            log_level=os.getenv("COCOA_LOG_LEVEL", "INFO"),
            sources=read_yaml("sources.yaml")["sources"],
            locations=read_yaml("locations.yaml")["locations"],
            quality=read_yaml("quality.yaml")["checks"],
        )
