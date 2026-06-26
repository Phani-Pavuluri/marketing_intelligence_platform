"""Lightweight checks for P12 SDK/API usage examples documentation."""

from __future__ import annotations

from pathlib import Path

_DOC = Path("docs/examples/P12_SDK_API_USAGE_EXAMPLES_001.md")

_EXPECTED_ROUTES = (
    "/health",
    "/version",
    "/advisory/cold-start",
    "/readiness/assess",
    "/calibration/map",
    "/intake/overview",
)

_LINKED_DOCS = (
    "docs/product/PRODUCT_ENTRYPOINT_AND_DEMO_EXPERIENCE_PLAN_001.md",
    "docs/product/SYNTHETIC_DEMO_DATASET_STRATEGY_PLAN_001.md",
    "docs/service/DETERMINISTIC_USAGE_MODES.md",
)


def test_p12_usage_examples_doc_exists() -> None:
    assert _DOC.is_file()


def test_p12_doc_mentions_all_six_api_routes() -> None:
    content = _DOC.read_text(encoding="utf-8")
    for route in _EXPECTED_ROUTES:
        assert route in content, f"missing route in P12 doc: {route}"


def test_p12_doc_referenced_paths_exist() -> None:
    repo_root = Path(".")
    for relative in _LINKED_DOCS:
        assert (repo_root / relative).is_file(), relative
