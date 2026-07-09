"""GeoX panel_exp integration boundary workflow (Stage 3A — plan only, no runtime call)."""

from __future__ import annotations

from mip.contracts.geox_panel_exp_integration import (
    GEOX_INPUT_MODEL,
    GEOX_OUTPUT_MODEL,
    GeoXMaterializedInputAvailability,
    GeoXPanelExpIntegrationIssueCode,
    GeoXPanelExpIntegrationRequest,
    GeoXPanelExpIntegrationResult,
    GeoXPanelExpIntegrationStatus,
    GeoXPanelExpRuntimeReference,
    GeoXPostTestExperimentType,
    GeoXPostTestSpendAdapterInputPlan,
    GeoXPostTestSpendInputRequirements,
)
from mip.contracts.geox_readout_input_resolution import (
    GeoXReadoutInputHandoff,
    GeoXReadoutIntent,
    MappingConfirmationStatus,
    SpendColumnMapping,
)

_SPEND_READINESS_INTENTS = frozenset(
    {
        GeoXReadoutIntent.READOUT_WITH_COST_PER,
        GeoXReadoutIntent.READOUT_WITH_ROAS,
        GeoXReadoutIntent.READOUT_WITH_PROFIT_ROI,
    }
)

_CONFIRMED_STATUSES = frozenset(
    {
        MappingConfirmationStatus.USER_CONFIRMED,
        MappingConfirmationStatus.NOT_REQUIRED,
    }
)

_BASELINE_REQUIRED_TYPES = frozenset(
    {
        GeoXPostTestExperimentType.GO_DARK,
        GeoXPostTestExperimentType.HEAVY_UP,
    }
)

_MSG_NO_SPEND_READINESS = (
    "Spend readiness adapter planning is not requested for KPI-only or lift-only readout."
)
_MSG_MATERIALIZED_SPEND_REQUIRED = (
    "GeoX post-test spend runtime requires a materialized spend dataframe. "
    "MIP dataset references must be materialized before Stage 3B can call panel_exp."
)
_MSG_MATERIALIZED_ASSIGNMENT_REQUIRED = (
    "GeoX post-test spend runtime requires a materialized assignment dataframe "
    "or confirmed assignment mapping."
)
_MSG_SPEND_MAPPING_MISSING = (
    "Confirmed spend date, geo, and amount column mappings are required before "
    "building PostTestSpendInput."
)
_MSG_ASSIGNMENT_MAPPING_MISSING = (
    "Confirmed assignment join keys or cell mapping are required for spend readiness."
)
_MSG_POST_PERIOD_DATES_MISSING = (
    "Post-period start and end dates are required for post-test spend evidence."
)
_MSG_EXPERIMENT_TYPE_MISSING = (
    "Experiment type (go_dark, heavy_up, holdout, dosage, reallocation) is required."
)
_MSG_BASELINE_MISSING = (
    "Baseline or counterfactual spend definition is required for this experiment type."
)
_MSG_RUNTIME_NOT_CONFIGURED = (
    "panel_exp runtime call is deferred to Stage 3B after materialized inputs exist."
)
_MSG_IMPORT_NOT_ALLOWED = (
    "panel_exp import is not allowed in Stage 3A. Adapter boundary planning only."
)
_MSG_VALUE_MAPPING_NOT_CONSUMED = (
    "Value/revenue mapping is not consumed by the post-test spend readiness runtime. "
    "ROAS/profit ROI value mapping remains a separate panel_exp readout concern."
)
_MSG_CLAIM_DELEGATION = (
    "Claim authorization for spend_delta and efficiency metrics remains delegated "
    "to panel_exp trusted readout paths."
)


def prepare_geox_panel_exp_integration(
    request: GeoXPanelExpIntegrationRequest,
) -> GeoXPanelExpIntegrationResult:
    """Evaluate handoff against panel_exp materialization boundary."""
    plan = build_geox_post_test_spend_adapter_input_plan(request)
    messages = _user_messages_for_status(plan.integration_status)
    issues = list(plan.issues)
    warnings = list(dict.fromkeys(request.warnings + plan.warnings))

    if request.allow_panel_exp_import or request.allow_panel_exp_runtime_call:
        if request.allow_panel_exp_import and not request.allow_panel_exp_runtime_call:
            plan.integration_status = (
                GeoXPanelExpIntegrationStatus.BLOCKED_PANEL_EXP_IMPORT_NOT_ALLOWED
            )
            issues.append(GeoXPanelExpIntegrationIssueCode.PANEL_EXP_RUNTIME_NOT_CALLED_IN_STAGE_3A)
            messages = [_MSG_IMPORT_NOT_ALLOWED, _MSG_RUNTIME_NOT_CONFIGURED]
        else:
            plan.integration_status = (
                GeoXPanelExpIntegrationStatus.BLOCKED_PANEL_EXP_RUNTIME_NOT_CONFIGURED
            )
            issues.append(GeoXPanelExpIntegrationIssueCode.PANEL_EXP_RUNTIME_NOT_CALLED_IN_STAGE_3A)
            messages = [_MSG_RUNTIME_NOT_CONFIGURED]

    issues.append(GeoXPanelExpIntegrationIssueCode.CLAIM_AUTHORIZATION_DELEGATED)
    warnings.append(_MSG_CLAIM_DELEGATION)

    return GeoXPanelExpIntegrationResult(
        request_id=request.request_id,
        integration_status=plan.integration_status,
        adapter_input_plan=plan,
        runtime_called=False,
        user_messages=messages,
        issues=_dedupe_issues(issues),
        warnings=warnings,
        lineage={
            **request.lineage,
            "integration_stage": "3a_adapter_boundary",
            "panel_exp_input_model": GEOX_INPUT_MODEL,
            "panel_exp_output_model": GEOX_OUTPUT_MODEL,
        },
    )


def build_geox_post_test_spend_adapter_input_plan(
    request: GeoXPanelExpIntegrationRequest,
) -> GeoXPostTestSpendAdapterInputPlan:
    """Build adapter input plan from handoff and materialized availability."""
    handoff = request.handoff
    availability = request.materialized_input_availability
    lineage = {**handoff.lineage, **request.lineage, **availability.lineage}
    warnings = list(dict.fromkeys(handoff.warnings + request.warnings + availability.warnings))
    issues: list[GeoXPanelExpIntegrationIssueCode] = []
    missing_materialized: list[str] = []
    missing_mappings: list[str] = []
    missing_metadata: list[str] = []

    experiment_type = _resolve_experiment_type(lineage)
    input_requirements = _default_input_requirements(experiment_type)
    mapped_fields = _mapped_handoff_fields(handoff)
    handoff_summary = _handoff_ref_summary(handoff)
    baseline_requirements = _baseline_requirements_for_type(experiment_type)
    input_requirements.baseline_or_counterfactual_required = bool(baseline_requirements)

    if not _spend_readiness_requested(handoff):
        issues.append(GeoXPanelExpIntegrationIssueCode.PANEL_EXP_RUNTIME_NOT_CALLED_IN_STAGE_3A)
        return _plan(
            request,
            GeoXPanelExpIntegrationStatus.BLOCKED_NO_SPEND_READINESS_REQUESTED,
            availability,
            input_requirements,
            handoff_summary,
            mapped_fields,
            missing_materialized,
            missing_mappings,
            missing_metadata,
            experiment_type,
            baseline_requirements,
            lineage,
            issues,
            warnings,
            ready_to_call=False,
        )

    issues.append(GeoXPanelExpIntegrationIssueCode.PANEL_EXP_RUNTIME_REQUIRES_MATERIALIZED_INPUTS)

    if handoff.value_mapping_optional is not None:
        issues.append(GeoXPanelExpIntegrationIssueCode.VALUE_MAPPING_NOT_CONSUMED_BY_SPEND_RUNTIME)
        warnings.append(_MSG_VALUE_MAPPING_NOT_CONSUMED)

    if not availability.has_materialized_spend_df:
        issues.append(GeoXPanelExpIntegrationIssueCode.MATERIALIZED_SPEND_DF_MISSING)
        missing_materialized.append("spend_df")
        return _plan(
            request,
            GeoXPanelExpIntegrationStatus.BLOCKED_MATERIALIZED_SPEND_INPUT_REQUIRED,
            availability,
            input_requirements,
            handoff_summary,
            mapped_fields,
            missing_materialized,
            missing_mappings,
            missing_metadata,
            experiment_type,
            baseline_requirements,
            lineage,
            issues,
            warnings,
            ready_to_call=False,
        )

    if not _assignment_available(handoff, availability):
        issues.append(
            GeoXPanelExpIntegrationIssueCode.MATERIALIZED_ASSIGNMENT_DF_OR_MAPPING_MISSING
        )
        missing_materialized.append("assignment_df_or_mapping")
        return _plan(
            request,
            GeoXPanelExpIntegrationStatus.BLOCKED_MATERIALIZED_ASSIGNMENT_INPUT_REQUIRED,
            availability,
            input_requirements,
            handoff_summary,
            mapped_fields,
            missing_materialized,
            missing_mappings,
            missing_metadata,
            experiment_type,
            baseline_requirements,
            lineage,
            warnings=warnings,
            issues=issues,
            ready_to_call=False,
        )

    spend_mapping = handoff.spend_column_mapping_optional
    spend_mapping_issues = _spend_mapping_issues(spend_mapping, missing_mappings)
    issues.extend(spend_mapping_issues)
    if spend_mapping_issues:
        return _plan(
            request,
            GeoXPanelExpIntegrationStatus.BLOCKED_MISSING_CONFIRMED_SPEND_MAPPING,
            availability,
            input_requirements,
            handoff_summary,
            mapped_fields,
            missing_materialized,
            missing_mappings,
            missing_metadata,
            experiment_type,
            baseline_requirements,
            lineage,
            issues,
            warnings,
            ready_to_call=False,
        )

    if not _assignment_mapping_confirmed(handoff, availability, lineage, missing_mappings):
        issues.append(GeoXPanelExpIntegrationIssueCode.ASSIGNMENT_JOIN_KEYS_MISSING)
        return _plan(
            request,
            GeoXPanelExpIntegrationStatus.BLOCKED_MISSING_CONFIRMED_ASSIGNMENT_MAPPING,
            availability,
            input_requirements,
            handoff_summary,
            mapped_fields,
            missing_materialized,
            missing_mappings,
            missing_metadata,
            experiment_type,
            baseline_requirements,
            lineage,
            issues,
            warnings,
            ready_to_call=False,
        )

    post_start = lineage.get("post_period_start")
    post_end = lineage.get("post_period_end")
    if not post_start:
        issues.append(GeoXPanelExpIntegrationIssueCode.POST_PERIOD_START_MISSING)
        missing_metadata.append("post_period_start")
    if not post_end:
        issues.append(GeoXPanelExpIntegrationIssueCode.POST_PERIOD_END_MISSING)
        missing_metadata.append("post_period_end")
    if missing_metadata:
        return _plan(
            request,
            GeoXPanelExpIntegrationStatus.BLOCKED_MISSING_POST_PERIOD_DATES,
            availability,
            input_requirements,
            handoff_summary,
            mapped_fields,
            missing_materialized,
            missing_mappings,
            missing_metadata,
            experiment_type,
            baseline_requirements,
            lineage,
            issues,
            warnings,
            ready_to_call=False,
        )

    if experiment_type == GeoXPostTestExperimentType.UNKNOWN:
        issues.append(GeoXPanelExpIntegrationIssueCode.EXPERIMENT_TYPE_MISSING)
        missing_metadata.append("experiment_type")
        return _plan(
            request,
            GeoXPanelExpIntegrationStatus.BLOCKED_MISSING_EXPERIMENT_TYPE,
            availability,
            input_requirements,
            handoff_summary,
            mapped_fields,
            missing_materialized,
            missing_mappings,
            missing_metadata,
            experiment_type,
            baseline_requirements,
            lineage,
            issues,
            warnings,
            ready_to_call=False,
        )

    if not _baseline_satisfied(handoff, experiment_type, lineage):
        issues.append(GeoXPanelExpIntegrationIssueCode.BASELINE_OR_COUNTERFACTUAL_SPEND_MISSING)
        missing_metadata.append("baseline_or_counterfactual_spend")
        return _plan(
            request,
            GeoXPanelExpIntegrationStatus.BLOCKED_MISSING_BASELINE_FOR_EXPERIMENT_TYPE,
            availability,
            input_requirements,
            handoff_summary,
            mapped_fields,
            missing_materialized,
            missing_mappings,
            missing_metadata,
            experiment_type,
            baseline_requirements,
            lineage,
            issues,
            warnings,
            ready_to_call=False,
        )

    status = GeoXPanelExpIntegrationStatus.READY_TO_BUILD_POST_TEST_SPEND_INPUT
    ready_to_call = False
    if request.allow_panel_exp_runtime_call and request.allow_panel_exp_import:
        status = GeoXPanelExpIntegrationStatus.READY_TO_CALL_GEOX_POST_TEST_SPEND_RUNTIME
        ready_to_call = True

    issues.append(GeoXPanelExpIntegrationIssueCode.PANEL_EXP_RUNTIME_NOT_CALLED_IN_STAGE_3A)
    return _plan(
        request,
        status,
        availability,
        input_requirements,
        handoff_summary,
        mapped_fields,
        missing_materialized,
        missing_mappings,
        missing_metadata,
        experiment_type,
        baseline_requirements,
        lineage,
        issues,
        warnings,
        ready_to_call=ready_to_call,
    )


def _spend_readiness_requested(handoff: GeoXReadoutInputHandoff) -> bool:
    if handoff.readout_intent in _SPEND_READINESS_INTENTS:
        return True
    if handoff.spend_dataset_ref_optional is not None:
        return True
    if handoff.spend_column_mapping_optional is not None:
        return True
    metrics = {metric.strip().lower() for metric in handoff.requested_metrics}
    return bool(metrics.intersection({"cost_per", "cpa", "roi", "roas", "profit_roi", "profit"}))


def _assignment_available(
    handoff: GeoXReadoutInputHandoff,
    availability: GeoXMaterializedInputAvailability,
) -> bool:
    if availability.has_materialized_assignment_df:
        return True
    if availability.has_assignment_mapping:
        return True
    if handoff.assignment_artifact_ref is not None:
        return True
    if handoff.design_artifact_ref is not None:
        return True
    return False


def _spend_mapping_issues(
    mapping: SpendColumnMapping | None,
    missing_mappings: list[str],
) -> list[GeoXPanelExpIntegrationIssueCode]:
    issues: list[GeoXPanelExpIntegrationIssueCode] = []
    if mapping is None:
        missing_mappings.extend(
            ["spend_date_column", "spend_geo_column", "spend_amount_column"]
        )
        return [
            GeoXPanelExpIntegrationIssueCode.SPEND_DATE_COLUMN_MISSING,
            GeoXPanelExpIntegrationIssueCode.SPEND_GEO_COLUMN_MISSING,
            GeoXPanelExpIntegrationIssueCode.SPEND_AMOUNT_COLUMN_MISSING,
        ]
    if not mapping.date_week_column:
        missing_mappings.append("spend_date_column")
        issues.append(GeoXPanelExpIntegrationIssueCode.SPEND_DATE_COLUMN_MISSING)
    elif mapping.confirmation_status not in _CONFIRMED_STATUSES:
        missing_mappings.append("spend_date_column_confirmation")
        issues.append(GeoXPanelExpIntegrationIssueCode.SPEND_DATE_COLUMN_MISSING)
    if not mapping.geo_unit_column:
        missing_mappings.append("spend_geo_column")
        issues.append(GeoXPanelExpIntegrationIssueCode.SPEND_GEO_COLUMN_MISSING)
    elif mapping.confirmation_status not in _CONFIRMED_STATUSES:
        missing_mappings.append("spend_geo_column_confirmation")
        issues.append(GeoXPanelExpIntegrationIssueCode.SPEND_GEO_COLUMN_MISSING)
    if not mapping.spend_amount_column:
        missing_mappings.append("spend_amount_column")
        issues.append(GeoXPanelExpIntegrationIssueCode.SPEND_AMOUNT_COLUMN_MISSING)
    elif mapping.confirmation_status not in _CONFIRMED_STATUSES:
        missing_mappings.append("spend_amount_column_confirmation")
        issues.append(GeoXPanelExpIntegrationIssueCode.SPEND_AMOUNT_COLUMN_MISSING)
    return issues


def _assignment_mapping_confirmed(
    handoff: GeoXReadoutInputHandoff,
    availability: GeoXMaterializedInputAvailability,
    lineage: dict[str, str],
    missing_mappings: list[str],
) -> bool:
    if availability.has_materialized_assignment_df:
        return True
    if handoff.assignment_artifact_ref is not None:
        return True
    if availability.has_assignment_mapping:
        if lineage.get("assignment_join_keys_confirmed") == "true":
            return True
        if lineage.get("geo_unit_column") and (
            lineage.get("cell_column") or lineage.get("treatment_control_label_column")
        ):
            return True
        missing_mappings.append("assignment_join_keys")
        return False
    return True


def _baseline_satisfied(
    handoff: GeoXReadoutInputHandoff,
    experiment_type: GeoXPostTestExperimentType,
    lineage: dict[str, str],
) -> bool:
    if experiment_type in _BASELINE_REQUIRED_TYPES:
        if handoff.spend_baseline_definition_optional:
            return True
        if lineage.get("baseline_or_counterfactual_available") == "true":
            return True
        return False
    if experiment_type == GeoXPostTestExperimentType.HOLDOUT:
        return (
            lineage.get("treatment_control_comparators_available") == "true"
            or handoff.assignment_artifact_ref is not None
            or lineage.get("baseline_or_counterfactual_available") == "true"
        )
    if experiment_type == GeoXPostTestExperimentType.DOSAGE:
        return lineage.get("dosage_cells_available") == "true"
    if experiment_type == GeoXPostTestExperimentType.REALLOCATION:
        return lineage.get("reallocation_scopes_available") == "true"
    return True


def _resolve_experiment_type(lineage: dict[str, str]) -> GeoXPostTestExperimentType:
    raw = lineage.get("experiment_type", "").strip().lower()
    if not raw:
        return GeoXPostTestExperimentType.UNKNOWN
    try:
        return GeoXPostTestExperimentType(raw)
    except ValueError:
        return GeoXPostTestExperimentType.UNKNOWN


def _baseline_requirements_for_type(
    experiment_type: GeoXPostTestExperimentType,
) -> list[str]:
    if experiment_type == GeoXPostTestExperimentType.GO_DARK:
        return ["bau_counterfactual_spend"]
    if experiment_type == GeoXPostTestExperimentType.HEAVY_UP:
        return ["bau_counterfactual_spend"]
    if experiment_type == GeoXPostTestExperimentType.HOLDOUT:
        return ["treatment_control_baseline_comparators"]
    if experiment_type == GeoXPostTestExperimentType.DOSAGE:
        return ["treatment_dosage_cells", "baseline_control_dosage_cells"]
    if experiment_type == GeoXPostTestExperimentType.REALLOCATION:
        return ["added_spend_scope", "removed_spend_scope"]
    return []


def _default_input_requirements(
    experiment_type: GeoXPostTestExperimentType,
) -> GeoXPostTestSpendInputRequirements:
    required = [
        "experiment_id",
        "spend_df",
        "assignment_df_or_mapping",
        "spend_date_column",
        "spend_geo_column",
        "spend_amount_column",
        "post_period_start",
        "post_period_end",
        "experiment_type",
    ]
    optional = ["currency_column", "channel_column", "source_lineage"]
    baseline_required = experiment_type in _BASELINE_REQUIRED_TYPES
    if baseline_required:
        required.append("baseline_or_counterfactual_spend")
    return GeoXPostTestSpendInputRequirements(
        baseline_or_counterfactual_required=baseline_required,
        required_fields=required,
        optional_fields=optional,
        warnings=[
            "PostTestSpendInput must be materialized in package runtime; "
            "MIP passes refs only."
        ],
    )


def _mapped_handoff_fields(handoff: GeoXReadoutInputHandoff) -> dict[str, str]:
    mapped: dict[str, str] = {
        "experiment_id": handoff.experiment_id,
        "readout_intent": str(handoff.readout_intent),
        "mip_resolution_status": str(handoff.mip_resolution_status),
    }
    spend = handoff.spend_column_mapping_optional
    if spend is not None:
        if spend.date_week_column:
            mapped["spend_date_column"] = spend.date_week_column
        if spend.geo_unit_column:
            mapped["spend_geo_column"] = spend.geo_unit_column
        if spend.spend_amount_column:
            mapped["spend_amount_column"] = spend.spend_amount_column
    if handoff.spend_dataset_ref_optional is not None:
        mapped["spend_dataset_ref_id"] = handoff.spend_dataset_ref_optional.dataset_ref_id
    if handoff.spend_baseline_definition_optional:
        mapped["spend_baseline_definition"] = handoff.spend_baseline_definition_optional
    return mapped


def _handoff_ref_summary(handoff: GeoXReadoutInputHandoff) -> dict[str, str]:
    summary = {
        "request_id": handoff.request_id,
        "experiment_id": handoff.experiment_id,
        "panel_exp_target_contract": handoff.panel_exp_target_contract,
        "panel_exp_expected_runtime": handoff.panel_exp_expected_runtime,
    }
    if handoff.kpi_dataset_ref is not None:
        summary["kpi_dataset_ref_id"] = handoff.kpi_dataset_ref.dataset_ref_id
    if handoff.spend_dataset_ref_optional is not None:
        summary["spend_dataset_ref_id"] = handoff.spend_dataset_ref_optional.dataset_ref_id
    return summary


def _user_messages_for_status(status: GeoXPanelExpIntegrationStatus) -> list[str]:
    mapping = {
        GeoXPanelExpIntegrationStatus.BLOCKED_NO_SPEND_READINESS_REQUESTED: [
            _MSG_NO_SPEND_READINESS
        ],
        GeoXPanelExpIntegrationStatus.BLOCKED_MATERIALIZED_SPEND_INPUT_REQUIRED: [
            _MSG_MATERIALIZED_SPEND_REQUIRED
        ],
        GeoXPanelExpIntegrationStatus.BLOCKED_MATERIALIZED_ASSIGNMENT_INPUT_REQUIRED: [
            _MSG_MATERIALIZED_ASSIGNMENT_REQUIRED
        ],
        GeoXPanelExpIntegrationStatus.BLOCKED_MISSING_CONFIRMED_SPEND_MAPPING: [
            _MSG_SPEND_MAPPING_MISSING
        ],
        GeoXPanelExpIntegrationStatus.BLOCKED_MISSING_CONFIRMED_ASSIGNMENT_MAPPING: [
            _MSG_ASSIGNMENT_MAPPING_MISSING
        ],
        GeoXPanelExpIntegrationStatus.BLOCKED_MISSING_POST_PERIOD_DATES: [
            _MSG_POST_PERIOD_DATES_MISSING
        ],
        GeoXPanelExpIntegrationStatus.BLOCKED_MISSING_EXPERIMENT_TYPE: [
            _MSG_EXPERIMENT_TYPE_MISSING
        ],
        GeoXPanelExpIntegrationStatus.BLOCKED_MISSING_BASELINE_FOR_EXPERIMENT_TYPE: [
            _MSG_BASELINE_MISSING
        ],
        GeoXPanelExpIntegrationStatus.READY_TO_BUILD_POST_TEST_SPEND_INPUT: [
            "Adapter input plan is ready. Stage 3B may build "
            "PostTestSpendInput after materialization."
        ],
        GeoXPanelExpIntegrationStatus.READY_TO_CALL_GEOX_POST_TEST_SPEND_RUNTIME: [
            "Materialized inputs and mappings are ready, but runtime call is deferred to Stage 3B."
        ],
    }
    return mapping.get(status, [_MSG_RUNTIME_NOT_CONFIGURED])


def _dedupe_issues(
    issues: list[GeoXPanelExpIntegrationIssueCode],
) -> list[GeoXPanelExpIntegrationIssueCode]:
    seen: set[GeoXPanelExpIntegrationIssueCode] = set()
    ordered: list[GeoXPanelExpIntegrationIssueCode] = []
    for issue in issues:
        if issue not in seen:
            seen.add(issue)
            ordered.append(issue)
    return ordered


def _plan(
    request: GeoXPanelExpIntegrationRequest,
    status: GeoXPanelExpIntegrationStatus,
    availability: GeoXMaterializedInputAvailability,
    input_requirements: GeoXPostTestSpendInputRequirements,
    handoff_summary: dict[str, str],
    mapped_fields: dict[str, str],
    missing_materialized: list[str],
    missing_mappings: list[str],
    missing_metadata: list[str],
    experiment_type: GeoXPostTestExperimentType,
    baseline_requirements: list[str],
    lineage: dict[str, str],
    issues: list[GeoXPanelExpIntegrationIssueCode],
    warnings: list[str],
    *,
    ready_to_call: bool,
) -> GeoXPostTestSpendAdapterInputPlan:
    return GeoXPostTestSpendAdapterInputPlan(
        request_id=request.request_id,
        experiment_id=request.handoff.experiment_id,
        integration_status=status,
        runtime_reference=GeoXPanelExpRuntimeReference(),
        handoff_ref_summary=handoff_summary,
        materialized_input_availability=availability,
        input_requirements=input_requirements,
        required_panel_exp_fields=list(input_requirements.required_fields),
        mapped_handoff_fields=mapped_fields,
        missing_materialized_inputs=missing_materialized,
        missing_required_mappings=missing_mappings,
        missing_required_metadata=missing_metadata,
        experiment_type=experiment_type,
        baseline_requirements=baseline_requirements,
        source_lineage=lineage,
        issues=_dedupe_issues(issues),
        warnings=warnings,
        ready_to_call_runtime=ready_to_call,
    )
