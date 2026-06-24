"""Tests for public mip.workflows.readiness exports."""


def test_public_imports() -> None:
    from mip.workflows.readiness import (
        DataReadinessReport,
        DataReadinessStatus,
        DatasetProfile,
        DetectedTimeGrain,
        ReadinessCheckCode,
        ReadinessCheckResult,
        ReadinessSeverity,
        build_data_readiness_report,
        build_readiness_from_records,
        profile_from_records,
        profile_to_availability,
        run_readiness_checks,
    )

    assert DetectedTimeGrain.WEEKLY.value == "weekly"
    assert DataReadinessStatus.READY.value == "ready"
    assert ReadinessSeverity.BLOCKER.value == "blocker"
    assert ReadinessCheckCode.READY.value == "ready"
    assert callable(profile_from_records)
    assert callable(profile_to_availability)
    assert callable(run_readiness_checks)
    assert callable(build_data_readiness_report)
    assert callable(build_readiness_from_records)
    assert DatasetProfile is not None
    assert DataReadinessReport is not None
    assert ReadinessCheckResult is not None
