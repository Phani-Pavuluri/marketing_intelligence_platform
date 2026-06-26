"""Lightweight structural checks for Stage A.3 advisory/readiness/intake adapter plan."""

from __future__ import annotations

import json
from pathlib import Path

_PLAN = Path(
    "docs/architecture/STAGE_A3_ADVISORY_READINESS_INTAKE_ADAPTER_PLAN_001.md"
)
_SUMMARY = Path(
    "docs/architecture/archives/"
    "stage_a3_advisory_readiness_intake_adapter_plan_001_summary.json"
)
_CALIBRATION_BASELINE_TERMS = (
    "mip.examples.stage_a_adapters",
    "build_calibration_report_from_stage_a_fixture",
    "deterministic_report_v1",
)
_REQUIRED_SECTIONS = (
    "## 5. Cold-start advisory adapter plan",
    "## 6. Readiness adapter plan",
    "## 7. Intake/routing adapter plan",
    "## 8. Governance unsupported-claim adapter plan",
    "## 9. Report envelope mapping",
    "## 10. Golden paths #1–#2",
    "## 11. Implementation readiness verdict",
    "## 12. Acceptance criteria for future implementation",
)
_FORBIDDEN_OUTPUT_TERMS = (
    "response curves",
    "matched markets",
    "power/MDE",
    "roi_proof",
    "DecisionSurface",
)


def test_stage_a3_adapter_plan_exists() -> None:
    assert _PLAN.is_file()


def test_plan_references_calibration_baseline() -> None:
    content = _PLAN.read_text(encoding="utf-8")
    for term in _CALIBRATION_BASELINE_TERMS:
        assert term in content, f"missing calibration baseline term: {term}"


def test_plan_includes_required_adapter_sections() -> None:
    content = _PLAN.read_text(encoding="utf-8")
    for section in _REQUIRED_SECTIONS:
        assert section in content, f"missing section: {section}"


def test_plan_includes_cold_start_advisory_adapter_plan() -> None:
    content = _PLAN.read_text(encoding="utf-8")
    assert "build_cold_start_input_from_stage_a_fixture" in content
    assert "run_cold_start_advisory_for_stage_a_fixture" in content
    assert "cold_start_advisory" in content


def test_plan_includes_readiness_adapter_plan() -> None:
    content = _PLAN.read_text(encoding="utf-8")
    assert "build_readiness_input_from_stage_a_fixture" in content
    assert "run_readiness_assessment_for_stage_a_fixture" in content
    assert "readiness_assessment" in content


def test_plan_includes_intake_adapter_plan() -> None:
    content = _PLAN.read_text(encoding="utf-8")
    assert "build_intake_input_from_stage_a_fixture" in content
    assert "run_intake_routing_for_stage_a_fixture" in content
    assert "intake_routing" in content


def test_plan_includes_governance_unsupported_claim_stance() -> None:
    content = _PLAN.read_text(encoding="utf-8").lower()
    assert "unsupported_claim_examples" in content
    assert "test/guidance" in content or "test-only" in content


def test_plan_includes_golden_paths_one_and_two() -> None:
    content = _PLAN.read_text(encoding="utf-8")
    assert "Golden path #1" in content
    assert "Golden path #2" in content
    assert "local_fitness_studio" in content
    assert "national_weekly_channel_summary" in content


def test_plan_includes_forbidden_outputs() -> None:
    content = _PLAN.read_text(encoding="utf-8").lower()
    for term in _FORBIDDEN_OUTPUT_TERMS:
        assert term.lower() in content, f"missing forbidden output term: {term}"


def test_plan_includes_implementation_readiness_verdict() -> None:
    content = _PLAN.read_text(encoding="utf-8")
    for verdict in (
        "ready_to_implement",
        "needs_source_inspection",
        "needs_contract_update",
        "blocked",
    ):
        assert verdict in content, f"missing verdict: {verdict}"


def test_plan_summary_json_exists() -> None:
    assert _SUMMARY.is_file()
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["plan_id"] == "STAGE_A3_ADVISORY_READINESS_INTAKE_ADAPTER_PLAN_001"
    assert "golden_paths" in summary
    assert summary["governance_stance"].startswith("unsupported_claim_examples")
