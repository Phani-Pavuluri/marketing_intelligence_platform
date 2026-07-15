# ruff: noqa: E501
import json
from pathlib import Path

ROOT = Path(__file__).parents[2]
REGISTRY = ROOT / "docs/architecture/archives/MIP_CONVERSATIONAL_CAPABILITY_ROUTING_AND_GROUNDED_RESPONSE_ARCHITECTURE_001_phase_registry.json"
REQUIRED = {"phase_id","phase_name","phase_type","objective","user_or_platform_outcome","rationale","entry_criteria","required_prior_artifacts","required_prior_capabilities","required_decisions","inputs","contracts_consumed","artifacts_consumed","deliverables","contracts_created_or_changed","artifacts_created_or_changed","likely_repository_areas","capabilities_enabled","capabilities_remaining_blocked","execution_boundary","claim_boundary","dependencies","parallelizable_with","must_precede","must_follow","implementation_tasks","recommended_commit_boundary","recommended_next_artifact","acceptance_criteria","focused_tests","integration_tests","evaluation_requirements","browser_or_manual_review","docker_validation","deployment_validation","stop_conditions","rollback_or_recovery","exit_criteria","downstream_authorization","owner","status"}

def test_phase_registry_is_complete_and_ordered() -> None:
    data = json.loads(REGISTRY.read_text())
    phases = data["phases"]
    assert data["schema_version"] == "phase_definition_v1"
    ids = [p["phase_id"] for p in phases]
    assert ids == [f"phase_{c}" for c in "abcdefghijkl"]
    assert len(ids) == len(set(ids)) == 12
    known = set(ids) | {"external:approved_architecture", "external:implementation_plan"}
    scalar = {"phase_id","phase_name","phase_type","objective","user_or_platform_outcome","rationale","execution_boundary","claim_boundary","recommended_commit_boundary","recommended_next_artifact","browser_or_manual_review","deployment_validation","rollback_or_recovery","owner","status"}
    for phase in phases:
        assert REQUIRED <= phase.keys()
        for key in REQUIRED - scalar - {"parallelizable_with", "must_follow"}:
            assert isinstance(phase[key], list) and phase[key]
        for key in ("dependencies","parallelizable_with","must_precede","must_follow","downstream_authorization"):
            assert set(phase[key]) <= known
    edges = {(d, p["phase_id"]) for p in phases for d in p["dependencies"] + p["must_follow"] if d in ids}
    remaining = set(ids)
    while remaining:
        ready = {n for n in remaining if not any((d,n) in edges for d in remaining)}
        assert ready
        remaining -= ready

def test_positive_verdict_is_compatible_with_registry() -> None:
    audit = (ROOT / "docs/architecture/MIP_CONVERSATIONAL_CONTROL_PLANE_PHASE_COMPLETENESS_AUDIT_001.md").read_text()
    assert "PHASE_DEFINITIONS_COMPLETE_IMPLEMENTATION_PLAN_ALLOWED" in audit
    data = json.loads(REGISTRY.read_text())
    assert all(p["status"] not in {"unknown","incomplete","requires_decision"} for p in data["phases"])
