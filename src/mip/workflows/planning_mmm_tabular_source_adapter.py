"""Planning/MMM tabular source adapter compatibility workflow.

Maps generic TabularSourceInspectionResult outputs to Planning/MMM intake semantics
without re-reading CSVs, calling connectors, or mutating existing uploaded CSV lanes.
"""

from __future__ import annotations

from mip.contracts.intake_sources import DataSourceRef
from mip.contracts.planning_mmm_tabular_source_adapter import (
    PlanningMMMTabularSourceAdapterIssueCode,
    PlanningMMMTabularSourceAdapterRequest,
    PlanningMMMTabularSourceAdapterResult,
    PlanningMMMTabularSourceAdapterStatus,
    PlanningMMMTabularSourceInputAvailability,
    PlanningMMMTabularSourceRoleMapping,
    PlanningMMMTabularSourceRoleSource,
)
from mip.contracts.planning_mmm_uploaded_csv_adapter import (
    PlanningMMMUploadedCSVAdapterIssueCode,
    PlanningMMMUploadedCSVAdapterResult,
    PlanningMMMUploadedCSVAdapterStatus,
    PlanningMMMUploadedCSVInputAvailability,
    PlanningMMMUploadedCSVRole,
    PlanningMMMUploadedCSVRoleMapping,
    PlanningMMMUploadedCSVRoleSource,
)
from mip.contracts.planning_mmm_uploaded_csv_input_plan import (
    PlanningMMMUploadedCSVInputPlanRequest,
)
from mip.contracts.tabular_source_reference import (
    TabularSourceInspection,
    TabularSourceInspectionStatus,
    TabularSourceReference,
)

_READY_TABULAR_STATUSES = {
    TabularSourceInspectionStatus.INSPECTED,
    TabularSourceInspectionStatus.INSPECTED_WITH_WARNINGS,
}
_REQUIRED_ROLES = {
    PlanningMMMUploadedCSVRole.HISTORICAL_SPEND,
    PlanningMMMUploadedCSVRole.HISTORICAL_OUTCOME,
}
_OPTIONAL_ROLES = {
    PlanningMMMUploadedCSVRole.CHANNEL_TAXONOMY,
    PlanningMMMUploadedCSVRole.BUDGET_CONSTRAINTS,
    PlanningMMMUploadedCSVRole.CALIBRATION_SIGNALS,
    PlanningMMMUploadedCSVRole.MODEL_CONFIG,
}
_ROLE_ALIASES: dict[str, PlanningMMMUploadedCSVRole] = {
    "historical_spend": PlanningMMMUploadedCSVRole.HISTORICAL_SPEND,
    "spend": PlanningMMMUploadedCSVRole.HISTORICAL_SPEND,
    "media_spend": PlanningMMMUploadedCSVRole.HISTORICAL_SPEND,
    "marketing_spend": PlanningMMMUploadedCSVRole.HISTORICAL_SPEND,
    "historical_outcome": PlanningMMMUploadedCSVRole.HISTORICAL_OUTCOME,
    "outcome": PlanningMMMUploadedCSVRole.HISTORICAL_OUTCOME,
    "kpi": PlanningMMMUploadedCSVRole.HISTORICAL_OUTCOME,
    "revenue": PlanningMMMUploadedCSVRole.HISTORICAL_OUTCOME,
    "conversions": PlanningMMMUploadedCSVRole.HISTORICAL_OUTCOME,
    "sales": PlanningMMMUploadedCSVRole.HISTORICAL_OUTCOME,
    "channel_taxonomy": PlanningMMMUploadedCSVRole.CHANNEL_TAXONOMY,
    "taxonomy": PlanningMMMUploadedCSVRole.CHANNEL_TAXONOMY,
    "channel_mapping": PlanningMMMUploadedCSVRole.CHANNEL_TAXONOMY,
    "budget_constraints": PlanningMMMUploadedCSVRole.BUDGET_CONSTRAINTS,
    "constraints": PlanningMMMUploadedCSVRole.BUDGET_CONSTRAINTS,
    "planning_constraints": PlanningMMMUploadedCSVRole.BUDGET_CONSTRAINTS,
    "scenario_constraints": PlanningMMMUploadedCSVRole.BUDGET_CONSTRAINTS,
    "calibration_signals": PlanningMMMUploadedCSVRole.CALIBRATION_SIGNALS,
    "calibration": PlanningMMMUploadedCSVRole.CALIBRATION_SIGNALS,
    "priors": PlanningMMMUploadedCSVRole.CALIBRATION_SIGNALS,
    "experiment_priors": PlanningMMMUploadedCSVRole.CALIBRATION_SIGNALS,
    "model_config": PlanningMMMUploadedCSVRole.MODEL_CONFIG,
    "mmm_config": PlanningMMMUploadedCSVRole.MODEL_CONFIG,
    "config": PlanningMMMUploadedCSVRole.MODEL_CONFIG,
}
_OPTIONAL_MISSING_ISSUE: dict[
    PlanningMMMUploadedCSVRole, PlanningMMMTabularSourceAdapterIssueCode
] = {
    PlanningMMMUploadedCSVRole.CHANNEL_TAXONOMY: (
        PlanningMMMTabularSourceAdapterIssueCode.OPTIONAL_CHANNEL_TAXONOMY_MISSING
    ),
    PlanningMMMUploadedCSVRole.BUDGET_CONSTRAINTS: (
        PlanningMMMTabularSourceAdapterIssueCode.OPTIONAL_BUDGET_CONSTRAINTS_MISSING
    ),
    PlanningMMMUploadedCSVRole.CALIBRATION_SIGNALS: (
        PlanningMMMTabularSourceAdapterIssueCode.OPTIONAL_CALIBRATION_SIGNALS_MISSING
    ),
    PlanningMMMUploadedCSVRole.MODEL_CONFIG: (
        PlanningMMMTabularSourceAdapterIssueCode.OPTIONAL_MODEL_CONFIG_MISSING
    ),
}
_TABULAR_TO_UPLOADED_STATUS: dict[
    PlanningMMMTabularSourceAdapterStatus, PlanningMMMUploadedCSVAdapterStatus
] = {
    PlanningMMMTabularSourceAdapterStatus.ADAPTED: PlanningMMMUploadedCSVAdapterStatus.ADAPTED,
    PlanningMMMTabularSourceAdapterStatus.ADAPTED_WITH_WARNINGS: (
        PlanningMMMUploadedCSVAdapterStatus.ADAPTED_WITH_WARNINGS
    ),
    PlanningMMMTabularSourceAdapterStatus.BLOCKED_MISSING_TABULAR_SOURCE_RESULT: (
        PlanningMMMUploadedCSVAdapterStatus.BLOCKED_MISSING_MATERIALIZATION_RESULT
    ),
    PlanningMMMTabularSourceAdapterStatus.BLOCKED_TABULAR_SOURCE_NOT_READY: (
        PlanningMMMUploadedCSVAdapterStatus.BLOCKED_MATERIALIZATION_NOT_READY
    ),
    PlanningMMMTabularSourceAdapterStatus.BLOCKED_MISSING_REQUIRED_ROLE: (
        PlanningMMMUploadedCSVAdapterStatus.BLOCKED_MISSING_REQUIRED_ROLE
    ),
    PlanningMMMTabularSourceAdapterStatus.BLOCKED_DUPLICATE_ROLE: (
        PlanningMMMUploadedCSVAdapterStatus.BLOCKED_DUPLICATE_ROLE
    ),
    PlanningMMMTabularSourceAdapterStatus.BLOCKED_AMBIGUOUS_ROLE: (
        PlanningMMMUploadedCSVAdapterStatus.BLOCKED_AMBIGUOUS_ROLE
    ),
    PlanningMMMTabularSourceAdapterStatus.BLOCKED_MISSING_REQUIRED_COLUMNS: (
        PlanningMMMUploadedCSVAdapterStatus.BLOCKED_MISSING_REQUIRED_COLUMNS
    ),
    PlanningMMMTabularSourceAdapterStatus.BLOCKED_DATA_SOURCE_REF_UNAVAILABLE: (
        PlanningMMMUploadedCSVAdapterStatus.BLOCKED_DATA_SOURCE_REF_BUILD_FAILED
    ),
}


def adapt_tabular_sources_for_planning_mmm(
    request: PlanningMMMTabularSourceAdapterRequest,
) -> PlanningMMMTabularSourceAdapterResult:
    """Adapt generic tabular source inspection outputs for Planning/MMM intake."""
    lineage = {
        **request.lineage,
        "adapter_stage": "planning_mmm_tabular_source_adapter",
    }
    warnings = list(dict.fromkeys(request.warnings))
    issues: list[PlanningMMMTabularSourceAdapterIssueCode] = [
        PlanningMMMTabularSourceAdapterIssueCode.TABULAR_SOURCE_LINEAGE_PRESERVED,
        PlanningMMMTabularSourceAdapterIssueCode.NO_CONNECTOR_RUNTIME,
        PlanningMMMTabularSourceAdapterIssueCode.NO_MODEL_EXECUTION,
        PlanningMMMTabularSourceAdapterIssueCode.NO_OPTIMIZER_EXECUTION,
        PlanningMMMTabularSourceAdapterIssueCode.NO_RECOMMENDATION_GENERATED,
    ]

    if request.tabular_source_result is None:
        return _blocked(
            request.request_id,
            PlanningMMMTabularSourceAdapterStatus.BLOCKED_MISSING_TABULAR_SOURCE_RESULT,
            issues + [PlanningMMMTabularSourceAdapterIssueCode.MISSING_TABULAR_SOURCE_RESULT],
            warnings,
            lineage,
        )

    tabular_result = request.tabular_source_result
    warnings.extend(tabular_result.warnings)
    lineage.update(tabular_result.lineage)

    if tabular_result.status not in _READY_TABULAR_STATUSES:
        return _blocked(
            request.request_id,
            PlanningMMMTabularSourceAdapterStatus.BLOCKED_TABULAR_SOURCE_NOT_READY,
            issues + [PlanningMMMTabularSourceAdapterIssueCode.TABULAR_SOURCE_NOT_READY],
            warnings,
            lineage,
        )

    RoleAssignment = tuple[
        TabularSourceInspection,
        PlanningMMMUploadedCSVRole,
        PlanningMMMTabularSourceRoleSource,
    ]
    role_assignments: list[RoleAssignment] = []

    for inspection in tabular_result.inspections:
        role, role_source, role_issues = _resolve_role(inspection, request)
        issues.extend(role_issues)
        if role == PlanningMMMUploadedCSVRole.UNKNOWN:
            return _blocked(
                request.request_id,
                PlanningMMMTabularSourceAdapterStatus.BLOCKED_AMBIGUOUS_ROLE,
                issues + [PlanningMMMTabularSourceAdapterIssueCode.AMBIGUOUS_ROLE],
                warnings,
                lineage,
            )
        role_assignments.append((inspection, role, role_source))

    role_counts: dict[PlanningMMMUploadedCSVRole, int] = {}
    for _, role, _ in role_assignments:
        role_counts[role] = role_counts.get(role, 0) + 1

    for role in _REQUIRED_ROLES | _OPTIONAL_ROLES:
        if role_counts.get(role, 0) > 1:
            return _blocked(
                request.request_id,
                PlanningMMMTabularSourceAdapterStatus.BLOCKED_DUPLICATE_ROLE,
                issues + [PlanningMMMTabularSourceAdapterIssueCode.DUPLICATE_ROLE],
                warnings + [f"Duplicate Planning/MMM role: {role}"],
                lineage,
            )

    present_roles = set(role_counts)
    missing_required = _REQUIRED_ROLES - present_roles
    if missing_required:
        return _blocked(
            request.request_id,
            PlanningMMMTabularSourceAdapterStatus.BLOCKED_MISSING_REQUIRED_ROLE,
            issues + [PlanningMMMTabularSourceAdapterIssueCode.MISSING_REQUIRED_ROLE],
            warnings
            + [
                "Missing required Planning/MMM roles: "
                + ", ".join(sorted(str(role) for role in missing_required))
            ],
            lineage,
        )

    for optional_role in _OPTIONAL_ROLES:
        if optional_role not in present_roles:
            warnings.append(f"Optional Planning/MMM role not provided: {optional_role}")
            issues.append(_OPTIONAL_MISSING_ISSUE[optional_role])

    role_mappings: list[PlanningMMMTabularSourceRoleMapping] = []
    data_source_refs: list[DataSourceRef] = []
    tabular_source_references: list[TabularSourceReference] = []

    for inspection, role, role_source in role_assignments:
        reference = inspection.source_reference
        schema = inspection.source_schema
        normalized_columns = (
            list(schema.normalized_column_names) if schema is not None else []
        )
        available_columns = list(schema.column_names) if schema is not None else []
        required_columns = list(request.required_columns_by_role.get(str(role), []))
        missing_columns = [
            column for column in required_columns if column not in normalized_columns
        ]
        if missing_columns:
            return _blocked(
                request.request_id,
                PlanningMMMTabularSourceAdapterStatus.BLOCKED_MISSING_REQUIRED_COLUMNS,
                issues + [PlanningMMMTabularSourceAdapterIssueCode.MISSING_REQUIRED_COLUMNS],
                warnings
                + [f"Missing required columns for {role}: {', '.join(missing_columns)}"],
                lineage,
            )

        data_source_ref = reference.data_source_ref
        if data_source_ref is None:
            return _blocked(
                request.request_id,
                PlanningMMMTabularSourceAdapterStatus.BLOCKED_DATA_SOURCE_REF_UNAVAILABLE,
                issues + [PlanningMMMTabularSourceAdapterIssueCode.DATA_SOURCE_REF_UNAVAILABLE],
                warnings + [f"DataSourceRef unavailable for source_id={reference.source_id}"],
                lineage,
            )

        dataset_id = (
            inspection.availability.materialized_dataset_id
            if inspection.availability and inspection.availability.materialized_dataset_id
            else f"tabular:{reference.source_id}"
        )
        mapping_issues = [
            PlanningMMMTabularSourceAdapterIssueCode.TABULAR_SOURCE_SCHEMA_USED,
            PlanningMMMTabularSourceAdapterIssueCode.TABULAR_SOURCE_REFERENCE_PRESERVED,
            PlanningMMMTabularSourceAdapterIssueCode.DATA_SOURCE_REF_PRESERVED,
        ]
        mapping = PlanningMMMTabularSourceRoleMapping(
            source_id=reference.source_id,
            source_type=reference.source_type,
            source_name=reference.source_name,
            role=role,
            role_source=role_source,
            required_columns=required_columns,
            available_columns=available_columns,
            normalized_columns=normalized_columns,
            missing_columns=missing_columns,
            data_source_ref=data_source_ref,
            tabular_source_reference=reference,
            lineage={
                **(inspection.lineage.metadata if inspection.lineage else {}),
                **(inspection.lineage.upstream_lineage if inspection.lineage else {}),
                **reference.metadata,
                "dataset_id": dataset_id,
                "planning_mmm_role": str(role),
                "role_source": str(role_source),
            },
            warnings=list(inspection.warnings),
            issues=mapping_issues,
        )
        role_mappings.append(mapping)
        data_source_refs.append(data_source_ref)
        tabular_source_references.append(reference)
        issues.extend(mapping_issues)

    issues.append(
        PlanningMMMTabularSourceAdapterIssueCode.UPLOADED_CSV_COMPATIBILITY_PATH_SUPPORTED
    )

    availability = _build_availability(
        role_mappings,
        data_source_refs,
        tabular_source_references,
        lineage,
    )
    status = PlanningMMMTabularSourceAdapterStatus.ADAPTED
    if warnings:
        status = PlanningMMMTabularSourceAdapterStatus.ADAPTED_WITH_WARNINGS

    return PlanningMMMTabularSourceAdapterResult(
        request_id=request.request_id,
        status=status,
        availability=availability,
        role_mappings=role_mappings,
        data_source_refs=data_source_refs,
        tabular_source_references=tabular_source_references,
        issues=_dedupe_issues(issues),
        warnings=list(dict.fromkeys(warnings)),
        lineage=lineage,
    )


def build_uploaded_csv_adapter_result_from_tabular_source_adapter_result(
    result: PlanningMMMTabularSourceAdapterResult,
) -> PlanningMMMUploadedCSVAdapterResult:
    """Convert tabular source adapter output into uploaded CSV adapter result shape."""
    uploaded_role_mappings = [
        PlanningMMMUploadedCSVRoleMapping(
            source_id=mapping.source_id,
            dataset_id=mapping.lineage.get("dataset_id", f"tabular:{mapping.source_id}"),
            role=mapping.role,
            role_source=_to_uploaded_role_source(mapping.role_source),
            required_columns=list(mapping.required_columns),
            available_columns=list(mapping.available_columns),
            normalized_columns=list(mapping.normalized_columns),
            missing_columns=list(mapping.missing_columns),
            data_source_ref=mapping.data_source_ref,
            lineage=dict(mapping.lineage),
            warnings=list(mapping.warnings),
            issues=[PlanningMMMUploadedCSVAdapterIssueCode.DATA_SOURCE_REF_CREATED],
        )
        for mapping in result.role_mappings
    ]
    uploaded_availability = _to_uploaded_availability(result.availability, uploaded_role_mappings)
    uploaded_issues = _to_uploaded_issues(result.issues)
    return PlanningMMMUploadedCSVAdapterResult(
        request_id=result.request_id,
        status=_TABULAR_TO_UPLOADED_STATUS.get(
            result.status,
            PlanningMMMUploadedCSVAdapterStatus.BLOCKED_MATERIALIZATION_NOT_READY,
        ),
        availability=uploaded_availability,
        role_mappings=uploaded_role_mappings,
        data_source_refs=list(result.data_source_refs),
        issues=uploaded_issues,
        warnings=list(result.warnings),
        lineage={
            **result.lineage,
            "compatibility_bridge": "planning_mmm_tabular_source_adapter",
        },
    )


def build_uploaded_csv_input_plan_request_from_tabular_source_adapter_result(
    result: PlanningMMMTabularSourceAdapterResult,
    *,
    request_id: str,
    required_columns_by_role: dict[str, list[str]] | None = None,
    require_channel_taxonomy: bool = False,
    require_budget_constraints: bool = False,
    require_calibration_signals: bool = False,
    require_model_config: bool = False,
    lineage: dict[str, str] | None = None,
    warnings: list[str] | None = None,
) -> PlanningMMMUploadedCSVInputPlanRequest:
    """Build an input-plan request from tabular source adapter output."""
    return PlanningMMMUploadedCSVInputPlanRequest(
        request_id=request_id,
        adapter_result=build_uploaded_csv_adapter_result_from_tabular_source_adapter_result(
            result
        ),
        required_columns_by_role=required_columns_by_role or {},
        require_channel_taxonomy=require_channel_taxonomy,
        require_budget_constraints=require_budget_constraints,
        require_calibration_signals=require_calibration_signals,
        require_model_config=require_model_config,
        lineage={
            **(lineage or {}),
            "input_plan_source": "planning_mmm_tabular_source_adapter",
        },
        warnings=list(warnings or []),
    )


def _resolve_role(
    inspection: TabularSourceInspection,
    request: PlanningMMMTabularSourceAdapterRequest,
) -> tuple[
    PlanningMMMUploadedCSVRole,
    PlanningMMMTabularSourceRoleSource,
    list[PlanningMMMTabularSourceAdapterIssueCode],
]:
    issues: list[PlanningMMMTabularSourceAdapterIssueCode] = []
    source_id = inspection.source_reference.source_id
    if source_id in request.explicit_role_by_source_id:
        issues.append(PlanningMMMTabularSourceAdapterIssueCode.ROLE_EXPLICITLY_PROVIDED)
        return (
            request.explicit_role_by_source_id[source_id],
            PlanningMMMTabularSourceRoleSource.EXPLICIT,
            issues,
        )

    hint = (inspection.source_reference.declared_role_hint or "").strip().lower()
    if hint and hint in _ROLE_ALIASES:
        issues.append(PlanningMMMTabularSourceAdapterIssueCode.ROLE_HINT_USED)
        return (
            _ROLE_ALIASES[hint],
            PlanningMMMTabularSourceRoleSource.DECLARED_ROLE_HINT,
            issues,
        )

    return PlanningMMMUploadedCSVRole.UNKNOWN, PlanningMMMTabularSourceRoleSource.UNKNOWN, issues


def _build_availability(
    role_mappings: list[PlanningMMMTabularSourceRoleMapping],
    data_source_refs: list[DataSourceRef],
    tabular_source_references: list[TabularSourceReference],
    lineage: dict[str, str],
) -> PlanningMMMTabularSourceInputAvailability:
    by_role = {mapping.role: mapping for mapping in role_mappings}
    spend = by_role.get(PlanningMMMUploadedCSVRole.HISTORICAL_SPEND)
    outcome = by_role.get(PlanningMMMUploadedCSVRole.HISTORICAL_OUTCOME)
    taxonomy = by_role.get(PlanningMMMUploadedCSVRole.CHANNEL_TAXONOMY)
    budget = by_role.get(PlanningMMMUploadedCSVRole.BUDGET_CONSTRAINTS)
    calibration = by_role.get(PlanningMMMUploadedCSVRole.CALIBRATION_SIGNALS)
    model_config = by_role.get(PlanningMMMUploadedCSVRole.MODEL_CONFIG)
    return PlanningMMMTabularSourceInputAvailability(
        has_historical_spend=spend is not None,
        has_historical_outcome=outcome is not None,
        has_channel_taxonomy=taxonomy is not None,
        has_budget_constraints=budget is not None,
        has_calibration_signals=calibration is not None,
        has_model_config=model_config is not None,
        historical_spend_source_id=spend.source_id if spend else None,
        historical_outcome_source_id=outcome.source_id if outcome else None,
        channel_taxonomy_source_id=taxonomy.source_id if taxonomy else None,
        budget_constraints_source_id=budget.source_id if budget else None,
        calibration_signals_source_id=calibration.source_id if calibration else None,
        model_config_source_id=model_config.source_id if model_config else None,
        data_source_refs=list(data_source_refs),
        role_mappings=list(role_mappings),
        tabular_source_references=list(tabular_source_references),
        lineage={
            **lineage,
            "role_mapping_count": str(len(role_mappings)),
        },
    )


def _to_uploaded_role_source(
    role_source: PlanningMMMTabularSourceRoleSource,
) -> PlanningMMMUploadedCSVRoleSource:
    if role_source == PlanningMMMTabularSourceRoleSource.EXPLICIT:
        return PlanningMMMUploadedCSVRoleSource.EXPLICIT
    if role_source == PlanningMMMTabularSourceRoleSource.DECLARED_ROLE_HINT:
        return PlanningMMMUploadedCSVRoleSource.DECLARED_ROLE_HINT
    return PlanningMMMUploadedCSVRoleSource.UNKNOWN


def _to_uploaded_availability(
    availability: PlanningMMMTabularSourceInputAvailability | None,
    role_mappings: list[PlanningMMMUploadedCSVRoleMapping],
) -> PlanningMMMUploadedCSVInputAvailability | None:
    if availability is None:
        return None
    return PlanningMMMUploadedCSVInputAvailability(
        has_historical_spend=availability.has_historical_spend,
        has_historical_outcome=availability.has_historical_outcome,
        has_channel_taxonomy=availability.has_channel_taxonomy,
        has_budget_constraints=availability.has_budget_constraints,
        has_calibration_signals=availability.has_calibration_signals,
        has_model_config=availability.has_model_config,
        historical_spend_source_id=availability.historical_spend_source_id,
        historical_outcome_source_id=availability.historical_outcome_source_id,
        channel_taxonomy_source_id=availability.channel_taxonomy_source_id,
        budget_constraints_source_id=availability.budget_constraints_source_id,
        calibration_signals_source_id=availability.calibration_signals_source_id,
        model_config_source_id=availability.model_config_source_id,
        data_source_refs=list(availability.data_source_refs),
        role_mappings=list(role_mappings),
        lineage=dict(availability.lineage),
    )


def _to_uploaded_issues(
    issues: list[PlanningMMMTabularSourceAdapterIssueCode],
) -> list[PlanningMMMUploadedCSVAdapterIssueCode]:
    mapping: dict[
        PlanningMMMTabularSourceAdapterIssueCode,
        PlanningMMMUploadedCSVAdapterIssueCode,
    ] = {
        PlanningMMMTabularSourceAdapterIssueCode.MISSING_TABULAR_SOURCE_RESULT: (
            PlanningMMMUploadedCSVAdapterIssueCode.MISSING_MATERIALIZATION_RESULT
        ),
        PlanningMMMTabularSourceAdapterIssueCode.TABULAR_SOURCE_NOT_READY: (
            PlanningMMMUploadedCSVAdapterIssueCode.MATERIALIZATION_NOT_READY
        ),
        PlanningMMMTabularSourceAdapterIssueCode.MISSING_REQUIRED_ROLE: (
            PlanningMMMUploadedCSVAdapterIssueCode.MISSING_REQUIRED_ROLE
        ),
        PlanningMMMTabularSourceAdapterIssueCode.DUPLICATE_ROLE: (
            PlanningMMMUploadedCSVAdapterIssueCode.DUPLICATE_ROLE
        ),
        PlanningMMMTabularSourceAdapterIssueCode.AMBIGUOUS_ROLE: (
            PlanningMMMUploadedCSVAdapterIssueCode.AMBIGUOUS_ROLE
        ),
        PlanningMMMTabularSourceAdapterIssueCode.MISSING_REQUIRED_COLUMNS: (
            PlanningMMMUploadedCSVAdapterIssueCode.MISSING_REQUIRED_COLUMNS
        ),
        PlanningMMMTabularSourceAdapterIssueCode.DATA_SOURCE_REF_UNAVAILABLE: (
            PlanningMMMUploadedCSVAdapterIssueCode.DATA_SOURCE_REF_BUILD_FAILED
        ),
        PlanningMMMTabularSourceAdapterIssueCode.ROLE_HINT_USED: (
            PlanningMMMUploadedCSVAdapterIssueCode.ROLE_HINT_USED
        ),
        PlanningMMMTabularSourceAdapterIssueCode.ROLE_EXPLICITLY_PROVIDED: (
            PlanningMMMUploadedCSVAdapterIssueCode.ROLE_EXPLICITLY_PROVIDED
        ),
        PlanningMMMTabularSourceAdapterIssueCode.OPTIONAL_CHANNEL_TAXONOMY_MISSING: (
            PlanningMMMUploadedCSVAdapterIssueCode.OPTIONAL_CHANNEL_TAXONOMY_MISSING
        ),
        PlanningMMMTabularSourceAdapterIssueCode.OPTIONAL_BUDGET_CONSTRAINTS_MISSING: (
            PlanningMMMUploadedCSVAdapterIssueCode.OPTIONAL_BUDGET_CONSTRAINTS_MISSING
        ),
        PlanningMMMTabularSourceAdapterIssueCode.OPTIONAL_CALIBRATION_SIGNALS_MISSING: (
            PlanningMMMUploadedCSVAdapterIssueCode.OPTIONAL_CALIBRATION_SIGNALS_MISSING
        ),
        PlanningMMMTabularSourceAdapterIssueCode.OPTIONAL_MODEL_CONFIG_MISSING: (
            PlanningMMMUploadedCSVAdapterIssueCode.OPTIONAL_MODEL_CONFIG_MISSING
        ),
        PlanningMMMTabularSourceAdapterIssueCode.TABULAR_SOURCE_LINEAGE_PRESERVED: (
            PlanningMMMUploadedCSVAdapterIssueCode.LINEAGE_PRESERVED
        ),
    }
    uploaded: list[PlanningMMMUploadedCSVAdapterIssueCode] = []
    for issue in issues:
        mapped = mapping.get(issue)
        if mapped is not None:
            uploaded.append(mapped)
    if PlanningMMMUploadedCSVAdapterIssueCode.LINEAGE_PRESERVED not in uploaded:
        uploaded.insert(0, PlanningMMMUploadedCSVAdapterIssueCode.LINEAGE_PRESERVED)
    return _dedupe_uploaded_issues(uploaded)


def _blocked(
    request_id: str,
    status: PlanningMMMTabularSourceAdapterStatus,
    issues: list[PlanningMMMTabularSourceAdapterIssueCode],
    warnings: list[str],
    lineage: dict[str, str],
) -> PlanningMMMTabularSourceAdapterResult:
    return PlanningMMMTabularSourceAdapterResult(
        request_id=request_id,
        status=status,
        issues=_dedupe_issues(issues),
        warnings=list(dict.fromkeys(warnings)),
        lineage=lineage,
    )


def _dedupe_issues(
    issues: list[PlanningMMMTabularSourceAdapterIssueCode],
) -> list[PlanningMMMTabularSourceAdapterIssueCode]:
    seen: set[PlanningMMMTabularSourceAdapterIssueCode] = set()
    ordered: list[PlanningMMMTabularSourceAdapterIssueCode] = []
    for issue in issues:
        if issue not in seen:
            seen.add(issue)
            ordered.append(issue)
    return ordered


def _dedupe_uploaded_issues(
    issues: list[PlanningMMMUploadedCSVAdapterIssueCode],
) -> list[PlanningMMMUploadedCSVAdapterIssueCode]:
    seen: set[PlanningMMMUploadedCSVAdapterIssueCode] = set()
    ordered: list[PlanningMMMUploadedCSVAdapterIssueCode] = []
    for issue in issues:
        if issue not in seen:
            seen.add(issue)
            ordered.append(issue)
    return ordered
