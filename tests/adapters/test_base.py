"""Tests for shared adapter contracts."""

import pytest

from mip.adapters.base import (
    AdapterOutputBundle,
    AdapterRunKind,
    AdapterRunStatus,
    AdapterValidationReport,
    validate_adapter_output,
)
from mip.adapters.mmm import MMMAdapterOutputPlaceholder


def test_completed_output_requires_validation_report() -> None:
    with pytest.raises(ValueError, match="requires validation report"):
        AdapterOutputBundle(
            kind=AdapterRunKind.MMM,
            status=AdapterRunStatus.COMPLETED,
            source_config_marker="marker-1",
            mmm_output=MMMAdapterOutputPlaceholder(config_marker="marker-1"),
        )


def test_failed_output_requires_reason() -> None:
    with pytest.raises(ValueError, match="requires reason"):
        AdapterOutputBundle(
            kind=AdapterRunKind.MMM,
            status=AdapterRunStatus.FAILED,
            source_config_marker="marker-1",
            mmm_output=MMMAdapterOutputPlaceholder(config_marker="marker-1"),
        )


def test_validate_adapter_output_rejects_forbidden_claim_text() -> None:
    output = AdapterOutputBundle(
        kind=AdapterRunKind.MMM,
        status=AdapterRunStatus.FAILED,
        source_config_marker="marker-1",
        reason="estimated lift from model results",
        mmm_output=MMMAdapterOutputPlaceholder(config_marker="marker-1"),
    )
    with pytest.raises(ValueError, match="forbidden claim phrase"):
        validate_adapter_output(output)


def test_validate_adapter_output_accepts_completed_bundle() -> None:
    output = AdapterOutputBundle(
        kind=AdapterRunKind.MMM,
        status=AdapterRunStatus.COMPLETED,
        source_config_marker="marker-1",
        validation=AdapterValidationReport(
            status=AdapterRunStatus.COMPLETED,
            passed_checks=["placeholder_only"],
        ),
        mmm_output=MMMAdapterOutputPlaceholder(config_marker="marker-1"),
    )
    report = validate_adapter_output(output)
    assert report.status == AdapterRunStatus.COMPLETED
