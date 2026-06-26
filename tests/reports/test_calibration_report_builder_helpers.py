"""Tests for calibration deterministic report builder helpers."""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path

import pytest

from mip.contracts.deterministic_report import (
    DETERMINISTIC_REPORT_SCHEMA_VERSION,
    GovernanceStatus,
)
from mip.reports.calibration_reports import (
    build_calibration_report_from_stage_a_fixture,
    export_calibration_report_from_stage_a_fixture,
)
from mip.reports.deterministic_reports import DeterministicReportExportError

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


def test_valid_fixture_builds_candidate_report() -> None:
    report = build_calibration_report_from_stage_a_fixture(
        "experiment_readout_valid",
        generated_at=_NOW,
        report_id="det-report-cal-experiment_readout_valid",
    )
    assert report.schema_version == DETERMINISTIC_REPORT_SCHEMA_VERSION
    assert report.governance_status == GovernanceStatus.CANDIDATE
    assert report.source_input_ref.source_fixture_id_or_payload_ref == (
        "experiment_readout_valid"
    )


def test_missing_se_fixture_builds_needs_more_data_report() -> None:
    report = build_calibration_report_from_stage_a_fixture(
        "experiment_readout_missing_se",
        generated_at=_NOW,
    )
    assert report.governance_status == GovernanceStatus.NEEDS_MORE_DATA
    assert "standard_error" in report.missing_data


def test_metric_mismatch_fixture_builds_incompatible_report() -> None:
    report = build_calibration_report_from_stage_a_fixture(
        "experiment_readout_metric_mismatch",
        generated_at=_NOW,
    )
    assert report.governance_status == GovernanceStatus.INCOMPATIBLE


def test_non_calibration_fixture_fails_closed() -> None:
    with pytest.raises(DeterministicReportExportError, match="calibration report build failed"):
        build_calibration_report_from_stage_a_fixture("local_fitness_studio")


@pytest.mark.parametrize(
    "fixture_id",
    [
        "experiment_readout_valid",
        "experiment_readout_missing_se",
        "experiment_readout_metric_mismatch",
    ],
)
def test_exported_json_round_trips(fixture_id: str, tmp_path: Path) -> None:
    output = tmp_path / f"{fixture_id}.json"
    path = export_calibration_report_from_stage_a_fixture(
        fixture_id,
        output,
        generated_at=_NOW,
        report_id=f"det-report-cal-{fixture_id}",
        overwrite=True,
    )
    parsed = json.loads(path.read_text(encoding="utf-8"))
    assert parsed["schema_version"] == DETERMINISTIC_REPORT_SCHEMA_VERSION
    assert parsed["source_input_ref"]["source_fixture_id_or_payload_ref"] == fixture_id


@pytest.mark.parametrize(
    "fixture_id",
    [
        "experiment_readout_valid",
        "experiment_readout_missing_se",
        "experiment_readout_metric_mismatch",
    ],
)
def test_reports_exclude_unsupported_output_claims(fixture_id: str) -> None:
    report = build_calibration_report_from_stage_a_fixture(
        fixture_id,
        generated_at=_NOW,
    )
    text = json.dumps(report.model_dump(mode="json")).lower()
    match = _FORBIDDEN_OUTPUT_CLAIMS.search(text)
    assert match is None, f"forbidden claim in {fixture_id}: {match}"
