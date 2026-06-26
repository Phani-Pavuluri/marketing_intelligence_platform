"""Tests for cold-start advisory deterministic report builder helpers."""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path

import pytest

from mip.contracts.deterministic_report import (
    DETERMINISTIC_REPORT_SCHEMA_VERSION,
    DeterministicReportEnvelope,
    GovernanceStatus,
    ReportType,
)
from mip.reports.advisory_reports import (
    build_cold_start_advisory_report_from_stage_a_fixture,
    export_cold_start_advisory_report_from_stage_a_fixture,
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


def _advisory_output_text(report: DeterministicReportEnvelope) -> str:
    parts = [
        report.summary,
        " ".join(report.recommended_next_steps),
        " ".join(finding.message for finding in report.findings),
        json.dumps(report.workflow_payload, sort_keys=True),
    ]
    return " ".join(parts).lower()


def test_builds_advisory_report_from_local_fitness_studio() -> None:
    report = build_cold_start_advisory_report_from_stage_a_fixture(
        "local_fitness_studio",
        generated_at=_NOW,
        report_id="det-report-adv-local_fitness_studio",
    )
    assert report.schema_version == DETERMINISTIC_REPORT_SCHEMA_VERSION
    assert report.report_type == ReportType.COLD_START_ADVISORY
    assert report.governance_status == GovernanceStatus.ADVISORY_ONLY
    assert report.source_input_ref.source_fixture_id_or_payload_ref == "local_fitness_studio"


def test_non_business_profile_fixture_fails_closed() -> None:
    with pytest.raises(DeterministicReportExportError, match="advisory report build failed"):
        build_cold_start_advisory_report_from_stage_a_fixture("experiment_readout_valid")


def test_exported_json_round_trips(tmp_path: Path) -> None:
    output = tmp_path / "local_fitness_studio.json"
    path = export_cold_start_advisory_report_from_stage_a_fixture(
        "local_fitness_studio",
        output,
        generated_at=_NOW,
        report_id="det-report-adv-local_fitness_studio",
        overwrite=True,
    )
    parsed = json.loads(path.read_text(encoding="utf-8"))
    assert parsed["schema_version"] == DETERMINISTIC_REPORT_SCHEMA_VERSION
    assert parsed["report_type"] == ReportType.COLD_START_ADVISORY.value
    assert (
        parsed["source_input_ref"]["source_fixture_id_or_payload_ref"]
        == "local_fitness_studio"
    )


def test_overwrite_protection(tmp_path: Path) -> None:
    output = tmp_path / "local_fitness_studio.json"
    export_cold_start_advisory_report_from_stage_a_fixture(
        "local_fitness_studio",
        output,
        generated_at=_NOW,
        overwrite=True,
    )
    with pytest.raises(DeterministicReportExportError, match="report output already exists"):
        export_cold_start_advisory_report_from_stage_a_fixture(
            "local_fitness_studio",
            output,
            generated_at=_NOW,
        )


def test_forbidden_downstream_uses_preserved() -> None:
    report = build_cold_start_advisory_report_from_stage_a_fixture(
        "local_fitness_studio",
        generated_at=_NOW,
    )
    forbidden = set(report.forbidden_downstream_uses)
    assert "roi_proof" in forbidden
    assert "budget_optimization" in forbidden
    assert "geox_design_approval" in forbidden


def test_report_excludes_unsupported_advanced_outputs() -> None:
    report = build_cold_start_advisory_report_from_stage_a_fixture(
        "local_fitness_studio",
        generated_at=_NOW,
    )
    text = _advisory_output_text(report)
    match = _FORBIDDEN_OUTPUT_CLAIMS.search(text)
    assert match is None, f"forbidden claim in advisory report: {match}"
