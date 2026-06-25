"""Pure display helpers for the P7 local workflow UI shell."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel

from mip.contracts.advisory import ColdStartAdvisoryPlan
from mip.contracts.calibration_intake import CalibrationMappingReport
from mip.contracts.llm_provider import LLMExplanationPlan, LLMProviderConfig
from mip.contracts.workflow_readiness import BaseWorkflowReadinessReport

_STATUS_BADGES = {
    "ready": "[READY]",
    "ready_with_warnings": "[READY WITH WARNINGS]",
    "needs_more_data": "[NEEDS MORE DATA]",
    "blocked": "[BLOCKED]",
    "not_applicable": "[NOT APPLICABLE]",
    "mapped": "[MAPPED]",
    "incompatible": "[INCOMPATIBLE]",
    "draft": "[DRAFT]",
    "advisory_plan_ready": "[ADVISORY PLAN READY]",
    "needs_tracking_setup": "[NEEDS TRACKING SETUP]",
    "deterministic_only": "[DETERMINISTIC ONLY]",
    "needs_provider": "[NEEDS PROVIDER]",
    "future_only": "[FUTURE ONLY]",
}

BLOCKED_CLAIM_TOPICS: tuple[str, ...] = (
    "ROI estimates or ROI-proven channel claims",
    "Causal lift or incremental impact claims",
    "Optimal media mix or optimal allocation",
    "Budget optimization or budget recommendations",
    "Power, MDE, or design-validity certification",
    "Matched markets or treatment/control assignment",
    "Decision approval or production authorization",
)

DETERMINISTIC_MODE_LABEL = "Deterministic"
DETERMINISTIC_MODE_DESCRIPTION = (
    "No LLM is being used. Outputs come from MIP contracts, deterministic helpers, "
    "and governed report objects."
)


def _enum_value(value: object) -> str:
    if isinstance(value, Enum):
        return str(value.value)
    if isinstance(value, str):
        return value
    return str(value)


def format_status_badge(status: object) -> str:
    """Format a workflow or mapping status for display."""
    normalized = _enum_value(status).strip().lower().replace(" ", "_")
    return _STATUS_BADGES.get(normalized, f"[{_enum_value(status).upper()}]")


def summarize_warnings(warnings: list[str] | None) -> list[str]:
    """Return warnings as a stable display list."""
    if not warnings:
        return ["None"]
    return list(warnings)


def summarize_blocking_reasons(blocking_reasons: list[str] | None) -> list[str]:
    """Return blocking reasons as a stable display list."""
    if not blocking_reasons:
        return ["None"]
    return list(blocking_reasons)


def render_allowed_blocked_steps(
    allowed_next_steps: list[str] | None,
    blocked_next_steps: list[str] | None,
) -> dict[str, list[str]]:
    """Build allowed/blocked next-step display sections."""
    return {
        "allowed_next_steps": list(allowed_next_steps or []) or ["None"],
        "blocked_next_steps": list(blocked_next_steps or []) or ["None"],
    }


def contract_to_display_dict(model: BaseModel) -> dict[str, Any]:
    """Convert a Pydantic contract to a JSON-serializable display dictionary."""
    return model.model_dump(mode="json")


def advisory_plan_to_display_dict(plan: ColdStartAdvisoryPlan) -> dict[str, Any]:
    """Render a cold-start advisory plan for UI display."""
    hypotheses = [
        {
            "channel": _enum_value(hypothesis.channel_candidate),
            "claim_type": _enum_value(hypothesis.claim_type),
            "evidence_level": _enum_value(hypothesis.evidence_level),
            "summary": hypothesis.hypothesis_text,
            "warnings": list(hypothesis.warnings),
        }
        for hypothesis in plan.channel_hypotheses
    ]
    steps = render_allowed_blocked_steps(plan.allowed_next_steps, plan.blocked_next_steps)
    evidence_levels: list[str] = []
    if plan.channel_suitability is not None:
        evidence_levels = [_enum_value(level) for level in plan.channel_suitability.evidence_levels]
    tracking = plan.tracking_checklist
    return {
        "plan_id": plan.plan_id,
        "status": _enum_value(plan.status),
        "status_badge": format_status_badge(plan.status),
        "evidence_mode": _enum_value(plan.evidence_mode),
        "claim_types": [_enum_value(claim) for claim in plan.claim_types],
        "evidence_levels": evidence_levels,
        "channel_hypotheses": hypotheses,
        "tracking_checklist": {
            "required_items": list(tracking.required_items) if tracking else [],
            "missing_items": list(tracking.missing_items) if tracking else [],
        },
        "measurement_plan": contract_to_display_dict(plan.measurement_plan)
        if plan.measurement_plan is not None
        else {},
        "learning_agenda": contract_to_display_dict(plan.learning_agenda)
        if plan.learning_agenda is not None
        else {},
        "warnings": summarize_warnings(plan.warnings),
        "blocking_reasons": summarize_blocking_reasons(plan.blocking_reasons),
        **steps,
        "advisory_disclaimer": (
            "This is advisory-only and hypothesis-to-test. "
            "It is not ROI-proven and not a causal recommendation."
        ),
        "blocked_claim_topics": list(BLOCKED_CLAIM_TOPICS),
    }


def readiness_report_to_display_dict(report: BaseWorkflowReadinessReport) -> dict[str, Any]:
    """Render a workflow readiness report card for UI display."""
    payload = contract_to_display_dict(report)
    steps = render_allowed_blocked_steps(
        report.allowed_next_steps,
        report.blocked_next_steps,
    )
    payload.update(
        {
            "status_badge": format_status_badge(report.status),
            "report_type_label": _enum_value(report.report_type).replace("_", " ").title(),
            "warnings": summarize_warnings(report.warnings),
            "blocking_reasons": summarize_blocking_reasons(report.blocking_reasons),
            **steps,
        }
    )
    return payload


def calibration_mapping_to_display_dict(
    report: CalibrationMappingReport,
    *,
    signal_id: str | None = None,
) -> dict[str, Any]:
    """Render a calibration mapping report for UI display."""
    steps = render_allowed_blocked_steps(report.allowed_next_steps, report.blocked_next_steps)
    metrics: dict[str, Any] = {}
    if report.mapped_signal is not None:
        metrics = dict(report.mapped_signal.diagnostics.metrics)
    lineage = {
        "source_evidence_id": report.mapped_signal.source_evidence_id
        if report.mapped_signal is not None
        else None,
        "source_artifact_id": metrics.get("source_artifact_id"),
        "source_experiment_id": metrics.get("source_experiment_id"),
        "source_readout_id": metrics.get("source_readout_id"),
        "target_model_id": report.mapped_signal.target_model_id
        if report.mapped_signal is not None
        else None,
        "confidence_tier": _enum_value(report.mapped_signal.confidence_tier)
        if report.mapped_signal is not None
        else None,
    }
    return {
        "report_id": report.report_id,
        "status": _enum_value(report.status),
        "status_badge": format_status_badge(report.status),
        "mapped_signal_id": signal_id or report.mapped_signal_id,
        "missing_fields": list(report.missing_fields) or ["None"],
        "incompatible_fields": list(report.incompatible_fields) or ["None"],
        "warnings": summarize_warnings(report.warnings),
        "blocking_reasons": summarize_blocking_reasons(report.blocking_reasons),
        "lineage": lineage,
        **steps,
        "calibration_disclaimer": (
            "This does not execute MMM calibration, estimate effects, or certify causality."
        ),
        "blocked_claim_topics": list(BLOCKED_CLAIM_TOPICS),
    }


def intake_recommendation_to_display_dict(
    label: str,
    recommendation: Any,
    session: Any,
) -> dict[str, Any]:
    """Render an intake path recommendation example."""
    steps = render_allowed_blocked_steps(
        recommendation.allowed_next_steps,
        recommendation.blocked_next_steps,
    )
    return {
        "label": label,
        "session_id": session.session_id,
        "business_question": session.business_question,
        "workflow_kind": _enum_value(session.workflow_kind),
        "recommended_path": _enum_value(recommendation.recommended_path),
        "status": _enum_value(recommendation.status),
        "status_badge": format_status_badge(recommendation.status),
        "why_this_path": recommendation.why_this_path,
        "why_other_paths_blocked": list(recommendation.why_other_paths_blocked) or ["None"],
        "warnings": summarize_warnings(recommendation.warnings),
        "blocking_reasons": summarize_blocking_reasons(recommendation.blocking_reasons),
        **steps,
    }


def mode_banner() -> dict[str, str]:
    """Active provider/mode banner for the UI shell."""
    return {
        "mode": DETERMINISTIC_MODE_LABEL,
        "description": DETERMINISTIC_MODE_DESCRIPTION,
    }


def format_provider_mode(config: LLMProviderConfig) -> dict[str, str]:
    """Format provider mode configuration for display."""
    return {
        "mode": _enum_value(config.mode),
        "status": _enum_value(config.status),
        "provider_name": config.provider_name or "none",
        "model_name": config.model_name or "none",
        "is_experimental": str(config.is_experimental),
        "requires_user_key": str(config.requires_user_key),
        "requires_local_runtime": str(config.requires_local_runtime),
    }


def format_explanation_plan(plan: LLMExplanationPlan) -> dict[str, Any]:
    """Format an LLM explanation plan for display (not a generated answer)."""
    return {
        "plan_id": plan.plan_id,
        "status": _enum_value(plan.status),
        "status_badge": format_status_badge(plan.status),
        "provider_mode": _enum_value(plan.provider_mode),
        "use_case": _enum_value(plan.use_case),
        "allowed_inputs": list(plan.allowed_inputs),
        "blocked_inputs": list(plan.blocked_inputs),
        "required_labels": list(plan.required_labels),
        "required_warnings": summarize_warnings(plan.required_warnings),
        "blocked_output_claim_types": list(plan.blocked_output_claim_types),
        "blocking_reasons": summarize_blocking_reasons(plan.blocking_reasons),
        "system_guardrails": list(plan.system_guardrails),
    }
