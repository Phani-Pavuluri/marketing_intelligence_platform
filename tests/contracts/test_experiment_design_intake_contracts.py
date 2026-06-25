"""Tests for experiment design intake contracts."""

from datetime import UTC, datetime
from typing import Any

import pytest
from pydantic import ValidationError

from mip.contracts.experiment_design_intake import (
    ExperimentDesignEntryPath,
    ExperimentDesignIntake,
    ExperimentDesignObjective,
    ExperimentDesignStatus,
    ExperimentDesignTriggerReason,
    ExperimentDiagnosticRequest,
    ExperimentDiagnosticRequestStatus,
    ExperimentKpiFamily,
    ExperimentObjectiveCategory,
    MMMToGeoXDesignBridge,
    StandaloneGeoXDesignRequest,
)

_NOW = datetime(2026, 5, 28, 12, 0, tzinfo=UTC)

_FORBIDDEN_FRAGMENTS = (
    "matched markets",
    "mde is",
    "power is",
    "lift estimate",
    "budget allocation",
    "treatment assignment",
)


def _objective(**overrides: Any) -> ExperimentDesignObjective:
    base: dict[str, Any] = {
        "objective_id": "obj-001",
        "entry_path": ExperimentDesignEntryPath.STANDALONE_GEOX,
        "objective_category": ExperimentObjectiveCategory.AWARENESS,
        "business_question": "Measure awareness lift from Meta prospecting.",
        "created_at": _NOW,
    }
    base.update(overrides)
    return ExperimentDesignObjective(**base)


def test_experiment_design_objective_requires_core_fields() -> None:
    objective = _objective()
    assert objective.candidate_kpi_families == []
    assert objective.warnings == []


def test_experiment_design_objective_rejects_forbidden_claims() -> None:
    with pytest.raises(ValidationError, match="forbidden claim"):
        _objective(business_question="These are the matched markets for the test.")


def test_standalone_request_unknown_objective_requires_clarification_questions() -> None:
    with pytest.raises(ValidationError, match="clarification_questions"):
        StandaloneGeoXDesignRequest(
            request_id="req-001",
            business_question="Design a geo experiment.",
            objective_category=ExperimentObjectiveCategory.UNKNOWN,
            created_at=_NOW,
        )


def test_standalone_request_unknown_with_questions_valid() -> None:
    request = StandaloneGeoXDesignRequest(
        request_id="req-001",
        business_question="Design a geo experiment.",
        objective_category=ExperimentObjectiveCategory.UNKNOWN,
        clarification_questions=["What is the primary KPI?"],
        created_at=_NOW,
    )
    assert request.clarification_questions


def test_mmm_bridge_requires_why_experiment_needed() -> None:
    with pytest.raises(ValidationError, match="why_experiment_needed"):
        MMMToGeoXDesignBridge(
            bridge_id="bridge-001",
            trigger_reason=ExperimentDesignTriggerReason.CALIBRATION_GAP,
            why_experiment_needed="   ",
            created_at=_NOW,
        )


def test_experiment_design_intake_mmm_driven_requires_bridge() -> None:
    objective = _objective(entry_path=ExperimentDesignEntryPath.MMM_DRIVEN)
    with pytest.raises(ValidationError, match="mmm_bridge"):
        ExperimentDesignIntake(
            intake_id="intake-001",
            session_id="sess-001",
            recommendation_id="rec-001",
            entry_path=ExperimentDesignEntryPath.MMM_DRIVEN,
            objective=objective,
            created_at=_NOW,
        )


def test_experiment_design_intake_standalone_requires_request() -> None:
    objective = _objective()
    with pytest.raises(ValidationError, match="standalone_request"):
        ExperimentDesignIntake(
            intake_id="intake-001",
            session_id="sess-001",
            recommendation_id="rec-001",
            entry_path=ExperimentDesignEntryPath.STANDALONE_GEOX,
            objective=objective,
            created_at=_NOW,
        )


def test_diagnostic_request_blocked_requires_blocking_reasons() -> None:
    with pytest.raises(ValidationError, match="blocking_reasons"):
        ExperimentDiagnosticRequest(
            diagnostic_request_id="diag-001",
            experiment_intake_id="intake-001",
            session_id="sess-001",
            entry_path=ExperimentDesignEntryPath.STANDALONE_GEOX,
            objective_category=ExperimentObjectiveCategory.AWARENESS,
            status=ExperimentDiagnosticRequestStatus.BLOCKED,
            created_at=_NOW,
        )


def test_diagnostic_request_has_no_result_fields() -> None:
    request = ExperimentDiagnosticRequest(
        diagnostic_request_id="diag-001",
        experiment_intake_id="intake-001",
        session_id="sess-001",
        entry_path=ExperimentDesignEntryPath.STANDALONE_GEOX,
        objective_category=ExperimentObjectiveCategory.AWARENESS,
        status=ExperimentDiagnosticRequestStatus.READY_FOR_PANEL_EXP_DIAGNOSTICS,
        created_at=_NOW,
    )
    dumped = request.model_dump()
    forbidden_result_keys = {
        "mde",
        "power",
        "power_result",
        "matched_markets",
        "lift",
        "roi",
        "budget_recommendation",
        "treatment_assignment",
        "control_assignment",
        "effect_estimate",
    }
    assert forbidden_result_keys.isdisjoint(dumped.keys())
    serialized = str(dumped).lower()
    for fragment in _FORBIDDEN_FRAGMENTS:
        assert fragment not in serialized


def test_intake_status_enum_values() -> None:
    assert ExperimentDesignStatus.REQUIREMENTS_READY.value == "requirements_ready"
    assert ExperimentDiagnosticRequestStatus.READY_FOR_PANEL_EXP_DIAGNOSTICS.value == (
        "ready_for_panel_exp_diagnostics"
    )


def test_kpi_family_enum_values() -> None:
    assert ExperimentKpiFamily.AWARENESS_SEARCH.value == "awareness_search"
    assert ExperimentKpiFamily.CALIBRATION_ALIGNED.value == "calibration_aligned"
