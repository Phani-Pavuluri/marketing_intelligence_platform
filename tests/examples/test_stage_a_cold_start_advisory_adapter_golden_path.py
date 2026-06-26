"""Golden-path tests for Stage A.3 cold-start advisory fixture adapters."""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime

import pytest

from mip.contracts.deterministic_report import (
    DETERMINISTIC_REPORT_SCHEMA_VERSION,
    DeterministicReportEnvelope,
    EvidenceMode,
    GovernanceStatus,
    ReportType,
)
from mip.examples.stage_a_adapters import (
    StageAAdapterError,
    build_cold_start_input_from_stage_a_fixture,
    list_supported_advisory_fixture_ids,
    run_cold_start_advisory_for_stage_a_fixture,
)
from mip.examples.stage_a_fixtures import load_stage_a_fixture

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
    """Scan governed output fields, excluding intentional blocked-claim labels."""
    parts = [
        report.summary,
        " ".join(report.recommended_next_steps),
        " ".join(finding.message for finding in report.findings),
        json.dumps(report.workflow_payload, sort_keys=True),
    ]
    return " ".join(parts).lower()


def test_local_fitness_studio_loads_via_stage_a_loader() -> None:
    payload = load_stage_a_fixture("local_fitness_studio")
    assert payload["fixture_id"] == "local_fitness_studio"
    assert payload["workflow_area"] == "cold_start_advisory"


def test_adapter_builds_cold_start_workflow_input() -> None:
    adapter_input = build_cold_start_input_from_stage_a_fixture("local_fitness_studio")
    profile = adapter_input["business_profile"]
    assert adapter_input["synthetic"] is True
    assert profile.profile_id == "stage-a-local_fitness_studio"
    assert profile.geography == "Austin, TX"
    assert profile.monthly_budget == "$1500"


def test_local_fitness_studio_golden_path_envelope() -> None:
    report = run_cold_start_advisory_for_stage_a_fixture(
        "local_fitness_studio",
        generated_at=_NOW,
        report_id="det-report-adv-local_fitness_studio",
    )
    assert report.report_type == ReportType.COLD_START_ADVISORY
    assert report.schema_version == DETERMINISTIC_REPORT_SCHEMA_VERSION
    assert report.governance_status == GovernanceStatus.ADVISORY_ONLY
    assert report.evidence_mode == EvidenceMode.BUSINESS_PROFILE_ONLY
    assert report.source_input_ref.source_fixture_id_or_payload_ref == "local_fitness_studio"
    assert report.recommended_next_steps
    assert report.missing_data
    payload = report.workflow_payload["cold_start_advisory_plan"]
    assert payload["plan_id"] == "adv-stage-a-local_fitness_studio"


def test_non_business_profile_fixture_fails_closed() -> None:
    with pytest.raises(StageAAdapterError, match="not a supported advisory fixture"):
        build_cold_start_input_from_stage_a_fixture("experiment_readout_valid")


def test_unsupported_fixture_id_fails_closed() -> None:
    with pytest.raises(StageAAdapterError, match="not a supported advisory fixture"):
        build_cold_start_input_from_stage_a_fixture("national_weekly_channel_summary")


def test_local_fitness_studio_excludes_unsupported_output_claims() -> None:
    report = run_cold_start_advisory_for_stage_a_fixture(
        "local_fitness_studio",
        generated_at=_NOW,
    )
    text = _advisory_output_text(report)
    match = _FORBIDDEN_OUTPUT_CLAIMS.search(text)
    assert match is None, f"forbidden claim in local_fitness_studio: {match}"
    assert "causal_lift" in report.blocked_claims


def test_forbidden_downstream_uses_preserved() -> None:
    report = run_cold_start_advisory_for_stage_a_fixture(
        "local_fitness_studio",
        generated_at=_NOW,
    )
    forbidden = set(report.forbidden_downstream_uses)
    assert "roi_proof" in forbidden
    assert "budget_optimization" in forbidden
    assert "mmm_model_output" in forbidden


@pytest.mark.parametrize("fixture_id", list_supported_advisory_fixture_ids())
def test_supported_business_profiles_remain_advisory_only(fixture_id: str) -> None:
    report = run_cold_start_advisory_for_stage_a_fixture(
        fixture_id,
        generated_at=_NOW,
        report_id=f"det-report-adv-{fixture_id}",
    )
    assert report.governance_status == GovernanceStatus.ADVISORY_ONLY
    assert report.report_type == ReportType.COLD_START_ADVISORY
