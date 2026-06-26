"""Deterministic agent answerability evaluator (no LLM)."""

from __future__ import annotations

from uuid import uuid4

from mip.contracts.agent_answerability import (
    AgentAnswerabilityDecision,
    AgentAnswerabilityRequest,
    AgentAnswerabilityState,
    AgentAnswerMode,
    AnswerabilityEvidenceLevel,
    AvailableReportSummary,
    RequestedClaimType,
    RoutingConfidence,
    ToolAvailabilityStatus,
)
from mip.contracts.deterministic_report import ReportType

_CLAIM_TO_REQUIRED_EVIDENCE: dict[RequestedClaimType, AnswerabilityEvidenceLevel] = {
    RequestedClaimType.GENERAL_MARKETING_ADVICE: AnswerabilityEvidenceLevel.BUSINESS_PROFILE_ONLY,
    RequestedClaimType.TRACKING_OR_DATA_READINESS: (
        AnswerabilityEvidenceLevel.DETERMINISTIC_WORKFLOW_REPORT
    ),
    RequestedClaimType.COLD_START_ADVISORY: AnswerabilityEvidenceLevel.BUSINESS_PROFILE_ONLY,
    RequestedClaimType.MEASUREMENT_READINESS: AnswerabilityEvidenceLevel.DIAGNOSTIC_ONLY,
    RequestedClaimType.EXPERIMENT_CALIBRATION: AnswerabilityEvidenceLevel.CALIBRATION_CANDIDATE,
    RequestedClaimType.CAUSAL_LIFT: AnswerabilityEvidenceLevel.CORE_GEOX_REQUIRED,
    RequestedClaimType.ROI: AnswerabilityEvidenceLevel.CORE_MMM_REQUIRED,
    RequestedClaimType.BUDGET_OPTIMIZATION: (
        AnswerabilityEvidenceLevel.CERTIFIED_DECISION_SURFACE_REQUIRED
    ),
    RequestedClaimType.SCENARIO_PLANNING: (
        AnswerabilityEvidenceLevel.CERTIFIED_DECISION_SURFACE_REQUIRED
    ),
    RequestedClaimType.RESPONSE_CURVE: AnswerabilityEvidenceLevel.CORE_MMM_REQUIRED,
    RequestedClaimType.MATCHED_MARKET_DESIGN: AnswerabilityEvidenceLevel.CORE_GEOX_REQUIRED,
    RequestedClaimType.POWER_MDE: AnswerabilityEvidenceLevel.CORE_GEOX_REQUIRED,
    RequestedClaimType.TREATMENT_ASSIGNMENT: AnswerabilityEvidenceLevel.CORE_GEOX_REQUIRED,
    RequestedClaimType.PRODUCTION_RECOMMENDATION: (
        AnswerabilityEvidenceLevel.CERTIFIED_DECISION_SURFACE_REQUIRED
    ),
}

_CORE_ML_CLAIMS = frozenset(
    {
        RequestedClaimType.CAUSAL_LIFT,
        RequestedClaimType.ROI,
        RequestedClaimType.BUDGET_OPTIMIZATION,
        RequestedClaimType.SCENARIO_PLANNING,
        RequestedClaimType.RESPONSE_CURVE,
        RequestedClaimType.MATCHED_MARKET_DESIGN,
        RequestedClaimType.POWER_MDE,
        RequestedClaimType.TREATMENT_ASSIGNMENT,
        RequestedClaimType.PRODUCTION_RECOMMENDATION,
    }
)

_CLAIM_TO_CORE_ENGINE: dict[RequestedClaimType, str] = {
    RequestedClaimType.CAUSAL_LIFT: "geox",
    RequestedClaimType.ROI: "mmm",
    RequestedClaimType.RESPONSE_CURVE: "mmm",
    RequestedClaimType.BUDGET_OPTIMIZATION: "decision_surface",
    RequestedClaimType.SCENARIO_PLANNING: "decision_surface",
    RequestedClaimType.MATCHED_MARKET_DESIGN: "geox",
    RequestedClaimType.POWER_MDE: "geox",
    RequestedClaimType.TREATMENT_ASSIGNMENT: "geox",
    RequestedClaimType.PRODUCTION_RECOMMENDATION: "decision_surface",
}

_CLAIM_TO_REPORT_TYPES: dict[RequestedClaimType, frozenset[str]] = {
    RequestedClaimType.GENERAL_MARKETING_ADVICE: frozenset(
        {ReportType.COLD_START_ADVISORY.value}
    ),
    RequestedClaimType.COLD_START_ADVISORY: frozenset(
        {ReportType.COLD_START_ADVISORY.value}
    ),
    RequestedClaimType.TRACKING_OR_DATA_READINESS: frozenset(
        {ReportType.COLD_START_ADVISORY.value, ReportType.READINESS_ASSESSMENT.value}
    ),
    RequestedClaimType.MEASUREMENT_READINESS: frozenset(
        {ReportType.READINESS_ASSESSMENT.value}
    ),
    RequestedClaimType.EXPERIMENT_CALIBRATION: frozenset(
        {ReportType.CALIBRATION_MAPPING.value}
    ),
}

_CLAIM_DOWNSTREAM_TOKENS: dict[RequestedClaimType, tuple[str, ...]] = {
    RequestedClaimType.ROI: ("roi_proof", "channel_roi"),
    RequestedClaimType.CAUSAL_LIFT: ("causal_lift", "causal_effect_authorization"),
    RequestedClaimType.BUDGET_OPTIMIZATION: ("budget_optimization",),
    RequestedClaimType.MATCHED_MARKET_DESIGN: (
        "matched_market_selection",
        "geox_design_approval",
    ),
    RequestedClaimType.POWER_MDE: ("power_mde_results",),
    RequestedClaimType.TREATMENT_ASSIGNMENT: ("treatment_unit_assignment",),
    RequestedClaimType.RESPONSE_CURVE: ("fitted_mmm_outputs", "response_curves"),
}


def _normalize_claim(claim: RequestedClaimType | str) -> RequestedClaimType:
    if isinstance(claim, RequestedClaimType):
        return claim
    return RequestedClaimType(claim)


def _claim_tokens(claim: RequestedClaimType | str) -> tuple[str, ...]:
    normalized = _normalize_claim(claim)
    return _CLAIM_DOWNSTREAM_TOKENS.get(normalized, (normalized.value,))


def _report_blocks_claim(report: AvailableReportSummary, claim: RequestedClaimType) -> bool:
    tokens = _claim_tokens(claim)
    blocked = {item.lower() for item in report.blocked_claims}
    forbidden = {item.lower() for item in report.forbidden_downstream_uses}
    for token in tokens:
        if token.lower() in blocked or token.lower() in forbidden:
            return True
    if claim in _CORE_ML_CLAIMS and report.governance_status == "advisory_only":
        return True
    return False


def _report_authorizes_claim(report: AvailableReportSummary, claim: RequestedClaimType) -> bool:
    if _report_blocks_claim(report, claim):
        return False
    allowed_types = _CLAIM_TO_REPORT_TYPES.get(claim, frozenset())
    if allowed_types and report.report_type not in allowed_types:
        return False
    if claim in _CORE_ML_CLAIMS:
        return False
    return True


def _report_explainable_for_claim(
    report: AvailableReportSummary,
    claim: RequestedClaimType,
) -> bool:
    if not _report_authorizes_claim(report, claim):
        return False
    allowed_types = _CLAIM_TO_REPORT_TYPES.get(claim, frozenset())
    return report.report_type in allowed_types


def _governance_blocks_claim(request: AgentAnswerabilityRequest) -> tuple[bool, list[str]]:
    blocked_reasons: list[str] = []
    if not request.available_reports:
        return False, blocked_reasons
    if not request.assert_claim_authorized_by_available_artifacts:
        return False, blocked_reasons
    for report in request.available_reports:
        if not _report_authorizes_claim(report, _normalize_claim(request.requested_claim_type)):
            blocked_reasons.extend(report.blocked_claims)
            blocked_reasons.extend(report.forbidden_downstream_uses)
    if blocked_reasons:
        return True, list(dict.fromkeys(blocked_reasons))
    return False, blocked_reasons


def _tool_supports_claim(
    tool: ToolAvailabilityStatus,
    claim: RequestedClaimType,
    reports: list[AvailableReportSummary],
) -> bool:
    claim_value = claim.value
    if claim_value in tool.unsupported_claim_types:
        return False
    if tool.supports_claim_types and claim_value not in tool.supports_claim_types:
        return False
    for report in reports:
        if _report_blocks_claim(report, claim):
            return False
    return tool.available


def _select_answer_mode(
    state: AgentAnswerabilityState,
    claim: RequestedClaimType,
    *,
    tool_unavailable: bool = False,
) -> AgentAnswerMode:
    if tool_unavailable:
        return AgentAnswerMode.TOOL_UNAVAILABLE_FALLBACK
    if state == AgentAnswerabilityState.BLOCKED_BY_CLAIM_BOUNDARY:
        return AgentAnswerMode.BLOCKED_UNSUPPORTED_CLAIM
    if state == AgentAnswerabilityState.NEEDS_USER_INPUT_OR_DATA:
        return AgentAnswerMode.MISSING_DATA_REQUEST
    if state == AgentAnswerabilityState.ANSWERABLE_FROM_REGISTERED_ARTIFACT:
        return AgentAnswerMode.DIRECT_REPORT_EXPLANATION
    if state == AgentAnswerabilityState.ANSWERABLE_FROM_DETERMINISTIC_TOOL_OUTPUT:
        if claim == RequestedClaimType.COLD_START_ADVISORY:
            return AgentAnswerMode.ADVISORY_ONLY_GUIDANCE
        return AgentAnswerMode.DETERMINISTIC_TOOL_REPORT
    engine = _CLAIM_TO_CORE_ENGINE.get(claim)
    if engine == "mmm":
        return AgentAnswerMode.ROUTE_TO_MMM
    if engine == "geox":
        return AgentAnswerMode.ROUTE_TO_GEOX
    if engine == "decision_surface":
        return AgentAnswerMode.ROUTE_TO_DECISION_SURFACE
    if claim == RequestedClaimType.EXPERIMENT_CALIBRATION:
        return AgentAnswerMode.ROUTE_TO_CALIBRATION
    if claim in {
        RequestedClaimType.MEASUREMENT_READINESS,
        RequestedClaimType.TRACKING_OR_DATA_READINESS,
    }:
        return AgentAnswerMode.ROUTE_TO_READINESS
    return AgentAnswerMode.OUT_OF_SCOPE


def _fallback_message_for_state(
    state: AgentAnswerabilityState,
    claim: RequestedClaimType,
    *,
    assert_from_artifacts: bool,
) -> str | None:
    if state == AgentAnswerabilityState.BLOCKED_BY_CLAIM_BOUNDARY:
        return (
            "That claim is not supported from the available evidence. "
            "A safe alternative route is available."
        )
    if state == AgentAnswerabilityState.NEEDS_USER_INPUT_OR_DATA:
        return "Additional governed inputs are required before this can be answered safely."
    if state == AgentAnswerabilityState.NEEDS_CORE_DIAGNOSTIC_OR_ML:
        if claim == RequestedClaimType.ROI and not assert_from_artifacts:
            return (
                "ROI requires certified MMM or experiment output. "
                "MIP can route to core ML when available."
            )
        engine = _CLAIM_TO_CORE_ENGINE.get(claim, "core ML")
        return (
            f"This request requires {engine} output "
            "that is not available from current artifacts."
        )
    return None


def evaluate_agent_answerability(
    request: AgentAnswerabilityRequest,
    *,
    decision_id: str | None = None,
) -> AgentAnswerabilityDecision:
    """Classify structured answerability input into exactly one state."""
    claim = _normalize_claim(request.requested_claim_type)
    evidence_level = _CLAIM_TO_REQUIRED_EVIDENCE.get(
        claim,
        AnswerabilityEvidenceLevel.UNSUPPORTED,
    )
    report_ids = [report.report_id for report in request.available_reports]
    blocked_claims: list[str] = []
    forbidden_scope: list[str] = []
    allowed_scope: list[str] = []
    required_tool: str | None = None
    required_core_engine: str | None = None
    state: AgentAnswerabilityState
    tool_unavailable = False

    governance_blocked, governance_reasons = _governance_blocks_claim(request)
    if governance_blocked:
        state = AgentAnswerabilityState.BLOCKED_BY_CLAIM_BOUNDARY
        blocked_claims = list(dict.fromkeys(governance_reasons))
        forbidden_scope = list(dict.fromkeys(governance_reasons))
    elif request.missing_inputs:
        state = AgentAnswerabilityState.NEEDS_USER_INPUT_OR_DATA
        blocked_claims = list(dict.fromkeys(request.missing_inputs))
    else:
        explainable_reports = [
            report
            for report in request.available_reports
            if _report_explainable_for_claim(report, claim)
        ]
        if explainable_reports:
            state = AgentAnswerabilityState.ANSWERABLE_FROM_REGISTERED_ARTIFACT
            allowed_scope = list(
                dict.fromkeys(
                    token
                    for report in explainable_reports
                    for token in report.allowed_downstream_uses
                )
            )
            forbidden_scope = list(
                dict.fromkeys(
                    token
                    for report in explainable_reports
                    for token in report.forbidden_downstream_uses
                )
            )
            blocked_claims = list(
                dict.fromkeys(
                    token
                    for report in explainable_reports
                    for token in report.blocked_claims
                )
            )
        else:
            matching_tools = [
                tool
                for tool in request.available_tools
                if _tool_supports_claim(tool, claim, request.available_reports)
            ]
            unavailable_tools = [
                tool
                for tool in request.available_tools
                if claim.value in tool.supports_claim_types and not tool.available
            ]
            if matching_tools:
                state = AgentAnswerabilityState.ANSWERABLE_FROM_DETERMINISTIC_TOOL_OUTPUT
                required_tool = matching_tools[0].tool_name
                allowed_scope = ["deterministic_tool_report", "advisory_hypothesis"]
                forbidden_scope = list(
                    dict.fromkeys(
                        token
                        for report in request.available_reports
                        for token in report.forbidden_downstream_uses
                    )
                )
            elif unavailable_tools:
                state = AgentAnswerabilityState.NEEDS_USER_INPUT_OR_DATA
                tool_unavailable = True
                required_tool = unavailable_tools[0].tool_name
            elif claim in _CORE_ML_CLAIMS:
                state = AgentAnswerabilityState.NEEDS_CORE_DIAGNOSTIC_OR_ML
                required_core_engine = _CLAIM_TO_CORE_ENGINE.get(claim)
                forbidden_scope = list(_claim_tokens(claim))
            else:
                state = AgentAnswerabilityState.NEEDS_USER_INPUT_OR_DATA

    answer_mode = _select_answer_mode(
        state,
        claim,
        tool_unavailable=tool_unavailable,
    )
    if state == AgentAnswerabilityState.ANSWERABLE_FROM_REGISTERED_ARTIFACT:
        evidence_level = AnswerabilityEvidenceLevel.DETERMINISTIC_WORKFLOW_REPORT

    return AgentAnswerabilityDecision(
        decision_id=decision_id or f"answerability-{uuid4()}",
        state=state,
        user_intent=request.user_intent,
        requested_claim_type=claim,
        answer_mode=answer_mode,
        evidence_level=evidence_level,
        available_report_ids=report_ids,
        required_tool=required_tool,
        required_core_engine=required_core_engine,
        missing_inputs=list(request.missing_inputs),
        blocked_claims=blocked_claims,
        allowed_response_scope=allowed_scope,
        forbidden_response_scope=forbidden_scope,
        fallback_message=_fallback_message_for_state(
            state,
            claim,
            assert_from_artifacts=request.assert_claim_authorized_by_available_artifacts,
        ),
        confidence_in_routing=RoutingConfidence.HIGH,
    )


__all__ = ["evaluate_agent_answerability"]
