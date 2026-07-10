"""Deterministic MMM planning-response renderer (envelope → safe sections)."""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field, field_validator

from mip.contracts.base import ContractBaseModel
from mip.contracts.mmm_planning_answer_eligibility import MMMPlanningAnswerMode
from mip.contracts.mmm_planning_answer_envelope import (
    MMMPlanningAnswerClaimStatement,
    MMMPlanningAnswerEnvelope,
    MMMPlanningAnswerEnvelopeStatus,
    MMMPlanningAnswerEvidenceReference,
)

RECOMMENDED_NEXT_MMM_PLANNING_RESPONSE_RENDERER_CHECKPOINT_AUDIT_ARTIFACT = (
    "MIP_MMM_PLANNING_RESPONSE_RENDERER_CHECKPOINT_AUDIT_001"
)


class MMMPlanningResponseRenderIssueCode(StrEnum):
    """Typed issue codes for deterministic planning-response rendering."""

    ENVELOPE_PRESENT = "envelope_present"
    ENVELOPE_MISSING = "envelope_missing"
    STATUS_RENDERED = "status_rendered"
    ANSWER_MODE_RENDERED = "answer_mode_rendered"
    CAN_SAY_RENDERED = "can_say_rendered"
    CANNOT_SAY_RENDERED = "cannot_say_rendered"
    CAVEATS_RENDERED = "caveats_rendered"
    REQUIRED_GATES_RENDERED = "required_gates_rendered"
    BLOCKED_REASONS_RENDERED = "blocked_reasons_rendered"
    DEFERRED_REASONS_RENDERED = "deferred_reasons_rendered"
    HUMAN_REVIEW_RENDERED = "human_review_rendered"
    EVIDENCE_REFERENCES_RENDERED = "evidence_references_rendered"
    LINEAGE_PRESERVED = "lineage_preserved"
    UNSUPPORTED_NUMERIC_CLAIMS_NOT_RENDERED = "unsupported_numeric_claims_not_rendered"
    RECOMMENDATION_CLAIMS_NOT_RENDERED_WITHOUT_GATE = (
        "recommendation_claims_not_rendered_without_gate"
    )
    SCENARIO_SIMULATION_CLAIMS_NOT_RENDERED_WITHOUT_DECISION_SURFACE = (
        "scenario_simulation_claims_not_rendered_without_decision_surface"
    )
    NO_LLM_CALL = "no_llm_call"  # No LLM
    NO_DECISION_SURFACE_CONSTRUCTION = "no_decision_surface_construction"
    NO_DECISION_SURFACE_EXECUTION = "no_decision_surface_execution"
    NO_TRUST_REPORT_CONSTRUCTION = "no_trust_report_construction"
    NO_TRUST_REPORT_BYPASS = "no_trust_report_bypass"
    NO_RECOMMENDATION_CONTRACT_GENERATION = "no_recommendation_contract_generation"
    NO_RECOMMENDATION_GENERATION = "no_recommendation_generation"
    NO_OPTIMIZER_EXECUTION = "no_optimizer_execution"  # must not
    NO_SIMULATOR_EXECUTION = "no_simulator_execution"  # must not
    NO_BUDGET_ALLOCATION_CALCULATION = "no_budget_allocation_calculation"
    NO_ROI_ROAS_LIFT_INCREMENTALITY_CALCULATION = "no_roi_roas_lift_incrementality_calculation"
    NO_ARTIFACT_LOADING = "no_artifact_loading"
    NO_MODEL_LOADING = "no_model_loading"
    NO_MODEL_EXECUTION = "no_model_execution"
    NO_MMM_FITTING = "no_mmm_fitting"
    NO_CLAIM_AUTHORIZATION = "no_claim_authorization"
    NO_LLM_PROVIDER_BEHAVIOR_CHANGE = "no_llm_provider_behavior_change"  # No LLM


_BOUNDARY_ISSUES = (
    MMMPlanningResponseRenderIssueCode.LINEAGE_PRESERVED,
    MMMPlanningResponseRenderIssueCode.UNSUPPORTED_NUMERIC_CLAIMS_NOT_RENDERED,
    MMMPlanningResponseRenderIssueCode.RECOMMENDATION_CLAIMS_NOT_RENDERED_WITHOUT_GATE,
    MMMPlanningResponseRenderIssueCode.SCENARIO_SIMULATION_CLAIMS_NOT_RENDERED_WITHOUT_DECISION_SURFACE,
    MMMPlanningResponseRenderIssueCode.NO_LLM_CALL,
    MMMPlanningResponseRenderIssueCode.NO_DECISION_SURFACE_CONSTRUCTION,
    MMMPlanningResponseRenderIssueCode.NO_DECISION_SURFACE_EXECUTION,
    MMMPlanningResponseRenderIssueCode.NO_TRUST_REPORT_CONSTRUCTION,
    MMMPlanningResponseRenderIssueCode.NO_TRUST_REPORT_BYPASS,
    MMMPlanningResponseRenderIssueCode.NO_RECOMMENDATION_CONTRACT_GENERATION,
    MMMPlanningResponseRenderIssueCode.NO_RECOMMENDATION_GENERATION,
    MMMPlanningResponseRenderIssueCode.NO_OPTIMIZER_EXECUTION,
    MMMPlanningResponseRenderIssueCode.NO_SIMULATOR_EXECUTION,
    MMMPlanningResponseRenderIssueCode.NO_BUDGET_ALLOCATION_CALCULATION,
    MMMPlanningResponseRenderIssueCode.NO_ROI_ROAS_LIFT_INCREMENTALITY_CALCULATION,
    MMMPlanningResponseRenderIssueCode.NO_ARTIFACT_LOADING,
    MMMPlanningResponseRenderIssueCode.NO_MODEL_LOADING,
    MMMPlanningResponseRenderIssueCode.NO_MODEL_EXECUTION,
    MMMPlanningResponseRenderIssueCode.NO_MMM_FITTING,
    MMMPlanningResponseRenderIssueCode.NO_CLAIM_AUTHORIZATION,
    MMMPlanningResponseRenderIssueCode.NO_LLM_PROVIDER_BEHAVIOR_CHANGE,
)


class MMMPlanningResponseSection(ContractBaseModel):
    """One deterministic user-facing response section."""

    section_id: str
    title: str
    items: list[str] = Field(default_factory=list)
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)

    @field_validator("section_id", "title")
    @classmethod
    def required_text_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "section_id and title cannot be empty"
            raise ValueError(msg)
        return value


class MMMPlanningRenderedResponse(ContractBaseModel):
    """Deterministic rendered planning response from an answer envelope."""

    request_id: str
    status: MMMPlanningAnswerEnvelopeStatus
    answer_mode: MMMPlanningAnswerMode
    answer_allowed: bool = False
    human_review_required: bool = False
    sections: list[MMMPlanningResponseSection] = Field(default_factory=list)
    issues: list[MMMPlanningResponseRenderIssueCode] = Field(default_factory=list)
    lineage: dict[str, str] = Field(default_factory=dict)
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)

    @field_validator("request_id")
    @classmethod
    def request_id_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "request_id cannot be empty"
            raise ValueError(msg)
        return value


def render_mmm_planning_response(
    envelope: MMMPlanningAnswerEnvelope | None,
) -> MMMPlanningRenderedResponse:
    """Render an MMM planning-answer envelope into deterministic safe sections.

    Metadata/text only. Does not call an LLM, compute metrics, or construct
    DecisionSurface / TrustReport / RecommendationContract payloads.
    """
    issues: list[MMMPlanningResponseRenderIssueCode] = list(_BOUNDARY_ISSUES)

    if envelope is None:
        issues.append(MMMPlanningResponseRenderIssueCode.ENVELOPE_MISSING)
        issues.append(MMMPlanningResponseRenderIssueCode.STATUS_RENDERED)
        issues.append(MMMPlanningResponseRenderIssueCode.CANNOT_SAY_RENDERED)
        issues.append(MMMPlanningResponseRenderIssueCode.REQUIRED_GATES_RENDERED)
        return MMMPlanningRenderedResponse(
            request_id="missing-envelope",
            status=MMMPlanningAnswerEnvelopeStatus.UNKNOWN,
            answer_mode=MMMPlanningAnswerMode.BLOCKED,
            answer_allowed=False,
            human_review_required=False,
            sections=[
                _section(
                    section_id="status",
                    title="Status",
                    items=["missing envelope"],
                ),
                _section(
                    section_id="answer_mode",
                    title="Answer mode",
                    items=[_enum_value(MMMPlanningAnswerMode.BLOCKED)],
                ),
                _section(
                    section_id="can_say",
                    title="What I can say",
                    items=["No can-say statements available without an envelope."],
                ),
                _section(
                    section_id="cannot_say",
                    title="What I cannot say",
                    items=[
                        "Cannot answer without a planning-answer envelope.",
                        (
                            "Cannot report ROI, ROAS, lift, or incrementality unless "
                            "supplied by an approved artifact."
                        ),
                        (
                            "Cannot recommend budget allocation without "
                            "RecommendationContract gate."
                        ),
                    ],
                ),
                _section(
                    section_id="caveats",
                    title="Caveats",
                    items=["No caveats supplied."],
                ),
                _section(
                    section_id="required_gates",
                    title="Required gates",
                    items=["Build or provide a planning-answer envelope."],
                ),
                _section(
                    section_id="blocked_deferred_reasons",
                    title="Blocked/deferred reasons",
                    items=["Envelope missing; response blocked."],
                ),
                _section(
                    section_id="human_review_required",
                    title="Human review required",
                    items=["No"],
                ),
                _section(
                    section_id="evidence_references",
                    title="Evidence references",
                    items=["No evidence references supplied."],
                ),
            ],
            issues=list(dict.fromkeys(issues)),
            lineage={"planning_response_renderer_stage": "mmm_planning_response_renderer"},
            metadata={
                "deterministic_rendering_only": True,
                "no_llm_call": True,  # No LLM
                "no_recommendation_generated": True,
            },
        )

    issues.append(MMMPlanningResponseRenderIssueCode.ENVELOPE_PRESENT)
    lineage = {
        **envelope.lineage,
        "planning_response_renderer_stage": "mmm_planning_response_renderer",
        "source_envelope_request_id": envelope.request_id,
    }

    sections = [
        _render_status_section(envelope, issues),
        _render_answer_mode_section(envelope, issues),
        _render_can_say_section(envelope, issues),
        _render_cannot_say_section(envelope, issues),
        _render_caveats_section(envelope, issues),
        _render_required_gates_section(envelope, issues),
        _render_blocked_deferred_section(envelope, issues),
        _render_human_review_section(envelope, issues),
        _render_evidence_section(envelope, issues),
    ]

    return MMMPlanningRenderedResponse(
        request_id=envelope.request_id,
        status=envelope.status,
        answer_mode=envelope.answer_mode,
        answer_allowed=envelope.answer_allowed,
        human_review_required=envelope.human_review_required,
        sections=sections,
        issues=list(dict.fromkeys(issues)),
        lineage=lineage,
        metadata={
            **envelope.metadata,
            "deterministic_rendering_only": True,
            "no_llm_call": True,  # No LLM
            "no_recommendation_generated": True,
            "question_class": _enum_value(envelope.question_class),
        },
    )


def summarize_mmm_planning_rendered_response(
    response: MMMPlanningRenderedResponse,
) -> dict[str, object]:
    """Return count/status summary only (no recommendation wording)."""
    can_say_section = _find_section(response, "can_say")
    cannot_say_section = _find_section(response, "cannot_say")
    evidence_section = _find_section(response, "evidence_references")
    return {
        "status": _enum_value(response.status),
        "answer_mode": _enum_value(response.answer_mode),
        "answer_allowed": response.answer_allowed,
        "human_review_required": response.human_review_required,
        "section_count": len(response.sections),
        "can_say_item_count": len(can_say_section.items) if can_say_section else 0,
        "cannot_say_item_count": len(cannot_say_section.items) if cannot_say_section else 0,
        "evidence_reference_count": _evidence_count(evidence_section),
        "issue_count": len(response.issues),
    }


def _render_status_section(
    envelope: MMMPlanningAnswerEnvelope,
    issues: list[MMMPlanningResponseRenderIssueCode],
) -> MMMPlanningResponseSection:
    issues.append(MMMPlanningResponseRenderIssueCode.STATUS_RENDERED)
    return _section(
        section_id="status",
        title="Status",
        items=[_enum_value(envelope.status).upper()],
    )


def _render_answer_mode_section(
    envelope: MMMPlanningAnswerEnvelope,
    issues: list[MMMPlanningResponseRenderIssueCode],
) -> MMMPlanningResponseSection:
    issues.append(MMMPlanningResponseRenderIssueCode.ANSWER_MODE_RENDERED)
    return _section(
        section_id="answer_mode",
        title="Answer mode",
        items=[_enum_value(envelope.answer_mode).upper()],
    )


def _render_can_say_section(
    envelope: MMMPlanningAnswerEnvelope,
    issues: list[MMMPlanningResponseRenderIssueCode],
) -> MMMPlanningResponseSection:
    issues.append(MMMPlanningResponseRenderIssueCode.CAN_SAY_RENDERED)
    items = [_format_claim(claim) for claim in envelope.can_say]
    if not items:
        items = ["No can-say statements supplied."]
    return _section(section_id="can_say", title="What I can say", items=items)


def _render_cannot_say_section(
    envelope: MMMPlanningAnswerEnvelope,
    issues: list[MMMPlanningResponseRenderIssueCode],
) -> MMMPlanningResponseSection:
    issues.append(MMMPlanningResponseRenderIssueCode.CANNOT_SAY_RENDERED)
    items = [_format_claim(claim) for claim in envelope.cannot_say]
    if not items:
        items = ["No cannot-say statements supplied."]
    return _section(section_id="cannot_say", title="What I cannot say", items=items)


def _render_caveats_section(
    envelope: MMMPlanningAnswerEnvelope,
    issues: list[MMMPlanningResponseRenderIssueCode],
) -> MMMPlanningResponseSection:
    issues.append(MMMPlanningResponseRenderIssueCode.CAVEATS_RENDERED)
    items = list(envelope.caveats) if envelope.caveats else ["No caveats supplied."]
    return _section(section_id="caveats", title="Caveats", items=items)


def _render_required_gates_section(
    envelope: MMMPlanningAnswerEnvelope,
    issues: list[MMMPlanningResponseRenderIssueCode],
) -> MMMPlanningResponseSection:
    issues.append(MMMPlanningResponseRenderIssueCode.REQUIRED_GATES_RENDERED)
    items: list[str] = []
    if envelope.decision_surface_required:
        items.append("DecisionSurface gate/reference required.")
    if envelope.trust_review_required:
        items.append("Trust review required.")
    if envelope.recommendation_contract_required:
        items.append("RecommendationContract gate/reference required.")
    for gate in envelope.gate_references:
        detail = f"Gate reference: {gate.gate_name} status={gate.gate_status}"
        if gate.passed:
            detail += " passed=true"
        elif gate.required:
            detail += " required=true"
        if gate.blocked_reasons:
            detail += f" blocked_reasons={';'.join(gate.blocked_reasons)}"
        items.append(detail)
    if not items:
        items = ["No required gates supplied."]
    return _section(section_id="required_gates", title="Required gates", items=items)


def _render_blocked_deferred_section(
    envelope: MMMPlanningAnswerEnvelope,
    issues: list[MMMPlanningResponseRenderIssueCode],
) -> MMMPlanningResponseSection:
    items: list[str] = []
    if envelope.blocked_reasons:
        issues.append(MMMPlanningResponseRenderIssueCode.BLOCKED_REASONS_RENDERED)
        items.extend(f"Blocked: {reason}" for reason in envelope.blocked_reasons)
    else:
        items.append("No blocked reasons supplied.")
    if envelope.deferred_reasons:
        issues.append(MMMPlanningResponseRenderIssueCode.DEFERRED_REASONS_RENDERED)
        items.extend(f"Deferred: {reason}" for reason in envelope.deferred_reasons)
    else:
        items.append("No deferred reasons supplied.")
    return _section(
        section_id="blocked_deferred_reasons",
        title="Blocked/deferred reasons",
        items=items,
    )


def _render_human_review_section(
    envelope: MMMPlanningAnswerEnvelope,
    issues: list[MMMPlanningResponseRenderIssueCode],
) -> MMMPlanningResponseSection:
    issues.append(MMMPlanningResponseRenderIssueCode.HUMAN_REVIEW_RENDERED)
    return _section(
        section_id="human_review_required",
        title="Human review required",
        items=["Yes" if envelope.human_review_required else "No"],
        metadata={"human_review_required": envelope.human_review_required},
    )


def _render_evidence_section(
    envelope: MMMPlanningAnswerEnvelope,
    issues: list[MMMPlanningResponseRenderIssueCode],
) -> MMMPlanningResponseSection:
    issues.append(MMMPlanningResponseRenderIssueCode.EVIDENCE_REFERENCES_RENDERED)
    items = [_format_evidence(ref) for ref in envelope.evidence_references]
    if not items:
        items = ["No evidence references supplied."]
    return _section(
        section_id="evidence_references",
        title="Evidence references",
        items=items,
        metadata={"evidence_reference_count": len(envelope.evidence_references)},
    )


def _format_claim(claim: MMMPlanningAnswerClaimStatement) -> str:
    text = claim.statement
    if claim.required_gate:
        text = f"{text} (required_gate={claim.required_gate})"
    return text


def _format_evidence(ref: MMMPlanningAnswerEvidenceReference) -> str:
    parts = [
        f"{_enum_value(ref.evidence_type).upper()}: {ref.evidence_id}",
    ]
    if ref.status:
        parts.append(f"status={ref.status}")
    if ref.gate_name:
        parts.append(f"gate={ref.gate_name}")
    if ref.artifact_id:
        parts.append(f"artifact_id={ref.artifact_id}")
    if ref.source_id:
        parts.append(f"source_id={ref.source_id}")
    return " | ".join(parts)


def _section(
    *,
    section_id: str,
    title: str,
    items: list[str],
    metadata: dict[str, str | int | float | bool] | None = None,
) -> MMMPlanningResponseSection:
    return MMMPlanningResponseSection(
        section_id=section_id,
        title=title,
        items=list(items),
        metadata=dict(metadata or {}),
    )


def _find_section(
    response: MMMPlanningRenderedResponse,
    section_id: str,
) -> MMMPlanningResponseSection | None:
    for section in response.sections:
        if section.section_id == section_id:
            return section
    return None


def _evidence_count(section: MMMPlanningResponseSection | None) -> int:
    if section is None:
        return 0
    count = section.metadata.get("evidence_reference_count")
    if isinstance(count, int):
        return count
    if section.items == ["No evidence references supplied."]:
        return 0
    return len(section.items)


def _enum_value(value: object) -> str:
    return value.value if hasattr(value, "value") else str(value)
