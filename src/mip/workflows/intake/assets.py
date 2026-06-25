"""Deterministic required data asset planning (P2 / I3)."""

from typing import Any

from mip.contracts.intake import (
    DataGrain,
    GeoGrain,
    IntakeCandidatePath,
    IntakePathRecommendation,
    IntakeRecommendationStatus,
)
from mip.contracts.intake_assets import (
    DataAssetPurpose,
    DataAssetRequirementLevel,
    DataAssetType,
    IntakePlan,
    RequiredDataAsset,
    SampleColumnRole,
    SampleColumnSpec,
    SampleRow,
    SampleSchemaExpectation,
)

_BLOCKED_PATHS = frozenset(
    {
        IntakeCandidatePath.BLOCKED_NEEDS_MORE_DATA,
        "blocked_needs_more_data",
    }
)


def _path_slug(path: IntakeCandidatePath | str) -> str:
    return path.value if isinstance(path, IntakeCandidatePath) else path


def _col(
    name: str,
    role: SampleColumnRole,
    description: str,
    *,
    required: bool = True,
    example_value: str | int | float | None = None,
) -> SampleColumnSpec:
    return SampleColumnSpec(
        name=name,
        role=role,
        required=required,
        description=description,
        example_value=example_value,
    )


def _outcome_schema(*, geo_level: bool, path: IntakeCandidatePath) -> SampleSchemaExpectation:
    required = [
        _col("week", SampleColumnRole.DATE, "Weekly period start", example_value="2026-01-05"),
        _col("country", SampleColumnRole.COUNTRY, "Country code", example_value="US"),
        _col("product", SampleColumnRole.PRODUCT, "Product scope", example_value="CreativeCloud"),
        _col(
            "metric_id",
            SampleColumnRole.METRIC_ID,
            "Canonical metric id",
            example_value="conversions",
        ),
        _col(
            "metric_value",
            SampleColumnRole.METRIC_VALUE,
            "Outcome metric value",
            example_value=12450,
        ),
    ]
    if geo_level:
        required.insert(
            1,
            _col("geo", SampleColumnRole.GEO, "Geo or DMA identifier", example_value="US-CA"),
        )
    sample_values: dict[str, str | int | float | bool] = {
        "week": "2026-01-05",
        "country": "US",
        "product": "CreativeCloud",
        "metric_id": "conversions",
        "metric_value": 12450,
    }
    if geo_level:
        sample_values["geo"] = "US-CA"
    warnings = []
    if geo_level:
        warnings.append("Geo-level MMM requires geo-level KPI variation.")
    return SampleSchemaExpectation(
        schema_id=f"{_path_slug(path)}-outcome",
        asset_type=DataAssetType.OUTCOME_KPI_DATA,
        description="Weekly outcome KPI panel for MMM intake.",
        minimum_grain=DataGrain.WEEKLY,
        required_columns=required,
        sample_rows=[SampleRow(values=sample_values)],
        warnings=warnings,
    )


def _media_schema(*, geo_level: bool, path: IntakeCandidatePath) -> SampleSchemaExpectation:
    required = [
        _col("week", SampleColumnRole.DATE, "Weekly period start", example_value="2026-01-05"),
        _col("country", SampleColumnRole.COUNTRY, "Country code", example_value="US"),
        _col("product", SampleColumnRole.PRODUCT, "Product scope", example_value="CreativeCloud"),
        _col("channel", SampleColumnRole.CHANNEL, "Media channel", example_value="Paid Social"),
        _col("platform", SampleColumnRole.PLATFORM, "Platform label", example_value="Meta"),
        _col(
            "campaign",
            SampleColumnRole.CAMPAIGN,
            "Campaign label",
            example_value="prospecting_us_q1",
        ),
        _col("spend", SampleColumnRole.SPEND, "Media spend", example_value=125000),
        _col("impressions", SampleColumnRole.IMPRESSIONS, "Impressions", example_value=8200000),
        _col("clicks", SampleColumnRole.CLICKS, "Clicks", example_value=64500),
    ]
    if geo_level:
        required.insert(
            1,
            _col("geo", SampleColumnRole.GEO, "Geo or DMA identifier", example_value="US-CA"),
        )
    sample_values: dict[str, str | int | float | bool] = {
        "week": "2026-01-05",
        "country": "US",
        "product": "CreativeCloud",
        "channel": "Paid Social",
        "platform": "Meta",
        "campaign": "prospecting_us_q1",
        "spend": 125000,
        "impressions": 8200000,
        "clicks": 64500,
    }
    if geo_level:
        sample_values["geo"] = "US-CA"
    return SampleSchemaExpectation(
        schema_id=f"{_path_slug(path)}-media",
        asset_type=DataAssetType.MEDIA_SPEND_DATA,
        description="Weekly media spend and delivery panel.",
        minimum_grain=DataGrain.WEEKLY,
        required_columns=required,
        sample_rows=[SampleRow(values=sample_values)],
        warnings=["Geo-level media variation is required for geo-level MMM."] if geo_level else [],
    )


def _calendar_schema(path: IntakeCandidatePath) -> SampleSchemaExpectation:
    return SampleSchemaExpectation(
        schema_id=f"{_path_slug(path)}-calendar",
        asset_type=DataAssetType.CALENDAR_SEASONALITY_DATA,
        description="Calendar and promo control flags.",
        minimum_grain=DataGrain.WEEKLY,
        required_columns=[
            _col("week", SampleColumnRole.DATE, "Weekly period start", example_value="2026-01-05"),
            _col("country", SampleColumnRole.COUNTRY, "Country code", example_value="US"),
            _col("holiday_flag", SampleColumnRole.CONTROL, "Holiday indicator", example_value=0),
            _col("promo_flag", SampleColumnRole.CONTROL, "Promotion indicator", example_value=1),
            _col(
                "discount_rate",
                SampleColumnRole.CONTROL,
                "Discount intensity",
                example_value=0.10,
            ),
            _col(
                "site_outage_flag",
                SampleColumnRole.CONTROL,
                "Site outage indicator",
                example_value=0,
            ),
        ],
        sample_rows=[
            SampleRow(
                values={
                    "week": "2026-01-05",
                    "country": "US",
                    "holiday_flag": 0,
                    "promo_flag": 1,
                    "discount_rate": 0.10,
                    "site_outage_flag": 0,
                }
            )
        ],
    )


def _channel_mapping_schema(path: IntakeCandidatePath) -> SampleSchemaExpectation:
    return SampleSchemaExpectation(
        schema_id=f"{_path_slug(path)}-channel-mapping",
        asset_type=DataAssetType.CHANNEL_MAPPING,
        description="Source-to-canonical channel mapping.",
        required_columns=[
            _col(
                "source_channel",
                SampleColumnRole.MAPPING_SOURCE,
                "Source channel label",
                example_value="facebook",
            ),
            _col(
                "source_platform",
                SampleColumnRole.MAPPING_SOURCE,
                "Source platform label",
                example_value="Meta",
            ),
            _col(
                "canonical_channel",
                SampleColumnRole.MAPPING_TARGET,
                "Canonical channel",
                example_value="Paid Social",
            ),
            _col(
                "canonical_platform",
                SampleColumnRole.MAPPING_TARGET,
                "Canonical platform",
                example_value="Meta",
            ),
        ],
        sample_rows=[
            SampleRow(
                values={
                    "source_channel": "facebook",
                    "source_platform": "Meta",
                    "canonical_channel": "Paid Social",
                    "canonical_platform": "Meta",
                }
            )
        ],
    )


def _calibration_schema(path: IntakeCandidatePath) -> SampleSchemaExpectation:
    return SampleSchemaExpectation(
        schema_id=f"{_path_slug(path)}-calibration-signal",
        asset_type=DataAssetType.CALIBRATION_SIGNAL_DATA,
        description="Structured CalibrationSignal-compatible experiment evidence.",
        required_columns=[
            _col("signal_id", SampleColumnRole.STATUS, "Calibration signal id"),
            _col("source", SampleColumnRole.STATUS, "Evidence source system"),
            _col("metric_id", SampleColumnRole.METRIC_ID, "Canonical metric id"),
            _col("estimand_id", SampleColumnRole.METRIC_ID, "Canonical estimand id"),
            _col("channel_scope", SampleColumnRole.CHANNEL, "Channel scope list"),
            _col("geo_scope", SampleColumnRole.GEO, "Geo scope list"),
            _col(
                "effect_estimate",
                SampleColumnRole.EFFECT_ESTIMATE,
                "Governed effect estimate",
                example_value=0.045,
            ),
            _col(
                "standard_error",
                SampleColumnRole.STANDARD_ERROR,
                "Governed standard error",
                example_value=0.018,
            ),
            _col(
                "causal_validity_status",
                SampleColumnRole.STATUS,
                "Governed validity status",
                example_value="governed",
            ),
        ],
        sample_rows=[
            SampleRow(
                values={
                    "signal_id": "geox_meta_us_2026_q1",
                    "source": "GeoX",
                    "metric_id": "conversions",
                    "estimand_id": "incremental_conversions",
                    "channel_scope": '["Meta"]',
                    "geo_scope": '["US"]',
                    "effect_estimate": 0.045,
                    "standard_error": 0.018,
                    "causal_validity_status": "governed",
                }
            )
        ],
        warnings=[
            "Experiment evidence must map to CalibrationSignal.",
            "Loose text or unstructured readouts are not model-ready calibration inputs.",
        ],
    )


def _geo_mapping_schema(path: IntakeCandidatePath) -> SampleSchemaExpectation:
    return SampleSchemaExpectation(
        schema_id=f"{_path_slug(path)}-geo-mapping",
        asset_type=DataAssetType.GEO_MAPPING,
        description="Geo hierarchy mapping for experiment design or readout.",
        required_columns=[
            _col("source_geo", SampleColumnRole.MAPPING_SOURCE, "Source geo label"),
            _col("canonical_geo", SampleColumnRole.MAPPING_TARGET, "Canonical geo id"),
            _col("market", SampleColumnRole.MARKET, "Market label"),
        ],
        sample_rows=[
            SampleRow(
                values={
                    "source_geo": "California",
                    "canonical_geo": "US-CA",
                    "market": "US",
                }
            )
        ],
    )


def _experiment_export_schema(path: IntakeCandidatePath) -> SampleSchemaExpectation:
    return SampleSchemaExpectation(
        schema_id=f"{_path_slug(path)}-experiment-export",
        asset_type=DataAssetType.EXPERIMENT_EXPORT_DATA,
        description="Governed experiment export for readout or calibration intake.",
        required_columns=[
            _col("export_id", SampleColumnRole.STATUS, "Experiment export id"),
            _col("source_repo", SampleColumnRole.STATUS, "Source repository"),
            _col("metric_id", SampleColumnRole.METRIC_ID, "Canonical metric id"),
            _col("estimand_id", SampleColumnRole.METRIC_ID, "Canonical estimand id"),
            _col("time_window", SampleColumnRole.TIME_WINDOW, "Experiment window"),
            _col("status", SampleColumnRole.STATUS, "Governed export status"),
        ],
        sample_rows=[
            SampleRow(
                values={
                    "export_id": "geox_export_001",
                    "source_repo": "panel_exp",
                    "metric_id": "conversions",
                    "estimand_id": "incremental_conversions",
                    "time_window": "2026-Q1",
                    "status": "governed",
                }
            )
        ],
        warnings=["Readout requires governed experiment export/evidence before decision claims."],
    )


def _asset(
    asset_id: str,
    asset_type: DataAssetType,
    requirement_level: DataAssetRequirementLevel,
    purpose: DataAssetPurpose,
    description: str,
    *,
    path: IntakeCandidatePath,
    sample_schema: SampleSchemaExpectation | None = None,
    minimum_time_grain: DataGrain = DataGrain.UNKNOWN,
    minimum_geo_grain: GeoGrain = GeoGrain.UNKNOWN,
    blocks_if_missing: bool | None = None,
    warnings: list[str] | None = None,
) -> RequiredDataAsset:
    if blocks_if_missing is None:
        blocks_if_missing = requirement_level in {
            DataAssetRequirementLevel.REQUIRED,
            DataAssetRequirementLevel.CONDITIONAL,
        }
    return RequiredDataAsset(
        asset_id=asset_id,
        asset_type=asset_type,
        requirement_level=requirement_level,
        purpose=purpose,
        description=description,
        required_for_paths=[path],
        minimum_time_grain=minimum_time_grain,
        minimum_geo_grain=minimum_geo_grain,
        sample_schema=sample_schema,
        blocks_if_missing=blocks_if_missing,
        warnings=warnings or [],
    )


def _mmm_diagnostic_assets(
    path: IntakeCandidatePath,
    *,
    geo_level: bool,
) -> tuple[list[RequiredDataAsset], list[RequiredDataAsset], list[RequiredDataAsset]]:
    geo_grain = GeoGrain.GEO if geo_level else GeoGrain.NATIONAL
    geo_warning = (
        ["Geo-level MMM requires geo-level KPI and media variation."]
        if geo_level
        else []
    )
    if geo_level:
        geo_warning.append("National-only data is insufficient for this path.")

    required = [
        _asset(
            f"{_path_slug(path)}-outcome",
            DataAssetType.OUTCOME_KPI_DATA,
            DataAssetRequirementLevel.REQUIRED,
            DataAssetPurpose.MODEL_OUTCOME,
            "Outcome KPI time series for MMM intake.",
            path=path,
            sample_schema=_outcome_schema(geo_level=geo_level, path=path),
            minimum_time_grain=DataGrain.WEEKLY,
            minimum_geo_grain=geo_grain,
            warnings=geo_warning,
        ),
        _asset(
            f"{_path_slug(path)}-media",
            DataAssetType.MEDIA_SPEND_DATA,
            DataAssetRequirementLevel.REQUIRED,
            DataAssetPurpose.MEDIA_INPUT,
            "Media spend and delivery time series.",
            path=path,
            sample_schema=_media_schema(geo_level=geo_level, path=path),
            minimum_time_grain=DataGrain.WEEKLY,
            minimum_geo_grain=geo_grain,
            warnings=geo_warning,
        ),
        _asset(
            f"{_path_slug(path)}-channel-mapping",
            DataAssetType.CHANNEL_MAPPING,
            DataAssetRequirementLevel.REQUIRED,
            DataAssetPurpose.SEMANTIC_MAPPING,
            "Canonical channel and platform mapping.",
            path=path,
            sample_schema=_channel_mapping_schema(path),
        ),
        _asset(
            f"{_path_slug(path)}-calendar",
            DataAssetType.CALENDAR_SEASONALITY_DATA,
            DataAssetRequirementLevel.REQUIRED,
            DataAssetPurpose.CONFOUNDER_CONTROL,
            "Calendar, promo, and seasonality controls.",
            path=path,
            sample_schema=_calendar_schema(path),
            minimum_time_grain=DataGrain.WEEKLY,
        ),
    ]
    recommended = [
        _asset(
            f"{_path_slug(path)}-exposure",
            DataAssetType.MEDIA_EXPOSURE_DATA,
            DataAssetRequirementLevel.RECOMMENDED,
            DataAssetPurpose.EXPOSURE_DIAGNOSTIC,
            "Optional exposure diagnostics beyond spend.",
            path=path,
            blocks_if_missing=False,
        ),
        _asset(
            f"{_path_slug(path)}-controls",
            DataAssetType.CONTROL_DATA,
            DataAssetRequirementLevel.RECOMMENDED,
            DataAssetPurpose.CONFOUNDER_CONTROL,
            "Additional control variables beyond calendar flags.",
            path=path,
            blocks_if_missing=False,
        ),
        _asset(
            f"{_path_slug(path)}-pricing-promo",
            DataAssetType.PRICING_PROMO_DATA,
            DataAssetRequirementLevel.RECOMMENDED,
            DataAssetPurpose.CONFOUNDER_CONTROL,
            "Pricing and promotion context.",
            path=path,
            blocks_if_missing=False,
        ),
        _asset(
            f"{_path_slug(path)}-metric-mapping",
            DataAssetType.METRIC_MAPPING,
            DataAssetRequirementLevel.RECOMMENDED,
            DataAssetPurpose.SEMANTIC_MAPPING,
            "Canonical metric mapping for outcome fields.",
            path=path,
            blocks_if_missing=False,
        ),
    ]
    optional = [
        _asset(
            f"{_path_slug(path)}-calibration",
            DataAssetType.CALIBRATION_SIGNAL_DATA,
            DataAssetRequirementLevel.OPTIONAL,
            DataAssetPurpose.CALIBRATION_EVIDENCE,
            "Optional calibration evidence for diagnostic MMM.",
            path=path,
            blocks_if_missing=False,
        ),
        _asset(
            f"{_path_slug(path)}-experiment-export",
            DataAssetType.EXPERIMENT_EXPORT_DATA,
            DataAssetRequirementLevel.OPTIONAL,
            DataAssetPurpose.EXPERIMENT_EVIDENCE,
            "Optional governed experiment export.",
            path=path,
            blocks_if_missing=False,
        ),
    ]
    return required, recommended, optional


def _blocked_plan(recommendation: IntakePathRecommendation) -> IntakePlan:
    return IntakePlan(
        plan_id=f"{recommendation.session_id}-plan",
        session_id=recommendation.session_id,
        recommendation_id=recommendation.recommendation_id,
        recommended_path=recommendation.recommended_path,
        blocked_assets=[
            _asset(
                "optimizer-governance-deferred",
                DataAssetType.EXPERIMENT_EXPORT_DATA,
                DataAssetRequirementLevel.BLOCKED_UNTIL_LATER_PHASE,
                DataAssetPurpose.GOVERNANCE_CONTEXT,
                "Optimizer and decision-support evidence requirements are deferred.",
                path=recommendation.recommended_path,
                blocks_if_missing=False,
                warnings=["No executable upload plan until governance prerequisites exist."],
            )
        ],
        warnings=list(recommendation.warnings),
        blocking_reasons=list(recommendation.blocking_reasons)
        or ["Path is blocked; complete intake clarification before requesting data."],
        next_user_actions=["Resolve blocking reasons before preparing data assets."],
    )


def build_intake_plan(recommendation: IntakePathRecommendation) -> IntakePlan:
    """Build a deterministic data asset plan from a path recommendation."""

    path = recommendation.recommended_path
    if (
        recommendation.status == IntakeRecommendationStatus.BLOCKED
        or path in _BLOCKED_PATHS
        or recommendation.status == IntakeRecommendationStatus.NEEDS_CLARIFICATION
    ):
        return _blocked_plan(recommendation)

    plan_id = f"{recommendation.session_id}-plan"
    base_kwargs = {
        "plan_id": plan_id,
        "session_id": recommendation.session_id,
        "recommendation_id": recommendation.recommendation_id,
        "recommended_path": path,
        "warnings": list(recommendation.warnings),
        "next_user_actions": list(recommendation.allowed_next_steps)
        or ["Review required data assets and sample schemas before upload/connect."],
    }

    def _plan(**overrides: Any) -> dict[str, Any]:
        return {**base_kwargs, **overrides}

    if path == IntakeCandidatePath.NATIONAL_DIAGNOSTIC_MMM:
        required, recommended, optional = _mmm_diagnostic_assets(path, geo_level=False)
        return IntakePlan(
            **_plan(
                required_assets=required,
                recommended_assets=recommended,
                optional_assets=optional,
            )
        )

    if path == IntakeCandidatePath.GEO_LEVEL_MMM:
        required, recommended, optional = _mmm_diagnostic_assets(path, geo_level=True)
        return IntakePlan(
            **_plan(
                warnings=[
                    *base_kwargs["warnings"],
                    "Geo-level MMM requires geo-level KPI and media variation.",
                    "National-only data is insufficient for this path.",
                ],
                required_assets=required,
                recommended_assets=recommended,
                optional_assets=optional,
            )
        )

    if path in {
        IntakeCandidatePath.CALIBRATED_MMM,
        IntakeCandidatePath.DECISION_SURFACE_CERTIFICATION,
    }:
        required, recommended, optional = _mmm_diagnostic_assets(
            IntakeCandidatePath.CALIBRATED_MMM,
            geo_level=False,
        )
        required.append(
            _asset(
                f"{_path_slug(path)}-calibration",
                DataAssetType.CALIBRATION_SIGNAL_DATA,
                DataAssetRequirementLevel.REQUIRED,
                DataAssetPurpose.CALIBRATION_EVIDENCE,
                "Structured CalibrationSignal-compatible experiment evidence.",
                path=path,
                sample_schema=_calibration_schema(path),
                warnings=[
                    "Experiment evidence must map to CalibrationSignal.",
                    "Loose text or unstructured readouts are not model-ready calibration inputs.",
                ],
            )
        )
        extra_warnings = list(base_kwargs["warnings"])
        if path == IntakeCandidatePath.DECISION_SURFACE_CERTIFICATION:
            extra_warnings.append(
                "Decision surface certification and optimizer paths remain deferred."
            )
        return IntakePlan(
            **_plan(
                warnings=extra_warnings,
                required_assets=required,
                recommended_assets=recommended,
                optional_assets=optional,
            )
        )

    if path == IntakeCandidatePath.GEO_EXPERIMENT_DESIGN:
        return IntakePlan(
            **_plan(
                warnings=[
                    *base_kwargs["warnings"],
                    "Design quality depends on pre-period outcome history, geo mapping, "
                    "and media variation.",
                ],
                required_assets=[
                    _asset(
                        f"{_path_slug(path)}-geo-mapping",
                        DataAssetType.GEO_MAPPING,
                        DataAssetRequirementLevel.REQUIRED,
                        DataAssetPurpose.SEMANTIC_MAPPING,
                        "Geo hierarchy mapping for experiment cells.",
                        path=path,
                        sample_schema=_geo_mapping_schema(path),
                    ),
                    _asset(
                        f"{_path_slug(path)}-outcome",
                        DataAssetType.OUTCOME_KPI_DATA,
                        DataAssetRequirementLevel.REQUIRED,
                        DataAssetPurpose.MODEL_OUTCOME,
                        "Historical outcome KPI series for power and design.",
                        path=path,
                        sample_schema=_outcome_schema(geo_level=True, path=path),
                        minimum_time_grain=DataGrain.WEEKLY,
                        minimum_geo_grain=GeoGrain.GEO,
                    ),
                    _asset(
                        f"{_path_slug(path)}-media",
                        DataAssetType.MEDIA_SPEND_DATA,
                        DataAssetRequirementLevel.CONDITIONAL,
                        DataAssetPurpose.MEDIA_INPUT,
                        "Historical media spend or exposure for design diagnostics.",
                        path=path,
                        sample_schema=_media_schema(geo_level=True, path=path),
                        minimum_time_grain=DataGrain.WEEKLY,
                        minimum_geo_grain=GeoGrain.GEO,
                    ),
                ],
            )
        )

    if path == IntakeCandidatePath.GEO_EXPERIMENT_READOUT:
        return IntakePlan(
            **_plan(
                warnings=[
                    *base_kwargs["warnings"],
                    "Readout requires governed experiment export/evidence before decision claims.",
                ],
                required_assets=[
                    _asset(
                        f"{_path_slug(path)}-experiment-export",
                        DataAssetType.EXPERIMENT_EXPORT_DATA,
                        DataAssetRequirementLevel.REQUIRED,
                        DataAssetPurpose.EXPERIMENT_EVIDENCE,
                        "Governed experiment export for readout.",
                        path=path,
                        sample_schema=_experiment_export_schema(path),
                    ),
                    _asset(
                        f"{_path_slug(path)}-outcome",
                        DataAssetType.OUTCOME_KPI_DATA,
                        DataAssetRequirementLevel.REQUIRED,
                        DataAssetPurpose.MODEL_OUTCOME,
                        "Outcome KPI context for experiment readout.",
                        path=path,
                        sample_schema=_outcome_schema(geo_level=True, path=path),
                    ),
                    _asset(
                        f"{_path_slug(path)}-geo-mapping",
                        DataAssetType.GEO_MAPPING,
                        DataAssetRequirementLevel.REQUIRED,
                        DataAssetPurpose.SEMANTIC_MAPPING,
                        "Geo mapping for experiment readout scope.",
                        path=path,
                        sample_schema=_geo_mapping_schema(path),
                    ),
                ],
            )
        )

    if path == IntakeCandidatePath.EXPERIMENT_CALIBRATION_INTAKE:
        return IntakePlan(
            **_plan(
                warnings=[
                    *base_kwargs["warnings"],
                    "Evidence must pass metric, estimand, scope, freshness, and causal-validity "
                    "checks in later phases.",
                ],
                required_assets=[
                    _asset(
                        f"{_path_slug(path)}-calibration",
                        DataAssetType.CALIBRATION_SIGNAL_DATA,
                        DataAssetRequirementLevel.CONDITIONAL,
                        DataAssetPurpose.CALIBRATION_EVIDENCE,
                        "Structured CalibrationSignal evidence.",
                        path=path,
                        sample_schema=_calibration_schema(path),
                    ),
                    _asset(
                        f"{_path_slug(path)}-experiment-export",
                        DataAssetType.EXPERIMENT_EXPORT_DATA,
                        DataAssetRequirementLevel.CONDITIONAL,
                        DataAssetPurpose.EXPERIMENT_EVIDENCE,
                        "Governed experiment export when CalibrationSignal is not yet mapped.",
                        path=path,
                        sample_schema=_experiment_export_schema(path),
                    ),
                    _asset(
                        f"{_path_slug(path)}-metric-mapping",
                        DataAssetType.METRIC_MAPPING,
                        DataAssetRequirementLevel.REQUIRED,
                        DataAssetPurpose.SEMANTIC_MAPPING,
                        "Canonical metric mapping for calibration intake.",
                        path=path,
                    ),
                    _asset(
                        f"{_path_slug(path)}-channel-mapping",
                        DataAssetType.CHANNEL_MAPPING,
                        DataAssetRequirementLevel.REQUIRED,
                        DataAssetPurpose.SEMANTIC_MAPPING,
                        "Canonical channel mapping for calibration intake.",
                        path=path,
                        sample_schema=_channel_mapping_schema(path),
                    ),
                ],
            )
        )

    if path == IntakeCandidatePath.DECISION_REVIEW_PACKET:
        return IntakePlan(
            **_plan(
                warnings=[
                    *base_kwargs["warnings"],
                    "TrustReport and evidence export assembly are deferred to later phases.",
                    "Decision packet requires evidence alignment, TrustReport, uncertainty, "
                    "and approval state.",
                ],
                blocked_assets=[
                    _asset(
                        f"{_path_slug(path)}-trust-report",
                        DataAssetType.EXPERIMENT_EXPORT_DATA,
                        DataAssetRequirementLevel.BLOCKED_UNTIL_LATER_PHASE,
                        DataAssetPurpose.GOVERNANCE_CONTEXT,
                        "TrustReport and governed evidence export context.",
                        path=path,
                        blocks_if_missing=False,
                    )
                ],
                required_assets=[
                    _asset(
                        f"{_path_slug(path)}-metric-mapping",
                        DataAssetType.METRIC_MAPPING,
                        DataAssetRequirementLevel.CONDITIONAL,
                        DataAssetPurpose.SEMANTIC_MAPPING,
                        "Metric alignment for decision review packet.",
                        path=path,
                    )
                ],
            )
        )

    return _blocked_plan(recommendation)
