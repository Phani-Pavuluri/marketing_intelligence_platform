"""Planning/MMM trusted input package and model-run eligibility workflow."""

from __future__ import annotations

from mip.contracts.mmm_existing_model_availability import MMMExistingModelAvailabilityStatus
from mip.contracts.planning_mmm_calibration_signal_mapping_readiness import (
    PlanningMMMCalibrationSignalMappingReadinessResult,
    PlanningMMMCalibrationSignalReadinessStatus,
)
from mip.contracts.planning_mmm_readiness_report_adapter import (
    PlanningMMMReadinessReportAdapterResult,
    PlanningMMMReadinessReportAdapterStatus,
)
from mip.contracts.planning_mmm_trusted_input_model_run_eligibility import (
    PlanningMMMModelRunEligibilityDecision,
    PlanningMMMModelRunEligibilityIssueCode,
    PlanningMMMModelRunEligibilityRequest,
    PlanningMMMModelRunEligibilityResult,
    PlanningMMMModelRunEligibilityStatus,
    PlanningMMMTrustedInputComponentStatus,
    PlanningMMMTrustedInputPackage,
    PlanningMMMTrustedInputStatus,
)

_READY_DATA_STATUSES = {
    PlanningMMMReadinessReportAdapterStatus.REPORT_ADAPTED,
    PlanningMMMReadinessReportAdapterStatus.REPORT_ADAPTED_WITH_WARNINGS,
}
_BLOCKED_DATA_STATUSES = {
    PlanningMMMReadinessReportAdapterStatus.BLOCKED_MISSING_WORKFLOW_READINESS_RESULT,
    PlanningMMMReadinessReportAdapterStatus.BLOCKED_WORKFLOW_READINESS_NOT_READY,
    PlanningMMMReadinessReportAdapterStatus.BLOCKED_MISSING_REQUIRED_INPUT,
    PlanningMMMReadinessReportAdapterStatus.BLOCKED_MISSING_REQUIRED_COLUMNS,
    PlanningMMMReadinessReportAdapterStatus.BLOCKED_MMM_DATA_READINESS_CONTRACT_UNAVAILABLE,
}
_USABLE_EXISTING_MODEL_STATUSES = {
    MMMExistingModelAvailabilityStatus.USABLE_EXISTING_MODEL,
    MMMExistingModelAvailabilityStatus.USABLE_EXISTING_MODEL_WITH_WARNINGS,
}
_REFRESH_EXISTING_MODEL_STATUSES = {
    MMMExistingModelAvailabilityStatus.REQUIRES_MODEL_REFRESH,
}
_NEW_RUN_EXISTING_MODEL_STATUSES = {
    MMMExistingModelAvailabilityStatus.REQUIRES_NEW_MODEL_RUN,
    MMMExistingModelAvailabilityStatus.BLOCKED_NO_CANDIDATE_MODEL,
}

_BOUNDARY_ISSUES = (
    PlanningMMMModelRunEligibilityIssueCode.NO_MODEL_EXECUTION,
    PlanningMMMModelRunEligibilityIssueCode.NO_MODEL_ARTIFACT_LOADING,
    PlanningMMMModelRunEligibilityIssueCode.NO_PRIOR_APPLICATION,
    PlanningMMMModelRunEligibilityIssueCode.NO_LIKELIHOOD_CONSTRUCTION,
    PlanningMMMModelRunEligibilityIssueCode.NO_POSTERIOR_CALCULATION,
    PlanningMMMModelRunEligibilityIssueCode.NO_OPTIMIZER_EXECUTION,
    PlanningMMMModelRunEligibilityIssueCode.NO_SIMULATOR_EXECUTION,
    PlanningMMMModelRunEligibilityIssueCode.NO_RECOMMENDATION_GENERATED,
    PlanningMMMModelRunEligibilityIssueCode.NO_DECISION_SURFACE_EXECUTION,
    PlanningMMMModelRunEligibilityIssueCode.NO_TRUST_REPORT_CONSTRUCTION,
    PlanningMMMModelRunEligibilityIssueCode.NO_CLAIM_AUTHORIZATION,
)


def evaluate_planning_mmm_trusted_input_and_model_run_eligibility(
    request: PlanningMMMModelRunEligibilityRequest,
) -> PlanningMMMModelRunEligibilityResult:
    """Evaluate trusted input package and model-run eligibility for Planning/MMM."""
    lineage = {
        **request.lineage,
        "eligibility_stage": "planning_mmm_trusted_input_model_run_eligibility",
    }
    warnings: list[str] = []
    issues: list[PlanningMMMModelRunEligibilityIssueCode] = list(_BOUNDARY_ISSUES)

    data_ok, data_warnings, data_blocked, data_issues, data_components = _evaluate_data_readiness(
        request.data_readiness_result
    )
    warnings.extend(data_warnings)
    issues.extend(data_issues)

    calibration_ok, calibration_warnings, calibration_blocked, calibration_issues = (
        _evaluate_calibration_readiness(
            request.calibration_readiness_result,
            require_calibration_readiness=request.require_calibration_readiness,
            allow_diagnostic_only_calibration=request.allow_diagnostic_only_calibration,
        )
    )
    warnings.extend(calibration_warnings)
    issues.extend(calibration_issues)

    existing_usable = False
    existing_refresh = False
    existing_new_run = False
    if request.existing_model_availability_result is not None:
        issues.append(PlanningMMMModelRunEligibilityIssueCode.EXISTING_MODEL_AVAILABILITY_PRESENT)
        existing_usable, existing_refresh, existing_new_run, existing_issues, existing_warnings = (
            _evaluate_existing_model_availability(request.existing_model_availability_result)
        )
        issues.extend(existing_issues)
        warnings.extend(existing_warnings)

    if request.model_config_present:
        issues.append(PlanningMMMModelRunEligibilityIssueCode.MODEL_CONFIG_PRESENT)
    elif request.model_config_id:
        issues.append(PlanningMMMModelRunEligibilityIssueCode.MODEL_CONFIG_PRESENT)

    package = _build_trusted_input_package(
        request=request,
        data_components=data_components,
        warnings=warnings,
        issues=issues,
        lineage=lineage,
    )
    issues.append(PlanningMMMModelRunEligibilityIssueCode.TRUSTED_INPUT_PACKAGE_CREATED)

    if not request.data_readiness_result:
        return _blocked(
            request=request,
            trusted_input_status=PlanningMMMTrustedInputStatus.TRUSTED_INPUT_BLOCKED,
            eligibility_status=PlanningMMMModelRunEligibilityStatus.BLOCKED_MISSING_REQUIRED_DATA,
            decision=PlanningMMMModelRunEligibilityDecision.BLOCK,
            package=package,
            blocked_reasons=["data readiness result is missing"],
            warnings=warnings,
            issues=issues + [PlanningMMMModelRunEligibilityIssueCode.DATA_READINESS_MISSING],
            lineage=lineage,
        )

    if data_blocked:
        return _blocked(
            request=request,
            trusted_input_status=PlanningMMMTrustedInputStatus.TRUSTED_INPUT_BLOCKED,
            eligibility_status=PlanningMMMModelRunEligibilityStatus.BLOCKED_DATA_READINESS_FAILED,
            decision=PlanningMMMModelRunEligibilityDecision.BLOCK,
            package=package,
            blocked_reasons=["data readiness evaluation failed"],
            warnings=warnings,
            issues=issues,
            lineage=lineage,
        )

    if not data_ok:
        return _blocked(
            request=request,
            trusted_input_status=PlanningMMMTrustedInputStatus.TRUSTED_INPUT_BLOCKED,
            eligibility_status=PlanningMMMModelRunEligibilityStatus.BLOCKED_DATA_READINESS_FAILED,
            decision=PlanningMMMModelRunEligibilityDecision.BLOCK,
            package=package,
            blocked_reasons=["required historical spend or outcome data is missing"],
            warnings=warnings,
            issues=issues,
            lineage=lineage,
        )

    if request.require_calibration_readiness and request.calibration_readiness_result is None:
        return _blocked(
            request=request,
            trusted_input_status=PlanningMMMTrustedInputStatus.TRUSTED_INPUT_BLOCKED,
            eligibility_status=PlanningMMMModelRunEligibilityStatus.BLOCKED_CALIBRATION_READINESS_FAILED,
            decision=PlanningMMMModelRunEligibilityDecision.BLOCK,
            package=package,
            blocked_reasons=["calibration readiness is required but missing"],
            warnings=warnings,
            issues=issues,
            lineage=lineage,
        )

    if calibration_blocked:
        return _blocked(
            request=request,
            trusted_input_status=PlanningMMMTrustedInputStatus.TRUSTED_INPUT_BLOCKED,
            eligibility_status=PlanningMMMModelRunEligibilityStatus.BLOCKED_CALIBRATION_READINESS_FAILED,
            decision=PlanningMMMModelRunEligibilityDecision.BLOCK,
            package=package,
            blocked_reasons=["calibration readiness evaluation blocked"],
            warnings=warnings,
            issues=issues,
            lineage=lineage,
        )

    if warnings and request.require_human_review_for_warnings:
        issues.append(PlanningMMMModelRunEligibilityIssueCode.HUMAN_REVIEW_REQUIRED)
        return _blocked(
            request=request,
            trusted_input_status=PlanningMMMTrustedInputStatus.TRUSTED_INPUT_READY_WITH_WARNINGS,
            eligibility_status=PlanningMMMModelRunEligibilityStatus.BLOCKED_GOVERNANCE_REVIEW_REQUIRED,
            decision=PlanningMMMModelRunEligibilityDecision.BLOCK,
            package=package,
            blocked_reasons=["human review required for warnings before model-run action"],
            warnings=warnings,
            issues=issues,
            lineage=lineage,
            human_review_required=True,
        )

    effective_existing_usable = existing_usable and request.allow_existing_model_reuse

    if (
        request.allow_existing_model_reuse
        and existing_usable
        and request.existing_model_availability_result is not None
    ):
        trusted_status = (
            PlanningMMMTrustedInputStatus.TRUSTED_INPUT_READY_WITH_WARNINGS
            if warnings
            else PlanningMMMTrustedInputStatus.TRUSTED_INPUT_READY
        )
        eligibility = (
            PlanningMMMModelRunEligibilityStatus.USE_EXISTING_MODEL
            if not warnings
            else PlanningMMMModelRunEligibilityStatus.ELIGIBLE_TO_REQUEST_MODEL_RUN_WITH_WARNINGS
        )
        return _result(
            request=request,
            trusted_input_status=trusted_status,
            eligibility_status=eligibility,
            decision=PlanningMMMModelRunEligibilityDecision.USE_EXISTING_MODEL,
            package=package,
            eligible_to_request_model_run=False,
            use_existing_model=True,
            warnings=warnings,
            issues=issues
            + [PlanningMMMModelRunEligibilityIssueCode.MODEL_RUN_ELIGIBILITY_EVALUATED],
            lineage=lineage,
        )

    if request.allow_existing_model_reuse and existing_refresh:
        if not request.model_config_present and not request.model_config_id:
            return _blocked(
                request=request,
                trusted_input_status=PlanningMMMTrustedInputStatus.TRUSTED_INPUT_READY_WITH_WARNINGS,
                eligibility_status=PlanningMMMModelRunEligibilityStatus.BLOCKED_MISSING_MODEL_CONFIG,
                decision=PlanningMMMModelRunEligibilityDecision.BLOCK,
                package=package,
                blocked_reasons=["model config required for model refresh request"],
                warnings=warnings,
                issues=issues,
                lineage=lineage,
            )
        return _result(
            request=request,
            trusted_input_status=PlanningMMMTrustedInputStatus.TRUSTED_INPUT_READY_WITH_WARNINGS,
            eligibility_status=PlanningMMMModelRunEligibilityStatus.REQUIRES_MODEL_REFRESH,
            decision=PlanningMMMModelRunEligibilityDecision.REQUEST_MODEL_REFRESH,
            package=package,
            requires_model_refresh=True,
            warnings=warnings,
            issues=issues
            + [PlanningMMMModelRunEligibilityIssueCode.MODEL_RUN_ELIGIBILITY_EVALUATED],
            lineage=lineage,
        )

    needs_new_run = (
        existing_new_run
        or request.existing_model_availability_result is None
        or not effective_existing_usable
    )
    if needs_new_run:
        if not request.model_config_present and not request.model_config_id:
            return _blocked(
                request=request,
                trusted_input_status=PlanningMMMTrustedInputStatus.TRUSTED_INPUT_READY_WITH_WARNINGS,
                eligibility_status=PlanningMMMModelRunEligibilityStatus.BLOCKED_MISSING_MODEL_CONFIG,
                decision=PlanningMMMModelRunEligibilityDecision.BLOCK,
                package=package,
                blocked_reasons=["model config required to request a new MMM model run"],
                warnings=warnings,
                issues=issues + [PlanningMMMModelRunEligibilityIssueCode.MODEL_CONFIG_MISSING],
                lineage=lineage,
            )

        if not calibration_ok and request.calibration_readiness_result is not None:
            warnings.append("calibration readiness not fully ready; proceeding with warnings")

        trusted_status = (
            PlanningMMMTrustedInputStatus.TRUSTED_INPUT_READY_WITH_WARNINGS
            if warnings
            else PlanningMMMTrustedInputStatus.TRUSTED_INPUT_READY
        )
        eligibility = (
            PlanningMMMModelRunEligibilityStatus.ELIGIBLE_TO_REQUEST_MODEL_RUN_WITH_WARNINGS
            if warnings
            else PlanningMMMModelRunEligibilityStatus.ELIGIBLE_TO_REQUEST_MODEL_RUN
        )
        return _result(
            request=request,
            trusted_input_status=trusted_status,
            eligibility_status=eligibility,
            decision=PlanningMMMModelRunEligibilityDecision.REQUEST_NEW_MODEL_RUN,
            package=package,
            eligible_to_request_model_run=True,
            requires_new_model_run=True,
            warnings=warnings,
            issues=issues
            + [
                PlanningMMMModelRunEligibilityIssueCode.NEW_MODEL_RUN_REQUIRED,
                PlanningMMMModelRunEligibilityIssueCode.MODEL_RUN_ELIGIBILITY_EVALUATED,
            ],
            lineage=lineage,
        )

    if (
        not request.allow_existing_model_reuse
        and existing_usable
        and request.existing_model_availability_result is not None
    ):
        issues.append(PlanningMMMModelRunEligibilityIssueCode.EXISTING_MODEL_NOT_USABLE)

    return _result(
        request=request,
        trusted_input_status=PlanningMMMTrustedInputStatus.TRUSTED_INPUT_DEFERRED,
        eligibility_status=PlanningMMMModelRunEligibilityStatus.DEFERRED,
        decision=PlanningMMMModelRunEligibilityDecision.DEFER,
        package=package,
        blocked_reasons=["model-run eligibility could not be resolved from available metadata"],
        warnings=warnings,
        issues=issues + [PlanningMMMModelRunEligibilityIssueCode.MODEL_RUN_ELIGIBILITY_EVALUATED],
        lineage=lineage,
    )


def summarize_planning_mmm_model_run_eligibility(
    result: PlanningMMMModelRunEligibilityResult,
) -> dict[str, str | bool | list[str]]:
    """Return metadata-only summary of model-run eligibility evaluation."""
    return {
        "request_id": result.request_id,
        "trusted_input_status": _enum_value(result.trusted_input_status),
        "eligibility_status": _enum_value(result.eligibility_status),
        "decision": _enum_value(result.decision),
        "eligible_to_request_model_run": result.eligible_to_request_model_run,
        "use_existing_model": result.use_existing_model,
        "requires_model_refresh": result.requires_model_refresh,
        "requires_new_model_run": result.requires_new_model_run,
        "human_review_required": result.human_review_required,
        "blocked_reasons": list(result.blocked_reasons),
        "warnings": list(result.warnings),
    }


def _evaluate_data_readiness(
    data_result: PlanningMMMReadinessReportAdapterResult | None,
) -> tuple[
    bool,
    list[str],
    bool,
    list[PlanningMMMModelRunEligibilityIssueCode],
    list[PlanningMMMTrustedInputComponentStatus],
]:
    warnings: list[str] = []
    issues: list[PlanningMMMModelRunEligibilityIssueCode] = []
    components: list[PlanningMMMTrustedInputComponentStatus] = []

    if data_result is None:
        return False, warnings, False, issues, components

    issues.append(PlanningMMMModelRunEligibilityIssueCode.DATA_READINESS_PRESENT)
    envelope = data_result.envelope
    metadata: dict[str, str | bool] = {}
    if envelope is not None:
        metadata = {k: bool(v) for k, v in envelope.readiness_metadata.items()}

    has_spend = bool(metadata.get("has_historical_spend"))
    has_outcome = bool(metadata.get("has_historical_outcome"))
    has_channel = bool(metadata.get("has_channel_taxonomy"))
    has_budget = bool(metadata.get("has_budget_constraints"))

    components.extend(
        [
            PlanningMMMTrustedInputComponentStatus(
                component_name="historical_spend",
                present=has_spend,
                required=True,
                status="present" if has_spend else "missing",
            ),
            PlanningMMMTrustedInputComponentStatus(
                component_name="historical_outcome",
                present=has_outcome,
                required=True,
                status="present" if has_outcome else "missing",
            ),
            PlanningMMMTrustedInputComponentStatus(
                component_name="channel_taxonomy",
                present=has_channel,
                required=False,
                status="present" if has_channel else "missing",
            ),
            PlanningMMMTrustedInputComponentStatus(
                component_name="budget_constraints",
                present=has_budget,
                required=False,
                status="present" if has_budget else "missing",
            ),
        ]
    )

    if has_spend:
        issues.append(PlanningMMMModelRunEligibilityIssueCode.HISTORICAL_SPEND_PRESENT)
    else:
        issues.append(PlanningMMMModelRunEligibilityIssueCode.HISTORICAL_SPEND_MISSING)

    if has_outcome:
        issues.append(PlanningMMMModelRunEligibilityIssueCode.HISTORICAL_OUTCOME_PRESENT)
    else:
        issues.append(PlanningMMMModelRunEligibilityIssueCode.HISTORICAL_OUTCOME_MISSING)

    if has_channel:
        issues.append(PlanningMMMModelRunEligibilityIssueCode.CHANNEL_TAXONOMY_PRESENT)
    else:
        issues.append(PlanningMMMModelRunEligibilityIssueCode.CHANNEL_TAXONOMY_MISSING)
        warnings.append("channel taxonomy not present")

    if has_budget:
        issues.append(PlanningMMMModelRunEligibilityIssueCode.BUDGET_CONSTRAINTS_PRESENT)
    else:
        issues.append(PlanningMMMModelRunEligibilityIssueCode.BUDGET_CONSTRAINTS_MISSING)
        warnings.append("budget constraints not present")

    data_blocked = data_result.status in _BLOCKED_DATA_STATUSES
    if data_blocked:
        issues.append(PlanningMMMModelRunEligibilityIssueCode.DATA_READINESS_BLOCKED)

    data_ready = data_result.status in _READY_DATA_STATUSES or (
        data_result.status == PlanningMMMReadinessReportAdapterStatus.DIAGNOSTIC_ONLY
        and has_spend
        and has_outcome
    )
    if not data_ready and not data_blocked:
        issues.append(PlanningMMMModelRunEligibilityIssueCode.DATA_READINESS_BLOCKED)

    ok = has_spend and has_outcome and data_ready and not data_blocked
    return ok, warnings, data_blocked, issues, components


def _evaluate_calibration_readiness(
    calibration_result: PlanningMMMCalibrationSignalMappingReadinessResult | None,
    *,
    require_calibration_readiness: bool,
    allow_diagnostic_only_calibration: bool,
) -> tuple[bool, list[str], bool, list[PlanningMMMModelRunEligibilityIssueCode]]:
    warnings: list[str] = []
    issues: list[PlanningMMMModelRunEligibilityIssueCode] = []

    if calibration_result is None:
        if require_calibration_readiness:
            issues.append(PlanningMMMModelRunEligibilityIssueCode.CALIBRATION_READINESS_BLOCKED)
        return not require_calibration_readiness, warnings, require_calibration_readiness, issues

    issues.append(PlanningMMMModelRunEligibilityIssueCode.CALIBRATION_READINESS_PRESENT)
    readiness = calibration_result.readiness_status

    if readiness == PlanningMMMCalibrationSignalReadinessStatus.READY_FOR_MODEL_CALIBRATION:
        issues.append(PlanningMMMModelRunEligibilityIssueCode.CALIBRATION_READINESS_READY)
        return True, warnings, False, issues

    if readiness == PlanningMMMCalibrationSignalReadinessStatus.READY_WITH_WARNINGS:
        issues.append(PlanningMMMModelRunEligibilityIssueCode.CALIBRATION_READINESS_WARNINGS)
        warnings.extend(calibration_result.warnings)
        return True, warnings, False, issues

    if readiness == PlanningMMMCalibrationSignalReadinessStatus.STALE_REQUIRES_REVIEW:
        issues.append(PlanningMMMModelRunEligibilityIssueCode.CALIBRATION_READINESS_WARNINGS)
        warnings.append("calibration signals stale and require review")
        return True, warnings, False, issues

    if readiness == PlanningMMMCalibrationSignalReadinessStatus.DIAGNOSTIC_ONLY:
        issues.append(PlanningMMMModelRunEligibilityIssueCode.CALIBRATION_READINESS_DIAGNOSTIC_ONLY)
        warnings.append("calibration readiness is diagnostic-only")
        if require_calibration_readiness and not allow_diagnostic_only_calibration:
            return False, warnings, False, issues
        return allow_diagnostic_only_calibration, warnings, False, issues

    if readiness == PlanningMMMCalibrationSignalReadinessStatus.BLOCKED:
        issues.append(PlanningMMMModelRunEligibilityIssueCode.CALIBRATION_READINESS_BLOCKED)
        return False, warnings, True, issues

    if readiness == PlanningMMMCalibrationSignalReadinessStatus.DEFERRED:
        warnings.append("calibration readiness deferred")
        return not require_calibration_readiness, warnings, False, issues

    return not require_calibration_readiness, warnings, False, issues


def _evaluate_existing_model_availability(
    existing_result: object,
) -> tuple[bool, bool, bool, list[PlanningMMMModelRunEligibilityIssueCode], list[str]]:
    from mip.contracts.mmm_existing_model_availability import MMMExistingModelAvailabilityResult

    if not isinstance(existing_result, MMMExistingModelAvailabilityResult):
        return False, False, True, [], []

    issues: list[PlanningMMMModelRunEligibilityIssueCode] = []
    warnings = list(existing_result.warnings)
    status = existing_result.status

    usable = status in _USABLE_EXISTING_MODEL_STATUSES
    refresh = status in _REFRESH_EXISTING_MODEL_STATUSES
    new_run = status in _NEW_RUN_EXISTING_MODEL_STATUSES or existing_result.requires_new_model_run

    if usable:
        issues.append(PlanningMMMModelRunEligibilityIssueCode.EXISTING_MODEL_USABLE)
    elif refresh:
        issues.append(PlanningMMMModelRunEligibilityIssueCode.EXISTING_MODEL_REFRESH_REQUIRED)
    else:
        issues.append(PlanningMMMModelRunEligibilityIssueCode.EXISTING_MODEL_NOT_USABLE)
        if new_run:
            issues.append(PlanningMMMModelRunEligibilityIssueCode.NEW_MODEL_RUN_REQUIRED)

    return usable, refresh, new_run, issues, warnings


def _build_trusted_input_package(
    *,
    request: PlanningMMMModelRunEligibilityRequest,
    data_components: list[PlanningMMMTrustedInputComponentStatus],
    warnings: list[str],
    issues: list[PlanningMMMModelRunEligibilityIssueCode],
    lineage: dict[str, str],
) -> PlanningMMMTrustedInputPackage:
    data_status: str | None = None
    data_request_id: str | None = None
    calibration_status: str | None = None
    calibration_request_id: str | None = None
    existing_status: str | None = None
    existing_request_id: str | None = None
    selected_model_id: str | None = None

    if request.data_readiness_result is not None:
        data_request_id = request.data_readiness_result.request_id
        data_status = str(request.data_readiness_result.status)
        lineage["data_readiness_request_id"] = data_request_id
        lineage["data_readiness_status"] = data_status

    if request.calibration_readiness_result is not None:
        calibration_request_id = request.calibration_readiness_result.request_id
        calibration_status = str(request.calibration_readiness_result.readiness_status)
        lineage["calibration_readiness_request_id"] = calibration_request_id
        lineage["calibration_readiness_status"] = calibration_status

    if request.existing_model_availability_result is not None:
        existing_request_id = request.existing_model_availability_result.request_id
        existing_status = str(request.existing_model_availability_result.status)
        lineage["existing_model_availability_request_id"] = existing_request_id
        lineage["existing_model_availability_status"] = existing_status
        if request.existing_model_availability_result.selected_model is not None:
            selected_model_id = (
                request.existing_model_availability_result.selected_model.model_id
            )
            lineage["existing_model_selected_id"] = selected_model_id

    required_components = [c for c in data_components if c.required]
    optional_components = [c for c in data_components if not c.required]
    if request.model_config_present or request.model_config_id:
        optional_components.append(
            PlanningMMMTrustedInputComponentStatus(
                component_name="model_config",
                present=True,
                required=False,
                status="present",
            )
        )
    else:
        optional_components.append(
            PlanningMMMTrustedInputComponentStatus(
                component_name="model_config",
                present=False,
                required=False,
                status="missing",
            )
        )

    return PlanningMMMTrustedInputPackage(
        package_id=f"trusted-input:{request.request_id}",
        request_id=request.request_id,
        data_readiness_request_id=data_request_id,
        data_readiness_status=data_status,
        calibration_readiness_request_id=calibration_request_id,
        calibration_readiness_status=calibration_status,
        existing_model_availability_request_id=existing_request_id,
        existing_model_availability_status=existing_status,
        existing_model_selected_id=selected_model_id,
        model_config_id=request.model_config_id,
        model_config_present=request.model_config_present or bool(request.model_config_id),
        required_component_statuses=required_components,
        optional_component_statuses=optional_components,
        lineage=lineage,
        warnings=list(dict.fromkeys(warnings)),
        issues=_dedupe_issues(issues),
        metadata=dict(request.metadata),
    )


def _blocked(
    *,
    request: PlanningMMMModelRunEligibilityRequest,
    trusted_input_status: PlanningMMMTrustedInputStatus,
    eligibility_status: PlanningMMMModelRunEligibilityStatus,
    decision: PlanningMMMModelRunEligibilityDecision,
    package: PlanningMMMTrustedInputPackage,
    blocked_reasons: list[str],
    warnings: list[str],
    issues: list[PlanningMMMModelRunEligibilityIssueCode],
    lineage: dict[str, str],
    human_review_required: bool = False,
) -> PlanningMMMModelRunEligibilityResult:
    return PlanningMMMModelRunEligibilityResult(
        request_id=request.request_id,
        trusted_input_status=trusted_input_status,
        eligibility_status=eligibility_status,
        decision=decision,
        trusted_input_package=package,
        human_review_required=human_review_required,
        blocked_reasons=blocked_reasons,
        warnings=list(dict.fromkeys(warnings)),
        issues=_dedupe_issues(
            issues + [PlanningMMMModelRunEligibilityIssueCode.MODEL_RUN_ELIGIBILITY_EVALUATED]
        ),
        lineage=lineage,
        metadata=dict(request.metadata),
    )


def _result(
    *,
    request: PlanningMMMModelRunEligibilityRequest,
    trusted_input_status: PlanningMMMTrustedInputStatus,
    eligibility_status: PlanningMMMModelRunEligibilityStatus,
    decision: PlanningMMMModelRunEligibilityDecision,
    package: PlanningMMMTrustedInputPackage,
    eligible_to_request_model_run: bool = False,
    use_existing_model: bool = False,
    requires_model_refresh: bool = False,
    requires_new_model_run: bool = False,
    blocked_reasons: list[str] | None = None,
    warnings: list[str] | None = None,
    issues: list[PlanningMMMModelRunEligibilityIssueCode] | None = None,
    lineage: dict[str, str] | None = None,
    human_review_required: bool = False,
) -> PlanningMMMModelRunEligibilityResult:
    return PlanningMMMModelRunEligibilityResult(
        request_id=request.request_id,
        trusted_input_status=trusted_input_status,
        eligibility_status=eligibility_status,
        decision=decision,
        trusted_input_package=package,
        eligible_to_request_model_run=eligible_to_request_model_run,
        use_existing_model=use_existing_model,
        requires_model_refresh=requires_model_refresh,
        requires_new_model_run=requires_new_model_run,
        human_review_required=human_review_required,
        blocked_reasons=blocked_reasons or [],
        warnings=list(dict.fromkeys(warnings or [])),
        issues=_dedupe_issues(issues or []),
        lineage=lineage or {},
        metadata=dict(request.metadata),
    )


def _enum_value(value: object) -> str:
    if hasattr(value, "value"):
        return str(getattr(value, "value"))
    return str(value)


def _dedupe_issues(
    issues: list[PlanningMMMModelRunEligibilityIssueCode],
) -> list[PlanningMMMModelRunEligibilityIssueCode]:
    seen: set[PlanningMMMModelRunEligibilityIssueCode] = set()
    ordered: list[PlanningMMMModelRunEligibilityIssueCode] = []
    for issue in issues:
        if issue not in seen:
            seen.add(issue)
            ordered.append(issue)
    return ordered
