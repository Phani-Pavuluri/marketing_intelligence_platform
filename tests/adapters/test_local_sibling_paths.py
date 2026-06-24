"""Tests for local sibling export path wiring."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest
from pydantic import ValidationError

from mip.adapters.base import AdapterRunKind
from mip.adapters.local_sibling_paths import (
    LocalSiblingPathStatus,
    LocalSiblingRepoPathDefaults,
    assert_safe_local_sibling_path_result,
    build_local_mmm_export_config,
    build_local_panel_exp_export_config,
    build_local_sibling_compatibility_registry,
    default_local_sibling_path_config,
    local_sibling_path_sections,
    register_compatible_local_sibling_exports,
)
from mip.adapters.sibling_compatibility import SiblingRepoCompatibilityStatus
from mip.adapters.sibling_fixtures import SiblingFixtureSource
from mip.evidence.registry import EvidenceRegistry

_REPO_ROOT = Path(__file__).resolve().parents[2]
_EXPORT_FIXTURE_DIR = _REPO_ROOT / "tests/fixtures/sibling_exports"
_MMM_FIXTURE = _EXPORT_FIXTURE_DIR / "mmm_adapter_export_fixture.json"
_GEOX_FIXTURE = _EXPORT_FIXTURE_DIR / "geox_adapter_export_fixture.json"


def _compatible_local_defaults(tmp_path: Path) -> LocalSiblingRepoPathDefaults:
    mmm_root = tmp_path / "mmm"
    panel_root = tmp_path / "panel_exp"
    mmm_export = mmm_root / "integrations/mip/exports"
    panel_export = panel_root / "integrations/mip/exports"
    mmm_export.mkdir(parents=True)
    panel_export.mkdir(parents=True)
    shutil.copy(_MMM_FIXTURE, mmm_export / "mmm_adapter_export_fixture.json")
    shutil.copy(_GEOX_FIXTURE, panel_export / "geox_adapter_export_fixture.json")
    return default_local_sibling_path_config().model_copy(
        update={
            "mmm_repo_path": str(mmm_root),
            "panel_exp_repo_path": str(panel_root),
        }
    )


def test_default_local_path_config_builds() -> None:
    defaults = default_local_sibling_path_config()
    assert defaults.mmm_repo_path == "/Users/phani/Desktop/mmm"
    assert defaults.panel_exp_repo_path == "/Users/phani/Desktop/panel_exp"
    assert defaults.export_directory_relative_path == "integrations/mip/exports"
    assert defaults.read_only is True
    assert "local_sibling_export_path_wiring_only" in defaults.labels


def test_mmm_config_has_source_repo_mmm_and_engine_kind_mmm() -> None:
    config = build_local_mmm_export_config()
    assert config.expected_source_repo == SiblingFixtureSource.MMM
    assert config.expected_engine_kind == AdapterRunKind.MMM
    assert str(config.repo_name) == "mmm"


def test_panel_exp_config_has_source_repo_panel_exp_and_engine_kind_geox() -> None:
    config = build_local_panel_exp_export_config()
    assert config.expected_source_repo == SiblingFixtureSource.PANEL_EXP
    assert config.expected_engine_kind == AdapterRunKind.GEOX
    assert str(config.repo_name) == "panel_exp"


def test_export_relative_path_cannot_escape_repo_root() -> None:
    data = default_local_sibling_path_config().model_dump()
    data["export_directory_relative_path"] = "../outside"
    with pytest.raises(ValidationError, match="cannot escape repo root"):
        LocalSiblingRepoPathDefaults.model_validate(data)


def test_read_only_must_be_true() -> None:
    data = default_local_sibling_path_config().model_dump()
    data["read_only"] = False
    with pytest.raises(ValidationError, match="read_only"):
        LocalSiblingRepoPathDefaults.model_validate(data)


def test_missing_local_repo_path_returns_safe_not_found_result(tmp_path: Path) -> None:
    defaults = default_local_sibling_path_config().model_copy(
        update={
            "mmm_repo_path": str(tmp_path / "missing_mmm"),
            "panel_exp_repo_path": str(tmp_path / "missing_panel_exp"),
        }
    )
    result = build_local_sibling_compatibility_registry(defaults)
    assert result.aggregate_status == LocalSiblingPathStatus.NOT_FOUND
    assert result.mmm_report is not None
    assert result.panel_exp_report is not None
    assert result.blocking_reasons or result.mmm_report.blocking_reasons
    assert_safe_local_sibling_path_result(result)


def test_compatible_temp_directory_produces_compatible_report(tmp_path: Path) -> None:
    defaults = _compatible_local_defaults(tmp_path)
    result = build_local_sibling_compatibility_registry(defaults)
    assert result.aggregate_status in (
        LocalSiblingPathStatus.COMPATIBLE,
        LocalSiblingPathStatus.COMPATIBLE_WITH_WARNINGS,
    )
    assert result.mmm_report is not None
    assert result.mmm_report.compatible_export_count >= 1
    assert result.panel_exp_report is not None
    assert result.panel_exp_report.compatible_export_count >= 1


def test_registration_only_runs_for_compatible_reports(tmp_path: Path) -> None:
    defaults = _compatible_local_defaults(tmp_path)
    registry = EvidenceRegistry()
    result, registrations = register_compatible_local_sibling_exports(registry, defaults)
    assert registrations
    assert any(item.registered_in_registry for item in registrations)
    assert result.mmm_report is not None
    assert result.mmm_report.status in (
        SiblingRepoCompatibilityStatus.COMPATIBLE,
        SiblingRepoCompatibilityStatus.COMPATIBLE_WITH_WARNINGS,
    )


def test_blocked_compatibility_report_does_not_register_usable_exports(tmp_path: Path) -> None:
    defaults = _compatible_local_defaults(tmp_path).model_copy(
        update={"expected_schema_version": "9.9.9"}
    )
    registry = EvidenceRegistry()
    result, registrations = register_compatible_local_sibling_exports(registry, defaults)
    assert not registrations
    assert result.aggregate_status in (
        LocalSiblingPathStatus.INVALID,
        LocalSiblingPathStatus.BLOCKED,
    )


def test_forbidden_claims_are_rejected() -> None:
    defaults = default_local_sibling_path_config().model_copy(
        update={"disclaimer": "actual ROI from local exports"}
    )
    with pytest.raises(ValueError, match="forbidden phrase"):
        assert_safe_local_sibling_path_result(defaults)


def test_local_sibling_path_sections_are_safe(tmp_path: Path) -> None:
    defaults = _compatible_local_defaults(tmp_path)
    result = build_local_sibling_compatibility_registry(defaults)
    sections = local_sibling_path_sections(result)
    assert sections["mmm_repo_path"] == str(tmp_path / "mmm")
    assert sections["aggregate_status"]
    combined = str(sections).lower()
    assert "local_sibling_export_path_wiring_only" in combined
    assert "actual roi" not in combined


def test_public_imports() -> None:
    from mip.adapters import (
        LocalSiblingPathRegistryResult,
        LocalSiblingPathStatus,
        LocalSiblingRepoPathDefaults,
        assert_safe_local_sibling_path_result,
        build_default_local_sibling_path_sections,
        build_local_mmm_export_config,
        build_local_panel_exp_export_config,
        build_local_sibling_compatibility_registry,
        default_local_sibling_path_config,
        local_sibling_path_sections,
        register_compatible_local_sibling_exports,
    )

    assert LocalSiblingPathStatus.CONFIGURED.value == "configured"
    assert callable(default_local_sibling_path_config)
    assert callable(build_local_mmm_export_config)
    assert callable(build_local_panel_exp_export_config)
    assert callable(build_local_sibling_compatibility_registry)
    assert callable(register_compatible_local_sibling_exports)
    assert callable(local_sibling_path_sections)
    assert callable(assert_safe_local_sibling_path_result)
    assert callable(build_default_local_sibling_path_sections)
    assert LocalSiblingRepoPathDefaults is not None
    assert LocalSiblingPathRegistryResult is not None
