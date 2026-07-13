"""Domain dataset grain compatibility contracts (metadata only).

Classifies raw panel/KPI grain, declares allowed/blocked conversions, and
blocks unsafe MMM/GeoX model input when grain would double-count KPIs.

Does not generate datasets, fit MMM models, run GeoX estimators, call LLM
providers, construct DecisionSurface/TrustReport/RecommendationContract, or
compute ROI/ROAS/lift/incrementality.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from enum import StrEnum
from typing import Any

from pydantic import Field, field_validator

from mip.contracts.base import ContractBaseModel

ARTIFACT_ID = "MIP_DOMAIN_DATASET_GRAIN_COMPATIBILITY_CONTRACT_001"
CONTRACT_MODULE = "mip.contracts.domain_dataset_grain_compatibility"
RECOMMENDED_NEXT_ARTIFACT = "MIP_DEMO_DOMAIN_DATASETS_001"
DOMAIN_DATASET_GRAIN_COMPATIBILITY_CONTRACT_ARTIFACT_ID = ARTIFACT_ID
RECOMMENDED_NEXT_DOMAIN_DATASET_GRAIN_COMPATIBILITY_ARTIFACT = (
    RECOMMENDED_NEXT_ARTIFACT
)

_BASE_ISSUES: tuple[str, ...] = (
    "RAW_GRAIN_CLASSIFIED",
    "KPI_GRAIN_CLASSIFIED",
    "MODEL_READY_GRAIN_DECLARED",
    "MMM_COMPATIBILITY_DECLARED",
    "GEOX_COMPATIBILITY_DECLARED",
    "LLM_METADATA_ONLY_DECLARED",
    "NO_DATASET_GENERATION",
    "NO_MMM_FITTING",
    "NO_GEOX_ESTIMATOR_LOGIC",
    "NO_LLM_PROVIDER_EXECUTION",
    "NO_DECISION_SURFACE_GENERATION",
    "NO_RECOMMENDATION_GENERATION",
    "NO_ROI_ROAS_LIFT_INCREMENTALITY_COMPUTATION",
)


class DomainDatasetGeoGrain(StrEnum):
    """Geographic grain of a domain dataset panel."""

    DMA = "DMA"
    STATE = "STATE"
    REGION = "REGION"
    COUNTRY = "COUNTRY"
    ZIP = "ZIP"
    COUNTY = "COUNTY"
    NONE = "NONE"
    UNKNOWN = "UNKNOWN"


class DomainDatasetTimeGrain(StrEnum):
    """Temporal grain of a domain dataset panel."""

    DAY = "DAY"
    WEEK = "WEEK"
    MONTH = "MONTH"
    QUARTER = "QUARTER"
    NONE = "NONE"
    UNKNOWN = "UNKNOWN"


class DomainDatasetChannelGrain(StrEnum):
    """Channel grain of a domain dataset panel."""

    CHANNEL = "CHANNEL"
    CHANNEL_GROUP = "CHANNEL_GROUP"
    NONE = "NONE"
    UNKNOWN = "UNKNOWN"


class DomainDatasetKPIGrain(StrEnum):
    """Grain at which KPI values are uniquely defined."""

    TIME_GEO = "TIME_GEO"
    TIME_GEO_CHANNEL = "TIME_GEO_CHANNEL"
    TIME_CHANNEL = "TIME_CHANNEL"
    TIME_ONLY = "TIME_ONLY"
    GEO_ONLY = "GEO_ONLY"
    ROW_LEVEL = "ROW_LEVEL"
    UNKNOWN = "UNKNOWN"


class DomainDatasetPanelGrain(StrEnum):
    """Row grain of the panel (identifiers present per row)."""

    TIME_GEO = "TIME_GEO"
    TIME_GEO_CHANNEL = "TIME_GEO_CHANNEL"
    TIME_CHANNEL = "TIME_CHANNEL"
    TIME_ONLY = "TIME_ONLY"
    GEO_ONLY = "GEO_ONLY"
    CHANNEL_ONLY = "CHANNEL_ONLY"
    ROW_LEVEL = "ROW_LEVEL"
    UNKNOWN = "UNKNOWN"


class DomainDatasetCompatibilityTarget(StrEnum):
    """Downstream consumption target for grain compatibility."""

    MMM_INPUT = "MMM_INPUT"
    GEOX_DESIGN_INPUT = "GEOX_DESIGN_INPUT"
    CALIBRATION_SIGNAL_INPUT = "CALIBRATION_SIGNAL_INPUT"
    LLM_VISIBLE_METADATA = "LLM_VISIBLE_METADATA"


class DomainDatasetCompatibilityStatus(StrEnum):
    """Compatibility outcome for a target."""

    COMPATIBLE_AS_IS = "COMPATIBLE_AS_IS"
    COMPATIBLE_AFTER_CONVERSION = "COMPATIBLE_AFTER_CONVERSION"
    BLOCKED_UNSAFE_GRAIN = "BLOCKED_UNSAFE_GRAIN"
    BLOCKED_INSUFFICIENT_GRAIN = "BLOCKED_INSUFFICIENT_GRAIN"
    BLOCKED_UNSUPPORTED_GRAIN = "BLOCKED_UNSUPPORTED_GRAIN"
    METADATA_ONLY = "METADATA_ONLY"
    UNKNOWN = "UNKNOWN"


class DomainDatasetConversionType(StrEnum):
    """Allowed or blocked grain conversion operations."""

    PIVOT_CHANNEL_SPEND_WIDE = "PIVOT_CHANNEL_SPEND_WIDE"
    AGGREGATE_CHANNEL_TO_TOTAL = "AGGREGATE_CHANNEL_TO_TOTAL"
    FILTER_TO_TEST_CHANNEL = "FILTER_TO_TEST_CHANNEL"
    AGGREGATE_TIME_UP = "AGGREGATE_TIME_UP"
    AGGREGATE_GEO_UP = "AGGREGATE_GEO_UP"
    BROADCAST_CONTROL_TO_GEO_TIME = "BROADCAST_CONTROL_TO_GEO_TIME"
    KEEP_KPI_ONCE_PER_TIME_GEO = "KEEP_KPI_ONCE_PER_TIME_GEO"
    NO_CONVERSION_REQUIRED = "NO_CONVERSION_REQUIRED"
    BLOCKED_CONVERSION = "BLOCKED_CONVERSION"


class DomainDatasetGrainIssueCode(StrEnum):
    """Deterministic grain-compatibility issue codes."""

    RAW_GRAIN_CLASSIFIED = "RAW_GRAIN_CLASSIFIED"
    KPI_GRAIN_CLASSIFIED = "KPI_GRAIN_CLASSIFIED"
    MODEL_READY_GRAIN_DECLARED = "MODEL_READY_GRAIN_DECLARED"
    MMM_COMPATIBILITY_DECLARED = "MMM_COMPATIBILITY_DECLARED"
    GEOX_COMPATIBILITY_DECLARED = "GEOX_COMPATIBILITY_DECLARED"
    LLM_METADATA_ONLY_DECLARED = "LLM_METADATA_ONLY_DECLARED"
    LONG_CHANNEL_PANEL_DETECTED = "LONG_CHANNEL_PANEL_DETECTED"
    KPI_REPEATED_ACROSS_CHANNELS = "KPI_REPEATED_ACROSS_CHANNELS"
    KPI_DOUBLE_COUNT_RISK_BLOCKED = "KPI_DOUBLE_COUNT_RISK_BLOCKED"
    MMM_REQUIRES_TIME_GEO_WIDE_OR_CONVERTIBLE = (
        "MMM_REQUIRES_TIME_GEO_WIDE_OR_CONVERTIBLE"
    )
    GEOX_REQUIRES_TIME_GEO_DESIGN_PANEL = "GEOX_REQUIRES_TIME_GEO_DESIGN_PANEL"
    DMA_GRAIN_SUPPORTED_FOR_US_FIXTURES = "DMA_GRAIN_SUPPORTED_FOR_US_FIXTURES"
    STATE_TO_DMA_CONVERSION_BLOCKED = "STATE_TO_DMA_CONVERSION_BLOCKED"
    DAY_TO_WEEK_AGGREGATION_ALLOWED = "DAY_TO_WEEK_AGGREGATION_ALLOWED"
    WEEK_TO_DAY_DISAGGREGATION_BLOCKED = "WEEK_TO_DAY_DISAGGREGATION_BLOCKED"
    CHANNEL_TAXONOMY_REQUIRED = "CHANNEL_TAXONOMY_REQUIRED"
    CONTROL_ALIGNMENT_REQUIRED = "CONTROL_ALIGNMENT_REQUIRED"
    NO_DATASET_GENERATION = "NO_DATASET_GENERATION"
    NO_MMM_FITTING = "NO_MMM_FITTING"
    NO_GEOX_ESTIMATOR_LOGIC = "NO_GEOX_ESTIMATOR_LOGIC"
    NO_LLM_PROVIDER_EXECUTION = "NO_LLM_PROVIDER_EXECUTION"
    NO_DECISION_SURFACE_GENERATION = "NO_DECISION_SURFACE_GENERATION"
    NO_RECOMMENDATION_GENERATION = "NO_RECOMMENDATION_GENERATION"
    NO_ROI_ROAS_LIFT_INCREMENTALITY_COMPUTATION = (
        "NO_ROI_ROAS_LIFT_INCREMENTALITY_COMPUTATION"
    )


class DomainDatasetGrainSpec(ContractBaseModel):
    """Declared grain metadata for a domain dataset panel."""

    geo_grain: str
    time_grain: str
    channel_grain: str
    panel_grain: str
    kpi_grain: str
    geo_identifier_columns: tuple[str, ...] = ()
    time_identifier_columns: tuple[str, ...] = ()
    channel_identifier_columns: tuple[str, ...] = ()
    kpi_columns: tuple[str, ...] = ()
    spend_columns: tuple[str, ...] = ()
    control_columns: tuple[str, ...] = ()
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)

    @field_validator(
        "geo_grain",
        "time_grain",
        "channel_grain",
        "panel_grain",
        "kpi_grain",
    )
    @classmethod
    def required_text_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "grain fields cannot be empty"
            raise ValueError(msg)
        return value


class DomainDatasetGrainConversionRule(ContractBaseModel):
    """Allowed or blocked conversion between panel grains."""

    conversion_type: str
    source_panel_grain: str
    target_panel_grain: str
    allowed: bool
    reason: str = ""
    required_columns: tuple[str, ...] = ()
    blocked_reason: str = ""
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)

    @field_validator("conversion_type", "source_panel_grain", "target_panel_grain")
    @classmethod
    def required_text_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "conversion identity fields cannot be empty"
            raise ValueError(msg)
        return value


class DomainDatasetCompatibilityDecision(ContractBaseModel):
    """Compatibility decision for one downstream target."""

    target: str
    status: str
    source_grain: DomainDatasetGrainSpec | None = None
    target_grain: DomainDatasetGrainSpec | None = None
    required_conversions: tuple[str, ...] = ()
    blocked_reasons: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    issues: tuple[str, ...] = ()
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)

    @field_validator("target", "status")
    @classmethod
    def required_text_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "target and status cannot be empty"
            raise ValueError(msg)
        return value


class DomainDatasetGrainCompatibilityReport(ContractBaseModel):
    """Grain classification and compatibility report (no data payload)."""

    fixture_id: str
    raw_grain: DomainDatasetGrainSpec
    kpi_repeated_across_channels: bool = False
    mmm_decision: DomainDatasetCompatibilityDecision
    geox_decision: DomainDatasetCompatibilityDecision
    calibration_signal_decision: DomainDatasetCompatibilityDecision
    llm_metadata_decision: DomainDatasetCompatibilityDecision
    conversion_rules: tuple[DomainDatasetGrainConversionRule, ...] = ()
    issues: tuple[str, ...] = ()
    lineage: Mapping[str, Any] = Field(default_factory=dict)
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)

    @field_validator("fixture_id")
    @classmethod
    def fixture_id_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "fixture_id cannot be empty"
            raise ValueError(msg)
        return value


def build_domain_dataset_grain_compatibility_report(
    *,
    fixture_id: str,
    raw_grain: DomainDatasetGrainSpec,
    requested_mmm_geo_grain: DomainDatasetGeoGrain | str | None = None,
    requested_geox_geo_grain: DomainDatasetGeoGrain | str | None = None,
    requested_mmm_time_grain: DomainDatasetTimeGrain | str | None = None,
    requested_geox_time_grain: DomainDatasetTimeGrain | str | None = None,
    test_channel_available: bool = False,
    spend_already_wide: bool = False,
    channel_taxonomy_present: bool = True,
    control_alignment_present: bool = True,
    us_fixture: bool = False,
    lineage: Mapping[str, Any] | None = None,
    metadata: dict[str, str | int | float | bool] | None = None,
) -> DomainDatasetGrainCompatibilityReport:
    """Build a metadata-only grain compatibility report with deterministic rules."""

    issues: list[str] = list(_BASE_ISSUES)
    conversion_rules: list[DomainDatasetGrainConversionRule] = []

    panel = _enum_value(raw_grain.panel_grain)
    kpi = _enum_value(raw_grain.kpi_grain)
    geo = _enum_value(raw_grain.geo_grain)
    time = _enum_value(raw_grain.time_grain)
    channel = _enum_value(raw_grain.channel_grain)

    kpi_repeated = (
        panel == DomainDatasetPanelGrain.TIME_GEO_CHANNEL.value
        and kpi == DomainDatasetKPIGrain.TIME_GEO.value
    )
    if kpi_repeated:
        issues.extend(
            (
                DomainDatasetGrainIssueCode.LONG_CHANNEL_PANEL_DETECTED.value,
                DomainDatasetGrainIssueCode.KPI_REPEATED_ACROSS_CHANNELS.value,
                DomainDatasetGrainIssueCode.KPI_DOUBLE_COUNT_RISK_BLOCKED.value,
            )
        )

    if us_fixture and geo == DomainDatasetGeoGrain.DMA.value:
        issues.append(
            DomainDatasetGrainIssueCode.DMA_GRAIN_SUPPORTED_FOR_US_FIXTURES.value
        )

    if not channel_taxonomy_present and channel in {
        DomainDatasetChannelGrain.CHANNEL.value,
        DomainDatasetChannelGrain.CHANNEL_GROUP.value,
    }:
        issues.append(DomainDatasetGrainIssueCode.CHANNEL_TAXONOMY_REQUIRED.value)

    if not control_alignment_present and raw_grain.control_columns:
        issues.append(DomainDatasetGrainIssueCode.CONTROL_ALIGNMENT_REQUIRED.value)

    req_mmm_geo = (
        _enum_value(requested_mmm_geo_grain)
        if requested_mmm_geo_grain is not None
        else geo
    )
    req_geox_geo = (
        _enum_value(requested_geox_geo_grain)
        if requested_geox_geo_grain is not None
        else geo
    )
    req_mmm_time = (
        _enum_value(requested_mmm_time_grain)
        if requested_mmm_time_grain is not None
        else time
    )
    req_geox_time = (
        _enum_value(requested_geox_time_grain)
        if requested_geox_time_grain is not None
        else time
    )

    mmm_decision, mmm_rules, mmm_issues = _decide_mmm(
        raw_grain=raw_grain,
        panel=panel,
        kpi=kpi,
        channel=channel,
        geo=geo,
        time=time,
        requested_geo=req_mmm_geo,
        requested_time=req_mmm_time,
        spend_already_wide=spend_already_wide,
        kpi_repeated=kpi_repeated,
    )
    conversion_rules.extend(mmm_rules)
    issues.extend(mmm_issues)

    geox_decision, geox_rules, geox_issues = _decide_geox(
        raw_grain=raw_grain,
        panel=panel,
        geo=geo,
        time=time,
        requested_geo=req_geox_geo,
        requested_time=req_geox_time,
        test_channel_available=test_channel_available,
    )
    conversion_rules.extend(geox_rules)
    issues.extend(geox_issues)

    calibration_decision = _decide_calibration(raw_grain=raw_grain, panel=panel)
    llm_decision = DomainDatasetCompatibilityDecision(
        target=DomainDatasetCompatibilityTarget.LLM_VISIBLE_METADATA.value,
        status=DomainDatasetCompatibilityStatus.METADATA_ONLY.value,
        source_grain=raw_grain,
        target_grain=None,
        required_conversions=(
            DomainDatasetConversionType.NO_CONVERSION_REQUIRED.value,
        ),
        warnings=("LLM may consume grain metadata only; no raw panel exposure",),
        issues=(DomainDatasetGrainIssueCode.LLM_METADATA_ONLY_DECLARED.value,),
        metadata={"raw_data_exposed": False, "model_ready_data_exposed": False},
    )

    conversion_rules.extend(
        _time_conversion_rules(
            source_time=time,
            target_time=req_mmm_time,
            source_panel=panel,
        )
    )
    conversion_rules.extend(
        _time_conversion_rules(
            source_time=time,
            target_time=req_geox_time,
            source_panel=panel,
        )
    )
    for rule in conversion_rules:
        if (
            rule.conversion_type
            == DomainDatasetConversionType.AGGREGATE_TIME_UP.value
            and rule.allowed
        ):
            issues.append(
                DomainDatasetGrainIssueCode.DAY_TO_WEEK_AGGREGATION_ALLOWED.value
            )
        if (
            not rule.allowed
            and rule.blocked_reason
            == DomainDatasetGrainIssueCode.WEEK_TO_DAY_DISAGGREGATION_BLOCKED.value
        ):
            issues.append(
                DomainDatasetGrainIssueCode.WEEK_TO_DAY_DISAGGREGATION_BLOCKED.value
            )

    deduped_issues = tuple(dict.fromkeys(issues))
    deduped_rules = _dedupe_rules(conversion_rules)

    return DomainDatasetGrainCompatibilityReport(
        fixture_id=fixture_id,
        raw_grain=raw_grain,
        kpi_repeated_across_channels=kpi_repeated,
        mmm_decision=mmm_decision,
        geox_decision=geox_decision,
        calibration_signal_decision=calibration_decision,
        llm_metadata_decision=llm_decision,
        conversion_rules=deduped_rules,
        issues=deduped_issues,
        lineage={
            "artifact_id": ARTIFACT_ID,
            "contract_module": CONTRACT_MODULE,
            "dataset_generation_implemented": False,
            "mmm_fitting_implemented": False,
            "geox_estimator_logic_implemented": False,
            **dict(lineage or {}),
        },
        metadata={
            **(metadata or {}),
            "grain_contract_only": True,
            "model_ready_grain_declared": True,
        },
    )


def summarize_domain_dataset_grain_compatibility_report(
    report: DomainDatasetGrainCompatibilityReport,
) -> dict[str, object]:
    """Return counts/flags only — no raw panel rows or recommendations."""

    return {
        "fixture_id": report.fixture_id,
        "panel_grain": report.raw_grain.panel_grain,
        "kpi_grain": report.raw_grain.kpi_grain,
        "geo_grain": report.raw_grain.geo_grain,
        "time_grain": report.raw_grain.time_grain,
        "kpi_repeated_across_channels": report.kpi_repeated_across_channels,
        "mmm_status": report.mmm_decision.status,
        "geox_status": report.geox_decision.status,
        "calibration_status": report.calibration_signal_decision.status,
        "llm_status": report.llm_metadata_decision.status,
        "mmm_required_conversion_count": len(report.mmm_decision.required_conversions),
        "geox_required_conversion_count": len(report.geox_decision.required_conversions),
        "conversion_rule_count": len(report.conversion_rules),
        "issue_count": len(report.issues),
        "llm_metadata_only": (
            report.llm_metadata_decision.status
            == DomainDatasetCompatibilityStatus.METADATA_ONLY.value
        ),
    }


def _decide_mmm(
    *,
    raw_grain: DomainDatasetGrainSpec,
    panel: str,
    kpi: str,
    channel: str,
    geo: str,
    time: str,
    requested_geo: str,
    requested_time: str,
    spend_already_wide: bool,
    kpi_repeated: bool,
) -> tuple[
    DomainDatasetCompatibilityDecision,
    list[DomainDatasetGrainConversionRule],
    list[str],
]:
    del kpi  # used via kpi_repeated
    rules: list[DomainDatasetGrainConversionRule] = []
    issues: list[str] = [
        DomainDatasetGrainIssueCode.MMM_COMPATIBILITY_DECLARED.value,
        DomainDatasetGrainIssueCode.MODEL_READY_GRAIN_DECLARED.value,
    ]
    blocked: list[str] = []
    warnings: list[str] = []
    required: list[str] = []

    if geo == DomainDatasetGeoGrain.STATE.value and requested_geo == (
        DomainDatasetGeoGrain.DMA.value
    ):
        blocked.append(
            DomainDatasetGrainIssueCode.STATE_TO_DMA_CONVERSION_BLOCKED.value
        )
        issues.append(DomainDatasetGrainIssueCode.STATE_TO_DMA_CONVERSION_BLOCKED.value)
        rules.append(
            DomainDatasetGrainConversionRule(
                conversion_type=DomainDatasetConversionType.BLOCKED_CONVERSION.value,
                source_panel_grain=panel,
                target_panel_grain=DomainDatasetPanelGrain.TIME_GEO.value,
                allowed=False,
                reason="State grain cannot satisfy requested DMA design",
                blocked_reason=(
                    DomainDatasetGrainIssueCode.STATE_TO_DMA_CONVERSION_BLOCKED.value
                ),
            )
        )
        return (
            DomainDatasetCompatibilityDecision(
                target=DomainDatasetCompatibilityTarget.MMM_INPUT.value,
                status=DomainDatasetCompatibilityStatus.BLOCKED_UNSUPPORTED_GRAIN.value,
                source_grain=raw_grain,
                target_grain=_target_grain(
                    raw_grain,
                    panel_grain=DomainDatasetPanelGrain.TIME_GEO.value,
                    channel_grain=DomainDatasetChannelGrain.NONE.value,
                    kpi_grain=DomainDatasetKPIGrain.TIME_GEO.value,
                    geo_grain=requested_geo,
                    time_grain=requested_time,
                ),
                required_conversions=(),
                blocked_reasons=tuple(blocked),
                warnings=tuple(warnings),
                issues=tuple(dict.fromkeys(issues)),
            ),
            rules,
            issues,
        )

    if (
        time == DomainDatasetTimeGrain.WEEK.value
        and requested_time == DomainDatasetTimeGrain.DAY.value
    ):
        blocked.append(
            DomainDatasetGrainIssueCode.WEEK_TO_DAY_DISAGGREGATION_BLOCKED.value
        )
        issues.append(
            DomainDatasetGrainIssueCode.WEEK_TO_DAY_DISAGGREGATION_BLOCKED.value
        )
        return (
            DomainDatasetCompatibilityDecision(
                target=DomainDatasetCompatibilityTarget.MMM_INPUT.value,
                status=DomainDatasetCompatibilityStatus.BLOCKED_UNSUPPORTED_GRAIN.value,
                source_grain=raw_grain,
                target_grain=None,
                required_conversions=(),
                blocked_reasons=tuple(blocked),
                issues=tuple(dict.fromkeys(issues)),
            ),
            rules,
            issues,
        )

    if panel == DomainDatasetPanelGrain.TIME_GEO_CHANNEL.value and kpi_repeated:
        required.extend(
            (
                DomainDatasetConversionType.PIVOT_CHANNEL_SPEND_WIDE.value,
                DomainDatasetConversionType.KEEP_KPI_ONCE_PER_TIME_GEO.value,
            )
        )
        issues.append(
            DomainDatasetGrainIssueCode.MMM_REQUIRES_TIME_GEO_WIDE_OR_CONVERTIBLE.value
        )
        rules.append(
            DomainDatasetGrainConversionRule(
                conversion_type=(
                    DomainDatasetConversionType.PIVOT_CHANNEL_SPEND_WIDE.value
                ),
                source_panel_grain=panel,
                target_panel_grain=DomainDatasetPanelGrain.TIME_GEO.value,
                allowed=True,
                reason="Pivot channel spend wide before MMM input",
                required_columns=tuple(raw_grain.spend_columns)
                + tuple(raw_grain.channel_identifier_columns),
            )
        )
        rules.append(
            DomainDatasetGrainConversionRule(
                conversion_type=(
                    DomainDatasetConversionType.KEEP_KPI_ONCE_PER_TIME_GEO.value
                ),
                source_panel_grain=panel,
                target_panel_grain=DomainDatasetPanelGrain.TIME_GEO.value,
                allowed=True,
                reason="Keep KPI once per time×geo to avoid double-count",
                required_columns=tuple(raw_grain.kpi_columns),
            )
        )
        warnings.append("Raw TIME_GEO_CHANNEL panel is not MMM-ready as-is")
        return (
            DomainDatasetCompatibilityDecision(
                target=DomainDatasetCompatibilityTarget.MMM_INPUT.value,
                status=(
                    DomainDatasetCompatibilityStatus.COMPATIBLE_AFTER_CONVERSION.value
                ),
                source_grain=raw_grain,
                target_grain=_target_grain(
                    raw_grain,
                    panel_grain=DomainDatasetPanelGrain.TIME_GEO.value,
                    channel_grain=DomainDatasetChannelGrain.NONE.value,
                    kpi_grain=DomainDatasetKPIGrain.TIME_GEO.value,
                    geo_grain=requested_geo,
                    time_grain=requested_time,
                ),
                required_conversions=tuple(required),
                blocked_reasons=(
                    DomainDatasetGrainIssueCode.KPI_DOUBLE_COUNT_RISK_BLOCKED.value,
                ),
                warnings=tuple(warnings),
                issues=tuple(dict.fromkeys(issues)),
                metadata={"compatible_as_is": False},
            ),
            rules,
            issues,
        )

    if panel == DomainDatasetPanelGrain.TIME_GEO.value:
        if spend_already_wide or channel == DomainDatasetChannelGrain.NONE.value:
            if (
                time == DomainDatasetTimeGrain.DAY.value
                and requested_time == DomainDatasetTimeGrain.WEEK.value
            ):
                required.append(DomainDatasetConversionType.AGGREGATE_TIME_UP.value)
                status = (
                    DomainDatasetCompatibilityStatus.COMPATIBLE_AFTER_CONVERSION.value
                )
            else:
                required.append(
                    DomainDatasetConversionType.NO_CONVERSION_REQUIRED.value
                )
                status = DomainDatasetCompatibilityStatus.COMPATIBLE_AS_IS.value
            return (
                DomainDatasetCompatibilityDecision(
                    target=DomainDatasetCompatibilityTarget.MMM_INPUT.value,
                    status=status,
                    source_grain=raw_grain,
                    target_grain=_target_grain(
                        raw_grain,
                        panel_grain=DomainDatasetPanelGrain.TIME_GEO.value,
                        channel_grain=DomainDatasetChannelGrain.NONE.value,
                        kpi_grain=DomainDatasetKPIGrain.TIME_GEO.value,
                        geo_grain=requested_geo,
                        time_grain=requested_time,
                    ),
                    required_conversions=tuple(required),
                    issues=tuple(dict.fromkeys(issues)),
                ),
                rules,
                issues,
            )
        issues.append(
            DomainDatasetGrainIssueCode.MMM_REQUIRES_TIME_GEO_WIDE_OR_CONVERTIBLE.value
        )
        return (
            DomainDatasetCompatibilityDecision(
                target=DomainDatasetCompatibilityTarget.MMM_INPUT.value,
                status=DomainDatasetCompatibilityStatus.BLOCKED_INSUFFICIENT_GRAIN.value,
                source_grain=raw_grain,
                target_grain=None,
                blocked_reasons=("spend_not_wide_and_channel_grain_present",),
                issues=tuple(dict.fromkeys(issues)),
            ),
            rules,
            issues,
        )

    issues.append(
        DomainDatasetGrainIssueCode.MMM_REQUIRES_TIME_GEO_WIDE_OR_CONVERTIBLE.value
    )
    return (
        DomainDatasetCompatibilityDecision(
            target=DomainDatasetCompatibilityTarget.MMM_INPUT.value,
            status=DomainDatasetCompatibilityStatus.BLOCKED_UNSUPPORTED_GRAIN.value,
            source_grain=raw_grain,
            target_grain=None,
            blocked_reasons=("unsupported_panel_grain_for_mmm",),
            issues=tuple(dict.fromkeys(issues)),
        ),
        rules,
        issues,
    )


def _decide_geox(
    *,
    raw_grain: DomainDatasetGrainSpec,
    panel: str,
    geo: str,
    time: str,
    requested_geo: str,
    requested_time: str,
    test_channel_available: bool,
) -> tuple[
    DomainDatasetCompatibilityDecision,
    list[DomainDatasetGrainConversionRule],
    list[str],
]:
    rules: list[DomainDatasetGrainConversionRule] = []
    issues: list[str] = [
        DomainDatasetGrainIssueCode.GEOX_COMPATIBILITY_DECLARED.value,
        DomainDatasetGrainIssueCode.MODEL_READY_GRAIN_DECLARED.value,
    ]

    if geo == DomainDatasetGeoGrain.STATE.value and requested_geo == (
        DomainDatasetGeoGrain.DMA.value
    ):
        issues.append(DomainDatasetGrainIssueCode.STATE_TO_DMA_CONVERSION_BLOCKED.value)
        rules.append(
            DomainDatasetGrainConversionRule(
                conversion_type=DomainDatasetConversionType.BLOCKED_CONVERSION.value,
                source_panel_grain=panel,
                target_panel_grain=DomainDatasetPanelGrain.TIME_GEO.value,
                allowed=False,
                reason="State grain cannot satisfy requested DMA GeoX design",
                blocked_reason=(
                    DomainDatasetGrainIssueCode.STATE_TO_DMA_CONVERSION_BLOCKED.value
                ),
            )
        )
        return (
            DomainDatasetCompatibilityDecision(
                target=DomainDatasetCompatibilityTarget.GEOX_DESIGN_INPUT.value,
                status=DomainDatasetCompatibilityStatus.BLOCKED_UNSUPPORTED_GRAIN.value,
                source_grain=raw_grain,
                target_grain=None,
                blocked_reasons=(
                    DomainDatasetGrainIssueCode.STATE_TO_DMA_CONVERSION_BLOCKED.value,
                ),
                issues=tuple(dict.fromkeys(issues)),
            ),
            rules,
            issues,
        )

    if (
        time == DomainDatasetTimeGrain.WEEK.value
        and requested_time == DomainDatasetTimeGrain.DAY.value
    ):
        issues.append(
            DomainDatasetGrainIssueCode.WEEK_TO_DAY_DISAGGREGATION_BLOCKED.value
        )
        return (
            DomainDatasetCompatibilityDecision(
                target=DomainDatasetCompatibilityTarget.GEOX_DESIGN_INPUT.value,
                status=DomainDatasetCompatibilityStatus.BLOCKED_UNSUPPORTED_GRAIN.value,
                source_grain=raw_grain,
                target_grain=None,
                blocked_reasons=(
                    DomainDatasetGrainIssueCode.WEEK_TO_DAY_DISAGGREGATION_BLOCKED.value,
                ),
                issues=tuple(dict.fromkeys(issues)),
            ),
            rules,
            issues,
        )

    has_identifiers = bool(
        raw_grain.geo_identifier_columns
        and raw_grain.time_identifier_columns
        and raw_grain.kpi_columns
    )

    if panel == DomainDatasetPanelGrain.TIME_GEO.value and has_identifiers:
        required: list[str] = []
        status = DomainDatasetCompatibilityStatus.COMPATIBLE_AS_IS.value
        if (
            time == DomainDatasetTimeGrain.DAY.value
            and requested_time == DomainDatasetTimeGrain.WEEK.value
        ):
            required.append(DomainDatasetConversionType.AGGREGATE_TIME_UP.value)
            status = DomainDatasetCompatibilityStatus.COMPATIBLE_AFTER_CONVERSION.value
        else:
            required.append(DomainDatasetConversionType.NO_CONVERSION_REQUIRED.value)
        return (
            DomainDatasetCompatibilityDecision(
                target=DomainDatasetCompatibilityTarget.GEOX_DESIGN_INPUT.value,
                status=status,
                source_grain=raw_grain,
                target_grain=_target_grain(
                    raw_grain,
                    panel_grain=DomainDatasetPanelGrain.TIME_GEO.value,
                    channel_grain=DomainDatasetChannelGrain.NONE.value,
                    kpi_grain=DomainDatasetKPIGrain.TIME_GEO.value,
                    geo_grain=requested_geo,
                    time_grain=requested_time,
                ),
                required_conversions=tuple(required),
                issues=tuple(dict.fromkeys(issues)),
            ),
            rules,
            issues,
        )

    if panel == DomainDatasetPanelGrain.TIME_GEO_CHANNEL.value:
        issues.append(
            DomainDatasetGrainIssueCode.GEOX_REQUIRES_TIME_GEO_DESIGN_PANEL.value
        )
        required_conversions = [
            DomainDatasetConversionType.FILTER_TO_TEST_CHANNEL.value,
            DomainDatasetConversionType.AGGREGATE_CHANNEL_TO_TOTAL.value,
        ]
        if not test_channel_available:
            return (
                DomainDatasetCompatibilityDecision(
                    target=DomainDatasetCompatibilityTarget.GEOX_DESIGN_INPUT.value,
                    status=(
                        DomainDatasetCompatibilityStatus.BLOCKED_INSUFFICIENT_GRAIN.value
                    ),
                    source_grain=raw_grain,
                    target_grain=None,
                    required_conversions=tuple(required_conversions),
                    blocked_reasons=("test_channel_unavailable",),
                    issues=tuple(dict.fromkeys(issues)),
                ),
                rules,
                issues,
            )
        rules.append(
            DomainDatasetGrainConversionRule(
                conversion_type=(
                    DomainDatasetConversionType.FILTER_TO_TEST_CHANNEL.value
                ),
                source_panel_grain=panel,
                target_panel_grain=DomainDatasetPanelGrain.TIME_GEO.value,
                allowed=True,
                reason="Filter to GeoX test channel for design panel",
                required_columns=tuple(raw_grain.channel_identifier_columns),
            )
        )
        rules.append(
            DomainDatasetGrainConversionRule(
                conversion_type=(
                    DomainDatasetConversionType.AGGREGATE_CHANNEL_TO_TOTAL.value
                ),
                source_panel_grain=panel,
                target_panel_grain=DomainDatasetPanelGrain.TIME_GEO.value,
                allowed=True,
                reason="Aggregate remaining channel spend to total if needed",
                required_columns=tuple(raw_grain.spend_columns),
            )
        )
        return (
            DomainDatasetCompatibilityDecision(
                target=DomainDatasetCompatibilityTarget.GEOX_DESIGN_INPUT.value,
                status=(
                    DomainDatasetCompatibilityStatus.COMPATIBLE_AFTER_CONVERSION.value
                ),
                source_grain=raw_grain,
                target_grain=_target_grain(
                    raw_grain,
                    panel_grain=DomainDatasetPanelGrain.TIME_GEO.value,
                    channel_grain=DomainDatasetChannelGrain.NONE.value,
                    kpi_grain=DomainDatasetKPIGrain.TIME_GEO.value,
                    geo_grain=requested_geo,
                    time_grain=requested_time,
                ),
                required_conversions=tuple(required_conversions),
                issues=tuple(dict.fromkeys(issues)),
            ),
            rules,
            issues,
        )

    issues.append(DomainDatasetGrainIssueCode.GEOX_REQUIRES_TIME_GEO_DESIGN_PANEL.value)
    return (
        DomainDatasetCompatibilityDecision(
            target=DomainDatasetCompatibilityTarget.GEOX_DESIGN_INPUT.value,
            status=DomainDatasetCompatibilityStatus.BLOCKED_UNSUPPORTED_GRAIN.value,
            source_grain=raw_grain,
            target_grain=None,
            blocked_reasons=("unsupported_panel_grain_for_geox",),
            issues=tuple(dict.fromkeys(issues)),
        ),
        rules,
        issues,
    )


def _decide_calibration(
    *,
    raw_grain: DomainDatasetGrainSpec,
    panel: str,
) -> DomainDatasetCompatibilityDecision:
    if panel in {
        DomainDatasetPanelGrain.TIME_GEO.value,
        DomainDatasetPanelGrain.TIME_GEO_CHANNEL.value,
    }:
        status = DomainDatasetCompatibilityStatus.COMPATIBLE_AFTER_CONVERSION.value
        required: tuple[str, ...] = (
            DomainDatasetConversionType.KEEP_KPI_ONCE_PER_TIME_GEO.value,
        )
    else:
        status = DomainDatasetCompatibilityStatus.BLOCKED_INSUFFICIENT_GRAIN.value
        required = ()
    return DomainDatasetCompatibilityDecision(
        target=DomainDatasetCompatibilityTarget.CALIBRATION_SIGNAL_INPUT.value,
        status=status,
        source_grain=raw_grain,
        target_grain=None,
        required_conversions=required,
        issues=("CALIBRATION_SIGNAL_COMPATIBILITY_DECLARED",),
        metadata={"runtime_mapping_changed": False},
    )


def _time_conversion_rules(
    *,
    source_time: str,
    target_time: str,
    source_panel: str,
) -> list[DomainDatasetGrainConversionRule]:
    if source_time == target_time:
        return []
    if (
        source_time == DomainDatasetTimeGrain.DAY.value
        and target_time == DomainDatasetTimeGrain.WEEK.value
    ):
        return [
            DomainDatasetGrainConversionRule(
                conversion_type=DomainDatasetConversionType.AGGREGATE_TIME_UP.value,
                source_panel_grain=source_panel,
                target_panel_grain=source_panel,
                allowed=True,
                reason="Day-to-week aggregation is allowed",
                metadata={"source_time": source_time, "target_time": target_time},
            )
        ]
    if (
        source_time == DomainDatasetTimeGrain.WEEK.value
        and target_time == DomainDatasetTimeGrain.DAY.value
    ):
        return [
            DomainDatasetGrainConversionRule(
                conversion_type=DomainDatasetConversionType.BLOCKED_CONVERSION.value,
                source_panel_grain=source_panel,
                target_panel_grain=source_panel,
                allowed=False,
                reason="Week-to-day disaggregation is blocked",
                blocked_reason=(
                    DomainDatasetGrainIssueCode.WEEK_TO_DAY_DISAGGREGATION_BLOCKED.value
                ),
                metadata={"source_time": source_time, "target_time": target_time},
            )
        ]
    return []


def _target_grain(
    raw_grain: DomainDatasetGrainSpec,
    *,
    panel_grain: str,
    channel_grain: str,
    kpi_grain: str,
    geo_grain: str,
    time_grain: str,
) -> DomainDatasetGrainSpec:
    return DomainDatasetGrainSpec(
        geo_grain=geo_grain,
        time_grain=time_grain,
        channel_grain=channel_grain,
        panel_grain=panel_grain,
        kpi_grain=kpi_grain,
        geo_identifier_columns=raw_grain.geo_identifier_columns,
        time_identifier_columns=raw_grain.time_identifier_columns,
        channel_identifier_columns=(),
        kpi_columns=raw_grain.kpi_columns,
        spend_columns=raw_grain.spend_columns,
        control_columns=raw_grain.control_columns,
        metadata={"model_ready": True},
    )


def _dedupe_rules(
    rules: Sequence[DomainDatasetGrainConversionRule],
) -> tuple[DomainDatasetGrainConversionRule, ...]:
    seen: set[tuple[str, str, str, bool]] = set()
    out: list[DomainDatasetGrainConversionRule] = []
    for rule in rules:
        key = (
            rule.conversion_type,
            rule.source_panel_grain,
            rule.target_panel_grain,
            rule.allowed,
        )
        if key in seen:
            continue
        seen.add(key)
        out.append(rule)
    return tuple(out)


def _enum_value(value: object) -> str:
    if isinstance(value, StrEnum):
        return str(value.value)
    return str(value)


__all__ = [
    "ARTIFACT_ID",
    "CONTRACT_MODULE",
    "RECOMMENDED_NEXT_ARTIFACT",
    "DOMAIN_DATASET_GRAIN_COMPATIBILITY_CONTRACT_ARTIFACT_ID",
    "RECOMMENDED_NEXT_DOMAIN_DATASET_GRAIN_COMPATIBILITY_ARTIFACT",
    "DomainDatasetGeoGrain",
    "DomainDatasetTimeGrain",
    "DomainDatasetChannelGrain",
    "DomainDatasetKPIGrain",
    "DomainDatasetPanelGrain",
    "DomainDatasetCompatibilityTarget",
    "DomainDatasetCompatibilityStatus",
    "DomainDatasetConversionType",
    "DomainDatasetGrainIssueCode",
    "DomainDatasetGrainSpec",
    "DomainDatasetGrainConversionRule",
    "DomainDatasetCompatibilityDecision",
    "DomainDatasetGrainCompatibilityReport",
    "build_domain_dataset_grain_compatibility_report",
    "summarize_domain_dataset_grain_compatibility_report",
]
