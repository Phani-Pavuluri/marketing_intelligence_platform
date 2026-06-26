"""Tests for Stage A synthetic fixture loader helpers."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from mip.contracts.calibration_intake import (
    CalibrationEvidenceInput,
    CalibrationMappingRequirement,
)
from mip.examples.stage_a_fixtures import (
    StageAFixtureError,
    list_stage_a_fixtures,
    load_stage_a_fixture,
    load_stage_a_fixtures_by_workflow_area,
    load_stage_a_manifest,
    stage_a_fixture_path,
)
from mip.workflows.intake.calibration_mapping import map_evidence_to_calibration_signal

_STAGE_A_ROOT = (
    Path(__file__).resolve().parents[2] / "examples" / "fixtures" / "stage_a"
)


def test_load_stage_a_manifest_returns_all_entries() -> None:
    entries = load_stage_a_manifest()
    assert len(entries) >= 15
    assert all(isinstance(entry, dict) for entry in entries)
    assert all(entry.get("fixture_id") for entry in entries)


def test_list_stage_a_fixtures_returns_all_entries() -> None:
    entries = list_stage_a_fixtures()
    manifest_entries = load_stage_a_manifest()
    assert len(entries) == len(manifest_entries)


def test_list_stage_a_fixtures_filters_by_workflow_area() -> None:
    calibration_entries = list_stage_a_fixtures(workflow_area="calibration_mapping")
    assert calibration_entries
    assert all(
        entry.get("workflow_area") == "calibration_mapping" for entry in calibration_entries
    )
    assert {entry["fixture_id"] for entry in calibration_entries} == {
        "experiment_readout_valid",
        "experiment_readout_missing_se",
        "experiment_readout_metric_mismatch",
    }


@pytest.mark.parametrize("fixture_id", [entry["fixture_id"] for entry in load_stage_a_manifest()])
def test_load_stage_a_fixture_by_id(fixture_id: str) -> None:
    payload = load_stage_a_fixture(fixture_id)
    assert isinstance(payload, dict)
    assert payload.get("synthetic") is True
    assert payload.get("fixture_id") == fixture_id
    assert payload.get("requires_mmm_or_geox_engine") is False


def test_load_stage_a_fixtures_by_workflow_area_returns_payloads() -> None:
    payloads = load_stage_a_fixtures_by_workflow_area("intake_routing")
    assert len(payloads) == 4
    assert all(payload.get("workflow_area") == "intake_routing" for payload in payloads)


def test_missing_fixture_id_raises_stage_a_fixture_error() -> None:
    with pytest.raises(StageAFixtureError, match="fixture id not found"):
        load_stage_a_fixture("does_not_exist_fixture")


def test_stage_a_fixture_path_resolves_under_stage_a_root() -> None:
    path = stage_a_fixture_path("experiment_readout_valid")
    assert path.is_file()
    assert _STAGE_A_ROOT.resolve() in path.resolve().parents


def test_fixture_paths_do_not_escape_stage_a_root() -> None:
    for entry in load_stage_a_manifest():
        path = stage_a_fixture_path(str(entry["fixture_id"]))
        assert _STAGE_A_ROOT.resolve() in path.resolve().parents


def test_helpers_work_from_different_working_directory() -> None:
    original_cwd = Path.cwd()
    try:
        os.chdir(Path("/tmp"))
        payload = load_stage_a_fixture("local_fitness_studio")
        assert payload["fixture_id"] == "local_fitness_studio"
    finally:
        os.chdir(original_cwd)


def test_calibration_fixture_loads_into_mapping_workflow() -> None:
    payload = load_stage_a_fixture("experiment_readout_valid")
    evidence = CalibrationEvidenceInput(**payload["evidence"])
    requirement = CalibrationMappingRequirement(**payload["requirement"])
    signal, report = map_evidence_to_calibration_signal(evidence, requirement)
    assert signal is not None
    assert report.mapped_signal_id is not None
