"""Tests for MIP_MMM_LLM_RESPONSE_BOUNDARY_APPLICATION_001."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from mip.llm.mmm_response_boundary_application import (
    MMMResponseBoundaryApplicationInput,
    MMMResponseBoundaryApplicationOutput,
    MMMResponseBoundaryApplicationSection,
    MMMResponseBoundaryApplicationStatus,
    package_mmm_llm_response_boundary,
    serialize_mmm_llm_response_boundary_application_output,
)

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/contracts/MIP_MMM_LLM_RESPONSE_BOUNDARY_APPLICATION_001.md"
SUMMARY = (
    ROOT
    / "docs/contracts/archives/MIP_MMM_LLM_RESPONSE_BOUNDARY_APPLICATION_001_summary.json"
)
ROADMAP = ROOT / "docs/roadmap/ROADMAP_EXECUTION_SEQUENCE.md"
STRATEGY = ROOT / "docs/architecture/REPO_INTEGRATION_STRATEGY.md"

ALLOWED_NEXT = "MIP_MMM_LLM_RESPONSE_BOUNDARY_APPLICATION_CHECKPOINT_001"


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


def test_public_api_import() -> None:
    assert callable(package_mmm_llm_response_boundary)
    assert callable(serialize_mmm_llm_response_boundary_application_output)
    assert MMMResponseBoundaryApplicationInput is not None
    assert MMMResponseBoundaryApplicationOutput is not None
    assert MMMResponseBoundaryApplicationSection is not None


def test_valid_sections_package_successfully() -> None:
    output = package_mmm_llm_response_boundary(
        MMMResponseBoundaryApplicationInput(
            rendered_sections=_valid_sections(),
            lineage={"source": "test"},
            request_context={"request_id": "req-1"},
        )
    )
    assert (
        output.application_status
        == MMMResponseBoundaryApplicationStatus.READY_FOR_METADATA_PACKAGING.value
    )
    assert len(output.sections) == 6
    assert output.safe_response_guidance
    assert "Use only the packaged rendered sections" in output.safe_response_guidance


def test_can_say_and_cannot_say_preserved_and_cannot_say_dominates() -> None:
    output = package_mmm_llm_response_boundary(
        MMMResponseBoundaryApplicationInput(rendered_sections=_valid_sections())
    )
    assert "Channel spend share is descriptive only." in output.can_say
    assert "Do not recommend budget moves." in output.cannot_say
    assert "overlap_claim" in output.cannot_say
    assert "overlap_claim" not in output.can_say


def test_unsupported_deferred_and_gates_and_provenance_preserved() -> None:
    output = package_mmm_llm_response_boundary(
        MMMResponseBoundaryApplicationInput(
            rendered_sections=_valid_sections(),
            lineage={"run_id": "r1"},
        )
    )
    assert "RecommendationContract not approved" in output.unsupported_or_deferred_reasons
    assert "TrustReport" in output.required_gates
    assert "DecisionSurface" in output.required_gates
    assert output.provenance.get("source") == "deterministic_rendered_mmm_planning_sections"
    assert output.lineage.get("artifact_id") == "MIP_MMM_LLM_RESPONSE_BOUNDARY_APPLICATION_001"
    assert output.lineage.get("input_lineage", {}).get("run_id") == "r1"
    refs = [
        ref
        for section in output.sections
        for ref in section.source_artifact_refs
    ]
    assert "artifact:mmm-planning-envelope-1" in refs


def test_missing_rendered_sections_block() -> None:
    output = package_mmm_llm_response_boundary(
        MMMResponseBoundaryApplicationInput(rendered_sections=[])
    )
    assert (
        output.application_status
        == MMMResponseBoundaryApplicationStatus.BLOCKED_MISSING_RENDERED_SECTIONS.value
    )


def test_missing_boundary_metadata_blocks_under_strict_mode() -> None:
    output = package_mmm_llm_response_boundary(
        MMMResponseBoundaryApplicationInput(
            rendered_sections=[
                {
                    "section_id": "status",
                    "title": "Status",
                    "rendered_text": "READY_TO_EXPLAIN",
                }
            ],
            strict_boundary=True,
        )
    )
    assert (
        output.application_status
        == MMMResponseBoundaryApplicationStatus.BLOCKED_BOUNDARY_VIOLATION.value
    )


def test_recommendation_like_content_without_required_gates_blocks() -> None:
    output = package_mmm_llm_response_boundary(
        MMMResponseBoundaryApplicationInput(
            rendered_sections=[
                {
                    "section_id": "can_say",
                    "title": "What I can say",
                    "items": ["Descriptive only"],
                },
                {
                    "section_id": "cannot_say",
                    "title": "What I cannot say",
                    "items": ["No budget advice"],
                },
                {
                    "section_id": "advice",
                    "title": "Advice",
                    "rendered_text": "I recommend reallocating budget for higher ROI.",
                },
            ],
            strict_boundary=True,
        )
    )
    assert (
        output.application_status
        == MMMResponseBoundaryApplicationStatus.BLOCKED_UNSUPPORTED_RECOMMENDATION.value
    )


def test_ready_flags_always_false_and_serializer_json_safe() -> None:
    output = package_mmm_llm_response_boundary(
        MMMResponseBoundaryApplicationInput(rendered_sections=_valid_sections())
    )
    assert output.ready_for_llm_prompt_assembly is False
    assert output.ready_for_user_facing_answer is False
    assert output.ready_for_full_orchestration is False
    payload = serialize_mmm_llm_response_boundary_application_output(output)
    json.dumps(payload)
    assert payload["ready_for_llm_prompt_assembly"] is False
    assert isinstance(payload["sections"], list)
    assert isinstance(payload["can_say"], list)


def test_summary_and_docs_flags() -> None:
    assert DOC.is_file()
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    assert summary["artifact_id"] == "MIP_MMM_LLM_RESPONSE_BOUNDARY_APPLICATION_001"
    assert summary["application_packaging_implemented"] is True
    assert summary["rendered_sections_consumed"] is True
    assert summary["can_say_metadata_preserved"] is True
    assert summary["cannot_say_metadata_preserved"] is True
    assert summary["unsupported_deferred_states_preserved"] is True
    assert summary["safe_response_guidance_returned"] is True
    assert summary["cannot_say_dominates_can_say"] is True
    assert summary["missing_rendered_sections_block"] is True
    assert summary["missing_boundary_metadata_blocks_under_strict_mode"] is True
    assert summary["recommendation_like_content_without_required_gates_blocks"] is True
    assert summary["json_safe_serializer_implemented"] is True
    assert summary["ready_for_llm_prompt_assembly"] is False
    assert summary["ready_for_user_facing_answer"] is False
    assert summary["ready_for_full_orchestration"] is False
    for key in (
        "llm_provider_called",
        "prompt_assembly_implemented",
        "user_facing_answer_generation_implemented",
        "full_orchestration_implemented",
        "decision_surface_authorized",
        "trust_report_bypassed",
        "recommendation_contract_authorized",
        "planning_recommendation_enabled",
        "budget_optimization_enabled",
        "spend_movement_authorized",
        "roi_roas_authorized",
        "claim_authorization_changed",
        "catalog_unblocked",
        "production_compatibility_authorized",
        "method_promoted",
        "instrument_promoted",
    ):
        assert summary[key] is False, key
    assert summary["recommended_next_artifact"] == ALLOWED_NEXT
    roadmap = ROADMAP.read_text(encoding="utf-8")
    strategy = STRATEGY.read_text(encoding="utf-8")
    assert "MIP_MMM_LLM_RESPONSE_BOUNDARY_APPLICATION_001" in roadmap
    assert "MIP_MMM_LLM_RESPONSE_BOUNDARY_APPLICATION_001" in strategy
