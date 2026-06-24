"""Tests for sibling-side export producer specifications."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from mip.adapters.base import AdapterRunKind
from mip.adapters.local_sibling_paths import (
    LocalSiblingPathStatus,
    build_local_sibling_compatibility_registry,
    default_local_sibling_path_config,
)
from mip.adapters.sibling_compatibility import (
    SiblingRepoCompatibilityStatus,
    check_sibling_repo_compatibility,
)
from mip.adapters.sibling_export_hooks import (
    SiblingExportDirectoryRef,
    SiblingExportHookStatus,
    load_sibling_exports_from_directory,
)
from mip.adapters.sibling_fixtures import (
    SiblingFixtureArtifactKind,
    SiblingFixtureSource,
    load_sibling_fixture_export,
    validate_sibling_fixture_export,
)
from mip.adapters.sibling_producer_specs import (
    assert_valid_producer_spec_example,
    build_producer_spec_compatibility_config,
    expected_export_directory_for_source_repo,
    producer_spec_doc_paths,
    producer_spec_example_paths,
    producer_spec_summary_sections,
    required_producer_labels,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_EXPORT_RELATIVE = "integrations/mip/exports"


def _producer_examples() -> dict[str, Path]:
    return producer_spec_example_paths()


def test_mmm_producer_example_loads_through_sibling_fixture_export() -> None:
    export = load_sibling_fixture_export(_producer_examples()["mmm"])
    assert export.fixture_id == "producer-spec-mmm-minimal-valid"
    assert export.source_repo == SiblingFixtureSource.MMM


def test_panel_exp_producer_example_loads_through_sibling_fixture_export() -> None:
    export = load_sibling_fixture_export(_producer_examples()["panel_exp"])
    assert export.fixture_id == "producer-spec-panel-exp-minimal-valid"
    assert export.source_repo == SiblingFixtureSource.PANEL_EXP


def test_mmm_producer_example_validates_through_phase_8b_schema() -> None:
    export = load_sibling_fixture_export(_producer_examples()["mmm"])
    assert validate_sibling_fixture_export(export) == []
    assert_valid_producer_spec_example(_producer_examples()["mmm"])


def test_panel_exp_producer_example_validates_through_phase_8b_schema() -> None:
    export = load_sibling_fixture_export(_producer_examples()["panel_exp"])
    assert validate_sibling_fixture_export(export) == []
    assert_valid_producer_spec_example(_producer_examples()["panel_exp"])


def test_producer_examples_discovered_through_phase_8c_directory_loading(
    tmp_path: Path,
) -> None:
    export_dir = tmp_path / _EXPORT_RELATIVE
    export_dir.mkdir(parents=True)
    shutil.copy(_producer_examples()["mmm"], export_dir / "producer_spec_mmm.json")
    directory_ref = SiblingExportDirectoryRef(
        directory_path=str(export_dir),
        expected_source_repo=SiblingFixtureSource.MMM,
        expected_engine_kind=AdapterRunKind.MMM,
    )
    discovery = load_sibling_exports_from_directory(directory_ref)
    assert discovery.status == SiblingExportHookStatus.VALIDATED
    assert len(discovery.loaded_exports) == 1


def test_producer_examples_compatible_through_phase_8d_config_checks(
    tmp_path: Path,
) -> None:
    mmm_root = tmp_path / "mmm"
    export_dir = mmm_root / _EXPORT_RELATIVE
    export_dir.mkdir(parents=True)
    shutil.copy(_producer_examples()["mmm"], export_dir / "producer_spec_mmm.json")
    config = build_producer_spec_compatibility_config(
        SiblingFixtureSource.MMM,
        str(mmm_root),
    )
    report = check_sibling_repo_compatibility(config)
    assert report.status in (
        SiblingRepoCompatibilityStatus.COMPATIBLE,
        SiblingRepoCompatibilityStatus.COMPATIBLE_WITH_WARNINGS,
    )
    assert report.compatible_export_count >= 1


def test_producer_examples_seen_by_local_path_wiring_in_temp_repo_dirs(
    tmp_path: Path,
) -> None:
    mmm_root = tmp_path / "mmm"
    panel_root = tmp_path / "panel_exp"
    mmm_export = mmm_root / _EXPORT_RELATIVE
    panel_export = panel_root / _EXPORT_RELATIVE
    mmm_export.mkdir(parents=True)
    panel_export.mkdir(parents=True)
    shutil.copy(_producer_examples()["mmm"], mmm_export / "producer_spec_mmm.json")
    shutil.copy(
        _producer_examples()["panel_exp"],
        panel_export / "producer_spec_panel_exp.json",
    )
    defaults = default_local_sibling_path_config().model_copy(
        update={
            "mmm_repo_path": str(mmm_root),
            "panel_exp_repo_path": str(panel_root),
        }
    )
    result = build_local_sibling_compatibility_registry(defaults)
    assert result.aggregate_status in (
        LocalSiblingPathStatus.COMPATIBLE,
        LocalSiblingPathStatus.COMPATIBLE_WITH_WARNINGS,
    )


def test_required_producer_labels_are_present() -> None:
    labels = required_producer_labels()
    assert "static_export_file_only" in labels
    assert "not_live_engine_execution" in labels
    for path in _producer_examples().values():
        export = load_sibling_fixture_export(path)
        for label in labels:
            assert label in export.labels


def test_source_repo_engine_artifact_mapping_is_correct() -> None:
    mmm = load_sibling_fixture_export(_producer_examples()["mmm"])
    panel = load_sibling_fixture_export(_producer_examples()["panel_exp"])
    assert mmm.engine_kind == AdapterRunKind.MMM
    assert mmm.artifact_kind == SiblingFixtureArtifactKind.MMM_ADAPTER_OUTPUT
    assert panel.engine_kind == AdapterRunKind.GEOX
    assert panel.artifact_kind == SiblingFixtureArtifactKind.GEOX_ADAPTER_OUTPUT


def test_expected_export_directories_match_spec() -> None:
    assert expected_export_directory_for_source_repo("mmm") == "mmm/integrations/mip/exports/"
    assert (
        expected_export_directory_for_source_repo("panel_exp")
        == "panel_exp/integrations/mip/exports/"
    )


@pytest.mark.parametrize("doc_path", producer_spec_doc_paths())
def test_docs_mention_hard_boundaries(doc_path: Path) -> None:
    text = doc_path.read_text(encoding="utf-8").lower()
    assert "integrations/mip/exports" in text
    for phrase in (
        "import",
        "subprocess",
        "execution",
        "training",
        "estimation",
    ):
        assert phrase in text
    for phrase in (
        "roi",
        "lift",
        "causal impact",
        "budget recommendation",
        "production readiness",
    ):
        assert phrase in text


def test_producer_spec_summary_sections_are_safe() -> None:
    sections = producer_spec_summary_sections(_producer_examples()["mmm"])
    assert sections["fixture_id"]
    assert sections["expected_export_directory"] == "mmm/integrations/mip/exports/"
    combined = str(sections).lower()
    assert "actual roi" not in combined


def test_public_imports() -> None:
    from mip.adapters import (
        assert_valid_producer_spec_example,
        expected_export_directory_for_source_repo,
        producer_spec_example_paths,
        producer_spec_summary_sections,
        required_producer_labels,
    )

    assert callable(expected_export_directory_for_source_repo)
    assert callable(required_producer_labels)
    assert callable(assert_valid_producer_spec_example)
    assert callable(producer_spec_summary_sections)
    assert callable(producer_spec_example_paths)
