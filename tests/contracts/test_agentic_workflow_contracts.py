"""Tests for P8b agentic workflow contracts."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from mip.contracts.agentic_workflow import (
    MAX_AGENT_RETRY_ATTEMPTS,
    AgentAuthorityLevel,
    AgentCapability,
    AgentEscalationPolicy,
    AgentFailurePacket,
    AgentHandoffPacket,
    AgentLifecycleStatus,
    AgentPermissionBoundary,
    AgentResolutionPlan,
    AgentRetryPolicy,
    AgentRole,
    AgentRoleDefinition,
    AgentRunManifest,
    AgentStepManifest,
    AgentTask,
    AgentValidationReport,
    AgentWorkflowType,
    default_forbidden_claim_topics,
)

_NOW = datetime(2026, 5, 28, 12, 0, tzinfo=UTC)

_ALL_CONTRACT_MODELS = (
    AgentCapability,
    AgentPermissionBoundary,
    AgentRoleDefinition,
    AgentTask,
    AgentStepManifest,
    AgentRunManifest,
    AgentFailurePacket,
    AgentResolutionPlan,
    AgentValidationReport,
    AgentHandoffPacket,
    AgentRetryPolicy,
    AgentEscalationPolicy,
)

_FORBIDDEN_FIELD_NAMES = (
    "api_key",
    "secret",
    "raw_rows",
    "generated_answer",
    "final_response",
    "autonomous_execution_result",
)


def _permission_boundary(role: AgentRole = AgentRole.INTAKE_ROUTING) -> AgentPermissionBoundary:
    return AgentPermissionBoundary(
        boundary_id="boundary-test",
        agent_role=role,
        authority_level=AgentAuthorityLevel.EXPLAIN_ONLY,
    )


def test_default_forbidden_claim_topics_include_roi_and_matched_markets() -> None:
    topics = default_forbidden_claim_topics()
    assert "roi" in topics
    assert "matched_markets" in topics
    assert "budget_optimization" in topics


def test_agent_role_definition_rejects_execution_ownership() -> None:
    with pytest.raises(ValidationError, match="must not own execution"):
        AgentRoleDefinition(
            role_id="role-bad",
            role=AgentRole.MMM_SPECIALIST,
            display_name="Bad",
            purpose="Test",
            permission_boundary=_permission_boundary(AgentRole.MMM_SPECIALIST),
            owns_execution=True,
            created_at=_NOW,
        )


def test_agent_role_definition_deferred_requires_trigger_conditions() -> None:
    with pytest.raises(ValidationError, match="deferred_trigger_conditions"):
        AgentRoleDefinition(
            role_id="role-deferred-bad",
            role=AgentRole.FEATURE_STORE_EXPLORER_DEFERRED,
            display_name="Deferred",
            status=AgentLifecycleStatus.DEFERRED,
            purpose="Deferred agent",
            permission_boundary=_permission_boundary(AgentRole.FEATURE_STORE_EXPLORER_DEFERRED),
            deferred_trigger_conditions=[],
            created_at=_NOW,
        )


def test_agent_run_manifest_rejects_raw_rows_in_package_metadata() -> None:
    with pytest.raises(ValidationError, match="raw_rows"):
        AgentRunManifest(
            run_id="run-1",
            task_id="task-1",
            role=AgentRole.DATA_READINESS,
            workflow_type=AgentWorkflowType.DATA_PROFILING,
            package_metadata={"raw_rows": "forbidden"},
        )


def test_agent_retry_policy_caps_max_attempts() -> None:
    with pytest.raises(ValidationError, match="max_retry_attempts cannot exceed"):
        AgentRetryPolicy(
            retry_policy_id="retry-bad",
            workflow_type=AgentWorkflowType.MMM_READINESS,
            max_retry_attempts=MAX_AGENT_RETRY_ATTEMPTS + 1,
        )


def test_contract_models_do_not_expose_forbidden_field_names() -> None:
    for model in _ALL_CONTRACT_MODELS:
        for field_name in _FORBIDDEN_FIELD_NAMES:
            assert field_name not in model.model_fields


def test_agent_failure_packet_rejects_forbidden_claim_in_message() -> None:
    with pytest.raises(ValidationError, match="forbidden claim"):
        AgentFailurePacket(
            failure_id="fail-1",
            run_id="run-1",
            task_id="task-1",
            role=AgentRole.FAILURE_RECOVERY,
            workflow_type=AgentWorkflowType.FAILURE_RECOVERY,
            error_type="validation",
            error_message="ROI is proven for this channel",
            created_at=_NOW,
        )
