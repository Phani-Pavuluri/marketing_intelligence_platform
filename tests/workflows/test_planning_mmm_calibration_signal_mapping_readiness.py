"""Tests for Planning/MMM calibration-signal mapping and readiness workflow."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from mip.contracts.mmm_existing_model_availability import (
    MMMExistingModelAvailabilityResult,
    MMMExistingModelAvailabilityStatus,
)
from mip.contracts.planning_mmm_calibration_signal_mapping_readiness import (
    PlanningMMMCalibrationSignalMappingIssueCode,
    PlanningMMMCalibrationSignalMappingReadinessRequest,
    PlanningMMMCalibrationSignalMappingReadinessResult,
    PlanningMMMCalibrationSignalMappingStatus,
    PlanningMMMCalibrationSignalMappingTarget,
    PlanningMMMCalibrationSignalReadinessStatus,
    PlanningMMMCalibrationSignalRecordMetadata,
    PlanningMMMCalibrationSignalUsability,
)
from mip.contracts.planning_mmm_calibration_signal_tabular_intake import (
    PlanningMMMCalibrationSignalConstructionMode,
    PlanningMMMCalibrationSignalTabularIntakeEnvelope,
    PlanningMMMCalibrationSignalTabularIntakeRequest,
    PlanningMMMCalibrationSignalTabularIntakeResult,
    PlanningMMMCalibrationSignalTabularIntakeStatus,
)
from mip.contracts.uploaded_csv_materialization import (
    UploadedCSVMaterializationRequest,
    UploadedCSVSource,
    UploadedCSVSourceType,
)
from mip.workflows.planning_mmm_calibration_signal_mapping_readiness import (
    evaluate_planning_mmm_calibration_signal_mapping_readiness,
    summarize_planning_mmm_calibration_signal_mapping_readiness,
)
from mip.workflows.planning_mmm_calibration_signal_tabular_intake import (
    intake_calibration_signals_from_tabular_source,
)
from mip.workflows.tabular_source_inspection import (
    build_tabular_source_inspection_from_uploaded_csv_materialization,
)
from mip.workflows.uploaded_csv_materialization import materialize_uploaded_csvs

_FIXTURE_ROOT = Path("examples/fixtures/planning_mmm_uploaded_csv_adapter")
_CALIBRATION_PATH = str(_FIXTURE_ROOT / "calibration_signals.csv")
_SPEND_PATH = str(_FIXTURE_ROOT / "historical_spend.csv")
_OUTCOME_PATH = str(_FIXTURE_ROOT / "historical_outcome.csv")
_REFERENCE_END = date(2026, 6, 1)
_WORKFLOW_SOURCE = Path(
    "src/mip/workflows/planning_mmm_calibration_signal_mapping_readiness.py"
)
_CONTRACT_SOURCE = Path(
    "src/mip/contracts/planning_mmm_calibration_signal_mapping_readiness.py"
)
_FIXTURE_REQUIRED_COLUMNS = ["channel", "lift", "standard_error"]
_FIXTURE_COLUMN_ALIASES = {
    "lift": ["prior_lift"],
    "standard_error": ["prior_uncertainty"],
}


def _source(source_id: str, path: str, *, hint: str | None = None) -> UploadedCSVSource:
    return UploadedCSVSource(
        source_id=source_id,
        source_type=UploadedCSVSourceType.UPLOADED_CSV,
        path=path,
        original_filename=Path(path).name,
        declared_role_hint=hint,
    )


def _ready_intake(
    *, request_id: str = "intake-map-1"
) -> PlanningMMMCalibrationSignalTabularIntakeResult:
    materialization = materialize_uploaded_csvs(
        UploadedCSVMaterializationRequest(
            request_id="mat-map",
            sources=[
                _source("spend", _SPEND_PATH),
                _source("outcome", _OUTCOME_PATH),
                _source("calibration", _CALIBRATION_PATH, hint="calibration_signals"),
            ],
        )
    )
    tabular = build_tabular_source_inspection_from_uploaded_csv_materialization(
        request_id="tabular-map",
        materialization_result=materialization,
    )
    return intake_calibration_signals_from_tabular_source(
        PlanningMMMCalibrationSignalTabularIntakeRequest(
            request_id=request_id,
            tabular_source_result=tabular,
            explicit_calibration_source_ids=["calibration"],
            required_columns=list(_FIXTURE_REQUIRED_COLUMNS),
            column_role_aliases=dict(_FIXTURE_COLUMN_ALIASES),
        )
    )


def _target(
    *,
    metric: str = "revenue",
    channels: list[str] | None = None,
    estimand: str = "incremental_contribution",
    allow_diagnostic_only: bool = False,
    require_uncertainty: bool = True,
    max_signal_age_days: int = 365,
) -> PlanningMMMCalibrationSignalMappingTarget:
    return PlanningMMMCalibrationSignalMappingTarget(
        target_model_id="mmm-target-1",
        metric=metric,
        channels=channels or ["search"],
        estimand=estimand,
        planning_start_date=date(2025, 1, 1),
        planning_end_date=_REFERENCE_END,
        max_signal_age_days=max_signal_age_days,
        allow_diagnostic_only=allow_diagnostic_only,
        require_uncertainty=require_uncertainty,
    )


def _aligned_record(
    *,
    record_id: str = "rec-search",
    source_id: str = "calibration",
    metric: str = "revenue",
    channel: str = "search",
    estimand: str = "incremental_contribution",
    evidence_source: str = "experiment",
    freshness_date: date | None = None,
    end_date: date | None = None,
    uncertainty_field_name: str = "prior_uncertainty",
) -> PlanningMMMCalibrationSignalRecordMetadata:
    return PlanningMMMCalibrationSignalRecordMetadata(
        record_id=record_id,
        source_id=source_id,
        metric=metric,
        channel=channel,
        estimand=estimand,
        effect_field_name="prior_lift",
        uncertainty_field_name=uncertainty_field_name,
        start_date=date(2025, 1, 1),
        end_date=end_date or date(2025, 12, 31),
        freshness_date=freshness_date or date(2026, 5, 1),
        evidence_source=evidence_source,
    )


def _evaluate(
    *,
    intake: PlanningMMMCalibrationSignalTabularIntakeResult | None,
    target: PlanningMMMCalibrationSignalMappingTarget | None = None,
    signal_records: list[PlanningMMMCalibrationSignalRecordMetadata] | None = None,
    existing_model_availability: MMMExistingModelAvailabilityResult | None = None,
) -> PlanningMMMCalibrationSignalMappingReadinessResult:
    return evaluate_planning_mmm_calibration_signal_mapping_readiness(
        PlanningMMMCalibrationSignalMappingReadinessRequest(
            request_id="map-readiness-1",
            intake_result=intake,
            target=target or _target(),
            signal_records=signal_records or [],
            existing_model_availability_result=existing_model_availability,
        )
    )


def test_missing_intake_blocks() -> None:
    result = _evaluate(intake=None, signal_records=[_aligned_record()])
    assert result.mapping_status == PlanningMMMCalibrationSignalMappingStatus.BLOCKED_MISSING_INTAKE
    assert result.readiness_status == PlanningMMMCalibrationSignalReadinessStatus.BLOCKED


def test_blocked_intake_propagates_blocker() -> None:
    blocked = PlanningMMMCalibrationSignalTabularIntakeResult(
        request_id="blocked-intake",
        status=PlanningMMMCalibrationSignalTabularIntakeStatus.BLOCKED_MISSING_TABULAR_SOURCE_RESULT,
    )
    result = _evaluate(intake=blocked, signal_records=[_aligned_record()])
    assert (
        result.mapping_status
        == PlanningMMMCalibrationSignalMappingStatus.BLOCKED_INTAKE_NOT_READY
    )
    assert PlanningMMMCalibrationSignalMappingIssueCode.INTAKE_NOT_READY in result.issues


def test_aligned_causal_signal_ready_for_model_calibration() -> None:
    intake = _ready_intake()
    result = _evaluate(intake=intake, signal_records=[_aligned_record()])
    assert result.readiness_status in {
        PlanningMMMCalibrationSignalReadinessStatus.READY_FOR_MODEL_CALIBRATION,
        PlanningMMMCalibrationSignalReadinessStatus.READY_WITH_WARNINGS,
    }
    assert result.mapping_status in {
        PlanningMMMCalibrationSignalMappingStatus.MAPPING_READY,
        PlanningMMMCalibrationSignalMappingStatus.MAPPING_READY_WITH_WARNINGS,
    }
    assert result.assessment.usable_signal_ids


def test_aligned_signal_missing_optional_fields_ready_with_warnings() -> None:
    intake = _ready_intake()
    record = _aligned_record()
    record = record.model_copy(update={"geo_scope": None})
    result = _evaluate(intake=intake, signal_records=[record])
    assert result.readiness_status in {
        PlanningMMMCalibrationSignalReadinessStatus.READY_FOR_MODEL_CALIBRATION,
        PlanningMMMCalibrationSignalReadinessStatus.READY_WITH_WARNINGS,
    }


def test_metric_mismatch_blocks_record() -> None:
    intake = _ready_intake()
    result = _evaluate(
        intake=intake,
        signal_records=[_aligned_record(metric="orders")],
    )
    assert result.readiness_status == PlanningMMMCalibrationSignalReadinessStatus.BLOCKED
    assert any(
        record.usability == PlanningMMMCalibrationSignalUsability.BLOCKED
        for record in result.mapped_records
    )


def test_channel_mismatch_blocks_record() -> None:
    intake = _ready_intake()
    result = _evaluate(
        intake=intake,
        target=_target(channels=["tv"]),
        signal_records=[_aligned_record(channel="search")],
    )
    assert result.readiness_status == PlanningMMMCalibrationSignalReadinessStatus.BLOCKED


def test_estimand_mismatch_blocks_when_policy_disallows_diagnostic() -> None:
    intake = _ready_intake()
    result = _evaluate(
        intake=intake,
        target=_target(allow_diagnostic_only=False),
        signal_records=[_aligned_record(estimand="contribution_share")],
    )
    assert result.readiness_status == PlanningMMMCalibrationSignalReadinessStatus.BLOCKED


def test_estimand_mismatch_diagnostic_only_when_allowed() -> None:
    intake = _ready_intake()
    result = _evaluate(
        intake=intake,
        target=_target(allow_diagnostic_only=True),
        signal_records=[_aligned_record(estimand="contribution_share")],
    )
    assert result.readiness_status == PlanningMMMCalibrationSignalReadinessStatus.DIAGNOSTIC_ONLY
    assert result.mapping_status == PlanningMMMCalibrationSignalMappingStatus.DIAGNOSTIC_ONLY


def test_time_window_mismatch_blocks_when_policy_disallows_diagnostic() -> None:
    intake = _ready_intake()
    record = _aligned_record()
    record = record.model_copy(
        update={"start_date": date(2024, 1, 1), "end_date": date(2024, 3, 1)}
    )
    result = _evaluate(
        intake=intake,
        target=_target(allow_diagnostic_only=False),
        signal_records=[record],
    )
    assert result.readiness_status == PlanningMMMCalibrationSignalReadinessStatus.BLOCKED


def test_stale_signal_requires_review() -> None:
    intake = _ready_intake()
    result = _evaluate(
        intake=intake,
        target=_target(max_signal_age_days=90),
        signal_records=[
            _aligned_record(freshness_date=date(2025, 1, 1), end_date=date(2025, 1, 31))
        ],
    )
    assert result.readiness_status in {
        PlanningMMMCalibrationSignalReadinessStatus.STALE_REQUIRES_REVIEW,
        PlanningMMMCalibrationSignalReadinessStatus.BLOCKED,
    }
    assert any(
        record.usability == PlanningMMMCalibrationSignalUsability.STALE
        for record in result.mapped_records
    )


def test_missing_uncertainty_blocks_when_required() -> None:
    intake = _ready_intake()
    result = _evaluate(
        intake=intake,
        target=_target(require_uncertainty=True),
        signal_records=[_aligned_record(uncertainty_field_name="")],
    )
    record = result.mapped_records[0]
    assert record.usability == PlanningMMMCalibrationSignalUsability.BLOCKED
    assert (
        PlanningMMMCalibrationSignalMappingIssueCode.UNCERTAINTY_MISSING in record.issues
    )


def test_missing_uncertainty_warning_when_not_required() -> None:
    intake = _ready_intake()
    record = _aligned_record()
    record = record.model_copy(update={"uncertainty_field_name": ""})
    result = _evaluate(
        intake=intake,
        target=_target(require_uncertainty=False),
        signal_records=[record],
    )
    assert "uncertainty field missing" in " ".join(result.mapped_records[0].warnings).lower()
    assert result.readiness_status in {
        PlanningMMMCalibrationSignalReadinessStatus.READY_FOR_MODEL_CALIBRATION,
        PlanningMMMCalibrationSignalReadinessStatus.READY_WITH_WARNINGS,
    }


def test_diagnostic_only_signal_classification() -> None:
    intake = _ready_intake()
    result = _evaluate(
        intake=intake,
        signal_records=[_aligned_record(evidence_source="observational")],
    )
    assert result.assessment.diagnostic_only_signal_ids
    assert result.readiness_status == PlanningMMMCalibrationSignalReadinessStatus.DIAGNOSTIC_ONLY


def test_mixed_signals_summarized_correctly() -> None:
    intake = _ready_intake()
    result = _evaluate(
        intake=intake,
        signal_records=[
            _aligned_record(record_id="usable", channel="search"),
            _aligned_record(
                record_id="stale",
                channel="search",
                freshness_date=date(2024, 1, 1),
                end_date=date(2024, 12, 31),
            ),
            _aligned_record(
                record_id="blocked",
                channel="search",
                metric="orders",
            ),
            _aligned_record(
                record_id="diagnostic",
                channel="search",
                evidence_source="observational",
            ),
        ],
        target=_target(channels=["search"], max_signal_age_days=365),
    )
    summary = summarize_planning_mmm_calibration_signal_mapping_readiness(result)
    usable_count = summary["usable_count"]
    blocked_count = summary["blocked_count"]
    diagnostic_count = summary["diagnostic_only_count"]
    assert isinstance(usable_count, int) and usable_count >= 1
    assert isinstance(blocked_count, int) and blocked_count >= 1
    assert isinstance(diagnostic_count, int) and diagnostic_count >= 1


def test_data_source_ref_preserved() -> None:
    intake = _ready_intake()
    result = _evaluate(intake=intake, signal_records=[_aligned_record()])
    assert result.mapped_records[0].data_source_ref is not None
    assert (
        PlanningMMMCalibrationSignalMappingIssueCode.DATA_SOURCE_REF_PRESERVED in result.issues
    )


def test_tabular_source_ref_preserved() -> None:
    intake = _ready_intake()
    result = _evaluate(intake=intake, signal_records=[_aligned_record()])
    assert result.mapped_records[0].tabular_source_reference is not None
    assert (
        PlanningMMMCalibrationSignalMappingIssueCode.TABULAR_SOURCE_REF_PRESERVED
        in result.issues
    )


def test_lineage_preserved() -> None:
    intake = _ready_intake()
    result = _evaluate(intake=intake, signal_records=[_aligned_record()])
    assert result.lineage.get("mapping_stage") == (
        "planning_mmm_calibration_signal_mapping_readiness"
    )
    assert PlanningMMMCalibrationSignalMappingIssueCode.LINEAGE_PRESERVED in result.issues


def test_existing_model_availability_reference_metadata_only() -> None:
    intake = _ready_intake()
    availability = MMMExistingModelAvailabilityResult(
        request_id="avail-ref",
        status=MMMExistingModelAvailabilityStatus.USABLE_EXISTING_MODEL,
    )
    result = _evaluate(
        intake=intake,
        signal_records=[_aligned_record()],
        existing_model_availability=availability,
    )
    assert result.lineage.get("existing_model_availability_request_id") == "avail-ref"


def test_model_calibration_readiness_integration_deferred() -> None:
    intake = _ready_intake()
    result = _evaluate(intake=intake, signal_records=[_aligned_record()])
    assert result.assessment.model_calibration_readiness_deferred is True
    assert result.assessment.model_calibration_readiness_deferred_reason
    assert (
        PlanningMMMCalibrationSignalMappingIssueCode.MODEL_CALIBRATION_READINESS_REFERENCE_CREATED
        in result.issues
        or PlanningMMMCalibrationSignalMappingIssueCode.MAPPING_DEFERRED in result.issues
    )


def test_no_model_execution_or_calibration_math_in_sources() -> None:
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
        content = path.read_text(encoding="utf-8")
        for line in content.splitlines():
            if line.strip().startswith("#"):
                continue
            for token in forbidden:
                assert token not in line, f"{token} in {path}: {line}"


def test_boundary_issue_codes_present() -> None:
    intake = _ready_intake()
    result = _evaluate(intake=intake, signal_records=[_aligned_record()])
    for code in (
        PlanningMMMCalibrationSignalMappingIssueCode.NO_MODEL_EXECUTION,
        PlanningMMMCalibrationSignalMappingIssueCode.NO_PRIOR_APPLICATION,
        PlanningMMMCalibrationSignalMappingIssueCode.NO_LIKELIHOOD_CONSTRUCTION,
        PlanningMMMCalibrationSignalMappingIssueCode.NO_POSTERIOR_CALCULATION,
        PlanningMMMCalibrationSignalMappingIssueCode.NO_OPTIMIZER_EXECUTION,
        PlanningMMMCalibrationSignalMappingIssueCode.NO_SIMULATOR_EXECUTION,
        PlanningMMMCalibrationSignalMappingIssueCode.NO_RECOMMENDATION_GENERATED,
        PlanningMMMCalibrationSignalMappingIssueCode.NO_DECISION_SURFACE_EXECUTION,
        PlanningMMMCalibrationSignalMappingIssueCode.NO_CLAIM_AUTHORIZATION,
    ):
        assert code in result.issues


def test_intake_only_without_signal_values_defers_or_blocks() -> None:
    intake = _ready_intake()
    result = _evaluate(intake=intake)
    assert result.readiness_status in {
        PlanningMMMCalibrationSignalReadinessStatus.DEFERRED,
        PlanningMMMCalibrationSignalReadinessStatus.BLOCKED,
    }


def test_manual_envelope_intake_diagnostic_only() -> None:
    envelope = PlanningMMMCalibrationSignalTabularIntakeEnvelope(
        envelope_id="env-diag",
        status=PlanningMMMCalibrationSignalTabularIntakeStatus.DIAGNOSTIC_ONLY,
        construction_mode=PlanningMMMCalibrationSignalConstructionMode.DIAGNOSTIC_ONLY,
    )
    intake = PlanningMMMCalibrationSignalTabularIntakeResult(
        request_id="diag-intake",
        status=PlanningMMMCalibrationSignalTabularIntakeStatus.DIAGNOSTIC_ONLY,
        envelope=envelope,
    )
    result = _evaluate(intake=intake, signal_records=[_aligned_record()])
    assert result.mapping_status == PlanningMMMCalibrationSignalMappingStatus.DIAGNOSTIC_ONLY
