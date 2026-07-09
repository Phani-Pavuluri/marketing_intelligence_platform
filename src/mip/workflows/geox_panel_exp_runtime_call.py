"""GeoX panel_exp runtime-call workflow (Stage 3B — fixture materialization path only)."""

from __future__ import annotations

from typing import Any

from mip.contracts.geox_fixture_materialization import GeoXFixtureMaterializationStatus
from mip.contracts.geox_panel_exp_integration import (
    GeoXPanelExpIntegrationStatus,
    GeoXPostTestSpendAdapterInputPlan,
)
from mip.contracts.geox_panel_exp_runtime_call import (
    _PLAN_READY_STATUSES,
    CLAIM_AUTHORIZATION_OWNER,
    GeoXPanelExpRuntimeCallIssueCode,
    GeoXPanelExpRuntimeCallMode,
    GeoXPanelExpRuntimeCallRequest,
    GeoXPanelExpRuntimeCallResult,
    GeoXPanelExpRuntimeCallStatus,
    GeoXPostTestSpendEvidenceArtifact,
    GeoXTrustedReadoutSpendHandoffArtifact,
)


def call_geox_post_test_spend_runtime_for_fixture(
    request: GeoXPanelExpRuntimeCallRequest,
) -> GeoXPanelExpRuntimeCallResult:
    """Call panel_exp post-test spend runtime using fixture-materialized inputs only."""
    plan = request.adapter_input_plan
    lineage = {
        **plan.source_lineage,
        **request.lineage,
        "runtime_call_mode": str(request.call_mode),
        "runtime_call_stage": "3b_fixture_only",
    }
    warnings = list(dict.fromkeys(request.warnings + plan.warnings))
    issues: list[GeoXPanelExpRuntimeCallIssueCode] = [
        GeoXPanelExpRuntimeCallIssueCode.FIXTURE_ONLY_RUNTIME_CALL,
        GeoXPanelExpRuntimeCallIssueCode.CLAIM_AUTHORIZATION_DELEGATED,
        GeoXPanelExpRuntimeCallIssueCode.ROI_ROAS_NOT_COMPUTED_IN_MIP,
    ]

    if request.call_mode != GeoXPanelExpRuntimeCallMode.FIXTURE_ONLY:
        return _blocked(
            request.request_id,
            GeoXPanelExpRuntimeCallStatus.BLOCKED_RUNTIME_CALL_NOT_ALLOWED,
            issues
            + [
                GeoXPanelExpRuntimeCallIssueCode.RUNTIME_CALL_NOT_ALLOWED,
            ],
            warnings,
            lineage,
        )

    if not request.allow_runtime_call:
        return _blocked(
            request.request_id,
            GeoXPanelExpRuntimeCallStatus.BLOCKED_RUNTIME_CALL_NOT_ALLOWED,
            issues + [GeoXPanelExpRuntimeCallIssueCode.RUNTIME_CALL_NOT_ALLOWED],
            warnings,
            lineage,
        )

    fixture_result = request.fixture_materialization_result
    if (
        fixture_result is None
        or fixture_result.status != GeoXFixtureMaterializationStatus.MATERIALIZED
    ):
        return _blocked(
            request.request_id,
            GeoXPanelExpRuntimeCallStatus.BLOCKED_FIXTURE_MATERIALIZATION_REQUIRED,
            issues,
            warnings,
            lineage,
        )

    if fixture_result.spend_dataset is None:
        return _blocked(
            request.request_id,
            GeoXPanelExpRuntimeCallStatus.BLOCKED_MATERIALIZED_SPEND_INPUT_REQUIRED,
            issues + [GeoXPanelExpRuntimeCallIssueCode.MATERIALIZED_SPEND_DF_MISSING],
            warnings,
            lineage,
        )

    if not _assignment_materialized(fixture_result):
        return _blocked(
            request.request_id,
            GeoXPanelExpRuntimeCallStatus.BLOCKED_MATERIALIZED_ASSIGNMENT_INPUT_REQUIRED,
            issues
            + [GeoXPanelExpRuntimeCallIssueCode.MATERIALIZED_ASSIGNMENT_DF_OR_MAPPING_MISSING],
            warnings,
            lineage,
        )

    if not _adapter_plan_ready(plan):
        return _blocked(
            request.request_id,
            _blocked_status_for_plan(plan),
            issues + [GeoXPanelExpRuntimeCallIssueCode.POST_TEST_SPEND_INPUT_BUILD_FAILED],
            warnings,
            lineage,
        )

    try:
        runtime = _import_panel_exp_runtime()
    except Exception as exc:  # noqa: BLE001 — import boundary
        warnings.append(f"panel_exp import failed: {exc}")
        return _blocked(
            request.request_id,
            GeoXPanelExpRuntimeCallStatus.BLOCKED_PANEL_EXP_IMPORT_FAILED,
            issues + [GeoXPanelExpRuntimeCallIssueCode.PANEL_EXP_IMPORT_FAILED],
            warnings,
            lineage,
        )

    try:
        spend_input = _build_post_test_spend_input(plan, fixture_result, runtime)
    except Exception as exc:  # noqa: BLE001 — input construction boundary
        warnings.append(f"PostTestSpendInput build failed: {exc}")
        return _blocked(
            request.request_id,
            GeoXPanelExpRuntimeCallStatus.BLOCKED_POST_TEST_SPEND_INPUT_BUILD_FAILED,
            issues + [GeoXPanelExpRuntimeCallIssueCode.POST_TEST_SPEND_INPUT_BUILD_FAILED],
            warnings,
            lineage,
        )

    try:
        evidence = runtime["build_post_test_spend_evidence"](spend_input)
    except Exception as exc:  # noqa: BLE001 — package runtime boundary
        warnings.append(f"panel_exp runtime failed: {exc}")
        return _blocked(
            request.request_id,
            GeoXPanelExpRuntimeCallStatus.BLOCKED_PANEL_EXP_RUNTIME_FAILED,
            issues + [GeoXPanelExpRuntimeCallIssueCode.PANEL_EXP_RUNTIME_EXCEPTION],
            warnings,
            lineage,
        )

    try:
        handoff = runtime["build_trusted_readout_spend_handoff"](evidence)
    except Exception as exc:  # noqa: BLE001 — handoff boundary
        warnings.append(f"trusted readout spend handoff failed: {exc}")
        return _blocked(
            request.request_id,
            GeoXPanelExpRuntimeCallStatus.BLOCKED_TRUSTED_READOUT_HANDOFF_FAILED,
            issues + [GeoXPanelExpRuntimeCallIssueCode.TRUSTED_READOUT_HANDOFF_EXCEPTION],
            warnings,
            lineage,
        )

    evidence_artifact = _evidence_artifact_from_package(plan, evidence, runtime)
    handoff_artifact = _handoff_artifact_from_package(plan, handoff)
    issues.append(GeoXPanelExpRuntimeCallIssueCode.SPEND_DELTA_PACKAGE_COMPUTED)
    warnings.append(
        "spend_delta and readiness status are package-computed outputs; "
        "MIP does not authorize claims."
    )

    return GeoXPanelExpRuntimeCallResult(
        request_id=request.request_id,
        status=GeoXPanelExpRuntimeCallStatus.CALLED_PANEL_EXP_RUNTIME,
        runtime_called=True,
        post_test_spend_evidence_artifact=evidence_artifact,
        trusted_readout_spend_handoff_artifact=handoff_artifact,
        issues=_dedupe_issues(issues),
        warnings=list(dict.fromkeys(warnings)),
        lineage={
            **lineage,
            **fixture_result.lineage,
            "claim_authorization_owner": CLAIM_AUTHORIZATION_OWNER,
            "package_runtime_module": plan.runtime_reference.runtime_module_path,
            "package_primary_callable": plan.runtime_reference.primary_callable,
            "package_handoff_helper": plan.runtime_reference.handoff_helper_callable,
        },
    )


def _import_panel_exp_runtime() -> dict[str, Any]:
    from panel_exp.validation.post_test_spend_readiness_adapter_runtime_001 import (  # type: ignore[import-untyped]
        PostTestSpendInput,
        build_post_test_spend_evidence,
        build_trusted_readout_spend_handoff,
    )

    return {
        "PostTestSpendInput": PostTestSpendInput,
        "build_post_test_spend_evidence": build_post_test_spend_evidence,
        "build_trusted_readout_spend_handoff": build_trusted_readout_spend_handoff,
    }


def _assignment_materialized(fixture_result: Any) -> bool:
    if fixture_result.assignment_dataset is not None:
        return True
    availability = getattr(fixture_result, "materialized_input_availability", None)
    if availability is not None and getattr(availability, "has_assignment_mapping", False):
        return True
    return False


def _adapter_plan_ready(plan: GeoXPostTestSpendAdapterInputPlan) -> bool:
    if plan.ready_to_call_runtime:
        return True
    return plan.integration_status in _PLAN_READY_STATUSES


def _blocked_status_for_plan(
    plan: GeoXPostTestSpendAdapterInputPlan,
) -> GeoXPanelExpRuntimeCallStatus:
    mapping = {
        GeoXPanelExpIntegrationStatus.BLOCKED_MATERIALIZED_SPEND_INPUT_REQUIRED: (
            GeoXPanelExpRuntimeCallStatus.BLOCKED_MATERIALIZED_SPEND_INPUT_REQUIRED
        ),
        GeoXPanelExpIntegrationStatus.BLOCKED_MATERIALIZED_ASSIGNMENT_INPUT_REQUIRED: (
            GeoXPanelExpRuntimeCallStatus.BLOCKED_MATERIALIZED_ASSIGNMENT_INPUT_REQUIRED
        ),
    }
    return mapping.get(
        plan.integration_status,
        GeoXPanelExpRuntimeCallStatus.BLOCKED_POST_TEST_SPEND_INPUT_BUILD_FAILED,
    )


def _build_post_test_spend_input(
    plan: GeoXPostTestSpendAdapterInputPlan,
    fixture_result: Any,
    runtime: dict[str, Any],
) -> Any:
    spend_dataset = fixture_result.spend_dataset
    if spend_dataset is None:
        msg = "materialized spend dataset required"
        raise ValueError(msg)

    spend_df = spend_dataset.dataframe
    mapped = plan.mapped_handoff_fields
    lineage = {**plan.source_lineage, **fixture_result.lineage, **spend_dataset.source_lineage}

    spend_date_col = mapped.get("spend_date_column") or "date"
    spend_geo_col = mapped.get("spend_geo_column") or "dma"
    spend_amount_col = mapped.get("spend_amount_column") or "spend"

    assignment_rows: list[dict[str, Any]] | None = None
    assignment_geo_col = "geo_unit_id"
    assignment_cell_col = "cell_id"
    assignment_role_col = "cell_role"
    if fixture_result.assignment_dataset is not None:
        assign_df = fixture_result.assignment_dataset.dataframe
        assignment_rows = assign_df.to_dict(orient="records")
        columns = set(assign_df.columns)
        if "dma" in columns:
            assignment_geo_col = "dma"
        if "cell" in columns:
            assignment_cell_col = "cell"
        if "treatment" in columns:
            assignment_role_col = "treatment"

    post_start = lineage.get("post_period_start")
    post_end = lineage.get("post_period_end")
    if not post_start or not post_end:
        msg = "post_period_start and post_period_end required in adapter plan lineage"
        raise ValueError(msg)

    experiment_type = str(plan.experiment_type)
    if experiment_type == "unknown":
        experiment_type = str(lineage.get("experiment_type", "unknown"))
    if not experiment_type or experiment_type == "unknown":
        msg = "experiment_type required for PostTestSpendInput"
        raise ValueError(msg)

    spend_columns = set(spend_df.columns)
    spend_cell_column = "cell" if "cell" in spend_columns else None
    currency_column = "currency" if "currency" in spend_columns else None
    channel_column = "channel" if "channel" in spend_columns else None
    campaign_column = "campaign" if "campaign" in spend_columns else None

    counterfactual = _optional_float(lineage.get("counterfactual_or_bau_spend"))
    baseline = _optional_float(lineage.get("baseline_spend"))

    post_test_spend_input = runtime["PostTestSpendInput"]
    return post_test_spend_input(
        experiment_id=plan.experiment_id,
        spend_rows=spend_df.to_dict(orient="records"),
        assignment_rows=assignment_rows,
        post_period_start=post_start,
        post_period_end=post_end,
        experiment_type=experiment_type,
        spend_date_column=spend_date_col,
        spend_geo_column=spend_geo_col,
        spend_amount_column=spend_amount_col,
        spend_cell_column=spend_cell_column,
        assignment_geo_column=assignment_geo_col,
        assignment_cell_column=assignment_cell_col,
        assignment_role_column=assignment_role_col,
        currency_column=currency_column,
        spend_channel_column=channel_column,
        spend_campaign_column=campaign_column,
        counterfactual_or_bau_spend=counterfactual,
        baseline_spend=baseline,
        spend_baseline_policy=mapped.get("spend_baseline_definition"),
        source_dataset_ref=spend_dataset.dataset_ref_id,
        source_lineage=lineage,
    )


def _evidence_artifact_from_package(
    plan: GeoXPostTestSpendAdapterInputPlan,
    evidence: Any,
    runtime: dict[str, Any],
) -> GeoXPostTestSpendEvidenceArtifact:
    readiness_status = evidence.readiness_status
    if hasattr(readiness_status, "value"):
        readiness_status = readiness_status.value

    package_summary: dict[str, str | float | int | bool | None] = {
        "readiness_status": str(readiness_status),
        "actual_treatment_spend": evidence.actual_treatment_spend,
        "actual_control_or_baseline_spend": evidence.actual_control_or_baseline_spend,
        "counterfactual_or_bau_spend": evidence.counterfactual_or_bau_spend,
        "spend_delta_definition": evidence.spend_delta_definition,
        "spend_currency": evidence.spend_currency,
        "spend_scope": evidence.spend_scope,
    }
    if evidence.spend_delta is not None:
        package_summary["package_computed_spend_delta"] = evidence.spend_delta

    return GeoXPostTestSpendEvidenceArtifact(
        artifact_id=f"geox-post-test-spend-evidence:{plan.experiment_id}:{plan.request_id}",
        experiment_id=plan.experiment_id,
        source_dataset_ref=evidence.source_dataset_ref,
        source_lineage={
            **{str(k): str(v) for k, v in (evidence.source_lineage or {}).items()},
            **plan.source_lineage,
        },
        readiness_status=str(readiness_status),
        blocking_reasons=list(evidence.blocking_reasons),
        warnings=list(evidence.warnings),
        package_output_summary=package_summary,
        package_runtime_reference=plan.runtime_reference,
        claim_authorization_owner=CLAIM_AUTHORIZATION_OWNER,
    )


def _handoff_artifact_from_package(
    plan: GeoXPostTestSpendAdapterInputPlan,
    handoff: dict[str, Any],
) -> GeoXTrustedReadoutSpendHandoffArtifact:
    summary = handoff.get("spend_readiness_summary") or {}
    efficiency = handoff.get("efficiency_metric_readiness") or {}
    roi_status = handoff.get("roi_claim_authorization_status", "NOT_EVALUATED")
    return GeoXTrustedReadoutSpendHandoffArtifact(
        artifact_id=f"geox-trusted-readout-spend-handoff:{plan.experiment_id}:{plan.request_id}",
        experiment_id=plan.experiment_id,
        spend_readiness_summary={
            str(k): v if isinstance(v, bool) else str(v) for k, v in summary.items()
        },
        blocked_efficiency_metrics=list(handoff.get("blocked_efficiency_metrics") or []),
        spend_lineage={
            str(k): str(v) for k, v in (handoff.get("spend_lineage") or {}).items()
        },
        spend_warnings=[str(item) for item in handoff.get("spend_warnings") or []],
        package_handoff_summary={
            "roi_claim_authorization_status": str(roi_status),
            "cost_per_incremental_kpi": str(efficiency.get("cost_per_incremental_kpi", "")),
            "roas": str(efficiency.get("roas", "")),
            "profit_roi": str(efficiency.get("profit_roi", "")),
        },
        claim_authorization_owner=CLAIM_AUTHORIZATION_OWNER,
    )


def _optional_float(value: str | None) -> float | None:
    if value is None or not str(value).strip():
        return None
    return float(value)


def _blocked(
    request_id: str,
    status: GeoXPanelExpRuntimeCallStatus,
    issues: list[GeoXPanelExpRuntimeCallIssueCode],
    warnings: list[str],
    lineage: dict[str, str],
) -> GeoXPanelExpRuntimeCallResult:
    return GeoXPanelExpRuntimeCallResult(
        request_id=request_id,
        status=status,
        runtime_called=False,
        issues=_dedupe_issues(issues),
        warnings=list(dict.fromkeys(warnings)),
        lineage=lineage,
    )


def _dedupe_issues(
    issues: list[GeoXPanelExpRuntimeCallIssueCode],
) -> list[GeoXPanelExpRuntimeCallIssueCode]:
    seen: set[GeoXPanelExpRuntimeCallIssueCode] = set()
    ordered: list[GeoXPanelExpRuntimeCallIssueCode] = []
    for issue in issues:
        if issue not in seen:
            seen.add(issue)
            ordered.append(issue)
    return ordered
