"""Structural checks for MIP LLM control plane architecture."""

from __future__ import annotations

import json
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
    "## 30. Final verdict",
)

_FORBIDDEN_RUNTIME_FLAGS = (
    "runtime_llm_agents_implemented.*true",
    "runtime_tool_orchestration_implemented.*true",
    "production_authorization_granted.*true",
    "llm_decisioning_authorized.*true",
    "session_state_inferred_claims_allowed.*true",
    "ballpark_standalone_contract_active.*true",
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


def test_summary_json_valid_and_safe() -> None:
    assert _SUMMARY.is_file()
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["artifact_id"] == "MIP_LLM_CONTROL_PLANE_ARCHITECTURE_001"
    assert summary["runtime_llm_agents_implemented"] is False
    assert summary["session_state_inferred_claims_allowed"] is False
    assert summary["ballpark_standalone_contract_active"] is False
    assert summary["final_verdict"] == (
        "mip_llm_control_plane_architecture_defined_no_runtime_agents_or_production_authorization"
    )
    assert len(summary["necessary_llm_capabilities"]) == 7
    assert len(summary["recommended_next_mip_artifacts"]) == 7
