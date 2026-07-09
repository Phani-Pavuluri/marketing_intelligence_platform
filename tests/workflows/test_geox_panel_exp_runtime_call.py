"""Tests for GeoX panel_exp runtime-call workflow (Stage 3B)."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from mip.contracts.deterministic_report import (
    ArtifactReference,
    EvidenceMode,
    GovernanceStatus,
    default_package_version_label,
)
from mip.contracts.geox_fixture_materialization import (
    GeoXFixtureDatasetMaterializationRequest,
    GeoXFixtureMaterializationRequest,
    GeoXFixtureMaterializationResult,
    GeoXFixtureMaterializationStatus,
    GeoXMaterializedDatasetRole,
)
from mip.contracts.geox_panel_exp_integration import (
    GeoXPanelExpIntegrationRequest,
    GeoXPanelExpIntegrationStatus,
    GeoXPostTestSpendAdapterInputPlan,
)
from mip.contracts.geox_panel_exp_runtime_call import (
    CLAIM_AUTHORIZATION_OWNER,
    GeoXPanelExpRuntimeCallIssueCode,
    GeoXPanelExpRuntimeCallMode,
    GeoXPanelExpRuntimeCallRequest,
    GeoXPanelExpRuntimeCallResult,
    GeoXPanelExpRuntimeCallStatus,
)
from mip.contracts.geox_readout_input_resolution import (
    DatasetReference,
    DatasetSemanticType,
    DatasetSourceType,
    GeoXExperimentMetadataRef,
    GeoXReadoutInputResolutionRequest,
    GeoXReadoutIntent,
    MappingConfirmationStatus,
    SpendColumnMapping,
)
from mip.workflows.geox_fixture_materialization import (
    build_materialized_input_availability_from_fixture_result,
    materialize_geox_readout_fixtures,
)
from mip.workflows.geox_panel_exp_integration import build_geox_post_test_spend_adapter_input_plan
from mip.workflows.geox_panel_exp_runtime_call import (
    call_geox_post_test_spend_runtime_for_fixture,
)
from mip.workflows.geox_readout_input_resolution_pipeline import (
    resolve_geox_readout_inputs_with_source_inspection,
)

_FIXTURE_ROOT = Path("examples/fixtures/geox_readout_materialization")
_MANIFEST_PATH = _FIXTURE_ROOT / "manifest.json"
_SPEND_PATH = str(_FIXTURE_ROOT / "spend_panel.csv")
_ASSIGNMENT_PATH = str(_FIXTURE_ROOT / "assignment_table.csv")
_RUNTIME_SOURCE = Path("src/mip/workflows/geox_panel_exp_runtime_call.py")
_NOW = datetime(2026, 7, 9, 12, 0, tzinfo=UTC)

panel_exp = pytest.importorskip("panel_exp")


def _artifact_ref() -> ArtifactReference:
    return ArtifactReference(
        artifact_id="geox-design:exp-fixture-1",
        artifact_type="geox_design",
        source_workflow="panel_exp.design",
        source_fixture_id_or_payload_ref="exp-fixture-1",
        source_commit_or_version=default_package_version_label(),
        created_at=_NOW,
        governance_status=GovernanceStatus.CANDIDATE,
        evidence_mode=EvidenceMode.DIAGNOSTIC_CANDIDATE,
        allowed_downstream_uses=["geox_readout"],
        forbidden_downstream_uses=[],
    )


def _fixture_ref(
    *,
    dataset_ref_id: str,
    path: str,
    semantic_type: DatasetSemanticType,
    columns: list[str],
) -> DatasetReference:
    return DatasetReference(
        dataset_ref_id=dataset_ref_id,
        source_type=DatasetSourceType.REGISTERED_ARTIFACT,
        semantic_type=semantic_type,
        source_uri_or_handle=f"registered://{path}",
        file_name_or_table_name=path,
        declared_or_detected_columns=columns,
        classification_confidence=0.9,
    )


def _materialize_fixture_pair() -> GeoXFixtureMaterializationResult:
    return materialize_geox_readout_fixtures(
        GeoXFixtureMaterializationRequest(
            request_id="fixture-runtime-call",
            dataset_requests=[
                GeoXFixtureDatasetMaterializationRequest(
                    dataset_ref=_fixture_ref(
                        dataset_ref_id="geox-fixture-spend-panel",
                        path=_SPEND_PATH,
                        semantic_type=DatasetSemanticType.SPEND_PANEL,
                        columns=["date", "dma", "spend", "currency"],
                    ),
                    role=GeoXMaterializedDatasetRole.SPEND,
                    required_columns=["date", "dma", "spend", "currency"],
                ),
                GeoXFixtureDatasetMaterializationRequest(
                    dataset_ref=_fixture_ref(
                        dataset_ref_id="geox-fixture-assignment-table",
                        path=_ASSIGNMENT_PATH,
                        semantic_type=DatasetSemanticType.ASSIGNMENT_TABLE,
                        columns=["dma", "cell", "treatment"],
                    ),
                    role=GeoXMaterializedDatasetRole.ASSIGNMENT,
                    required_columns=["dma", "cell", "treatment"],
                ),
            ],
        )
    )


def _ready_adapter_plan(
    fixture_result: GeoXFixtureMaterializationResult,
) -> GeoXPostTestSpendAdapterInputPlan:
    from mip.contracts.geox_readout_input_resolution import (
        GeoXReadoutInputHandoff,
        GeoXReadoutResolutionStatus,
    )

    handoff = GeoXReadoutInputHandoff(
        request_id="handoff-fixture",
        readout_intent=GeoXReadoutIntent.READOUT_WITH_COST_PER,
        experiment_id="exp-fixture-1",
        assignment_artifact_ref=_artifact_ref(),
        spend_dataset_ref_optional=_fixture_ref(
            dataset_ref_id="geox-fixture-spend-panel",
            path=_SPEND_PATH,
            semantic_type=DatasetSemanticType.SPEND_PANEL,
            columns=["date", "dma", "spend", "currency"],
        ),
        spend_column_mapping_optional=SpendColumnMapping(
            date_week_column="date",
            geo_unit_column="dma",
            spend_amount_column="spend",
            currency_column="currency",
            confirmation_status=MappingConfirmationStatus.USER_CONFIRMED,
        ),
        mip_resolution_status=GeoXReadoutResolutionStatus.READY_FOR_COST_PER_READOUT,
    )
    availability = build_materialized_input_availability_from_fixture_result(fixture_result)
    return build_geox_post_test_spend_adapter_input_plan(
        GeoXPanelExpIntegrationRequest(
            request_id="integration-fixture",
            handoff=handoff,
            materialized_input_availability=availability,
            lineage={
                "post_period_start": "2026-01-01",
                "post_period_end": "2026-01-31",
                "experiment_type": "holdout",
                "treatment_control_comparators_available": "true",
                "assignment_join_keys_confirmed": "true",
            },
        )
    )


def _runtime_request(
    *,
    plan: GeoXPostTestSpendAdapterInputPlan,
    fixture_result: GeoXFixtureMaterializationResult | None,
    allow_runtime_call: bool = False,
) -> GeoXPanelExpRuntimeCallRequest:
    return GeoXPanelExpRuntimeCallRequest(
        request_id="runtime-call-1",
        adapter_input_plan=plan,
        fixture_materialization_result=fixture_result,
        call_mode=GeoXPanelExpRuntimeCallMode.FIXTURE_ONLY,
        allow_runtime_call=allow_runtime_call,
    )


def test_runtime_call_disabled_blocked() -> None:
    fixture_result = _materialize_fixture_pair()
    plan = _ready_adapter_plan(fixture_result)
    result = call_geox_post_test_spend_runtime_for_fixture(
        _runtime_request(plan=plan, fixture_result=fixture_result, allow_runtime_call=False)
    )
    assert result.status == GeoXPanelExpRuntimeCallStatus.BLOCKED_RUNTIME_CALL_NOT_ALLOWED
    assert result.runtime_called is False
    assert GeoXPanelExpRuntimeCallIssueCode.RUNTIME_CALL_NOT_ALLOWED in result.issues


def test_missing_fixture_materialization_blocked() -> None:
    fixture_result = _materialize_fixture_pair()
    plan = _ready_adapter_plan(fixture_result)
    result = call_geox_post_test_spend_runtime_for_fixture(
        GeoXPanelExpRuntimeCallRequest(
            request_id="runtime-call-1",
            adapter_input_plan=plan,
            fixture_materialization_result=None,
            allow_runtime_call=True,
        )
    )
    assert result.status == GeoXPanelExpRuntimeCallStatus.BLOCKED_FIXTURE_MATERIALIZATION_REQUIRED
    assert result.runtime_called is False


def test_missing_materialized_spend_blocked() -> None:
    fixture_result = _materialize_fixture_pair()
    fixture_result = fixture_result.model_copy(update={"spend_dataset": None})
    plan = _ready_adapter_plan(fixture_result)
    result = call_geox_post_test_spend_runtime_for_fixture(
        _runtime_request(plan=plan, fixture_result=fixture_result, allow_runtime_call=True)
    )
    assert result.status == GeoXPanelExpRuntimeCallStatus.BLOCKED_MATERIALIZED_SPEND_INPUT_REQUIRED
    assert GeoXPanelExpRuntimeCallIssueCode.MATERIALIZED_SPEND_DF_MISSING in result.issues


def test_missing_materialized_assignment_blocked() -> None:
    fixture_result = _materialize_fixture_pair()
    fixture_result = fixture_result.model_copy(update={"assignment_dataset": None})
    plan = _ready_adapter_plan(fixture_result)
    result = call_geox_post_test_spend_runtime_for_fixture(
        _runtime_request(plan=plan, fixture_result=fixture_result, allow_runtime_call=True)
    )
    assert result.status == (
        GeoXPanelExpRuntimeCallStatus.BLOCKED_MATERIALIZED_ASSIGNMENT_INPUT_REQUIRED
    )


def test_adapter_input_plan_not_ready_blocked() -> None:
    fixture_result = _materialize_fixture_pair()
    plan = _ready_adapter_plan(fixture_result)
    plan = plan.model_copy(
        update={
            "integration_status": (
                GeoXPanelExpIntegrationStatus.BLOCKED_MISSING_CONFIRMED_SPEND_MAPPING
            ),
            "ready_to_call_runtime": False,
        }
    )
    result = call_geox_post_test_spend_runtime_for_fixture(
        _runtime_request(plan=plan, fixture_result=fixture_result, allow_runtime_call=True)
    )
    assert result.status == GeoXPanelExpRuntimeCallStatus.BLOCKED_POST_TEST_SPEND_INPUT_BUILD_FAILED
    assert result.runtime_called is False


def test_successful_fixture_runtime_call() -> None:
    fixture_result = _materialize_fixture_pair()
    plan = _ready_adapter_plan(fixture_result)
    assert plan.integration_status in {
        GeoXPanelExpIntegrationStatus.READY_TO_BUILD_POST_TEST_SPEND_INPUT,
        GeoXPanelExpIntegrationStatus.READY_TO_CALL_GEOX_POST_TEST_SPEND_RUNTIME,
    }
    result = call_geox_post_test_spend_runtime_for_fixture(
        _runtime_request(plan=plan, fixture_result=fixture_result, allow_runtime_call=True)
    )
    assert result.status == GeoXPanelExpRuntimeCallStatus.CALLED_PANEL_EXP_RUNTIME
    assert result.runtime_called is True
    assert result.post_test_spend_evidence_artifact is not None
    assert result.trusted_readout_spend_handoff_artifact is not None
    assert result.post_test_spend_evidence_artifact.readiness_status
    assert (
        result.post_test_spend_evidence_artifact.claim_authorization_owner
        == CLAIM_AUTHORIZATION_OWNER
    )


def test_package_computed_spend_delta_labeled_as_package_output() -> None:
    fixture_result = _materialize_fixture_pair()
    plan = _ready_adapter_plan(fixture_result)
    result = call_geox_post_test_spend_runtime_for_fixture(
        _runtime_request(plan=plan, fixture_result=fixture_result, allow_runtime_call=True)
    )
    artifact = result.post_test_spend_evidence_artifact
    assert artifact is not None
    summary = artifact.package_output_summary
    assert "package_computed_spend_delta" in summary
    assert summary["package_computed_spend_delta"] is not None
    assert "spend_delta" not in artifact.model_dump()


def test_trusted_readout_handoff_created() -> None:
    fixture_result = _materialize_fixture_pair()
    plan = _ready_adapter_plan(fixture_result)
    result = call_geox_post_test_spend_runtime_for_fixture(
        _runtime_request(plan=plan, fixture_result=fixture_result, allow_runtime_call=True)
    )
    handoff = result.trusted_readout_spend_handoff_artifact
    assert handoff is not None
    assert handoff.spend_readiness_summary
    assert isinstance(handoff.blocked_efficiency_metrics, list)
    assert handoff.claim_authorization_owner == CLAIM_AUTHORIZATION_OWNER
    assert handoff.package_handoff_summary.get("roi_claim_authorization_status") in {
        "NOT_EVALUATED",
        None,
    }


def test_import_failure_path() -> None:
    fixture_result = _materialize_fixture_pair()
    plan = _ready_adapter_plan(fixture_result)

    def _raise_import() -> None:
        msg = "simulated panel_exp import failure"
        raise ImportError(msg)

    with patch(
        "mip.workflows.geox_panel_exp_runtime_call._import_panel_exp_runtime",
        side_effect=_raise_import,
    ):
        result = call_geox_post_test_spend_runtime_for_fixture(
            _runtime_request(plan=plan, fixture_result=fixture_result, allow_runtime_call=True)
        )
    assert result.status == GeoXPanelExpRuntimeCallStatus.BLOCKED_PANEL_EXP_IMPORT_FAILED
    assert GeoXPanelExpRuntimeCallIssueCode.PANEL_EXP_IMPORT_FAILED in result.issues


def test_no_production_loader_path() -> None:
    blocked = materialize_geox_readout_fixtures(
        GeoXFixtureMaterializationRequest(
            request_id="warehouse-blocked",
            dataset_requests=[
                GeoXFixtureDatasetMaterializationRequest(
                    dataset_ref=DatasetReference(
                        dataset_ref_id="warehouse-spend",
                        source_type=DatasetSourceType.WAREHOUSE_TABLE,
                        semantic_type=DatasetSemanticType.SPEND_PANEL,
                        source_uri_or_handle="warehouse://spend",
                        file_name_or_table_name="spend",
                        declared_or_detected_columns=["date", "dma", "spend"],
                        classification_confidence=0.9,
                    ),
                    role=GeoXMaterializedDatasetRole.SPEND,
                    required_columns=["date", "dma", "spend"],
                ),
            ],
        )
    )
    assert blocked.status == GeoXFixtureMaterializationStatus.BLOCKED_SOURCE_TYPE_UNSUPPORTED


def test_no_roi_roas_claim_authorization_by_mip() -> None:
    fixture_result = _materialize_fixture_pair()
    plan = _ready_adapter_plan(fixture_result)
    result = call_geox_post_test_spend_runtime_for_fixture(
        _runtime_request(plan=plan, fixture_result=fixture_result, allow_runtime_call=True)
    )
    payload = result.model_dump_json().lower()
    assert "mip_authorized" not in payload
    assert GeoXPanelExpRuntimeCallIssueCode.ROI_ROAS_NOT_COMPUTED_IN_MIP in result.issues
    handoff = result.trusted_readout_spend_handoff_artifact
    assert handoff is not None
    assert handoff.package_handoff_summary.get("roas") == "NOT_COMPUTED"


def test_workflow_imports_panel_exp_only_in_runtime_module() -> None:
    source = _RUNTIME_SOURCE.read_text(encoding="utf-8")
    assert "from panel_exp" in source
    assert "_import_panel_exp_runtime" in source


def _refs_from_manifest() -> list[DatasetReference]:
    manifest = json.loads(_MANIFEST_PATH.read_text(encoding="utf-8"))
    refs: list[DatasetReference] = []
    for dataset in manifest["datasets"]:
        semantic = (
            DatasetSemanticType.SPEND_PANEL
            if dataset["role"] == "spend"
            else DatasetSemanticType.ASSIGNMENT_TABLE
        )
        refs.append(
            DatasetReference(
                dataset_ref_id=dataset["dataset_ref_id"],
                source_type=DatasetSourceType.REGISTERED_ARTIFACT,
                semantic_type=semantic,
                source_uri_or_handle=f"registered://{dataset['file_path']}",
                file_name_or_table_name=dataset["file_path"],
                declared_or_detected_columns=dataset["required_columns"],
                classification_confidence=0.9,
            )
        )
    return refs


def run_controlled_geox_fixture_runtime_call_flow() -> GeoXPanelExpRuntimeCallResult:
    """End-to-end controlled fixture flow for Stage 3B validation."""
    dataset_refs = _refs_from_manifest()
    dataset_refs.append(
        _fixture_ref(
            dataset_ref_id="geox-fixture-kpi-panel",
            path=str(_FIXTURE_ROOT / "spend_panel.csv"),
            semantic_type=DatasetSemanticType.KPI_PANEL,
            columns=["date", "dma", "conversions"],
        )
    )
    resolution_request = GeoXReadoutInputResolutionRequest(
        request_id="full-flow",
        requested_intent=GeoXReadoutIntent.READOUT_WITH_COST_PER,
        dataset_refs=dataset_refs,
        experiment_metadata=GeoXExperimentMetadataRef(
            experiment_id="exp-fixture-1",
            design_artifact_ref=_artifact_ref(),
            assignment_artifact_ref=_artifact_ref(),
            test_start_date="2026-01-01",
            test_end_date="2026-01-31",
            post_period_start="2026-01-01",
            post_period_end="2026-01-31",
        ),
        geox_runtime_available=True,
        lineage={"experiment_type": "holdout"},
    )
    pipeline = resolve_geox_readout_inputs_with_source_inspection(resolution_request)
    handoff = pipeline.resolution_result.handoff
    assert handoff is not None

    manifest = json.loads(_MANIFEST_PATH.read_text(encoding="utf-8"))
    dataset_requests = [
        GeoXFixtureDatasetMaterializationRequest(
            dataset_ref=next(
                ref for ref in dataset_refs if ref.dataset_ref_id == dataset["dataset_ref_id"]
            ),
            role=(
                GeoXMaterializedDatasetRole.SPEND
                if dataset["role"] == "spend"
                else GeoXMaterializedDatasetRole.ASSIGNMENT
            ),
            required_columns=dataset["required_columns"],
        )
        for dataset in manifest["datasets"]
    ]
    fixture_result = materialize_geox_readout_fixtures(
        GeoXFixtureMaterializationRequest(
            request_id="full-flow-fixture",
            dataset_requests=dataset_requests,
        )
    )
    availability = build_materialized_input_availability_from_fixture_result(fixture_result)
    plan = build_geox_post_test_spend_adapter_input_plan(
        GeoXPanelExpIntegrationRequest(
            request_id="full-flow-integration",
            handoff=handoff,
            materialized_input_availability=availability,
            lineage={
                "post_period_start": "2026-01-01",
                "post_period_end": "2026-01-31",
                "experiment_type": "holdout",
                "treatment_control_comparators_available": "true",
                "assignment_join_keys_confirmed": "true",
            },
        )
    )
    return call_geox_post_test_spend_runtime_for_fixture(
        GeoXPanelExpRuntimeCallRequest(
            request_id="full-flow-runtime",
            adapter_input_plan=plan,
            fixture_materialization_result=fixture_result,
            allow_runtime_call=True,
        )
    )


def test_full_controlled_fixture_flow() -> None:
    result = run_controlled_geox_fixture_runtime_call_flow()
    assert result.status == GeoXPanelExpRuntimeCallStatus.CALLED_PANEL_EXP_RUNTIME
    assert result.runtime_called is True
    assert result.post_test_spend_evidence_artifact is not None
    assert result.trusted_readout_spend_handoff_artifact is not None
    assert result.post_test_spend_evidence_artifact.experiment_id == "exp-fixture-1"
