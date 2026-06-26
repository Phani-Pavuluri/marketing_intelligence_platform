"""Validation tests for Stage A synthetic deterministic fixtures."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pytest

from mip.contracts.calibration_intake import (
    CalibrationEvidenceInput,
    CalibrationIntakeStatus,
    CalibrationMappingRequirement,
)
from mip.workflows.intake.calibration_mapping import map_evidence_to_calibration_signal

_REPO_ROOT = Path(__file__).resolve().parents[2]
_STAGE_A = _REPO_ROOT / "examples" / "fixtures" / "stage_a"
_MANIFEST = _STAGE_A / "manifest.json"

_FORBIDDEN_OUTPUT_CLAIMS = re.compile(
    r"\b("
    r"channel_roi|"
    r"response_curve|"
    r"optimizer_output|"
    r"matched_markets|"
    r"treatment_assignment|"
    r"causal_lift|"
    r"power_mde|"
    r"mmm_fitted|"
    r"budget_optimization_result"
    r")\b",
    re.IGNORECASE,
)

_RAW_ROW_INDICATORS = ("user_id", "customer_id", "raw_rows", "row_level_data")


def _load_manifest() -> dict[str, Any]:
    return json.loads(_MANIFEST.read_text(encoding="utf-8"))  # type: ignore[no-any-return]


def _load_fixture(relative_path: str) -> dict[str, Any]:
    return json.loads((_REPO_ROOT / relative_path).read_text(encoding="utf-8"))  # type: ignore[no-any-return]


def _fixture_paths() -> list[str]:
    manifest = _load_manifest()
    return [entry["path"] for entry in manifest["fixtures"]]


@pytest.fixture(scope="module")
def manifest() -> dict[str, Any]:
    return _load_manifest()


def test_manifest_exists_and_is_valid_json() -> None:
    assert _MANIFEST.is_file()
    data = _load_manifest()
    assert data.get("schema_version") == "stage_a_v1"
    assert data.get("synthetic") is True
    assert isinstance(data.get("fixtures"), list)
    assert len(data["fixtures"]) >= 15


@pytest.mark.parametrize("relative_path", _fixture_paths())
def test_manifest_paths_exist(relative_path: str) -> None:
    assert (_REPO_ROOT / relative_path).is_file(), relative_path


@pytest.mark.parametrize("relative_path", _fixture_paths())
def test_fixtures_are_valid_json_with_synthetic_marker(relative_path: str) -> None:
    payload = _load_fixture(relative_path)
    assert payload.get("synthetic") is True, relative_path
    assert payload.get("fixture_id"), relative_path
    assert payload.get("workflow_area"), relative_path
    assert payload.get("requires_mmm_or_geox_engine") is False, relative_path


def test_manifest_entries_require_no_engine(manifest: dict[str, Any]) -> None:
    for entry in manifest["fixtures"]:
        assert entry.get("requires_mmm_or_geox_engine") is False, entry["fixture_id"]


def _text_for_forbidden_claim_scan(payload: dict[str, Any]) -> str:
    """Serialize fixture text excluding fields that legitimately mention blocked claims."""
    excluded_keys = {
        "blocked_claims",
        "why_blocked",
        "user_request",
        "safe_alternative",
        "examples",
        "notes",
        "missing_for_geox",
        "missing_for_measurement",
        "structural_support",
    }
    filtered = {key: value for key, value in payload.items() if key not in excluded_keys}
    return json.dumps(filtered).lower()


def test_no_forbidden_advanced_output_claims_in_fixtures() -> None:
    for relative_path in _fixture_paths():
        payload = _load_fixture(relative_path)
        text = _text_for_forbidden_claim_scan(payload)
        match = _FORBIDDEN_OUTPUT_CLAIMS.search(text)
        assert match is None, f"{relative_path} contains forbidden claim: {match}"


def test_readiness_fixtures_are_summaries_not_raw_rows() -> None:
    readiness_dir = _STAGE_A / "readiness"
    for path in sorted(readiness_dir.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload.get("summary_type") or payload.get("structural_support"), path.name
        serialized = json.dumps(payload).lower()
        for indicator in _RAW_ROW_INDICATORS:
            assert indicator not in serialized, f"{path.name} looks like raw row data"


def test_governance_examples_are_educational_only() -> None:
    payload = _load_fixture(
        "examples/fixtures/stage_a/governance/unsupported_claim_examples.json"
    )
    assert payload["workflow_area"] == "governance_education"
    assert isinstance(payload.get("examples"), list)
    assert len(payload["examples"]) >= 3
    for example in payload["examples"]:
        assert "user_request" in example
        assert "why_blocked" in example
        assert "safe_alternative" in example


@pytest.mark.parametrize(
    ("fixture_path", "expected_status"),
    [
        (
            "examples/fixtures/stage_a/calibration/experiment_readout_valid.json",
            CalibrationIntakeStatus.MAPPED,
        ),
        (
            "examples/fixtures/stage_a/calibration/experiment_readout_missing_se.json",
            CalibrationIntakeStatus.NEEDS_MORE_DATA,
        ),
        (
            "examples/fixtures/stage_a/calibration/experiment_readout_metric_mismatch.json",
            CalibrationIntakeStatus.INCOMPATIBLE,
        ),
    ],
)
def test_calibration_fixtures_load_into_mapping_workflow(
    fixture_path: str,
    expected_status: CalibrationIntakeStatus,
) -> None:
    payload = _load_fixture(fixture_path)
    evidence = CalibrationEvidenceInput(**payload["evidence"])
    requirement = CalibrationMappingRequirement(**payload["requirement"])
    signal, report = map_evidence_to_calibration_signal(evidence, requirement)
    assert report.status == expected_status
    if expected_status == CalibrationIntakeStatus.MAPPED:
        assert signal is not None
    else:
        assert signal is None


def test_calibration_missing_se_fixture_has_null_uncertainty() -> None:
    payload = _load_fixture(
        "examples/fixtures/stage_a/calibration/experiment_readout_missing_se.json"
    )
    evidence = payload["evidence"]
    assert evidence.get("standard_error") is None
    assert evidence.get("confidence_interval_low") is None
    assert evidence.get("confidence_interval_high") is None


def test_calibration_mismatch_fixture_has_metric_mismatch() -> None:
    payload = _load_fixture(
        "examples/fixtures/stage_a/calibration/experiment_readout_metric_mismatch.json"
    )
    assert payload["evidence"]["metric_id"] != payload["requirement"]["required_metric_id"]
