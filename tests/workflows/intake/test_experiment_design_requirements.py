"""Tests for experiment design requirement helpers."""

from datetime import UTC, datetime
from typing import Any

from mip.contracts.experiment_design_intake import (
    ExperimentDesignEntryPath,
    ExperimentDesignStatus,
    ExperimentDesignTriggerReason,
    ExperimentDiagnosticRequestStatus,
    ExperimentKpiFamily,
    ExperimentObjectiveCategory,
    StandaloneGeoXDesignRequest,
)
from mip.contracts.intake import (
    DataGrain,
    GeoGrain,
    IntakeCandidatePath,
    IntakeIntendedUse,
    IntakePathRecommendation,
    IntakeRecommendationStatus,
    MeasurementIntakeSession,
    MeasurementWorkflowKind,
)
from mip.contracts.intake_assets import DataAssetType
from mip.workflows.intake.experiment_design import (
    build_experiment_design_data_requirements,
    build_experiment_design_intake,
    build_experiment_diagnostic_request,
    build_mmm_to_geox_bridge,
    suggest_kpi_families_for_objective,
    suggest_kpi_labels_for_families,
)

_NOW = datetime(2026, 5, 28, 12, 0, tzinfo=UTC)

_FORBIDDEN_FRAGMENTS = (
    "matched markets",
    "mde is",
    "power is",
    "lift estimate",
    "budget allocation",
    "treatment assignment",
    "control assignment",
    "effect estimate is",
)


def _session(**overrides: Any) -> MeasurementIntakeSession:
    base: dict[str, Any] = {
        "session_id": "sess-exp-001",
        "business_question": "Should we run a DMA-level Meta awareness test?",
        "intended_use": IntakeIntendedUse.GEO_EXPERIMENT_DESIGN,
        "workflow_kind": MeasurementWorkflowKind.GEOX,
        "time_grain": DataGrain.WEEKLY,
        "geo_grain": GeoGrain.DMA,
        "product_scope": "Acrobat",
        "platform_scope": "Meta",
        "market_scope": "US DMAs",
        "created_at": _NOW,
    }
    base.update(overrides)
    return MeasurementIntakeSession(**base)


def _recommendation(session: MeasurementIntakeSession) -> IntakePathRecommendation:
    return IntakePathRecommendation(
        recommendation_id="rec-exp-001",
        session_id=session.session_id,
        status=IntakeRecommendationStatus.RECOMMENDED,
        recommended_path=IntakeCandidatePath.GEO_EXPERIMENT_DESIGN,
        workflow_kind=session.workflow_kind,
        why_this_path="Geo experiment design path selected for standalone design intake.",
        created_at=_NOW,
    )


def _assert_no_forbidden_claims(*objects: Any) -> None:
    combined = " ".join(str(obj.model_dump()) for obj in objects).lower()
    for fragment in _FORBIDDEN_FRAGMENTS:
        assert fragment not in combined


def test_awareness_objective_maps_to_awareness_search_and_traffic() -> None:
    families = suggest_kpi_families_for_objective(ExperimentObjectiveCategory.AWARENESS)
    assert ExperimentKpiFamily.AWARENESS_SEARCH in families
    assert ExperimentKpiFamily.TRAFFIC in families


def test_demand_creation_maps_to_traffic_funnel_trials() -> None:
    families = suggest_kpi_families_for_objective(ExperimentObjectiveCategory.DEMAND_CREATION)
    assert ExperimentKpiFamily.TRAFFIC in families
    assert ExperimentKpiFamily.FUNNEL_ENGAGEMENT in families
    assert ExperimentKpiFamily.TRIALS_LEADS in families


def test_conversion_maps_to_conversion_sales_and_revenue_arr() -> None:
    families = suggest_kpi_families_for_objective(ExperimentObjectiveCategory.CONVERSION)
    assert ExperimentKpiFamily.CONVERSION_SALES in families
    assert ExperimentKpiFamily.REVENUE_ARR in families


def test_mmm_calibration_maps_to_calibration_aligned() -> None:
    families = suggest_kpi_families_for_objective(ExperimentObjectiveCategory.MMM_CALIBRATION)
    assert families == [ExperimentKpiFamily.CALIBRATION_ALIGNED]


def test_awareness_data_requirements_include_geo_kpi_spend_geo_mapping() -> None:
    from mip.contracts.experiment_design_intake import ExperimentDesignObjective

    objective = ExperimentDesignObjective(
        objective_id="obj-awareness",
        entry_path=ExperimentDesignEntryPath.STANDALONE_GEOX,
        objective_category=ExperimentObjectiveCategory.AWARENESS,
        business_question="Measure awareness.",
        geo_grain=GeoGrain.DMA,
        created_at=_NOW,
    )
    requirements = build_experiment_design_data_requirements(objective)
    assert requirements
    required = {asset for req in requirements for asset in req.required_data_assets}
    assert DataAssetType.OUTCOME_KPI_DATA in required
    assert DataAssetType.MEDIA_SPEND_DATA in required
    assert DataAssetType.MEDIA_EXPOSURE_DATA in required
    assert DataAssetType.GEO_MAPPING in required


def test_conversion_requirements_include_conversion_promo_seasonality() -> None:
    from mip.contracts.experiment_design_intake import ExperimentDesignObjective

    objective = ExperimentDesignObjective(
        objective_id="obj-conv",
        entry_path=ExperimentDesignEntryPath.STANDALONE_GEOX,
        objective_category=ExperimentObjectiveCategory.CONVERSION,
        business_question="Measure conversion lift.",
        geo_grain=GeoGrain.DMA,
        created_at=_NOW,
    )
    requirements = build_experiment_design_data_requirements(objective)
    required = {asset for req in requirements for asset in req.required_data_assets}
    assert DataAssetType.OUTCOME_KPI_DATA in required
    assert DataAssetType.MEDIA_SPEND_DATA in required
    assert DataAssetType.MEDIA_EXPOSURE_DATA in required
    assert DataAssetType.PRICING_PROMO_DATA in required
    assert DataAssetType.CALENDAR_SEASONALITY_DATA in required
    assert DataAssetType.GEO_MAPPING in required


def test_mmm_driven_intake_requires_mmm_bridge() -> None:
    session = _session(workflow_kind=MeasurementWorkflowKind.MMM)
    recommendation = _recommendation(session)
    bridge = build_mmm_to_geox_bridge(
        bridge_id="bridge-001",
        trigger_reason=ExperimentDesignTriggerReason.CALIBRATION_GAP,
        why_experiment_needed="MMM channel uncertainty requires geo validation.",
        objective_category=ExperimentObjectiveCategory.MMM_CALIBRATION,
        metric_id="conversions",
        estimand_id="incremental_conversions",
    )
    intake = build_experiment_design_intake(
        session,
        recommendation,
        entry_path=ExperimentDesignEntryPath.MMM_DRIVEN,
        objective_category=ExperimentObjectiveCategory.MMM_CALIBRATION,
        mmm_bridge=bridge,
    )
    assert intake.mmm_bridge is not None
    assert intake.entry_path == ExperimentDesignEntryPath.MMM_DRIVEN
    assert intake.mmm_bridge.requires_calibration_signal_output is True


def test_standalone_geox_intake_requires_standalone_request() -> None:
    session = _session()
    recommendation = _recommendation(session)
    standalone = StandaloneGeoXDesignRequest(
        request_id="standalone-001",
        business_question=session.business_question,
        objective_category=ExperimentObjectiveCategory.AWARENESS,
        product_scope="Acrobat",
        platform_scope="Meta",
        geo_grain=GeoGrain.DMA,
        market_scope="US DMAs",
        candidate_kpi_families=suggest_kpi_families_for_objective(
            ExperimentObjectiveCategory.AWARENESS
        ),
        primary_kpi_candidates=suggest_kpi_labels_for_families(
            suggest_kpi_families_for_objective(ExperimentObjectiveCategory.AWARENESS)
        ),
        created_at=_NOW,
    )
    intake = build_experiment_design_intake(
        session,
        recommendation,
        entry_path=ExperimentDesignEntryPath.STANDALONE_GEOX,
        objective_category=ExperimentObjectiveCategory.AWARENESS,
        standalone_request=standalone,
    )
    assert intake.standalone_request is not None
    assert intake.status == ExperimentDesignStatus.REQUIREMENTS_READY


def test_unknown_objective_produces_needs_clarification_with_questions() -> None:
    session = _session(product_scope=None, platform_scope=None, geo_grain=GeoGrain.UNKNOWN)
    recommendation = _recommendation(session)
    standalone = StandaloneGeoXDesignRequest(
        request_id="standalone-unknown",
        business_question="Design an experiment.",
        objective_category=ExperimentObjectiveCategory.UNKNOWN,
        clarification_questions=["What is the experiment objective?"],
        created_at=_NOW,
    )
    intake = build_experiment_design_intake(
        session,
        recommendation,
        entry_path=ExperimentDesignEntryPath.STANDALONE_GEOX,
        objective_category=ExperimentObjectiveCategory.UNKNOWN,
        standalone_request=standalone,
    )
    assert intake.status == ExperimentDesignStatus.NEEDS_CLARIFICATION
    assert intake.clarification_questions


def test_complete_standalone_dma_meta_awareness_produces_requirements_ready() -> None:
    session = _session()
    recommendation = _recommendation(session)
    standalone = StandaloneGeoXDesignRequest(
        request_id="standalone-dma-meta",
        business_question="DMA-level Meta awareness test for Acrobat.",
        objective_category=ExperimentObjectiveCategory.AWARENESS,
        product_scope="Acrobat",
        platform_scope="Meta",
        geo_grain=GeoGrain.DMA,
        market_scope="US DMAs",
        candidate_kpi_families=suggest_kpi_families_for_objective(
            ExperimentObjectiveCategory.AWARENESS
        ),
        primary_kpi_candidates=["visits", "BSV"],
        created_at=_NOW,
    )
    intake = build_experiment_design_intake(
        session,
        recommendation,
        entry_path=ExperimentDesignEntryPath.STANDALONE_GEOX,
        objective_category=ExperimentObjectiveCategory.AWARENESS,
        standalone_request=standalone,
    )
    assert intake.status == ExperimentDesignStatus.REQUIREMENTS_READY
    assert intake.data_requirements
    _assert_no_forbidden_claims(intake)


def test_diagnostic_request_from_ready_intake_is_ready_for_panel_exp() -> None:
    session = _session()
    recommendation = _recommendation(session)
    standalone = StandaloneGeoXDesignRequest(
        request_id="standalone-ready",
        business_question=session.business_question,
        objective_category=ExperimentObjectiveCategory.AWARENESS,
        product_scope="Acrobat",
        platform_scope="Meta",
        geo_grain=GeoGrain.DMA,
        market_scope="US DMAs",
        primary_kpi_candidates=["visits"],
        created_at=_NOW,
    )
    intake = build_experiment_design_intake(
        session,
        recommendation,
        entry_path=ExperimentDesignEntryPath.STANDALONE_GEOX,
        objective_category=ExperimentObjectiveCategory.AWARENESS,
        standalone_request=standalone,
    )
    diagnostic = build_experiment_diagnostic_request(intake)
    assert (
        diagnostic.status
        == ExperimentDiagnosticRequestStatus.READY_FOR_PANEL_EXP_DIAGNOSTICS
    )
    assert diagnostic.requires_power_diagnostic is True
    assert diagnostic.requires_matchability_diagnostic is True
    assert diagnostic.requires_duration_sensitivity is True
    _assert_no_forbidden_claims(diagnostic)


def test_diagnostic_request_from_needs_clarification_is_needs_data() -> None:
    session = _session(product_scope=None, platform_scope=None, geo_grain=GeoGrain.UNKNOWN)
    recommendation = _recommendation(session)
    standalone = StandaloneGeoXDesignRequest(
        request_id="standalone-clarify",
        business_question="Design an experiment.",
        objective_category=ExperimentObjectiveCategory.UNKNOWN,
        clarification_questions=["What is the primary KPI?"],
        created_at=_NOW,
    )
    intake = build_experiment_design_intake(
        session,
        recommendation,
        entry_path=ExperimentDesignEntryPath.STANDALONE_GEOX,
        objective_category=ExperimentObjectiveCategory.UNKNOWN,
        standalone_request=standalone,
    )
    diagnostic = build_experiment_diagnostic_request(intake)
    assert diagnostic.status == ExperimentDiagnosticRequestStatus.NEEDS_DATA


def test_mmm_calibration_bridge_requires_calibration_signal_output() -> None:
    bridge = build_mmm_to_geox_bridge(
        bridge_id="bridge-cal",
        trigger_reason=ExperimentDesignTriggerReason.CALIBRATION_GAP,
        why_experiment_needed="Calibration gap on paid social channel.",
        objective_category=ExperimentObjectiveCategory.MMM_CALIBRATION,
    )
    assert bridge.requires_calibration_signal_output is True

    session = _session(workflow_kind=MeasurementWorkflowKind.MMM)
    recommendation = _recommendation(session)
    intake = build_experiment_design_intake(
        session,
        recommendation,
        entry_path=ExperimentDesignEntryPath.MMM_DRIVEN,
        objective_category=ExperimentObjectiveCategory.MMM_CALIBRATION,
        mmm_bridge=bridge,
    )
    diagnostic = build_experiment_diagnostic_request(intake)
    assert diagnostic.requires_calibration_signal_output is True
