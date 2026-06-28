"""Structural checks for MIP LLM control plane architecture."""

from __future__ import annotations

import json
import re
from pathlib import Path

_DOC = Path("docs/architecture/MIP_LLM_CONTROL_PLANE_ARCHITECTURE_001.md")
_SUMMARY = Path(
    "docs/architecture/archives/mip_llm_control_plane_architecture_001_summary.json"
)

_REQUIRED_SECTIONS = (
    "## 3. Current decision: LLM-first, deterministic-core",
    "## 4. Shared MIP control plane and package-specific adapters",
    "## 8. Tool routing policy: LLM proposes, deterministic registry validates",
    "## 9. Answerability gate policy",
    "## 10. Low-risk diagnostic auto-run policy",
    "## 11. High-stakes action authorization policy",
    "## 12. Final report invocation policy",
    "## 13. Advisory mode policy",
    "## 14. Session state / assumption management policy",
    "## 15. Necessary LLM capabilities / modules",
    "## 16. Deferred / collapsed standalone agents",
    "## 17. Ballpark standalone contract deferral",
    "## 18. Artifact / report grounding requirements",
    "## 19. Failure recovery requirements",
    "## 30. LLM control-plane eval strategy",
    "## 31. Required eval dimensions",
    "## 32. Eval fixture strategy",
    "## 33. CI-safe deterministic/mock eval strategy",
    "## 34. Human review / red-team eval strategy",
    "## 35. Eval gates before runtime LLM enablement",
    "## 36. Final verdict",
)

_FORBIDDEN_RUNTIME_FLAGS = (
    "runtime_llm_agents_implemented.*true",
    "runtime_tool_orchestration_implemented.*true",
    "runtime_llm_provider_eval_implemented.*true",
    "production_authorization_granted.*true",
    "llm_decisioning_authorized.*true",
    "session_state_inferred_claims_allowed.*true",
    "ballpark_standalone_contract_active.*true",
)

_REQUIRED_LLM_EVAL_DIMENSIONS = (
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


def test_mip_llm_control_plane_architecture_doc_exists() -> None:
    assert _DOC.is_file()


def test_core_principle_documented() -> None:
    content = _DOC.read_text(encoding="utf-8")
    assert "LLM-first" in content
    assert "deterministic-core" in content.lower() or "deterministic-core" in content
    assert "LLM explains and routes; deterministic contracts decide" in content


def test_shared_control_plane_and_adapters() -> None:
    content = _DOC.read_text(encoding="utf-8")
    assert (
        "package-specific adapters" in content.lower()
        or "package-specific tool adapters" in content
    )
    assert "MMM" in content
    assert "GeoX" in content or "panel_exp" in content


def test_answerability_gate_policy() -> None:
    content = _DOC.read_text(encoding="utf-8")
    assert "AgentAnswerabilityState" in content
    assert "evaluate_agent_answerability" in content


def test_deferred_agents_and_ballpark() -> None:
    content = _DOC.read_text(encoding="utf-8")
    assert "Design Feasibility Interpreter Agent" in content
    assert "BALLPARK_FEASIBILITY_MODE_CONTRACT_001" in content
    assert "deferred" in content.lower()


def test_geox_compatibility_preserved() -> None:
    content = _DOC.read_text(encoding="utf-8")
    assert "GEO_KPI_SPEND_DATA_PROFILER_001" in content
    assert "GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001" in content
    assert "PANEL_EXP_GOLDEN_PATH_ACCEPTANCE_TESTS_001" in content
    assert "No rollback" in content or "not rolled back" in content.lower()


def test_required_sections_present() -> None:
    content = _DOC.read_text(encoding="utf-8")
    for section in _REQUIRED_SECTIONS:
        assert section in content, f"missing section: {section}"


def test_llm_eval_strategy_documented() -> None:
    content = _DOC.read_text(encoding="utf-8")
    assert "LLM control-plane eval strategy" in content
    assert "Rule-sprawl resistance" in content
    assert "CI-safe deterministic/mock eval strategy" in content
    assert "Eval gates before runtime LLM enablement" in content
    assert "SPEND_CONTRAST_FEASIBILITY_TOOLING_CONTRACT_001" in content
    assert "do **not** substitute for MIP-level LLM control-plane evals" in content


def test_summary_json_valid_and_safe() -> None:
    assert _SUMMARY.is_file()
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["artifact_id"] == "MIP_LLM_CONTROL_PLANE_ARCHITECTURE_001"
    assert summary["runtime_llm_agents_implemented"] is False
    assert summary["session_state_inferred_claims_allowed"] is False
    assert summary["ballpark_standalone_contract_active"] is False
    assert summary["llm_control_plane_eval_strategy_defined"] is True
    assert summary["runtime_llm_provider_eval_implemented"] is False
    assert summary["ci_safe_mock_eval_required"] is True
    assert summary["human_review_red_team_eval_required"] is True
    assert summary["required_llm_eval_dimensions"] == list(_REQUIRED_LLM_EVAL_DIMENSIONS)
    assert summary["final_verdict"] == (
        "mip_llm_control_plane_architecture_defined_no_runtime_agents_or_production_authorization"
    )
    assert len(summary["necessary_llm_capabilities"]) == 7
    assert len(summary["recommended_next_mip_artifacts"]) == 7


def test_summary_json_forbidden_runtime_flags() -> None:
    raw = _SUMMARY.read_text(encoding="utf-8")

    for pattern in _FORBIDDEN_RUNTIME_FLAGS:
        assert not re.search(pattern, raw), f"forbidden flag pattern matched: {pattern}"
