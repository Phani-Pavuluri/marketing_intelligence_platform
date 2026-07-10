"""Planning/MMM uploaded CSV input plan workflow.

Converts Planning/MMM uploaded CSV adapter output into a governed input plan
and readiness metadata. Does not fit models, optimize budgets, or execute workflows.
"""

from __future__ import annotations

from mip.contracts.planning_mmm_uploaded_csv_adapter import (
    PlanningMMMUploadedCSVAdapterResult,
    PlanningMMMUploadedCSVAdapterStatus,
    PlanningMMMUploadedCSVRole,
)
from mip.contracts.planning_mmm_uploaded_csv_input_plan import (
    PlanningMMMUploadedCSVInputPlan,
    PlanningMMMUploadedCSVInputPlanIssueCode,
    PlanningMMMUploadedCSVInputPlanReadinessTier,
    PlanningMMMUploadedCSVInputPlanRequest,
    PlanningMMMUploadedCSVInputPlanResult,
    PlanningMMMUploadedCSVInputPlanStatus,
    PlanningMMMUploadedCSVInputRequirement,
)

_READY_ADAPTER_STATUSES = {
    PlanningMMMUploadedCSVAdapterStatus.ADAPTED,
    PlanningMMMUploadedCSVAdapterStatus.ADAPTED_WITH_WARNINGS,
}
_DEFAULT_REQUIRED_ROLES = {
    PlanningMMMUploadedCSVRole.HISTORICAL_SPEND,
    PlanningMMMUploadedCSVRole.HISTORICAL_OUTCOME,
}
_OPTIONAL_ROLES = {
    PlanningMMMUploadedCSVRole.CHANNEL_TAXONOMY,
    PlanningMMMUploadedCSVRole.BUDGET_CONSTRAINTS,
    PlanningMMMUploadedCSVRole.CALIBRATION_SIGNALS,
    PlanningMMMUploadedCSVRole.MODEL_CONFIG,
}
_ROLE_REQUIRE_FLAG: dict[PlanningMMMUploadedCSVRole, str] = {
    PlanningMMMUploadedCSVRole.CHANNEL_TAXONOMY: "require_channel_taxonomy",
    PlanningMMMUploadedCSVRole.BUDGET_CONSTRAINTS: "require_budget_constraints",
    PlanningMMMUploadedCSVRole.CALIBRATION_SIGNALS: "require_calibration_signals",
    PlanningMMMUploadedCSVRole.MODEL_CONFIG: "require_model_config",
}
_DEFERRED_OBJECTS: dict[str, str] = {
    "IntakeManifest": "deferred until session/workflow context exists",
    "MMMConfigDraft": "deferred until model specification context exists",
    "ModelCalibrationReadiness": "deferred until calibration/model candidate context exists",
    "CalibrationSignalMapping": "deferred until calibration source semantics are confirmed",
}


def build_planning_mmm_uploaded_csv_input_plan(
    request: PlanningMMMUploadedCSVInputPlanRequest,
) -> PlanningMMMUploadedCSVInputPlanResult:
    """Build a governed Planning/MMM input plan from uploaded CSV adapter output."""
    lineage = {
        **request.lineage,
        "input_plan_stage": "planning_mmm_uploaded_csv_input_plan",
    }
    warnings = list(dict.fromkeys(request.warnings))
    issues: list[PlanningMMMUploadedCSVInputPlanIssueCode] = [
        PlanningMMMUploadedCSVInputPlanIssueCode.LINEAGE_PRESERVED,
        PlanningMMMUploadedCSVInputPlanIssueCode.NO_MODEL_EXECUTION,
        PlanningMMMUploadedCSVInputPlanIssueCode.NO_OPTIMIZER_EXECUTION,
        PlanningMMMUploadedCSVInputPlanIssueCode.NO_RECOMMENDATION_GENERATED,
    ]

    if request.adapter_result is None:
        return _blocked(
            request.request_id,
            PlanningMMMUploadedCSVInputPlanStatus.PLAN_BLOCKED_MISSING_ADAPTER_RESULT,
            issues + [PlanningMMMUploadedCSVInputPlanIssueCode.MISSING_ADAPTER_RESULT],
            warnings,
            lineage,
        )

    adapter = request.adapter_result
    warnings.extend(adapter.warnings)
    lineage.update(adapter.lineage)

    if adapter.status not in _READY_ADAPTER_STATUSES:
        return _blocked(
            request.request_id,
            PlanningMMMUploadedCSVInputPlanStatus.PLAN_BLOCKED_ADAPTER_NOT_READY,
            issues + [PlanningMMMUploadedCSVInputPlanIssueCode.ADAPTER_NOT_READY],
            warnings,
            lineage,
        )

    required_roles = _required_roles_for_request(request)
    optional_roles = _OPTIONAL_ROLES - required_roles
    mapping_by_role = {mapping.role: mapping for mapping in adapter.role_mappings}
    schema_level = (
        "role_and_required_columns"
        if request.required_columns_by_role
        else "role_presence_only"
    )

    requirements: list[PlanningMMMUploadedCSVInputRequirement] = []
    missing_required: list[str] = []
    missing_optional: list[str] = []
    required_present: list[str] = []
    optional_present: list[str] = []

    for role in sorted(required_roles | optional_roles, key=str):
        is_required = role in required_roles
        mapping = mapping_by_role.get(role)
        required_columns = list(request.required_columns_by_role.get(str(role), []))
        missing_columns: list[str] = []
        if mapping is not None and required_columns:
            missing_columns = [
                column
                for column in required_columns
                if column not in mapping.normalized_columns
            ]

        requirement = PlanningMMMUploadedCSVInputRequirement(
            role=role,
            required=is_required,
            required_columns=required_columns,
            available=mapping is not None,
            source_id=mapping.source_id if mapping else None,
            data_source_ref=mapping.data_source_ref if mapping else None,
            missing_columns=missing_columns,
            lineage={
                **(mapping.lineage if mapping else {}),
                "role": str(role),
                "required": str(is_required).lower(),
            },
        )
        requirements.append(requirement)

        if mapping is None:
            if is_required:
                missing_required.append(str(role))
            else:
                missing_optional.append(str(role))
                warnings.append(f"Optional Planning/MMM input not provided: {role}")
                issues.append(PlanningMMMUploadedCSVInputPlanIssueCode.OPTIONAL_INPUT_MISSING)
        elif is_required:
            required_present.append(str(role))
            if missing_columns:
                return _blocked(
                    request.request_id,
                    PlanningMMMUploadedCSVInputPlanStatus.PLAN_BLOCKED_MISSING_REQUIRED_COLUMNS,
                    issues + [PlanningMMMUploadedCSVInputPlanIssueCode.MISSING_REQUIRED_COLUMNS],
                    warnings + [
                        f"Missing required columns for {role}: "
                        + ", ".join(missing_columns)
                    ],
                    lineage,
                )
        else:
            optional_present.append(str(role))

    if missing_required:
        return _blocked(
            request.request_id,
            PlanningMMMUploadedCSVInputPlanStatus.PLAN_BLOCKED_MISSING_REQUIRED_INPUT,
            issues + [PlanningMMMUploadedCSVInputPlanIssueCode.MISSING_REQUIRED_INPUT],
            warnings + [f"Missing required inputs: {', '.join(missing_required)}"],
            lineage,
        )

    data_source_refs = list(adapter.data_source_refs)
    if data_source_refs:
        issues.append(PlanningMMMUploadedCSVInputPlanIssueCode.DATA_SOURCE_REF_INCLUDED)

    deferred_objects = dict(_DEFERRED_OBJECTS)
    issues.extend(
        [
            PlanningMMMUploadedCSVInputPlanIssueCode.INTAKE_MANIFEST_DEFERRED,
            PlanningMMMUploadedCSVInputPlanIssueCode.MMM_CONFIG_DRAFT_DEFERRED,
            PlanningMMMUploadedCSVInputPlanIssueCode.MODEL_READINESS_DEFERRED,
            PlanningMMMUploadedCSVInputPlanIssueCode.CALIBRATION_SIGNAL_MAPPING_DEFERRED,
        ]
    )

    readiness_metadata = _build_readiness_metadata(
        adapter=adapter,
        schema_level=schema_level,
        missing_optional=missing_optional,
    )
    issues.append(PlanningMMMUploadedCSVInputPlanIssueCode.READINESS_METADATA_CREATED)

    if missing_optional:
        readiness_tier = PlanningMMMUploadedCSVInputPlanReadinessTier.READY_WITH_OPTIONAL_GAPS
        status = PlanningMMMUploadedCSVInputPlanStatus.PLAN_READY_WITH_WARNINGS
    else:
        readiness_tier = PlanningMMMUploadedCSVInputPlanReadinessTier.READY_FOR_WORKFLOW_READINESS
        status = PlanningMMMUploadedCSVInputPlanStatus.PLAN_READY

    plan = PlanningMMMUploadedCSVInputPlan(
        plan_id=f"planning-mmm-input-plan:{request.request_id}",
        readiness_tier=readiness_tier,
        requirements=requirements,
        data_source_refs=data_source_refs,
        required_inputs_present=required_present,
        optional_inputs_present=optional_present,
        missing_required_inputs=missing_required,
        missing_optional_inputs=missing_optional,
        deferred_objects=deferred_objects,
        readiness_metadata=readiness_metadata,
        lineage={
            **lineage,
            "schema_validation_level": schema_level,
            "adapter_request_id": adapter.request_id,
        },
        warnings=list(dict.fromkeys(warnings)),
        issues=_dedupe_issues(issues),
    )

    return PlanningMMMUploadedCSVInputPlanResult(
        request_id=request.request_id,
        status=status,
        plan=plan,
        issues=_dedupe_issues(issues),
        warnings=list(dict.fromkeys(warnings)),
        lineage=lineage,
    )


def summarize_planning_mmm_uploaded_csv_input_plan(
    result: PlanningMMMUploadedCSVInputPlanResult,
) -> dict[str, str | list[str] | bool]:
    """Produce a metadata-only summary of a Planning/MMM uploaded CSV input plan."""
    plan = result.plan
    if plan is None:
        return {
            "status": str(result.status),
            "readiness_tier": "blocked",
            "missing_required_inputs": [],
            "missing_optional_inputs": [],
            "deferred_objects": list(_DEFERRED_OBJECTS.keys()),
            "model_execution_allowed": False,
            "optimizer_execution_allowed": False,
            "recommendation_generation_allowed": False,
            "decision_surface_execution_allowed": False,
            "claim_authorization_allowed": False,
        }

    metadata = plan.readiness_metadata
    return {
        "status": str(result.status),
        "readiness_tier": str(plan.readiness_tier),
        "missing_required_inputs": list(plan.missing_required_inputs),
        "missing_optional_inputs": list(plan.missing_optional_inputs),
        "deferred_objects": list(plan.deferred_objects.keys()),
        "schema_validation_level": str(metadata.get("schema_validation_level", "")),
        "model_execution_allowed": bool(metadata.get("model_execution_allowed", False)),
        "optimizer_execution_allowed": bool(metadata.get("optimizer_execution_allowed", False)),
        "recommendation_generation_allowed": bool(
            metadata.get("recommendation_generation_allowed", False)
        ),
        "decision_surface_execution_allowed": bool(
            metadata.get("decision_surface_execution_allowed", False)
        ),
        "claim_authorization_allowed": bool(metadata.get("claim_authorization_allowed", False)),
    }


def _required_roles_for_request(
    request: PlanningMMMUploadedCSVInputPlanRequest,
) -> set[PlanningMMMUploadedCSVRole]:
    required = set(_DEFAULT_REQUIRED_ROLES)
    for role, flag_name in _ROLE_REQUIRE_FLAG.items():
        if getattr(request, flag_name):
            required.add(role)
    return required


def _build_readiness_metadata(
    *,
    adapter: PlanningMMMUploadedCSVAdapterResult,
    schema_level: str,
    missing_optional: list[str],
) -> dict[str, str | bool]:
    availability = adapter.availability
    return {
        "has_historical_spend": availability.has_historical_spend if availability else False,
        "has_historical_outcome": availability.has_historical_outcome if availability else False,
        "has_channel_taxonomy": availability.has_channel_taxonomy if availability else False,
        "has_budget_constraints": availability.has_budget_constraints if availability else False,
        "has_calibration_signals": availability.has_calibration_signals if availability else False,
        "has_model_config": availability.has_model_config if availability else False,
        "schema_validation_level": schema_level,
        "optional_gaps_present": bool(missing_optional),
        "model_execution_allowed": False,
        "optimizer_execution_allowed": False,
        "recommendation_generation_allowed": False,
        "decision_surface_execution_allowed": False,
        "claim_authorization_allowed": False,
    }


def _blocked(
    request_id: str,
    status: PlanningMMMUploadedCSVInputPlanStatus,
    issues: list[PlanningMMMUploadedCSVInputPlanIssueCode],
    warnings: list[str],
    lineage: dict[str, str],
) -> PlanningMMMUploadedCSVInputPlanResult:
    return PlanningMMMUploadedCSVInputPlanResult(
        request_id=request_id,
        status=status,
        issues=_dedupe_issues(issues),
        warnings=list(dict.fromkeys(warnings)),
        lineage=lineage,
    )


def _dedupe_issues(
    issues: list[PlanningMMMUploadedCSVInputPlanIssueCode],
) -> list[PlanningMMMUploadedCSVInputPlanIssueCode]:
    seen: set[PlanningMMMUploadedCSVInputPlanIssueCode] = set()
    ordered: list[PlanningMMMUploadedCSVInputPlanIssueCode] = []
    for issue in issues:
        if issue not in seen:
            seen.add(issue)
            ordered.append(issue)
    return ordered
