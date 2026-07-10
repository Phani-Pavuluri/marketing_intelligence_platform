"""GeoX uploaded CSV runtime bridge workflow.

Bridges shared uploaded CSV materialization + GeoX adapter outputs into the existing
package post-test spend runtime path. Does not re-read CSVs.
"""

from __future__ import annotations

from typing import Any

from mip.contracts.geox_panel_exp_integration import (
    GeoXMaterializedInputAvailability,
    GeoXPanelExpIntegrationStatus,
    GeoXPostTestExperimentType,
    GeoXPostTestSpendAdapterInputPlan,
)
from mip.contracts.geox_panel_exp_runtime_call import (
    CLAIM_AUTHORIZATION_OWNER,
)
from mip.contracts.geox_uploaded_csv_adapter import (
    GeoXUploadedCSVAdapterResult,
    GeoXUploadedCSVAdapterStatus,
    GeoXUploadedCSVRole,
)
from mip.contracts.geox_uploaded_csv_runtime_bridge import (
    _REQUIRED_SPEND_COLUMN_MAPPING_FIELDS,
    GeoXUploadedCSVRuntimeBridgeIssueCode,
    GeoXUploadedCSVRuntimeBridgeRequest,
    GeoXUploadedCSVRuntimeBridgeResult,
    GeoXUploadedCSVRuntimeBridgeStatus,
    GeoXUploadedCSVRuntimeColumnMapping,
)
from mip.contracts.uploaded_csv_materialization import (
    MaterializedTabularDataset,
    UploadedCSVMaterializationResult,
    UploadedCSVMaterializationStatus,
)
from mip.workflows.geox_panel_exp_runtime_call import (
    _evidence_artifact_from_package,
    _handoff_artifact_from_package,
    _import_panel_exp_runtime,
)

_READY_MATERIALIZATION_STATUSES = {
    UploadedCSVMaterializationStatus.MATERIALIZED,
    UploadedCSVMaterializationStatus.MATERIALIZED_WITH_WARNINGS,
}
_READY_ADAPTER_STATUSES = {
    GeoXUploadedCSVAdapterStatus.ADAPTED,
    GeoXUploadedCSVAdapterStatus.ADAPTED_WITH_WARNINGS,
}


def call_geox_post_test_spend_runtime_for_uploaded_csvs(
    request: GeoXUploadedCSVRuntimeBridgeRequest,
) -> GeoXUploadedCSVRuntimeBridgeResult:
    """Call package post-test spend runtime using uploaded CSV materialized DataFrames."""
    lineage = {
        **request.lineage,
        "runtime_bridge_stage": "geox_uploaded_csv_runtime_bridge",
        "runtime_call_mode": "uploaded_csv_materialized",
    }
    warnings = list(dict.fromkeys(request.warnings))
    issues: list[GeoXUploadedCSVRuntimeBridgeIssueCode] = [
        GeoXUploadedCSVRuntimeBridgeIssueCode.LINEAGE_PRESERVED,
        GeoXUploadedCSVRuntimeBridgeIssueCode.CSV_REPARSE_AVOIDED,
    ]

    if request.materialization_result is None:
        return _blocked(
            request.request_id,
            GeoXUploadedCSVRuntimeBridgeStatus.BLOCKED_MISSING_MATERIALIZATION_RESULT,
            issues + [GeoXUploadedCSVRuntimeBridgeIssueCode.MISSING_MATERIALIZATION_RESULT],
            warnings,
            lineage,
        )

    materialization = request.materialization_result
    warnings.extend(materialization.warnings)
    lineage.update(materialization.lineage)

    if materialization.status not in _READY_MATERIALIZATION_STATUSES:
        return _blocked(
            request.request_id,
            GeoXUploadedCSVRuntimeBridgeStatus.BLOCKED_MATERIALIZATION_NOT_READY,
            issues + [GeoXUploadedCSVRuntimeBridgeIssueCode.MATERIALIZATION_NOT_READY],
            warnings,
            lineage,
        )

    if request.adapter_result is None:
        return _blocked(
            request.request_id,
            GeoXUploadedCSVRuntimeBridgeStatus.BLOCKED_MISSING_ADAPTER_RESULT,
            issues + [GeoXUploadedCSVRuntimeBridgeIssueCode.MISSING_ADAPTER_RESULT],
            warnings,
            lineage,
        )

    adapter = request.adapter_result
    warnings.extend(adapter.warnings)
    lineage.update(adapter.lineage)

    if adapter.status not in _READY_ADAPTER_STATUSES:
        return _blocked(
            request.request_id,
            GeoXUploadedCSVRuntimeBridgeStatus.BLOCKED_ADAPTER_NOT_READY,
            issues + [GeoXUploadedCSVRuntimeBridgeIssueCode.ADAPTER_NOT_READY],
            warnings,
            lineage,
        )

    missing_mapping = _missing_required_column_mapping(request.column_mapping)
    if missing_mapping:
        return _blocked(
            request.request_id,
            GeoXUploadedCSVRuntimeBridgeStatus.BLOCKED_MISSING_REQUIRED_COLUMN_MAPPING,
            issues + [GeoXUploadedCSVRuntimeBridgeIssueCode.MISSING_REQUIRED_COLUMN_MAPPING],
            warnings + [f"Missing required column mapping fields: {', '.join(missing_mapping)}"],
            lineage,
        )

    spend_dataset = _dataset_for_role(materialization, adapter, GeoXUploadedCSVRole.SPEND_PANEL)
    if spend_dataset is None:
        return _blocked(
            request.request_id,
            GeoXUploadedCSVRuntimeBridgeStatus.BLOCKED_MISSING_REQUIRED_DATASET,
            issues + [GeoXUploadedCSVRuntimeBridgeIssueCode.MISSING_REQUIRED_DATASET],
            warnings + ["Missing required spend panel dataset"],
            lineage,
        )

    assignment_dataset = _dataset_for_role(
        materialization,
        adapter,
        GeoXUploadedCSVRole.ASSIGNMENT_TABLE,
    )
    if assignment_dataset is None:
        return _blocked(
            request.request_id,
            GeoXUploadedCSVRuntimeBridgeStatus.BLOCKED_MISSING_REQUIRED_DATASET,
            issues + [GeoXUploadedCSVRuntimeBridgeIssueCode.MISSING_REQUIRED_DATASET],
            warnings + ["Missing required assignment table dataset"],
            lineage,
        )

    if spend_dataset.dataframe is None:
        return _blocked(
            request.request_id,
            GeoXUploadedCSVRuntimeBridgeStatus.BLOCKED_MISSING_REQUIRED_DATAFRAME,
            issues + [GeoXUploadedCSVRuntimeBridgeIssueCode.MISSING_REQUIRED_DATAFRAME],
            warnings + ["Missing materialized spend DataFrame"],
            lineage,
        )

    if assignment_dataset.dataframe is None:
        return _blocked(
            request.request_id,
            GeoXUploadedCSVRuntimeBridgeStatus.BLOCKED_MISSING_REQUIRED_DATAFRAME,
            issues + [GeoXUploadedCSVRuntimeBridgeIssueCode.MISSING_REQUIRED_DATAFRAME],
            warnings + ["Missing materialized assignment DataFrame"],
            lineage,
        )

    try:
        runtime = _import_panel_exp_runtime()
    except Exception as exc:  # noqa: BLE001 — import boundary
        warnings.append(f"panel_exp import failed: {exc}")
        return _blocked(
            request.request_id,
            GeoXUploadedCSVRuntimeBridgeStatus.BLOCKED_PACKAGE_RUNTIME_UNAVAILABLE,
            issues + [GeoXUploadedCSVRuntimeBridgeIssueCode.PACKAGE_RUNTIME_UNAVAILABLE],
            warnings,
            lineage,
        )

    adapter_plan = _bridge_adapter_plan(request, lineage, spend_dataset, assignment_dataset)
    try:
        spend_input = _build_post_test_spend_input_from_uploaded_csv(
            request,
            spend_dataset,
            assignment_dataset,
            runtime,
            lineage,
        )
        issues.append(GeoXUploadedCSVRuntimeBridgeIssueCode.POST_TEST_SPEND_INPUT_CREATED)
    except Exception as exc:  # noqa: BLE001 — input construction boundary
        warnings.append(f"PostTestSpendInput build failed: {exc}")
        return _blocked(
            request.request_id,
            GeoXUploadedCSVRuntimeBridgeStatus.BLOCKED_PACKAGE_RUNTIME_FAILED,
            issues + [GeoXUploadedCSVRuntimeBridgeIssueCode.PACKAGE_RUNTIME_FAILED],
            warnings,
            lineage,
        )

    try:
        evidence = runtime["build_post_test_spend_evidence"](spend_input)
    except Exception as exc:  # noqa: BLE001 — package runtime boundary
        warnings.append(f"panel_exp runtime failed: {exc}")
        return _blocked(
            request.request_id,
            GeoXUploadedCSVRuntimeBridgeStatus.BLOCKED_PACKAGE_RUNTIME_FAILED,
            issues + [GeoXUploadedCSVRuntimeBridgeIssueCode.PACKAGE_RUNTIME_FAILED],
            warnings,
            lineage,
        )

    try:
        handoff = runtime["build_trusted_readout_spend_handoff"](evidence)
    except Exception as exc:  # noqa: BLE001 — handoff boundary
        warnings.append(f"trusted readout spend handoff failed: {exc}")
        return _blocked(
            request.request_id,
            GeoXUploadedCSVRuntimeBridgeStatus.BLOCKED_PACKAGE_RUNTIME_FAILED,
            issues + [GeoXUploadedCSVRuntimeBridgeIssueCode.PACKAGE_RUNTIME_FAILED],
            warnings,
            lineage,
        )

    evidence_artifact = _evidence_artifact_from_package(adapter_plan, evidence, runtime)
    handoff_artifact = _handoff_artifact_from_package(adapter_plan, handoff)
    package_output_summary = dict(evidence_artifact.package_output_summary)
    issues.extend(
        [
            GeoXUploadedCSVRuntimeBridgeIssueCode.PACKAGE_EVIDENCE_CREATED,
            GeoXUploadedCSVRuntimeBridgeIssueCode.TRUSTED_HANDOFF_CREATED,
        ]
    )
    warnings.append(
        "spend_delta and readiness status are package-computed outputs; "
        "MIP does not authorize claims."
    )

    status = GeoXUploadedCSVRuntimeBridgeStatus.RUNTIME_COMPLETED
    if warnings:
        status = GeoXUploadedCSVRuntimeBridgeStatus.RUNTIME_COMPLETED_WITH_WARNINGS

    return GeoXUploadedCSVRuntimeBridgeResult(
        request_id=request.request_id,
        status=status,
        evidence_artifact=evidence_artifact,
        trusted_handoff_artifact=handoff_artifact,
        package_output_summary=package_output_summary,
        issues=_dedupe_issues(issues),
        warnings=list(dict.fromkeys(warnings)),
        lineage={
            **lineage,
            **spend_dataset.lineage,
            **assignment_dataset.lineage,
            "claim_authorization_owner": CLAIM_AUTHORIZATION_OWNER,
            "spend_source_id": spend_dataset.source_id,
            "assignment_source_id": assignment_dataset.source_id,
        },
    )


def _dataset_for_role(
    materialization: UploadedCSVMaterializationResult,
    adapter: GeoXUploadedCSVAdapterResult,
    role: GeoXUploadedCSVRole,
) -> MaterializedTabularDataset | None:
    mapping = next((item for item in adapter.role_mappings if item.role == role), None)
    if mapping is None:
        return None
    return next(
        (dataset for dataset in materialization.datasets if dataset.source_id == mapping.source_id),
        None,
    )


def _missing_required_column_mapping(
    column_mapping: GeoXUploadedCSVRuntimeColumnMapping,
) -> list[str]:
    missing: list[str] = []
    for field in _REQUIRED_SPEND_COLUMN_MAPPING_FIELDS:
        value = getattr(column_mapping, field, None)
        if value is None or not str(value).strip():
            missing.append(field)
    return missing


def _bridge_adapter_plan(
    request: GeoXUploadedCSVRuntimeBridgeRequest,
    lineage: dict[str, str],
    spend_dataset: MaterializedTabularDataset,
    assignment_dataset: MaterializedTabularDataset,
) -> GeoXPostTestSpendAdapterInputPlan:
    mapping = request.column_mapping
    return GeoXPostTestSpendAdapterInputPlan(
        request_id=request.request_id,
        experiment_id=request.experiment_id,
        integration_status=GeoXPanelExpIntegrationStatus.READY_TO_CALL_GEOX_POST_TEST_SPEND_RUNTIME,
        materialized_input_availability=GeoXMaterializedInputAvailability(
            has_materialized_spend_df=True,
            has_materialized_assignment_df=True,
            has_assignment_mapping=True,
            materialized_spend_ref_optional=spend_dataset.source_id,
            materialized_assignment_ref_optional=assignment_dataset.source_id,
            lineage=lineage,
        ),
        mapped_handoff_fields={
            "spend_date_column": mapping.spend_date_column,
            "spend_geo_column": mapping.spend_geo_column,
            "spend_amount_column": mapping.spend_amount_column,
        },
        experiment_type=_parse_experiment_type(request.experiment_type),
        source_lineage=lineage,
        ready_to_call_runtime=True,
    )


def _build_post_test_spend_input_from_uploaded_csv(
    request: GeoXUploadedCSVRuntimeBridgeRequest,
    spend_dataset: MaterializedTabularDataset,
    assignment_dataset: MaterializedTabularDataset,
    runtime: dict[str, Any],
    lineage: dict[str, str],
) -> Any:
    spend_df = spend_dataset.dataframe
    assign_df = assignment_dataset.dataframe
    if spend_df is None or assign_df is None:
        msg = "materialized spend and assignment DataFrames required"
        raise ValueError(msg)

    mapping = request.column_mapping
    assignment_mapping = request.assignment_mapping

    assignment_geo_col = (
        assignment_mapping.get("geo_column")
        or mapping.assignment_geo_column
        or _first_present(assign_df.columns, ("dma", "geo_unit_id"))
        or "geo_unit_id"
    )
    assignment_cell_col = (
        assignment_mapping.get("cell_column")
        or mapping.assignment_cell_column
        or _first_present(assign_df.columns, ("cell", "cell_id"))
        or "cell_id"
    )
    assignment_role_col = (
        assignment_mapping.get("role_column")
        or mapping.assignment_role_column
        or _first_present(assign_df.columns, ("treatment", "cell_role"))
        or "cell_role"
    )

    spend_columns = set(spend_df.columns)
    spend_cell_column = mapping.spend_cell_column or (
        "cell" if "cell" in spend_columns else None
    )
    currency_column = mapping.currency_column or (
        "currency" if "currency" in spend_columns else None
    )
    channel_column = mapping.spend_channel_column or (
        "channel" if "channel" in spend_columns else None
    )
    campaign_column = mapping.spend_campaign_column or (
        "campaign" if "campaign" in spend_columns else None
    )

    experiment_type = request.experiment_type.strip()
    if not experiment_type or experiment_type == "unknown":
        msg = "experiment_type required for PostTestSpendInput"
        raise ValueError(msg)

    post_test_spend_input = runtime["PostTestSpendInput"]
    return post_test_spend_input(
        experiment_id=request.experiment_id,
        spend_rows=spend_df.to_dict(orient="records"),
        assignment_rows=assign_df.to_dict(orient="records"),
        post_period_start=request.post_period_start,
        post_period_end=request.post_period_end,
        experiment_type=experiment_type,
        spend_date_column=mapping.spend_date_column,
        spend_geo_column=mapping.spend_geo_column,
        spend_amount_column=mapping.spend_amount_column,
        spend_cell_column=spend_cell_column,
        assignment_geo_column=assignment_geo_col,
        assignment_cell_column=assignment_cell_col,
        assignment_role_column=assignment_role_col,
        currency_column=currency_column,
        spend_channel_column=channel_column,
        spend_campaign_column=campaign_column,
        counterfactual_or_bau_spend=_optional_float(lineage.get("counterfactual_or_bau_spend")),
        baseline_spend=_optional_float(lineage.get("baseline_spend")),
        spend_baseline_policy=lineage.get("spend_baseline_definition"),
        source_dataset_ref=spend_dataset.source_id,
        source_lineage={
            **lineage,
            **spend_dataset.lineage,
            **assignment_dataset.lineage,
            "uploaded_csv_runtime_bridge": "true",
        },
    )


def _parse_experiment_type(value: str) -> GeoXPostTestExperimentType:
    normalized = value.strip().lower()
    for experiment_type in GeoXPostTestExperimentType:
        if experiment_type.value == normalized:
            return experiment_type
    return GeoXPostTestExperimentType.UNKNOWN


def _first_present(columns: Any, candidates: tuple[str, ...]) -> str | None:
    column_set = set(columns)
    for candidate in candidates:
        if candidate in column_set:
            return candidate
    return None


def _optional_float(value: str | None) -> float | None:
    if value is None or not str(value).strip():
        return None
    return float(value)


def _blocked(
    request_id: str,
    status: GeoXUploadedCSVRuntimeBridgeStatus,
    issues: list[GeoXUploadedCSVRuntimeBridgeIssueCode],
    warnings: list[str],
    lineage: dict[str, str],
) -> GeoXUploadedCSVRuntimeBridgeResult:
    return GeoXUploadedCSVRuntimeBridgeResult(
        request_id=request_id,
        status=status,
        issues=_dedupe_issues(issues),
        warnings=list(dict.fromkeys(warnings)),
        lineage=lineage,
    )


def _dedupe_issues(
    issues: list[GeoXUploadedCSVRuntimeBridgeIssueCode],
) -> list[GeoXUploadedCSVRuntimeBridgeIssueCode]:
    seen: set[GeoXUploadedCSVRuntimeBridgeIssueCode] = set()
    ordered: list[GeoXUploadedCSVRuntimeBridgeIssueCode] = []
    for issue in issues:
        if issue not in seen:
            seen.add(issue)
            ordered.append(issue)
    return ordered
