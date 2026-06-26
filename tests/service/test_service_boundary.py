"""Static and behavioral boundary tests for P10b.1 service architecture."""

from __future__ import annotations

import ast
import importlib
from pathlib import Path

from fastapi.testclient import TestClient

from mip.service.app import create_app

_SERVICE_DIR = Path("src/mip/service")
_ALLOWED_DEMO_FIXTURE_IMPORTS = {
    "resolve_advisory_demo_inputs",
    "resolve_readiness_demo_context",
    "resolve_calibration_demo_inputs",
    "resolve_intake_demo_inputs",
}
_FORBIDDEN_IMPORT_PREFIXES = (
    "app.ui_renderers",
    "streamlit",
    "openai",
    "anthropic",
    "mip.llm",
)


def _service_py_files() -> list[Path]:
    return sorted(_SERVICE_DIR.glob("*.py"))


def _import_names_from_file(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                if module:
                    names.add(f"{module}.{alias.name}")
                names.add(alias.name)
    return names


def test_service_code_does_not_import_streamlit_or_ui_renderers() -> None:
    for path in _service_py_files():
        names = _import_names_from_file(path)
        for forbidden in _FORBIDDEN_IMPORT_PREFIXES:
            assert not any(
                name == forbidden or name.startswith(f"{forbidden}.")
                for name in names
            ), f"{path} imports forbidden module: {forbidden}"


def test_service_demo_fixture_imports_are_input_resolvers_only() -> None:
    for path in _service_py_files():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom) or node.module != "app.demo_fixtures":
                continue
            imported = {alias.name for alias in node.names}
            disallowed = imported - _ALLOWED_DEMO_FIXTURE_IMPORTS
            assert not disallowed, f"{path} imports disallowed demo_fixtures symbols: {disallowed}"


def test_workflow_routes_still_return_200_for_demo_fixture_keys() -> None:
    client = TestClient(create_app())
    cases = [
        ("post", "/advisory/cold-start", {"sample_key": "dtc_skincare_ecommerce"}),
        ("post", "/readiness/assess", {"sample_key": "national_mmm_ready_geox_blocked"}),
        ("post", "/calibration/map", {"sample_key": "valid_governed_evidence"}),
        ("post", "/intake/overview", {"example_key": "national_mmm_diagnostic"}),
    ]
    for method, route, payload in cases:
        response = getattr(client, method)(route, json=payload)
        assert response.status_code == 200, f"{route} failed: {response.text}"


def test_streamlit_app_import_still_works() -> None:
    streamlit_app = importlib.import_module("app.streamlit_app")
    assert callable(streamlit_app.main)
