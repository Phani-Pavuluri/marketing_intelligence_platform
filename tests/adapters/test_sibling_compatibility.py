"""Tests for sibling repo compatibility registry."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from mip.adapters.base import AdapterRunKind
from mip.adapters.sibling_compatibility import (
    SiblingRepoCompatibilityStatus,
    SiblingRepoExportConfig,
    SiblingRepoName,
    assert_safe_sibling_compatibility,
    build_sibling_repo_compatibility_registry,
    check_sibling_repo_compatibility,
    compatibility_report_to_directory_ref,
    default_mmm_repo_export_config,
    default_panel_exp_repo_export_config,
    discover_exports_for_compatible_repo,
    register_exports_for_compatible_repo,
    resolve_export_directory,
    sibling_compatibility_sections,
)
from mip.adapters.sibling_export_hooks import SiblingExportDirectoryRef
from mip.adapters.sibling_fixtures import SiblingFixtureSource
from mip.evidence.registry import EvidenceRegistry

_REPO_ROOT = Path(__file__).resolve().parents[2]
_FIXTURE_REPO_ROOT = _REPO_ROOT / "tests/fixtures"
_EXPORT_DIR = _FIXTURE_REPO_ROOT / "sibling_exports"
_MMM_FIXTURE_PATH = _EXPORT_DIR / "mmm_adapter_export_fixture.json"


def test_compatible_mmm_config_over_pinned_fixture_directory() -> None:
    report = check_sibling_repo_compatibility(default_mmm_repo_export_config())
    assert report.status in (
        SiblingRepoCompatibilityStatus.COMPATIBLE,
        SiblingRepoCompatibilityStatus.COMPATIBLE_WITH_WARNINGS,
    )
    assert report.compatible_export_count >= 1
    assert report.resolved_export_directory == str(_EXPORT_DIR.resolve())
    assert "1.0.0" in report.schema_versions_found


def test_compatible_panel_exp_config_over_pinned_fixture_directory() -> None:
    report = check_sibling_repo_compatibility(default_panel_exp_repo_export_config())
    assert report.status in (
        SiblingRepoCompatibilityStatus.COMPATIBLE,
        SiblingRepoCompatibilityStatus.COMPATIBLE_WITH_WARNINGS,
    )
    assert report.compatible_export_count >= 1
    assert "panel_exp@fixture-pin-8b-001" in report.source_commit_markers_found


def test_missing_export_directory_returns_not_configured_safely() -> None:
    config = default_mmm_repo_export_config().model_copy(
        update={"export_directory_relative_path": "missing_exports_dir"}
    )
    report = check_sibling_repo_compatibility(config)
    assert report.status == SiblingRepoCompatibilityStatus.NOT_CONFIGURED
    assert report.blocking_reasons
    assert_safe_sibling_compatibility(report)


def test_expected_source_repo_mismatch_blocks_config() -> None:
    data = default_mmm_repo_export_config().model_dump()
    data["expected_source_repo"] = SiblingFixtureSource.PANEL_EXP
    with pytest.raises(ValidationError, match="mmm repo requires expected_source_repo mmm"):
        SiblingRepoExportConfig.model_validate(data)


def test_expected_engine_kind_mismatch_blocks_config() -> None:
    data = default_panel_exp_repo_export_config().model_dump()
    data["expected_engine_kind"] = AdapterRunKind.MMM
    with pytest.raises(ValidationError, match="panel_exp repo requires expected_engine_kind geox"):
        SiblingRepoExportConfig.model_validate(data)


def test_expected_schema_version_mismatch_blocks_compatibility() -> None:
    config = default_mmm_repo_export_config().model_copy(
        update={"expected_schema_version": "9.9.9"}
    )
    report = check_sibling_repo_compatibility(config)
    assert report.status == SiblingRepoCompatibilityStatus.INVALID
    assert report.compatible_export_count == 0
    assert any("schema_version_mismatch" in warning for warning in report.warnings)


def test_export_directory_path_cannot_escape_repo_root_via_dotdot() -> None:
    data = default_mmm_repo_export_config().model_dump()
    data["export_directory_relative_path"] = "../outside"
    with pytest.raises(ValidationError, match="cannot contain"):
        SiblingRepoExportConfig.model_validate(data)


def test_read_only_must_be_true() -> None:
    data = default_mmm_repo_export_config().model_dump()
    data["read_only"] = False
    with pytest.raises(ValidationError, match="read_only"):
        SiblingRepoExportConfig.model_validate(data)


def test_registry_aggregates_mixed_compatible_and_blocked_reports() -> None:
    missing_config = default_mmm_repo_export_config().model_copy(
        update={"export_directory_relative_path": "missing_exports_dir"}
    )
    registry = build_sibling_repo_compatibility_registry(
        [default_mmm_repo_export_config(), missing_config]
    )
    assert len(registry.reports) == 2
    assert registry.aggregate_status in (
        SiblingRepoCompatibilityStatus.BLOCKED,
        SiblingRepoCompatibilityStatus.NOT_CONFIGURED,
        SiblingRepoCompatibilityStatus.COMPATIBLE_WITH_WARNINGS,
    )
    assert registry.blocking_reasons


def test_compatible_report_converts_to_directory_ref() -> None:
    report = check_sibling_repo_compatibility(default_mmm_repo_export_config())
    directory_ref = compatibility_report_to_directory_ref(report)
    assert isinstance(directory_ref, SiblingExportDirectoryRef)
    assert directory_ref.expected_source_repo == SiblingFixtureSource.MMM
    assert directory_ref.expected_engine_kind == AdapterRunKind.MMM


def test_compatible_report_registers_exports_through_phase_8c_path() -> None:
    report = check_sibling_repo_compatibility(default_mmm_repo_export_config())
    registry = EvidenceRegistry()
    discovery, registrations = register_exports_for_compatible_repo(registry, report)
    assert discovery.loaded_exports
    assert registrations
    assert any(item.adapter_output_marker != "not_registered" for item in registrations)


def test_blocked_report_cannot_register_usable_exports() -> None:
    config = default_mmm_repo_export_config().model_copy(
        update={"export_directory_relative_path": "missing_exports_dir"}
    )
    report = check_sibling_repo_compatibility(config)
    with pytest.raises(ValueError, match="incompatible report cannot register"):
        register_exports_for_compatible_repo(EvidenceRegistry(), report)


def test_forbidden_claims_are_rejected(tmp_path: Path) -> None:
    payload = json.loads(_MMM_FIXTURE_PATH.read_text(encoding="utf-8"))
    payload["warnings"] = ["actual ROI"]
    export_dir = tmp_path / "sibling_exports"
    export_dir.mkdir()
    (export_dir / "mmm_adapter_export_fixture.json").write_text(json.dumps(payload))
    config = default_mmm_repo_export_config().model_copy(update={"repo_path": str(tmp_path)})
    report = check_sibling_repo_compatibility(config)
    assert report.status == SiblingRepoCompatibilityStatus.INVALID


def test_discover_exports_for_compatible_repo_uses_phase_8c() -> None:
    report = check_sibling_repo_compatibility(default_panel_exp_repo_export_config())
    discovery = discover_exports_for_compatible_repo(report)
    assert discovery.loaded_exports
    assert discovery.loaded_exports[0].source_repo == SiblingFixtureSource.PANEL_EXP


def test_resolve_export_directory_returns_absolute_path() -> None:
    resolved = resolve_export_directory(default_mmm_repo_export_config())
    assert resolved == _EXPORT_DIR.resolve()


def test_sibling_compatibility_sections_are_safe() -> None:
    report = check_sibling_repo_compatibility(default_mmm_repo_export_config())
    sections = sibling_compatibility_sections(report)
    assert sections["repo_name"] == SiblingRepoName.MMM.value
    assert sections["status"]
    combined = str(sections).lower()
    assert "actual roi" not in combined
    assert "budget recommendation" not in combined


def test_public_imports() -> None:
    from mip.adapters import (
        SiblingRepoCompatibilityRegistry,
        SiblingRepoCompatibilityReport,
        SiblingRepoCompatibilityStatus,
        SiblingRepoExportConfig,
        SiblingRepoName,
        assert_safe_sibling_compatibility,
        build_default_sibling_compatibility_sections,
        build_sibling_repo_compatibility_registry,
        check_sibling_repo_compatibility,
        compatibility_report_to_directory_ref,
        register_exports_for_compatible_repo,
        resolve_export_directory,
        sibling_compatibility_sections,
    )

    assert SiblingRepoName.MMM.value == "mmm"
    assert callable(check_sibling_repo_compatibility)
    assert callable(build_sibling_repo_compatibility_registry)
    assert callable(resolve_export_directory)
    assert callable(compatibility_report_to_directory_ref)
    assert callable(register_exports_for_compatible_repo)
    assert callable(sibling_compatibility_sections)
    assert callable(assert_safe_sibling_compatibility)
    assert callable(build_default_sibling_compatibility_sections)
    assert SiblingRepoExportConfig is not None
    assert SiblingRepoCompatibilityReport is not None
    assert SiblingRepoCompatibilityRegistry is not None
    assert SiblingRepoCompatibilityStatus is not None
