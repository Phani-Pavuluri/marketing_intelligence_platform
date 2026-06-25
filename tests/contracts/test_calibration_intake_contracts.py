"""Tests for CalibrationSignal intake mapping contracts."""

from datetime import UTC, datetime
from typing import Any

import pytest
from pydantic import ValidationError

from mip.contracts.calibration_intake import (
    FORBIDDEN_CALIBRATION_INTAKE_RESULT_FIELD_NAMES,
    CalibrationEvidenceInput,
    CalibrationIntakeStatus,
    CalibrationMappingReport,
    CalibrationMappingRequirement,
)

_NOW = datetime(2026, 5, 28, 12, 0, tzinfo=UTC)
_WINDOW_START = datetime(2025, 1, 1, tzinfo=UTC)
_WINDOW_END = datetime(2025, 6, 1, tzinfo=UTC)


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


def test_calibration_evidence_input_constructs() -> None:
    evidence = _evidence()
    assert evidence.input_id == "evidence-001"
    assert evidence.effect_estimate == 0.12


def test_mapping_report_mapped_requires_signal_id() -> None:
    with pytest.raises(ValidationError, match="mapped_signal_id"):
        CalibrationMappingReport(
            report_id="rep-001",
            input_id="evidence-001",
            status=CalibrationIntakeStatus.MAPPED,
            created_at=_NOW,
        )


def test_mapping_report_rejects_forbidden_claims() -> None:
    with pytest.raises(ValidationError, match="forbidden claim"):
        CalibrationMappingReport(
            report_id="rep-001",
            input_id="evidence-001",
            warnings=["This budget recommendation is final."],
            created_at=_NOW,
        )


def test_forbidden_result_field_names_documented() -> None:
    assert "roi_estimate" in FORBIDDEN_CALIBRATION_INTAKE_RESULT_FIELD_NAMES
    assert "budget_recommendation" in FORBIDDEN_CALIBRATION_INTAKE_RESULT_FIELD_NAMES


def test_mapping_report_has_no_forbidden_result_fields() -> None:
    report = CalibrationMappingReport(
        report_id="rep-001",
        input_id="evidence-001",
        status=CalibrationIntakeStatus.DRAFT,
        created_at=_NOW,
    )
    assert FORBIDDEN_CALIBRATION_INTAKE_RESULT_FIELD_NAMES.isdisjoint(report.model_dump().keys())
