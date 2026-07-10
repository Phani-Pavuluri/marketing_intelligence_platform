"""Planning/MMM readiness report adapter workflow.

Maps Planning/MMM workflow-readiness output into MMMDataReadinessReport-compatible
metadata without model fitting, optimization, recommendations, or claim authorization.
"""

from __future__ import annotations

from mip.contracts.planning_mmm_readiness_report_adapter import (
    PlanningMMMReadinessReportAdapterEnvelope,
    PlanningMMMReadinessReportAdapterIssueCode,
    PlanningMMMReadinessReportAdapterRequest,
    PlanningMMMReadinessReportAdapterResult,
    PlanningMMMReadinessReportAdapterStatus,
    PlanningMMMReadinessReportCompatibility,
    PlanningMMMReadinessReportCompatibilityMode,
)
from mip.contracts.planning_mmm_uploaded_csv_workflow_readiness import (
    PlanningMMMUploadedCSVWorkflowReadinessReport,
    PlanningMMMUploadedCSVWorkflowReadinessResult,
    PlanningMMMUploadedCSVWorkflowReadinessStatus,
)
from mip.contracts.tabular_source_reference import (
    TabularSourceAccessMode,
    TabularSourceMaterializationMode,
    TabularSourceReference,
    TabularSourceType,
)

_READY_WORKFLOW_STATUSES = {
    PlanningMMMUploadedCSVWorkflowReadinessStatus.READY_FOR_MMM_WORKFLOW_READINESS,
    PlanningMMMUploadedCSVWorkflowReadinessStatus.READY_WITH_WARNINGS,
}
_BLOCKED_WORKFLOW_STATUS_MAP: dict[
    PlanningMMMUploadedCSVWorkflowReadinessStatus,
    PlanningMMMReadinessReportAdapterStatus,
] = {
    PlanningMMMUploadedCSVWorkflowReadinessStatus.BLOCKED_MISSING_INPUT_PLAN_RESULT: (
        PlanningMMMReadinessReportAdapterStatus.BLOCKED_WORKFLOW_READINESS_NOT_READY
    ),
    PlanningMMMUploadedCSVWorkflowReadinessStatus.BLOCKED_INPUT_PLAN_NOT_READY: (
        PlanningMMMReadinessReportAdapterStatus.BLOCKED_WORKFLOW_READINESS_NOT_READY
    ),
    PlanningMMMUploadedCSVWorkflowReadinessStatus.BLOCKED_MISSING_REQUIRED_INPUT: (
        PlanningMMMReadinessReportAdapterStatus.BLOCKED_MISSING_REQUIRED_INPUT
    ),
    PlanningMMMUploadedCSVWorkflowReadinessStatus.BLOCKED_MISSING_REQUIRED_COLUMNS: (
        PlanningMMMReadinessReportAdapterStatus.BLOCKED_MISSING_REQUIRED_COLUMNS
    ),
    PlanningMMMUploadedCSVWorkflowReadinessStatus.BLOCKED_EXECUTION_FLAGS_NOT_SAFE: (
        PlanningMMMReadinessReportAdapterStatus.BLOCKED_WORKFLOW_READINESS_NOT_READY
    ),
}
_MMM_FULL_REPORT_REQUIRED_FIELDS = (
    "session_id",
    "recommendation_id",
    "manifest_id",
    "assessment_id",
    "created_at",
    "findings",
    "blocking_reasons",
)
_MMM_METADATA_COMPATIBLE_FIELDS = (
    "has_outcome_data",
    "has_media_data",
    "has_time_coverage",
    "has_channel_mapping",
    "has_calibration_signal_data",
    "calibration_required",
    "status",
    "warnings",
)


def adapt_planning_mmm_workflow_readiness_to_readiness_report(
    request: PlanningMMMReadinessReportAdapterRequest,
) -> PlanningMMMReadinessReportAdapterResult:
    """Adapt Planning/MMM workflow readiness into readiness report semantics."""
    lineage = {
        **request.lineage,
        "adapter_stage": "planning_mmm_readiness_report_adapter",
    }
    warnings = list(dict.fromkeys(request.warnings))
    issues: list[PlanningMMMReadinessReportAdapterIssueCode] = [
        PlanningMMMReadinessReportAdapterIssueCode.LINEAGE_PRESERVED,
        PlanningMMMReadinessReportAdapterIssueCode.NO_MODEL_EXECUTION,
        PlanningMMMReadinessReportAdapterIssueCode.NO_BAYESIAN_FITTING,
        PlanningMMMReadinessReportAdapterIssueCode.NO_OPTIMIZER_EXECUTION,
        PlanningMMMReadinessReportAdapterIssueCode.NO_SIMULATOR_EXECUTION,
        PlanningMMMReadinessReportAdapterIssueCode.NO_RECOMMENDATION_GENERATED,
        PlanningMMMReadinessReportAdapterIssueCode.NO_DECISION_SURFACE_EXECUTION,
        PlanningMMMReadinessReportAdapterIssueCode.NO_CLAIM_AUTHORIZATION,
    ]

    if request.workflow_readiness_result is None:
        return _blocked(
            request.request_id,
            PlanningMMMReadinessReportAdapterStatus.BLOCKED_MISSING_WORKFLOW_READINESS_RESULT,
            issues + [PlanningMMMReadinessReportAdapterIssueCode.MISSING_WORKFLOW_READINESS_RESULT],
            warnings,
            lineage,
        )

    workflow_result = request.workflow_readiness_result
    warnings.extend(workflow_result.warnings)
    lineage.update(workflow_result.lineage)

    if workflow_result.status == PlanningMMMUploadedCSVWorkflowReadinessStatus.DIAGNOSTIC_ONLY:
        return _adapt_diagnostic(
            request.request_id,
            workflow_result,
            issues,
            warnings,
            lineage,
        )

    if workflow_result.status not in _READY_WORKFLOW_STATUSES:
        blocked_status = _BLOCKED_WORKFLOW_STATUS_MAP.get(
            workflow_result.status,
            PlanningMMMReadinessReportAdapterStatus.BLOCKED_WORKFLOW_READINESS_NOT_READY,
        )
        return _blocked(
            request.request_id,
            blocked_status,
            issues + [PlanningMMMReadinessReportAdapterIssueCode.WORKFLOW_READINESS_NOT_READY],
            warnings,
            lineage,
            workflow_result=workflow_result,
        )

    report = workflow_result.report
    if report is None:
        return _blocked(
            request.request_id,
            PlanningMMMReadinessReportAdapterStatus.BLOCKED_WORKFLOW_READINESS_NOT_READY,
            issues + [PlanningMMMReadinessReportAdapterIssueCode.WORKFLOW_READINESS_NOT_READY],
            warnings,
            lineage,
        )

    if report.missing_required_inputs:
        return _blocked(
            request.request_id,
            PlanningMMMReadinessReportAdapterStatus.BLOCKED_MISSING_REQUIRED_INPUT,
            issues + [PlanningMMMReadinessReportAdapterIssueCode.MISSING_REQUIRED_INPUT],
            warnings,
            lineage,
            workflow_result=workflow_result,
            report=report,
        )

    if report.missing_required_columns:
        return _blocked(
            request.request_id,
            PlanningMMMReadinessReportAdapterStatus.BLOCKED_MISSING_REQUIRED_COLUMNS,
            issues + [PlanningMMMReadinessReportAdapterIssueCode.MISSING_REQUIRED_COLUMNS],
            warnings,
            lineage,
            workflow_result=workflow_result,
            report=report,
        )

    compatibility = _build_compatibility(report, request.require_full_mmm_data_readiness_report)
    issues.extend(compatibility.issues)

    if (
        request.require_full_mmm_data_readiness_report
        and compatibility.mode
        != PlanningMMMReadinessReportCompatibilityMode.FULL_REPORT_CONSTRUCTION_READY
    ):
        return _blocked(
            request.request_id,
            PlanningMMMReadinessReportAdapterStatus.BLOCKED_MMM_DATA_READINESS_CONTRACT_UNAVAILABLE,
            issues,
            warnings + ["Full MMMDataReadinessReport construction unavailable"],
            lineage,
            workflow_result=workflow_result,
            report=report,
            compatibility=compatibility,
        )

    if report.missing_optional_inputs:
        issues.append(PlanningMMMReadinessReportAdapterIssueCode.OPTIONAL_INPUT_MISSING)
        warnings.append(
            f"Optional inputs missing: {', '.join(report.missing_optional_inputs)}"
        )

    has_warnings = bool(warnings) or bool(report.missing_optional_inputs) or bool(
        compatibility.mode
        == PlanningMMMReadinessReportCompatibilityMode.FULL_REPORT_CONSTRUCTION_DEFERRED
    )
    if has_warnings:
        status = PlanningMMMReadinessReportAdapterStatus.REPORT_ADAPTED_WITH_WARNINGS
    else:
        status = PlanningMMMReadinessReportAdapterStatus.REPORT_ADAPTED

    envelope = _build_envelope(
        request_id=request.request_id,
        workflow_result=workflow_result,
        report=report,
        compatibility=compatibility,
        issues=issues,
        warnings=warnings,
        lineage=lineage,
    )

    return PlanningMMMReadinessReportAdapterResult(
        request_id=request.request_id,
        status=status,
        envelope=envelope,
        issues=_dedupe_issues(issues + envelope.issues),
        warnings=list(dict.fromkeys(warnings)),
        lineage=lineage,
    )


def summarize_planning_mmm_readiness_report_adapter(
    result: PlanningMMMReadinessReportAdapterResult,
) -> dict[str, str | list[str] | dict[str, bool]]:
    """Produce a metadata-only summary of the readiness report adapter result."""
    envelope = result.envelope
    if envelope is None:
        return {
            "status": str(result.status),
            "source_workflow_readiness_status": "",
            "source_workflow_readiness_tier": "",
            "compatibility_mode": "blocked",
            "missing_required_inputs": [],
            "missing_optional_inputs": [],
            "missing_required_columns": [],
            "deferred_objects": [],
            "execution_allowed": _default_execution_allowed(),
        }

    return {
        "status": str(result.status),
        "source_workflow_readiness_status": envelope.source_workflow_readiness_status,
        "source_workflow_readiness_tier": envelope.source_workflow_readiness_tier,
        "compatibility_mode": str(envelope.compatibility.mode),
        "missing_required_inputs": list(envelope.missing_required_inputs),
        "missing_optional_inputs": list(envelope.missing_optional_inputs),
        "missing_required_columns": list(envelope.missing_required_columns),
        "deferred_objects": list(envelope.deferred_objects.keys()),
        "execution_allowed": dict(envelope.execution_allowed),
    }


def _adapt_diagnostic(
    request_id: str,
    workflow_result: PlanningMMMUploadedCSVWorkflowReadinessResult,
    issues: list[PlanningMMMReadinessReportAdapterIssueCode],
    warnings: list[str],
    lineage: dict[str, str],
) -> PlanningMMMReadinessReportAdapterResult:
    report = workflow_result.report
    compatibility = PlanningMMMReadinessReportCompatibility(
        mode=PlanningMMMReadinessReportCompatibilityMode.DIAGNOSTIC_ONLY,
        metadata_compatible=False,
        full_report_constructed=False,
        full_report_deferred_reason="workflow readiness diagnostic only",
        issues=[PlanningMMMReadinessReportAdapterIssueCode.MMM_DATA_READINESS_FULL_CONSTRUCTION_DEFERRED],
    )
    envelope = _build_envelope(
        request_id=request_id,
        workflow_result=workflow_result,
        report=report,
        compatibility=compatibility,
        issues=issues,
        warnings=warnings,
        lineage=lineage,
        readiness_report_status="diagnostic_only",
    )
    return PlanningMMMReadinessReportAdapterResult(
        request_id=request_id,
        status=PlanningMMMReadinessReportAdapterStatus.DIAGNOSTIC_ONLY,
        envelope=envelope,
        issues=_dedupe_issues(issues + envelope.issues),
        warnings=list(dict.fromkeys(warnings)),
        lineage=lineage,
    )


def _build_compatibility(
    report: PlanningMMMUploadedCSVWorkflowReadinessReport,
    require_full_report: bool,
) -> PlanningMMMReadinessReportCompatibility:
    metadata = report.readiness_metadata
    compatible_fields: list[str] = []
    if metadata.get("has_historical_outcome"):
        compatible_fields.append("has_outcome_data")
    if metadata.get("has_historical_spend"):
        compatible_fields.append("has_media_data")
    if metadata.get("has_channel_taxonomy"):
        compatible_fields.append("has_channel_mapping")
    if metadata.get("has_calibration_signals"):
        compatible_fields.append("has_calibration_signal_data")
    if metadata.get("schema_validation_level"):
        compatible_fields.append("has_time_coverage")
    compatible_fields.extend(["status", "warnings"])

    metadata_compatible = bool(
        report.compatibility.get("mmm_data_readiness_report_compatible", False)
        or compatible_fields
    )
    deferred_reason = ""
    compat_issues: list[PlanningMMMReadinessReportAdapterIssueCode] = []

    if metadata_compatible:
        compat_issues.append(
            PlanningMMMReadinessReportAdapterIssueCode.MMM_DATA_READINESS_METADATA_COMPATIBLE
        )
        deferred_reason = (
            "MMMDataReadinessReport requires session/manifest/recommendation context"
        )
        mode = PlanningMMMReadinessReportCompatibilityMode.FULL_REPORT_CONSTRUCTION_DEFERRED
        compat_issues.append(
            PlanningMMMReadinessReportAdapterIssueCode.MMM_DATA_READINESS_FULL_CONSTRUCTION_DEFERRED
        )
    else:
        deferred_reason = "workflow readiness metadata insufficient for MMM data readiness"
        mode = PlanningMMMReadinessReportCompatibilityMode.FULL_REPORT_CONSTRUCTION_DEFERRED
        compat_issues.append(
            PlanningMMMReadinessReportAdapterIssueCode.MMM_DATA_READINESS_FULL_CONSTRUCTION_DEFERRED
        )

    return PlanningMMMReadinessReportCompatibility(
        mode=mode,
        mmm_data_readiness_report_available=True,
        full_report_constructed=False,
        full_report_deferred_reason=deferred_reason,
        metadata_compatible=metadata_compatible,
        compatible_fields=list(dict.fromkeys(compatible_fields)),
        missing_fields=list(_MMM_FULL_REPORT_REQUIRED_FIELDS),
        deferred_fields=list(_MMM_FULL_REPORT_REQUIRED_FIELDS),
        warnings=list(report.warnings),
        issues=compat_issues,
    )


def _build_envelope(
    *,
    request_id: str,
    workflow_result: PlanningMMMUploadedCSVWorkflowReadinessResult,
    report: PlanningMMMUploadedCSVWorkflowReadinessReport | None,
    compatibility: PlanningMMMReadinessReportCompatibility,
    issues: list[PlanningMMMReadinessReportAdapterIssueCode],
    warnings: list[str],
    lineage: dict[str, str],
    readiness_report_status: str | None = None,
) -> PlanningMMMReadinessReportAdapterEnvelope:
    if report is None:
        return PlanningMMMReadinessReportAdapterEnvelope(
            envelope_id=f"planning-mmm-readiness-envelope:{request_id}",
            source_workflow_readiness_status=str(workflow_result.status),
            source_workflow_readiness_tier="blocked",
            readiness_report_status=readiness_report_status or "blocked",
            compatibility=compatibility,
            execution_allowed=_default_execution_allowed(),
            lineage=lineage,
            warnings=list(dict.fromkeys(warnings)),
            issues=_dedupe_issues(issues),
        )

    envelope_issues = list(issues)
    if report.data_source_refs:
        envelope_issues.append(PlanningMMMReadinessReportAdapterIssueCode.DATA_SOURCE_REFS_PRESERVED)
    tabular_refs = _tabular_source_refs_from_report(report)
    if tabular_refs:
        envelope_issues.append(
            PlanningMMMReadinessReportAdapterIssueCode.TABULAR_SOURCE_REFS_PRESERVED
        )
    if report.deferred_objects:
        envelope_issues.append(
            PlanningMMMReadinessReportAdapterIssueCode.DEFERRED_OBJECTS_PRESERVED
        )
    envelope_issues.extend(
        [
            PlanningMMMReadinessReportAdapterIssueCode.READINESS_STATUS_PRESERVED,
            PlanningMMMReadinessReportAdapterIssueCode.READINESS_TIER_PRESERVED,
        ]
    )

    return PlanningMMMReadinessReportAdapterEnvelope(
        envelope_id=f"planning-mmm-readiness-envelope:{request_id}",
        source_workflow_readiness_status=str(report.status),
        source_workflow_readiness_tier=str(report.tier),
        readiness_report_status=readiness_report_status or str(report.status),
        compatibility=compatibility,
        data_source_refs=list(report.data_source_refs),
        tabular_source_refs=tabular_refs,
        missing_required_inputs=list(report.missing_required_inputs),
        missing_optional_inputs=list(report.missing_optional_inputs),
        missing_required_columns=list(report.missing_required_columns),
        deferred_objects=dict(report.deferred_objects),
        readiness_metadata=dict(report.readiness_metadata),
        execution_allowed=_normalize_execution_allowed(report.execution_allowed),
        lineage={
            **lineage,
            **report.lineage,
            "input_plan_id": report.input_plan_id or "",
        },
        warnings=list(dict.fromkeys(warnings)),
        issues=_dedupe_issues(envelope_issues),
    )


def _tabular_source_refs_from_report(
    report: PlanningMMMUploadedCSVWorkflowReadinessReport,
) -> list[TabularSourceReference]:
    refs: list[TabularSourceReference] = []
    raw_ids = report.lineage.get("tabular_source_reference_ids", "")
    if raw_ids:
        for source_id in raw_ids.split(","):
            source_id = source_id.strip()
            if not source_id:
                continue
            refs.append(
                TabularSourceReference(
                    source_id=source_id,
                    source_type=TabularSourceType.UPLOADED_CSV,
                    access_mode=TabularSourceAccessMode.LOCAL_FILE,
                    materialization_mode=TabularSourceMaterializationMode.MATERIALIZED_IN_MEMORY,
                    source_uri=report.lineage.get(f"tabular_source_uri:{source_id}", ""),
                    source_name=report.lineage.get(f"tabular_source_name:{source_id}", ""),
                )
            )
    metadata_ids = report.readiness_metadata.get("tabular_source_reference_ids")
    if isinstance(metadata_ids, str) and metadata_ids and not refs:
        for source_id in metadata_ids.split(","):
            source_id = source_id.strip()
            if source_id:
                refs.append(
                    TabularSourceReference(
                        source_id=source_id,
                        source_type=TabularSourceType.UNKNOWN,
                        access_mode=TabularSourceAccessMode.REFERENCE_ONLY,
                        materialization_mode=TabularSourceMaterializationMode.REFERENCE_ONLY,
                    )
                )
    return refs


def _normalize_execution_allowed(execution_allowed: dict[str, bool]) -> dict[str, bool]:
    normalized = _default_execution_allowed()
    for key in normalized:
        if key in execution_allowed:
            normalized[key] = bool(execution_allowed[key])
    for key, value in execution_allowed.items():
        if key not in normalized:
            normalized[key] = bool(value)
    return normalized


def _default_execution_allowed() -> dict[str, bool]:
    return {
        "model_execution": False,
        "bayesian_model_execution": False,
        "optimizer_execution": False,
        "simulator_execution": False,
        "recommendation_generation": False,
        "decision_surface_execution": False,
        "claim_authorization": False,
    }


def _blocked(
    request_id: str,
    status: PlanningMMMReadinessReportAdapterStatus,
    issues: list[PlanningMMMReadinessReportAdapterIssueCode],
    warnings: list[str],
    lineage: dict[str, str],
    *,
    workflow_result: PlanningMMMUploadedCSVWorkflowReadinessResult | None = None,
    report: PlanningMMMUploadedCSVWorkflowReadinessReport | None = None,
    compatibility: PlanningMMMReadinessReportCompatibility | None = None,
) -> PlanningMMMReadinessReportAdapterResult:
    envelope: PlanningMMMReadinessReportAdapterEnvelope | None = None
    if workflow_result is not None:
        compat = compatibility or PlanningMMMReadinessReportCompatibility(
            mode=PlanningMMMReadinessReportCompatibilityMode.FULL_REPORT_CONSTRUCTION_DEFERRED,
            metadata_compatible=False,
            full_report_deferred_reason="workflow readiness blocked",
            issues=[PlanningMMMReadinessReportAdapterIssueCode.MMM_DATA_READINESS_FULL_CONSTRUCTION_DEFERRED],
        )
        envelope = _build_envelope(
            request_id=request_id,
            workflow_result=workflow_result,
            report=report or workflow_result.report,
            compatibility=compat,
            issues=issues,
            warnings=warnings,
            lineage=lineage,
            readiness_report_status="blocked",
        )
    return PlanningMMMReadinessReportAdapterResult(
        request_id=request_id,
        status=status,
        envelope=envelope,
        issues=_dedupe_issues(issues + (envelope.issues if envelope is not None else [])),
        warnings=list(dict.fromkeys(warnings)),
        lineage=lineage,
    )


def _dedupe_issues(
    issues: list[PlanningMMMReadinessReportAdapterIssueCode],
) -> list[PlanningMMMReadinessReportAdapterIssueCode]:
    seen: set[PlanningMMMReadinessReportAdapterIssueCode] = set()
    ordered: list[PlanningMMMReadinessReportAdapterIssueCode] = []
    for issue in issues:
        if issue not in seen:
            seen.add(issue)
            ordered.append(issue)
    return ordered
