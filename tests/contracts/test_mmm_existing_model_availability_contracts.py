"""Tests for MMM existing model availability contracts."""

from __future__ import annotations

from datetime import UTC, date, datetime

from mip.contracts import (
    DEFAULT_MAX_MODEL_AGE_DAYS,
    FORBIDDEN_MMM_EXISTING_MODEL_AVAILABILITY_RESULT_FIELD_NAMES,
    RECOMMENDED_NEXT_PLANNING_MMM_CALIBRATION_SIGNAL_MAPPING_AND_READINESS_ARTIFACT,
    RECOMMENDED_NEXT_PLANNING_MMM_TRUSTED_INPUT_AND_MODEL_RUN_ELIGIBILITY_ARTIFACT,
    MMMExistingModelAvailabilityIssueCode,
    MMMExistingModelAvailabilityRequest,
    MMMExistingModelAvailabilityResult,
    MMMExistingModelAvailabilityStatus,
    MMMModelAllowedUse,
    MMMModelArtifact,
    MMMModelArtifactMatch,
    MMMModelArtifactQuery,
    MMMModelArtifactStatus,
    MMMModelDiagnosticStatus,
    MMMModelPromotionStatus,
)

_FORBIDDEN_TOP_LEVEL = (
    "spend_delta",
    "delta_mu",
    "roi",
    "roas",
    "lift",
    "incrementality",
    "optimal_budget",
    "marginal_roi",
    "recommendation",
    "budget_recommendation",
)


def test_required_enums_exist() -> None:
    assert MMMModelArtifactStatus.AVAILABLE in MMMModelArtifactStatus
    assert MMMModelPromotionStatus.PROMOTED_FOR_PLANNING in MMMModelPromotionStatus
    assert MMMModelDiagnosticStatus.PASSED in MMMModelDiagnosticStatus
    assert MMMModelAllowedUse.BUDGET_PLANNING in MMMModelAllowedUse
    assert (
        MMMExistingModelAvailabilityStatus.USABLE_EXISTING_MODEL
        in MMMExistingModelAvailabilityStatus
    )
    assert MMMExistingModelAvailabilityIssueCode.NO_MODEL_EXECUTION in (
        MMMExistingModelAvailabilityIssueCode
    )


def test_models_serialize() -> None:
    artifact = MMMModelArtifact(
        model_id="mmm-1",
        artifact_fingerprint="fp-1",
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
    )
    query = MMMModelArtifactQuery(
        request_id="query-1",
        intended_use=MMMModelAllowedUse.BUDGET_PLANNING,
    )
    assert query.require_promoted is True
    assert query.require_diagnostics_passed is True
    assert query.require_trust_metadata is False
    assert query.max_model_age_days == DEFAULT_MAX_MODEL_AGE_DAYS
    request = MMMExistingModelAvailabilityRequest(
        request_id="req-1",
        query=query,
        candidate_models=[artifact],
    )
    assert request.candidate_models[0].model_id == "mmm-1"


def test_artifact_can_reference_trust_decision_surface_and_readiness_ids() -> None:
    artifact = MMMModelArtifact(
        model_id="mmm-trust-1",
        artifact_fingerprint="fp-trust-1",
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
        trust_report_id="trust-1",
        decision_surface_id="surface-1",
        model_calibration_readiness_id="readiness-1",
    )
    assert artifact.trust_report_id == "trust-1"
    assert artifact.decision_surface_id == "surface-1"
    assert artifact.model_calibration_readiness_id == "readiness-1"


def test_result_has_no_forbidden_top_level_fields() -> None:
    for field_name in MMMExistingModelAvailabilityResult.model_fields:
        assert field_name not in _FORBIDDEN_TOP_LEVEL
    assert "spend_delta" in FORBIDDEN_MMM_EXISTING_MODEL_AVAILABILITY_RESULT_FIELD_NAMES


def test_match_model_serializes() -> None:
    artifact = MMMModelArtifact(
        model_id="mmm-2",
        artifact_fingerprint="fp-2",
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
    )
    match = MMMModelArtifactMatch(model_artifact=artifact, scope_match=True, match_score=10)
    assert match.model_artifact.model_id == "mmm-2"


def test_contracts_exported_from_mip_contracts() -> None:
    result = MMMExistingModelAvailabilityResult(
        request_id="req-export",
        status=MMMExistingModelAvailabilityStatus.BLOCKED_NO_CANDIDATE_MODEL,
    )
    assert result.status == MMMExistingModelAvailabilityStatus.BLOCKED_NO_CANDIDATE_MODEL
    assert (
        RECOMMENDED_NEXT_PLANNING_MMM_CALIBRATION_SIGNAL_MAPPING_AND_READINESS_ARTIFACT
        == "MIP_PLANNING_MMM_CALIBRATION_SIGNAL_MAPPING_AND_READINESS_001"
    )
    assert (
        RECOMMENDED_NEXT_PLANNING_MMM_TRUSTED_INPUT_AND_MODEL_RUN_ELIGIBILITY_ARTIFACT
        == "MIP_PLANNING_MMM_TRUSTED_INPUT_AND_MODEL_RUN_ELIGIBILITY_001"
    )


def test_query_planning_dates_optional() -> None:
    query = MMMModelArtifactQuery(
        request_id="query-dates",
        intended_use=MMMModelAllowedUse.READ_ONLY_SUMMARY,
        planning_start_date=date(2026, 1, 1),
        planning_end_date=date(2026, 6, 1),
    )
    assert query.planning_start_date == date(2026, 1, 1)
