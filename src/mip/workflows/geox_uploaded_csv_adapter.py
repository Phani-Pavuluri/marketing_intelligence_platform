"""GeoX readout uploaded CSV adapter workflow.

Maps shared MaterializedTabularDataset outputs to GeoX readout semantics.
Does not re-read CSVs or invoke GeoX package runtime.
"""

from __future__ import annotations

from mip.contracts.geox_panel_exp_integration import GeoXMaterializedInputAvailability
from mip.contracts.geox_readout_input_resolution import (
    DatasetReference,
    DatasetSemanticType,
    DatasetSourceType,
    MappingConfirmationStatus,
)
from mip.contracts.geox_uploaded_csv_adapter import (
    GeoXUploadedCSVAdapterAvailability,
    GeoXUploadedCSVAdapterIssueCode,
    GeoXUploadedCSVAdapterRequest,
    GeoXUploadedCSVAdapterResult,
    GeoXUploadedCSVAdapterStatus,
    GeoXUploadedCSVRole,
    GeoXUploadedCSVRoleMapping,
    GeoXUploadedCSVRoleSource,
)
from mip.contracts.uploaded_csv_materialization import (
    MaterializedTabularDataset,
    UploadedCSVInspection,
    UploadedCSVMaterializationStatus,
)

_READY_MATERIALIZATION_STATUSES = {
    UploadedCSVMaterializationStatus.MATERIALIZED,
    UploadedCSVMaterializationStatus.MATERIALIZED_WITH_WARNINGS,
}
_REQUIRED_ROLES = {
    GeoXUploadedCSVRole.KPI_PANEL,
    GeoXUploadedCSVRole.SPEND_PANEL,
    GeoXUploadedCSVRole.ASSIGNMENT_TABLE,
}
_ROLE_ALIASES: dict[str, GeoXUploadedCSVRole] = {
    "kpi_panel": GeoXUploadedCSVRole.KPI_PANEL,
    "kpi": GeoXUploadedCSVRole.KPI_PANEL,
    "outcome_panel": GeoXUploadedCSVRole.KPI_PANEL,
    "spend_panel": GeoXUploadedCSVRole.SPEND_PANEL,
    "spend": GeoXUploadedCSVRole.SPEND_PANEL,
    "assignment_table": GeoXUploadedCSVRole.ASSIGNMENT_TABLE,
    "assignment": GeoXUploadedCSVRole.ASSIGNMENT_TABLE,
    "design": GeoXUploadedCSVRole.ASSIGNMENT_TABLE,
    "experiment_metadata": GeoXUploadedCSVRole.EXPERIMENT_METADATA,
    "metadata": GeoXUploadedCSVRole.EXPERIMENT_METADATA,
}
_ROLE_TO_SEMANTIC: dict[GeoXUploadedCSVRole, DatasetSemanticType] = {
    GeoXUploadedCSVRole.KPI_PANEL: DatasetSemanticType.KPI_PANEL,
    GeoXUploadedCSVRole.SPEND_PANEL: DatasetSemanticType.SPEND_PANEL,
    GeoXUploadedCSVRole.ASSIGNMENT_TABLE: DatasetSemanticType.ASSIGNMENT_TABLE,
    GeoXUploadedCSVRole.EXPERIMENT_METADATA: DatasetSemanticType.EXPERIMENT_METADATA,
    GeoXUploadedCSVRole.UNKNOWN: DatasetSemanticType.UNKNOWN_DATASET,
}


def adapt_uploaded_csvs_for_geox_readout(
    request: GeoXUploadedCSVAdapterRequest,
) -> GeoXUploadedCSVAdapterResult:
    """Adapt shared uploaded CSV materialization outputs for GeoX readout input."""
    lineage = {
        **request.lineage,
        "adapter_stage": "geox_uploaded_csv_adapter",
    }
    warnings = list(dict.fromkeys(request.warnings))
    issues: list[GeoXUploadedCSVAdapterIssueCode] = [
        GeoXUploadedCSVAdapterIssueCode.LINEAGE_PRESERVED,
    ]

    if request.materialization_result is None:
        return _blocked(
            request.request_id,
            GeoXUploadedCSVAdapterStatus.BLOCKED_MISSING_MATERIALIZATION_RESULT,
            issues + [GeoXUploadedCSVAdapterIssueCode.MISSING_MATERIALIZATION_RESULT],
            warnings,
            lineage,
        )

    materialization = request.materialization_result
    warnings.extend(materialization.warnings)
    lineage.update(materialization.lineage)

    if materialization.status not in _READY_MATERIALIZATION_STATUSES:
        return _blocked(
            request.request_id,
            GeoXUploadedCSVAdapterStatus.BLOCKED_MATERIALIZATION_NOT_READY,
            issues + [GeoXUploadedCSVAdapterIssueCode.MATERIALIZATION_NOT_READY],
            warnings,
            lineage,
        )

    inspection_by_source = {
        inspection.source_id: inspection for inspection in materialization.inspections
    }
    RoleAssignment = tuple[
        MaterializedTabularDataset,
        UploadedCSVInspection,
        GeoXUploadedCSVRole,
        GeoXUploadedCSVRoleSource,
    ]
    role_assignments: list[RoleAssignment] = []

    for dataset in materialization.datasets:
        inspection = inspection_by_source.get(dataset.source_id)
        if inspection is None:
            return _blocked(
                request.request_id,
                GeoXUploadedCSVAdapterStatus.BLOCKED_MATERIALIZATION_NOT_READY,
                issues + [GeoXUploadedCSVAdapterIssueCode.MATERIALIZATION_NOT_READY],
                warnings + [f"Missing inspection for source_id={dataset.source_id}"],
                lineage,
            )
        role, role_source, role_issues = _resolve_role(dataset, request)
        issues.extend(role_issues)
        if role == GeoXUploadedCSVRole.UNKNOWN:
            return _blocked(
                request.request_id,
                GeoXUploadedCSVAdapterStatus.BLOCKED_AMBIGUOUS_ROLE,
                issues + [GeoXUploadedCSVAdapterIssueCode.AMBIGUOUS_ROLE],
                warnings,
                lineage,
            )
        role_assignments.append((dataset, inspection, role, role_source))

    role_counts: dict[GeoXUploadedCSVRole, int] = {}
    for _, _, role, _ in role_assignments:
        role_counts[role] = role_counts.get(role, 0) + 1

    for role in _REQUIRED_ROLES:
        if role_counts.get(role, 0) > 1:
            return _blocked(
                request.request_id,
                GeoXUploadedCSVAdapterStatus.BLOCKED_DUPLICATE_ROLE,
                issues + [GeoXUploadedCSVAdapterIssueCode.DUPLICATE_ROLE],
                warnings + [f"Duplicate GeoX role: {role}"],
                lineage,
            )

    if GeoXUploadedCSVRole.EXPERIMENT_METADATA in role_counts and role_counts[
        GeoXUploadedCSVRole.EXPERIMENT_METADATA
    ] > 1:
        return _blocked(
            request.request_id,
            GeoXUploadedCSVAdapterStatus.BLOCKED_DUPLICATE_ROLE,
            issues + [GeoXUploadedCSVAdapterIssueCode.DUPLICATE_ROLE],
            warnings + ["Duplicate optional experiment metadata role"],
            lineage,
        )

    present_roles = set(role_counts)
    missing_required = _REQUIRED_ROLES - present_roles
    if missing_required:
        return _blocked(
            request.request_id,
            GeoXUploadedCSVAdapterStatus.BLOCKED_MISSING_REQUIRED_ROLE,
            issues + [GeoXUploadedCSVAdapterIssueCode.MISSING_REQUIRED_ROLE],
            warnings + [
                "Missing required GeoX roles: "
                + ", ".join(sorted(str(role) for role in missing_required))
            ],
            lineage,
        )

    if GeoXUploadedCSVRole.EXPERIMENT_METADATA not in present_roles:
        warnings.append("Optional experiment metadata CSV not provided.")
        issues.append(GeoXUploadedCSVAdapterIssueCode.OPTIONAL_METADATA_MISSING)

    role_mappings: list[GeoXUploadedCSVRoleMapping] = []
    dataset_references: list[DatasetReference] = []

    for dataset, inspection, role, role_source in role_assignments:
        required_columns = list(
            request.required_columns_by_role.get(str(role), [])
        )
        missing_columns = [
            column
            for column in required_columns
            if column not in inspection.normalized_columns
        ]
        if missing_columns:
            return _blocked(
                request.request_id,
                GeoXUploadedCSVAdapterStatus.BLOCKED_MISSING_REQUIRED_COLUMNS,
                issues + [GeoXUploadedCSVAdapterIssueCode.MISSING_REQUIRED_COLUMNS],
                warnings + [f"Missing required columns for {role}: {', '.join(missing_columns)}"],
                lineage,
            )

        try:
            dataset_ref = _build_geox_dataset_reference(dataset, inspection, role, role_source)
        except ValueError:
            return _blocked(
                request.request_id,
                GeoXUploadedCSVAdapterStatus.BLOCKED_DATASET_REFERENCE_BUILD_FAILED,
                issues + [GeoXUploadedCSVAdapterIssueCode.DATASET_REFERENCE_BUILD_FAILED],
                warnings,
                lineage,
            )

        mapping = GeoXUploadedCSVRoleMapping(
            source_id=dataset.source_id,
            dataset_id=dataset.dataset_id,
            role=role,
            role_source=role_source,
            required_columns=required_columns,
            available_columns=list(inspection.columns),
            normalized_columns=list(inspection.normalized_columns),
            missing_columns=missing_columns,
            dataset_reference=dataset_ref,
            lineage={
                **dataset.lineage,
                **inspection.lineage,
                "geox_role": str(role),
                "role_source": str(role_source),
            },
            warnings=list(inspection.warnings),
            issues=[GeoXUploadedCSVAdapterIssueCode.DATASET_REFERENCE_CREATED],
        )
        role_mappings.append(mapping)
        dataset_references.append(dataset_ref)
        issues.append(GeoXUploadedCSVAdapterIssueCode.DATASET_REFERENCE_CREATED)

    issues.extend(
        [
            GeoXUploadedCSVAdapterIssueCode.SOURCE_INSPECTION_COMPATIBLE,
            GeoXUploadedCSVAdapterIssueCode.INPUT_RESOLUTION_COMPATIBLE,
        ]
    )

    availability = _build_availability(role_mappings, dataset_references, lineage)
    status = GeoXUploadedCSVAdapterStatus.ADAPTED
    if warnings:
        status = GeoXUploadedCSVAdapterStatus.ADAPTED_WITH_WARNINGS

    return GeoXUploadedCSVAdapterResult(
        request_id=request.request_id,
        status=status,
        availability=availability,
        role_mappings=role_mappings,
        dataset_references=dataset_references,
        issues=_dedupe_issues(issues),
        warnings=list(dict.fromkeys(warnings)),
        lineage=lineage,
    )


def build_geox_dataset_references_from_uploaded_csv_adapter_result(
    result: GeoXUploadedCSVAdapterResult,
) -> list[DatasetReference]:
    """Return DatasetReference objects from a GeoX uploaded CSV adapter result."""
    if result.dataset_references:
        return list(result.dataset_references)
    return [
        mapping.dataset_reference
        for mapping in result.role_mappings
        if mapping.dataset_reference is not None
    ]


def build_geox_materialized_input_availability_from_uploaded_csv_adapter_result(
    result: GeoXUploadedCSVAdapterResult,
) -> GeoXMaterializedInputAvailability:
    """Map GeoX uploaded CSV adapter output to Stage 3A availability indicators."""
    availability = result.availability
    if availability is None:
        return GeoXMaterializedInputAvailability(
            lineage={
                **result.lineage,
                "adapter_status": str(result.status),
            },
            warnings=list(result.warnings),
        )

    spend_path = None
    assignment_path = None
    for mapping in availability.role_mappings:
        if mapping.dataset_reference is None:
            continue
        path = mapping.dataset_reference.source_uri_or_handle
        if mapping.role == GeoXUploadedCSVRole.SPEND_PANEL:
            spend_path = path
        elif mapping.role == GeoXUploadedCSVRole.ASSIGNMENT_TABLE:
            assignment_path = path

    return GeoXMaterializedInputAvailability(
        has_materialized_spend_df=availability.has_spend_panel,
        has_materialized_assignment_df=availability.has_assignment_table,
        has_assignment_mapping=availability.has_assignment_table,
        materialized_spend_ref_optional=spend_path,
        materialized_assignment_ref_optional=assignment_path,
        lineage={
            **result.lineage,
            **availability.lineage,
            "adapter_status": str(result.status),
            "has_kpi_panel": str(availability.has_kpi_panel).lower(),
            "has_experiment_metadata": str(availability.has_experiment_metadata).lower(),
        },
        warnings=list(result.warnings),
    )


def _resolve_role(
    dataset: MaterializedTabularDataset,
    request: GeoXUploadedCSVAdapterRequest,
) -> tuple[GeoXUploadedCSVRole, GeoXUploadedCSVRoleSource, list[GeoXUploadedCSVAdapterIssueCode]]:
    issues: list[GeoXUploadedCSVAdapterIssueCode] = []
    if dataset.source_id in request.explicit_role_by_source_id:
        issues.append(GeoXUploadedCSVAdapterIssueCode.ROLE_EXPLICITLY_PROVIDED)
        return (
            request.explicit_role_by_source_id[dataset.source_id],
            GeoXUploadedCSVRoleSource.EXPLICIT,
            issues,
        )

    hint = (dataset.declared_role_hint or "").strip().lower()
    if hint and hint in _ROLE_ALIASES:
        issues.append(GeoXUploadedCSVAdapterIssueCode.ROLE_HINT_USED)
        return _ROLE_ALIASES[hint], GeoXUploadedCSVRoleSource.DECLARED_ROLE_HINT, issues

    return GeoXUploadedCSVRole.UNKNOWN, GeoXUploadedCSVRoleSource.UNKNOWN, issues


def _build_geox_dataset_reference(
    dataset: MaterializedTabularDataset,
    inspection: UploadedCSVInspection,
    role: GeoXUploadedCSVRole,
    role_source: GeoXUploadedCSVRoleSource,
) -> DatasetReference:
    uploaded_path = inspection.lineage.get("uploaded_path", "").strip()
    if not uploaded_path:
        msg = "uploaded_path missing from inspection lineage"
        raise ValueError(msg)

    return DatasetReference(
        dataset_ref_id=dataset.source_id,
        source_type=DatasetSourceType.UPLOADED_CSV,
        semantic_type=_ROLE_TO_SEMANTIC[role],
        source_uri_or_handle=uploaded_path,
        file_name_or_table_name=inspection.original_filename,
        declared_or_detected_columns=list(inspection.normalized_columns),
        classification_confidence=1.0 if role != GeoXUploadedCSVRole.UNKNOWN else 0.0,
        user_confirmation_status=(
            MappingConfirmationStatus.USER_CONFIRMED
            if role_source == GeoXUploadedCSVRoleSource.EXPLICIT
            else MappingConfirmationStatus.NOT_REQUIRED
        ),
        lineage={
            **dataset.lineage,
            **inspection.lineage,
            "geox_role": str(role),
            "role_source": str(role_source),
            "declared_role_hint": dataset.declared_role_hint or "",
            "geox_uploaded_csv_adapter": "true",
        },
        warnings=list(inspection.warnings),
    )


def _build_availability(
    role_mappings: list[GeoXUploadedCSVRoleMapping],
    dataset_references: list[DatasetReference],
    lineage: dict[str, str],
) -> GeoXUploadedCSVAdapterAvailability:
    by_role = {mapping.role: mapping for mapping in role_mappings}
    kpi = by_role.get(GeoXUploadedCSVRole.KPI_PANEL)
    spend = by_role.get(GeoXUploadedCSVRole.SPEND_PANEL)
    assignment = by_role.get(GeoXUploadedCSVRole.ASSIGNMENT_TABLE)
    metadata = by_role.get(GeoXUploadedCSVRole.EXPERIMENT_METADATA)
    return GeoXUploadedCSVAdapterAvailability(
        has_kpi_panel=kpi is not None,
        has_spend_panel=spend is not None,
        has_assignment_table=assignment is not None,
        has_experiment_metadata=metadata is not None,
        kpi_panel_source_id=kpi.source_id if kpi else None,
        spend_panel_source_id=spend.source_id if spend else None,
        assignment_table_source_id=assignment.source_id if assignment else None,
        metadata_source_id=metadata.source_id if metadata else None,
        dataset_references=list(dataset_references),
        role_mappings=list(role_mappings),
        lineage={
            **lineage,
            "role_mapping_count": str(len(role_mappings)),
        },
    )


def _blocked(
    request_id: str,
    status: GeoXUploadedCSVAdapterStatus,
    issues: list[GeoXUploadedCSVAdapterIssueCode],
    warnings: list[str],
    lineage: dict[str, str],
) -> GeoXUploadedCSVAdapterResult:
    return GeoXUploadedCSVAdapterResult(
        request_id=request_id,
        status=status,
        issues=_dedupe_issues(issues),
        warnings=list(dict.fromkeys(warnings)),
        lineage=lineage,
    )


def _dedupe_issues(
    issues: list[GeoXUploadedCSVAdapterIssueCode],
) -> list[GeoXUploadedCSVAdapterIssueCode]:
    seen: set[GeoXUploadedCSVAdapterIssueCode] = set()
    ordered: list[GeoXUploadedCSVAdapterIssueCode] = []
    for issue in issues:
        if issue not in seen:
            seen.add(issue)
            ordered.append(issue)
    return ordered
