import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "sync_collection_issues.py"
SPEC = importlib.util.spec_from_file_location("sync_collection_issues", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def test_collection_issue_title_is_deterministic() -> None:
    assert MODULE.issue_title("seagri") == "Falha de coleta: seagri"
