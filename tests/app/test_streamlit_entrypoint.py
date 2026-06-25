"""Tests for canonical vs legacy Streamlit entrypoints."""

from __future__ import annotations

import importlib
from pathlib import Path


def test_canonical_streamlit_app_module_exists() -> None:
    streamlit_app = importlib.import_module("app.streamlit_app")
    assert callable(streamlit_app.main)


def test_canonical_demo_fixtures_and_render_helpers_import() -> None:
    demo_fixtures = importlib.import_module("app.demo_fixtures")
    ui_renderers = importlib.import_module("app.ui_renderers")
    assert hasattr(demo_fixtures, "build_advisory_plan")
    assert hasattr(ui_renderers, "advisory_plan_to_display_dict")


def test_legacy_streamlit_app_imports_and_documents_canonical_entrypoint() -> None:
    legacy = importlib.import_module("mip.app.streamlit_app")
    package = importlib.import_module("mip.app")

    assert legacy.CANONICAL_STREAMLIT_ENTRYPOINT == "app/streamlit_app.py"
    assert package.CANONICAL_STREAMLIT_ENTRYPOINT == "app/streamlit_app.py"
    assert callable(legacy.main)
    assert "backward compatibility" in (legacy.__doc__ or "").lower()
    assert "app/streamlit_app.py" in (legacy.__doc__ or "")


def test_readme_references_canonical_streamlit_command() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")
    assert "poetry run streamlit run app/streamlit_app.py" in readme
    assert "deterministic mode" in readme.lower()
    assert "mip-app" in readme
