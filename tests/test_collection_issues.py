import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "sync_collection_issues.py"
SPEC = importlib.util.spec_from_file_location("sync_collection_issues", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def test_collection_issue_title_is_deterministic() -> None:
    assert MODULE.issue_title("seagri") == "Falha de coleta: seagri"


def test_quality_errors_are_combined_with_collection_failures() -> None:
    collection = {
        "failures": [{"source": "seagri", "message": "parser alterado"}],
        "sources": {"bcb": {}},
    }
    quality = [
        {"source": "seagri", "severity": "error", "message": "fonte atrasada"},
        {"source": "bcb", "severity": "warning", "message": "aviso"},
        {"source": "icco", "severity": "error", "check_name": "freshness"},
    ]

    failures = MODULE.combined_failures(collection, quality)

    assert failures == {
        "seagri": "parser alterado; fonte atrasada",
        "icco": "freshness",
    }
