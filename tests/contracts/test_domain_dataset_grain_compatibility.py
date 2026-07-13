"""Contract tests for domain dataset grain compatibility."""

from __future__ import annotations

import inspect

import mip.contracts as contracts
import mip.contracts.domain_dataset_grain_compatibility as grain_mod
from mip.contracts.domain_dataset_grain_compatibility import (
    DomainDatasetChannelGrain,
    DomainDatasetCompatibilityDecision,
    DomainDatasetCompatibilityStatus,
    DomainDatasetCompatibilityTarget,
    DomainDatasetConversionType,
    DomainDatasetGeoGrain,
    DomainDatasetGrainCompatibilityReport,
    DomainDatasetGrainConversionRule,
    DomainDatasetGrainIssueCode,
    DomainDatasetGrainSpec,
    DomainDatasetKPIGrain,
    DomainDatasetPanelGrain,
    DomainDatasetTimeGrain,
    build_domain_dataset_grain_compatibility_report,
    summarize_domain_dataset_grain_compatibility_report,
)


def _week_dma_channel_grain() -> DomainDatasetGrainSpec:
    return DomainDatasetGrainSpec(
        geo_grain=DomainDatasetGeoGrain.DMA.value,
        time_grain=DomainDatasetTimeGrain.WEEK.value,
        channel_grain=DomainDatasetChannelGrain.CHANNEL.value,
        panel_grain=DomainDatasetPanelGrain.TIME_GEO_CHANNEL.value,
        kpi_grain=DomainDatasetKPIGrain.TIME_GEO.value,
        geo_identifier_columns=("dma",),
        time_identifier_columns=("week",),
        channel_identifier_columns=("channel",),
        kpi_columns=("paid_conversions",),
        spend_columns=("spend",),
        control_columns=("holiday_flag",),
    )


def _week_dma_time_geo_grain() -> DomainDatasetGrainSpec:
    return DomainDatasetGrainSpec(
        geo_grain=DomainDatasetGeoGrain.DMA.value,
        time_grain=DomainDatasetTimeGrain.WEEK.value,
        channel_grain=DomainDatasetChannelGrain.NONE.value,
        panel_grain=DomainDatasetPanelGrain.TIME_GEO.value,
        kpi_grain=DomainDatasetKPIGrain.TIME_GEO.value,
        geo_identifier_columns=("dma",),
        time_identifier_columns=("week",),
        kpi_columns=("paid_conversions",),
        spend_columns=("search_spend", "meta_spend", "youtube_spend"),
        control_columns=("holiday_flag",),
    )


def test_required_enums_contain_required_values() -> None:
    assert {i.value for i in DomainDatasetGeoGrain} >= {
        "DMA",
        "STATE",
        "REGION",
        "COUNTRY",
        "ZIP",
        "COUNTY",
        "NONE",
        "UNKNOWN",
    }
    assert {i.value for i in DomainDatasetTimeGrain} >= {
        "DAY",
        "WEEK",
        "MONTH",
        "QUARTER",
        "NONE",
        "UNKNOWN",
    }
    assert {i.value for i in DomainDatasetChannelGrain} >= {
        "CHANNEL",
        "CHANNEL_GROUP",
        "NONE",
        "UNKNOWN",
    }
    assert {i.value for i in DomainDatasetKPIGrain} >= {
        "TIME_GEO",
        "TIME_GEO_CHANNEL",
        "TIME_CHANNEL",
        "TIME_ONLY",
        "GEO_ONLY",
        "ROW_LEVEL",
        "UNKNOWN",
    }
    assert {i.value for i in DomainDatasetPanelGrain} >= {
        "TIME_GEO",
        "TIME_GEO_CHANNEL",
        "TIME_CHANNEL",
        "TIME_ONLY",
        "GEO_ONLY",
        "CHANNEL_ONLY",
        "ROW_LEVEL",
        "UNKNOWN",
    }
    assert {i.value for i in DomainDatasetCompatibilityTarget} >= {
        "MMM_INPUT",
        "GEOX_DESIGN_INPUT",
        "CALIBRATION_SIGNAL_INPUT",
        "LLM_VISIBLE_METADATA",
    }
    assert {i.value for i in DomainDatasetCompatibilityStatus} >= {
        "COMPATIBLE_AS_IS",
        "COMPATIBLE_AFTER_CONVERSION",
        "BLOCKED_UNSAFE_GRAIN",
        "BLOCKED_INSUFFICIENT_GRAIN",
        "BLOCKED_UNSUPPORTED_GRAIN",
        "METADATA_ONLY",
        "UNKNOWN",
    }
    assert {i.value for i in DomainDatasetConversionType} >= {
        "PIVOT_CHANNEL_SPEND_WIDE",
        "AGGREGATE_CHANNEL_TO_TOTAL",
        "FILTER_TO_TEST_CHANNEL",
        "AGGREGATE_TIME_UP",
        "AGGREGATE_GEO_UP",
        "BROADCAST_CONTROL_TO_GEO_TIME",
        "KEEP_KPI_ONCE_PER_TIME_GEO",
        "NO_CONVERSION_REQUIRED",
        "BLOCKED_CONVERSION",
    }
    issues = {i.value for i in DomainDatasetGrainIssueCode}
    for required in (
        "RAW_GRAIN_CLASSIFIED",
        "KPI_GRAIN_CLASSIFIED",
        "MODEL_READY_GRAIN_DECLARED",
        "MMM_COMPATIBILITY_DECLARED",
        "GEOX_COMPATIBILITY_DECLARED",
        "LLM_METADATA_ONLY_DECLARED",
        "LONG_CHANNEL_PANEL_DETECTED",
        "KPI_REPEATED_ACROSS_CHANNELS",
        "KPI_DOUBLE_COUNT_RISK_BLOCKED",
        "MMM_REQUIRES_TIME_GEO_WIDE_OR_CONVERTIBLE",
        "GEOX_REQUIRES_TIME_GEO_DESIGN_PANEL",
        "DMA_GRAIN_SUPPORTED_FOR_US_FIXTURES",
        "STATE_TO_DMA_CONVERSION_BLOCKED",
        "DAY_TO_WEEK_AGGREGATION_ALLOWED",
        "WEEK_TO_DAY_DISAGGREGATION_BLOCKED",
        "CHANNEL_TAXONOMY_REQUIRED",
        "CONTROL_ALIGNMENT_REQUIRED",
        "NO_DATASET_GENERATION",
        "NO_MMM_FITTING",
        "NO_GEOX_ESTIMATOR_LOGIC",
        "NO_LLM_PROVIDER_EXECUTION",
        "NO_DECISION_SURFACE_GENERATION",
        "NO_RECOMMENDATION_GENERATION",
        "NO_ROI_ROAS_LIFT_INCREMENTALITY_COMPUTATION",
    ):
        assert required in issues


def test_grain_spec_serializes() -> None:
    payload = _week_dma_channel_grain().model_dump()
    assert payload["panel_grain"] == "TIME_GEO_CHANNEL"
    assert payload["kpi_grain"] == "TIME_GEO"


def test_conversion_rule_serializes() -> None:
    rule = DomainDatasetGrainConversionRule(
        conversion_type=DomainDatasetConversionType.PIVOT_CHANNEL_SPEND_WIDE.value,
        source_panel_grain=DomainDatasetPanelGrain.TIME_GEO_CHANNEL.value,
        target_panel_grain=DomainDatasetPanelGrain.TIME_GEO.value,
        allowed=True,
        reason="pivot spend",
    )
    assert rule.model_dump()["allowed"] is True


def test_compatibility_decision_serializes() -> None:
    decision = DomainDatasetCompatibilityDecision(
        target=DomainDatasetCompatibilityTarget.MMM_INPUT.value,
        status=DomainDatasetCompatibilityStatus.COMPATIBLE_AFTER_CONVERSION.value,
        required_conversions=(
            DomainDatasetConversionType.PIVOT_CHANNEL_SPEND_WIDE.value,
        ),
    )
    assert decision.model_dump()["target"] == "MMM_INPUT"


def test_report_serializes() -> None:
    report = build_domain_dataset_grain_compatibility_report(
        fixture_id="week_dma_channel_v1",
        raw_grain=_week_dma_channel_grain(),
        test_channel_available=True,
        us_fixture=True,
    )
    payload = report.model_dump()
    assert payload["fixture_id"] == "week_dma_channel_v1"
    assert payload["kpi_repeated_across_channels"] is True


def test_week_dma_channel_with_time_geo_kpi_blocks_mmm_as_is() -> None:
    report = build_domain_dataset_grain_compatibility_report(
        fixture_id="week_dma_channel_v1",
        raw_grain=_week_dma_channel_grain(),
        test_channel_available=True,
        us_fixture=True,
    )
    assert (
        report.mmm_decision.status
        != DomainDatasetCompatibilityStatus.COMPATIBLE_AS_IS.value
    )
    assert report.mmm_decision.metadata.get("compatible_as_is") is False


def test_week_dma_channel_mmm_compatible_after_pivot_and_keep_kpi() -> None:
    report = build_domain_dataset_grain_compatibility_report(
        fixture_id="week_dma_channel_v1",
        raw_grain=_week_dma_channel_grain(),
        test_channel_available=True,
    )
    assert (
        report.mmm_decision.status
        == DomainDatasetCompatibilityStatus.COMPATIBLE_AFTER_CONVERSION.value
    )
    assert DomainDatasetConversionType.PIVOT_CHANNEL_SPEND_WIDE.value in (
        report.mmm_decision.required_conversions
    )
    assert DomainDatasetConversionType.KEEP_KPI_ONCE_PER_TIME_GEO.value in (
        report.mmm_decision.required_conversions
    )


def test_week_dma_channel_marks_kpi_double_count_risk() -> None:
    report = build_domain_dataset_grain_compatibility_report(
        fixture_id="week_dma_channel_v1",
        raw_grain=_week_dma_channel_grain(),
        test_channel_available=True,
    )
    assert report.kpi_repeated_across_channels is True
    assert DomainDatasetGrainIssueCode.KPI_DOUBLE_COUNT_RISK_BLOCKED.value in (
        report.issues
    )
    assert DomainDatasetGrainIssueCode.KPI_DOUBLE_COUNT_RISK_BLOCKED.value in (
        report.mmm_decision.blocked_reasons
    )


def test_week_dma_channel_geox_after_filter_or_aggregate() -> None:
    report = build_domain_dataset_grain_compatibility_report(
        fixture_id="week_dma_channel_v1",
        raw_grain=_week_dma_channel_grain(),
        test_channel_available=True,
    )
    assert (
        report.geox_decision.status
        == DomainDatasetCompatibilityStatus.COMPATIBLE_AFTER_CONVERSION.value
    )
    assert DomainDatasetConversionType.FILTER_TO_TEST_CHANNEL.value in (
        report.geox_decision.required_conversions
    )
    assert DomainDatasetConversionType.AGGREGATE_CHANNEL_TO_TOTAL.value in (
        report.geox_decision.required_conversions
    )


def test_week_dma_geox_design_compatible_as_is() -> None:
    report = build_domain_dataset_grain_compatibility_report(
        fixture_id="week_dma_design_v1",
        raw_grain=_week_dma_time_geo_grain(),
        spend_already_wide=True,
    )
    assert (
        report.geox_decision.status
        == DomainDatasetCompatibilityStatus.COMPATIBLE_AS_IS.value
    )


def test_state_panel_blocked_for_dma_geox_request() -> None:
    grain = DomainDatasetGrainSpec(
        geo_grain=DomainDatasetGeoGrain.STATE.value,
        time_grain=DomainDatasetTimeGrain.WEEK.value,
        channel_grain=DomainDatasetChannelGrain.NONE.value,
        panel_grain=DomainDatasetPanelGrain.TIME_GEO.value,
        kpi_grain=DomainDatasetKPIGrain.TIME_GEO.value,
        geo_identifier_columns=("state",),
        time_identifier_columns=("week",),
        kpi_columns=("paid_conversions",),
    )
    report = build_domain_dataset_grain_compatibility_report(
        fixture_id="state_panel_v1",
        raw_grain=grain,
        requested_geox_geo_grain=DomainDatasetGeoGrain.DMA,
        spend_already_wide=True,
    )
    assert (
        report.geox_decision.status
        == DomainDatasetCompatibilityStatus.BLOCKED_UNSUPPORTED_GRAIN.value
    )
    assert DomainDatasetGrainIssueCode.STATE_TO_DMA_CONVERSION_BLOCKED.value in (
        report.issues
    )


def test_day_to_week_aggregation_allowed() -> None:
    grain = DomainDatasetGrainSpec(
        geo_grain=DomainDatasetGeoGrain.DMA.value,
        time_grain=DomainDatasetTimeGrain.DAY.value,
        channel_grain=DomainDatasetChannelGrain.NONE.value,
        panel_grain=DomainDatasetPanelGrain.TIME_GEO.value,
        kpi_grain=DomainDatasetKPIGrain.TIME_GEO.value,
        geo_identifier_columns=("dma",),
        time_identifier_columns=("day",),
        kpi_columns=("paid_conversions",),
        spend_columns=("search_spend",),
    )
    report = build_domain_dataset_grain_compatibility_report(
        fixture_id="day_dma_v1",
        raw_grain=grain,
        requested_mmm_time_grain=DomainDatasetTimeGrain.WEEK,
        requested_geox_time_grain=DomainDatasetTimeGrain.WEEK,
        spend_already_wide=True,
        us_fixture=True,
    )
    assert DomainDatasetConversionType.AGGREGATE_TIME_UP.value in (
        report.mmm_decision.required_conversions
    )
    assert DomainDatasetGrainIssueCode.DAY_TO_WEEK_AGGREGATION_ALLOWED.value in (
        report.issues
    )
    assert any(
        rule.conversion_type == DomainDatasetConversionType.AGGREGATE_TIME_UP.value
        and rule.allowed
        for rule in report.conversion_rules
    )


def test_week_to_day_disaggregation_blocked() -> None:
    report = build_domain_dataset_grain_compatibility_report(
        fixture_id="week_dma_design_v1",
        raw_grain=_week_dma_time_geo_grain(),
        requested_mmm_time_grain=DomainDatasetTimeGrain.DAY,
        requested_geox_time_grain=DomainDatasetTimeGrain.DAY,
        spend_already_wide=True,
    )
    assert (
        report.mmm_decision.status
        == DomainDatasetCompatibilityStatus.BLOCKED_UNSUPPORTED_GRAIN.value
    )
    assert DomainDatasetGrainIssueCode.WEEK_TO_DAY_DISAGGREGATION_BLOCKED.value in (
        report.issues
    )


def test_llm_decision_is_metadata_only() -> None:
    report = build_domain_dataset_grain_compatibility_report(
        fixture_id="week_dma_channel_v1",
        raw_grain=_week_dma_channel_grain(),
        test_channel_available=True,
    )
    assert (
        report.llm_metadata_decision.status
        == DomainDatasetCompatibilityStatus.METADATA_ONLY.value
    )
    assert report.llm_metadata_decision.metadata.get("raw_data_exposed") is False


def test_dma_geo_grain_supported_for_us_fixtures() -> None:
    report = build_domain_dataset_grain_compatibility_report(
        fixture_id="week_dma_channel_v1",
        raw_grain=_week_dma_channel_grain(),
        test_channel_available=True,
        us_fixture=True,
    )
    assert DomainDatasetGrainIssueCode.DMA_GRAIN_SUPPORTED_FOR_US_FIXTURES.value in (
        report.issues
    )


def test_channel_taxonomy_requirement_represented() -> None:
    report = build_domain_dataset_grain_compatibility_report(
        fixture_id="week_dma_channel_v1",
        raw_grain=_week_dma_channel_grain(),
        test_channel_available=True,
        channel_taxonomy_present=False,
    )
    assert DomainDatasetGrainIssueCode.CHANNEL_TAXONOMY_REQUIRED.value in report.issues


def test_control_alignment_requirement_represented() -> None:
    report = build_domain_dataset_grain_compatibility_report(
        fixture_id="week_dma_channel_v1",
        raw_grain=_week_dma_channel_grain(),
        test_channel_available=True,
        control_alignment_present=False,
    )
    assert DomainDatasetGrainIssueCode.CONTROL_ALIGNMENT_REQUIRED.value in report.issues


def test_summary_helper_returns_counts_flags_only() -> None:
    report = build_domain_dataset_grain_compatibility_report(
        fixture_id="week_dma_channel_v1",
        raw_grain=_week_dma_channel_grain(),
        test_channel_available=True,
        us_fixture=True,
    )
    summary = summarize_domain_dataset_grain_compatibility_report(report)
    assert summary["fixture_id"] == "week_dma_channel_v1"
    assert summary["kpi_repeated_across_channels"] is True
    assert summary["llm_metadata_only"] is True
    assert "dataframe" not in summary
    assert "recommendation" not in summary
    assert "rows" not in summary


def test_no_dataset_generation_functions_or_fields() -> None:
    source = inspect.getsource(grain_mod)
    for token in (
        "def generate_",  # forbidden
        "pd.read",  # forbidden
        "pandas",  # forbidden
        "open(",  # forbidden
        "read_text",  # forbidden
        "json.load",  # forbidden
    ):
        assert token not in source
    assert "NO_DATASET_GENERATION" in {
        i.value for i in DomainDatasetGrainIssueCode
    }
    fields = set(DomainDatasetGrainCompatibilityReport.model_fields)
    assert "rows" not in fields
    assert "dataframe" not in fields


def test_no_mmm_fitting_or_geox_estimator_logic() -> None:
    source = inspect.getsource(grain_mod)
    for token in (
        "def fit(",  # forbidden
        ".fit(",  # forbidden
        "predict(",  # forbidden
        "sample(",  # forbidden
        "optimize(",  # forbidden
    ):
        assert token not in source


def test_no_decision_surface_rec_contract_or_opt_fields() -> None:
    fields = set(DomainDatasetGrainCompatibilityReport.model_fields)
    for token in (
        "decision_surface",  # forbidden
        "trust_report",  # forbidden
        "recommendation_contract",  # forbidden
        "optimizer",  # forbidden
        "simulator",  # forbidden
    ):
        assert token not in fields
    source = inspect.getsource(grain_mod)
    assert "DecisionSurface(" not in source  # forbidden
    assert "RecommendationContract(" not in source  # forbidden


def test_no_roi_roas_lift_incrementality_fields() -> None:
    fields = set(DomainDatasetGrainCompatibilityReport.model_fields)
    for token in ("roi", "roas", "lift", "incrementality", "recommended_budget"):
        assert token not in fields  # forbidden


def test_exported_from_mip_contracts() -> None:
    assert (
        contracts.DomainDatasetGrainCompatibilityReport
        is DomainDatasetGrainCompatibilityReport
    )
    assert contracts.DomainDatasetGeoGrain is DomainDatasetGeoGrain
    assert contracts.build_domain_dataset_grain_compatibility_report is (
        build_domain_dataset_grain_compatibility_report
    )
    assert contracts.summarize_domain_dataset_grain_compatibility_report is (
        summarize_domain_dataset_grain_compatibility_report
    )
    assert "DomainDatasetGrainCompatibilityReport" in contracts.__all__
    assert "build_domain_dataset_grain_compatibility_report" in contracts.__all__
