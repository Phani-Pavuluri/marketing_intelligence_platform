"""Tests for MMM artifact governance and use-readiness contracts."""

from __future__ import annotations

from mip.contracts import (
    FORBIDDEN_MMM_ARTIFACT_GOVERNANCE_USE_READINESS_RESULT_FIELD_NAMES,
    RECOMMENDED_NEXT_MMM_RUNTIME_ORCHESTRATION_LANE_COMPLETION_AUDIT_ARTIFACT,
    MMMArtifactGovernanceRoute,
    MMMArtifactGovernanceRouteDecision,
    MMMArtifactGovernanceUseReadinessIssueCode,
    MMMArtifactGovernanceUseReadinessRequest,
    MMMArtifactGovernanceUseReadinessResult,
    MMMArtifactGovernanceUseReadinessStatus,
    MMMArtifactUseReadiness,
)

_FORBIDDEN_TOP_LEVEL = (
    "spend_delta",
    "delta_mu",
    "roi",
    "roas",
    "incrementality",
    "optimal_budget",
    "marginal_roi",
    "recommendation",
    "budget_recommendation",
)


def test_required_enums_exist() -> None:
    assert (
        MMMArtifactGovernanceUseReadinessStatus.READY_FOR_GOVERNANCE_REVIEW
        in MMMArtifactGovernanceUseReadinessStatus
    )
    assert MMMArtifactGovernanceRoute.TRUST_REPORT_REVIEW in MMMArtifactGovernanceRoute
    assert MMMArtifactUseReadiness.PLANNING_READY in MMMArtifactUseReadiness
    assert MMMArtifactGovernanceUseReadinessIssueCode.NO_TRUST_REPORT_CONSTRUCTION in (
        MMMArtifactGovernanceUseReadinessIssueCode
    )


def test_request_and_result_models_serialize() -> None:
    request = MMMArtifactGovernanceUseReadinessRequest(request_id="gov-req-1")
    assert request.require_model_artifact is False
    assert request.require_model_artifact_uri is True
    assert request.require_manifest_uri is True
    assert request.allow_trust_report_route is True
    result = MMMArtifactGovernanceUseReadinessResult(
        request_id="gov-req-1",
        status=MMMArtifactGovernanceUseReadinessStatus.BLOCKED,
        use_readiness=MMMArtifactUseReadiness.BLOCKED,
    )
    assert result.planning_ready is False


def test_route_decisions_serialize() -> None:
    decision = MMMArtifactGovernanceRouteDecision(
        route=MMMArtifactGovernanceRoute.TRUST_REPORT_REVIEW,
        enabled=True,
        reason="ready",
        candidate_reference="trust_report:candidate:ext-1",
    )
    assert decision.enabled is True
    assert decision.candidate_reference is not None


def test_no_forbidden_top_level_fields() -> None:
    for field_name in MMMArtifactGovernanceUseReadinessResult.model_fields:
        assert field_name not in _FORBIDDEN_TOP_LEVEL
    assert "roi" in FORBIDDEN_MMM_ARTIFACT_GOVERNANCE_USE_READINESS_RESULT_FIELD_NAMES


def test_exports_from_mip_contracts() -> None:
    assert RECOMMENDED_NEXT_MMM_RUNTIME_ORCHESTRATION_LANE_COMPLETION_AUDIT_ARTIFACT == (
        "MIP_MMM_RUNTIME_ORCHESTRATION_LANE_COMPLETION_AUDIT_001"
    )


def test_no_duplicate_promotion_system_fields() -> None:
    fields = set(MMMArtifactGovernanceUseReadinessResult.model_fields)
    assert "promotion_status" not in fields
    assert "allowed_uses" not in fields
    assert "diagnostic_status" not in fields
