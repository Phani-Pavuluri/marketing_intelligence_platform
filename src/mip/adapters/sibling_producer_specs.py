"""Sibling-side static export producer specifications for MIP consumption."""

from __future__ import annotations

from pathlib import Path

from mip.adapters.base import AdapterRunKind
from mip.adapters.sibling_compatibility import (
    SiblingRepoExportConfig,
    SiblingRepoName,
)
from mip.adapters.sibling_fixtures import (
    SiblingFixtureSource,
    assert_safe_sibling_fixture_export,
    load_sibling_fixture_export,
)

_EXPORT_SCHEMA_VERSION = "1.0.0"
_EXPORT_RELATIVE_PATH = "integrations/mip/exports"

_REPO_EXPORT_DIRECTORIES = {
    SiblingFixtureSource.MMM: "mmm/integrations/mip/exports/",
    SiblingFixtureSource.PANEL_EXP: "panel_exp/integrations/mip/exports/",
}

_REQUIRED_PRODUCER_LABELS = (
    "static_export_file_only",
    "not_live_engine_execution",
    "not_real_model_result",
    "diagnostic_only",
    "not_decision_ready",
)

_PRODUCER_SPEC_DOCS = (
    "docs/integrations/MIP_SIBLING_EXPORT_PRODUCER_SPEC.md",
    "docs/integrations/MMM_MIP_EXPORT_PRODUCER_SPEC.md",
    "docs/integrations/PANEL_EXP_MIP_EXPORT_PRODUCER_SPEC.md",
)

_REPO_ROOT = Path(__file__).resolve().parents[3]
_MMM_PRODUCER_EXAMPLE = (
    _REPO_ROOT / "tests/fixtures/sibling_exports/producer_spec_mmm_minimal_valid.json"
)
_PANEL_EXP_PRODUCER_EXAMPLE = (
    _REPO_ROOT
    / "tests/fixtures/sibling_exports/producer_spec_panel_exp_minimal_valid.json"
)


def expected_export_directory_for_source_repo(
    source_repo: SiblingFixtureSource | str,
) -> str:
    """Return the canonical sibling export directory for a source repo."""
    key = SiblingFixtureSource(_enum_value(source_repo))
    return _REPO_EXPORT_DIRECTORIES[key]


def required_producer_labels() -> list[str]:
    """Return required labels for sibling-side static export producers."""
    return list(_REQUIRED_PRODUCER_LABELS)


def producer_spec_example_paths() -> dict[str, Path]:
    """Return canonical minimal valid producer spec example paths."""
    return {
        "mmm": _MMM_PRODUCER_EXAMPLE,
        "panel_exp": _PANEL_EXP_PRODUCER_EXAMPLE,
    }


def assert_valid_producer_spec_example(path: Path | str) -> None:
    """Validate a producer spec example through existing MIP export contracts."""
    export = load_sibling_fixture_export(path)
    missing = [
        label for label in _REQUIRED_PRODUCER_LABELS if label not in export.labels
    ]
    if missing:
        msg = f"producer spec example missing required labels: {', '.join(missing)}"
        raise ValueError(msg)
    assert_safe_sibling_fixture_export(export)


def producer_spec_summary_sections(path: Path | str) -> dict[str, object]:
    """Format a producer spec example for display-only summary sections."""
    export = load_sibling_fixture_export(path)
    assert_valid_producer_spec_example(path)
    return {
        "fixture_id": export.fixture_id,
        "source_repo": _enum_value(export.source_repo),
        "source_commit_marker": export.source_commit_marker,
        "export_schema_version": export.export_schema_version,
        "artifact_kind": _enum_value(export.artifact_kind),
        "engine_kind": _enum_value(export.engine_kind),
        "config_marker": export.config_marker,
        "validation_status": _enum_value(export.validation_status),
        "labels": list(export.labels),
        "warnings": list(export.warnings),
        "expected_export_directory": expected_export_directory_for_source_repo(
            export.source_repo
        ),
        "required_producer_labels": required_producer_labels(),
        "disclaimer": export.disclaimer,
    }


def producer_spec_doc_paths() -> list[Path]:
    """Return paths to sibling export producer specification documents."""
    return [_REPO_ROOT / doc_path for doc_path in _PRODUCER_SPEC_DOCS]


def build_producer_spec_compatibility_config(
    source_repo: SiblingFixtureSource,
    repo_path: str,
) -> SiblingRepoExportConfig:
    """Build a Phase 8D compatibility config for a producer export directory."""
    if source_repo == SiblingFixtureSource.MMM:
        return SiblingRepoExportConfig(
            repo_name=SiblingRepoName.MMM,
            repo_path=repo_path,
            export_directory_relative_path=_EXPORT_RELATIVE_PATH,
            expected_source_repo=SiblingFixtureSource.MMM,
            expected_engine_kind=AdapterRunKind.MMM,
            expected_schema_version=_EXPORT_SCHEMA_VERSION,
            labels=[
                "sibling_repo_compatibility_check_only",
                "readonly_export_contract_only",
                "static_export_file_only",
                "not_live_engine_execution",
                "not_real_model_result",
                "diagnostic_only",
                "not_decision_ready",
            ],
        )
    return SiblingRepoExportConfig(
        repo_name=SiblingRepoName.PANEL_EXP,
        repo_path=repo_path,
        export_directory_relative_path=_EXPORT_RELATIVE_PATH,
        expected_source_repo=SiblingFixtureSource.PANEL_EXP,
        expected_engine_kind=AdapterRunKind.GEOX,
        expected_schema_version=_EXPORT_SCHEMA_VERSION,
        labels=[
            "sibling_repo_compatibility_check_only",
            "readonly_export_contract_only",
            "static_export_file_only",
            "not_live_engine_execution",
            "not_real_model_result",
            "diagnostic_only",
            "not_decision_ready",
        ],
    )


def _enum_value(value: object) -> str:
    if isinstance(value, str):
        return value
    return str(getattr(value, "value", value))


__all__ = [
    "assert_valid_producer_spec_example",
    "build_producer_spec_compatibility_config",
    "expected_export_directory_for_source_repo",
    "producer_spec_doc_paths",
    "producer_spec_example_paths",
    "producer_spec_summary_sections",
    "required_producer_labels",
]
