"""Metadata-only MMM LLM response template from application package.

Consumes MMMResponseBoundaryApplicationOutput and builds instruction slots for a
future prompt-assembly layer.

Does not execute prompts, call providers, assemble provider-ready prompts,
generate user-facing answers, construct DecisionSurface / TrustReport /
RecommendationContract, run optimizer/simulator, or authorize claims.
"""

from __future__ import annotations

from collections.abc import Mapping
from enum import StrEnum
from typing import Any

from pydantic import Field, field_validator, model_validator

from mip.contracts.base import ContractBaseModel
from mip.llm.mmm_response_boundary_application import (
    MMMResponseBoundaryApplicationOutput,
)

ARTIFACT_ID = "MIP_MMM_LLM_RESPONSE_TEMPLATE_FROM_APPLICATION_PACKAGE_001"
TEMPLATE_MODULE = "mip.llm.mmm_response_template"
RECOMMENDED_NEXT_ARTIFACT = "MIP_MMM_LLM_RESPONSE_TEMPLATE_CHECKPOINT_AUDIT_001"

_FORBIDDEN_TEMPLATE_FIELD_NAMES = frozenset(
    {
        "prompt",
        "system_prompt",
        "developer_prompt",
        "rendered_prompt",
        "provider",
        "model",
        "completion",
        "message",
        "answer",
        "final_answer",
        "spend_delta",
        "delta_mu",
        "lift",
        "roi",
        "roas",
        "incrementality",
        "optimal_budget",
        "marginal_roi",
        "recommended_budget",
        "recommendation",
        "response_boundary",
        "llm_response_boundary",
        "boundary",
    }
)

_SYSTEM_INSTRUCTION = (
    "Use only the supplied application package slots. "
    "Do not infer from raw MMM internals or lower-level boundaries. "
    "Do not use LLMExplanationPlan as a parallel MMM prompt path."
)

_DEVELOPER_INSTRUCTION = (
    "Preserve cannot_say, gates, deferred/unsupported status, human review, "
    "provenance, and lineage. "
    "Do not add recommendations, ROI/ROAS/lift/incrementality, "
    "optimizer/simulator outputs, DecisionSurface output, TrustReport claims, "
    "or RecommendationContract claims. "
    "When not ready for prompt assembly, produce only refusal/defer instructions."
)

_BASE_NON_EXECUTION_ISSUES: tuple[str, ...] = (
    "NO_PROMPT_EXECUTION",
    "NO_PROVIDER_INTEGRATION",
    "NO_LLM_CALL",
    "NO_ORCHESTRATION_ROUTING",
    "NO_USER_FACING_ANSWER_GENERATION",
    "NO_DECISION_SURFACE_CONSTRUCTION",
    "NO_DECISION_SURFACE_EXECUTION",
    "NO_TRUST_REPORT_CONSTRUCTION",
    "NO_TRUST_REPORT_BYPASS",
    "NO_RECOMMENDATION_CONTRACT_GENERATION",
    "NO_RECOMMENDATION_GENERATION",
    "NO_OPTIMIZER_EXECUTION",
    "NO_SIMULATOR_EXECUTION",
    "NO_BUDGET_ALLOCATION_CALCULATION",
    "NO_ROI_ROAS_LIFT_INCREMENTALITY_CALCULATION",
    "NO_ARTIFACT_LOADING",
    "NO_MODEL_LOADING",
    "NO_MODEL_EXECUTION",
    "NO_MMM_FITTING",
    "NO_CLAIM_AUTHORIZATION",
    "NO_LLM_PROVIDER_BEHAVIOR_CHANGE",
    "LLM_EXPLANATION_PLAN_PARALLEL_PATH_BLOCKED",
    "RAW_BOUNDARY_DIRECT_INPUT_BLOCKED",
)


class MMMResponseTemplateStatus(StrEnum):
    """Template packaging status (metadata only)."""

    READY_FOR_REFUSAL_OR_DEFER_TEMPLATE = "READY_FOR_REFUSAL_OR_DEFER_TEMPLATE"
    READY_FOR_PROMPT_ASSEMBLY = "READY_FOR_PROMPT_ASSEMBLY"
    BLOCKED = "BLOCKED"
    DEFERRED = "DEFERRED"
    HUMAN_REVIEW_REQUIRED = "HUMAN_REVIEW_REQUIRED"
    UNKNOWN = "UNKNOWN"


class MMMResponseTemplateSlotType(StrEnum):
    """Instruction slot kinds."""

    SYSTEM_INSTRUCTION = "SYSTEM_INSTRUCTION"
    DEVELOPER_INSTRUCTION = "DEVELOPER_INSTRUCTION"
    CAN_SAY_SECTION = "CAN_SAY_SECTION"
    CANNOT_SAY_SECTION = "CANNOT_SAY_SECTION"
    SAFE_RESPONSE_GUIDANCE = "SAFE_RESPONSE_GUIDANCE"
    REFUSAL_RULE = "REFUSAL_RULE"
    DEFER_RULE = "DEFER_RULE"
    GATE_REQUIREMENT = "GATE_REQUIREMENT"
    PROVENANCE_REFERENCE = "PROVENANCE_REFERENCE"
    LINEAGE_REFERENCE = "LINEAGE_REFERENCE"
    READINESS_FLAG = "READINESS_FLAG"
    HUMAN_REVIEW_REQUIREMENT = "HUMAN_REVIEW_REQUIREMENT"
    FORBIDDEN_ADDITION = "FORBIDDEN_ADDITION"


class MMMResponseTemplateMode(StrEnum):
    """Template operating mode."""

    NORMAL_EXPLANATION = "NORMAL_EXPLANATION"
    REFUSAL_ONLY = "REFUSAL_ONLY"
    DEFER_ONLY = "DEFER_ONLY"
    BLOCKED = "BLOCKED"
    UNKNOWN = "UNKNOWN"


class MMMResponseTemplateIssueCode(StrEnum):
    """Deterministic template issue codes."""

    APPLICATION_PACKAGE_PRESENT = "APPLICATION_PACKAGE_PRESENT"
    APPLICATION_PACKAGE_MISSING = "APPLICATION_PACKAGE_MISSING"
    APPLICATION_PACKAGE_NOT_READY_FOR_PROMPT_ASSEMBLY = (
        "APPLICATION_PACKAGE_NOT_READY_FOR_PROMPT_ASSEMBLY"
    )
    REFUSAL_ONLY_TEMPLATE_ALLOWED = "REFUSAL_ONLY_TEMPLATE_ALLOWED"
    NORMAL_PROMPT_ASSEMBLY_BLOCKED = "NORMAL_PROMPT_ASSEMBLY_BLOCKED"
    CAN_SAY_INJECTED = "CAN_SAY_INJECTED"
    CANNOT_SAY_INJECTED = "CANNOT_SAY_INJECTED"
    CANNOT_SAY_PRIORITIZED = "CANNOT_SAY_PRIORITIZED"
    SAFE_RESPONSE_GUIDANCE_INJECTED = "SAFE_RESPONSE_GUIDANCE_INJECTED"
    GATES_INJECTED = "GATES_INJECTED"
    PROVENANCE_INJECTED = "PROVENANCE_INJECTED"
    LINEAGE_INJECTED = "LINEAGE_INJECTED"
    READINESS_FLAGS_INJECTED = "READINESS_FLAGS_INJECTED"
    HUMAN_REVIEW_INJECTED = "HUMAN_REVIEW_INJECTED"
    UNSUPPORTED_DEFERRED_STATUS_INJECTED = "UNSUPPORTED_DEFERRED_STATUS_INJECTED"
    FORBIDDEN_ADDITIONS_INJECTED = "FORBIDDEN_ADDITIONS_INJECTED"
    LLM_EXPLANATION_PLAN_PARALLEL_PATH_BLOCKED = (
        "LLM_EXPLANATION_PLAN_PARALLEL_PATH_BLOCKED"
    )
    RAW_BOUNDARY_DIRECT_INPUT_BLOCKED = "RAW_BOUNDARY_DIRECT_INPUT_BLOCKED"
    READY_FOR_REFUSAL_OR_DEFER_TEMPLATE = "READY_FOR_REFUSAL_OR_DEFER_TEMPLATE"
    READY_FOR_PROMPT_ASSEMBLY = "READY_FOR_PROMPT_ASSEMBLY"
    NO_PROMPT_EXECUTION = "NO_PROMPT_EXECUTION"
    NO_PROVIDER_INTEGRATION = "NO_PROVIDER_INTEGRATION"
    NO_LLM_CALL = "NO_LLM_CALL"
    NO_ORCHESTRATION_ROUTING = "NO_ORCHESTRATION_ROUTING"
    NO_USER_FACING_ANSWER_GENERATION = "NO_USER_FACING_ANSWER_GENERATION"
    NO_DECISION_SURFACE_CONSTRUCTION = "NO_DECISION_SURFACE_CONSTRUCTION"
    NO_DECISION_SURFACE_EXECUTION = "NO_DECISION_SURFACE_EXECUTION"
    NO_TRUST_REPORT_CONSTRUCTION = "NO_TRUST_REPORT_CONSTRUCTION"
    NO_TRUST_REPORT_BYPASS = "NO_TRUST_REPORT_BYPASS"
    NO_RECOMMENDATION_CONTRACT_GENERATION = "NO_RECOMMENDATION_CONTRACT_GENERATION"
    NO_RECOMMENDATION_GENERATION = "NO_RECOMMENDATION_GENERATION"
    NO_OPTIMIZER_EXECUTION = "NO_OPTIMIZER_EXECUTION"
    NO_SIMULATOR_EXECUTION = "NO_SIMULATOR_EXECUTION"
    NO_BUDGET_ALLOCATION_CALCULATION = "NO_BUDGET_ALLOCATION_CALCULATION"
    NO_ROI_ROAS_LIFT_INCREMENTALITY_CALCULATION = (
        "NO_ROI_ROAS_LIFT_INCREMENTALITY_CALCULATION"
    )
    NO_ARTIFACT_LOADING = "NO_ARTIFACT_LOADING"
    NO_MODEL_LOADING = "NO_MODEL_LOADING"
    NO_MODEL_EXECUTION = "NO_MODEL_EXECUTION"
    NO_MMM_FITTING = "NO_MMM_FITTING"
    NO_CLAIM_AUTHORIZATION = "NO_CLAIM_AUTHORIZATION"
    NO_LLM_PROVIDER_BEHAVIOR_CHANGE = "NO_LLM_PROVIDER_BEHAVIOR_CHANGE"


class MMMResponseTemplateInstructionSlot(ContractBaseModel):
    """One metadata-only instruction slot."""

    slot_id: str
    slot_type: str
    content: str
    source: str = "application_package"
    must_include: bool = True
    cannot_omit: bool = False
    must_preserve_verbatim: bool = False
    may_rewrite_lightly: bool = False
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)

    @field_validator("slot_id", "slot_type", "content", "source")
    @classmethod
    def required_text_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "slot_id, slot_type, content, and source cannot be empty"
            raise ValueError(msg)
        return value


class MMMResponseTemplateInput(ContractBaseModel):
    """Input for metadata-only template packaging from an application package."""

    request_id: str
    application_package: MMMResponseBoundaryApplicationOutput | None = None
    user_question: str = ""
    lineage: Mapping[str, Any] = Field(default_factory=dict)
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)

    @field_validator("request_id")
    @classmethod
    def request_id_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "request_id cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def forbid_raw_boundary_input_fields(self) -> MMMResponseTemplateInput:
        for key in self.metadata:
            if key.lower() in {
                "response_boundary",
                "llm_response_boundary",
                "boundary",
            }:
                msg = (
                    "raw boundary fields are not accepted as template metadata; "
                    "consume MMMResponseBoundaryApplicationOutput only"
                )
                raise ValueError(msg)
        return self


class MMMResponseTemplateOutput(ContractBaseModel):
    """Metadata-only template output with instruction slots."""

    request_id: str
    status: str
    mode: str
    ready_for_prompt_assembly: bool = False
    ready_for_refusal_or_defer_template: bool = False
    ready_for_user_facing_answer: bool = False
    instruction_slots: tuple[MMMResponseTemplateInstructionSlot, ...] = ()
    system_instruction_slots: tuple[MMMResponseTemplateInstructionSlot, ...] = ()
    developer_instruction_slots: tuple[MMMResponseTemplateInstructionSlot, ...] = ()
    can_say_slots: tuple[MMMResponseTemplateInstructionSlot, ...] = ()
    cannot_say_slots: tuple[MMMResponseTemplateInstructionSlot, ...] = ()
    safe_response_guidance_slots: tuple[MMMResponseTemplateInstructionSlot, ...] = ()
    refusal_rule_slots: tuple[MMMResponseTemplateInstructionSlot, ...] = ()
    defer_rule_slots: tuple[MMMResponseTemplateInstructionSlot, ...] = ()
    gate_requirement_slots: tuple[MMMResponseTemplateInstructionSlot, ...] = ()
    provenance_reference_slots: tuple[MMMResponseTemplateInstructionSlot, ...] = ()
    lineage_reference_slots: tuple[MMMResponseTemplateInstructionSlot, ...] = ()
    readiness_flag_slots: tuple[MMMResponseTemplateInstructionSlot, ...] = ()
    human_review_slots: tuple[MMMResponseTemplateInstructionSlot, ...] = ()
    forbidden_addition_slots: tuple[MMMResponseTemplateInstructionSlot, ...] = ()
    issues: tuple[str, ...] = ()
    lineage: Mapping[str, Any] = Field(default_factory=dict)
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)

    @field_validator("request_id", "status", "mode")
    @classmethod
    def required_text_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "request_id, status, and mode cannot be empty"
            raise ValueError(msg)
        return value


def build_mmm_response_template_from_application_package(
    request: MMMResponseTemplateInput,
) -> MMMResponseTemplateOutput:
    """Build metadata-only instruction slots from an application package.

    Never executes prompts, calls providers, or flips readiness beyond the
    application package's own flags.
    """

    base_lineage: dict[str, Any] = {
        "artifact_id": ARTIFACT_ID,
        "template_module": TEMPLATE_MODULE,
        "builder": "build_mmm_response_template_from_application_package",
        "prompt_execution_implemented": False,
        "provider_integration_implemented": False,
        "llm_call_implemented": False,
        "orchestration_routing_implemented": False,
        "user_facing_answer_generation_implemented": False,
        "llm_explanation_plan_parallel_path_blocked": True,
        "raw_boundary_direct_input_blocked": True,
        **dict(request.lineage or {}),
    }

    package = request.application_package
    if package is None:
        issues = (
            MMMResponseTemplateIssueCode.APPLICATION_PACKAGE_MISSING.value,
            MMMResponseTemplateIssueCode.RAW_BOUNDARY_DIRECT_INPUT_BLOCKED.value,
            MMMResponseTemplateIssueCode.LLM_EXPLANATION_PLAN_PARALLEL_PATH_BLOCKED.value,
            *_BASE_NON_EXECUTION_ISSUES,
        )
        return MMMResponseTemplateOutput(
            request_id=request.request_id,
            status=MMMResponseTemplateStatus.UNKNOWN.value,
            mode=MMMResponseTemplateMode.UNKNOWN.value,
            ready_for_prompt_assembly=False,
            ready_for_refusal_or_defer_template=False,
            ready_for_user_facing_answer=False,
            issues=tuple(dict.fromkeys(issues)),
            lineage={
                **base_lineage,
                "application_package_present": False,
            },
            metadata=dict(request.metadata),
        )

    return _build_from_package(
        request=request, package=package, base_lineage=base_lineage
    )


def serialize_mmm_response_template_output(
    output: MMMResponseTemplateOutput,
) -> dict[str, object]:
    """Serialize template output to a JSON-safe dict."""

    data = output.model_dump(mode="json")
    for key, value in list(data.items()):
        if isinstance(value, tuple):
            data[key] = list(value)
    return data


def summarize_mmm_response_template_output(
    output: MMMResponseTemplateOutput,
) -> dict[str, object]:
    """Return counts/flags only — no prompt or recommendation wording."""

    return {
        "status": output.status,
        "mode": output.mode,
        "ready_for_prompt_assembly": output.ready_for_prompt_assembly,
        "ready_for_refusal_or_defer_template": (
            output.ready_for_refusal_or_defer_template
        ),
        "ready_for_user_facing_answer": output.ready_for_user_facing_answer,
        "instruction_slot_count": len(output.instruction_slots),
        "can_say_slot_count": len(output.can_say_slots),
        "cannot_say_slot_count": len(output.cannot_say_slots),
        "safe_guidance_slot_count": len(output.safe_response_guidance_slots),
        "refusal_slot_count": len(output.refusal_rule_slots),
        "defer_slot_count": len(output.defer_rule_slots),
        "gate_slot_count": len(output.gate_requirement_slots),
        "provenance_slot_count": len(output.provenance_reference_slots),
        "lineage_slot_count": len(output.lineage_reference_slots),
        "issue_count": len(output.issues),
    }


def _build_from_package(
    *,
    request: MMMResponseTemplateInput,
    package: MMMResponseBoundaryApplicationOutput,
    base_lineage: Mapping[str, Any],
) -> MMMResponseTemplateOutput:
    issues: list[str] = [
        MMMResponseTemplateIssueCode.APPLICATION_PACKAGE_PRESENT.value,
        MMMResponseTemplateIssueCode.RAW_BOUNDARY_DIRECT_INPUT_BLOCKED.value,
        MMMResponseTemplateIssueCode.LLM_EXPLANATION_PLAN_PARALLEL_PATH_BLOCKED.value,
        *_BASE_NON_EXECUTION_ISSUES,
    ]

    can_say = _cannot_say_dominates(package.can_say, package.cannot_say)
    if package.cannot_say:
        issues.append(MMMResponseTemplateIssueCode.CANNOT_SAY_PRIORITIZED.value)

    slots: list[MMMResponseTemplateInstructionSlot] = []
    slot_n = 0

    def _add(
        *,
        slot_type: MMMResponseTemplateSlotType,
        content: str,
        source: str = "application_package",
        must_include: bool = True,
        cannot_omit: bool = False,
        must_preserve_verbatim: bool = False,
        may_rewrite_lightly: bool = False,
        metadata: dict[str, str | int | float | bool] | None = None,
    ) -> MMMResponseTemplateInstructionSlot:
        nonlocal slot_n
        slot_n += 1
        slot = MMMResponseTemplateInstructionSlot(
            slot_id=f"slot-{slot_n:03d}-{slot_type.value.lower()}",
            slot_type=slot_type.value,
            content=content,
            source=source,
            must_include=must_include,
            cannot_omit=cannot_omit,
            must_preserve_verbatim=must_preserve_verbatim,
            may_rewrite_lightly=may_rewrite_lightly,
            metadata=metadata or {},
        )
        slots.append(slot)
        return slot

    _add(
        slot_type=MMMResponseTemplateSlotType.SYSTEM_INSTRUCTION,
        content=_SYSTEM_INSTRUCTION,
        source="template_builder",
        cannot_omit=True,
        must_preserve_verbatim=True,
    )
    _add(
        slot_type=MMMResponseTemplateSlotType.DEVELOPER_INSTRUCTION,
        content=_DEVELOPER_INSTRUCTION,
        source="template_builder",
        cannot_omit=True,
        must_preserve_verbatim=True,
    )

    if package.safe_response_guidance.strip():
        _add(
            slot_type=MMMResponseTemplateSlotType.SAFE_RESPONSE_GUIDANCE,
            content=package.safe_response_guidance,
            cannot_omit=True,
            must_preserve_verbatim=True,
        )
        issues.append(MMMResponseTemplateIssueCode.SAFE_RESPONSE_GUIDANCE_INJECTED.value)

    for item in can_say:
        _add(
            slot_type=MMMResponseTemplateSlotType.CAN_SAY_SECTION,
            content=item,
            may_rewrite_lightly=True,
            metadata={"forbidden_to_expand": True},
        )
    if can_say:
        issues.append(MMMResponseTemplateIssueCode.CAN_SAY_INJECTED.value)

    for item in package.cannot_say:
        _add(
            slot_type=MMMResponseTemplateSlotType.CANNOT_SAY_SECTION,
            content=item,
            cannot_omit=True,
            must_preserve_verbatim=True,
        )
    if package.cannot_say:
        issues.append(MMMResponseTemplateIssueCode.CANNOT_SAY_INJECTED.value)

    for gate in package.required_gates:
        _add(
            slot_type=MMMResponseTemplateSlotType.GATE_REQUIREMENT,
            content=gate,
            cannot_omit=True,
            must_preserve_verbatim=True,
        )
    if package.required_gates:
        issues.append(MMMResponseTemplateIssueCode.GATES_INJECTED.value)

    for capability in package.blocked_capabilities:
        _add(
            slot_type=MMMResponseTemplateSlotType.FORBIDDEN_ADDITION,
            content=f"blocked_capability:{capability}",
            cannot_omit=True,
            must_preserve_verbatim=True,
        )
    if package.blocked_capabilities:
        issues.append(MMMResponseTemplateIssueCode.FORBIDDEN_ADDITIONS_INJECTED.value)

    for reason in package.unsupported_or_deferred_reasons:
        deferred = _looks_deferred(reason)
        _add(
            slot_type=(
                MMMResponseTemplateSlotType.DEFER_RULE
                if deferred
                else MMMResponseTemplateSlotType.REFUSAL_RULE
            ),
            content=reason,
            cannot_omit=True,
            must_preserve_verbatim=True,
        )
    if package.unsupported_or_deferred_reasons:
        issues.append(
            MMMResponseTemplateIssueCode.UNSUPPORTED_DEFERRED_STATUS_INJECTED.value
        )

    if package.provenance:
        _add(
            slot_type=MMMResponseTemplateSlotType.PROVENANCE_REFERENCE,
            content=_mapping_as_content(package.provenance),
            cannot_omit=True,
            must_preserve_verbatim=True,
            metadata={"key_count": len(dict(package.provenance))},
        )
        issues.append(MMMResponseTemplateIssueCode.PROVENANCE_INJECTED.value)

    package_lineage = dict(package.lineage or {})
    if package_lineage:
        _add(
            slot_type=MMMResponseTemplateSlotType.LINEAGE_REFERENCE,
            content=_mapping_as_content(package_lineage),
            cannot_omit=True,
            must_preserve_verbatim=True,
            metadata={"key_count": len(package_lineage)},
        )
        issues.append(MMMResponseTemplateIssueCode.LINEAGE_INJECTED.value)

    readiness_pairs = (
        ("ready_for_llm_prompt_assembly", package.ready_for_llm_prompt_assembly),
        ("ready_for_user_facing_answer", package.ready_for_user_facing_answer),
        ("ready_for_full_orchestration", package.ready_for_full_orchestration),
    )
    for name, value in readiness_pairs:
        _add(
            slot_type=MMMResponseTemplateSlotType.READINESS_FLAG,
            content=f"{name}={value}",
            cannot_omit=True,
            must_preserve_verbatim=True,
            metadata={"flag": name, "value": value},
        )
    issues.append(MMMResponseTemplateIssueCode.READINESS_FLAGS_INJECTED.value)

    human_review_required = _human_review_required(package, request)
    if human_review_required:
        _add(
            slot_type=MMMResponseTemplateSlotType.HUMAN_REVIEW_REQUIREMENT,
            content=(
                "Human review is required before user-facing answer generation."
            ),
            cannot_omit=True,
            must_preserve_verbatim=True,
        )
        issues.append(MMMResponseTemplateIssueCode.HUMAN_REVIEW_INJECTED.value)

    status_upper = str(package.application_status).upper()
    is_blocked_status = "BLOCKED" in status_upper
    is_deferred_status = bool(package.unsupported_or_deferred_reasons) or (
        "DEFER" in status_upper
    )

    if is_blocked_status:
        _add(
            slot_type=MMMResponseTemplateSlotType.REFUSAL_RULE,
            content=f"application_status={package.application_status}",
            cannot_omit=True,
            must_preserve_verbatim=True,
        )

    ready_for_assembly = bool(package.ready_for_llm_prompt_assembly)
    has_refusal_material = bool(
        package.safe_response_guidance.strip()
        or package.cannot_say
        or package.unsupported_or_deferred_reasons
        or package.blocked_capabilities
        or is_blocked_status
    )

    status: MMMResponseTemplateStatus
    mode: MMMResponseTemplateMode
    ready_for_prompt_assembly: bool
    ready_for_refusal_or_defer: bool

    if ready_for_assembly and not is_blocked_status:
        status = MMMResponseTemplateStatus.READY_FOR_PROMPT_ASSEMBLY
        mode = MMMResponseTemplateMode.NORMAL_EXPLANATION
        ready_for_prompt_assembly = True
        ready_for_refusal_or_defer = False
        issues.append(MMMResponseTemplateIssueCode.READY_FOR_PROMPT_ASSEMBLY.value)
    elif ready_for_assembly and is_blocked_status:
        status = MMMResponseTemplateStatus.BLOCKED
        mode = MMMResponseTemplateMode.BLOCKED
        ready_for_prompt_assembly = False
        ready_for_refusal_or_defer = False
        issues.append(
            MMMResponseTemplateIssueCode.APPLICATION_PACKAGE_NOT_READY_FOR_PROMPT_ASSEMBLY.value
        )
        issues.append(MMMResponseTemplateIssueCode.NORMAL_PROMPT_ASSEMBLY_BLOCKED.value)
    elif has_refusal_material:
        status = MMMResponseTemplateStatus.READY_FOR_REFUSAL_OR_DEFER_TEMPLATE
        if is_deferred_status and not is_blocked_status:
            mode = MMMResponseTemplateMode.DEFER_ONLY
        else:
            mode = MMMResponseTemplateMode.REFUSAL_ONLY
        ready_for_prompt_assembly = False
        ready_for_refusal_or_defer = True
        issues.append(
            MMMResponseTemplateIssueCode.APPLICATION_PACKAGE_NOT_READY_FOR_PROMPT_ASSEMBLY.value
        )
        issues.append(MMMResponseTemplateIssueCode.NORMAL_PROMPT_ASSEMBLY_BLOCKED.value)
        issues.append(MMMResponseTemplateIssueCode.REFUSAL_ONLY_TEMPLATE_ALLOWED.value)
        issues.append(
            MMMResponseTemplateIssueCode.READY_FOR_REFUSAL_OR_DEFER_TEMPLATE.value
        )
    else:
        status = MMMResponseTemplateStatus.BLOCKED
        mode = MMMResponseTemplateMode.BLOCKED
        ready_for_prompt_assembly = False
        ready_for_refusal_or_defer = False
        issues.append(
            MMMResponseTemplateIssueCode.APPLICATION_PACKAGE_NOT_READY_FOR_PROMPT_ASSEMBLY.value
        )
        issues.append(MMMResponseTemplateIssueCode.NORMAL_PROMPT_ASSEMBLY_BLOCKED.value)

    if human_review_required and status not in {
        MMMResponseTemplateStatus.BLOCKED,
        MMMResponseTemplateStatus.UNKNOWN,
    }:
        status = MMMResponseTemplateStatus.HUMAN_REVIEW_REQUIRED

    grouped = _group_slots(slots)
    lineage = {
        **dict(base_lineage),
        "application_package_present": True,
        "application_status": package.application_status,
        "package_lineage": package_lineage,
        "ready_for_llm_prompt_assembly": package.ready_for_llm_prompt_assembly,
        "ready_for_user_facing_answer": package.ready_for_user_facing_answer,
        "ready_for_full_orchestration": package.ready_for_full_orchestration,
        "human_review_required": human_review_required,
        "cannot_say_prioritized": True,
    }

    return MMMResponseTemplateOutput(
        request_id=request.request_id,
        status=status.value,
        mode=mode.value,
        ready_for_prompt_assembly=ready_for_prompt_assembly,
        ready_for_refusal_or_defer_template=ready_for_refusal_or_defer,
        ready_for_user_facing_answer=False,
        instruction_slots=tuple(slots),
        system_instruction_slots=grouped["system"],
        developer_instruction_slots=grouped["developer"],
        can_say_slots=grouped["can_say"],
        cannot_say_slots=grouped["cannot_say"],
        safe_response_guidance_slots=grouped["safe_guidance"],
        refusal_rule_slots=grouped["refusal"],
        defer_rule_slots=grouped["defer"],
        gate_requirement_slots=grouped["gates"],
        provenance_reference_slots=grouped["provenance"],
        lineage_reference_slots=grouped["lineage"],
        readiness_flag_slots=grouped["readiness"],
        human_review_slots=grouped["human_review"],
        forbidden_addition_slots=grouped["forbidden"],
        issues=tuple(dict.fromkeys(issues)),
        lineage=lineage,
        metadata={
            **dict(request.metadata),
            "application_status": package.application_status,
            "user_question_present": bool(request.user_question.strip()),
        },
    )


def _group_slots(
    slots: list[MMMResponseTemplateInstructionSlot],
) -> dict[str, tuple[MMMResponseTemplateInstructionSlot, ...]]:
    buckets: dict[str, list[MMMResponseTemplateInstructionSlot]] = {
        "system": [],
        "developer": [],
        "can_say": [],
        "cannot_say": [],
        "safe_guidance": [],
        "refusal": [],
        "defer": [],
        "gates": [],
        "provenance": [],
        "lineage": [],
        "readiness": [],
        "human_review": [],
        "forbidden": [],
    }
    mapping = {
        MMMResponseTemplateSlotType.SYSTEM_INSTRUCTION.value: "system",
        MMMResponseTemplateSlotType.DEVELOPER_INSTRUCTION.value: "developer",
        MMMResponseTemplateSlotType.CAN_SAY_SECTION.value: "can_say",
        MMMResponseTemplateSlotType.CANNOT_SAY_SECTION.value: "cannot_say",
        MMMResponseTemplateSlotType.SAFE_RESPONSE_GUIDANCE.value: "safe_guidance",
        MMMResponseTemplateSlotType.REFUSAL_RULE.value: "refusal",
        MMMResponseTemplateSlotType.DEFER_RULE.value: "defer",
        MMMResponseTemplateSlotType.GATE_REQUIREMENT.value: "gates",
        MMMResponseTemplateSlotType.PROVENANCE_REFERENCE.value: "provenance",
        MMMResponseTemplateSlotType.LINEAGE_REFERENCE.value: "lineage",
        MMMResponseTemplateSlotType.READINESS_FLAG.value: "readiness",
        MMMResponseTemplateSlotType.HUMAN_REVIEW_REQUIREMENT.value: "human_review",
        MMMResponseTemplateSlotType.FORBIDDEN_ADDITION.value: "forbidden",
    }
    for slot in slots:
        bucket = mapping.get(slot.slot_type)
        if bucket is not None:
            buckets[bucket].append(slot)
    return {key: tuple(value) for key, value in buckets.items()}


def _cannot_say_dominates(
    can_say: tuple[str, ...] | list[str],
    cannot_say: tuple[str, ...] | list[str],
) -> tuple[str, ...]:
    blocked = {item.strip().lower() for item in cannot_say if item.strip()}
    return tuple(item for item in can_say if item.strip().lower() not in blocked)


def _mapping_as_content(mapping: Mapping[str, Any]) -> str:
    parts: list[str] = []
    for key in sorted(mapping.keys(), key=str):
        parts.append(f"{key}={mapping[key]!r}")
    return "; ".join(parts) if parts else "{}"


def _looks_deferred(reason: str) -> bool:
    lowered = reason.lower()
    return "defer" in lowered or "unsupported" in lowered or "missing" in lowered


def _human_review_required(
    package: MMMResponseBoundaryApplicationOutput,
    request: MMMResponseTemplateInput,
) -> bool:
    if bool(request.metadata.get("human_review_required")):
        return True
    for reason in package.unsupported_or_deferred_reasons:
        if "human_review" in reason.lower() or "human review" in reason.lower():
            return True
    for section in package.sections:
        if "human_review" in section.section_id.lower():
            return True
        if "human review" in section.title.lower():
            return True
    lineage = dict(package.lineage or {})
    if lineage.get("human_review_required") is True:
        return True
    return False


def _assert_no_forbidden_field_names(model: type[ContractBaseModel]) -> None:
    for name in model.model_fields:
        if name.lower() in _FORBIDDEN_TEMPLATE_FIELD_NAMES:
            msg = f"forbidden template field name present: {name}"
            raise AssertionError(msg)


_assert_no_forbidden_field_names(MMMResponseTemplateInput)
_assert_no_forbidden_field_names(MMMResponseTemplateOutput)
_assert_no_forbidden_field_names(MMMResponseTemplateInstructionSlot)


__all__ = [
    "ARTIFACT_ID",
    "TEMPLATE_MODULE",
    "RECOMMENDED_NEXT_ARTIFACT",
    "MMMResponseTemplateStatus",
    "MMMResponseTemplateSlotType",
    "MMMResponseTemplateMode",
    "MMMResponseTemplateIssueCode",
    "MMMResponseTemplateInstructionSlot",
    "MMMResponseTemplateInput",
    "MMMResponseTemplateOutput",
    "build_mmm_response_template_from_application_package",
    "serialize_mmm_response_template_output",
    "summarize_mmm_response_template_output",
]
