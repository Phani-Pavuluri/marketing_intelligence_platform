"""Tests for in-memory evidence registry."""

from datetime import UTC, datetime

import pytest

from mip.contracts import (
    ArtifactStatus,
    CausalQuantity,
    CompatibilityStatus,
    ConfidenceTier,
    DiagnosticSummary,
    ExperimentType,
    TimeWindow,
    TrustReport,
)
from mip.evidence import (
    DuplicateCalibrationSignalError,
    DuplicateEvidenceError,
    EvidenceRegistry,
    MissingCalibrationSignalError,
    MissingEvidenceError,
)
from tests.evidence.conftest import build_calibration, build_estimand, build_evidence


@pytest.fixture
def registry() -> EvidenceRegistry:
    return EvidenceRegistry()


def test_new_registry_is_empty() -> None:
    assert len(EvidenceRegistry()) == 0


def test_add_and_get_evidence(
    registry: EvidenceRegistry,
    time_window: TimeWindow,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    estimand = build_estimand(time_window)
    evidence = build_evidence(estimand, passing_diagnostics)
    registry.add_evidence(evidence)
    assert registry.get_evidence("exp-001") == evidence


def test_duplicate_evidence_raises(
    registry: EvidenceRegistry,
    time_window: TimeWindow,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    estimand = build_estimand(time_window)
    registry.add_evidence(build_evidence(estimand, passing_diagnostics))
    with pytest.raises(DuplicateEvidenceError):
        registry.add_evidence(build_evidence(estimand, passing_diagnostics))


def test_missing_evidence_raises(registry: EvidenceRegistry) -> None:
    with pytest.raises(MissingEvidenceError):
        registry.get_evidence("missing")
    with pytest.raises(MissingEvidenceError):
        registry.get_evidence("  ")


def test_add_and_get_calibration_signal(
    registry: EvidenceRegistry,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    signal = build_calibration(passing_diagnostics)
    registry.add_calibration_signal(signal)
    assert registry.get_calibration_signal("cal-001") == signal


def test_duplicate_calibration_signal_raises(
    registry: EvidenceRegistry,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    registry.add_calibration_signal(build_calibration(passing_diagnostics))
    with pytest.raises(DuplicateCalibrationSignalError):
        registry.add_calibration_signal(build_calibration(passing_diagnostics))


def test_missing_calibration_signal_raises(registry: EvidenceRegistry) -> None:
    with pytest.raises(MissingCalibrationSignalError):
        registry.get_calibration_signal("missing")
    with pytest.raises(MissingCalibrationSignalError):
        registry.get_calibration_signal("")


def test_list_evidence_sorted(
    registry: EvidenceRegistry,
    time_window: TimeWindow,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    early = build_evidence(
        build_estimand(time_window),
        passing_diagnostics,
        evidence_id="exp-b",
        created_at=datetime(2025, 1, 1, tzinfo=UTC),
    )
    same_time_a = build_evidence(
        build_estimand(time_window),
        passing_diagnostics,
        evidence_id="exp-a",
        created_at=datetime(2025, 6, 1, tzinfo=UTC),
    )
    same_time_z = build_evidence(
        build_estimand(time_window),
        passing_diagnostics,
        evidence_id="exp-z",
        created_at=datetime(2025, 6, 1, tzinfo=UTC),
    )
    registry.add_evidence(early)
    registry.add_evidence(same_time_z)
    registry.add_evidence(same_time_a)

    ids = [item.evidence_id for item in registry.list_evidence()]
    assert ids == ["exp-b", "exp-a", "exp-z"]


def test_list_calibration_signals_sorted(
    registry: EvidenceRegistry,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    registry.add_calibration_signal(
        build_calibration(passing_diagnostics, calibration_id="cal-b")
    )
    registry.add_calibration_signal(
        build_calibration(passing_diagnostics, calibration_id="cal-a")
    )
    ids = [item.calibration_id for item in registry.list_calibration_signals()]
    assert ids == ["cal-a", "cal-b"]


def test_find_evidence_by_experiment_type(
    registry: EvidenceRegistry,
    time_window: TimeWindow,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    geox = build_evidence(
        build_estimand(time_window),
        passing_diagnostics,
        evidence_id="exp-geox",
        experiment_type=ExperimentType.GEOX,
    )
    panel = build_evidence(
        build_estimand(time_window),
        passing_diagnostics,
        evidence_id="exp-panel",
        experiment_type=ExperimentType.PANEL,
    )
    registry.add_evidence(geox)
    registry.add_evidence(panel)
    found = registry.find_evidence(experiment_type=ExperimentType.PANEL)
    assert [item.evidence_id for item in found] == ["exp-panel"]


def test_find_evidence_by_target_metric(
    registry: EvidenceRegistry,
    time_window: TimeWindow,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    revenue = build_evidence(
        build_estimand(time_window, target_metric="revenue"),
        passing_diagnostics,
        evidence_id="exp-rev",
    )
    conversions = build_evidence(
        build_estimand(time_window, target_metric="conversions"),
        passing_diagnostics,
        evidence_id="exp-conv",
    )
    registry.add_evidence(revenue)
    registry.add_evidence(conversions)
    found = registry.find_evidence(target_metric="revenue")
    assert [item.evidence_id for item in found] == ["exp-rev"]


def test_find_evidence_by_causal_quantity(
    registry: EvidenceRegistry,
    time_window: TimeWindow,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    lift = build_evidence(
        build_estimand(time_window, causal_quantity=CausalQuantity.LIFT),
        passing_diagnostics,
        evidence_id="exp-lift",
    )
    delta = build_evidence(
        build_estimand(time_window, causal_quantity=CausalQuantity.DELTA_MU),
        passing_diagnostics,
        evidence_id="exp-delta",
    )
    registry.add_evidence(lift)
    registry.add_evidence(delta)
    found = registry.find_evidence(causal_quantity=CausalQuantity.DELTA_MU)
    assert [item.evidence_id for item in found] == ["exp-delta"]


def test_find_evidence_by_confidence_tier(
    registry: EvidenceRegistry,
    time_window: TimeWindow,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    directional = build_evidence(
        build_estimand(time_window),
        passing_diagnostics,
        evidence_id="exp-dir",
        confidence_tier=ConfidenceTier.DIRECTIONAL,
    )
    research = build_evidence(
        build_estimand(time_window),
        passing_diagnostics,
        evidence_id="exp-res",
        confidence_tier=ConfidenceTier.RESEARCH_ONLY,
    )
    registry.add_evidence(directional)
    registry.add_evidence(research)
    found = registry.find_evidence(confidence_tier=ConfidenceTier.RESEARCH_ONLY)
    assert [item.evidence_id for item in found] == ["exp-res"]


def test_find_evidence_by_status(
    registry: EvidenceRegistry,
    time_window: TimeWindow,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    validated = build_evidence(
        build_estimand(time_window),
        passing_diagnostics,
        evidence_id="exp-val",
        status=ArtifactStatus.VALIDATED,
    )
    draft = build_evidence(
        build_estimand(time_window),
        passing_diagnostics,
        evidence_id="exp-draft",
        status=ArtifactStatus.DRAFT,
    )
    registry.add_evidence(validated)
    registry.add_evidence(draft)
    found = registry.find_evidence(status=ArtifactStatus.DRAFT)
    assert [item.evidence_id for item in found] == ["exp-draft"]


def test_find_evidence_by_min_quality_score(
    registry: EvidenceRegistry,
    time_window: TimeWindow,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    high = build_evidence(
        build_estimand(time_window),
        passing_diagnostics,
        evidence_id="exp-high",
        quality_score=0.9,
    )
    low = build_evidence(
        build_estimand(time_window),
        passing_diagnostics,
        evidence_id="exp-low",
        quality_score=0.4,
    )
    registry.add_evidence(high)
    registry.add_evidence(low)
    found = registry.find_evidence(min_quality_score=0.8)
    assert [item.evidence_id for item in found] == ["exp-high"]


def test_find_evidence_by_min_freshness_score(
    registry: EvidenceRegistry,
    time_window: TimeWindow,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    fresh = build_evidence(
        build_estimand(time_window),
        passing_diagnostics,
        evidence_id="exp-fresh",
        freshness_score=0.9,
    )
    stale = build_evidence(
        build_estimand(time_window),
        passing_diagnostics,
        evidence_id="exp-stale",
        freshness_score=0.2,
    )
    registry.add_evidence(fresh)
    registry.add_evidence(stale)
    found = registry.find_evidence(min_freshness_score=0.5)
    assert [item.evidence_id for item in found] == ["exp-fresh"]


def test_find_evidence_by_scope_contains_string(
    registry: EvidenceRegistry,
    time_window: TimeWindow,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    match = build_evidence(
        build_estimand(time_window, scope={"country": "US"}),
        passing_diagnostics,
        evidence_id="exp-us",
    )
    other = build_evidence(
        build_estimand(time_window, scope={"country": "CA"}),
        passing_diagnostics,
        evidence_id="exp-ca",
    )
    registry.add_evidence(match)
    registry.add_evidence(other)
    found = registry.find_evidence(scope_contains={"country": "US"})
    assert [item.evidence_id for item in found] == ["exp-us"]


def test_find_evidence_by_scope_contains_list_membership(
    registry: EvidenceRegistry,
    time_window: TimeWindow,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    match = build_evidence(
        build_estimand(time_window, scope={"channel": ["search", "social"]}),
        passing_diagnostics,
        evidence_id="exp-match",
    )
    miss = build_evidence(
        build_estimand(time_window, scope={"channel": ["display"]}),
        passing_diagnostics,
        evidence_id="exp-miss",
    )
    registry.add_evidence(match)
    registry.add_evidence(miss)
    found = registry.find_evidence(scope_contains={"channel": "social"})
    assert [item.evidence_id for item in found] == ["exp-match"]


def test_find_evidence_multiple_filters_and(
    registry: EvidenceRegistry,
    time_window: TimeWindow,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    match = build_evidence(
        build_estimand(time_window, target_metric="revenue"),
        passing_diagnostics,
        evidence_id="exp-match",
        experiment_type=ExperimentType.GEOX,
        quality_score=0.9,
    )
    wrong_type = build_evidence(
        build_estimand(time_window, target_metric="revenue"),
        passing_diagnostics,
        evidence_id="exp-wrong-type",
        experiment_type=ExperimentType.PANEL,
        quality_score=0.9,
    )
    low_quality = build_evidence(
        build_estimand(time_window, target_metric="revenue"),
        passing_diagnostics,
        evidence_id="exp-low-quality",
        experiment_type=ExperimentType.GEOX,
        quality_score=0.4,
    )
    registry.add_evidence(match)
    registry.add_evidence(wrong_type)
    registry.add_evidence(low_quality)
    found = registry.find_evidence(
        experiment_type=ExperimentType.GEOX,
        target_metric="revenue",
        min_quality_score=0.8,
    )
    assert [item.evidence_id for item in found] == ["exp-match"]


def test_invalid_evidence_quality_threshold_raises(registry: EvidenceRegistry) -> None:
    with pytest.raises(ValueError, match="min_quality_score"):
        registry.find_evidence(min_quality_score=1.5)


def test_invalid_evidence_freshness_threshold_raises(registry: EvidenceRegistry) -> None:
    with pytest.raises(ValueError, match="min_freshness_score"):
        registry.find_evidence(min_freshness_score=-0.1)


def test_find_calibration_signals_by_source_evidence_id(
    registry: EvidenceRegistry,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    match = build_calibration(
        passing_diagnostics,
        calibration_id="cal-a",
        source_evidence_id="exp-100",
    )
    other = build_calibration(
        passing_diagnostics,
        calibration_id="cal-b",
        source_evidence_id="exp-200",
    )
    registry.add_calibration_signal(match)
    registry.add_calibration_signal(other)
    found = registry.find_calibration_signals(source_evidence_id="exp-100")
    assert [item.calibration_id for item in found] == ["cal-a"]


def test_find_calibration_signals_by_target_model_id(
    registry: EvidenceRegistry,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    match = build_calibration(
        passing_diagnostics,
        calibration_id="cal-a",
        target_model_id="mmm-001",
    )
    other = build_calibration(
        passing_diagnostics,
        calibration_id="cal-b",
        target_model_id="mmm-002",
    )
    registry.add_calibration_signal(match)
    registry.add_calibration_signal(other)
    found = registry.find_calibration_signals(target_model_id="mmm-002")
    assert [item.calibration_id for item in found] == ["cal-b"]


def test_find_calibration_signals_by_compatibility_status(
    registry: EvidenceRegistry,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    compatible = build_calibration(
        passing_diagnostics,
        calibration_id="cal-a",
        compatibility_status=CompatibilityStatus.COMPATIBLE,
    )
    unknown = build_calibration(
        passing_diagnostics,
        calibration_id="cal-b",
        compatibility_status=CompatibilityStatus.UNKNOWN,
    )
    registry.add_calibration_signal(compatible)
    registry.add_calibration_signal(unknown)
    found = registry.find_calibration_signals(compatibility_status=CompatibilityStatus.UNKNOWN)
    assert [item.calibration_id for item in found] == ["cal-b"]


def test_find_calibration_signals_by_min_weight(
    registry: EvidenceRegistry,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    heavy = build_calibration(passing_diagnostics, calibration_id="cal-heavy", weight=0.9)
    light = build_calibration(passing_diagnostics, calibration_id="cal-light", weight=0.2)
    registry.add_calibration_signal(heavy)
    registry.add_calibration_signal(light)
    found = registry.find_calibration_signals(min_weight=0.5)
    assert [item.calibration_id for item in found] == ["cal-heavy"]


def test_find_calibration_signals_by_confidence_tier(
    registry: EvidenceRegistry,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    directional = build_calibration(
        passing_diagnostics,
        calibration_id="cal-dir",
        confidence_tier=ConfidenceTier.DIRECTIONAL,
    )
    research = build_calibration(
        passing_diagnostics,
        calibration_id="cal-res",
        confidence_tier=ConfidenceTier.RESEARCH_ONLY,
    )
    registry.add_calibration_signal(directional)
    registry.add_calibration_signal(research)
    found = registry.find_calibration_signals(confidence_tier=ConfidenceTier.RESEARCH_ONLY)
    assert [item.calibration_id for item in found] == ["cal-res"]


def test_invalid_calibration_threshold_raises(registry: EvidenceRegistry) -> None:
    with pytest.raises(ValueError, match="min_weight"):
        registry.find_calibration_signals(min_weight=2.0)
    with pytest.raises(ValueError, match="min_freshness_decay"):
        registry.find_calibration_signals(min_freshness_decay=-0.5)


def test_trust_report_for_evidence_returns_trust_report(
    registry: EvidenceRegistry,
    time_window: TimeWindow,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    evidence = build_evidence(build_estimand(time_window), passing_diagnostics)
    registry.add_evidence(evidence)
    report = registry.trust_report_for_evidence("exp-001")
    assert isinstance(report, TrustReport)
    assert report.output_id == "exp-001"


def test_trust_report_for_calibration_signal_returns_trust_report(
    registry: EvidenceRegistry,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    signal = build_calibration(passing_diagnostics)
    registry.add_calibration_signal(signal)
    report = registry.trust_report_for_calibration_signal("cal-001")
    assert isinstance(report, TrustReport)
    assert report.output_id == "cal-001"


def test_len_counts_evidence_and_calibration_signals(
    registry: EvidenceRegistry,
    time_window: TimeWindow,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    registry.add_evidence(build_evidence(build_estimand(time_window), passing_diagnostics))
    registry.add_calibration_signal(build_calibration(passing_diagnostics))
    assert len(registry) == 2


def test_public_imports_from_mip_evidence() -> None:
    from mip.evidence import (
        DuplicateCalibrationSignalError as dup_cal,
    )
    from mip.evidence import (
        DuplicateEvidenceError as dup_ev,
    )
    from mip.evidence import (
        EvidenceRegistry as reg,
    )
    from mip.evidence import (
        MissingCalibrationSignalError as miss_cal,
    )
    from mip.evidence import (
        MissingEvidenceError as miss_ev,
    )

    assert issubclass(dup_ev, Exception)
    assert issubclass(dup_cal, Exception)
    assert issubclass(miss_ev, Exception)
    assert issubclass(miss_cal, Exception)
    assert reg() is not None
