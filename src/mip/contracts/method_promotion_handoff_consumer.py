"""MIP method promotion handoff consumer runtime.

Validator/normalizer for package-side MethodPromotionGenericAdapterMIPHandoff-like
payloads into MIPMethodPromotionHandoffConsumerRecord.

Enforcement gate only: governance context validation and normalization.
Does not create or approve DecisionSurface, bypass TrustReport, generate
RecommendationContract, enable planning answer eligibility, or authorize
budget/spend/ROI, claim/catalog/production readiness, or method/instrument promotion.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any, Mapping
from uuid import uuid4

from pydantic import Field

from mip.contracts.base import ContractBaseModel

ARTIFACT_ID = "MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_RUNTIME_001"
EXPECTED_SOURCE_PACKAGE = "panel_exp"
GENERIC_APPROVE_REVIEW_CONTINUATION = "APPROVE_REVIEW_CONTINUATION"

FIXED_AUTH = "NOT_AUTHORIZED_BY_METHOD_PROMOTION_HANDOFF"
FIXED_BYPASS = "NOT_BYPASSED_BY_METHOD_PROMOTION_HANDOFF"
FIXED_PROMO = "NOT_PROMOTED_BY_METHOD_PROMOTION_HANDOFF"

AUTH_STATUS_FIELDS: tuple[str, ...] = (
    "decision_surface_authorization_status",
    "recommendation_authorization_status",
    "catalog_authorization_status",
    "production_readout_authorization_status",
    "production_compatibility_authorization_status",
    "claim_authorization_status",
    "spend_roi_authorization_status",
    "causal_lift_authorization_status",
    "statistical_claim_authorization_status",
)
BYPASS_STATUS_FIELDS: tuple[str, ...] = ("trust_report_bypass_status",)
PROMO_STATUS_FIELDS: tuple[str, ...] = (
    "method_promotion_status",
    "instrument_promotion_status",
)

REQUIRED_BOUNDARY_KEYS: tuple[str, ...] = (
    "decision_surface_authorization_status",
    "trust_report_bypass_status",
    "recommendation_authorization_status",
    "catalog_authorization_status",
    "production_readout_authorization_status",
    "production_compatibility_authorization_status",
    "claim_authorization_status",
    "method_promotion_status",
    "instrument_promotion_status",
    "spend_roi_authorization_status",
    "causal_lift_authorization_status",
    "statistical_claim_authorization_status",
)

REQUIRED_MIP_ALLOWED_USES: frozenset[str] = frozenset(
    {
        "display_as_governance_context",
        "display_method_review_lineage",
        "display_profile_identity",
        "display_decision_scope",
        "display_missing_evidence",
        "display_blockers",
        "display_warnings",
        "display_prohibited_actions",
        "route_to_separate_catalog_review",
        "route_to_separate_claim_authorization_review",
        "route_to_separate_production_compatibility_review",
        "block_unsupported_recommendations",
        "explain_restricted_review_or_null_monitor_scope",
    }
)

# Package-side MethodPromotionGenericAdapterMIPHandoff vocabulary (accepted equivalently).
PACKAGE_MIP_ALLOWED_USES: frozenset[str] = frozenset(
    {
        "governance_context",
        "method_review_lineage",
        "profile_identity_display",
        "decision_scope_display",
        "missing_evidence_display",
        "blockers_display",
        "warnings_display",
        "prohibited_actions_display",
        "non_authorization_status_display",
        "routing_to_separate_catalog_review",
        "routing_to_separate_claim_review",
        "routing_to_separate_production_review",
        "preventing_unsupported_recommendations",
        "explaining_restricted_review_or_null_monitor_scope",
    }
)

REQUIRED_MIP_PROHIBITED_USES: frozenset[str] = frozenset(
    {
        "create_or_approve_decision_surface",
        "bypass_trust_report",
        "generate_recommendation_contract",
        "enable_planning_answer_eligibility",
        "authorize_spend_movement",
        "authorize_budget_optimization",
        "calculate_or_authorize_roi_roas",
        "authorize_production_readout",
        "authorize_production_compatibility",
        "unblock_catalog",
        "authorize_claims",
        "claim_causal_lift",
        "claim_business_lift",
        "claim_statistical_significance",
        "claim_confidence_interval_validity",
        "claim_p_value_validity",
        "claim_power_validity",
        "promote_method",
        "promote_instrument",
        "override_source_packet_runtime",
        "override_source_decision_runtime",
        "score_raw_evidence_quality",
        "repair_missing_evidence",
        "upgrade_approve_review_continuation_to_readiness",
    }
)

PACKAGE_MIP_PROHIBITED_USES: frozenset[str] = frozenset(
    {
        "decision_surface_approval",
        "trust_report_bypass",
        "recommendation_contract_authorization",
        "spend_movement_recommendation",
        "budget_optimization_authorization",
        "roi_roas_calculation_or_authorization",
        "production_readout_authorization",
        "production_compatibility_authorization",
        "catalog_unblock",
        "claim_authorization",
        "causal_lift_claim",
        "business_lift_claim",
        "statistical_significance_claim",
        "confidence_interval_claim",
        "p_value_claim",
        "statistical_power_claim",
        "method_promotion",
        "instrument_promotion",
        "overriding_source_packet_runtime",
        "overriding_source_decision_runtime",
        "raw_evidence_quality_scoring",
    }
)

CONSUMER_ALLOWED_ACTIONS: tuple[str, ...] = (
    "display_governance_context",
    "display_method_review_lineage",
    "display_profile_identity",
    "display_decision_scope",
    "display_missing_evidence",
    "display_blockers",
    "display_warnings",
    "display_prohibited_actions",
    "display_non_authorization_statuses",
    "route_to_separate_catalog_review",
    "route_to_separate_claim_authorization_review",
    "route_to_separate_production_compatibility_review",
    "block_unsupported_recommendations",
    "explain_restricted_review_or_null_monitor_scope",
    "attach_governance_context_to_diagnostic_explanation",
)

CONSUMER_BLOCKED_ACTIONS: tuple[str, ...] = (
    "create_decision_surface",
    "approve_decision_surface",
    "bypass_trust_report",
    "generate_recommendation_contract",
    "enable_planning_answer_eligibility",
    "authorize_spend_movement",
    "authorize_budget_optimization",
    "calculate_or_authorize_roi_roas",
    "authorize_production_readout",
    "authorize_production_compatibility",
    "unblock_catalog",
    "authorize_claims",
    "claim_causal_lift",
    "claim_business_lift",
    "claim_statistical_significance",
    "claim_confidence_interval_validity",
    "claim_p_value_validity",
    "claim_power_validity",
    "promote_method",
    "promote_instrument",
    "override_source_packet_runtime",
    "override_source_decision_runtime",
    "score_raw_evidence_quality",
    "repair_missing_evidence",
    "upgrade_approve_review_continuation_to_readiness",
)

_TRUTHY_ATTEMPT_KEYS: frozenset[str] = frozenset(
    {
        "create_decision_surface",
        "approve_decision_surface",
        "decision_surface_authorized",
        "bypass_trust_report",
        "trust_report_bypassed",
        "generate_recommendation_contract",
        "recommendation_contract_authorized",
        "enable_planning_answer_eligibility",
        "planning_recommendation_enabled",
        "planning_answer_eligibility_enabled",
        "authorize_spend_movement",
        "spend_movement_authorized",
        "authorize_budget_optimization",
        "budget_optimization_enabled",
        "calculate_or_authorize_roi_roas",
        "roi_roas_authorized",
        "authorize_production_readout",
        "authorize_production_compatibility",
        "production_compatibility_authorized",
        "unblock_catalog",
        "catalog_unblocked",
        "authorize_claims",
        "claim_authorization_changed",
        "claim_causal_lift",
        "causal_lift_claim_authorized",
        "claim_business_lift",
        "business_lift_claim_authorized",
        "claim_statistical_significance",
        "statistical_claim_authorized",
        "promote_method",
        "method_promoted",
        "promote_instrument",
        "instrument_promoted",
        "override_source_packet_runtime",
        "override_source_decision_runtime",
        "score_raw_evidence_quality",
        "repair_missing_evidence",
        "upgrade_approve_review_continuation_to_readiness",
        "production_ready",
        "readiness_authorized",
        "mip_integration_implemented",
    }
)

_BLOCKED_ROUTING_HINTS: frozenset[str] = frozenset(
    {
        "ROUTE_BLOCKED_DECISION_SURFACE_APPROVAL",
        "ROUTE_BLOCKED_TRUST_REPORT_BYPASS",
        "ROUTE_BLOCKED_RECOMMENDATION_CONTRACT",
        "ROUTE_BLOCKED_PLANNING_RECOMMENDATION",
        "ROUTE_BLOCKED_BUDGET_OPTIMIZER",
        "ROUTE_BLOCKED_SPEND_REALLOCATION",
        "ROUTE_BLOCKED_ROI_ROAS_RECOMMENDATION",
        "ROUTE_BLOCKED_PRODUCTION_READOUT",
        "ROUTE_TO_DECISION_SURFACE_APPROVAL",
        "ROUTE_TO_TRUST_REPORT_BYPASS",
        "ROUTE_TO_RECOMMENDATION_CONTRACT",
        "ROUTE_TO_PLANNING_RECOMMENDATION",
        "ROUTE_TO_BUDGET_OPTIMIZER",
        "ROUTE_TO_SPEND_REALLOCATION",
        "ROUTE_TO_ROI_ROAS_RECOMMENDATION",
        "ROUTE_TO_PRODUCTION_READOUT",
    }
)


class MIPMethodPromotionHandoffAuthorizationStatus(StrEnum):
    NOT_AUTHORIZED_BY_METHOD_PROMOTION_HANDOFF = FIXED_AUTH


class MIPMethodPromotionHandoffBypassStatus(StrEnum):
    NOT_BYPASSED_BY_METHOD_PROMOTION_HANDOFF = FIXED_BYPASS


class MIPMethodPromotionHandoffPromotionStatus(StrEnum):
    NOT_PROMOTED_BY_METHOD_PROMOTION_HANDOFF = FIXED_PROMO


class MIPMethodPromotionHandoffConsumerStatus(StrEnum):
    CONSUMER_RUNTIME_READY_FOR_GOVERNANCE_CONTEXT = (
        "CONSUMER_RUNTIME_READY_FOR_GOVERNANCE_CONTEXT"
    )
    CONSUMER_RUNTIME_BLOCKED_MISSING_PAYLOAD = "CONSUMER_RUNTIME_BLOCKED_MISSING_PAYLOAD"
    CONSUMER_RUNTIME_BLOCKED_UNSUPPORTED_SOURCE_PACKAGE = (
        "CONSUMER_RUNTIME_BLOCKED_UNSUPPORTED_SOURCE_PACKAGE"
    )
    CONSUMER_RUNTIME_BLOCKED_MISSING_HANDOFF_ID = (
        "CONSUMER_RUNTIME_BLOCKED_MISSING_HANDOFF_ID"
    )
    CONSUMER_RUNTIME_BLOCKED_MISSING_PROFILE_ID = (
        "CONSUMER_RUNTIME_BLOCKED_MISSING_PROFILE_ID"
    )
    CONSUMER_RUNTIME_BLOCKED_MISSING_CANONICAL_IDENTITY = (
        "CONSUMER_RUNTIME_BLOCKED_MISSING_CANONICAL_IDENTITY"
    )
    CONSUMER_RUNTIME_BLOCKED_MISSING_DECISION_SCOPE = (
        "CONSUMER_RUNTIME_BLOCKED_MISSING_DECISION_SCOPE"
    )
    CONSUMER_RUNTIME_BLOCKED_MISSING_GENERIC_DECISION_STATUS = (
        "CONSUMER_RUNTIME_BLOCKED_MISSING_GENERIC_DECISION_STATUS"
    )
    CONSUMER_RUNTIME_BLOCKED_MISSING_SOURCE_OF_TRUTH_REFS = (
        "CONSUMER_RUNTIME_BLOCKED_MISSING_SOURCE_OF_TRUTH_REFS"
    )
    CONSUMER_RUNTIME_BLOCKED_MISSING_BOUNDARY_STATUSES = (
        "CONSUMER_RUNTIME_BLOCKED_MISSING_BOUNDARY_STATUSES"
    )
    CONSUMER_RUNTIME_BLOCKED_MISSING_ALLOWED_USES = (
        "CONSUMER_RUNTIME_BLOCKED_MISSING_ALLOWED_USES"
    )
    CONSUMER_RUNTIME_BLOCKED_MISSING_PROHIBITED_USES = (
        "CONSUMER_RUNTIME_BLOCKED_MISSING_PROHIBITED_USES"
    )
    CONSUMER_RUNTIME_BLOCKED_AUTHORIZATION_STATUS_WEAKENED = (
        "CONSUMER_RUNTIME_BLOCKED_AUTHORIZATION_STATUS_WEAKENED"
    )
    CONSUMER_RUNTIME_BLOCKED_TRUST_BYPASS_ATTEMPT = (
        "CONSUMER_RUNTIME_BLOCKED_TRUST_BYPASS_ATTEMPT"
    )
    CONSUMER_RUNTIME_BLOCKED_RECOMMENDATION_AUTHORIZATION_ATTEMPT = (
        "CONSUMER_RUNTIME_BLOCKED_RECOMMENDATION_AUTHORIZATION_ATTEMPT"
    )
    CONSUMER_RUNTIME_BLOCKED_DECISION_SURFACE_AUTHORIZATION_ATTEMPT = (
        "CONSUMER_RUNTIME_BLOCKED_DECISION_SURFACE_AUTHORIZATION_ATTEMPT"
    )
    CONSUMER_RUNTIME_BLOCKED_CLAIM_OR_PRODUCTION_AUTHORIZATION_ATTEMPT = (
        "CONSUMER_RUNTIME_BLOCKED_CLAIM_OR_PRODUCTION_AUTHORIZATION_ATTEMPT"
    )
    CONSUMER_RUNTIME_BLOCKED_PROMOTION_ATTEMPT = (
        "CONSUMER_RUNTIME_BLOCKED_PROMOTION_ATTEMPT"
    )
    CONSUMER_RUNTIME_BLOCKED_PLANNING_RECOMMENDATION_ATTEMPT = (
        "CONSUMER_RUNTIME_BLOCKED_PLANNING_RECOMMENDATION_ATTEMPT"
    )
    CONSUMER_RUNTIME_BLOCKED_SPEND_ROI_AUTHORIZATION_ATTEMPT = (
        "CONSUMER_RUNTIME_BLOCKED_SPEND_ROI_AUTHORIZATION_ATTEMPT"
    )
    CONSUMER_RUNTIME_BLOCKED_SOURCE_OF_TRUTH_OVERRIDE_ATTEMPT = (
        "CONSUMER_RUNTIME_BLOCKED_SOURCE_OF_TRUTH_OVERRIDE_ATTEMPT"
    )
    CONSUMER_RUNTIME_BLOCKED_GENERIC_APPROVAL_UPGRADE_ATTEMPT = (
        "CONSUMER_RUNTIME_BLOCKED_GENERIC_APPROVAL_UPGRADE_ATTEMPT"
    )


class MIPMethodPromotionHandoffRoutingHint(StrEnum):
    ROUTE_TO_GOVERNANCE_CONTEXT_DISPLAY = "ROUTE_TO_GOVERNANCE_CONTEXT_DISPLAY"
    ROUTE_TO_DIAGNOSTIC_EXPLANATION = "ROUTE_TO_DIAGNOSTIC_EXPLANATION"
    ROUTE_TO_CATALOG_REVIEW = "ROUTE_TO_CATALOG_REVIEW"
    ROUTE_TO_CLAIM_AUTHORIZATION_REVIEW = "ROUTE_TO_CLAIM_AUTHORIZATION_REVIEW"
    ROUTE_TO_PRODUCTION_COMPATIBILITY_REVIEW = (
        "ROUTE_TO_PRODUCTION_COMPATIBILITY_REVIEW"
    )
    ROUTE_TO_UNSUPPORTED_RECOMMENDATION_BLOCK = (
        "ROUTE_TO_UNSUPPORTED_RECOMMENDATION_BLOCK"
    )
    ROUTE_BLOCKED_DECISION_SURFACE_APPROVAL = "ROUTE_BLOCKED_DECISION_SURFACE_APPROVAL"
    ROUTE_BLOCKED_TRUST_REPORT_BYPASS = "ROUTE_BLOCKED_TRUST_REPORT_BYPASS"
    ROUTE_BLOCKED_RECOMMENDATION_CONTRACT = "ROUTE_BLOCKED_RECOMMENDATION_CONTRACT"
    ROUTE_BLOCKED_PLANNING_RECOMMENDATION = "ROUTE_BLOCKED_PLANNING_RECOMMENDATION"
    ROUTE_BLOCKED_BUDGET_OPTIMIZER = "ROUTE_BLOCKED_BUDGET_OPTIMIZER"
    ROUTE_BLOCKED_SPEND_REALLOCATION = "ROUTE_BLOCKED_SPEND_REALLOCATION"
    ROUTE_BLOCKED_ROI_ROAS_RECOMMENDATION = "ROUTE_BLOCKED_ROI_ROAS_RECOMMENDATION"
    ROUTE_BLOCKED_PRODUCTION_READOUT = "ROUTE_BLOCKED_PRODUCTION_READOUT"


class MIPMethodPromotionHandoffConsumerRuntimeInput(ContractBaseModel):
    """Runtime input for method promotion handoff consumer validation."""

    raw_handoff_payload: Mapping[str, Any] | None = None
    ingestion_context: Mapping[str, Any] | None = None
    received_at: str | None = None
    source_package_expected: str = EXPECTED_SOURCE_PACKAGE
    upstream_artifact_expected: str | None = None
    strict_validation: bool = True
    lineage_context: Mapping[str, Any] | None = None


class MIPMethodPromotionHandoffConsumerRecord(ContractBaseModel):
    """Normalized MIP-side consumer record for governance context only."""

    consumer_record_id: str
    received_handoff_id: str
    source_package: str
    source_artifact_id: str
    source_runtime: str
    source_runtime_version: str
    profile_id: str
    canonical_identity: Mapping[str, Any]
    decision_scope: Mapping[str, Any]
    generic_packet_status: str
    generic_eligibility_status: str
    generic_decision_status: str
    generic_governance_stage: str
    source_of_truth_refs: Mapping[str, Any]
    source_packet_ref: str
    source_decision_ref: str
    source_governance_summary_ref: str
    missing_evidence: tuple[str, ...] = ()
    blockers: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    prohibited_actions: tuple[str, ...] = ()
    boundary_statuses: Mapping[str, Any]
    mip_allowed_uses: tuple[str, ...] = ()
    mip_prohibited_uses: tuple[str, ...] = ()
    consumer_allowed_actions: tuple[str, ...] = CONSUMER_ALLOWED_ACTIONS
    consumer_blocked_actions: tuple[str, ...] = CONSUMER_BLOCKED_ACTIONS
    decision_surface_authorization_status: str = FIXED_AUTH
    trust_report_bypass_status: str = FIXED_BYPASS
    recommendation_authorization_status: str = FIXED_AUTH
    catalog_authorization_status: str = FIXED_AUTH
    production_readout_authorization_status: str = FIXED_AUTH
    production_compatibility_authorization_status: str = FIXED_AUTH
    claim_authorization_status: str = FIXED_AUTH
    method_promotion_status: str = FIXED_PROMO
    instrument_promotion_status: str = FIXED_PROMO
    spend_roi_authorization_status: str = FIXED_AUTH
    causal_lift_authorization_status: str = FIXED_AUTH
    statistical_claim_authorization_status: str = FIXED_AUTH
    consumer_status: MIPMethodPromotionHandoffConsumerStatus = (
        MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_READY_FOR_GOVERNANCE_CONTEXT
    )
    routing_hint: MIPMethodPromotionHandoffRoutingHint = (
        MIPMethodPromotionHandoffRoutingHint.ROUTE_TO_GOVERNANCE_CONTEXT_DISPLAY
    )
    lineage: Mapping[str, Any] = Field(default_factory=dict)
    created_from_handoff: bool = True


class MIPMethodPromotionHandoffConsumerRuntimeOutput(ContractBaseModel):
    """Runtime output for method promotion handoff consumer validation."""

    consumer_record: MIPMethodPromotionHandoffConsumerRecord | None = None
    consumer_status: MIPMethodPromotionHandoffConsumerStatus
    validation_errors: tuple[str, ...] = ()
    validation_warnings: tuple[str, ...] = ()
    routing_hint: MIPMethodPromotionHandoffRoutingHint
    accepted_for_governance_context: bool = False
    rejected_for_decisioning: bool = True
    lineage: Mapping[str, Any] = Field(default_factory=dict)


def _as_str(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, StrEnum):
        return str(value.value)
    return str(value).strip()


def _as_mapping(value: Any) -> dict[str, Any] | None:
    if value is None:
        return None
    if isinstance(value, Mapping):
        return dict(value)
    return None


def _as_identity_or_scope(value: Any, *, key: str) -> dict[str, Any] | None:
    """Accept mapping or non-empty string (package payloads may send strings)."""

    mapping = _as_mapping(value)
    if mapping:
        return mapping
    text = _as_str(value)
    if text:
        return {key: text}
    return None


def _as_source_of_truth_refs(value: Any) -> dict[str, Any] | None:
    """Accept mapping or list/tuple of refs from package handoff."""

    mapping = _as_mapping(value)
    if mapping:
        return mapping
    if isinstance(value, (list, tuple)):
        refs = [_as_str(item) for item in value if _as_str(item)]
        if refs:
            return {"refs": refs}
    text = _as_str(value)
    if text:
        return {"refs": [text]}
    return None


def _as_str_tuple(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, (list, tuple)):
        return tuple(_as_str(item) for item in value if _as_str(item))
    if isinstance(value, str) and value.strip():
        return (value.strip(),)
    return ()


def _uses_cover_required(provided: tuple[str, ...], required: frozenset[str]) -> bool:
    return required.issubset(set(provided))


def _merge_boundary_statuses(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Merge boundary_statuses with top-level fixed status fields."""

    boundary = dict(_as_mapping(payload.get("boundary_statuses")) or {})
    for field in REQUIRED_BOUNDARY_KEYS:
        if field not in boundary and payload.get(field) is not None:
            boundary[field] = payload.get(field)
    return boundary


def _is_truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "authorized", "promoted"}
    return False


def _status_value(payload: Mapping[str, Any], field: str) -> str | None:
    boundary = _as_mapping(payload.get("boundary_statuses")) or {}
    if field in payload and payload.get(field) is not None:
        return _as_str(payload.get(field)) or None
    if field in boundary and boundary.get(field) is not None:
        return _as_str(boundary.get(field)) or None
    return None


def _blocked_output(
    *,
    status: MIPMethodPromotionHandoffConsumerStatus,
    errors: list[str],
    warnings: list[str] | None = None,
    routing_hint: MIPMethodPromotionHandoffRoutingHint = (
        MIPMethodPromotionHandoffRoutingHint.ROUTE_TO_UNSUPPORTED_RECOMMENDATION_BLOCK
    ),
    lineage: Mapping[str, Any] | None = None,
) -> MIPMethodPromotionHandoffConsumerRuntimeOutput:
    return MIPMethodPromotionHandoffConsumerRuntimeOutput(
        consumer_record=None,
        consumer_status=status,
        validation_errors=tuple(errors),
        validation_warnings=tuple(warnings or ()),
        routing_hint=routing_hint,
        accepted_for_governance_context=False,
        rejected_for_decisioning=True,
        lineage=dict(lineage or {}),
    )


def _detect_attempt_block(
    payload: Mapping[str, Any],
) -> tuple[MIPMethodPromotionHandoffConsumerStatus, MIPMethodPromotionHandoffRoutingHint, str] | None:
    """Return the most specific attempt block if present."""

    routing = _as_str(payload.get("routing_hint") or payload.get("requested_routing_hint"))
    if routing in _BLOCKED_ROUTING_HINTS:
        if "DECISION_SURFACE" in routing:
            return (
                MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_BLOCKED_DECISION_SURFACE_AUTHORIZATION_ATTEMPT,
                MIPMethodPromotionHandoffRoutingHint.ROUTE_BLOCKED_DECISION_SURFACE_APPROVAL,
                f"blocked routing hint attempted: {routing}",
            )
        if "TRUST" in routing:
            return (
                MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_BLOCKED_TRUST_BYPASS_ATTEMPT,
                MIPMethodPromotionHandoffRoutingHint.ROUTE_BLOCKED_TRUST_REPORT_BYPASS,
                f"blocked routing hint attempted: {routing}",
            )
        if "RECOMMENDATION" in routing and "PLANNING" not in routing and "ROI" not in routing:
            return (
                MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_BLOCKED_RECOMMENDATION_AUTHORIZATION_ATTEMPT,
                MIPMethodPromotionHandoffRoutingHint.ROUTE_BLOCKED_RECOMMENDATION_CONTRACT,
                f"blocked routing hint attempted: {routing}",
            )
        if "PLANNING" in routing:
            return (
                MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_BLOCKED_PLANNING_RECOMMENDATION_ATTEMPT,
                MIPMethodPromotionHandoffRoutingHint.ROUTE_BLOCKED_PLANNING_RECOMMENDATION,
                f"blocked routing hint attempted: {routing}",
            )
        if "BUDGET" in routing:
            return (
                MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_BLOCKED_SPEND_ROI_AUTHORIZATION_ATTEMPT,
                MIPMethodPromotionHandoffRoutingHint.ROUTE_BLOCKED_BUDGET_OPTIMIZER,
                f"blocked routing hint attempted: {routing}",
            )
        if "SPEND" in routing:
            return (
                MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_BLOCKED_SPEND_ROI_AUTHORIZATION_ATTEMPT,
                MIPMethodPromotionHandoffRoutingHint.ROUTE_BLOCKED_SPEND_REALLOCATION,
                f"blocked routing hint attempted: {routing}",
            )
        if "ROI" in routing or "ROAS" in routing:
            return (
                MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_BLOCKED_SPEND_ROI_AUTHORIZATION_ATTEMPT,
                MIPMethodPromotionHandoffRoutingHint.ROUTE_BLOCKED_ROI_ROAS_RECOMMENDATION,
                f"blocked routing hint attempted: {routing}",
            )
        if "PRODUCTION" in routing:
            return (
                MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_BLOCKED_CLAIM_OR_PRODUCTION_AUTHORIZATION_ATTEMPT,
                MIPMethodPromotionHandoffRoutingHint.ROUTE_BLOCKED_PRODUCTION_READOUT,
                f"blocked routing hint attempted: {routing}",
            )

    for key in _TRUTHY_ATTEMPT_KEYS:
        if key in payload and _is_truthy(payload.get(key)):
            if key in {
                "create_decision_surface",
                "approve_decision_surface",
                "decision_surface_authorized",
            }:
                return (
                    MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_BLOCKED_DECISION_SURFACE_AUTHORIZATION_ATTEMPT,
                    MIPMethodPromotionHandoffRoutingHint.ROUTE_BLOCKED_DECISION_SURFACE_APPROVAL,
                    f"decision surface authorization attempt via {key}",
                )
            if key in {"bypass_trust_report", "trust_report_bypassed"}:
                return (
                    MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_BLOCKED_TRUST_BYPASS_ATTEMPT,
                    MIPMethodPromotionHandoffRoutingHint.ROUTE_BLOCKED_TRUST_REPORT_BYPASS,
                    f"trust report bypass attempt via {key}",
                )
            if key in {
                "generate_recommendation_contract",
                "recommendation_contract_authorized",
            }:
                return (
                    MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_BLOCKED_RECOMMENDATION_AUTHORIZATION_ATTEMPT,
                    MIPMethodPromotionHandoffRoutingHint.ROUTE_BLOCKED_RECOMMENDATION_CONTRACT,
                    f"recommendation authorization attempt via {key}",
                )
            if key in {
                "enable_planning_answer_eligibility",
                "planning_recommendation_enabled",
                "planning_answer_eligibility_enabled",
            }:
                return (
                    MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_BLOCKED_PLANNING_RECOMMENDATION_ATTEMPT,
                    MIPMethodPromotionHandoffRoutingHint.ROUTE_BLOCKED_PLANNING_RECOMMENDATION,
                    f"planning recommendation attempt via {key}",
                )
            if key in {
                "authorize_spend_movement",
                "spend_movement_authorized",
                "authorize_budget_optimization",
                "budget_optimization_enabled",
                "calculate_or_authorize_roi_roas",
                "roi_roas_authorized",
            }:
                hint = MIPMethodPromotionHandoffRoutingHint.ROUTE_BLOCKED_SPEND_REALLOCATION
                if "budget" in key:
                    hint = MIPMethodPromotionHandoffRoutingHint.ROUTE_BLOCKED_BUDGET_OPTIMIZER
                if "roi" in key or "roas" in key:
                    hint = MIPMethodPromotionHandoffRoutingHint.ROUTE_BLOCKED_ROI_ROAS_RECOMMENDATION
                return (
                    MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_BLOCKED_SPEND_ROI_AUTHORIZATION_ATTEMPT,
                    hint,
                    f"spend/ROI authorization attempt via {key}",
                )
            if key in {
                "authorize_production_readout",
                "authorize_production_compatibility",
                "production_compatibility_authorized",
                "unblock_catalog",
                "catalog_unblocked",
                "authorize_claims",
                "claim_authorization_changed",
                "claim_causal_lift",
                "causal_lift_claim_authorized",
                "claim_business_lift",
                "business_lift_claim_authorized",
                "claim_statistical_significance",
                "statistical_claim_authorized",
            }:
                return (
                    MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_BLOCKED_CLAIM_OR_PRODUCTION_AUTHORIZATION_ATTEMPT,
                    MIPMethodPromotionHandoffRoutingHint.ROUTE_BLOCKED_PRODUCTION_READOUT,
                    f"claim/production authorization attempt via {key}",
                )
            if key in {
                "promote_method",
                "method_promoted",
                "promote_instrument",
                "instrument_promoted",
            }:
                return (
                    MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_BLOCKED_PROMOTION_ATTEMPT,
                    MIPMethodPromotionHandoffRoutingHint.ROUTE_TO_UNSUPPORTED_RECOMMENDATION_BLOCK,
                    f"promotion attempt via {key}",
                )
            if key in {
                "override_source_packet_runtime",
                "override_source_decision_runtime",
            }:
                return (
                    MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_BLOCKED_SOURCE_OF_TRUTH_OVERRIDE_ATTEMPT,
                    MIPMethodPromotionHandoffRoutingHint.ROUTE_TO_UNSUPPORTED_RECOMMENDATION_BLOCK,
                    f"source-of-truth override attempt via {key}",
                )
            if key in {
                "upgrade_approve_review_continuation_to_readiness",
                "production_ready",
                "readiness_authorized",
            }:
                return (
                    MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_BLOCKED_GENERIC_APPROVAL_UPGRADE_ATTEMPT,
                    MIPMethodPromotionHandoffRoutingHint.ROUTE_TO_UNSUPPORTED_RECOMMENDATION_BLOCK,
                    f"generic approval upgrade attempt via {key}",
                )
            if key in {"score_raw_evidence_quality", "repair_missing_evidence"}:
                return (
                    MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_BLOCKED_SOURCE_OF_TRUTH_OVERRIDE_ATTEMPT,
                    MIPMethodPromotionHandoffRoutingHint.ROUTE_TO_UNSUPPORTED_RECOMMENDATION_BLOCK,
                    f"evidence mutation attempt via {key}",
                )

    return None


def validate_and_normalize_method_promotion_handoff(
    runtime_input: MIPMethodPromotionHandoffConsumerRuntimeInput,
) -> MIPMethodPromotionHandoffConsumerRuntimeOutput:
    """Validate and normalize a package handoff payload into a consumer record.

    Valid payloads are accepted for governance context display only and always
    rejected for decisioning.
    """

    base_lineage: dict[str, Any] = {
        "artifact_id": ARTIFACT_ID,
        "runtime": "validate_and_normalize_method_promotion_handoff",
        **dict(runtime_input.lineage_context or {}),
    }
    if runtime_input.received_at:
        base_lineage["received_at"] = runtime_input.received_at
    if runtime_input.ingestion_context:
        base_lineage["ingestion_context"] = dict(runtime_input.ingestion_context)

    payload = runtime_input.raw_handoff_payload
    if payload is None or (isinstance(payload, Mapping) and len(payload) == 0):
        return _blocked_output(
            status=MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_BLOCKED_MISSING_PAYLOAD,
            errors=["raw_handoff_payload is missing or empty"],
            lineage=base_lineage,
        )

    if not isinstance(payload, Mapping):
        return _blocked_output(
            status=MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_BLOCKED_MISSING_PAYLOAD,
            errors=["raw_handoff_payload must be a mapping"],
            lineage=base_lineage,
        )

    payload_map = dict(payload)
    expected_package = _as_str(runtime_input.source_package_expected) or EXPECTED_SOURCE_PACKAGE
    source_package = _as_str(payload_map.get("source_package"))
    if source_package != expected_package:
        return _blocked_output(
            status=MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_BLOCKED_UNSUPPORTED_SOURCE_PACKAGE,
            errors=[
                f"unsupported source_package={source_package!r}; expected {expected_package!r}"
            ],
            lineage={**base_lineage, "source_package": source_package},
        )

    handoff_id = _as_str(payload_map.get("handoff_id") or payload_map.get("received_handoff_id"))
    if not handoff_id:
        return _blocked_output(
            status=MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_BLOCKED_MISSING_HANDOFF_ID,
            errors=["handoff_id is required"],
            lineage=base_lineage,
        )

    profile_id = _as_str(payload_map.get("profile_id"))
    if not profile_id:
        return _blocked_output(
            status=MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_BLOCKED_MISSING_PROFILE_ID,
            errors=["profile_id is required"],
            lineage=base_lineage,
        )

    canonical_identity = _as_identity_or_scope(
        payload_map.get("canonical_identity"), key="canonical_identity"
    )
    if not canonical_identity:
        return _blocked_output(
            status=MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_BLOCKED_MISSING_CANONICAL_IDENTITY,
            errors=["canonical_identity is required"],
            lineage=base_lineage,
        )

    decision_scope = _as_identity_or_scope(
        payload_map.get("decision_scope"), key="decision_scope"
    )
    if not decision_scope:
        return _blocked_output(
            status=MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_BLOCKED_MISSING_DECISION_SCOPE,
            errors=["decision_scope is required"],
            lineage=base_lineage,
        )

    generic_decision_status = _as_str(payload_map.get("generic_decision_status"))
    if not generic_decision_status:
        return _blocked_output(
            status=MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_BLOCKED_MISSING_GENERIC_DECISION_STATUS,
            errors=["generic_decision_status is required"],
            lineage=base_lineage,
        )

    source_of_truth_refs = _as_source_of_truth_refs(payload_map.get("source_of_truth_refs"))
    if not source_of_truth_refs:
        return _blocked_output(
            status=MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_BLOCKED_MISSING_SOURCE_OF_TRUTH_REFS,
            errors=["source_of_truth_refs is required"],
            lineage=base_lineage,
        )

    boundary_statuses = _merge_boundary_statuses(payload_map)
    if not boundary_statuses:
        return _blocked_output(
            status=MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_BLOCKED_MISSING_BOUNDARY_STATUSES,
            errors=["boundary_statuses is required"],
            lineage=base_lineage,
        )
    missing_boundary = [key for key in REQUIRED_BOUNDARY_KEYS if key not in boundary_statuses]
    if missing_boundary:
        return _blocked_output(
            status=MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_BLOCKED_MISSING_BOUNDARY_STATUSES,
            errors=[f"boundary_statuses missing keys: {', '.join(missing_boundary)}"],
            lineage=base_lineage,
        )

    mip_allowed_uses = _as_str_tuple(payload_map.get("mip_allowed_uses"))
    if not mip_allowed_uses:
        return _blocked_output(
            status=MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_BLOCKED_MISSING_ALLOWED_USES,
            errors=["mip_allowed_uses is required"],
            lineage=base_lineage,
        )
    if runtime_input.strict_validation:
        allowed_ok = _uses_cover_required(
            mip_allowed_uses, REQUIRED_MIP_ALLOWED_USES
        ) or _uses_cover_required(mip_allowed_uses, PACKAGE_MIP_ALLOWED_USES)
        if not allowed_ok:
            return _blocked_output(
                status=MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_BLOCKED_MISSING_ALLOWED_USES,
                errors=["mip_allowed_uses missing required uses for MIP or package vocabulary"],
                lineage=base_lineage,
            )

    mip_prohibited_uses = _as_str_tuple(payload_map.get("mip_prohibited_uses"))
    if not mip_prohibited_uses:
        return _blocked_output(
            status=MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_BLOCKED_MISSING_PROHIBITED_USES,
            errors=["mip_prohibited_uses is required"],
            lineage=base_lineage,
        )
    if runtime_input.strict_validation:
        prohibited_ok = _uses_cover_required(
            mip_prohibited_uses, REQUIRED_MIP_PROHIBITED_USES
        ) or _uses_cover_required(mip_prohibited_uses, PACKAGE_MIP_PROHIBITED_USES)
        if not prohibited_ok:
            return _blocked_output(
                status=MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_BLOCKED_MISSING_PROHIBITED_USES,
                errors=[
                    "mip_prohibited_uses missing or weakened required prohibitions "
                    "for MIP or package vocabulary"
                ],
                lineage=base_lineage,
            )

    # Fixed non-authorization statuses must be present and unweakened.
    for field in AUTH_STATUS_FIELDS:
        value = _status_value(payload_map, field)
        if value is None:
            return _blocked_output(
                status=MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_BLOCKED_MISSING_BOUNDARY_STATUSES,
                errors=[f"missing authorization status field: {field}"],
                lineage=base_lineage,
            )
        if value != FIXED_AUTH:
            return _blocked_output(
                status=MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_BLOCKED_AUTHORIZATION_STATUS_WEAKENED,
                errors=[f"authorization status weakened for {field}: {value!r}"],
                lineage=base_lineage,
                routing_hint=MIPMethodPromotionHandoffRoutingHint.ROUTE_TO_UNSUPPORTED_RECOMMENDATION_BLOCK,
            )
    for field in BYPASS_STATUS_FIELDS:
        value = _status_value(payload_map, field)
        if value is None:
            return _blocked_output(
                status=MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_BLOCKED_MISSING_BOUNDARY_STATUSES,
                errors=[f"missing bypass status field: {field}"],
                lineage=base_lineage,
            )
        if value != FIXED_BYPASS:
            return _blocked_output(
                status=MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_BLOCKED_TRUST_BYPASS_ATTEMPT,
                errors=[f"trust bypass status weakened for {field}: {value!r}"],
                lineage=base_lineage,
                routing_hint=MIPMethodPromotionHandoffRoutingHint.ROUTE_BLOCKED_TRUST_REPORT_BYPASS,
            )
    for field in PROMO_STATUS_FIELDS:
        value = _status_value(payload_map, field)
        if value is None:
            return _blocked_output(
                status=MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_BLOCKED_MISSING_BOUNDARY_STATUSES,
                errors=[f"missing promotion status field: {field}"],
                lineage=base_lineage,
            )
        if value != FIXED_PROMO:
            return _blocked_output(
                status=MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_BLOCKED_PROMOTION_ATTEMPT,
                errors=[f"promotion status weakened for {field}: {value!r}"],
                lineage=base_lineage,
            )

    attempt = _detect_attempt_block(payload_map)
    if attempt is not None:
        status, hint, message = attempt
        return _blocked_output(
            status=status,
            errors=[message],
            routing_hint=hint,
            lineage=base_lineage,
        )

    # Preserve APPROVE_REVIEW_CONTINUATION as weak governance context only.
    warnings: list[str] = []
    if generic_decision_status == GENERIC_APPROVE_REVIEW_CONTINUATION:
        warnings.append(
            "generic_decision_status APPROVE_REVIEW_CONTINUATION preserved as weak "
            "governance context only; not readiness, authorization, or promotion"
        )
        upgrade_flags = (
            "upgrade_approve_review_continuation_to_readiness",
            "production_ready",
            "readiness_authorized",
            "decision_surface_authorized",
        )
        for flag in upgrade_flags:
            if flag in payload_map and _is_truthy(payload_map.get(flag)):
                return _blocked_output(
                    status=MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_BLOCKED_GENERIC_APPROVAL_UPGRADE_ATTEMPT,
                    errors=[f"generic approval upgrade attempt via {flag}"],
                    lineage=base_lineage,
                )

    if runtime_input.upstream_artifact_expected:
        source_artifact = _as_str(payload_map.get("source_artifact_id"))
        if source_artifact and source_artifact != runtime_input.upstream_artifact_expected:
            warnings.append(
                "source_artifact_id does not match upstream_artifact_expected "
                f"({runtime_input.upstream_artifact_expected!r}); preserved without override"
            )

    source_packet_ref = _as_str(
        payload_map.get("source_packet_ref")
        or source_of_truth_refs.get("source_packet_ref")
        or source_of_truth_refs.get("packet_ref")
    )
    source_decision_ref = _as_str(
        payload_map.get("source_decision_ref")
        or source_of_truth_refs.get("source_decision_ref")
        or source_of_truth_refs.get("decision_ref")
    )
    source_governance_summary_ref = _as_str(
        payload_map.get("source_governance_summary_ref")
        or source_of_truth_refs.get("source_governance_summary_ref")
        or source_of_truth_refs.get("governance_summary_ref")
    )

    # Never override package source-of-truth refs; preserve as provided.
    preserved_refs = dict(source_of_truth_refs)

    raw_payload_lineage = payload_map.get("lineage")
    payload_lineage: dict[str, Any] = (
        dict(raw_payload_lineage) if isinstance(raw_payload_lineage, Mapping) else {}
    )
    record_lineage = {
        **base_lineage,
        "handoff_id": handoff_id,
        "profile_id": profile_id,
        "generic_decision_status": generic_decision_status,
        "generic_approve_review_continuation_weak_context_only": (
            generic_decision_status == GENERIC_APPROVE_REVIEW_CONTINUATION
        ),
        "accepted_for_governance_context_only": True,
        "rejected_for_decisioning": True,
        **payload_lineage,
    }

    record = MIPMethodPromotionHandoffConsumerRecord(
        consumer_record_id=_as_str(payload_map.get("consumer_record_id")) or f"mphc-{uuid4().hex[:12]}",
        received_handoff_id=handoff_id,
        source_package=source_package,
        source_artifact_id=_as_str(payload_map.get("source_artifact_id")),
        source_runtime=_as_str(payload_map.get("source_runtime")),
        source_runtime_version=_as_str(payload_map.get("source_runtime_version")),
        profile_id=profile_id,
        canonical_identity=dict(canonical_identity),
        decision_scope=dict(decision_scope),
        generic_packet_status=_as_str(payload_map.get("generic_packet_status")),
        generic_eligibility_status=_as_str(payload_map.get("generic_eligibility_status")),
        generic_decision_status=generic_decision_status,
        generic_governance_stage=_as_str(payload_map.get("generic_governance_stage")),
        source_of_truth_refs=preserved_refs,
        source_packet_ref=source_packet_ref,
        source_decision_ref=source_decision_ref,
        source_governance_summary_ref=source_governance_summary_ref,
        missing_evidence=_as_str_tuple(payload_map.get("missing_evidence")),
        blockers=_as_str_tuple(payload_map.get("blockers")),
        warnings=tuple(
            list(_as_str_tuple(payload_map.get("warnings"))) + warnings
        ),
        prohibited_actions=_as_str_tuple(payload_map.get("prohibited_actions")),
        boundary_statuses=dict(boundary_statuses),
        mip_allowed_uses=mip_allowed_uses,
        mip_prohibited_uses=mip_prohibited_uses,
        consumer_allowed_actions=CONSUMER_ALLOWED_ACTIONS,
        consumer_blocked_actions=CONSUMER_BLOCKED_ACTIONS,
        decision_surface_authorization_status=FIXED_AUTH,
        trust_report_bypass_status=FIXED_BYPASS,
        recommendation_authorization_status=FIXED_AUTH,
        catalog_authorization_status=FIXED_AUTH,
        production_readout_authorization_status=FIXED_AUTH,
        production_compatibility_authorization_status=FIXED_AUTH,
        claim_authorization_status=FIXED_AUTH,
        method_promotion_status=FIXED_PROMO,
        instrument_promotion_status=FIXED_PROMO,
        spend_roi_authorization_status=FIXED_AUTH,
        causal_lift_authorization_status=FIXED_AUTH,
        statistical_claim_authorization_status=FIXED_AUTH,
        consumer_status=MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_READY_FOR_GOVERNANCE_CONTEXT,
        routing_hint=MIPMethodPromotionHandoffRoutingHint.ROUTE_TO_GOVERNANCE_CONTEXT_DISPLAY,
        lineage=record_lineage,
        created_from_handoff=True,
    )

    return MIPMethodPromotionHandoffConsumerRuntimeOutput(
        consumer_record=record,
        consumer_status=MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_READY_FOR_GOVERNANCE_CONTEXT,
        validation_errors=(),
        validation_warnings=tuple(warnings),
        routing_hint=MIPMethodPromotionHandoffRoutingHint.ROUTE_TO_GOVERNANCE_CONTEXT_DISPLAY,
        accepted_for_governance_context=True,
        rejected_for_decisioning=True,
        lineage=record_lineage,
    )


def serialize_method_promotion_handoff_consumer_record(
    record: MIPMethodPromotionHandoffConsumerRecord,
) -> dict[str, Any]:
    """Serialize a consumer record to a JSON-safe dict."""

    data = record.model_dump(mode="json")
    # Ensure tuples/lists are lists and enums are strings (mode=json already does this).
    for key in (
        "missing_evidence",
        "blockers",
        "warnings",
        "prohibited_actions",
        "mip_allowed_uses",
        "mip_prohibited_uses",
        "consumer_allowed_actions",
        "consumer_blocked_actions",
    ):
        value = data.get(key)
        if isinstance(value, tuple):
            data[key] = list(value)
    return data


__all__ = [
    "ARTIFACT_ID",
    "CONSUMER_ALLOWED_ACTIONS",
    "CONSUMER_BLOCKED_ACTIONS",
    "FIXED_AUTH",
    "FIXED_BYPASS",
    "FIXED_PROMO",
    "MIPMethodPromotionHandoffAuthorizationStatus",
    "MIPMethodPromotionHandoffBypassStatus",
    "MIPMethodPromotionHandoffConsumerRecord",
    "MIPMethodPromotionHandoffConsumerRuntimeInput",
    "MIPMethodPromotionHandoffConsumerRuntimeOutput",
    "MIPMethodPromotionHandoffConsumerStatus",
    "MIPMethodPromotionHandoffPromotionStatus",
    "MIPMethodPromotionHandoffRoutingHint",
    "serialize_method_promotion_handoff_consumer_record",
    "validate_and_normalize_method_promotion_handoff",
]
