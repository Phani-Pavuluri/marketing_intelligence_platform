"""Tests for MIP_MMM_LLM_RESPONSE_TEMPLATE_FROM_APPLICATION_PACKAGE_001."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from mip.llm import (
    MMMResponseTemplateInput,
    MMMResponseTemplateOutput,
    MMMResponseTemplateStatus,
    build_mmm_response_template_from_application_package,
    serialize_mmm_response_template_output,
    summarize_mmm_response_template_output,
)
from mip.llm.mmm_response_boundary_application import (
    MMMResponseBoundaryApplicationInput,
    MMMResponseBoundaryApplicationOutput,
    package_mmm_llm_response_boundary,
)
from mip.llm.mmm_response_template import (
    MMMResponseTemplateIssueCode,
    MMMResponseTemplateMode,
    MMMResponseTemplateSlotType,
)

ROOT = Path(__file__).resolve().parents[2]
SUMMARY = (
    ROOT
    / "docs/contracts/archives"
    / "MIP_MMM_LLM_RESPONSE_TEMPLATE_FROM_APPLICATION_PACKAGE_001_summary.json"
)
ROADMAP = ROOT / "docs/roadmap/ROADMAP_EXECUTION_SEQUENCE.md"

_FORBIDDEN_KEYS = {
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
}


def _valid_sections() -> list[dict[str, Any]]:
    return [
        {
            "section_id": "status",
            "title": "Status",
            "items": ["READY_TO_EXPLAIN"],
        },
        {
            "section_id": "can_say",
            "title": "What I can say",
            "items": ["Channel spend share is descriptive only.", "overlap_claim"],
            "can_say": ["Channel spend share is descriptive only.", "overlap_claim"],
        },
        {
            "section_id": "cannot_say",
            "title": "What I cannot say",
            "items": ["Do not recommend budget moves.", "overlap_claim"],
            "cannot_say": ["Do not recommend budget moves.", "overlap_claim"],
        },
        {
            "section_id": "blocked_deferred_reasons",
            "title": "Blocked/deferred reasons",
            "items": ["RecommendationContract not approved"],
            "unsupported_or_deferred_reasons": ["RecommendationContract not approved"],
        },
        {
            "section_id": "required_gates",
            "title": "Required gates",
            "items": ["TrustReport", "DecisionSurface"],
            "required_gates": ["TrustReport", "DecisionSurface"],
        },
        {
            "section_id": "evidence_references",
            "title": "Evidence references",
            "items": ["artifact:mmm-planning-envelope-1"],
            "source_artifact_refs": ["artifact:mmm-planning-envelope-1"],
        },
    ]


def _packaged(
    *,
    ready_for_llm_prompt_assembly: bool | None = None,
    human_review_section: bool = False,
    blocked: bool = False,
) -> MMMResponseBoundaryApplicationOutput:
    sections = _valid_sections()
    if human_review_section:
        sections.append(
            {
                "section_id": "human_review_required",
                "title": "Human review",
                "items": ["Human review required"],
            }
        )
    package = package_mmm_llm_response_boundary(
        MMMResponseBoundaryApplicationInput(rendered_sections=sections)
    )
    if blocked:
        package = package.model_copy(
            update={
                "application_status": (
                    "MMM_LLM_RESPONSE_BOUNDARY_APPLICATION_"
                    "BLOCKED_UNSUPPORTED_RECOMMENDATION"
                ),
                "unsupported_or_deferred_reasons": (
                    "recommendation_like_content_without_required_gates",
                ),
            }
        )
    if ready_for_llm_prompt_assembly is not None:
        package = package.model_copy(
            update={"ready_for_llm_prompt_assembly": ready_for_llm_prompt_assembly}
        )
    return package


def test_missing_application_package_returns_unknown() -> None:
    output = build_mmm_response_template_from_application_package(
        MMMResponseTemplateInput(request_id="req-missing")
    )
    assert output.status == MMMResponseTemplateStatus.UNKNOWN.value
    assert output.mode == MMMResponseTemplateMode.UNKNOWN.value
    assert output.ready_for_prompt_assembly is False
    assert output.ready_for_refusal_or_defer_template is False
    assert (
        MMMResponseTemplateIssueCode.APPLICATION_PACKAGE_MISSING.value in output.issues
    )


def test_application_package_consumed() -> None:
    package = _packaged()
    output = build_mmm_response_template_from_application_package(
        MMMResponseTemplateInput(
            request_id="req-consume",
            application_package=package,
            user_question="What can I say about spend?",
        )
    )
    assert (
        MMMResponseTemplateIssueCode.APPLICATION_PACKAGE_PRESENT.value in output.issues
    )
    assert output.lineage.get("application_package_present") is True


def test_raw_boundary_direct_input_not_accepted() -> None:
    assert "response_boundary" not in MMMResponseTemplateInput.model_fields
    assert "llm_response_boundary" not in MMMResponseTemplateInput.model_fields
    assert "boundary" not in MMMResponseTemplateInput.model_fields
    with pytest.raises(ValidationError):
        MMMResponseTemplateInput(
            request_id="req-boundary",
            metadata={"response_boundary": "raw"},
        )


def test_can_say_slots_created() -> None:
    output = build_mmm_response_template_from_application_package(
        MMMResponseTemplateInput(request_id="req-can", application_package=_packaged())
    )
    assert output.can_say_slots
    assert MMMResponseTemplateIssueCode.CAN_SAY_INJECTED.value in output.issues
    assert all(
        slot.slot_type == MMMResponseTemplateSlotType.CAN_SAY_SECTION.value
        for slot in output.can_say_slots
    )


def test_cannot_say_slots_created_and_cannot_omit() -> None:
    output = build_mmm_response_template_from_application_package(
        MMMResponseTemplateInput(
            request_id="req-cannot", application_package=_packaged()
        )
    )
    assert output.cannot_say_slots
    assert all(slot.cannot_omit for slot in output.cannot_say_slots)
    assert all(slot.must_preserve_verbatim for slot in output.cannot_say_slots)
    assert MMMResponseTemplateIssueCode.CANNOT_SAY_INJECTED.value in output.issues


def test_cannot_say_prioritized_over_can_say() -> None:
    output = build_mmm_response_template_from_application_package(
        MMMResponseTemplateInput(
            request_id="req-priority", application_package=_packaged()
        )
    )
    can_say_contents = {slot.content for slot in output.can_say_slots}
    assert "overlap_claim" not in can_say_contents
    assert MMMResponseTemplateIssueCode.CANNOT_SAY_PRIORITIZED.value in output.issues


def test_safe_response_guidance_slots_created() -> None:
    output = build_mmm_response_template_from_application_package(
        MMMResponseTemplateInput(
            request_id="req-guidance", application_package=_packaged()
        )
    )
    assert output.safe_response_guidance_slots
    assert (
        MMMResponseTemplateIssueCode.SAFE_RESPONSE_GUIDANCE_INJECTED.value
        in output.issues
    )


def test_gates_slots_created() -> None:
    output = build_mmm_response_template_from_application_package(
        MMMResponseTemplateInput(
            request_id="req-gates", application_package=_packaged()
        )
    )
    assert output.gate_requirement_slots
    assert MMMResponseTemplateIssueCode.GATES_INJECTED.value in output.issues


def test_provenance_slots_created() -> None:
    output = build_mmm_response_template_from_application_package(
        MMMResponseTemplateInput(
            request_id="req-prov", application_package=_packaged()
        )
    )
    assert output.provenance_reference_slots
    assert MMMResponseTemplateIssueCode.PROVENANCE_INJECTED.value in output.issues


def test_lineage_slots_created() -> None:
    output = build_mmm_response_template_from_application_package(
        MMMResponseTemplateInput(
            request_id="req-lin", application_package=_packaged()
        )
    )
    assert output.lineage_reference_slots
    assert MMMResponseTemplateIssueCode.LINEAGE_INJECTED.value in output.issues


def test_readiness_flag_slots_created() -> None:
    output = build_mmm_response_template_from_application_package(
        MMMResponseTemplateInput(
            request_id="req-ready", application_package=_packaged()
        )
    )
    assert len(output.readiness_flag_slots) == 3
    assert MMMResponseTemplateIssueCode.READINESS_FLAGS_INJECTED.value in output.issues


def test_human_review_slot_created_when_required() -> None:
    output = build_mmm_response_template_from_application_package(
        MMMResponseTemplateInput(
            request_id="req-hr",
            application_package=_packaged(human_review_section=True),
            metadata={"human_review_required": True},
        )
    )
    assert output.human_review_slots
    assert MMMResponseTemplateIssueCode.HUMAN_REVIEW_INJECTED.value in output.issues
    assert output.status == MMMResponseTemplateStatus.HUMAN_REVIEW_REQUIRED.value


def test_readiness_false_blocks_normal_prompt_assembly() -> None:
    output = build_mmm_response_template_from_application_package(
        MMMResponseTemplateInput(
            request_id="req-not-ready",
            application_package=_packaged(ready_for_llm_prompt_assembly=False),
        )
    )
    assert output.ready_for_prompt_assembly is False
    assert (
        MMMResponseTemplateIssueCode.NORMAL_PROMPT_ASSEMBLY_BLOCKED.value
        in output.issues
    )
    assert (
        MMMResponseTemplateIssueCode.APPLICATION_PACKAGE_NOT_READY_FOR_PROMPT_ASSEMBLY.value
        in output.issues
    )


def test_readiness_false_allows_refusal_defer_template() -> None:
    output = build_mmm_response_template_from_application_package(
        MMMResponseTemplateInput(
            request_id="req-refusal",
            application_package=_packaged(ready_for_llm_prompt_assembly=False),
        )
    )
    assert output.ready_for_refusal_or_defer_template is True
    assert (
        output.status
        == MMMResponseTemplateStatus.READY_FOR_REFUSAL_OR_DEFER_TEMPLATE.value
    )
    assert (
        MMMResponseTemplateIssueCode.REFUSAL_ONLY_TEMPLATE_ALLOWED.value
        in output.issues
    )


def test_readiness_true_allows_metadata_prompt_assembly_readiness_only() -> None:
    package = _packaged(ready_for_llm_prompt_assembly=True)
    # Clear deferred reasons so blocked/deferred path does not dominate.
    package = package.model_copy(update={"unsupported_or_deferred_reasons": ()})
    output = build_mmm_response_template_from_application_package(
        MMMResponseTemplateInput(request_id="req-ready-true", application_package=package)
    )
    assert output.ready_for_prompt_assembly is True
    assert output.status == MMMResponseTemplateStatus.READY_FOR_PROMPT_ASSEMBLY.value
    assert output.mode == MMMResponseTemplateMode.NORMAL_EXPLANATION.value
    assert MMMResponseTemplateIssueCode.NO_PROMPT_EXECUTION.value in output.issues
    assert MMMResponseTemplateIssueCode.NO_LLM_CALL.value in output.issues


def test_unsupported_deferred_state_preserved() -> None:
    output = build_mmm_response_template_from_application_package(
        MMMResponseTemplateInput(
            request_id="req-deferred", application_package=_packaged()
        )
    )
    assert output.defer_rule_slots or output.refusal_rule_slots
    assert (
        MMMResponseTemplateIssueCode.UNSUPPORTED_DEFERRED_STATUS_INJECTED.value
        in output.issues
    )


def test_blocked_state_preserved() -> None:
    output = build_mmm_response_template_from_application_package(
        MMMResponseTemplateInput(
            request_id="req-blocked",
            application_package=_packaged(blocked=True),
        )
    )
    assert any("BLOCKED" in slot.content for slot in output.refusal_rule_slots)
    assert output.ready_for_prompt_assembly is False


def test_refusal_defer_slots_for_blocked_deferred() -> None:
    output = build_mmm_response_template_from_application_package(
        MMMResponseTemplateInput(
            request_id="req-slots",
            application_package=_packaged(blocked=True),
        )
    )
    assert output.refusal_rule_slots or output.defer_rule_slots


def test_system_and_developer_instruction_slots_created() -> None:
    output = build_mmm_response_template_from_application_package(
        MMMResponseTemplateInput(
            request_id="req-sys", application_package=_packaged()
        )
    )
    assert output.system_instruction_slots
    assert output.developer_instruction_slots
    assert "LLMExplanationPlan" in output.system_instruction_slots[0].content


def test_llm_explanation_plan_parallel_path_blocked() -> None:
    output = build_mmm_response_template_from_application_package(
        MMMResponseTemplateInput(
            request_id="req-plan", application_package=_packaged()
        )
    )
    assert (
        MMMResponseTemplateIssueCode.LLM_EXPLANATION_PLAN_PARALLEL_PATH_BLOCKED.value
        in output.issues
    )


def test_no_forbidden_prompt_provider_answer_fields() -> None:
    for model in (MMMResponseTemplateInput, MMMResponseTemplateOutput):
        for name in model.model_fields:
            assert name.lower() not in _FORBIDDEN_KEYS
    output = build_mmm_response_template_from_application_package(
        MMMResponseTemplateInput(
            request_id="req-forbid", application_package=_packaged()
        )
    )
    dumped = serialize_mmm_response_template_output(output)
    for key in dumped:
        assert key.lower() not in _FORBIDDEN_KEYS


def test_no_execution_and_no_downstream_authorization_issues() -> None:
    output = build_mmm_response_template_from_application_package(
        MMMResponseTemplateInput(
            request_id="req-noexec", application_package=_packaged()
        )
    )
    required = [
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
        "RAW_BOUNDARY_DIRECT_INPUT_BLOCKED",
    ]
    for code in required:
        assert code in output.issues


def test_serializer_json_safe() -> None:
    output = build_mmm_response_template_from_application_package(
        MMMResponseTemplateInput(
            request_id="req-ser", application_package=_packaged()
        )
    )
    payload = serialize_mmm_response_template_output(output)
    encoded = json.dumps(payload)
    assert isinstance(json.loads(encoded), dict)
    assert isinstance(payload["instruction_slots"], list)
    assert isinstance(payload["issues"], list)


def test_summary_helper_counts_only() -> None:
    output = build_mmm_response_template_from_application_package(
        MMMResponseTemplateInput(
            request_id="req-sum", application_package=_packaged()
        )
    )
    summary = summarize_mmm_response_template_output(output)
    assert set(summary) >= {
        "status",
        "mode",
        "ready_for_prompt_assembly",
        "instruction_slot_count",
        "can_say_slot_count",
        "cannot_say_slot_count",
        "issue_count",
    }
    for key in summary:
        assert key.lower() not in _FORBIDDEN_KEYS
    assert "Channel spend" not in json.dumps(summary)


def test_exported_from_mip_llm() -> None:
    assert callable(build_mmm_response_template_from_application_package)
    assert callable(serialize_mmm_response_template_output)
    assert callable(summarize_mmm_response_template_output)
    assert MMMResponseTemplateInput is not None
    assert MMMResponseTemplateOutput is not None


def test_summary_json_and_roadmap() -> None:
    assert SUMMARY.is_file()
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    assert summary["mmm_llm_response_template_from_application_package_implemented"] is True
    assert summary["application_package_consumed"] is True
    assert summary["raw_boundary_direct_input_blocked"] is True
    assert summary["prompt_execution_implemented"] is False
    assert (
        summary["recommended_next_artifact"]
        == "MIP_MMM_LLM_RESPONSE_TEMPLATE_CHECKPOINT_AUDIT_001"
    )
    roadmap = ROADMAP.read_text(encoding="utf-8")
    assert "MIP_MMM_LLM_RESPONSE_TEMPLATE_FROM_APPLICATION_PACKAGE_001" in roadmap
