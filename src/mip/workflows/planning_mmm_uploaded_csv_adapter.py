"""Planning/MMM uploaded CSV adapter workflow.

Maps shared MaterializedTabularDataset outputs to Planning/MMM intake semantics.
Does not re-read CSVs or invoke MMM fitting, optimizers, or simulators.
"""

from __future__ import annotations

from datetime import UTC, datetime

from mip.contracts.intake_assets import DataAssetType
from mip.contracts.intake_sources import DataSourceRef
from mip.contracts.planning_mmm_uploaded_csv_adapter import (
    PlanningMMMUploadedCSVAdapterIssueCode,
    PlanningMMMUploadedCSVAdapterRequest,
    PlanningMMMUploadedCSVAdapterResult,
    PlanningMMMUploadedCSVAdapterStatus,
    PlanningMMMUploadedCSVInputAvailability,
    PlanningMMMUploadedCSVRole,
    PlanningMMMUploadedCSVRoleMapping,
    PlanningMMMUploadedCSVRoleSource,
)
from mip.contracts.uploaded_csv_materialization import (
    MaterializedTabularDataset,
    UploadedCSVInspection,
    UploadedCSVMaterializationStatus,
    UploadedCSVSource,
)
from mip.workflows.uploaded_csv_materialization import (
    build_data_source_ref_from_uploaded_csv_inspection,
)

_READY_MATERIALIZATION_STATUSES = {
    UploadedCSVMaterializationStatus.MATERIALIZED,
    UploadedCSVMaterializationStatus.MATERIALIZED_WITH_WARNINGS,
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
_ROLE_TO_ASSET_TYPE: dict[PlanningMMMUploadedCSVRole, DataAssetType] = {
    PlanningMMMUploadedCSVRole.HISTORICAL_SPEND: DataAssetType.MEDIA_SPEND_DATA,
    PlanningMMMUploadedCSVRole.HISTORICAL_OUTCOME: DataAssetType.OUTCOME_KPI_DATA,
    PlanningMMMUploadedCSVRole.CHANNEL_TAXONOMY: DataAssetType.CHANNEL_MAPPING,
    PlanningMMMUploadedCSVRole.BUDGET_CONSTRAINTS: DataAssetType.CONTROL_DATA,
    PlanningMMMUploadedCSVRole.CALIBRATION_SIGNALS: DataAssetType.CALIBRATION_SIGNAL_DATA,
    PlanningMMMUploadedCSVRole.MODEL_CONFIG: DataAssetType.METRIC_MAPPING,
    PlanningMMMUploadedCSVRole.UNKNOWN: DataAssetType.METRIC_MAPPING,
}
OptionalMissingIssue = dict[PlanningMMMUploadedCSVRole, PlanningMMMUploadedCSVAdapterIssueCode]
_OPTIONAL_MISSING_ISSUE: OptionalMissingIssue = {
    PlanningMMMUploadedCSVRole.CHANNEL_TAXONOMY: (
        PlanningMMMUploadedCSVAdapterIssueCode.OPTIONAL_CHANNEL_TAXONOMY_MISSING
    ),
    PlanningMMMUploadedCSVRole.BUDGET_CONSTRAINTS: (
        PlanningMMMUploadedCSVAdapterIssueCode.OPTIONAL_BUDGET_CONSTRAINTS_MISSING
    ),
    PlanningMMMUploadedCSVRole.CALIBRATION_SIGNALS: (
        PlanningMMMUploadedCSVAdapterIssueCode.OPTIONAL_CALIBRATION_SIGNALS_MISSING
    ),
    PlanningMMMUploadedCSVRole.MODEL_CONFIG: (
        PlanningMMMUploadedCSVAdapterIssueCode.OPTIONAL_MODEL_CONFIG_MISSING
    ),
}


def adapt_uploaded_csvs_for_planning_mmm(
    request: PlanningMMMUploadedCSVAdapterRequest,
) -> PlanningMMMUploadedCSVAdapterResult:
    """Adapt shared uploaded CSV materialization outputs for Planning/MMM intake."""
    lineage = {
        **request.lineage,
        "adapter_stage": "planning_mmm_uploaded_csv_adapter",
    }
    warnings = list(dict.fromkeys(request.warnings))
    issues: list[PlanningMMMUploadedCSVAdapterIssueCode] = [
        PlanningMMMUploadedCSVAdapterIssueCode.LINEAGE_PRESERVED,
        PlanningMMMUploadedCSVAdapterIssueCode.CSV_REPARSE_AVOIDED,
    ]

    if request.materialization_result is None:
        return _blocked(
            request.request_id,
            PlanningMMMUploadedCSVAdapterStatus.BLOCKED_MISSING_MATERIALIZATION_RESULT,
            issues + [PlanningMMMUploadedCSVAdapterIssueCode.MISSING_MATERIALIZATION_RESULT],
            warnings,
            lineage,
        )

    materialization = request.materialization_result
    warnings.extend(materialization.warnings)
    lineage.update(materialization.lineage)

    if materialization.status not in _READY_MATERIALIZATION_STATUSES:
        return _blocked(
            request.request_id,
            PlanningMMMUploadedCSVAdapterStatus.BLOCKED_MATERIALIZATION_NOT_READY,
            issues + [PlanningMMMUploadedCSVAdapterIssueCode.MATERIALIZATION_NOT_READY],
            warnings,
            lineage,
        )

    inspection_by_source = {
        inspection.source_id: inspection for inspection in materialization.inspections
    }
    RoleAssignment = tuple[
        MaterializedTabularDataset,
        UploadedCSVInspection,
        PlanningMMMUploadedCSVRole,
        PlanningMMMUploadedCSVRoleSource,
    ]
    role_assignments: list[RoleAssignment] = []

    for dataset in materialization.datasets:
        inspection = inspection_by_source.get(dataset.source_id)
        if inspection is None:
            return _blocked(
                request.request_id,
                PlanningMMMUploadedCSVAdapterStatus.BLOCKED_MATERIALIZATION_NOT_READY,
                issues + [PlanningMMMUploadedCSVAdapterIssueCode.MATERIALIZATION_NOT_READY],
                warnings + [f"Missing inspection for source_id={dataset.source_id}"],
                lineage,
            )
        role, role_source, role_issues = _resolve_role(dataset, request)
        issues.extend(role_issues)
        if role == PlanningMMMUploadedCSVRole.UNKNOWN:
            return _blocked(
                request.request_id,
                PlanningMMMUploadedCSVAdapterStatus.BLOCKED_AMBIGUOUS_ROLE,
                issues + [PlanningMMMUploadedCSVAdapterIssueCode.AMBIGUOUS_ROLE],
                warnings,
                lineage,
            )
        role_assignments.append((dataset, inspection, role, role_source))

    role_counts: dict[PlanningMMMUploadedCSVRole, int] = {}
    for _, _, role, _ in role_assignments:
        role_counts[role] = role_counts.get(role, 0) + 1

    for role in _REQUIRED_ROLES | _OPTIONAL_ROLES:
        if role_counts.get(role, 0) > 1:
            return _blocked(
                request.request_id,
                PlanningMMMUploadedCSVAdapterStatus.BLOCKED_DUPLICATE_ROLE,
                issues + [PlanningMMMUploadedCSVAdapterIssueCode.DUPLICATE_ROLE],
                warnings + [f"Duplicate Planning/MMM role: {role}"],
                lineage,
            )

    present_roles = set(role_counts)
    missing_required = _REQUIRED_ROLES - present_roles
    if missing_required:
        return _blocked(
            request.request_id,
            PlanningMMMUploadedCSVAdapterStatus.BLOCKED_MISSING_REQUIRED_ROLE,
            issues + [PlanningMMMUploadedCSVAdapterIssueCode.MISSING_REQUIRED_ROLE],
            warnings + [
                "Missing required Planning/MMM roles: "
                + ", ".join(sorted(str(role) for role in missing_required))
            ],
            lineage,
        )

    for optional_role in _OPTIONAL_ROLES:
        if optional_role not in present_roles:
            warnings.append(f"Optional Planning/MMM role not provided: {optional_role}")
            issues.append(_OPTIONAL_MISSING_ISSUE[optional_role])

    role_mappings: list[PlanningMMMUploadedCSVRoleMapping] = []
    data_source_refs: list[DataSourceRef] = []

    for dataset, inspection, role, role_source in role_assignments:
        required_columns = list(request.required_columns_by_role.get(str(role), []))
        missing_columns = [
            column
            for column in required_columns
            if column not in inspection.normalized_columns
        ]
        if missing_columns:
            return _blocked(
                request.request_id,
                PlanningMMMUploadedCSVAdapterStatus.BLOCKED_MISSING_REQUIRED_COLUMNS,
                issues + [PlanningMMMUploadedCSVAdapterIssueCode.MISSING_REQUIRED_COLUMNS],
                warnings + [f"Missing required columns for {role}: {', '.join(missing_columns)}"],
                lineage,
            )

        try:
            source_ref = _build_planning_data_source_ref(dataset, inspection, role, role_source)
        except ValueError:
            return _blocked(
                request.request_id,
                PlanningMMMUploadedCSVAdapterStatus.BLOCKED_DATA_SOURCE_REF_BUILD_FAILED,
                issues + [PlanningMMMUploadedCSVAdapterIssueCode.DATA_SOURCE_REF_BUILD_FAILED],
                warnings,
                lineage,
            )

        mapping = PlanningMMMUploadedCSVRoleMapping(
            source_id=dataset.source_id,
            dataset_id=dataset.dataset_id,
            role=role,
            role_source=role_source,
            required_columns=required_columns,
            available_columns=list(inspection.columns),
            normalized_columns=list(inspection.normalized_columns),
            missing_columns=missing_columns,
            data_source_ref=source_ref,
            lineage={
                **dataset.lineage,
                **inspection.lineage,
                "planning_mmm_role": str(role),
                "role_source": str(role_source),
            },
            warnings=list(inspection.warnings),
            issues=[PlanningMMMUploadedCSVAdapterIssueCode.DATA_SOURCE_REF_CREATED],
        )
        role_mappings.append(mapping)
        data_source_refs.append(source_ref)
        issues.append(PlanningMMMUploadedCSVAdapterIssueCode.DATA_SOURCE_REF_CREATED)

    issues.extend(
        [
            PlanningMMMUploadedCSVAdapterIssueCode.INTAKE_MANIFEST_COMPATIBLE,
            PlanningMMMUploadedCSVAdapterIssueCode.MMM_CONFIG_DRAFT_COMPATIBLE,
            PlanningMMMUploadedCSVAdapterIssueCode.MODEL_READINESS_COMPATIBLE,
        ]
    )

    availability = _build_availability(role_mappings, data_source_refs, lineage)
    status = PlanningMMMUploadedCSVAdapterStatus.ADAPTED
    if warnings:
        status = PlanningMMMUploadedCSVAdapterStatus.ADAPTED_WITH_WARNINGS

    return PlanningMMMUploadedCSVAdapterResult(
        request_id=request.request_id,
        status=status,
        availability=availability,
        role_mappings=role_mappings,
        data_source_refs=data_source_refs,
        issues=_dedupe_issues(issues),
        warnings=list(dict.fromkeys(warnings)),
        lineage=lineage,
    )


def build_planning_mmm_data_source_refs_from_uploaded_csv_adapter_result(
    result: PlanningMMMUploadedCSVAdapterResult,
) -> list[DataSourceRef]:
    """Return DataSourceRef objects from a Planning/MMM uploaded CSV adapter result."""
    if result.data_source_refs:
        return list(result.data_source_refs)
    return [
        mapping.data_source_ref
        for mapping in result.role_mappings
        if mapping.data_source_ref is not None
    ]


def build_planning_mmm_input_availability_from_uploaded_csv_adapter_result(
    result: PlanningMMMUploadedCSVAdapterResult,
) -> PlanningMMMUploadedCSVInputAvailability:
    """Return Planning/MMM input availability from adapter output."""
    if result.availability is not None:
        return result.availability
    return PlanningMMMUploadedCSVInputAvailability(
        lineage={
            **result.lineage,
            "adapter_status": str(result.status),
        },
    )


def build_intake_manifest_compatibility_from_uploaded_csv_adapter_result(
    result: PlanningMMMUploadedCSVAdapterResult,
) -> dict[str, str | list[str]]:
    """Metadata-only MMMIntakeManifest field compatibility (full manifest construction deferred)."""
    availability = result.availability
    if availability is None:
        return {
            "compatibility_status": "deferred",
            "reason": "adapter_not_ready",
        }
    return {
        "compatibility_status": "metadata_only",
        "outcome_source_ref_id": availability.historical_outcome_source_id or "",
        "media_source_ref_ids": [
            ref.source_id
            for ref in availability.data_source_refs
            if ref.asset_type == DataAssetType.MEDIA_SPEND_DATA
        ],
        "mapping_source_ref_ids": [
            ref.source_id
            for ref in availability.data_source_refs
            if ref.asset_type == DataAssetType.CHANNEL_MAPPING
        ],
        "calibration_signal_source_ref_ids": [
            ref.source_id
            for ref in availability.data_source_refs
            if ref.asset_type == DataAssetType.CALIBRATION_SIGNAL_DATA
        ],
        "deferred_manifest_fields": [
            "manifest_id",
            "session_id",
            "recommendation_id",
            "plan_id",
            "business_question",
            "created_at",
        ],
    }


def build_mmm_config_draft_compatibility_from_uploaded_csv_adapter_result(
    result: PlanningMMMUploadedCSVAdapterResult,
) -> dict[str, str | list[str] | None]:
    """Metadata-only MMMConfigDraft field hints (full draft construction deferred)."""
    spend_mapping = _mapping_for_role(result, PlanningMMMUploadedCSVRole.HISTORICAL_SPEND)
    outcome_mapping = _mapping_for_role(result, PlanningMMMUploadedCSVRole.HISTORICAL_OUTCOME)
    spend_columns = spend_mapping.normalized_columns if spend_mapping else []
    outcome_columns = outcome_mapping.normalized_columns if outcome_mapping else []
    return {
        "compatibility_status": "metadata_only",
        "deferred_draft_fields": ["metadata"],
        "suggested_spend_field": _first_column(
            spend_columns, ("spend", "media_spend", "amount")
        ),
        "suggested_outcome_field": _first_column(
            outcome_columns, ("revenue", "conversions", "sales", "kpi", "outcome")
        ),
        "suggested_date_field": _first_column(
            spend_columns + outcome_columns, ("date", "week", "period")
        ),
        "suggested_channel_field": _first_column(
            spend_columns, ("channel", "media_channel")
        ),
    }


def build_model_readiness_compatibility_from_uploaded_csv_adapter_result(
    result: PlanningMMMUploadedCSVAdapterResult,
) -> dict[str, str | bool]:
    """Metadata-only model readiness indicators (no model fitting)."""
    availability = result.availability
    if availability is None:
        return {
            "compatibility_status": "deferred",
            "model_readiness_evaluated": False,
        }
    return {
        "compatibility_status": "metadata_only",
        "model_readiness_evaluated": False,
        "has_historical_spend": availability.has_historical_spend,
        "has_historical_outcome": availability.has_historical_outcome,
        "has_channel_taxonomy": availability.has_channel_taxonomy,
        "has_calibration_signals": availability.has_calibration_signals,
        "adapter_status": str(result.status),
    }


def _resolve_role(
    dataset: MaterializedTabularDataset,
    request: PlanningMMMUploadedCSVAdapterRequest,
) -> tuple[
    PlanningMMMUploadedCSVRole,
    PlanningMMMUploadedCSVRoleSource,
    list[PlanningMMMUploadedCSVAdapterIssueCode],
]:
    issues: list[PlanningMMMUploadedCSVAdapterIssueCode] = []
    if dataset.source_id in request.explicit_role_by_source_id:
        issues.append(PlanningMMMUploadedCSVAdapterIssueCode.ROLE_EXPLICITLY_PROVIDED)
        return (
            request.explicit_role_by_source_id[dataset.source_id],
            PlanningMMMUploadedCSVRoleSource.EXPLICIT,
            issues,
        )

    hint = (dataset.declared_role_hint or "").strip().lower()
    if hint and hint in _ROLE_ALIASES:
        issues.append(PlanningMMMUploadedCSVAdapterIssueCode.ROLE_HINT_USED)
        return _ROLE_ALIASES[hint], PlanningMMMUploadedCSVRoleSource.DECLARED_ROLE_HINT, issues

    return PlanningMMMUploadedCSVRole.UNKNOWN, PlanningMMMUploadedCSVRoleSource.UNKNOWN, issues


def _build_planning_data_source_ref(
    dataset: MaterializedTabularDataset,
    inspection: UploadedCSVInspection,
    role: PlanningMMMUploadedCSVRole,
    role_source: PlanningMMMUploadedCSVRoleSource,
) -> DataSourceRef:
    uploaded_path = inspection.lineage.get("uploaded_path", "").strip()
    if not uploaded_path:
        msg = "uploaded_path missing from inspection lineage"
        raise ValueError(msg)

    source = UploadedCSVSource(
        source_id=dataset.source_id,
        source_type=dataset.source_type,
        path=uploaded_path,
        original_filename=inspection.original_filename,
        declared_role_hint=dataset.declared_role_hint,
        lineage={
            **dataset.lineage,
            **inspection.lineage,
            "planning_mmm_role": str(role),
            "role_source": str(role_source),
        },
    )
    ref = build_data_source_ref_from_uploaded_csv_inspection(
        source,
        inspection,
        asset_type=_ROLE_TO_ASSET_TYPE[role],
        created_at=datetime.now(tz=UTC),
    )
    return ref.model_copy(
        update={
            "declared_scope": {
                **ref.declared_scope,
                "planning_mmm_role": str(role),
                "role_source": str(role_source),
                "declared_role_hint": dataset.declared_role_hint or "",
                "normalized_columns": ",".join(inspection.normalized_columns),
                "planning_mmm_uploaded_csv_adapter": "true",
            },
        }
    )


def _build_availability(
    role_mappings: list[PlanningMMMUploadedCSVRoleMapping],
    data_source_refs: list[DataSourceRef],
    lineage: dict[str, str],
) -> PlanningMMMUploadedCSVInputAvailability:
    by_role = {mapping.role: mapping for mapping in role_mappings}
    spend = by_role.get(PlanningMMMUploadedCSVRole.HISTORICAL_SPEND)
    outcome = by_role.get(PlanningMMMUploadedCSVRole.HISTORICAL_OUTCOME)
    taxonomy = by_role.get(PlanningMMMUploadedCSVRole.CHANNEL_TAXONOMY)
    budget = by_role.get(PlanningMMMUploadedCSVRole.BUDGET_CONSTRAINTS)
    calibration = by_role.get(PlanningMMMUploadedCSVRole.CALIBRATION_SIGNALS)
    model_config = by_role.get(PlanningMMMUploadedCSVRole.MODEL_CONFIG)
    return PlanningMMMUploadedCSVInputAvailability(
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
        lineage={
            **lineage,
            "role_mapping_count": str(len(role_mappings)),
        },
    )


def _mapping_for_role(
    result: PlanningMMMUploadedCSVAdapterResult,
    role: PlanningMMMUploadedCSVRole,
) -> PlanningMMMUploadedCSVRoleMapping | None:
    return next((mapping for mapping in result.role_mappings if mapping.role == role), None)


def _first_column(columns: list[str], candidates: tuple[str, ...]) -> str | None:
    normalized = {column.lower(): column for column in columns}
    for candidate in candidates:
        if candidate in normalized:
            return normalized[candidate]
    return None


def _blocked(
    request_id: str,
    status: PlanningMMMUploadedCSVAdapterStatus,
    issues: list[PlanningMMMUploadedCSVAdapterIssueCode],
    warnings: list[str],
    lineage: dict[str, str],
) -> PlanningMMMUploadedCSVAdapterResult:
    return PlanningMMMUploadedCSVAdapterResult(
        request_id=request_id,
        status=status,
        issues=_dedupe_issues(issues),
        warnings=list(dict.fromkeys(warnings)),
        lineage=lineage,
    )


def _dedupe_issues(
    issues: list[PlanningMMMUploadedCSVAdapterIssueCode],
) -> list[PlanningMMMUploadedCSVAdapterIssueCode]:
    seen: set[PlanningMMMUploadedCSVAdapterIssueCode] = set()
    ordered: list[PlanningMMMUploadedCSVAdapterIssueCode] = []
    for issue in issues:
        if issue not in seen:
            seen.add(issue)
            ordered.append(issue)
    return ordered
