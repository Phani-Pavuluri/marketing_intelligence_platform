"""Tests for adapter governance wiring."""

from datetime import date, timedelta

import pytest

from mip.adapters.base import (
    AdapterOutputBundle,
    AdapterRunKind,
    AdapterRunStatus,
    validate_adapter_output,
)
from mip.adapters.geox import build_geox_adapter_output_placeholder
from mip.adapters.governance import (
    adapter_output_to_decision_surface,
    adapter_output_to_experiment_evidence,
    gate_outcomes_for_adapter_output,
    register_adapter_output,
    trust_report_for_adapter_output,
)
from mip.adapters.mmm import build_mmm_adapter_output_placeholder
from mip.contracts import ConfidenceTier, ExperimentEvidence
from mip.contracts.decision_surface import DecisionSurface
from mip.evaluation.gates import GateDecision
from mip.evidence.registry import EvidenceRegistry
from mip.workflows.configs import draft_geox_config, draft_mmm_config
from mip.workflows.configs.geox import GeoXConfigDraft
from mip.workflows.configs.mmm import MMMConfigDraft
from mip.workflows.intake import (
    BusinessObjective,
    BusinessObjectiveType,
    evaluate_objective_feasibility,
)
from mip.workflows.readiness.profile import profile_to_availability
from mip.workflows.readiness.report import build_readiness_from_records


def _long_history_rows() -> list[dict[str, object]]:
    return [
        {
            "date": (date(2024, 1, 1) + timedelta(days=7 * index)).isoformat(),
            "spend": 100,
            "conversions": 10,
            "channel": "search" if index % 2 == 0 else "social",
            "geo": "us" if index % 2 == 0 else "uk",
        }
        for index in range(60)
    ]


def _experiment_rows() -> list[dict[str, object]]:
    return [
        {
            "date": (date(2024, 1, 1) + timedelta(days=7 * index)).isoformat(),
            "geo": "dma_a" if index % 2 == 0 else "dma_b",
            "outcome": 100 + index,
            "spend": 50,
        }
        for index in range(60)
    ]


def _mmm_draft() -> MMMConfigDraft:
    objective = BusinessObjective(objective_type=BusinessObjectiveType.CONVERSION_ROI)
    readiness = build_readiness_from_records(_long_history_rows(), objective)
    feasibility = evaluate_objective_feasibility(
        objective,
        profile_to_availability(readiness.profile),
    )
    return draft_mmm_config(objective, feasibility, readiness)


def _geox_draft() -> GeoXConfigDraft:
    objective = BusinessObjective(objective_type=BusinessObjectiveType.EXPERIMENT_DESIGN)
    readiness = build_readiness_from_records(_experiment_rows(), objective)
    feasibility = evaluate_objective_feasibility(
        objective,
        profile_to_availability(readiness.profile),
    )
    return draft_geox_config(objective, feasibility, readiness)


def test_geox_completed_placeholder_maps_to_experiment_evidence() -> None:
    output = build_geox_adapter_output_placeholder(_geox_draft())
    evidence = adapter_output_to_experiment_evidence(output)
    assert isinstance(evidence, ExperimentEvidence)
    assert evidence.evidence_id.startswith("adapter:geox:")
    assert evidence.status == "draft"
    assert "adapter_fixture_placeholder_only" in evidence.estimand.unsupported_claims


def test_mmm_completed_placeholder_maps_to_decision_surface() -> None:
    output = build_mmm_adapter_output_placeholder(_mmm_draft())
    surface = adapter_output_to_decision_surface(output)
    assert isinstance(surface, DecisionSurface)
    assert surface.surface_id.startswith("adapter:mmm:")
    assert surface.certification_status == "draft"
    assert "adapter_fixture_placeholder_only" in surface.warnings


def test_geox_output_does_not_map_to_decision_surface() -> None:
    output = build_geox_adapter_output_placeholder(_geox_draft())
    with pytest.raises(ValueError, match="mmm mapping requires mmm adapter output"):
        adapter_output_to_decision_surface(output)


def test_mmm_output_does_not_map_to_experiment_evidence() -> None:
    output = build_mmm_adapter_output_placeholder(_mmm_draft())
    with pytest.raises(ValueError, match="geox mapping requires geox adapter output"):
        adapter_output_to_experiment_evidence(output)


def test_blocked_output_produces_blocked_trust_report() -> None:
    draft = _mmm_draft()
    output = AdapterOutputBundle(
        kind=AdapterRunKind.MMM,
        status=AdapterRunStatus.BLOCKED,
        source_config_marker=draft.metadata.generated_marker,
        reason="adapter run blocked before execution",
        mmm_output=None,
    )
    report = trust_report_for_adapter_output(output)
    assert report.confidence_tier == ConfidenceTier.BLOCKED
    assert not report.diagnostics.passed


def test_completed_output_goes_through_existing_gates() -> None:
    output = build_geox_adapter_output_placeholder(_geox_draft())
    outcomes = gate_outcomes_for_adapter_output(output)
    assert len(outcomes) == 1
    assert outcomes[0].decision in (GateDecision.PASS, GateDecision.WARN, GateDecision.BLOCK)

    report = trust_report_for_adapter_output(output)
    assert report.uncertainty_summary["gate_count"] == 1


def test_registry_wiring_stores_geox_evidence() -> None:
    registry = EvidenceRegistry()
    output = build_geox_adapter_output_placeholder(_geox_draft())
    result = register_adapter_output(registry, output)
    assert result.registered_in_registry is True
    assert isinstance(result.artifact, ExperimentEvidence)
    assert registry.get_evidence(result.artifact.evidence_id) == result.artifact
    assert result.trust_report.output_id == result.artifact.evidence_id


def test_registry_wiring_keeps_mmm_surface_out_of_registry() -> None:
    registry = EvidenceRegistry()
    output = build_mmm_adapter_output_placeholder(_mmm_draft())
    result = register_adapter_output(registry, output)
    assert result.registered_in_registry is False
    assert isinstance(result.artifact, DecisionSurface)
    assert len(registry) == 0
    assert result.trust_report.output_type == "decision_surface"


def test_forbidden_claim_text_is_rejected() -> None:
    draft = _geox_draft()
    output = AdapterOutputBundle(
        kind=AdapterRunKind.GEOX,
        status=AdapterRunStatus.FAILED,
        source_config_marker=draft.metadata.generated_marker,
        reason="estimated lift from model results",
        geox_output=None,
    )
    with pytest.raises(ValueError, match="forbidden claim phrase"):
        validate_adapter_output(output)


def test_public_imports() -> None:
    from mip.adapters.governance import (
        AdapterRegistrationResult,
        adapter_output_to_decision_surface,
        adapter_output_to_experiment_evidence,
        register_adapter_output,
        trust_report_for_adapter_output,
    )

    assert callable(adapter_output_to_experiment_evidence)
    assert callable(adapter_output_to_decision_surface)
    assert callable(trust_report_for_adapter_output)
    assert callable(register_adapter_output)
    assert AdapterRegistrationResult is not None
