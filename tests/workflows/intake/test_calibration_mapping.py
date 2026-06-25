"""Tests for CalibrationSignal intake mapping helpers."""

from datetime import UTC, datetime
from typing import Any

from mip.contracts.calibration import CalibrationSignal
from mip.contracts.calibration_intake import (
    FORBIDDEN_CALIBRATION_INTAKE_RESULT_FIELD_NAMES,
    CalibrationEvidenceInput,
    CalibrationIntakeBlockingReason,
    CalibrationIntakeStatus,
    CalibrationMappingRequirement,
)
from mip.contracts.workflow_readiness import CalibrationSignalReadinessReport
from mip.workflows.intake.calibration_mapping import (
    build_calibration_mapping_report,
    map_evidence_to_calibration_signal,
    validate_calibration_evidence_input,
)
from mip.workflows.intake.readiness import build_calibration_signal_readiness_report

_NOW = datetime(2026, 5, 28, 12, 0, tzinfo=UTC)
_WINDOW_START = datetime(2025, 1, 1, tzinfo=UTC)
_WINDOW_END = datetime(2025, 6, 1, tzinfo=UTC)

_FORBIDDEN_FRAGMENTS = (
    "budget recommendation",
    "model refresh",
    "causal certification",
    "decision recommendation",
    "roi is",
    "optimizer",
)


def _evidence(**overrides: Any) -> CalibrationEvidenceInput:
    base: dict[str, Any] = {
        "input_id": "evidence-001",
        "metric_id": "revenue",
        "estimand_id": "incremental_revenue",
        "channel": "search",
        "platform": "google",
        "product_scope": "all_products",
        "geo_scope": "us",
        "time_window_start": _WINDOW_START,
        "time_window_end": _WINDOW_END,
        "effect_estimate": 0.12,
        "standard_error": 0.03,
        "lift_scale": "absolute",
        "evidence_type": "geox_readout",
        "is_causal": True,
        "freshness_status": "fresh",
        "source_artifact_id": "artifact-001",
        "source_experiment_id": "exp-001",
        "source_readout_id": "readout-001",
        "created_at": _NOW,
    }
    base.update(overrides)
    return CalibrationEvidenceInput(**base)


def _requirement(**overrides: Any) -> CalibrationMappingRequirement:
    base: dict[str, Any] = {
        "requirement_id": "req-001",
        "target_model_id": "mmm-001",
        "required_metric_id": "revenue",
        "required_estimand_id": "incremental_revenue",
        "required_channel": "search",
        "required_platform": "google",
        "required_product_scope": "all_products",
        "required_geo_scope": "us",
        "required_time_window_start": _WINDOW_START,
        "required_time_window_end": _WINDOW_END,
        "required_lift_scale": "absolute",
    }
    base.update(overrides)
    return CalibrationMappingRequirement(**base)


def _assert_no_forbidden_claims(*objects: Any) -> None:
    combined = " ".join(str(obj.model_dump()) for obj in objects).lower()
    for fragment in _FORBIDDEN_FRAGMENTS:
        assert fragment not in combined


def test_valid_evidence_maps_to_calibration_signal() -> None:
    evidence = _evidence()
    requirement = _requirement()
    signal, report = map_evidence_to_calibration_signal(evidence, requirement)
    assert signal is not None
    assert isinstance(signal, CalibrationSignal)
    assert report.status == CalibrationIntakeStatus.MAPPED
    assert report.mapped_signal_id == signal.calibration_id
    assert signal.source_evidence_id == "readout-001"
    assert signal.target_model_id == "mmm-001"
    assert signal.uncertainty == 0.03


def test_confidence_interval_without_se_needs_more_data() -> None:
    evidence = _evidence(
        standard_error=None,
        confidence_interval_low=0.08,
        confidence_interval_high=0.16,
    )
    requirement = _requirement()
    signal, report = map_evidence_to_calibration_signal(evidence, requirement)
    assert signal is None
    assert report.status == CalibrationIntakeStatus.NEEDS_MORE_DATA
    assert CalibrationIntakeBlockingReason.MISSING_UNCERTAINTY.value in report.blocking_reasons
    assert any(
        "standard_error" in warning.lower() or "ci" in warning.lower()
        for warning in report.warnings
    )


def test_missing_effect_estimate_blocks_mapping() -> None:
    evidence = _evidence(effect_estimate=None)
    report = validate_calibration_evidence_input(evidence, _requirement())
    assert report.status == CalibrationIntakeStatus.NEEDS_MORE_DATA
    assert CalibrationIntakeBlockingReason.MISSING_EFFECT_ESTIMATE.value in report.blocking_reasons


def test_missing_uncertainty_blocks_mapping() -> None:
    evidence = _evidence(
        standard_error=None,
        confidence_interval_low=None,
        confidence_interval_high=None,
    )
    report = validate_calibration_evidence_input(evidence, _requirement())
    assert report.status == CalibrationIntakeStatus.NEEDS_MORE_DATA
    assert CalibrationIntakeBlockingReason.MISSING_UNCERTAINTY.value in report.blocking_reasons


def test_missing_metric_id_blocks_mapping() -> None:
    evidence = _evidence(metric_id=None)
    report = validate_calibration_evidence_input(evidence, _requirement())
    assert CalibrationIntakeBlockingReason.MISSING_METRIC_MAPPING.value in report.blocking_reasons


def test_missing_estimand_id_blocks_mapping() -> None:
    evidence = _evidence(estimand_id=None)
    report = validate_calibration_evidence_input(evidence, _requirement())
    assert CalibrationIntakeBlockingReason.MISSING_ESTIMAND_MAPPING.value in report.blocking_reasons


def test_metric_mismatch_returns_incompatible() -> None:
    evidence = _evidence(metric_id="visits")
    report = validate_calibration_evidence_input(evidence, _requirement())
    assert report.status == CalibrationIntakeStatus.INCOMPATIBLE
    assert "metric_id" in report.incompatible_fields


def test_estimand_mismatch_returns_incompatible() -> None:
    evidence = _evidence(estimand_id="lift")
    report = validate_calibration_evidence_input(evidence, _requirement())
    assert report.status == CalibrationIntakeStatus.INCOMPATIBLE
    assert "estimand_id" in report.incompatible_fields


def test_lift_scale_mismatch_returns_incompatible() -> None:
    evidence = _evidence(lift_scale="relative")
    report = validate_calibration_evidence_input(
        evidence,
        _requirement(required_lift_scale="absolute"),
    )
    assert report.status == CalibrationIntakeStatus.INCOMPATIBLE
    assert "lift_scale" in report.incompatible_fields


def test_stale_evidence_blocks_when_not_allowed() -> None:
    evidence = _evidence(freshness_status="stale")
    report = validate_calibration_evidence_input(
        evidence,
        _requirement(allow_stale_evidence=False),
    )
    assert CalibrationIntakeBlockingReason.STALE_EVIDENCE.value in report.blocking_reasons


def test_non_causal_blocks_when_causal_required() -> None:
    evidence = _evidence(is_causal=False)
    report = validate_calibration_evidence_input(
        evidence,
        _requirement(require_causal_flag=True),
    )
    assert CalibrationIntakeBlockingReason.NOT_CAUSAL_EVIDENCE.value in report.blocking_reasons


def test_lineage_preserved_in_mapped_signal() -> None:
    evidence = _evidence(
        source_artifact_id="artifact-geo-001",
        source_readout_id="readout-geo-001",
        source_trust_report_id="trust-001",
    )
    signal, _report = map_evidence_to_calibration_signal(evidence, _requirement())
    assert signal is not None
    metrics = signal.diagnostics.metrics
    assert metrics.get("source_artifact_id") == "artifact-geo-001"
    assert metrics.get("source_readout_id") == "readout-geo-001"
    assert metrics.get("source_trust_report_id") == "trust-001"
    assert signal.source_evidence_id == "readout-geo-001"


def test_mapping_report_contains_next_steps() -> None:
    report = build_calibration_mapping_report(_evidence(), _requirement())
    assert report.allowed_next_steps
    assert "execute_mmm_calibration" in report.blocked_next_steps
    assert "claim_decision_recommendation" in report.blocked_next_steps


def test_missing_time_window_blocks_mapping() -> None:
    evidence = _evidence(time_window_start=None, time_window_end=None)
    report = validate_calibration_evidence_input(evidence, _requirement())
    assert CalibrationIntakeBlockingReason.MISSING_TIME_WINDOW.value in report.blocking_reasons


def test_mapping_forbidden_claims_absent() -> None:
    evidence = _evidence()
    signal, report = map_evidence_to_calibration_signal(evidence, _requirement())
    _assert_no_forbidden_claims(evidence, report, signal)
    forbidden = FORBIDDEN_CALIBRATION_INTAKE_RESULT_FIELD_NAMES
    assert forbidden.isdisjoint(report.model_dump().keys())
    if signal is not None:
        assert forbidden.isdisjoint(signal.model_dump().keys())


def test_readiness_and_mapping_are_complementary_layers() -> None:
    evidence = _evidence()
    report = validate_calibration_evidence_input(evidence, _requirement())
    assert report.alignment_passed is True
    assert callable(build_calibration_signal_readiness_report)
    assert CalibrationSignalReadinessReport is not None
