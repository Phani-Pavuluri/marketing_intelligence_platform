"""Structural checks for MIP LLM control plane evaluation strategy."""

from __future__ import annotations

import json
import re
from pathlib import Path

_DOC = Path("docs/evaluation/MIP_LLM_CONTROL_PLANE_EVALUATION_STRATEGY_001.md")
_SUMMARY = Path(
    "docs/evaluation/archives/mip_llm_control_plane_evaluation_strategy_001_summary.json"
)

_REQUIRED_SECTIONS = (
    "## 3. Scope distinction",
    "## 4. Eval layers",
    "## 5. Required LLM eval dimensions",
    "## 6. Fixture family strategy",
    "## 7. Proposed canned explanation eval schema",
    "## 8. Proposed validation result schema",
    "## 9. CI-safe deterministic/mock strategy",
    "## 10. Human review and red-team strategy",
    "## 11. Gates before runtime LLM enablement",
    "## 12. Relationship to future LLM explanation contracts",
    "## 13. Roadmap sequence",
    "## 14. Stop/go criteria",
)

_REQUIRED_EVAL_DIMENSIONS = (
    "intent_classification",
    "answerability_state_classification",
    "tool_routing_correctness",
    "deterministic_registry_validation_compliance",
    "missing_input_question_quality",
    "claim_boundary_preservation",
    "grounded_explanation_faithfulness",
    "report_invocation_correctness",
    "session_state_assumption_correctness",
    "failure_recovery_behavior",
    "advisory_mode_safety",
    "cross_package_routing",
    "unsupported_claim_refusal",
    "rule_sprawl_resistance",
)

_FIXTURE_FAMILIES = (
    "agent_capability_eval",
    "llm_explanation_canned_eval",
    "llm_explanation_mock_provider_eval",
    "llm_red_team_eval",
    "llm_cross_package_boundary_eval",
    "llm_tool_unavailable_eval",
)

_GATES = ("G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8")

_FORBIDDEN_RUNTIME_FLAGS = (
    "runtime_llm_provider_eval_implemented.*true",
    "runtime_llm_agents_implemented.*true",
)


def test_evaluation_strategy_doc_exists() -> None:
    assert _DOC.is_file()


def test_required_sections_present() -> None:
    content = _DOC.read_text(encoding="utf-8")
    for section in _REQUIRED_SECTIONS:
        assert section in content, f"missing section: {section}"


def test_scope_distinction_documented() -> None:
    content = _DOC.read_text(encoding="utf-8")
    assert "Answerability evals" in content
    assert "LLM control-plane evals" in content
    assert "Provider/runtime evals" in content
    assert (
        "does not replace MIP LLM control-plane evals"
        in content
    )


def test_five_eval_layers_documented() -> None:
    content = _DOC.read_text(encoding="utf-8")
    assert "Layer 1 — Answerability routing evals" in content
    assert "Layer 2 — Deterministic report/output evals" in content
    assert "Layer 3 — Canned LLM explanation response evals" in content
    assert "Layer 4 — Mock-provider CI evals" in content
    assert "Layer 5 — Human red-team / runtime provider evals" in content


def test_all_fourteen_eval_dimensions_documented() -> None:
    content = _DOC.read_text(encoding="utf-8")
    for dimension in _REQUIRED_EVAL_DIMENSIONS:
        assert dimension in content, f"missing dimension: {dimension}"


def test_fixture_family_strategy_documented() -> None:
    content = _DOC.read_text(encoding="utf-8")
    for family in _FIXTURE_FAMILIES:
        assert family in content, f"missing fixture family: {family}"


def test_canned_explanation_eval_schema_documented() -> None:
    content = _DOC.read_text(encoding="utf-8")
    assert "LLMExplanationEvalCase" in content
    assert "candidate_response" in content
    assert "expected_preserved_state" in content
    assert "forbidden_claims" in content


def test_validation_result_schema_documented() -> None:
    content = _DOC.read_text(encoding="utf-8")
    assert "LLMExplanationValidationResult" in content
    assert "unsupported_claims_detected" in content
    assert "provenance_errors" in content


def test_ci_safe_mock_strategy_documented() -> None:
    content = _DOC.read_text(encoding="utf-8")
    assert "Must not" in content and "provider API keys" in content
    assert "provider-free" in content.lower() or "Provider-free" in content


def test_human_red_team_strategy_documented() -> None:
    content = _DOC.read_text(encoding="utf-8")
    assert "red-team" in content.lower()
    assert "matched markets" in content.lower() or "treatment" in content.lower()


def test_gates_documented() -> None:
    content = _DOC.read_text(encoding="utf-8")
    for gate in _GATES:
        assert gate in content, f"missing gate: {gate}"
    assert "blocked until G3–G8" in content or "blocked until G3-G8" in content


def test_stop_go_criteria_documented() -> None:
    content = _DOC.read_text(encoding="utf-8")
    assert "### Safe now" in content
    assert "### Blocked" in content
    assert "Runtime provider calls" in content


def test_no_runtime_provider_implementation_claimed() -> None:
    content = _DOC.read_text(encoding="utf-8")
    assert "Docs/eval planning only" in content
    assert "provider calls" in content
    assert "generated explanations" in content
    assert "validate_llm_explanation_response()" in content
    assert "Not in scope for this artifact" in content


def test_summary_json_valid_and_safe() -> None:
    assert _SUMMARY.is_file()
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["artifact_id"] == "MIP_LLM_CONTROL_PLANE_EVALUATION_STRATEGY_001"
    assert summary["runtime_llm_provider_eval_implemented"] is False
    assert summary["ci_safe_mock_eval_required"] is True
    assert summary["human_review_red_team_eval_required"] is True
    assert summary["spend_contrast_eval_substitutes_llm_control_plane_eval"] is False
    assert summary["required_llm_eval_dimensions"] == list(_REQUIRED_EVAL_DIMENSIONS)
    assert len(summary["eval_layers"]) == 5
    assert len(summary["fixture_families"]) == 6


def test_summary_json_forbidden_runtime_flags() -> None:
    raw = _SUMMARY.read_text(encoding="utf-8")
    for pattern in _FORBIDDEN_RUNTIME_FLAGS:
        assert not re.search(pattern, raw), f"forbidden flag pattern matched: {pattern}"
