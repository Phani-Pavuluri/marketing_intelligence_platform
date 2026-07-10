"""Planning/MMM uploaded CSV workflow readiness evaluation.

Evaluates whether a governed Planning/MMM uploaded CSV input plan can enter
existing MMM workflow-readiness gates. Does not fit models, optimize budgets,
simulate scenarios, or execute workflows.
"""

from __future__ import annotations

from mip.contracts.planning_mmm_uploaded_csv_input_plan import (
    PlanningMMMUploadedCSVInputPlan,
    PlanningMMMUploadedCSVInputPlanReadinessTier,
    PlanningMMMUploadedCSVInputPlanResult,
    PlanningMMMUploadedCSVInputPlanStatus,
)
from mip.contracts.planning_mmm_uploaded_csv_workflow_readiness import (
    PlanningMMMUploadedCSVWorkflowReadinessIssueCode,
    PlanningMMMUploadedCSVWorkflowReadinessReport,
    PlanningMMMUploadedCSVWorkflowReadinessRequest,
    PlanningMMMUploadedCSVWorkflowReadinessResult,
    PlanningMMMUploadedCSVWorkflowReadinessStatus,
    PlanningMMMUploadedCSVWorkflowReadinessTier,
)

_BLOCKED_INPUT_PLAN_STATUSES = {
    PlanningMMMUploadedCSVInputPlanStatus.PLAN_BLOCKED_MISSING_ADAPTER_RESULT,
    PlanningMMMUploadedCSVInputPlanStatus.PLAN_BLOCKED_ADAPTER_NOT_READY,
    PlanningMMMUploadedCSVInputPlanStatus.PLAN_BLOCKED_MISSING_REQUIRED_INPUT,
    PlanningMMMUploadedCSVInputPlanStatus.PLAN_BLOCKED_MISSING_REQUIRED_COLUMNS,
}
_READY_INPUT_PLAN_STATUSES = {
    PlanningMMMUploadedCSVInputPlanStatus.PLAN_READY,
    PlanningMMMUploadedCSVInputPlanStatus.PLAN_READY_WITH_WARNINGS,
}
_EXECUTION_METADATA_FLAGS = (
    "model_execution_allowed",
    "optimizer_execution_allowed",
    "recommendation_generation_allowed",
    "decision_surface_execution_allowed",
    "claim_authorization_allowed",
    "bayesian_model_execution_allowed",
    "simulator_execution_allowed",
)
_DEFERRED_OBJECT_ISSUES: dict[str, PlanningMMMUploadedCSVWorkflowReadinessIssueCode] = {
    "IntakeManifest": PlanningMMMUploadedCSVWorkflowReadinessIssueCode.INTAKE_MANIFEST_DEFERRED,
    "MMMConfigDraft": PlanningMMMUploadedCSVWorkflowReadinessIssueCode.MMM_CONFIG_DRAFT_DEFERRED,
    "ModelCalibrationReadiness": (
        PlanningMMMUploadedCSVWorkflowReadinessIssueCode.MODEL_READINESS_DEFERRED
    ),
    "CalibrationSignalMapping": (
        PlanningMMMUploadedCSVWorkflowReadinessIssueCode.CALIBRATION_SIGNAL_MAPPING_DEFERRED
    ),
}


def evaluate_planning_mmm_workflow_readiness_from_uploaded_csv(
    request: PlanningMMMUploadedCSVWorkflowReadinessRequest,
) -> PlanningMMMUploadedCSVWorkflowReadinessResult:
    """Evaluate whether an uploaded CSV input plan can enter MMM workflow readiness."""
    lineage = {
        **request.lineage,
        "workflow_readiness_stage": "planning_mmm_uploaded_csv_workflow_readiness",
    }
    warnings = list(dict.fromkeys(request.warnings))
    issues: list[PlanningMMMUploadedCSVWorkflowReadinessIssueCode] = [
        PlanningMMMUploadedCSVWorkflowReadinessIssueCode.LINEAGE_PRESERVED,
        PlanningMMMUploadedCSVWorkflowReadinessIssueCode.NO_MODEL_EXECUTION,
        PlanningMMMUploadedCSVWorkflowReadinessIssueCode.NO_OPTIMIZER_EXECUTION,
        PlanningMMMUploadedCSVWorkflowReadinessIssueCode.NO_SIMULATOR_EXECUTION,
        PlanningMMMUploadedCSVWorkflowReadinessIssueCode.NO_RECOMMENDATION_GENERATED,
        PlanningMMMUploadedCSVWorkflowReadinessIssueCode.NO_DECISION_SURFACE_EXECUTION,
        PlanningMMMUploadedCSVWorkflowReadinessIssueCode.NO_CLAIM_AUTHORIZATION,
    ]

    if request.input_plan_result is None:
        return _blocked(
            request.request_id,
            PlanningMMMUploadedCSVWorkflowReadinessStatus.BLOCKED_MISSING_INPUT_PLAN_RESULT,
            PlanningMMMUploadedCSVWorkflowReadinessTier.BLOCKED,
            issues + [PlanningMMMUploadedCSVWorkflowReadinessIssueCode.MISSING_INPUT_PLAN_RESULT],
            warnings,
            lineage,
        )

    input_plan_result = request.input_plan_result
    warnings.extend(input_plan_result.warnings)
    lineage.update(input_plan_result.lineage)

    if input_plan_result.status == PlanningMMMUploadedCSVInputPlanStatus.PLAN_DIAGNOSTIC_ONLY:
        return _blocked(
            request.request_id,
            PlanningMMMUploadedCSVWorkflowReadinessStatus.DIAGNOSTIC_ONLY,
            PlanningMMMUploadedCSVWorkflowReadinessTier.DIAGNOSTIC_ONLY,
            issues + [PlanningMMMUploadedCSVWorkflowReadinessIssueCode.INPUT_PLAN_NOT_READY],
            warnings,
            lineage,
            input_plan_result=input_plan_result,
        )

    if input_plan_result.status in _BLOCKED_INPUT_PLAN_STATUSES:
        return _blocked(
            request.request_id,
            PlanningMMMUploadedCSVWorkflowReadinessStatus.BLOCKED_INPUT_PLAN_NOT_READY,
            PlanningMMMUploadedCSVWorkflowReadinessTier.BLOCKED,
            issues + [PlanningMMMUploadedCSVWorkflowReadinessIssueCode.INPUT_PLAN_NOT_READY],
            warnings,
            lineage,
            input_plan_result=input_plan_result,
        )

    plan = input_plan_result.plan
    if plan is None or input_plan_result.status not in _READY_INPUT_PLAN_STATUSES:
        return _blocked(
            request.request_id,
            PlanningMMMUploadedCSVWorkflowReadinessStatus.BLOCKED_INPUT_PLAN_NOT_READY,
            PlanningMMMUploadedCSVWorkflowReadinessTier.BLOCKED,
            issues + [PlanningMMMUploadedCSVWorkflowReadinessIssueCode.INPUT_PLAN_NOT_READY],
            warnings,
            lineage,
            input_plan_result=input_plan_result,
        )

    if plan.missing_required_inputs:
        return _blocked(
            request.request_id,
            PlanningMMMUploadedCSVWorkflowReadinessStatus.BLOCKED_MISSING_REQUIRED_INPUT,
            PlanningMMMUploadedCSVWorkflowReadinessTier.BLOCKED,
            issues + [PlanningMMMUploadedCSVWorkflowReadinessIssueCode.MISSING_REQUIRED_INPUT],
            warnings + [f"Missing required inputs: {', '.join(plan.missing_required_inputs)}"],
            lineage,
            input_plan_result=input_plan_result,
            plan=plan,
        )

    missing_required_columns = _missing_required_columns(plan)
    schema_level = _schema_validation_level(plan)
    if request.require_column_validated_schema and schema_level != "role_and_required_columns":
        return _blocked(
            request.request_id,
            PlanningMMMUploadedCSVWorkflowReadinessStatus.BLOCKED_MISSING_REQUIRED_COLUMNS,
            PlanningMMMUploadedCSVWorkflowReadinessTier.BLOCKED,
            issues + [PlanningMMMUploadedCSVWorkflowReadinessIssueCode.MISSING_REQUIRED_COLUMNS],
            warnings
            + [
                "Column-validated schema required but input plan schema validation is "
                f"{schema_level}"
            ],
            lineage,
            input_plan_result=input_plan_result,
            plan=plan,
            missing_required_columns=missing_required_columns,
        )

    if missing_required_columns:
        return _blocked(
            request.request_id,
            PlanningMMMUploadedCSVWorkflowReadinessStatus.BLOCKED_MISSING_REQUIRED_COLUMNS,
            PlanningMMMUploadedCSVWorkflowReadinessTier.BLOCKED,
            issues + [PlanningMMMUploadedCSVWorkflowReadinessIssueCode.MISSING_REQUIRED_COLUMNS],
            warnings
            + [f"Missing required columns: {', '.join(missing_required_columns)}"],
            lineage,
            input_plan_result=input_plan_result,
            plan=plan,
            missing_required_columns=missing_required_columns,
        )

    missing_optional = list(plan.missing_optional_inputs)
    if request.required_optional_inputs:
        required_optional_set = set(request.required_optional_inputs)
        missing_optional = [
            role for role in plan.missing_optional_inputs if role in required_optional_set
        ]
    elif request.require_optional_inputs:
        missing_optional = list(plan.missing_optional_inputs)

    if missing_optional and (request.require_optional_inputs or request.required_optional_inputs):
        return _blocked(
            request.request_id,
            PlanningMMMUploadedCSVWorkflowReadinessStatus.BLOCKED_MISSING_REQUIRED_INPUT,
            PlanningMMMUploadedCSVWorkflowReadinessTier.BLOCKED,
            issues + [PlanningMMMUploadedCSVWorkflowReadinessIssueCode.MISSING_REQUIRED_INPUT],
            warnings + [f"Missing required optional inputs: {', '.join(missing_optional)}"],
            lineage,
            input_plan_result=input_plan_result,
            plan=plan,
        )

    if not _execution_flags_safe(plan):
        return _blocked(
            request.request_id,
            PlanningMMMUploadedCSVWorkflowReadinessStatus.BLOCKED_EXECUTION_FLAGS_NOT_SAFE,
            PlanningMMMUploadedCSVWorkflowReadinessTier.BLOCKED,
            issues + [PlanningMMMUploadedCSVWorkflowReadinessIssueCode.EXECUTION_FLAGS_NOT_SAFE],
            warnings + ["Input plan readiness metadata contains unsafe execution flags"],
            lineage,
            input_plan_result=input_plan_result,
            plan=plan,
        )

    compatibility = _build_compatibility(plan)
    if compatibility["mmm_data_readiness_report_compatible"]:
        issues.append(
            PlanningMMMUploadedCSVWorkflowReadinessIssueCode.MMM_DATA_READINESS_COMPATIBLE
        )
    else:
        issues.append(
            PlanningMMMUploadedCSVWorkflowReadinessIssueCode.MMM_DATA_READINESS_COMPATIBILITY_DEFERRED
        )

    deferred_objects = dict(plan.deferred_objects)
    for key in deferred_objects:
        deferred_issue = _DEFERRED_OBJECT_ISSUES.get(key)
        if deferred_issue is not None:
            issues.append(deferred_issue)

    if plan.data_source_refs:
        issues.append(PlanningMMMUploadedCSVWorkflowReadinessIssueCode.DATA_SOURCE_REFS_AVAILABLE)

    if missing_optional:
        issues.append(PlanningMMMUploadedCSVWorkflowReadinessIssueCode.OPTIONAL_INPUT_MISSING)
        warnings.append(f"Optional inputs missing: {', '.join(missing_optional)}")

    has_warnings = bool(warnings) or bool(missing_optional)
    if has_warnings:
        status = PlanningMMMUploadedCSVWorkflowReadinessStatus.READY_WITH_WARNINGS
        tier = PlanningMMMUploadedCSVWorkflowReadinessTier.READY_FOR_GATED_WORKFLOW_WITH_WARNINGS
    else:
        status = PlanningMMMUploadedCSVWorkflowReadinessStatus.READY_FOR_MMM_WORKFLOW_READINESS
        tier = PlanningMMMUploadedCSVWorkflowReadinessTier.READY_FOR_GATED_WORKFLOW

    issues.append(
        PlanningMMMUploadedCSVWorkflowReadinessIssueCode.WORKFLOW_READINESS_METADATA_CREATED
    )

    report = PlanningMMMUploadedCSVWorkflowReadinessReport(
        report_id=f"planning-mmm-workflow-readiness:{request.request_id}",
        status=status,
        tier=tier,
        input_plan_id=plan.plan_id,
        data_source_refs=list(plan.data_source_refs),
        readiness_metadata=_build_readiness_metadata(plan, schema_level),
        missing_required_inputs=list(plan.missing_required_inputs),
        missing_optional_inputs=list(plan.missing_optional_inputs),
        missing_required_columns=missing_required_columns,
        deferred_objects=deferred_objects,
        compatibility=compatibility,
        execution_allowed=_default_execution_allowed(),
        issues=_dedupe_issues(issues),
        warnings=list(dict.fromkeys(warnings)),
        lineage={
            **lineage,
            "input_plan_request_id": input_plan_result.request_id,
            "schema_validation_level": schema_level,
        },
    )

    return PlanningMMMUploadedCSVWorkflowReadinessResult(
        request_id=request.request_id,
        status=status,
        report=report,
        issues=_dedupe_issues(issues),
        warnings=list(dict.fromkeys(warnings)),
        lineage=lineage,
    )


def summarize_planning_mmm_uploaded_csv_workflow_readiness(
    result: PlanningMMMUploadedCSVWorkflowReadinessResult,
) -> dict[str, str | list[str] | dict[str, bool]]:
    """Produce a metadata-only summary of uploaded CSV workflow readiness."""
    report = result.report
    if report is None:
        return {
            "status": str(result.status),
            "tier": "blocked",
            "missing_required_inputs": [],
            "missing_optional_inputs": [],
            "missing_required_columns": [],
            "deferred_objects": [],
            "compatibility": {},
            "execution_allowed": _default_execution_allowed(),
        }

    return {
        "status": str(result.status),
        "tier": str(report.tier),
        "missing_required_inputs": list(report.missing_required_inputs),
        "missing_optional_inputs": list(report.missing_optional_inputs),
        "missing_required_columns": list(report.missing_required_columns),
        "deferred_objects": list(report.deferred_objects.keys()),
        "compatibility": dict(report.compatibility),
        "execution_allowed": dict(report.execution_allowed),
    }


def _blocked(
    request_id: str,
    status: PlanningMMMUploadedCSVWorkflowReadinessStatus,
    tier: PlanningMMMUploadedCSVWorkflowReadinessTier,
    issues: list[PlanningMMMUploadedCSVWorkflowReadinessIssueCode],
    warnings: list[str],
    lineage: dict[str, str],
    *,
    input_plan_result: PlanningMMMUploadedCSVInputPlanResult | None = None,
    plan: PlanningMMMUploadedCSVInputPlan | None = None,
    missing_required_columns: list[str] | None = None,
) -> PlanningMMMUploadedCSVWorkflowReadinessResult:
    report: PlanningMMMUploadedCSVWorkflowReadinessReport | None = None
    if plan is not None:
        schema_level = _schema_validation_level(plan)
        report = PlanningMMMUploadedCSVWorkflowReadinessReport(
            report_id=f"planning-mmm-workflow-readiness:{request_id}",
            status=status,
            tier=tier,
            input_plan_id=plan.plan_id,
            data_source_refs=list(plan.data_source_refs),
            readiness_metadata=_build_readiness_metadata(plan, schema_level),
            missing_required_inputs=list(plan.missing_required_inputs),
            missing_optional_inputs=list(plan.missing_optional_inputs),
            missing_required_columns=missing_required_columns or _missing_required_columns(plan),
            deferred_objects=dict(plan.deferred_objects),
            compatibility=_build_compatibility(plan),
            execution_allowed=_default_execution_allowed(),
            issues=_dedupe_issues(issues),
            warnings=list(dict.fromkeys(warnings)),
            lineage={
                **lineage,
                "input_plan_request_id": (
                    input_plan_result.request_id if input_plan_result else ""
                ),
                "schema_validation_level": schema_level,
            },
        )
    return PlanningMMMUploadedCSVWorkflowReadinessResult(
        request_id=request_id,
        status=status,
        report=report,
        issues=_dedupe_issues(issues),
        warnings=list(dict.fromkeys(warnings)),
        lineage=lineage,
    )


def _schema_validation_level(plan: PlanningMMMUploadedCSVInputPlan) -> str:
    metadata_level = plan.readiness_metadata.get("schema_validation_level")
    if isinstance(metadata_level, str) and metadata_level:
        return metadata_level
    lineage_level = plan.lineage.get("schema_validation_level")
    if isinstance(lineage_level, str) and lineage_level:
        return lineage_level
    return "role_presence_only"


def _missing_required_columns(plan: PlanningMMMUploadedCSVInputPlan) -> list[str]:
    missing: list[str] = []
    for requirement in plan.requirements:
        if requirement.required and requirement.missing_columns:
            missing.extend(
                f"{requirement.role}:{column}" for column in requirement.missing_columns
            )
    return list(dict.fromkeys(missing))


def _execution_flags_safe(plan: PlanningMMMUploadedCSVInputPlan) -> bool:
    metadata = plan.readiness_metadata
    for flag in _EXECUTION_METADATA_FLAGS:
        if bool(metadata.get(flag, False)):
            return False
    return True


def _build_compatibility(plan: PlanningMMMUploadedCSVInputPlan) -> dict[str, bool]:
    metadata = plan.readiness_metadata
    has_required_data = bool(metadata.get("has_historical_spend")) and bool(
        metadata.get("has_historical_outcome")
    )
    mmm_compatible = (
        has_required_data
        and plan.readiness_tier
        in {
            PlanningMMMUploadedCSVInputPlanReadinessTier.READY_FOR_WORKFLOW_READINESS,
            PlanningMMMUploadedCSVInputPlanReadinessTier.READY_WITH_OPTIONAL_GAPS,
        }
    )
    return {
        "uploaded_csv_input_plan_compatible": True,
        "mmm_data_readiness_report_compatible": mmm_compatible,
        "intake_manifest_construction_ready": False,
        "mmm_config_draft_construction_ready": False,
        "model_calibration_readiness_ready": False,
        "calibration_signal_mapping_ready": False,
    }


def _build_readiness_metadata(
    plan: PlanningMMMUploadedCSVInputPlan,
    schema_level: str,
) -> dict[str, str | bool]:
    metadata = dict(plan.readiness_metadata)
    metadata.setdefault("schema_validation_level", schema_level)
    metadata.setdefault("optional_gaps_present", bool(plan.missing_optional_inputs))
    return metadata


def _default_execution_allowed() -> dict[str, bool]:
    return {
        "model_execution": False,
        "bayesian_model_execution": False,
        "optimizer_execution": False,
        "simulator_execution": False,
        "decision_surface_execution": False,
        "recommendation_generation": False,
        "claim_authorization": False,
    }


def _dedupe_issues(
    issues: list[PlanningMMMUploadedCSVWorkflowReadinessIssueCode],
) -> list[PlanningMMMUploadedCSVWorkflowReadinessIssueCode]:
    seen: set[PlanningMMMUploadedCSVWorkflowReadinessIssueCode] = set()
    ordered: list[PlanningMMMUploadedCSVWorkflowReadinessIssueCode] = []
    for issue in issues:
        if issue not in seen:
            seen.add(issue)
            ordered.append(issue)
    return ordered
