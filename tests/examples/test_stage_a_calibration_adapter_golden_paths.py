"""Golden-path tests for Stage A.3 calibration fixture adapters."""

from __future__ import annotations

import re
from datetime import UTC, datetime

import pytest

from mip.contracts.calibration_intake import CalibrationIntakeStatus
from mip.contracts.deterministic_report import (
    DETERMINISTIC_REPORT_SCHEMA_VERSION,
    GovernanceStatus,
    ReportType,
)
from mip.examples.stage_a_adapters import (
    StageAAdapterError,
    build_calibration_input_from_stage_a_fixture,
    run_calibration_mapping_for_stage_a_fixture,
)

_NOW = datetime(2026, 5, 28, 12, 0, tzinfo=UTC)

_FORBIDDEN_OUTPUT_CLAIMS = re.compile(
    r"\b("
    r"channel_roi|"
    r"response_curve|"
    r"optimizer_output|"
    r"matched_markets|"
    r"treatment_assignment|"
    r"power_mde|"
    r"mmm_fitted"
    r")\b",
    re.IGNORECASE,
)


def _envelope_text(fixture_id: str) -> str:
    report = run_calibration_mapping_for_stage_a_fixture(
        fixture_id,
        generated_at=_NOW,
        report_id=f"det-report-cal-{fixture_id}",
    )
    return report.model_dump_json()


def test_valid_readout_golden_path() -> None:
    report = run_calibration_mapping_for_stage_a_fixture(
        "experiment_readout_valid",
        generated_at=_NOW,
        report_id="det-report-cal-experiment_readout_valid",
    )
    assert report.report_type == ReportType.CALIBRATION_MAPPING
    assert report.schema_version == DETERMINISTIC_REPORT_SCHEMA_VERSION
    assert report.governance_status == GovernanceStatus.CANDIDATE
    assert report.source_input_ref.source_fixture_id_or_payload_ref == (
        "experiment_readout_valid"
    )
    payload = report.workflow_payload["calibration_mapping_report"]
    assert payload["status"] == CalibrationIntakeStatus.MAPPED.value
    assert payload["mapped_signal_id"] is not None


def test_missing_se_readout_golden_path() -> None:
    report = run_calibration_mapping_for_stage_a_fixture(
        "experiment_readout_missing_se",
        generated_at=_NOW,
        report_id="det-report-cal-experiment_readout_missing_se",
    )
    assert report.governance_status == GovernanceStatus.NEEDS_MORE_DATA
    payload = report.workflow_payload["calibration_mapping_report"]
    assert payload["status"] == CalibrationIntakeStatus.NEEDS_MORE_DATA.value
    assert payload.get("mapped_signal_id") is None
    assert "standard_error" in report.missing_data
    blocking_messages = [finding.message for finding in report.findings]
    blocking_reasons = payload.get("blocking_reasons", [])
    assert "missing_uncertainty" in blocking_messages or "missing_uncertainty" in (
        blocking_reasons
    )


def test_metric_mismatch_readout_golden_path() -> None:
    report = run_calibration_mapping_for_stage_a_fixture(
        "experiment_readout_metric_mismatch",
        generated_at=_NOW,
        report_id="det-report-cal-experiment_readout_metric_mismatch",
    )
    assert report.governance_status == GovernanceStatus.INCOMPATIBLE
    payload = report.workflow_payload["calibration_mapping_report"]
    assert payload["status"] == CalibrationIntakeStatus.INCOMPATIBLE.value
    assert payload.get("mapped_signal_id") is None


def test_non_calibration_fixture_raises_adapter_error() -> None:
    with pytest.raises(StageAAdapterError, match="not a supported calibration fixture"):
        build_calibration_input_from_stage_a_fixture("local_fitness_studio")


@pytest.mark.parametrize(
    "fixture_id",
    [
        "experiment_readout_valid",
        "experiment_readout_missing_se",
        "experiment_readout_metric_mismatch",
    ],
)
def test_golden_paths_preserve_source_fixture_provenance(fixture_id: str) -> None:
    report = run_calibration_mapping_for_stage_a_fixture(
        fixture_id,
        generated_at=_NOW,
        report_id=f"det-report-cal-{fixture_id}",
    )
    assert report.source_input_ref.source_fixture_id_or_payload_ref == fixture_id
    assert report.artifact_refs[0].source_fixture_id_or_payload_ref == fixture_id


@pytest.mark.parametrize(
    "fixture_id",
    [
        "experiment_readout_valid",
        "experiment_readout_missing_se",
        "experiment_readout_metric_mismatch",
    ],
)
def test_golden_paths_exclude_unsupported_output_claims(fixture_id: str) -> None:
    text = _envelope_text(fixture_id).lower()
    match = _FORBIDDEN_OUTPUT_CLAIMS.search(text)
    assert match is None, f"forbidden claim in {fixture_id}: {match}"
