"""Tests for P8b agentic recovery helpers."""

from mip.contracts.agentic_workflow import (
    MAX_AGENT_RETRY_ATTEMPTS,
    AgentActionType,
    AgentAuthorityLevel,
    AgentFailureSeverity,
    AgentRetryEligibility,
    AgentRole,
    AgentRunStatus,
    AgentValidationStatus,
    AgentWorkflowType,
    default_forbidden_claim_topics,
)
from mip.workflows.intake.agentic_recovery import (
    build_agent_failure_packet,
    build_agent_handoff_packet,
    build_agent_resolution_plan,
    build_agent_run_manifest,
    build_agent_task,
    build_agent_validation_report,
    build_default_agent_escalation_policy,
    build_default_agent_retry_policy,
    build_deferred_agent_role_definitions,
    build_first_wave_agent_role_definitions,
)

_FIRST_WAVE_ROLES = {
    AgentRole.INTAKE_ROUTING,
    AgentRole.DATA_READINESS,
    AgentRole.COLD_START_ADVISORY,
    AgentRole.MMM_SPECIALIST,
    AgentRole.GEOX_EXPERIMENT_SPECIALIST,
    AgentRole.CALIBRATION_SIGNAL_SPECIALIST,
    AgentRole.FAILURE_RECOVERY,
    AgentRole.EVALUATOR_VALIDATOR,
}

_DEFERRED_ROLES = {
    AgentRole.FEATURE_STORE_EXPLORER_DEFERRED,
    AgentRole.ML_ENGINEERING_DEFERRED,
    AgentRole.RESEARCH_SCOUT_DEFERRED,
    AgentRole.DATA_CONNECTOR_DEFERRED,
    AgentRole.PRIVACY_SECURITY_DEFERRED,
    AgentRole.PRODUCT_UX_GUIDE_DEFERRED,
}


def test_first_wave_role_definitions_include_required_agents() -> None:
    definitions = build_first_wave_agent_role_definitions()
    roles = {definition.role for definition in definitions}
    assert _FIRST_WAVE_ROLES.issubset(roles)
    assert len(definitions) == 8


def test_first_wave_agents_do_not_own_execution_or_measurement_authority() -> None:
    for definition in build_first_wave_agent_role_definitions():
        assert definition.owns_execution is False
        assert definition.authoritative_for_measurement is False


def test_evaluator_validator_has_validate_and_block_authority() -> None:
    evaluator = next(
        d
        for d in build_first_wave_agent_role_definitions()
        if d.role == AgentRole.EVALUATOR_VALIDATOR
    )
    assert evaluator.permission_boundary.authority_level == AgentAuthorityLevel.VALIDATE_AND_BLOCK


def test_failure_recovery_has_diagnose_and_recommend_authority() -> None:
    recovery = next(
        d for d in build_first_wave_agent_role_definitions() if d.role == AgentRole.FAILURE_RECOVERY
    )
    assert (
        recovery.permission_boundary.authority_level == AgentAuthorityLevel.DIAGNOSE_AND_RECOMMEND
    )
    assert AgentActionType.ESCALATE_TO_HUMAN in recovery.capabilities[0].allowed_actions


def test_deferred_roles_include_all_six_optional_agents() -> None:
    definitions = build_deferred_agent_role_definitions()
    roles = {definition.role for definition in definitions}
    assert roles == _DEFERRED_ROLES
    for definition in definitions:
        assert definition.deferred_trigger_conditions
        assert str(definition.status) == "deferred"


def test_permission_boundaries_include_forbidden_claim_topics() -> None:
    topics = set(default_forbidden_claim_topics())
    for definition in build_first_wave_agent_role_definitions():
        boundary_topics = set(definition.permission_boundary.forbidden_claim_topics)
        assert topics.issubset(boundary_topics)


def test_agent_task_defaults_block_unsafe_actions() -> None:
    task = build_agent_task(
        AgentRole.MMM_SPECIALIST,
        AgentWorkflowType.MMM_READINESS,
        "Assess national MMM readiness",
    )
    assert AgentActionType.RETRY_SAME_STEP in task.blocked_actions
    assert task.allowed_actions


def test_agent_run_manifest_stores_task_role_workflow_status() -> None:
    task = build_agent_task(
        AgentRole.DATA_READINESS,
        AgentWorkflowType.DATA_PROFILING,
        "Profile demo dataset",
        input_reference_ids=["profile-001"],
    )
    manifest = build_agent_run_manifest(task, status=AgentRunStatus.RUNNING)
    assert manifest.task_id == task.task_id
    assert manifest.role == AgentRole.DATA_READINESS
    assert manifest.workflow_type == AgentWorkflowType.DATA_PROFILING
    assert manifest.status == AgentRunStatus.RUNNING
    assert manifest.steps


def test_agent_failure_packet_stores_error_and_optional_stack_trace() -> None:
    task = build_agent_task(
        AgentRole.GEOX_EXPERIMENT_SPECIALIST,
        AgentWorkflowType.GEOX_READINESS,
        "Check geo coverage",
    )
    manifest = build_agent_run_manifest(task)
    packet = build_agent_failure_packet(
        manifest,
        step_id=manifest.steps[0].step_id,
        error_type="missing_geo",
        error_message="No DMA/state/geo column detected",
        stack_trace="Traceback (most recent call last): ...",
        typed_validation_failures=["geo_column_missing"],
    )
    assert packet.error_type == "missing_geo"
    assert packet.stack_trace is not None
    assert "raw_rows" not in packet.model_dump()


def test_missing_geo_failure_produces_safe_resolution_plan() -> None:
    task = build_agent_task(
        AgentRole.DATA_READINESS,
        AgentWorkflowType.GEOX_READINESS,
        "GeoX design readiness",
    )
    manifest = build_agent_run_manifest(task)
    packet = build_agent_failure_packet(
        manifest,
        manifest.steps[0].step_id,
        "missing_geo",
        "Geo column not found",
    )
    plan = build_agent_resolution_plan(packet)
    assert "geo" in plan.diagnosis.lower()
    assert plan.recommended_user_questions
    assert "invent_geo_mapping" in plan.blocked_next_steps
    assert plan.retry_eligibility == AgentRetryEligibility.RETRY_AFTER_USER_INPUT


def test_missing_uncertainty_failure_blocks_se_inference() -> None:
    task = build_agent_task(
        AgentRole.CALIBRATION_SIGNAL_SPECIALIST,
        AgentWorkflowType.CALIBRATION_MAPPING,
        "Map experiment readout",
    )
    manifest = build_agent_run_manifest(task)
    packet = build_agent_failure_packet(
        manifest,
        manifest.steps[0].step_id,
        "standard_error_missing",
        "Effect estimate present without uncertainty",
        typed_validation_failures=["missing_uncertainty"],
    )
    plan = build_agent_resolution_plan(packet)
    assert "infer_se_from_point_estimate" in plan.blocked_next_steps
    assert "execute_mmm_calibration" in plan.blocked_next_steps


def test_missing_spend_failure_blocks_silent_imputation() -> None:
    task = build_agent_task(
        AgentRole.MMM_SPECIALIST,
        AgentWorkflowType.MMM_READINESS,
        "Check media spend coverage",
    )
    manifest = build_agent_run_manifest(task)
    packet = build_agent_failure_packet(
        manifest,
        manifest.steps[0].step_id,
        "missing_spend_weeks",
        "Meta spend missing for 3 weeks",
    )
    plan = build_agent_resolution_plan(packet)
    assert "silently_impute_spend" in plan.blocked_next_steps


def test_forbidden_roi_claim_failure_blocks_rewrite_path() -> None:
    task = build_agent_task(
        AgentRole.EVALUATOR_VALIDATOR,
        AgentWorkflowType.VALIDATION,
        "Validate explanation",
    )
    manifest = build_agent_run_manifest(task)
    packet = build_agent_failure_packet(
        manifest,
        manifest.steps[0].step_id,
        "roi_claim",
        "Forbidden ROI claim in proposed output",
        severity=AgentFailureSeverity.CRITICAL,
    )
    plan = build_agent_resolution_plan(packet)
    assert "block_or_rewrite_explanation" in plan.safe_next_steps
    assert plan.requires_human_approval is True


def test_unknown_failure_escalates_without_automatic_retry() -> None:
    task = build_agent_task(
        AgentRole.FAILURE_RECOVERY,
        AgentWorkflowType.FAILURE_RECOVERY,
        "Diagnose unknown error",
    )
    manifest = build_agent_run_manifest(task)
    packet = build_agent_failure_packet(
        manifest,
        manifest.steps[0].step_id,
        "unexpected_internal_state",
        "Unhandled validator state",
    )
    plan = build_agent_resolution_plan(packet)
    assert "escalate_to_human" in plan.safe_next_steps
    assert "automatic_retry" in plan.blocked_next_steps
    assert plan.retry_eligibility == AgentRetryEligibility.NOT_RETRYABLE


def test_agent_validation_report_blocks_roi_claim() -> None:
    task = build_agent_task(
        AgentRole.EVALUATOR_VALIDATOR,
        AgentWorkflowType.LLM_EXPLANATION,
        "Validate LLM explanation plan",
    )
    report = build_agent_validation_report(
        task,
        proposed_output_summary="Meta is the highest ROI channel for this brand.",
    )
    assert report.validation_status == AgentValidationStatus.BLOCKED
    assert "roi" in report.forbidden_claim_findings
    assert "decision_supporting_explanation" in report.final_blocked_outputs


def test_agent_validation_report_blocks_matched_market_assignment() -> None:
    task = build_agent_task(
        AgentRole.EVALUATOR_VALIDATOR,
        AgentWorkflowType.VALIDATION,
        "Validate GeoX explanation",
    )
    report = build_agent_validation_report(
        task,
        proposed_output_summary="Assign treatment markets using matched markets selection.",
    )
    assert report.validation_status == AgentValidationStatus.BLOCKED
    assert "matched_markets" in report.forbidden_claim_findings


def test_agent_validation_report_passes_neutral_readiness_explanation() -> None:
    task = build_agent_task(
        AgentRole.MMM_SPECIALIST,
        AgentWorkflowType.MMM_READINESS,
        "Explain readiness",
    )
    summary = (
        "National MMM readiness is structurally supported with evidence labels attached."
    )
    report = build_agent_validation_report(task, proposed_output_summary=summary)
    assert report.validation_status in {
        AgentValidationStatus.PASSED,
        AgentValidationStatus.WARNING,
    }
    assert not report.forbidden_claim_findings


def test_agent_retry_policy_disallows_infinite_retries() -> None:
    policy = build_default_agent_retry_policy(AgentWorkflowType.MMM_READINESS)
    assert policy.max_retry_attempts <= MAX_AGENT_RETRY_ATTEMPTS
    assert AgentActionType.RETRY_SAME_STEP in policy.blocked_retry_actions


def test_agent_handoff_packet_preserves_allowed_blocked_actions() -> None:
    task = build_agent_task(
        AgentRole.INTAKE_ROUTING,
        AgentWorkflowType.INTAKE,
        "Route user request",
    )
    handoff = build_agent_handoff_packet(
        AgentRole.INTAKE_ROUTING,
        AgentRole.DATA_READINESS,
        task,
        reason="needs_profiling",
        summary="Route to data readiness after intake classification",
    )
    assert handoff.allowed_actions == task.allowed_actions
    assert handoff.blocked_actions == task.blocked_actions


def test_default_escalation_policy_requires_human_approval() -> None:
    policy = build_default_agent_escalation_policy(AgentWorkflowType.FAILURE_RECOVERY)
    assert policy.requires_human_approval is True
    assert policy.blocked_until_resolved is True
