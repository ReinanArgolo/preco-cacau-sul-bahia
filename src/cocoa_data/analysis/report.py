from __future__ import annotations

import warnings
from pathlib import Path


def render_notebook(root: Path) -> Path:
    try:
        import nbformat
        from nbconvert import HTMLExporter
        from nbconvert.preprocessors import ExecutePreprocessor
    except ImportError as exc:
        raise RuntimeError("Instale as dependências de análise: pip install -e '.[analysis]'") from exc

    notebook_path = root / "notebooks" / "01_analise_integrada_cacau.ipynb"
    output_path = root / "data" / "reports" / "analise_integrada_cacau.html"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="Cell is missing an id field")
        notebook = nbformat.read(notebook_path, as_version=4)
    for index, cell in enumerate(notebook.cells):
        cell.setdefault("id", f"cell-{index:03d}")
    processor = ExecutePreprocessor(timeout=600, kernel_name="python3")
    processor.preprocess(notebook, {"metadata": {"path": str(root)}})
    exporter = HTMLExporter()
    exporter.exclude_input_prompt = True
    exporter.exclude_output_prompt = True
    html, _ = exporter.from_notebook_node(notebook)
    output_path.write_text(html, encoding="utf-8")
    executed = output_path.with_suffix(".executed.ipynb")
    nbformat.write(notebook, executed)
    return output_path
