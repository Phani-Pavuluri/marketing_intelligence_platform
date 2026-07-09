"""Tests for GeoX panel_exp integration boundary workflow (Stage 3A)."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from mip.contracts.deterministic_report import (
    ArtifactReference,
    EvidenceMode,
    GovernanceStatus,
    default_package_version_label,
)
from mip.contracts.geox_panel_exp_integration import (
    GeoXMaterializedInputAvailability,
    GeoXPanelExpIntegrationIssueCode,
    GeoXPanelExpIntegrationRequest,
    GeoXPanelExpIntegrationStatus,
    GeoXPostTestExperimentType,
)
from mip.contracts.geox_readout_input_resolution import (
    DatasetReference,
    DatasetSemanticType,
    DatasetSourceType,
    GeoXExperimentMetadataRef,
    GeoXReadoutInputHandoff,
    GeoXReadoutInputResolutionRequest,
    GeoXReadoutIntent,
    GeoXReadoutResolutionStatus,
    MappingConfirmationStatus,
    SpendColumnMapping,
    ValueMapping,
)
from mip.workflows.geox_panel_exp_integration import (
    build_geox_post_test_spend_adapter_input_plan,
    prepare_geox_panel_exp_integration,
)
from mip.workflows.geox_readout_input_resolution_pipeline import (
    resolve_geox_readout_inputs_with_source_inspection,
)

_INTEGRATION_SOURCE = Path("src/mip/workflows/geox_panel_exp_integration.py")
_NOW = datetime(2026, 7, 9, 12, 0, tzinfo=UTC)


def _artifact_ref() -> ArtifactReference:
    return ArtifactReference(
        artifact_id="geox-design:exp-1",
        artifact_type="geox_design",
        source_workflow="panel_exp.design",
        source_fixture_id_or_payload_ref="exp-1",
        source_commit_or_version=default_package_version_label(),
        created_at=_NOW,
        governance_status=GovernanceStatus.CANDIDATE,
        evidence_mode=EvidenceMode.DIAGNOSTIC_CANDIDATE,
        allowed_downstream_uses=["geox_readout"],
        forbidden_downstream_uses=[],
    )


def _spend_mapping(*, confirmed: bool = True) -> SpendColumnMapping:
    return SpendColumnMapping(
        date_week_column="week",
        geo_unit_column="dma",
        spend_amount_column="spend",
        currency_column="currency",
        confirmation_status=(
            MappingConfirmationStatus.USER_CONFIRMED
            if confirmed
            else MappingConfirmationStatus.CONFIRMATION_REQUIRED
        ),
    )


def _handoff(
    *,
    intent: GeoXReadoutIntent = GeoXReadoutIntent.READOUT_WITH_COST_PER,
    spend_mapping: SpendColumnMapping | None = None,
    value_mapping: ValueMapping | None = None,
    baseline: str | None = None,
) -> GeoXReadoutInputHandoff:
    return GeoXReadoutInputHandoff(
        request_id="handoff-1",
        readout_intent=intent,
        experiment_id="exp-1",
        assignment_artifact_ref=_artifact_ref(),
        spend_dataset_ref_optional=DatasetReference(
            dataset_ref_id="spend-1",
            source_type=DatasetSourceType.WAREHOUSE_TABLE,
            semantic_type=DatasetSemanticType.SPEND_PANEL,
            source_uri_or_handle="warehouse://spend",
            file_name_or_table_name="spend",
            declared_or_detected_columns=["week", "dma", "spend"],
            classification_confidence=0.9,
        ),
        spend_column_mapping_optional=spend_mapping,
        value_mapping_optional=value_mapping,
        spend_baseline_definition_optional=baseline,
        mip_resolution_status=GeoXReadoutResolutionStatus.READY_FOR_COST_PER_READOUT,
    )


def _request(
    handoff: GeoXReadoutInputHandoff,
    *,
    availability: GeoXMaterializedInputAvailability | None = None,
    lineage: dict[str, str] | None = None,
    allow_import: bool = False,
    allow_runtime_call: bool = False,
) -> GeoXPanelExpIntegrationRequest:
    return GeoXPanelExpIntegrationRequest(
        request_id="integration-1",
        handoff=handoff,
        materialized_input_availability=availability or GeoXMaterializedInputAvailability(),
        allow_panel_exp_import=allow_import,
        allow_panel_exp_runtime_call=allow_runtime_call,
        lineage=lineage or {},
    )


def _complete_lineage(experiment_type: str = "go_dark") -> dict[str, str]:
    return {
        "post_period_start": "2026-03-02",
        "post_period_end": "2026-04-01",
        "experiment_type": experiment_type,
        "baseline_or_counterfactual_available": "true",
        "assignment_join_keys_confirmed": "true",
    }


def _complete_availability() -> GeoXMaterializedInputAvailability:
    return GeoXMaterializedInputAvailability(
        has_materialized_spend_df=True,
        has_assignment_mapping=True,
        materialized_spend_ref_optional="inmemory://spend-df-1",
        materialized_assignment_ref_optional="inmemory://assignment-df-1",
    )


def test_cost_per_without_materialized_spend_blocked() -> None:
    result = prepare_geox_panel_exp_integration(_request(_handoff()))
    assert result.integration_status == (
        GeoXPanelExpIntegrationStatus.BLOCKED_MATERIALIZED_SPEND_INPUT_REQUIRED
    )
    assert GeoXPanelExpIntegrationIssueCode.MATERIALIZED_SPEND_DF_MISSING in result.issues


def test_materialized_spend_without_assignment_blocked() -> None:
    availability = GeoXMaterializedInputAvailability(has_materialized_spend_df=True)
    handoff = _handoff()
    handoff.assignment_artifact_ref = None
    result = prepare_geox_panel_exp_integration(_request(handoff, availability=availability))
    assert result.integration_status == (
        GeoXPanelExpIntegrationStatus.BLOCKED_MATERIALIZED_ASSIGNMENT_INPUT_REQUIRED
    )


def test_missing_confirmed_spend_mapping_blocked() -> None:
    availability = GeoXMaterializedInputAvailability(
        has_materialized_spend_df=True,
        has_assignment_mapping=True,
    )
    handoff = _handoff(spend_mapping=_spend_mapping(confirmed=False))
    result = prepare_geox_panel_exp_integration(
        _request(handoff, availability=availability, lineage=_complete_lineage())
    )
    assert result.integration_status == (
        GeoXPanelExpIntegrationStatus.BLOCKED_MISSING_CONFIRMED_SPEND_MAPPING
    )


def test_missing_post_period_dates_blocked() -> None:
    lineage = _complete_lineage()
    del lineage["post_period_start"]
    result = prepare_geox_panel_exp_integration(
        _request(
            _handoff(spend_mapping=_spend_mapping()),
            availability=_complete_availability(),
            lineage=lineage,
        )
    )
    assert result.integration_status == (
        GeoXPanelExpIntegrationStatus.BLOCKED_MISSING_POST_PERIOD_DATES
    )


def test_missing_experiment_type_blocked() -> None:
    lineage = _complete_lineage()
    lineage["experiment_type"] = "unknown"
    result = prepare_geox_panel_exp_integration(
        _request(
            _handoff(spend_mapping=_spend_mapping()),
            availability=_complete_availability(),
            lineage=lineage,
        )
    )
    assert result.integration_status == (
        GeoXPanelExpIntegrationStatus.BLOCKED_MISSING_EXPERIMENT_TYPE
    )


def test_go_dark_missing_baseline_blocked() -> None:
    result = prepare_geox_panel_exp_integration(
        _request(
            _handoff(spend_mapping=_spend_mapping()),
            availability=_complete_availability(),
            lineage={
                "post_period_start": "2026-03-02",
                "post_period_end": "2026-04-01",
                "experiment_type": "go_dark",
                "assignment_join_keys_confirmed": "true",
            },
        )
    )
    assert result.integration_status == (
        GeoXPanelExpIntegrationStatus.BLOCKED_MISSING_BASELINE_FOR_EXPERIMENT_TYPE
    )


def test_heavy_up_missing_baseline_blocked() -> None:
    result = prepare_geox_panel_exp_integration(
        _request(
            _handoff(spend_mapping=_spend_mapping()),
            availability=_complete_availability(),
            lineage={
                "post_period_start": "2026-03-02",
                "post_period_end": "2026-04-01",
                "experiment_type": "heavy_up",
                "assignment_join_keys_confirmed": "true",
            },
        )
    )
    assert result.integration_status == (
        GeoXPanelExpIntegrationStatus.BLOCKED_MISSING_BASELINE_FOR_EXPERIMENT_TYPE
    )


def test_kpi_lift_only_no_spend_readiness_requested() -> None:
    handoff = _handoff(intent=GeoXReadoutIntent.READOUT_WITH_LIFT)
    handoff.spend_dataset_ref_optional = None
    handoff.spend_column_mapping_optional = None
    result = prepare_geox_panel_exp_integration(_request(handoff))
    assert result.integration_status == (
        GeoXPanelExpIntegrationStatus.BLOCKED_NO_SPEND_READINESS_REQUESTED
    )


def test_complete_materialized_plan_ready_runtime_not_called() -> None:
    result = prepare_geox_panel_exp_integration(
        _request(
            _handoff(spend_mapping=_spend_mapping(), baseline="bau_weekly_spend"),
            availability=_complete_availability(),
            lineage=_complete_lineage("go_dark"),
        )
    )
    assert result.integration_status in {
        GeoXPanelExpIntegrationStatus.READY_TO_BUILD_POST_TEST_SPEND_INPUT,
        GeoXPanelExpIntegrationStatus.READY_TO_CALL_GEOX_POST_TEST_SPEND_RUNTIME,
    }
    assert result.runtime_called is False
    assert result.adapter_input_plan.experiment_type == GeoXPostTestExperimentType.GO_DARK


def test_runtime_call_disallowed_fail_closed() -> None:
    result = prepare_geox_panel_exp_integration(
        _request(
            _handoff(spend_mapping=_spend_mapping(), baseline="bau_weekly_spend"),
            availability=_complete_availability(),
            lineage=_complete_lineage("go_dark"),
            allow_import=True,
            allow_runtime_call=True,
        )
    )
    assert result.integration_status == (
        GeoXPanelExpIntegrationStatus.BLOCKED_PANEL_EXP_RUNTIME_NOT_CONFIGURED
    )
    assert result.runtime_called is False


def test_value_mapping_warns_not_consumed_by_spend_runtime() -> None:
    result = prepare_geox_panel_exp_integration(
        _request(
            _handoff(
                spend_mapping=_spend_mapping(),
                value_mapping=ValueMapping(
                    revenue_mapping_source="finance://rev",
                    confirmation_status=MappingConfirmationStatus.USER_CONFIRMED,
                ),
            ),
            availability=GeoXMaterializedInputAvailability(has_materialized_spend_df=True),
        )
    )
    assert (
        GeoXPanelExpIntegrationIssueCode.VALUE_MAPPING_NOT_CONSUMED_BY_SPEND_RUNTIME
        in result.issues
    )
    payload = result.model_dump_json().lower()
    assert "roi_value" not in payload
    assert "roas_value" not in payload


def test_integration_does_not_import_panel_exp() -> None:
    source = _INTEGRATION_SOURCE.read_text(encoding="utf-8")
    assert "import panel_exp" not in source
    assert "from panel_exp" not in source


def test_stage_2c_handoff_hits_materialization_blocker() -> None:
    resolution_request = GeoXReadoutInputResolutionRequest(
        request_id="stage-2c-compat",
        requested_intent=GeoXReadoutIntent.READOUT_WITH_COST_PER,
        dataset_refs=[
            DatasetReference(
                dataset_ref_id="kpi-raw",
                source_type=DatasetSourceType.UPLOADED_CSV,
                semantic_type=DatasetSemanticType.UNKNOWN_DATASET,
                source_uri_or_handle="file://kpi.csv",
                file_name_or_table_name="kpi.csv",
                declared_or_detected_columns=["week", "dma", "conversions"],
                classification_confidence=0.0,
            ),
            DatasetReference(
                dataset_ref_id="spend-raw",
                source_type=DatasetSourceType.UPLOADED_CSV,
                semantic_type=DatasetSemanticType.UNKNOWN_DATASET,
                source_uri_or_handle="file://spend.csv",
                file_name_or_table_name="spend.csv",
                declared_or_detected_columns=["week_start", "market", "spend", "currency"],
                classification_confidence=0.0,
            ),
        ],
        experiment_metadata=GeoXExperimentMetadataRef(
            experiment_id="exp-1",
            design_artifact_ref=_artifact_ref(),
            assignment_artifact_ref=_artifact_ref(),
            test_start_date="2026-01-01",
            test_end_date="2026-03-01",
            post_period_start="2026-03-02",
            post_period_end="2026-04-01",
        ),
        geox_runtime_available=True,
    )
    pipeline = resolve_geox_readout_inputs_with_source_inspection(resolution_request)
    assert pipeline.resolution_result.handoff is not None
    integration = prepare_geox_panel_exp_integration(
        GeoXPanelExpIntegrationRequest(
            request_id="stage-2c-compat",
            handoff=pipeline.resolution_result.handoff,
            lineage={
                "post_period_start": "2026-03-02",
                "post_period_end": "2026-04-01",
                "experiment_type": "go_dark",
            },
        )
    )
    assert integration.integration_status == (
        GeoXPanelExpIntegrationStatus.BLOCKED_MATERIALIZED_SPEND_INPUT_REQUIRED
    )


def test_build_adapter_plan_records_runtime_reference() -> None:
    plan = build_geox_post_test_spend_adapter_input_plan(_request(_handoff()))
    assert plan.runtime_reference.input_model == "PostTestSpendInput"
    assert plan.runtime_reference.primary_callable == "build_post_test_spend_evidence"
