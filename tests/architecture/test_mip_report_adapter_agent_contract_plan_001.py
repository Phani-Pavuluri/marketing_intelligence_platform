"""Lightweight structural checks for report/adapter/agent contract plan."""

from __future__ import annotations

import json
from pathlib import Path

_PLAN = Path("docs/architecture/MIP_REPORT_ADAPTER_AGENT_CONTRACT_PLAN_001.md")
_SUMMARY = Path(
    "docs/architecture/archives/mip_report_adapter_agent_contract_plan_001_summary.json"
)
_AUDIT_REF = "MIP_AGENT_TOOLING_AND_ROADMAP_IMPLEMENTATION_DETAIL_AUDIT_001"

_REQUIRED_SECTIONS = (
    "## 4. Stage A.3 fixture→workflow adapter plan",
    "## 5. Deterministic report output contract plan",
    "## 6. Artifact registry / provenance plan",
    "## 7. Future agent packet contract plan",
    "## 8. LLM explanation boundary contract plan",
    "## 9. Golden-path deterministic acceptance test plan",
    "## 13. Stop/go criteria",
)

_FORBIDDEN_BOUNDARY_TERMS = (
    "mmm/geox execution",
    "response curves",
    "optimizer outputs",
    "causal lift",
    "roi",
)


def test_report_adapter_agent_contract_plan_exists() -> None:
    assert _PLAN.is_file()


def test_plan_references_audit() -> None:
    content = _PLAN.read_text(encoding="utf-8")
    assert _AUDIT_REF in content


def test_plan_includes_required_sections() -> None:
    content = _PLAN.read_text(encoding="utf-8")
    for section in _REQUIRED_SECTIONS:
        assert section in content, f"missing section: {section}"


def test_plan_documents_forbidden_boundaries() -> None:
    content = _PLAN.read_text(encoding="utf-8").lower()
    for term in _FORBIDDEN_BOUNDARY_TERMS:
        assert term.lower() in content, f"missing boundary term: {term}"


def test_plan_summary_json_exists() -> None:
    assert _SUMMARY.is_file()
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["plan_id"] == "MIP_REPORT_ADAPTER_AGENT_CONTRACT_PLAN_001"
    assert "golden_path_deterministic_acceptance_test_plan" in summary["sections"]
