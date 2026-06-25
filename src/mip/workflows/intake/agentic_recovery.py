"""Governed agentic workflow recovery helpers (P8b)."""

from __future__ import annotations

import re
import uuid
from collections.abc import Sequence
from datetime import UTC, datetime

from mip.contracts.agentic_workflow import (
    MAX_AGENT_RETRY_ATTEMPTS,
    AgentActionType,
    AgentAuthorityLevel,
    AgentCapability,
    AgentEscalationPolicy,
    AgentFailurePacket,
    AgentFailureSeverity,
    AgentHandoffPacket,
    AgentLifecycleStatus,
    AgentPermissionBoundary,
    AgentResolutionPlan,
    AgentRetryEligibility,
    AgentRetryPolicy,
    AgentRole,
    AgentRoleDefinition,
    AgentRunManifest,
    AgentRunStatus,
    AgentStepManifest,
    AgentTask,
    AgentValidationReport,
    AgentValidationStatus,
    AgentWorkflowType,
    default_forbidden_claim_topics,
)

_NOW = datetime(2026, 5, 28, 12, 0, tzinfo=UTC)


def _enum_value(value: object) -> str:
    if hasattr(value, "value"):
        return str(getattr(value, "value"))
    return str(value)


_UNSAFE_BLOCKED_ACTIONS: list[AgentActionType] = [
    AgentActionType.RETRY_SAME_STEP,
    AgentActionType.BLOCKED_ACTION,
]

_FORBIDDEN_OUTPUT_PATTERNS: list[tuple[str, str]] = [
    (r"\bhighest\s+roi\b", "roi"),
    (r"\broi\s+is\b", "roi"),
    (r"\bcausal\s+lift\b", "causal_lift"),
    (r"\blift\s+estimate\b", "causal_lift"),
    (r"\boptimal\s+mix\b", "optimal_mix"),
    (r"\bbudget\s+optim", "budget_optimization"),
    (r"\bpower\s+result\b", "power_mde"),
    (r"\bmde\s+result\b", "power_mde"),
    (r"\bmatched\s+markets?\b", "matched_markets"),
    (r"\btreatment\s+assignment\b", "treatment_control_assignment"),
    (r"\bcontrol\s+assignment\b", "treatment_control_assignment"),
    (r"\bdecision\s+approval\b", "decision_approval"),
    (r"\bmodel\s+promotion\b", "model_promotion"),
]

_FIRST_WAVE_ROLE_SPECS: list[dict[str, object]] = [
    {
        "role": AgentRole.INTAKE_ROUTING,
        "display_name": "Intake & Routing Agent",
        "status": AgentLifecycleStatus.AVAILABLE,
        "purpose": "Classify user requests and route to governed workflows.",
        "authority": AgentAuthorityLevel.EXPLAIN_ONLY,
        "workflows": [
            AgentWorkflowType.INTAKE,
            AgentWorkflowType.DATA_PROFILING,
            AgentWorkflowType.COLD_START_ADVISORY,
            AgentWorkflowType.MMM_READINESS,
            AgentWorkflowType.GEOX_READINESS,
            AgentWorkflowType.CALIBRATION_MAPPING,
            AgentWorkflowType.DECISION_REVIEW,
            AgentWorkflowType.LLM_EXPLANATION,
        ],
        "allowed_actions": [
            AgentActionType.ASK_USER_FOR_MISSING_DATA,
            AgentActionType.ROUTE_TO_ALTERNATIVE_WORKFLOW,
        ],
    },
    {
        "role": AgentRole.DATA_READINESS,
        "display_name": "Data Profiling / Data Readiness Agent",
        "status": AgentLifecycleStatus.AVAILABLE,
        "purpose": "Inspect governed summaries and assess structural workflow support.",
        "authority": AgentAuthorityLevel.DIAGNOSE_AND_RECOMMEND,
        "workflows": [AgentWorkflowType.DATA_PROFILING, AgentWorkflowType.INTAKE],
        "allowed_actions": [
            AgentActionType.ASK_USER_FOR_MISSING_DATA,
            AgentActionType.ASK_USER_TO_CONFIRM_MAPPING,
            AgentActionType.ROUTE_TO_ALTERNATIVE_WORKFLOW,
            AgentActionType.RERUN_READINESS,
        ],
    },
    {
        "role": AgentRole.COLD_START_ADVISORY,
        "display_name": "Cold-Start Advisory Agent",
        "status": AgentLifecycleStatus.AVAILABLE,
        "purpose": "Support pre-measurement advisory with labeled hypotheses only.",
        "authority": AgentAuthorityLevel.EXPLAIN_ONLY,
        "workflows": [AgentWorkflowType.COLD_START_ADVISORY],
        "allowed_actions": [
            AgentActionType.ASK_USER_FOR_MISSING_DATA,
            AgentActionType.ASK_USER_TO_CONFIRM_ASSUMPTION,
        ],
    },
    {
        "role": AgentRole.MMM_SPECIALIST,
        "display_name": "MMM Specialist Agent",
        "status": AgentLifecycleStatus.AVAILABLE,
        "purpose": "Explain MMM readiness, diagnostics context, and blocked paths.",
        "authority": AgentAuthorityLevel.DIAGNOSE_AND_RECOMMEND,
        "workflows": [AgentWorkflowType.MMM_READINESS, AgentWorkflowType.DECISION_REVIEW],
        "allowed_actions": [
            AgentActionType.ASK_USER_FOR_MISSING_DATA,
            AgentActionType.RERUN_READINESS,
            AgentActionType.ROUTE_TO_ALTERNATIVE_WORKFLOW,
        ],
    },
    {
        "role": AgentRole.GEOX_EXPERIMENT_SPECIALIST,
        "display_name": "GeoX / Experiment Specialist Agent",
        "status": AgentLifecycleStatus.AVAILABLE,
        "purpose": "Explain GeoX/experiment structural readiness and diagnostic prerequisites.",
        "authority": AgentAuthorityLevel.DIAGNOSE_AND_RECOMMEND,
        "workflows": [AgentWorkflowType.GEOX_READINESS, AgentWorkflowType.DECISION_REVIEW],
        "allowed_actions": [
            AgentActionType.ASK_USER_FOR_MISSING_DATA,
            AgentActionType.RERUN_READINESS,
            AgentActionType.ROUTE_TO_ALTERNATIVE_WORKFLOW,
        ],
    },
    {
        "role": AgentRole.CALIBRATION_SIGNAL_SPECIALIST,
        "display_name": "CalibrationSignal Specialist Agent",
        "status": AgentLifecycleStatus.AVAILABLE,
        "purpose": "Govern experiment evidence to CalibrationSignal mapping compatibility.",
        "authority": AgentAuthorityLevel.DIAGNOSE_AND_RECOMMEND,
        "workflows": [AgentWorkflowType.CALIBRATION_MAPPING],
        "allowed_actions": [
            AgentActionType.ASK_USER_FOR_MISSING_DATA,
            AgentActionType.ASK_USER_TO_CONFIRM_MAPPING,
            AgentActionType.RERUN_READINESS,
        ],
    },
    {
        "role": AgentRole.FAILURE_RECOVERY,
        "display_name": "Failure Recovery / Debugging Agent",
        "status": AgentLifecycleStatus.AVAILABLE,
        "purpose": "Diagnose failures and propose safe recovery plans without executing them.",
        "authority": AgentAuthorityLevel.DIAGNOSE_AND_RECOMMEND,
        "workflows": [AgentWorkflowType.FAILURE_RECOVERY],
        "allowed_actions": [
            AgentActionType.ASK_USER_FOR_MISSING_DATA,
            AgentActionType.ASK_USER_TO_CONFIRM_ASSUMPTION,
            AgentActionType.ROUTE_TO_ALTERNATIVE_WORKFLOW,
            AgentActionType.ESCALATE_TO_HUMAN,
            AgentActionType.CREATE_ISSUE_LATER,
        ],
    },
    {
        "role": AgentRole.EVALUATOR_VALIDATOR,
        "display_name": "Evaluator & Validator Agent",
        "status": AgentLifecycleStatus.AVAILABLE,
        "purpose": "Validate claim compliance before user-facing decision-supporting output.",
        "authority": AgentAuthorityLevel.VALIDATE_AND_BLOCK,
        "workflows": [AgentWorkflowType.VALIDATION, AgentWorkflowType.LLM_EXPLANATION],
        "allowed_actions": [
            AgentActionType.RERUN_VALIDATION,
            AgentActionType.ESCALATE_TO_HUMAN,
            AgentActionType.BLOCKED_ACTION,
        ],
    },
]

_DEFERRED_ROLE_SPECS: list[dict[str, object]] = [
    {
        "role": AgentRole.FEATURE_STORE_EXPLORER_DEFERRED,
        "display_name": "Feature Store Explorer Agent",
        "trigger": (
            "Production feature store integration (Feast, Tecton, "
            "Databricks Feature Store, or equivalent)."
        ),
    },
    {
        "role": AgentRole.ML_ENGINEERING_DEFERRED,
        "display_name": "ML Engineering / MLOps Specialist Agent",
        "trigger": (
            "Production schedulers, MLflow/model registry, Dockerized services, "
            "API deployment, or monitoring pipelines."
        ),
    },
    {
        "role": AgentRole.RESEARCH_SCOUT_DEFERRED,
        "display_name": "Research Scout Agent",
        "trigger": "Core product workflows stable and continuous method scouting is required.",
    },
    {
        "role": AgentRole.DATA_CONNECTOR_DEFERRED,
        "display_name": "Data Connector / Integration Agent",
        "trigger": "Production warehouse, GA4, or ads platform connectors are introduced.",
    },
    {
        "role": AgentRole.PRIVACY_SECURITY_DEFERRED,
        "display_name": "Privacy / Security Review Agent",
        "trigger": (
            "Before persistent uploads, public BYOK, platform-managed keys, "
            "or multi-user deployment."
        ),
    },
    {
        "role": AgentRole.PRODUCT_UX_GUIDE_DEFERRED,
        "display_name": "Product / UX Guide Agent",
        "trigger": "Hosted multi-workflow UI requires onboarding and mode guidance.",
    },
]


def _role_slug(role: AgentRole) -> str:
    return role.value.replace("_deferred", "")


def _build_permission_boundary(
    role: AgentRole,
    authority: AgentAuthorityLevel,
) -> AgentPermissionBoundary:
    return AgentPermissionBoundary(
        boundary_id=f"boundary-{_role_slug(role)}",
        agent_role=role,
        authority_level=authority,
        allowed_inputs=[
            "governed_profile_summary",
            "readiness_report",
            "advisory_plan",
            "calibration_mapping_report",
            "trust_report_summary",
            "agent_run_manifest",
            "agent_failure_packet",
        ],
        blocked_inputs=["raw_rows", "secrets", "api_credentials", "unvalidated_source_dump"],
        allowed_outputs=[
            "governed_explanation",
            "safe_next_steps",
            "blocked_next_steps",
            "user_questions",
            "validation_report",
        ],
        blocked_outputs=[
            "causal_effect_claim",
            "roi_claim",
            "budget_recommendation",
            "autonomous_execution_result",
        ],
        forbidden_claim_topics=list(default_forbidden_claim_topics()),
        requires_trust_report_for_decision_claims=True,
        requires_human_approval_for_execution=authority
        in {
            AgentAuthorityLevel.HUMAN_APPROVAL_REQUIRED,
            AgentAuthorityLevel.EXECUTE_SAFE_DETERMINISTIC_STEP_LATER,
        },
    )


def _build_role_definition(spec: dict[str, object]) -> AgentRoleDefinition:
    role = spec["role"]
    assert isinstance(role, AgentRole)
    authority = spec["authority"]
    assert isinstance(authority, AgentAuthorityLevel)
    workflows = spec.get("workflows", [])
    assert isinstance(workflows, list)
    allowed_actions = spec.get("allowed_actions", [])
    assert isinstance(allowed_actions, list)
    slug = _role_slug(role)
    capability = AgentCapability(
        capability_id=f"cap-{slug}",
        name=f"{spec['display_name']} capability",
        description=str(spec["purpose"]),
        allowed_workflow_types=list(workflows),
        allowed_actions=list(allowed_actions),
        blocked_actions=[AgentActionType.RETRY_SAME_STEP],
        requires_human_approval=authority == AgentAuthorityLevel.HUMAN_APPROVAL_REQUIRED,
    )
    status = spec.get("status", AgentLifecycleStatus.PLANNED)
    assert isinstance(status, AgentLifecycleStatus)
    return AgentRoleDefinition(
        role_id=f"role-{slug}",
        role=role,
        display_name=str(spec["display_name"]),
        status=status,
        purpose=str(spec["purpose"]),
        capabilities=[capability],
        permission_boundary=_build_permission_boundary(role, authority),
        deferred_trigger_conditions=[],
        created_at=_NOW,
    )


def build_first_wave_agent_role_definitions() -> list[AgentRoleDefinition]:
    """Return governed definitions for the first-wave specialist agents."""
    return [_build_role_definition(spec) for spec in _FIRST_WAVE_ROLE_SPECS]


def build_deferred_agent_role_definitions() -> list[AgentRoleDefinition]:
    """Return deferred agent role definitions with trigger conditions."""
    definitions: list[AgentRoleDefinition] = []
    for spec in _DEFERRED_ROLE_SPECS:
        role = spec["role"]
        assert isinstance(role, AgentRole)
        slug = _role_slug(role)
        trigger = str(spec["trigger"])
        definitions.append(
            AgentRoleDefinition(
                role_id=f"role-{slug}",
                role=role,
                display_name=str(spec["display_name"]),
                status=AgentLifecycleStatus.DEFERRED,
                purpose=f"Deferred optional agent: {spec['display_name']}.",
                capabilities=[],
                permission_boundary=_build_permission_boundary(
                    role,
                    AgentAuthorityLevel.EXPLAIN_ONLY,
                ),
                deferred_trigger_conditions=[trigger],
                warnings=["deferred_agent_not_available_in_p8b"],
                created_at=_NOW,
            )
        )
    return definitions


def _default_blocked_actions() -> list[AgentActionType]:
    return [
        AgentActionType.RETRY_SAME_STEP,
        AgentActionType.BLOCKED_ACTION,
    ]


def build_agent_task(
    role: AgentRole,
    workflow_type: AgentWorkflowType,
    user_request_summary: str,
    input_reference_ids: Sequence[str] | None = None,
) -> AgentTask:
    """Create a controlled agent task with role-based default actions."""
    role_defs = {
        definition.role: definition for definition in build_first_wave_agent_role_definitions()
    }
    definition = role_defs.get(role)
    allowed: list[AgentActionType] = []
    blocked = _default_blocked_actions()
    requires_approval = False
    if definition and definition.capabilities:
        capability = definition.capabilities[0]
        allowed = list(capability.allowed_actions)
        blocked = list({*blocked, *capability.blocked_actions})
        requires_approval = capability.requires_human_approval
    return AgentTask(
        task_id=f"task-{uuid.uuid4().hex[:12]}",
        role=role,
        workflow_type=workflow_type,
        user_request_summary=user_request_summary,
        input_reference_ids=list(input_reference_ids or []),
        allowed_actions=allowed,
        blocked_actions=blocked,
        requires_human_approval=requires_approval,
        created_at=_NOW,
    )


def build_agent_run_manifest(
    task: AgentTask,
    status: AgentRunStatus = AgentRunStatus.NOT_STARTED,
) -> AgentRunManifest:
    """Create a run manifest shell without executing any workflow."""
    step = AgentStepManifest(
        step_id=f"step-{uuid.uuid4().hex[:8]}",
        task_id=task.task_id,
        workflow_type=task.workflow_type,
        step_name=f"{_enum_value(task.workflow_type)}_planning",
        status=status,
        input_reference_ids=list(task.input_reference_ids),
    )
    return AgentRunManifest(
        run_id=f"run-{uuid.uuid4().hex[:12]}",
        task_id=task.task_id,
        role=task.role,
        workflow_type=task.workflow_type,
        status=status,
        steps=[step],
        input_reference_ids=list(task.input_reference_ids),
        package_metadata={"phase": "p8b_contract_only"},
        started_at=_NOW if status != AgentRunStatus.NOT_STARTED else None,
    )


def build_agent_failure_packet(
    run_manifest: AgentRunManifest,
    step_id: str | None,
    error_type: str,
    error_message: str,
    severity: AgentFailureSeverity = AgentFailureSeverity.BLOCKING,
    stack_trace: str | None = None,
    typed_validation_failures: Sequence[str] | None = None,
) -> AgentFailurePacket:
    """Create a structured failure packet with safe default retry action hints."""
    normalized_type = error_type.strip().lower()
    allowed_retry: list[AgentActionType] = [
        AgentActionType.ASK_USER_FOR_MISSING_DATA,
        AgentActionType.ROUTE_TO_ALTERNATIVE_WORKFLOW,
        AgentActionType.ESCALATE_TO_HUMAN,
    ]
    blocked_retry: list[AgentActionType] = [
        AgentActionType.RETRY_SAME_STEP,
        AgentActionType.BLOCKED_ACTION,
    ]
    if "roi" in normalized_type or "forbidden" in normalized_type:
        allowed_retry = [AgentActionType.RERUN_VALIDATION, AgentActionType.ESCALATE_TO_HUMAN]
    return AgentFailurePacket(
        failure_id=f"fail-{uuid.uuid4().hex[:12]}",
        run_id=run_manifest.run_id,
        task_id=run_manifest.task_id,
        step_id=step_id or (run_manifest.steps[0].step_id if run_manifest.steps else None),
        role=run_manifest.role,
        workflow_type=run_manifest.workflow_type,
        severity=severity,
        error_type=error_type,
        error_message=error_message,
        stack_trace=stack_trace,
        typed_validation_failures=list(typed_validation_failures or []),
        safe_context=f"workflow={_enum_value(run_manifest.workflow_type)}; error_type={error_type}",
        allowed_retry_actions=allowed_retry,
        blocked_retry_actions=blocked_retry,
        affected_artifact_ids=list(run_manifest.artifact_reference_ids),
        created_at=_NOW,
    )


def _failure_tokens(failure_packet: AgentFailurePacket) -> set[str]:
    tokens = {
        failure_packet.error_type.lower(),
        failure_packet.error_message.lower(),
        *(value.lower() for value in failure_packet.typed_validation_failures),
    }
    return tokens


def _tokens_match(tokens: set[str], *needles: str) -> bool:
    return any(needle in token for token in tokens for needle in needles)


def build_agent_resolution_plan(
    failure_packet: AgentFailurePacket,
) -> AgentResolutionPlan:
    """Build a deterministic safe recovery plan from a failure packet."""
    tokens = _failure_tokens(failure_packet)
    questions: list[str] = []
    safe_steps: list[str] = []
    blocked_steps: list[str] = []
    retry = AgentRetryEligibility.NOT_RETRYABLE
    requires_approval = False
    diagnosis = "Unknown failure; escalate for human review."
    impact = "Downstream workflow remains blocked until resolved."

    if _tokens_match(tokens, "missing_geo", "geo_missing", "no_geo", "missing geo"):
        diagnosis = "Geo coverage missing for GeoX/experiment design path."
        questions = [
            "Which column contains geo identifiers (DMA, state, region, or market)?",
            "Is an existing market/region column intended to represent geo?",
        ]
        safe_steps = [
            "ask_for_geo_column",
            "confirm_market_column_as_geo",
            "route_to_national_mmm_or_advisory_path",
        ]
        blocked_steps = [
            "invent_geo_mapping",
            "proceed_with_geox_design",
            "estimate_lift",
        ]
        retry = AgentRetryEligibility.RETRY_AFTER_USER_INPUT
    elif _tokens_match(
        tokens,
        "missing_uncertainty",
        "standard_error_missing",
        "missing standard_error",
        "no_uncertainty",
    ):
        diagnosis = "Calibration evidence missing uncertainty fields."
        questions = [
            "Please provide standard_error or supported confidence interval bounds.",
        ]
        safe_steps = ["ask_for_standard_error_or_ci", "keep_calibration_mapping_blocked"]
        blocked_steps = [
            "infer_se_from_point_estimate",
            "certify_evidence_as_causal",
            "execute_mmm_calibration",
        ]
        retry = AgentRetryEligibility.RETRY_AFTER_USER_INPUT
    elif _tokens_match(tokens, "missing_spend", "missing_weeks", "spend_gap", "missing spend"):
        diagnosis = "Media spend coverage incomplete for MMM readiness."
        questions = [
            "Can you provide missing spend for the affected weeks/channels?",
            "Should true zero spend be recorded explicitly for missing weeks?",
        ]
        safe_steps = [
            "ask_for_corrected_spend",
            "confirm_true_zero_spend",
            "exclude_channel_with_warning_if_policy_allows",
        ]
        blocked_steps = [
            "silently_impute_spend",
            "continue_without_recording_assumption",
            "claim_roi_or_budget_outcome",
        ]
        retry = AgentRetryEligibility.RETRY_AFTER_USER_INPUT
        impact = "MMM diagnostics and ROI/budget claims remain blocked until spend is governed."
    elif _tokens_match(tokens, "forbidden_claim", "roi_claim", "roi", "highest roi"):
        diagnosis = "Forbidden ROI or decision claim detected in proposed output."
        questions = []
        safe_steps = [
            "block_or_rewrite_explanation",
            "preserve_advisory_causal_decision_labels",
        ]
        blocked_steps = ["deliver_forbidden_roi_claim", "approve_decision"]
        retry = AgentRetryEligibility.NOT_RETRYABLE
        requires_approval = True
    else:
        safe_steps = ["escalate_to_human"]
        blocked_steps = ["automatic_retry", "bypass_gates"]
        retry = AgentRetryEligibility.NOT_RETRYABLE
        requires_approval = True

    return AgentResolutionPlan(
        resolution_plan_id=f"resolve-{uuid.uuid4().hex[:12]}",
        failure_id=failure_packet.failure_id,
        diagnosis=diagnosis,
        recommended_user_questions=questions,
        safe_next_steps=safe_steps,
        blocked_next_steps=blocked_steps,
        retry_eligibility=retry,
        requires_human_approval=requires_approval,
        expected_downstream_impact=impact,
        warnings=["resolution_plan_does_not_execute_recovery"],
        created_at=_NOW,
    )


def _detect_forbidden_claims(text: str | None) -> list[str]:
    if not text or not text.strip():
        return []
    lowered = text.lower()
    findings: list[str] = []
    for pattern, topic in _FORBIDDEN_OUTPUT_PATTERNS:
        if re.search(pattern, lowered):
            findings.append(topic)
    return sorted(set(findings))


def build_agent_validation_report(
    task: AgentTask,
    run_manifest: AgentRunManifest | None = None,
    proposed_output_summary: str | None = None,
) -> AgentValidationReport:
    """Validate proposed output for forbidden claims without LLM calls."""
    forbidden = _detect_forbidden_claims(proposed_output_summary)
    status = AgentValidationStatus.PASSED
    blocked_outputs: list[str] = []
    allowed_outputs: list[str] = ["governed_explanation"]
    findings: list[str] = []
    missing_labels: list[str] = []

    if forbidden:
        status = AgentValidationStatus.BLOCKED
        findings = [f"forbidden_claim_topic:{topic}" for topic in forbidden]
        blocked_outputs = ["decision_supporting_explanation", *forbidden]
        allowed_outputs = ["blocked_claim_explanation", "safe_next_steps"]
    elif proposed_output_summary:
        if "evidence" not in proposed_output_summary.lower():
            missing_labels.append("evidence_label")
            status = AgentValidationStatus.WARNING
        allowed_outputs = ["readiness_explanation", "governed_summary"]

    if (
        task.workflow_type
        in {
            AgentWorkflowType.MMM_READINESS,
            AgentWorkflowType.GEOX_READINESS,
            AgentWorkflowType.CALIBRATION_MAPPING,
        }
        and status == AgentValidationStatus.PASSED
    ):
        missing_labels.append("trust_report_not_verified_in_p8b")

    return AgentValidationReport(
        validation_report_id=f"val-{uuid.uuid4().hex[:12]}",
        task_id=task.task_id,
        run_id=run_manifest.run_id if run_manifest else None,
        role=AgentRole.EVALUATOR_VALIDATOR,
        validation_status=status,
        claim_compliance_findings=findings,
        forbidden_claim_findings=forbidden,
        missing_evidence_labels=missing_labels,
        trust_report_requirement_status="required_for_decision_claims",
        readiness_consistency_status="not_checked_in_p8b",
        calibration_consistency_status="not_checked_in_p8b",
        final_allowed_outputs=allowed_outputs,
        final_blocked_outputs=blocked_outputs,
        warnings=["validator_does_not_invent_results"],
        created_at=_NOW,
    )


def build_agent_handoff_packet(
    from_role: AgentRole,
    to_role: AgentRole,
    task: AgentTask,
    reason: str,
    summary: str,
) -> AgentHandoffPacket:
    """Create a controlled inter-agent handoff preserving action boundaries."""
    return AgentHandoffPacket(
        handoff_id=f"handoff-{uuid.uuid4().hex[:12]}",
        from_role=from_role,
        to_role=to_role,
        task_id=task.task_id,
        reason=reason,
        summary=summary,
        input_reference_ids=list(task.input_reference_ids),
        allowed_actions=list(task.allowed_actions),
        blocked_actions=list(task.blocked_actions),
        warnings=["handoff_does_not_execute_workflow"],
        created_at=_NOW,
    )


def build_default_agent_retry_policy(
    workflow_type: AgentWorkflowType,
) -> AgentRetryPolicy:
    """Return a conservative retry policy for a workflow type."""
    return AgentRetryPolicy(
        retry_policy_id=f"retry-{_enum_value(workflow_type)}",
        workflow_type=workflow_type,
        retry_eligibility=AgentRetryEligibility.RETRY_AFTER_USER_INPUT,
        max_retry_attempts=MAX_AGENT_RETRY_ATTEMPTS,
        allowed_retry_actions=[
            AgentActionType.ASK_USER_FOR_MISSING_DATA,
            AgentActionType.RERUN_READINESS,
            AgentActionType.RERUN_VALIDATION,
        ],
        blocked_retry_actions=[
            AgentActionType.RETRY_SAME_STEP,
            AgentActionType.BLOCKED_ACTION,
        ],
        requires_user_confirmation=True,
        requires_human_approval=False,
        warnings=["no_infinite_retries"],
    )


def build_default_agent_escalation_policy(
    workflow_type: AgentWorkflowType,
) -> AgentEscalationPolicy:
    """Return default escalation policy for unknown or critical failures."""
    return AgentEscalationPolicy(
        escalation_policy_id=f"escalate-{_enum_value(workflow_type)}",
        workflow_type=workflow_type,
        trigger_conditions=["unknown_failure", "critical_severity", "repeated_blocked_validation"],
        escalation_target="human_reviewer",
        requires_human_approval=True,
        blocked_until_resolved=True,
        warnings=["escalation_does_not_execute_recovery"],
    )
