"""Tests for Planning/MMM trusted input and model-run eligibility workflow."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from mip.contracts.mmm_existing_model_availability import (
    MMMExistingModelAvailabilityResult,
    MMMExistingModelAvailabilityStatus,
    MMMModelArtifact,
    MMMModelDiagnosticStatus,
    MMMModelPromotionStatus,
)
from mip.contracts.planning_mmm_calibration_signal_mapping_readiness import (
    PlanningMMMCalibrationSignalMappingReadinessResult,
    PlanningMMMCalibrationSignalMappingStatus,
    PlanningMMMCalibrationSignalReadinessAssessment,
    PlanningMMMCalibrationSignalReadinessStatus,
)
from mip.contracts.planning_mmm_readiness_report_adapter import (
    PlanningMMMReadinessReportAdapterEnvelope,
    PlanningMMMReadinessReportAdapterResult,
    PlanningMMMReadinessReportAdapterStatus,
    PlanningMMMReadinessReportCompatibility,
    PlanningMMMReadinessReportCompatibilityMode,
)
from mip.contracts.planning_mmm_trusted_input_model_run_eligibility import (
    PlanningMMMModelRunEligibilityDecision,
    PlanningMMMModelRunEligibilityIssueCode,
    PlanningMMMModelRunEligibilityRequest,
    PlanningMMMModelRunEligibilityResult,
    PlanningMMMModelRunEligibilityStatus,
    PlanningMMMTrustedInputStatus,
)
from mip.workflows.planning_mmm_trusted_input_model_run_eligibility import (
    evaluate_planning_mmm_trusted_input_and_model_run_eligibility,
    summarize_planning_mmm_model_run_eligibility,
)

_WORKFLOW_SOURCE = Path(
    "src/mip/workflows/planning_mmm_trusted_input_model_run_eligibility.py"
)
_CONTRACT_SOURCE = Path(
    "src/mip/contracts/planning_mmm_trusted_input_model_run_eligibility.py"
)


def _compatibility() -> PlanningMMMReadinessReportCompatibility:
    return PlanningMMMReadinessReportCompatibility(
        mode=PlanningMMMReadinessReportCompatibilityMode.METADATA_COMPATIBLE,
        metadata_compatible=True,
    )


def _data_readiness(
    *,
    status: PlanningMMMReadinessReportAdapterStatus = (
        PlanningMMMReadinessReportAdapterStatus.REPORT_ADAPTED
    ),
    has_spend: bool = True,
    has_outcome: bool = True,
    has_channel: bool = True,
    has_budget: bool = False,
    request_id: str = "data-readiness-1",
) -> PlanningMMMReadinessReportAdapterResult:
    return PlanningMMMReadinessReportAdapterResult(
        request_id=request_id,
        status=status,
        envelope=PlanningMMMReadinessReportAdapterEnvelope(
            envelope_id="env-data",
            source_workflow_readiness_status="ready_for_mmm_workflow_readiness",
            source_workflow_readiness_tier="ready_for_gated_workflow",
            readiness_report_status="ready",
            compatibility=_compatibility(),
            readiness_metadata={
                "has_historical_spend": has_spend,
                "has_historical_outcome": has_outcome,
                "has_channel_taxonomy": has_channel,
                "has_budget_constraints": has_budget,
            },
            lineage={"data_stage": "adapter"},
        ),
    )


def _calibration_readiness(
    *,
    readiness_status: PlanningMMMCalibrationSignalReadinessStatus = (
        PlanningMMMCalibrationSignalReadinessStatus.READY_FOR_MODEL_CALIBRATION
    ),
    mapping_status: PlanningMMMCalibrationSignalMappingStatus = (
        PlanningMMMCalibrationSignalMappingStatus.MAPPING_READY
    ),
    warnings: list[str] | None = None,
) -> PlanningMMMCalibrationSignalMappingReadinessResult:
    return PlanningMMMCalibrationSignalMappingReadinessResult(
        request_id="cal-readiness-1",
        mapping_status=mapping_status,
        readiness_status=readiness_status,
        assessment=PlanningMMMCalibrationSignalReadinessAssessment(
            readiness_status=readiness_status,
        ),
        warnings=warnings or [],
    )


def _existing_model_availability(
    *,
    status: MMMExistingModelAvailabilityStatus,
    requires_new_model_run: bool = False,
    requires_model_refresh: bool = False,
    model_id: str = "mmm-existing-1",
) -> MMMExistingModelAvailabilityResult:
    selected = None
    if status in {
        MMMExistingModelAvailabilityStatus.USABLE_EXISTING_MODEL,
        MMMExistingModelAvailabilityStatus.USABLE_EXISTING_MODEL_WITH_WARNINGS,
        MMMExistingModelAvailabilityStatus.REQUIRES_MODEL_REFRESH,
    }:
        selected = MMMModelArtifact(
            model_id=model_id,
            artifact_fingerprint="fp-1",
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
            diagnostic_status=MMMModelDiagnosticStatus.PASSED,
            promotion_status=MMMModelPromotionStatus.PROMOTED_FOR_PLANNING,
        )
    return MMMExistingModelAvailabilityResult(
        request_id="existing-avail-1",
        status=status,
        selected_model=selected,
        requires_new_model_run=requires_new_model_run,
        requires_model_refresh=requires_model_refresh,
    )


def _evaluate(
    *,
    data: PlanningMMMReadinessReportAdapterResult | None = _data_readiness(),
    calibration: PlanningMMMCalibrationSignalMappingReadinessResult | None = None,
    existing: MMMExistingModelAvailabilityResult | None = None,
    model_config_present: bool = False,
    model_config_id: str | None = None,
    require_calibration_readiness: bool = False,
    allow_diagnostic_only_calibration: bool = False,
    allow_existing_model_reuse: bool = True,
    require_human_review_for_warnings: bool = False,
) -> PlanningMMMModelRunEligibilityResult:
    return evaluate_planning_mmm_trusted_input_and_model_run_eligibility(
        PlanningMMMModelRunEligibilityRequest(
            request_id="eligibility-1",
            data_readiness_result=data,
            calibration_readiness_result=calibration,
            existing_model_availability_result=existing,
            model_config_present=model_config_present,
            model_config_id=model_config_id,
            require_calibration_readiness=require_calibration_readiness,
            allow_diagnostic_only_calibration=allow_diagnostic_only_calibration,
            allow_existing_model_reuse=allow_existing_model_reuse,
            require_human_review_for_warnings=require_human_review_for_warnings,
        )
    )


def test_missing_data_readiness_blocks() -> None:
    result = _evaluate(data=None)
    assert result.eligibility_status == (
        PlanningMMMModelRunEligibilityStatus.BLOCKED_MISSING_REQUIRED_DATA
    )
    assert result.decision == PlanningMMMModelRunEligibilityDecision.BLOCK


def test_blocked_data_readiness_blocks() -> None:
    result = _evaluate(
        data=_data_readiness(
            status=PlanningMMMReadinessReportAdapterStatus.BLOCKED_MISSING_REQUIRED_INPUT
        )
    )
    assert result.eligibility_status == (
        PlanningMMMModelRunEligibilityStatus.BLOCKED_DATA_READINESS_FAILED
    )


def test_missing_historical_spend_blocks() -> None:
    result = _evaluate(data=_data_readiness(has_spend=False))
    assert result.eligibility_status == (
        PlanningMMMModelRunEligibilityStatus.BLOCKED_DATA_READINESS_FAILED
    )
    assert PlanningMMMModelRunEligibilityIssueCode.HISTORICAL_SPEND_MISSING in result.issues


def test_missing_historical_outcome_blocks() -> None:
    result = _evaluate(data=_data_readiness(has_outcome=False))
    assert result.eligibility_status == (
        PlanningMMMModelRunEligibilityStatus.BLOCKED_DATA_READINESS_FAILED
    )
    assert (
        PlanningMMMModelRunEligibilityIssueCode.HISTORICAL_OUTCOME_MISSING in result.issues
    )


def test_usable_existing_model_selected_when_reuse_allowed() -> None:
    result = _evaluate(
        existing=_existing_model_availability(
            status=MMMExistingModelAvailabilityStatus.USABLE_EXISTING_MODEL
        )
    )
    assert result.decision == PlanningMMMModelRunEligibilityDecision.USE_EXISTING_MODEL
    assert result.use_existing_model is True
    assert result.eligible_to_request_model_run is False


def test_existing_model_ignored_when_reuse_disabled() -> None:
    result = _evaluate(
        existing=_existing_model_availability(
            status=MMMExistingModelAvailabilityStatus.USABLE_EXISTING_MODEL
        ),
        allow_existing_model_reuse=False,
        model_config_present=True,
        model_config_id="cfg-new",
    )
    assert result.decision == PlanningMMMModelRunEligibilityDecision.REQUEST_NEW_MODEL_RUN
    assert result.use_existing_model is False


def test_stale_existing_model_requests_refresh() -> None:
    result = _evaluate(
        existing=_existing_model_availability(
            status=MMMExistingModelAvailabilityStatus.REQUIRES_MODEL_REFRESH,
            requires_model_refresh=True,
        ),
        model_config_present=True,
        model_config_id="cfg-refresh",
    )
    assert result.decision == PlanningMMMModelRunEligibilityDecision.REQUEST_MODEL_REFRESH
    assert result.requires_model_refresh is True


def test_no_usable_existing_model_and_prerequisites_pass_requests_new_run() -> None:
    result = _evaluate(
        existing=_existing_model_availability(
            status=MMMExistingModelAvailabilityStatus.REQUIRES_NEW_MODEL_RUN,
            requires_new_model_run=True,
        ),
        model_config_present=True,
        model_config_id="cfg-new",
    )
    assert result.decision == PlanningMMMModelRunEligibilityDecision.REQUEST_NEW_MODEL_RUN
    assert result.eligible_to_request_model_run is True
    assert result.requires_new_model_run is True


def test_missing_model_config_blocks_new_run() -> None:
    result = _evaluate(
        existing=_existing_model_availability(
            status=MMMExistingModelAvailabilityStatus.REQUIRES_NEW_MODEL_RUN,
            requires_new_model_run=True,
        ),
        model_config_present=False,
    )
    assert result.eligibility_status == (
        PlanningMMMModelRunEligibilityStatus.BLOCKED_MISSING_MODEL_CONFIG
    )


def test_calibration_readiness_required_and_missing_blocks() -> None:
    result = _evaluate(require_calibration_readiness=True, calibration=None)
    assert result.eligibility_status == (
        PlanningMMMModelRunEligibilityStatus.BLOCKED_CALIBRATION_READINESS_FAILED
    )


def test_calibration_readiness_blocked_blocks_when_required() -> None:
    result = _evaluate(
        calibration=_calibration_readiness(
            readiness_status=PlanningMMMCalibrationSignalReadinessStatus.BLOCKED,
            mapping_status=PlanningMMMCalibrationSignalMappingStatus.BLOCKED_INCOMPATIBLE_METRIC,
        ),
        require_calibration_readiness=True,
        model_config_present=True,
    )
    assert result.eligibility_status == (
        PlanningMMMModelRunEligibilityStatus.BLOCKED_CALIBRATION_READINESS_FAILED
    )


def test_diagnostic_only_calibration_warning_when_allowed() -> None:
    result = _evaluate(
        calibration=_calibration_readiness(
            readiness_status=PlanningMMMCalibrationSignalReadinessStatus.DIAGNOSTIC_ONLY,
            mapping_status=PlanningMMMCalibrationSignalMappingStatus.DIAGNOSTIC_ONLY,
        ),
        allow_diagnostic_only_calibration=True,
        existing=_existing_model_availability(
            status=MMMExistingModelAvailabilityStatus.REQUIRES_NEW_MODEL_RUN,
            requires_new_model_run=True,
        ),
        model_config_present=True,
    )
    assert result.decision == PlanningMMMModelRunEligibilityDecision.REQUEST_NEW_MODEL_RUN
    assert (
        PlanningMMMModelRunEligibilityIssueCode.CALIBRATION_READINESS_DIAGNOSTIC_ONLY
        in result.issues
    )


def test_ready_calibration_with_warnings_handled() -> None:
    result = _evaluate(
        calibration=_calibration_readiness(
            readiness_status=PlanningMMMCalibrationSignalReadinessStatus.READY_WITH_WARNINGS,
            mapping_status=PlanningMMMCalibrationSignalMappingStatus.MAPPING_READY_WITH_WARNINGS,
            warnings=["calibration warning"],
        ),
        existing=_existing_model_availability(
            status=MMMExistingModelAvailabilityStatus.REQUIRES_NEW_MODEL_RUN,
            requires_new_model_run=True,
        ),
        model_config_present=True,
    )
    assert result.decision == PlanningMMMModelRunEligibilityDecision.REQUEST_NEW_MODEL_RUN
    assert result.trusted_input_status == (
        PlanningMMMTrustedInputStatus.TRUSTED_INPUT_READY_WITH_WARNINGS
    )


def test_human_review_required_for_warnings() -> None:
    result = _evaluate(
        data=_data_readiness(has_channel=False, has_budget=False),
        require_human_review_for_warnings=True,
    )
    assert result.human_review_required is True
    assert result.eligibility_status == (
        PlanningMMMModelRunEligibilityStatus.BLOCKED_GOVERNANCE_REVIEW_REQUIRED
    )


def test_trusted_input_package_created() -> None:
    result = _evaluate(
        existing=_existing_model_availability(
            status=MMMExistingModelAvailabilityStatus.USABLE_EXISTING_MODEL
        )
    )
    assert result.trusted_input_package is not None
    assert result.trusted_input_package.package_id.startswith("trusted-input:")
    assert (
        PlanningMMMModelRunEligibilityIssueCode.TRUSTED_INPUT_PACKAGE_CREATED in result.issues
    )


def test_lineage_preserved() -> None:
    result = _evaluate(
        existing=_existing_model_availability(
            status=MMMExistingModelAvailabilityStatus.USABLE_EXISTING_MODEL
        )
    )
    assert result.lineage.get("eligibility_stage") == (
        "planning_mmm_trusted_input_model_run_eligibility"
    )
    assert result.trusted_input_package is not None
    assert result.trusted_input_package.lineage.get("data_readiness_request_id")


def test_metadata_only_existing_model_availability_reference() -> None:
    result = _evaluate(
        existing=_existing_model_availability(
            status=MMMExistingModelAvailabilityStatus.USABLE_EXISTING_MODEL
        )
    )
    assert result.trusted_input_package is not None
    assert result.trusted_input_package.existing_model_availability_request_id == (
        "existing-avail-1"
    )
    assert (
        PlanningMMMModelRunEligibilityIssueCode.EXISTING_MODEL_AVAILABILITY_PRESENT
        in result.issues
    )


def test_no_model_execution_in_sources() -> None:
    forbidden = (
        "import pickle",
        "import joblib",
        "mlflow.pyfunc.load_model",
        "load_model(",
        ".fit(",
        ".predict(",
        ".sample(",
        "DecisionSurface(",
        "RecommendationContract(",
        "TrustReport(",
    )
    for path in (_WORKFLOW_SOURCE, _CONTRACT_SOURCE):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("#"):
                continue
            for token in forbidden:
                assert token not in line, f"{token} in {path}: {line}"


def test_boundary_issue_codes_present() -> None:
    result = _evaluate(
        existing=_existing_model_availability(
            status=MMMExistingModelAvailabilityStatus.USABLE_EXISTING_MODEL
        )
    )
    assert PlanningMMMModelRunEligibilityIssueCode.NO_MODEL_EXECUTION in result.issues
    assert PlanningMMMModelRunEligibilityIssueCode.NO_POSTERIOR_CALCULATION in result.issues
    assert PlanningMMMModelRunEligibilityIssueCode.NO_TRUST_REPORT_CONSTRUCTION in (
        result.issues
    )
    assert PlanningMMMModelRunEligibilityIssueCode.NO_CLAIM_AUTHORIZATION in result.issues


def test_summarize_returns_metadata_only() -> None:
    result = _evaluate(
        existing=_existing_model_availability(
            status=MMMExistingModelAvailabilityStatus.USABLE_EXISTING_MODEL
        )
    )
    summary = summarize_planning_mmm_model_run_eligibility(result)
    assert summary["decision"] == PlanningMMMModelRunEligibilityDecision.USE_EXISTING_MODEL.value
    assert "recommendation" not in summary
