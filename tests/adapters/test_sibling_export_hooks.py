"""Tests for read-only sibling export directory hooks."""

from __future__ import annotations

import json
from pathlib import Path

from mip.adapters.base import AdapterRunKind
from mip.adapters.sibling_export_hooks import (
    SiblingExportDirectoryRef,
    SiblingExportHookStatus,
    assert_safe_sibling_export_hook_result,
    default_sample_export_directory,
    discover_sibling_export_files,
    load_sibling_exports_from_directory,
    register_sibling_exports_from_directory,
    sibling_export_discovery_sections,
    validate_sibling_export_directory,
)
from mip.adapters.sibling_fixtures import SiblingFixtureSource
from mip.contracts import ExperimentEvidence
from mip.evidence.registry import EvidenceRegistry

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SAMPLE_EXPORT_DIR = _REPO_ROOT / "tests/fixtures/sibling_exports"
_MMM_FIXTURE_PATH = _SAMPLE_EXPORT_DIR / "mmm_adapter_export_fixture.json"


def test_discovers_pinned_fixture_files_from_sample_directory() -> None:
    directory_ref = SiblingExportDirectoryRef(directory_path=str(_SAMPLE_EXPORT_DIR))
    discovery = discover_sibling_export_files(directory_ref)
    assert discovery.status == SiblingExportHookStatus.DISCOVERED
    assert len(discovery.discovered_file_paths) == 2
    names = {Path(path).name for path in discovery.discovered_file_paths}
    assert names == {
        "mmm_adapter_export_fixture.json",
        "geox_adapter_export_fixture.json",
    }


def test_loads_valid_exports_from_directory() -> None:
    directory_ref = SiblingExportDirectoryRef(directory_path=str(_SAMPLE_EXPORT_DIR))
    discovery = load_sibling_exports_from_directory(directory_ref)
    validated = validate_sibling_export_directory(discovery)
    assert validated.status == SiblingExportHookStatus.VALIDATED
    assert len(validated.loaded_exports) == 2


def test_registers_valid_geox_export_into_registry_path() -> None:
    registry = EvidenceRegistry()
    directory_ref = SiblingExportDirectoryRef(directory_path=str(_SAMPLE_EXPORT_DIR))
    discovery, registrations = register_sibling_exports_from_directory(registry, directory_ref)
    assert discovery.status == SiblingExportHookStatus.VALIDATED
    geox_registration = next(
        item for item in registrations if "geox" in item.export_fixture_id
    )
    assert geox_registration.registered_in_registry is True
    assert geox_registration.governance_artifact_marker is not None
    assert registry.list_evidence()


def test_registers_mmm_export_through_trust_report_path() -> None:
    registry = EvidenceRegistry()
    directory_ref = SiblingExportDirectoryRef(directory_path=str(_SAMPLE_EXPORT_DIR))
    _, registrations = register_sibling_exports_from_directory(registry, directory_ref)
    mmm_registration = next(item for item in registrations if "mmm" in item.export_fixture_id)
    assert mmm_registration.trust_report_marker is not None
    assert mmm_registration.governance_artifact_marker is not None
    assert mmm_registration.registered_in_registry is False


def test_missing_directory_returns_not_configured_result_safely() -> None:
    directory_ref = SiblingExportDirectoryRef(
        directory_path=str(_REPO_ROOT / "tests/fixtures/missing_sibling_exports")
    )
    discovery = discover_sibling_export_files(directory_ref)
    assert discovery.status == SiblingExportHookStatus.NOT_CONFIGURED
    assert discovery.blocking_reasons
    assert_safe_sibling_export_hook_result(discovery)


def test_malformed_json_becomes_invalid_result(tmp_path: Path) -> None:
    bad_file = tmp_path / "bad_export.json"
    bad_file.write_text("{not valid json", encoding="utf-8")
    directory_ref = SiblingExportDirectoryRef(directory_path=str(tmp_path))
    discovery = load_sibling_exports_from_directory(directory_ref)
    assert discovery.status == SiblingExportHookStatus.INVALID
    assert any("malformed_json" in reason for reason in discovery.blocking_reasons)


def test_non_json_files_ignored(tmp_path: Path) -> None:
    (tmp_path / "notes.txt").write_text("ignore me", encoding="utf-8")
    payload = json.loads(_MMM_FIXTURE_PATH.read_text(encoding="utf-8"))
    (tmp_path / "valid_export.json").write_text(json.dumps(payload), encoding="utf-8")
    directory_ref = SiblingExportDirectoryRef(directory_path=str(tmp_path))
    discovery = discover_sibling_export_files(directory_ref)
    assert len(discovery.discovered_file_paths) == 1
    assert Path(discovery.discovered_file_paths[0]).name == "valid_export.json"


def test_source_repo_mismatch_blocks_export(tmp_path: Path) -> None:
    payload = json.loads(_MMM_FIXTURE_PATH.read_text(encoding="utf-8"))
    (tmp_path / "mmm_adapter_export_fixture.json").write_text(json.dumps(payload), encoding="utf-8")
    directory_ref = SiblingExportDirectoryRef(
        directory_path=str(tmp_path),
        expected_source_repo=SiblingFixtureSource.PANEL_EXP,
    )
    discovery = load_sibling_exports_from_directory(directory_ref)
    assert discovery.status == SiblingExportHookStatus.INVALID
    assert any("source_repo_mismatch" in reason for reason in discovery.blocking_reasons)


def test_engine_kind_mismatch_blocks_export(tmp_path: Path) -> None:
    payload = json.loads(_MMM_FIXTURE_PATH.read_text(encoding="utf-8"))
    (tmp_path / "mmm_adapter_export_fixture.json").write_text(json.dumps(payload), encoding="utf-8")
    directory_ref = SiblingExportDirectoryRef(
        directory_path=str(tmp_path),
        expected_engine_kind=AdapterRunKind.GEOX,
    )
    discovery = load_sibling_exports_from_directory(directory_ref)
    assert discovery.status == SiblingExportHookStatus.INVALID
    assert any("engine_kind_mismatch" in reason for reason in discovery.blocking_reasons)


def test_symlink_not_followed_by_default(tmp_path: Path) -> None:
    payload = json.loads(_MMM_FIXTURE_PATH.read_text(encoding="utf-8"))
    real_file = tmp_path / "real_export.json"
    real_file.write_text(json.dumps(payload), encoding="utf-8")
    symlink_file = tmp_path / "linked_export.json"
    symlink_file.symlink_to(real_file)
    directory_ref = SiblingExportDirectoryRef(directory_path=str(tmp_path))
    discovery = discover_sibling_export_files(directory_ref)
    names = {Path(path).name for path in discovery.discovered_file_paths}
    assert names == {"real_export.json"}


def test_forbidden_claims_are_rejected(tmp_path: Path) -> None:
    payload = json.loads(_MMM_FIXTURE_PATH.read_text(encoding="utf-8"))
    payload["warnings"] = ["actual ROI"]
    (tmp_path / "mmm_adapter_export_fixture.json").write_text(json.dumps(payload), encoding="utf-8")
    directory_ref = SiblingExportDirectoryRef(directory_path=str(tmp_path))
    discovery = load_sibling_exports_from_directory(directory_ref)
    assert discovery.status == SiblingExportHookStatus.INVALID
    assert discovery.blocking_reasons


def test_sibling_export_discovery_sections_are_safe() -> None:
    directory_ref = SiblingExportDirectoryRef(directory_path=str(_SAMPLE_EXPORT_DIR))
    discovery, registrations = register_sibling_exports_from_directory(
        EvidenceRegistry(),
        directory_ref,
    )
    sections = sibling_export_discovery_sections(discovery, registrations)
    assert sections["directory_path"] == str(_SAMPLE_EXPORT_DIR)
    assert sections["status"] == "validated"
    assert sections["discovered_file_paths"]
    assert sections["registration_results"]
    combined = str(sections).lower()
    assert "actual roi" not in combined
    assert "budget recommendation" not in combined


def test_default_sample_export_directory_points_to_committed_fixtures() -> None:
    assert default_sample_export_directory() == _SAMPLE_EXPORT_DIR


def test_registration_artifacts_match_governance_types() -> None:
    registry = EvidenceRegistry()
    directory_ref = SiblingExportDirectoryRef(directory_path=str(_SAMPLE_EXPORT_DIR))
    _, registrations = register_sibling_exports_from_directory(registry, directory_ref)
    geox_registration = next(
        item for item in registrations if "geox" in item.export_fixture_id
    )
    mmm_registration = next(item for item in registrations if "mmm" in item.export_fixture_id)
    evidence = registry.get_evidence(geox_registration.governance_artifact_marker or "")
    assert isinstance(evidence, ExperimentEvidence)
    assert mmm_registration.governance_artifact_marker is not None
    assert mmm_registration.governance_artifact_marker.startswith("adapter:mmm:")


def test_public_imports() -> None:
    from mip.adapters import (
        SiblingExportDirectoryRef,
        SiblingExportHookStatus,
        assert_safe_sibling_export_hook_result,
        build_default_sibling_export_hook_sections,
        discover_sibling_export_files,
        load_sibling_exports_from_directory,
        register_sibling_exports_from_directory,
        sibling_export_discovery_sections,
        validate_sibling_export_directory,
    )

    assert SiblingExportHookStatus.DISCOVERED.value == "discovered"
    assert callable(discover_sibling_export_files)
    assert callable(load_sibling_exports_from_directory)
    assert callable(validate_sibling_export_directory)
    assert callable(register_sibling_exports_from_directory)
    assert callable(sibling_export_discovery_sections)
    assert callable(assert_safe_sibling_export_hook_result)
    assert callable(build_default_sibling_export_hook_sections)
    assert SiblingExportDirectoryRef is not None
