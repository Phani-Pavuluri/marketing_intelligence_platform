"""Planning/MMM calibration-signal tabular intake workflow.

Intakes calibration-signal metadata from generic TabularSourceInspectionResult
without model fitting, prior application, or calibration math.
"""

from __future__ import annotations

from mip.contracts.planning_mmm_calibration_signal_tabular_intake import (
    DEFAULT_OPTIONAL_CALIBRATION_COLUMNS,
    DEFAULT_REQUIRED_CALIBRATION_COLUMNS,
    PlanningMMMCalibrationSignalColumnMapping,
    PlanningMMMCalibrationSignalColumnRole,
    PlanningMMMCalibrationSignalConstructionMode,
    PlanningMMMCalibrationSignalDeferredMapping,
    PlanningMMMCalibrationSignalTabularIntakeEnvelope,
    PlanningMMMCalibrationSignalTabularIntakeIssueCode,
    PlanningMMMCalibrationSignalTabularIntakeRequest,
    PlanningMMMCalibrationSignalTabularIntakeResult,
    PlanningMMMCalibrationSignalTabularIntakeStatus,
    PlanningMMMCalibrationSignalTabularSource,
)
from mip.contracts.tabular_source_reference import (
    TabularSourceInspection,
    TabularSourceInspectionResult,
    TabularSourceInspectionStatus,
)

_READY_TABULAR_STATUSES = {
    TabularSourceInspectionStatus.INSPECTED,
    TabularSourceInspectionStatus.INSPECTED_WITH_WARNINGS,
}
_CALIBRATION_ROLE_HINTS = {
    "calibration_signals",
    "calibration",
    "calibration_signal",
    "priors",
    "experiment_priors",
    "calibration_signal_data",
}
_CALIBRATION_SIGNAL_FULL_REQUIRED_FIELDS = (
    "calibration_id",
    "source_evidence_id",
    "target_model_id",
    "compatibility_status",
    "mapping_type",
    "lift_scale",
    "weight",
    "diagnostics",
    "confidence_tier",
)
_DEFAULT_COLUMN_ROLE_ALIASES: dict[PlanningMMMCalibrationSignalColumnRole, tuple[str, ...]] = {
    PlanningMMMCalibrationSignalColumnRole.CHANNEL: (
        "channel",
        "media_channel",
        "marketing_channel",
    ),
    PlanningMMMCalibrationSignalColumnRole.METRIC: ("metric", "kpi", "outcome_metric"),
    PlanningMMMCalibrationSignalColumnRole.ESTIMAND: (
        "estimand",
        "effect_estimand",
        "target_estimand",
    ),
    PlanningMMMCalibrationSignalColumnRole.LIFT: (
        "lift",
        "incremental_lift",
        "effect",
        "effect_size",
        "prior_lift",
    ),
    PlanningMMMCalibrationSignalColumnRole.STANDARD_ERROR: (
        "standard_error",
        "se",
        "std_error",
        "prior_uncertainty",
    ),
    PlanningMMMCalibrationSignalColumnRole.LOWER_BOUND: (
        "lower_bound",
        "ci_lower",
        "lower_ci",
    ),
    PlanningMMMCalibrationSignalColumnRole.UPPER_BOUND: (
        "upper_bound",
        "ci_upper",
        "upper_ci",
    ),
    PlanningMMMCalibrationSignalColumnRole.START_DATE: (
        "start_date",
        "period_start",
        "window_start",
    ),
    PlanningMMMCalibrationSignalColumnRole.END_DATE: (
        "end_date",
        "period_end",
        "window_end",
    ),
    PlanningMMMCalibrationSignalColumnRole.GEO_SCOPE: (
        "geo_scope",
        "scope",
        "market_scope",
    ),
    PlanningMMMCalibrationSignalColumnRole.EVIDENCE_SOURCE: (
        "evidence_source",
        "source",
        "experiment_source",
    ),
    PlanningMMMCalibrationSignalColumnRole.FRESHNESS_DATE: (
        "freshness_date",
        "as_of_date",
        "created_at",
    ),
}
_ROLE_FOR_REQUIRED_COLUMN: dict[str, PlanningMMMCalibrationSignalColumnRole] = {
    "channel": PlanningMMMCalibrationSignalColumnRole.CHANNEL,
    "metric": PlanningMMMCalibrationSignalColumnRole.METRIC,
    "estimand": PlanningMMMCalibrationSignalColumnRole.ESTIMAND,
    "lift": PlanningMMMCalibrationSignalColumnRole.LIFT,
    "standard_error": PlanningMMMCalibrationSignalColumnRole.STANDARD_ERROR,
    "start_date": PlanningMMMCalibrationSignalColumnRole.START_DATE,
    "end_date": PlanningMMMCalibrationSignalColumnRole.END_DATE,
    "lower_bound": PlanningMMMCalibrationSignalColumnRole.LOWER_BOUND,
    "upper_bound": PlanningMMMCalibrationSignalColumnRole.UPPER_BOUND,
    "geo_scope": PlanningMMMCalibrationSignalColumnRole.GEO_SCOPE,
    "evidence_source": PlanningMMMCalibrationSignalColumnRole.EVIDENCE_SOURCE,
    "freshness_date": PlanningMMMCalibrationSignalColumnRole.FRESHNESS_DATE,
}


def intake_calibration_signals_from_tabular_source(
    request: PlanningMMMCalibrationSignalTabularIntakeRequest,
) -> PlanningMMMCalibrationSignalTabularIntakeResult:
    """Intake calibration-signal metadata from generic tabular source inspection."""
    lineage = {
        **request.lineage,
        "intake_stage": "planning_mmm_calibration_signal_tabular_intake",
    }
    warnings = list(dict.fromkeys(request.warnings))
    issues: list[PlanningMMMCalibrationSignalTabularIntakeIssueCode] = [
        PlanningMMMCalibrationSignalTabularIntakeIssueCode.LINEAGE_PRESERVED,
        PlanningMMMCalibrationSignalTabularIntakeIssueCode.NO_MODEL_EXECUTION,
        PlanningMMMCalibrationSignalTabularIntakeIssueCode.NO_BAYESIAN_FITTING,
        PlanningMMMCalibrationSignalTabularIntakeIssueCode.NO_PRIOR_APPLICATION,
        PlanningMMMCalibrationSignalTabularIntakeIssueCode.NO_LIKELIHOOD_CONSTRUCTION,
        PlanningMMMCalibrationSignalTabularIntakeIssueCode.NO_POSTERIOR_CALCULATION,
        PlanningMMMCalibrationSignalTabularIntakeIssueCode.NO_OPTIMIZER_EXECUTION,
        PlanningMMMCalibrationSignalTabularIntakeIssueCode.NO_SIMULATOR_EXECUTION,
        PlanningMMMCalibrationSignalTabularIntakeIssueCode.NO_RECOMMENDATION_GENERATED,
        PlanningMMMCalibrationSignalTabularIntakeIssueCode.NO_DECISION_SURFACE_EXECUTION,
        PlanningMMMCalibrationSignalTabularIntakeIssueCode.NO_CLAIM_AUTHORIZATION,
    ]

    if request.tabular_source_result is None:
        return _blocked(
            request.request_id,
            PlanningMMMCalibrationSignalTabularIntakeStatus.BLOCKED_MISSING_TABULAR_SOURCE_RESULT,
            issues
            + [
                PlanningMMMCalibrationSignalTabularIntakeIssueCode.MISSING_TABULAR_SOURCE_RESULT
            ],
            warnings,
            lineage,
        )

    tabular_result = request.tabular_source_result
    warnings.extend(tabular_result.warnings)
    lineage.update(tabular_result.lineage)

    if tabular_result.status not in _READY_TABULAR_STATUSES:
        return _blocked(
            request.request_id,
            PlanningMMMCalibrationSignalTabularIntakeStatus.BLOCKED_TABULAR_SOURCE_NOT_READY,
            issues
            + [PlanningMMMCalibrationSignalTabularIntakeIssueCode.TABULAR_SOURCE_NOT_READY],
            warnings,
            lineage,
        )

    calibration_inspections = _identify_calibration_inspections(tabular_result, request)
    if not calibration_inspections:
        return _blocked(
            request.request_id,
            PlanningMMMCalibrationSignalTabularIntakeStatus.BLOCKED_MISSING_CALIBRATION_SIGNAL_SOURCE,
            issues
            + [
                PlanningMMMCalibrationSignalTabularIntakeIssueCode.MISSING_CALIBRATION_SIGNAL_SOURCE
            ],
            warnings,
            lineage,
        )

    if len(calibration_inspections) > 1 and not request.explicit_calibration_source_ids:
        return _blocked(
            request.request_id,
            PlanningMMMCalibrationSignalTabularIntakeStatus.BLOCKED_DUPLICATE_CALIBRATION_SIGNAL_SOURCE,
            issues
            + [
                PlanningMMMCalibrationSignalTabularIntakeIssueCode.DUPLICATE_CALIBRATION_SIGNAL_SOURCE
            ],
            warnings + ["Multiple calibration signal sources without explicit disambiguation"],
            lineage,
        )

    required_columns = (
        list(request.required_columns)
        if request.required_columns
        else list(DEFAULT_REQUIRED_CALIBRATION_COLUMNS)
    )
    optional_columns = (
        list(request.optional_columns)
        if request.optional_columns
        else list(DEFAULT_OPTIONAL_CALIBRATION_COLUMNS)
    )
    role_aliases = _merge_role_aliases(request.column_role_aliases)

    calibration_sources: list[PlanningMMMCalibrationSignalTabularSource] = []
    deferred_mappings: list[PlanningMMMCalibrationSignalDeferredMapping] = []
    data_source_refs = []
    tabular_source_references = []
    missing_required_all: list[str] = []
    optional_missing_all: list[str] = []

    for inspection in calibration_inspections:
        source, missing_required, optional_missing, source_issues = _build_calibration_source(
            inspection,
            required_columns=required_columns,
            optional_columns=optional_columns,
            role_aliases=role_aliases,
        )
        if missing_required:
            return _blocked(
                request.request_id,
                PlanningMMMCalibrationSignalTabularIntakeStatus.BLOCKED_MISSING_REQUIRED_COLUMNS,
                issues
                + source_issues
                + [PlanningMMMCalibrationSignalTabularIntakeIssueCode.MISSING_REQUIRED_COLUMNS],
                warnings
                + [
                    f"Missing required columns for {source.source_id}: "
                    f"{', '.join(missing_required)}"
                ],
                lineage,
            )

        construction_mode, deferred = _build_deferred_mapping(source)
        issues.extend(deferred.issues)

        if (
            request.require_full_calibration_signal_construction
            and construction_mode
            != PlanningMMMCalibrationSignalConstructionMode.CALIBRATION_SIGNAL_CONSTRUCTION_READY
        ):
            return _blocked(
                request.request_id,
                PlanningMMMCalibrationSignalTabularIntakeStatus.BLOCKED_CALIBRATION_SIGNAL_CONTRACT_UNAVAILABLE,
                issues
                + [
                    PlanningMMMCalibrationSignalTabularIntakeIssueCode.CALIBRATION_SIGNAL_CONTRACT_UNAVAILABLE
                ],
                warnings + ["Full CalibrationSignal construction unavailable"],
                lineage,
            )

        if optional_missing:
            warnings.append(
                f"Optional calibration columns missing for {source.source_id}: "
                + ", ".join(optional_missing)
            )
            issues.append(
                PlanningMMMCalibrationSignalTabularIntakeIssueCode.OPTIONAL_COLUMNS_MISSING
            )
            optional_missing_all.extend(optional_missing)

        calibration_sources.append(source)
        deferred_mappings.append(deferred)
        if source.data_source_ref is not None:
            data_source_refs.append(source.data_source_ref)
        if source.tabular_source_reference is not None:
            tabular_source_references.append(source.tabular_source_reference)
        missing_required_all.extend(missing_required)
        issues.extend(source.issues)
        issues.append(
            PlanningMMMCalibrationSignalTabularIntakeIssueCode.DEFERRED_MAPPING_CREATED
        )

    reference_only = all(
        inspection.availability is not None and inspection.availability.is_reference_only
        for inspection in calibration_inspections
    )
    construction_mode = (
        PlanningMMMCalibrationSignalConstructionMode.DIAGNOSTIC_ONLY
        if reference_only
        else deferred_mappings[0].construction_mode
        if deferred_mappings
        else PlanningMMMCalibrationSignalConstructionMode.CALIBRATION_SIGNAL_CONSTRUCTION_DEFERRED
    )

    if reference_only:
        status = PlanningMMMCalibrationSignalTabularIntakeStatus.DIAGNOSTIC_ONLY
    elif warnings or optional_missing_all or (
        construction_mode
        == PlanningMMMCalibrationSignalConstructionMode.CALIBRATION_SIGNAL_CONSTRUCTION_DEFERRED
    ):
        status = PlanningMMMCalibrationSignalTabularIntakeStatus.INTAKE_READY_WITH_WARNINGS
    else:
        status = PlanningMMMCalibrationSignalTabularIntakeStatus.INTAKE_READY

    envelope = PlanningMMMCalibrationSignalTabularIntakeEnvelope(
        envelope_id=f"planning-mmm-calibration-intake:{request.request_id}",
        status=status,
        construction_mode=construction_mode,
        calibration_signal_sources=calibration_sources,
        deferred_mappings=deferred_mappings,
        data_source_refs=data_source_refs,
        tabular_source_references=tabular_source_references,
        missing_required_columns=list(dict.fromkeys(missing_required_all)),
        optional_columns_missing=list(dict.fromkeys(optional_missing_all)),
        readiness_metadata={
            "calibration_signal_source_count": str(len(calibration_sources)),
            "metadata_compatible": str(
                any(m.metadata_compatible for m in deferred_mappings)
            ).lower(),
            "has_calibration_signal_data": "true",
        },
        execution_allowed=_default_execution_allowed(),
        lineage={
            **lineage,
            "calibration_source_ids": ",".join(s.source_id for s in calibration_sources),
        },
        warnings=list(dict.fromkeys(warnings)),
        issues=_dedupe_issues(
            issues
            + [PlanningMMMCalibrationSignalTabularIntakeIssueCode.TABULAR_SOURCE_SCHEMA_USED]
        ),
    )

    return PlanningMMMCalibrationSignalTabularIntakeResult(
        request_id=request.request_id,
        status=status,
        envelope=envelope,
        issues=_dedupe_issues(issues + envelope.issues),
        warnings=list(dict.fromkeys(warnings)),
        lineage=lineage,
    )


def summarize_calibration_signal_tabular_intake(
    result: PlanningMMMCalibrationSignalTabularIntakeResult,
) -> dict[str, str | list[str] | dict[str, bool]]:
    """Produce a metadata-only summary of calibration-signal tabular intake."""
    envelope = result.envelope
    if envelope is None:
        return {
            "status": str(result.status),
            "construction_mode": "blocked",
            "source_ids": [],
            "missing_required_columns": [],
            "optional_columns_missing": [],
            "deferred_mapping_ids": [],
            "execution_allowed": _default_execution_allowed(),
        }

    return {
        "status": str(result.status),
        "construction_mode": str(envelope.construction_mode),
        "source_ids": [source.source_id for source in envelope.calibration_signal_sources],
        "missing_required_columns": list(envelope.missing_required_columns),
        "optional_columns_missing": list(envelope.optional_columns_missing),
        "deferred_mapping_ids": [mapping.mapping_id for mapping in envelope.deferred_mappings],
        "execution_allowed": dict(envelope.execution_allowed),
    }


def _identify_calibration_inspections(
    tabular_result: TabularSourceInspectionResult,
    request: PlanningMMMCalibrationSignalTabularIntakeRequest,
) -> list[TabularSourceInspection]:
    if request.explicit_calibration_source_ids:
        by_id = {
            inspection.source_reference.source_id: inspection
            for inspection in tabular_result.inspections
        }
        selected: list[TabularSourceInspection] = []
        for source_id in request.explicit_calibration_source_ids:
            inspection = by_id.get(source_id)
            if inspection is not None:
                selected.append(inspection)
        return selected

    selected = []
    for inspection in tabular_result.inspections:
        hint = (inspection.source_reference.declared_role_hint or "").strip().lower()
        if hint in _CALIBRATION_ROLE_HINTS:
            selected.append(inspection)
    return selected


def _build_calibration_source(
    inspection: TabularSourceInspection,
    *,
    required_columns: list[str],
    optional_columns: list[str],
    role_aliases: dict[PlanningMMMCalibrationSignalColumnRole, tuple[str, ...]],
) -> tuple[
    PlanningMMMCalibrationSignalTabularSource,
    list[str],
    list[str],
    list[PlanningMMMCalibrationSignalTabularIntakeIssueCode],
]:
    reference = inspection.source_reference
    schema = inspection.source_schema
    normalized_columns = list(schema.normalized_column_names) if schema is not None else []
    schema_columns = list(schema.column_names) if schema is not None else []

    column_mappings: list[PlanningMMMCalibrationSignalColumnMapping] = []
    missing_required: list[str] = []
    optional_missing: list[str] = []
    source_issues = [
        PlanningMMMCalibrationSignalTabularIntakeIssueCode.TABULAR_SOURCE_SCHEMA_USED,
        PlanningMMMCalibrationSignalTabularIntakeIssueCode.TABULAR_SOURCE_REFERENCE_PRESERVED,
    ]
    if reference.data_source_ref is not None:
        source_issues.append(
            PlanningMMMCalibrationSignalTabularIntakeIssueCode.DATA_SOURCE_REF_PRESERVED
        )

    for column_name in required_columns:
        role = _ROLE_FOR_REQUIRED_COLUMN.get(
            column_name, PlanningMMMCalibrationSignalColumnRole.UNKNOWN
        )
        matched = _match_column(column_name, role, normalized_columns, role_aliases)
        present = matched is not None
        if not present:
            missing_required.append(column_name)
        column_mappings.append(
            PlanningMMMCalibrationSignalColumnMapping(
                column_name=matched or column_name,
                normalized_column_name=matched or column_name,
                column_role=role,
                required=True,
                present=present,
            )
        )

    for column_name in optional_columns:
        role = _ROLE_FOR_REQUIRED_COLUMN.get(
            column_name, PlanningMMMCalibrationSignalColumnRole.UNKNOWN
        )
        matched = _match_column(column_name, role, normalized_columns, role_aliases)
        present = matched is not None
        if not present:
            optional_missing.append(column_name)
        column_mappings.append(
            PlanningMMMCalibrationSignalColumnMapping(
                column_name=matched or column_name,
                normalized_column_name=matched or column_name,
                column_role=role,
                required=False,
                present=present,
            )
        )

    source = PlanningMMMCalibrationSignalTabularSource(
        source_id=reference.source_id,
        source_type=reference.source_type,
        source_name=reference.source_name,
        data_source_ref=reference.data_source_ref,
        tabular_source_reference=reference,
        lineage={
            **(inspection.lineage.metadata if inspection.lineage else {}),
            **(inspection.lineage.upstream_lineage if inspection.lineage else {}),
            **reference.metadata,
            "declared_role_hint": reference.declared_role_hint or "",
        },
        schema_columns=schema_columns,
        normalized_columns=normalized_columns,
        column_mappings=column_mappings,
        missing_required_columns=list(missing_required),
        warnings=list(inspection.warnings),
        issues=source_issues,
    )
    return source, missing_required, optional_missing, source_issues


def _build_deferred_mapping(
    source: PlanningMMMCalibrationSignalTabularSource,
) -> tuple[
    PlanningMMMCalibrationSignalConstructionMode,
    PlanningMMMCalibrationSignalDeferredMapping,
]:
    present_roles = {
        mapping.column_role
        for mapping in source.column_mappings
        if mapping.present and mapping.required
    }
    compatible_fields: list[str] = []
    if PlanningMMMCalibrationSignalColumnRole.CHANNEL in present_roles:
        compatible_fields.append("channel")
    if PlanningMMMCalibrationSignalColumnRole.LIFT in present_roles:
        compatible_fields.append("lift_column_reference")
    if PlanningMMMCalibrationSignalColumnRole.STANDARD_ERROR in present_roles:
        compatible_fields.append("standard_error_column_reference")
    if PlanningMMMCalibrationSignalColumnRole.METRIC in present_roles:
        compatible_fields.append("metric")
    if PlanningMMMCalibrationSignalColumnRole.ESTIMAND in present_roles:
        compatible_fields.append("estimand")

    metadata_compatible = bool(compatible_fields)
    deferred_issues = [
        PlanningMMMCalibrationSignalTabularIntakeIssueCode.CALIBRATION_SIGNAL_METADATA_COMPATIBLE,
        PlanningMMMCalibrationSignalTabularIntakeIssueCode.CALIBRATION_SIGNAL_CONSTRUCTION_DEFERRED,
    ]
    mode = PlanningMMMCalibrationSignalConstructionMode.CALIBRATION_SIGNAL_CONSTRUCTION_DEFERRED
    deferred_reason = (
        "CalibrationSignal requires target_model_id, diagnostics, and session context"
    )

    mapping = PlanningMMMCalibrationSignalDeferredMapping(
        mapping_id=f"deferred-calibration:{source.source_id}",
        source_id=source.source_id,
        construction_mode=mode,
        metadata_compatible=metadata_compatible,
        calibration_signal_contract_available=True,
        full_construction_deferred_reason=deferred_reason,
        compatible_fields=list(dict.fromkeys(compatible_fields)),
        missing_fields=list(_CALIBRATION_SIGNAL_FULL_REQUIRED_FIELDS),
        deferred_fields=list(_CALIBRATION_SIGNAL_FULL_REQUIRED_FIELDS),
        warnings=list(source.warnings),
        issues=deferred_issues,
    )
    return mode, mapping


def _match_column(
    column_name: str,
    role: PlanningMMMCalibrationSignalColumnRole,
    normalized_columns: list[str],
    role_aliases: dict[PlanningMMMCalibrationSignalColumnRole, tuple[str, ...]],
) -> str | None:
    candidates = {column_name.lower()}
    candidates.update(alias.lower() for alias in role_aliases.get(role, ()))
    for col in normalized_columns:
        if col.lower() in candidates:
            return col
    return None


def _merge_role_aliases(
    custom_aliases: dict[str, list[str]],
) -> dict[PlanningMMMCalibrationSignalColumnRole, tuple[str, ...]]:
    merged: dict[PlanningMMMCalibrationSignalColumnRole, tuple[str, ...]] = {
        role: aliases for role, aliases in _DEFAULT_COLUMN_ROLE_ALIASES.items()
    }
    for key, values in custom_aliases.items():
        role = _ROLE_FOR_REQUIRED_COLUMN.get(key)
        if role is None:
            continue
        existing = list(merged.get(role, ()))
        existing.extend(values)
        merged[role] = tuple(dict.fromkeys(existing))
    return merged


def _default_execution_allowed() -> dict[str, bool]:
    return {
        "model_execution": False,
        "bayesian_fitting": False,
        "prior_application": False,
        "likelihood_construction": False,
        "posterior_calculation": False,
        "optimizer_execution": False,
        "simulator_execution": False,
        "recommendation_generation": False,
        "decision_surface_execution": False,
        "claim_authorization": False,
    }


def _blocked(
    request_id: str,
    status: PlanningMMMCalibrationSignalTabularIntakeStatus,
    issues: list[PlanningMMMCalibrationSignalTabularIntakeIssueCode],
    warnings: list[str],
    lineage: dict[str, str],
) -> PlanningMMMCalibrationSignalTabularIntakeResult:
    return PlanningMMMCalibrationSignalTabularIntakeResult(
        request_id=request_id,
        status=status,
        issues=_dedupe_issues(issues),
        warnings=list(dict.fromkeys(warnings)),
        lineage=lineage,
    )


def _dedupe_issues(
    issues: list[PlanningMMMCalibrationSignalTabularIntakeIssueCode],
) -> list[PlanningMMMCalibrationSignalTabularIntakeIssueCode]:
    seen: set[PlanningMMMCalibrationSignalTabularIntakeIssueCode] = set()
    ordered: list[PlanningMMMCalibrationSignalTabularIntakeIssueCode] = []
    for issue in issues:
        if issue not in seen:
            seen.add(issue)
            ordered.append(issue)
    return ordered
