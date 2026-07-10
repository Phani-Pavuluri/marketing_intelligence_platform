"""GeoX tabular source adapter compatibility workflow.

Maps generic TabularSourceInspectionResult outputs to GeoX readout semantics
without re-reading CSVs, calling connectors, or invoking panel_exp runtime.
"""

from __future__ import annotations

from mip.contracts.geox_readout_input_resolution import (
    DatasetReference,
    DatasetSemanticType,
    DatasetSourceType,
    MappingConfirmationStatus,
)
from mip.contracts.geox_tabular_source_adapter import (
    GeoXTabularSourceAdapterIssueCode,
    GeoXTabularSourceAdapterRequest,
    GeoXTabularSourceAdapterResult,
    GeoXTabularSourceAdapterStatus,
    GeoXTabularSourceInputAvailability,
    GeoXTabularSourceRoleMapping,
    GeoXTabularSourceRoleSource,
)
from mip.contracts.geox_uploaded_csv_adapter import (
    GeoXUploadedCSVAdapterAvailability,
    GeoXUploadedCSVAdapterIssueCode,
    GeoXUploadedCSVAdapterResult,
    GeoXUploadedCSVAdapterStatus,
    GeoXUploadedCSVRole,
    GeoXUploadedCSVRoleMapping,
    GeoXUploadedCSVRoleSource,
)
from mip.contracts.intake_sources import DataSourceRef
from mip.contracts.tabular_source_reference import (
    TabularSourceInspection,
    TabularSourceInspectionStatus,
    TabularSourceReference,
    TabularSourceType,
)

_READY_TABULAR_STATUSES = {
    TabularSourceInspectionStatus.INSPECTED,
    TabularSourceInspectionStatus.INSPECTED_WITH_WARNINGS,
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
    "outcome": GeoXUploadedCSVRole.KPI_PANEL,
    "outcomes": GeoXUploadedCSVRole.KPI_PANEL,
    "response": GeoXUploadedCSVRole.KPI_PANEL,
    "metric": GeoXUploadedCSVRole.KPI_PANEL,
    "sales": GeoXUploadedCSVRole.KPI_PANEL,
    "conversions": GeoXUploadedCSVRole.KPI_PANEL,
    "revenue": GeoXUploadedCSVRole.KPI_PANEL,
    "spend_panel": GeoXUploadedCSVRole.SPEND_PANEL,
    "spend": GeoXUploadedCSVRole.SPEND_PANEL,
    "media_spend": GeoXUploadedCSVRole.SPEND_PANEL,
    "marketing_spend": GeoXUploadedCSVRole.SPEND_PANEL,
    "cost": GeoXUploadedCSVRole.SPEND_PANEL,
    "investment": GeoXUploadedCSVRole.SPEND_PANEL,
    "assignment_table": GeoXUploadedCSVRole.ASSIGNMENT_TABLE,
    "assignment": GeoXUploadedCSVRole.ASSIGNMENT_TABLE,
    "design": GeoXUploadedCSVRole.ASSIGNMENT_TABLE,
    "experiment_design": GeoXUploadedCSVRole.ASSIGNMENT_TABLE,
    "design_matrix": GeoXUploadedCSVRole.ASSIGNMENT_TABLE,
    "geo_assignment": GeoXUploadedCSVRole.ASSIGNMENT_TABLE,
    "matched_markets_design": GeoXUploadedCSVRole.ASSIGNMENT_TABLE,
    "experiment_metadata": GeoXUploadedCSVRole.EXPERIMENT_METADATA,
    "metadata": GeoXUploadedCSVRole.EXPERIMENT_METADATA,
    "geo_metadata": GeoXUploadedCSVRole.EXPERIMENT_METADATA,
    "geo": GeoXUploadedCSVRole.EXPERIMENT_METADATA,
    "market_metadata": GeoXUploadedCSVRole.EXPERIMENT_METADATA,
    "geo_lookup": GeoXUploadedCSVRole.EXPERIMENT_METADATA,
    "dma_metadata": GeoXUploadedCSVRole.EXPERIMENT_METADATA,
}
_ROLE_TO_SEMANTIC: dict[GeoXUploadedCSVRole, DatasetSemanticType] = {
    GeoXUploadedCSVRole.KPI_PANEL: DatasetSemanticType.KPI_PANEL,
    GeoXUploadedCSVRole.SPEND_PANEL: DatasetSemanticType.SPEND_PANEL,
    GeoXUploadedCSVRole.ASSIGNMENT_TABLE: DatasetSemanticType.ASSIGNMENT_TABLE,
    GeoXUploadedCSVRole.EXPERIMENT_METADATA: DatasetSemanticType.EXPERIMENT_METADATA,
    GeoXUploadedCSVRole.UNKNOWN: DatasetSemanticType.UNKNOWN_DATASET,
}
_TABULAR_TO_UPLOADED_STATUS: dict[
    GeoXTabularSourceAdapterStatus, GeoXUploadedCSVAdapterStatus
] = {
    GeoXTabularSourceAdapterStatus.ADAPTED: GeoXUploadedCSVAdapterStatus.ADAPTED,
    GeoXTabularSourceAdapterStatus.ADAPTED_WITH_WARNINGS: (
        GeoXUploadedCSVAdapterStatus.ADAPTED_WITH_WARNINGS
    ),
    GeoXTabularSourceAdapterStatus.BLOCKED_MISSING_TABULAR_SOURCE_RESULT: (
        GeoXUploadedCSVAdapterStatus.BLOCKED_MISSING_MATERIALIZATION_RESULT
    ),
    GeoXTabularSourceAdapterStatus.BLOCKED_TABULAR_SOURCE_NOT_READY: (
        GeoXUploadedCSVAdapterStatus.BLOCKED_MATERIALIZATION_NOT_READY
    ),
    GeoXTabularSourceAdapterStatus.BLOCKED_MISSING_REQUIRED_ROLE: (
        GeoXUploadedCSVAdapterStatus.BLOCKED_MISSING_REQUIRED_ROLE
    ),
    GeoXTabularSourceAdapterStatus.BLOCKED_DUPLICATE_ROLE: (
        GeoXUploadedCSVAdapterStatus.BLOCKED_DUPLICATE_ROLE
    ),
    GeoXTabularSourceAdapterStatus.BLOCKED_AMBIGUOUS_ROLE: (
        GeoXUploadedCSVAdapterStatus.BLOCKED_AMBIGUOUS_ROLE
    ),
    GeoXTabularSourceAdapterStatus.BLOCKED_MISSING_REQUIRED_COLUMNS: (
        GeoXUploadedCSVAdapterStatus.BLOCKED_MISSING_REQUIRED_COLUMNS
    ),
    GeoXTabularSourceAdapterStatus.BLOCKED_DATA_SOURCE_REF_UNAVAILABLE: (
        GeoXUploadedCSVAdapterStatus.BLOCKED_DATASET_REFERENCE_BUILD_FAILED
    ),
}


def adapt_tabular_sources_for_geox_readout(
    request: GeoXTabularSourceAdapterRequest,
) -> GeoXTabularSourceAdapterResult:
    """Adapt generic tabular source inspection outputs for GeoX readout."""
    lineage = {
        **request.lineage,
        "adapter_stage": "geox_tabular_source_adapter",
    }
    warnings = list(dict.fromkeys(request.warnings))
    issues: list[GeoXTabularSourceAdapterIssueCode] = [
        GeoXTabularSourceAdapterIssueCode.TABULAR_SOURCE_LINEAGE_PRESERVED,
        GeoXTabularSourceAdapterIssueCode.NO_CONNECTOR_RUNTIME,
        GeoXTabularSourceAdapterIssueCode.NO_PANEL_EXP_RUNTIME_EXECUTION,
        GeoXTabularSourceAdapterIssueCode.NO_LIFT_COMPUTATION,
        GeoXTabularSourceAdapterIssueCode.NO_DELTA_MU_COMPUTATION,
        GeoXTabularSourceAdapterIssueCode.NO_SPEND_DELTA_COMPUTATION,
        GeoXTabularSourceAdapterIssueCode.NO_ROI_ROAS_COMPUTATION,
        GeoXTabularSourceAdapterIssueCode.NO_DECISION_SURFACE_EXECUTION,
        GeoXTabularSourceAdapterIssueCode.NO_RECOMMENDATION_GENERATED,
        GeoXTabularSourceAdapterIssueCode.NO_CLAIM_AUTHORIZATION,
    ]

    if request.tabular_source_result is None:
        return _blocked(
            request.request_id,
            GeoXTabularSourceAdapterStatus.BLOCKED_MISSING_TABULAR_SOURCE_RESULT,
            issues + [GeoXTabularSourceAdapterIssueCode.MISSING_TABULAR_SOURCE_RESULT],
            warnings,
            lineage,
        )

    tabular_result = request.tabular_source_result
    warnings.extend(tabular_result.warnings)
    lineage.update(tabular_result.lineage)

    if tabular_result.status not in _READY_TABULAR_STATUSES:
        return _blocked(
            request.request_id,
            GeoXTabularSourceAdapterStatus.BLOCKED_TABULAR_SOURCE_NOT_READY,
            issues + [GeoXTabularSourceAdapterIssueCode.TABULAR_SOURCE_NOT_READY],
            warnings,
            lineage,
        )

    RoleAssignment = tuple[
        TabularSourceInspection,
        GeoXUploadedCSVRole,
        GeoXTabularSourceRoleSource,
    ]
    role_assignments: list[RoleAssignment] = []

    for inspection in tabular_result.inspections:
        role, role_source, role_issues = _resolve_role(inspection, request)
        issues.extend(role_issues)
        if role == GeoXUploadedCSVRole.UNKNOWN:
            return _blocked(
                request.request_id,
                GeoXTabularSourceAdapterStatus.BLOCKED_AMBIGUOUS_ROLE,
                issues + [GeoXTabularSourceAdapterIssueCode.AMBIGUOUS_ROLE],
                warnings,
                lineage,
            )
        role_assignments.append((inspection, role, role_source))

    role_counts: dict[GeoXUploadedCSVRole, int] = {}
    for _, role, _ in role_assignments:
        role_counts[role] = role_counts.get(role, 0) + 1

    for role in _REQUIRED_ROLES:
        if role_counts.get(role, 0) > 1:
            return _blocked(
                request.request_id,
                GeoXTabularSourceAdapterStatus.BLOCKED_DUPLICATE_ROLE,
                issues + [GeoXTabularSourceAdapterIssueCode.DUPLICATE_ROLE],
                warnings + [f"Duplicate GeoX role: {role}"],
                lineage,
            )

    if GeoXUploadedCSVRole.EXPERIMENT_METADATA in role_counts and role_counts[
        GeoXUploadedCSVRole.EXPERIMENT_METADATA
    ] > 1:
        return _blocked(
            request.request_id,
            GeoXTabularSourceAdapterStatus.BLOCKED_DUPLICATE_ROLE,
            issues + [GeoXTabularSourceAdapterIssueCode.DUPLICATE_ROLE],
            warnings + ["Duplicate optional experiment metadata role"],
            lineage,
        )

    present_roles = set(role_counts)
    missing_required = _REQUIRED_ROLES - present_roles
    if missing_required:
        return _blocked(
            request.request_id,
            GeoXTabularSourceAdapterStatus.BLOCKED_MISSING_REQUIRED_ROLE,
            issues + [GeoXTabularSourceAdapterIssueCode.MISSING_REQUIRED_ROLE],
            warnings
            + [
                "Missing required GeoX roles: "
                + ", ".join(sorted(str(role) for role in missing_required))
            ],
            lineage,
        )

    if GeoXUploadedCSVRole.EXPERIMENT_METADATA not in present_roles:
        warnings.append("Optional experiment metadata source not provided.")
        issues.append(GeoXTabularSourceAdapterIssueCode.OPTIONAL_GEO_METADATA_MISSING)

    role_mappings: list[GeoXTabularSourceRoleMapping] = []
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
                GeoXTabularSourceAdapterStatus.BLOCKED_MISSING_REQUIRED_COLUMNS,
                issues + [GeoXTabularSourceAdapterIssueCode.MISSING_REQUIRED_COLUMNS],
                warnings
                + [f"Missing required columns for {role}: {', '.join(missing_columns)}"],
                lineage,
            )

        data_source_ref = reference.data_source_ref
        if data_source_ref is None:
            return _blocked(
                request.request_id,
                GeoXTabularSourceAdapterStatus.BLOCKED_DATA_SOURCE_REF_UNAVAILABLE,
                issues + [GeoXTabularSourceAdapterIssueCode.DATA_SOURCE_REF_UNAVAILABLE],
                warnings + [f"DataSourceRef unavailable for source_id={reference.source_id}"],
                lineage,
            )

        source_uri = _resolve_source_uri(reference, data_source_ref, inspection)
        dataset_id = (
            inspection.availability.materialized_dataset_id
            if inspection.availability and inspection.availability.materialized_dataset_id
            else f"tabular:{reference.source_id}"
        )
        mapping_issues = [
            GeoXTabularSourceAdapterIssueCode.TABULAR_SOURCE_SCHEMA_USED,
            GeoXTabularSourceAdapterIssueCode.TABULAR_SOURCE_REFERENCE_PRESERVED,
            GeoXTabularSourceAdapterIssueCode.DATA_SOURCE_REF_PRESERVED,
        ]
        mapping = GeoXTabularSourceRoleMapping(
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
                "source_uri": source_uri,
                "geox_role": str(role),
                "role_source": str(role_source),
                "declared_role_hint": reference.declared_role_hint or "",
            },
            warnings=list(inspection.warnings),
            issues=mapping_issues,
        )
        role_mappings.append(mapping)
        data_source_refs.append(data_source_ref)
        tabular_source_references.append(reference)
        issues.extend(mapping_issues)

    issues.append(
        GeoXTabularSourceAdapterIssueCode.UPLOADED_CSV_COMPATIBILITY_PATH_SUPPORTED
    )

    availability = _build_availability(
        role_mappings,
        data_source_refs,
        tabular_source_references,
        lineage,
    )
    status = GeoXTabularSourceAdapterStatus.ADAPTED
    if warnings:
        status = GeoXTabularSourceAdapterStatus.ADAPTED_WITH_WARNINGS

    return GeoXTabularSourceAdapterResult(
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


def build_uploaded_csv_geox_adapter_result_from_tabular_source_adapter_result(
    result: GeoXTabularSourceAdapterResult,
) -> GeoXUploadedCSVAdapterResult:
    """Convert tabular source adapter output into uploaded CSV GeoX adapter result shape."""
    uploaded_role_mappings: list[GeoXUploadedCSVRoleMapping] = []
    dataset_references: list[DatasetReference] = []

    for mapping in result.role_mappings:
        dataset_ref = _build_dataset_reference_from_tabular_mapping(mapping)
        uploaded_role_mappings.append(
            GeoXUploadedCSVRoleMapping(
                source_id=mapping.source_id,
                dataset_id=mapping.lineage.get("dataset_id", f"tabular:{mapping.source_id}"),
                role=mapping.role,
                role_source=_to_uploaded_role_source(mapping.role_source),
                required_columns=list(mapping.required_columns),
                available_columns=list(mapping.available_columns),
                normalized_columns=list(mapping.normalized_columns),
                missing_columns=list(mapping.missing_columns),
                dataset_reference=dataset_ref,
                lineage=dict(mapping.lineage),
                warnings=list(mapping.warnings),
                issues=[GeoXUploadedCSVAdapterIssueCode.DATASET_REFERENCE_CREATED],
            )
        )
        dataset_references.append(dataset_ref)

    uploaded_availability = _to_uploaded_availability(
        result.availability,
        uploaded_role_mappings,
        dataset_references,
    )
    uploaded_issues = _to_uploaded_issues(result.issues)
    if result.status in {
        GeoXTabularSourceAdapterStatus.ADAPTED,
        GeoXTabularSourceAdapterStatus.ADAPTED_WITH_WARNINGS,
    }:
        uploaded_issues.extend(
            [
                GeoXUploadedCSVAdapterIssueCode.SOURCE_INSPECTION_COMPATIBLE,
                GeoXUploadedCSVAdapterIssueCode.INPUT_RESOLUTION_COMPATIBLE,
            ]
        )

    return GeoXUploadedCSVAdapterResult(
        request_id=result.request_id,
        status=_TABULAR_TO_UPLOADED_STATUS.get(
            result.status,
            GeoXUploadedCSVAdapterStatus.BLOCKED_MATERIALIZATION_NOT_READY,
        ),
        availability=uploaded_availability,
        role_mappings=uploaded_role_mappings,
        dataset_references=dataset_references,
        issues=_dedupe_uploaded_issues(uploaded_issues),
        warnings=list(result.warnings),
        lineage={
            **result.lineage,
            "compatibility_bridge": "geox_tabular_source_adapter",
        },
    )


def _resolve_role(
    inspection: TabularSourceInspection,
    request: GeoXTabularSourceAdapterRequest,
) -> tuple[
    GeoXUploadedCSVRole,
    GeoXTabularSourceRoleSource,
    list[GeoXTabularSourceAdapterIssueCode],
]:
    issues: list[GeoXTabularSourceAdapterIssueCode] = []
    source_id = inspection.source_reference.source_id
    if source_id in request.explicit_role_by_source_id:
        issues.append(GeoXTabularSourceAdapterIssueCode.ROLE_EXPLICITLY_PROVIDED)
        return (
            request.explicit_role_by_source_id[source_id],
            GeoXTabularSourceRoleSource.EXPLICIT,
            issues,
        )

    hint = (inspection.source_reference.declared_role_hint or "").strip().lower()
    if hint and hint in _ROLE_ALIASES:
        issues.append(GeoXTabularSourceAdapterIssueCode.ROLE_HINT_USED)
        return (
            _ROLE_ALIASES[hint],
            GeoXTabularSourceRoleSource.DECLARED_ROLE_HINT,
            issues,
        )

    return GeoXUploadedCSVRole.UNKNOWN, GeoXTabularSourceRoleSource.UNKNOWN, issues


def _resolve_source_uri(
    reference: TabularSourceReference,
    data_source_ref: DataSourceRef,
    inspection: TabularSourceInspection,
) -> str:
    if reference.source_uri.strip():
        return reference.source_uri.strip()
    if data_source_ref.uri_or_table_ref.strip():
        return data_source_ref.uri_or_table_ref.strip()
    if inspection.lineage and inspection.lineage.source_uri.strip():
        return inspection.lineage.source_uri.strip()
    return ""


def _build_dataset_reference_from_tabular_mapping(
    mapping: GeoXTabularSourceRoleMapping,
) -> DatasetReference:
    source_uri = mapping.lineage.get("source_uri", "").strip()
    if not source_uri:
        msg = "source_uri unavailable for tabular GeoX role mapping"
        raise ValueError(msg)

    source_type = DatasetSourceType.UPLOADED_CSV
    if mapping.source_type != TabularSourceType.UPLOADED_CSV:
        source_type = DatasetSourceType.UNKNOWN

    role_source = mapping.role_source
    return DatasetReference(
        dataset_ref_id=mapping.source_id,
        source_type=source_type,
        semantic_type=_ROLE_TO_SEMANTIC[mapping.role],
        source_uri_or_handle=source_uri,
        file_name_or_table_name=mapping.source_name or mapping.source_id,
        declared_or_detected_columns=list(mapping.normalized_columns),
        classification_confidence=1.0 if mapping.role != GeoXUploadedCSVRole.UNKNOWN else 0.0,
        user_confirmation_status=(
            MappingConfirmationStatus.USER_CONFIRMED
            if role_source == GeoXTabularSourceRoleSource.EXPLICIT
            else MappingConfirmationStatus.NOT_REQUIRED
        ),
        lineage={
            **mapping.lineage,
            "geox_tabular_source_adapter": "true",
        },
        warnings=list(mapping.warnings),
    )


def _build_availability(
    role_mappings: list[GeoXTabularSourceRoleMapping],
    data_source_refs: list[DataSourceRef],
    tabular_source_references: list[TabularSourceReference],
    lineage: dict[str, str],
) -> GeoXTabularSourceInputAvailability:
    by_role = {mapping.role: mapping for mapping in role_mappings}
    kpi = by_role.get(GeoXUploadedCSVRole.KPI_PANEL)
    spend = by_role.get(GeoXUploadedCSVRole.SPEND_PANEL)
    assignment = by_role.get(GeoXUploadedCSVRole.ASSIGNMENT_TABLE)
    metadata = by_role.get(GeoXUploadedCSVRole.EXPERIMENT_METADATA)
    return GeoXTabularSourceInputAvailability(
        has_kpi_panel=kpi is not None,
        has_spend_panel=spend is not None,
        has_assignment_table=assignment is not None,
        has_experiment_metadata=metadata is not None,
        kpi_panel_source_id=kpi.source_id if kpi else None,
        spend_panel_source_id=spend.source_id if spend else None,
        assignment_table_source_id=assignment.source_id if assignment else None,
        metadata_source_id=metadata.source_id if metadata else None,
        data_source_refs=list(data_source_refs),
        role_mappings=list(role_mappings),
        tabular_source_references=list(tabular_source_references),
        lineage={
            **lineage,
            "role_mapping_count": str(len(role_mappings)),
        },
    )


def _to_uploaded_role_source(
    role_source: GeoXTabularSourceRoleSource,
) -> GeoXUploadedCSVRoleSource:
    if role_source == GeoXTabularSourceRoleSource.EXPLICIT:
        return GeoXUploadedCSVRoleSource.EXPLICIT
    if role_source == GeoXTabularSourceRoleSource.DECLARED_ROLE_HINT:
        return GeoXUploadedCSVRoleSource.DECLARED_ROLE_HINT
    return GeoXUploadedCSVRoleSource.UNKNOWN


def _to_uploaded_availability(
    availability: GeoXTabularSourceInputAvailability | None,
    role_mappings: list[GeoXUploadedCSVRoleMapping],
    dataset_references: list[DatasetReference],
) -> GeoXUploadedCSVAdapterAvailability | None:
    if availability is None:
        return None
    return GeoXUploadedCSVAdapterAvailability(
        has_kpi_panel=availability.has_kpi_panel,
        has_spend_panel=availability.has_spend_panel,
        has_assignment_table=availability.has_assignment_table,
        has_experiment_metadata=availability.has_experiment_metadata,
        kpi_panel_source_id=availability.kpi_panel_source_id,
        spend_panel_source_id=availability.spend_panel_source_id,
        assignment_table_source_id=availability.assignment_table_source_id,
        metadata_source_id=availability.metadata_source_id,
        dataset_references=list(dataset_references),
        role_mappings=list(role_mappings),
        lineage=dict(availability.lineage),
    )


def _to_uploaded_issues(
    issues: list[GeoXTabularSourceAdapterIssueCode],
) -> list[GeoXUploadedCSVAdapterIssueCode]:
    mapping: dict[GeoXTabularSourceAdapterIssueCode, GeoXUploadedCSVAdapterIssueCode] = {
        GeoXTabularSourceAdapterIssueCode.MISSING_TABULAR_SOURCE_RESULT: (
            GeoXUploadedCSVAdapterIssueCode.MISSING_MATERIALIZATION_RESULT
        ),
        GeoXTabularSourceAdapterIssueCode.TABULAR_SOURCE_NOT_READY: (
            GeoXUploadedCSVAdapterIssueCode.MATERIALIZATION_NOT_READY
        ),
        GeoXTabularSourceAdapterIssueCode.MISSING_REQUIRED_ROLE: (
            GeoXUploadedCSVAdapterIssueCode.MISSING_REQUIRED_ROLE
        ),
        GeoXTabularSourceAdapterIssueCode.DUPLICATE_ROLE: (
            GeoXUploadedCSVAdapterIssueCode.DUPLICATE_ROLE
        ),
        GeoXTabularSourceAdapterIssueCode.AMBIGUOUS_ROLE: (
            GeoXUploadedCSVAdapterIssueCode.AMBIGUOUS_ROLE
        ),
        GeoXTabularSourceAdapterIssueCode.MISSING_REQUIRED_COLUMNS: (
            GeoXUploadedCSVAdapterIssueCode.MISSING_REQUIRED_COLUMNS
        ),
        GeoXTabularSourceAdapterIssueCode.DATA_SOURCE_REF_UNAVAILABLE: (
            GeoXUploadedCSVAdapterIssueCode.DATASET_REFERENCE_BUILD_FAILED
        ),
        GeoXTabularSourceAdapterIssueCode.ROLE_HINT_USED: (
            GeoXUploadedCSVAdapterIssueCode.ROLE_HINT_USED
        ),
        GeoXTabularSourceAdapterIssueCode.ROLE_EXPLICITLY_PROVIDED: (
            GeoXUploadedCSVAdapterIssueCode.ROLE_EXPLICITLY_PROVIDED
        ),
        GeoXTabularSourceAdapterIssueCode.OPTIONAL_GEO_METADATA_MISSING: (
            GeoXUploadedCSVAdapterIssueCode.OPTIONAL_METADATA_MISSING
        ),
        GeoXTabularSourceAdapterIssueCode.TABULAR_SOURCE_LINEAGE_PRESERVED: (
            GeoXUploadedCSVAdapterIssueCode.LINEAGE_PRESERVED
        ),
    }
    uploaded: list[GeoXUploadedCSVAdapterIssueCode] = []
    for issue in issues:
        mapped = mapping.get(issue)
        if mapped is not None:
            uploaded.append(mapped)
    if GeoXUploadedCSVAdapterIssueCode.LINEAGE_PRESERVED not in uploaded:
        uploaded.insert(0, GeoXUploadedCSVAdapterIssueCode.LINEAGE_PRESERVED)
    return uploaded


def _blocked(
    request_id: str,
    status: GeoXTabularSourceAdapterStatus,
    issues: list[GeoXTabularSourceAdapterIssueCode],
    warnings: list[str],
    lineage: dict[str, str],
) -> GeoXTabularSourceAdapterResult:
    return GeoXTabularSourceAdapterResult(
        request_id=request_id,
        status=status,
        issues=_dedupe_issues(issues),
        warnings=list(dict.fromkeys(warnings)),
        lineage=lineage,
    )


def _dedupe_issues(
    issues: list[GeoXTabularSourceAdapterIssueCode],
) -> list[GeoXTabularSourceAdapterIssueCode]:
    seen: set[GeoXTabularSourceAdapterIssueCode] = set()
    ordered: list[GeoXTabularSourceAdapterIssueCode] = []
    for issue in issues:
        if issue not in seen:
            seen.add(issue)
            ordered.append(issue)
    return ordered


def _dedupe_uploaded_issues(
    issues: list[GeoXUploadedCSVAdapterIssueCode],
) -> list[GeoXUploadedCSVAdapterIssueCode]:
    seen: set[GeoXUploadedCSVAdapterIssueCode] = set()
    ordered: list[GeoXUploadedCSVAdapterIssueCode] = []
    for issue in issues:
        if issue not in seen:
            seen.add(issue)
            ordered.append(issue)
    return ordered
