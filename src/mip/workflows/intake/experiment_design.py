"""Deterministic experiment design objective and data requirement helpers (P4b / I6b)."""

from datetime import UTC, datetime

from mip.contracts.experiment_design_intake import (
    ExperimentDesignDataRequirement,
    ExperimentDesignEntryPath,
    ExperimentDesignIntake,
    ExperimentDesignObjective,
    ExperimentDesignStatus,
    ExperimentDesignTriggerReason,
    ExperimentDiagnosticRequest,
    ExperimentDiagnosticRequestStatus,
    ExperimentKpiFamily,
    ExperimentObjectiveCategory,
    MMMToGeoXDesignBridge,
    StandaloneGeoXDesignRequest,
)
from mip.contracts.intake import (
    DataGrain,
    GeoGrain,
    IntakePathRecommendation,
    MeasurementIntakeSession,
)
from mip.contracts.intake_assets import DataAssetType

_GEO_LEVEL_GRAINS = frozenset(
    {GeoGrain.GEO, GeoGrain.DMA, GeoGrain.REGION, GeoGrain.MARKET},
)

_KPI_LABELS_BY_FAMILY: dict[ExperimentKpiFamily, list[str]] = {
    ExperimentKpiFamily.AWARENESS_SEARCH: [
        "BSV",
        "branded search",
        "direct traffic",
        "reach proxy",
    ],
    ExperimentKpiFamily.TRAFFIC: ["visits", "visitors", "sessions"],
    ExperimentKpiFamily.FUNNEL_ENGAGEMENT: [
        "product-page visits",
        "funnel engagement",
        "signups",
    ],
    ExperimentKpiFamily.TRIALS_LEADS: ["trials", "leads", "signups"],
    ExperimentKpiFamily.CONVERSION_SALES: ["conversions", "orders", "sales"],
    ExperimentKpiFamily.REVENUE_ARR: ["ARR", "GNARR", "revenue", "trials-to-paid"],
    ExperimentKpiFamily.RETENTION_USAGE: [
        "active users",
        "usage events",
        "renewal",
        "churn",
    ],
    ExperimentKpiFamily.CALIBRATION_ALIGNED: [
        "MMM metric-aligned KPI",
        "estimand-aligned KPI",
    ],
    ExperimentKpiFamily.UNKNOWN: [],
}


def suggest_kpi_families_for_objective(
    objective_category: ExperimentObjectiveCategory,
) -> list[ExperimentKpiFamily]:
    """Map experiment objective category to candidate KPI families."""
    mapping: dict[ExperimentObjectiveCategory, list[ExperimentKpiFamily]] = {
        ExperimentObjectiveCategory.AWARENESS: [
            ExperimentKpiFamily.AWARENESS_SEARCH,
            ExperimentKpiFamily.TRAFFIC,
        ],
        ExperimentObjectiveCategory.DEMAND_CREATION: [
            ExperimentKpiFamily.TRAFFIC,
            ExperimentKpiFamily.FUNNEL_ENGAGEMENT,
            ExperimentKpiFamily.TRIALS_LEADS,
        ],
        ExperimentObjectiveCategory.CONVERSION: [
            ExperimentKpiFamily.CONVERSION_SALES,
            ExperimentKpiFamily.REVENUE_ARR,
        ],
        ExperimentObjectiveCategory.RETENTION_USAGE: [
            ExperimentKpiFamily.RETENTION_USAGE,
        ],
        ExperimentObjectiveCategory.MMM_CALIBRATION: [
            ExperimentKpiFamily.CALIBRATION_ALIGNED,
        ],
        ExperimentObjectiveCategory.INCREMENTALITY_VALIDATION: [
            ExperimentKpiFamily.CALIBRATION_ALIGNED,
            ExperimentKpiFamily.UNKNOWN,
        ],
        ExperimentObjectiveCategory.UNKNOWN: [ExperimentKpiFamily.UNKNOWN],
    }
    return list(mapping[objective_category])


def suggest_kpi_labels_for_families(
    families: list[ExperimentKpiFamily],
) -> list[str]:
    """Return illustrative KPI labels for candidate families."""
    labels: list[str] = []
    seen: set[str] = set()
    for family in families:
        for label in _KPI_LABELS_BY_FAMILY.get(family, []):
            if label not in seen:
                seen.add(label)
                labels.append(label)
    return labels


def _requirement(
    *,
    requirement_id: str,
    objective_category: ExperimentObjectiveCategory,
    kpi_family: ExperimentKpiFamily,
    required_assets: list[DataAssetType],
    recommended_assets: list[DataAssetType],
    minimum_geo_grain: GeoGrain,
    minimum_time_grain: DataGrain,
    required_history_guidance: str,
    why_required: str,
    warnings: list[str] | None = None,
) -> ExperimentDesignDataRequirement:
    return ExperimentDesignDataRequirement(
        requirement_id=requirement_id,
        objective_category=objective_category,
        kpi_family=kpi_family,
        required_data_assets=required_assets,
        recommended_data_assets=recommended_assets,
        minimum_geo_grain=minimum_geo_grain,
        minimum_time_grain=minimum_time_grain,
        required_history_guidance=required_history_guidance,
        why_required=why_required,
        warnings=warnings or [],
    )


def build_experiment_design_data_requirements(
    objective: ExperimentDesignObjective,
) -> list[ExperimentDesignDataRequirement]:
    """Build objective-specific data requirement guidance (not data validation)."""
    category = objective.objective_category
    geo = objective.geo_grain
    min_geo = geo if geo != GeoGrain.UNKNOWN else GeoGrain.DMA
    min_time = DataGrain.WEEKLY
    prefix = objective.objective_id

    if category == ExperimentObjectiveCategory.AWARENESS:
        return [
            _requirement(
                requirement_id=f"{prefix}-awareness-kpi",
                objective_category=category,
                kpi_family=ExperimentKpiFamily.AWARENESS_SEARCH,
                required_assets=[
                    DataAssetType.OUTCOME_KPI_DATA,
                    DataAssetType.MEDIA_SPEND_DATA,
                    DataAssetType.MEDIA_EXPOSURE_DATA,
                    DataAssetType.GEO_MAPPING,
                ],
                recommended_assets=[
                    DataAssetType.CONTROL_DATA,
                    DataAssetType.CALENDAR_SEASONALITY_DATA,
                    DataAssetType.CHANNEL_MAPPING,
                    DataAssetType.PRODUCT_MAPPING,
                ],
                minimum_geo_grain=min_geo,
                minimum_time_grain=min_time,
                required_history_guidance=(
                    "Sufficient pre-period geo-time history to profile awareness or traffic KPI "
                    "variation before design diagnostics; final duration is not certified here."
                ),
                why_required=(
                    "Awareness objectives need geo-time awareness or traffic KPI series, "
                    "platform spend/exposure, campaign timing context, and geo mapping."
                ),
            ),
        ]

    if category == ExperimentObjectiveCategory.DEMAND_CREATION:
        return [
            _requirement(
                requirement_id=f"{prefix}-demand-funnel",
                objective_category=category,
                kpi_family=ExperimentKpiFamily.FUNNEL_ENGAGEMENT,
                required_assets=[
                    DataAssetType.OUTCOME_KPI_DATA,
                    DataAssetType.MEDIA_SPEND_DATA,
                    DataAssetType.MEDIA_EXPOSURE_DATA,
                    DataAssetType.CHANNEL_MAPPING,
                    DataAssetType.GEO_MAPPING,
                ],
                recommended_assets=[
                    DataAssetType.CONTROL_DATA,
                    DataAssetType.CALENDAR_SEASONALITY_DATA,
                    DataAssetType.PRODUCT_MAPPING,
                ],
                minimum_geo_grain=min_geo,
                minimum_time_grain=min_time,
                required_history_guidance=(
                    "Pre-period geo-time funnel history should cover typical campaign cadence; "
                    "exact test duration is deferred to panel_exp diagnostics."
                ),
                why_required=(
                    "Demand creation needs geo-time funnel metrics, spend/exposure, "
                    "campaign/tactic mapping, and geo mapping."
                ),
            ),
        ]

    if category == ExperimentObjectiveCategory.CONVERSION:
        return [
            _requirement(
                requirement_id=f"{prefix}-conversion-sales",
                objective_category=category,
                kpi_family=ExperimentKpiFamily.CONVERSION_SALES,
                required_assets=[
                    DataAssetType.OUTCOME_KPI_DATA,
                    DataAssetType.MEDIA_SPEND_DATA,
                    DataAssetType.MEDIA_EXPOSURE_DATA,
                    DataAssetType.PRICING_PROMO_DATA,
                    DataAssetType.CALENDAR_SEASONALITY_DATA,
                    DataAssetType.GEO_MAPPING,
                ],
                recommended_assets=[
                    DataAssetType.CHANNEL_MAPPING,
                    DataAssetType.PRODUCT_MAPPING,
                ],
                minimum_geo_grain=min_geo,
                minimum_time_grain=min_time,
                required_history_guidance=(
                    "Longer pre-period history helps profile conversion seasonality and promo "
                    "effects; this guidance is qualitative only."
                ),
                why_required=(
                    "Conversion objectives need geo-time conversion or sales KPI, media "
                    "spend/exposure, promo/pricing/seasonality context, and geo mapping."
                ),
            ),
        ]

    if category == ExperimentObjectiveCategory.RETENTION_USAGE:
        return [
            _requirement(
                requirement_id=f"{prefix}-retention-usage",
                objective_category=category,
                kpi_family=ExperimentKpiFamily.RETENTION_USAGE,
                required_assets=[
                    DataAssetType.OUTCOME_KPI_DATA,
                    DataAssetType.MEDIA_EXPOSURE_DATA,
                    DataAssetType.GEO_MAPPING,
                    DataAssetType.PRODUCT_MAPPING,
                ],
                recommended_assets=[
                    DataAssetType.CONTROL_DATA,
                    DataAssetType.CALENDAR_SEASONALITY_DATA,
                ],
                minimum_geo_grain=min_geo,
                minimum_time_grain=min_time,
                required_history_guidance=(
                    "Retention/usage designs benefit from exposure/treatment history across geos; "
                    "final feasibility is not certified here."
                ),
                why_required=(
                    "Retention/usage objectives need geo-time usage or retention metrics, "
                    "exposure/treatment history, and geo/product mapping."
                ),
            ),
        ]

    if category == ExperimentObjectiveCategory.MMM_CALIBRATION:
        return [
            _requirement(
                requirement_id=f"{prefix}-mmm-calibration",
                objective_category=category,
                kpi_family=ExperimentKpiFamily.CALIBRATION_ALIGNED,
                required_assets=[
                    DataAssetType.OUTCOME_KPI_DATA,
                    DataAssetType.MEDIA_SPEND_DATA,
                    DataAssetType.MEDIA_EXPOSURE_DATA,
                    DataAssetType.METRIC_MAPPING,
                    DataAssetType.CALIBRATION_SIGNAL_DATA,
                    DataAssetType.EXPERIMENT_EXPORT_DATA,
                ],
                recommended_assets=[
                    DataAssetType.GEO_MAPPING,
                    DataAssetType.CHANNEL_MAPPING,
                    DataAssetType.PRODUCT_MAPPING,
                ],
                minimum_geo_grain=min_geo,
                minimum_time_grain=min_time,
                required_history_guidance=(
                    "Experiment design and readout path must be able to produce effect estimate "
                    "and uncertainty aligned to MMM metric/estimand/scope."
                ),
                why_required=(
                    "MMM calibration needs KPI aligned to MMM metric/estimand/scope and an "
                    "experiment path that can yield CalibrationSignal-compatible evidence."
                ),
            ),
        ]

    if category == ExperimentObjectiveCategory.INCREMENTALITY_VALIDATION:
        return [
            _requirement(
                requirement_id=f"{prefix}-incrementality",
                objective_category=category,
                kpi_family=ExperimentKpiFamily.CALIBRATION_ALIGNED,
                required_assets=[
                    DataAssetType.OUTCOME_KPI_DATA,
                    DataAssetType.MEDIA_SPEND_DATA,
                    DataAssetType.GEO_MAPPING,
                ],
                recommended_assets=[
                    DataAssetType.MEDIA_EXPOSURE_DATA,
                    DataAssetType.CALIBRATION_SIGNAL_DATA,
                ],
                minimum_geo_grain=min_geo,
                minimum_time_grain=min_time,
                required_history_guidance=(
                    "Incrementality validation depends on the supplied KPI and objective; confirm "
                    "KPI family before design diagnostics."
                ),
                why_required=(
                    "Incrementality validation needs outcome KPI, media inputs, and geo mapping "
                    "aligned to the stated validation objective."
                ),
                warnings=[
                    "Incrementality validation KPI family depends on supplied objective; "
                    "calibration_aligned included with caution.",
                ],
            ),
        ]

    return [
        _requirement(
            requirement_id=f"{prefix}-unknown",
            objective_category=category,
            kpi_family=ExperimentKpiFamily.UNKNOWN,
            required_assets=[],
            recommended_assets=[],
            minimum_geo_grain=GeoGrain.UNKNOWN,
            minimum_time_grain=DataGrain.UNKNOWN,
            required_history_guidance="Clarify objective category before data requirements.",
            why_required="Objective category is unknown; data requirements cannot be finalized.",
            warnings=["Objective category unknown."],
        ),
    ]


def _clarification_questions_for_objective(
    objective: ExperimentDesignObjective,
) -> list[str]:
    questions: list[str] = []
    if objective.objective_category == ExperimentObjectiveCategory.UNKNOWN:
        questions.append(
            "Which experiment objective category applies: awareness, demand creation, "
            "conversion, retention/usage, or MMM calibration?"
        )
    if not objective.product_scope:
        questions.append("Which product scope should the experiment cover?")
    if not objective.platform_scope:
        questions.append("Which platform scope (e.g. Meta, Google) should the experiment target?")
    if objective.geo_grain == GeoGrain.UNKNOWN:
        questions.append("What geo grain is required (DMA, market, region, or country)?")
    if not objective.market_scope and objective.geo_grain in _GEO_LEVEL_GRAINS:
        questions.append("Which markets or geos should be in scope for the design?")
    if not objective.primary_kpi_candidates and objective.candidate_kpi_families:
        questions.append(
            "Which primary KPI candidate should govern the experiment objective "
            f"from families {objective.candidate_kpi_families}?"
        )
    return questions


def _build_objective_from_inputs(
    *,
    entry_path: ExperimentDesignEntryPath,
    objective_category: ExperimentObjectiveCategory,
    session: MeasurementIntakeSession,
    mmm_bridge: MMMToGeoXDesignBridge | None,
    standalone_request: StandaloneGeoXDesignRequest | None,
) -> ExperimentDesignObjective:
    if entry_path == ExperimentDesignEntryPath.MMM_DRIVEN and mmm_bridge is not None:
        families = suggest_kpi_families_for_objective(objective_category)
        labels = suggest_kpi_labels_for_families(families)
        return ExperimentDesignObjective(
            objective_id=f"{session.session_id}-exp-obj",
            entry_path=entry_path,
            objective_category=objective_category,
            business_question=session.business_question,
            product_scope=mmm_bridge.product_scope or session.product_scope,
            platform_scope=mmm_bridge.platform_scope or session.platform_scope,
            channel_scope=mmm_bridge.channel_scope or session.channel_scope,
            tactic_scope=session.campaign_scope,
            geo_grain=session.geo_grain,
            market_scope=mmm_bridge.geo_scope or session.market_scope,
            candidate_kpi_families=families,
            primary_kpi_candidates=labels,
            intended_decision=session.desired_output,
            created_at=datetime.now(tz=UTC),
        )

    assert standalone_request is not None
    families = standalone_request.candidate_kpi_families or suggest_kpi_families_for_objective(
        standalone_request.objective_category
    )
    labels = standalone_request.primary_kpi_candidates or suggest_kpi_labels_for_families(families)
    return ExperimentDesignObjective(
        objective_id=f"{session.session_id}-exp-obj",
        entry_path=entry_path,
        objective_category=standalone_request.objective_category,
        business_question=standalone_request.business_question,
        product_scope=standalone_request.product_scope,
        platform_scope=standalone_request.platform_scope,
        channel_scope=standalone_request.channel_scope,
        tactic_scope=standalone_request.tactic_scope,
        geo_grain=standalone_request.geo_grain,
        market_scope=standalone_request.market_scope,
        candidate_kpi_families=families,
        primary_kpi_candidates=labels,
        intended_decision=session.desired_output,
        created_at=datetime.now(tz=UTC),
    )


def build_experiment_design_intake(
    session: MeasurementIntakeSession,
    recommendation: IntakePathRecommendation,
    *,
    entry_path: ExperimentDesignEntryPath,
    objective_category: ExperimentObjectiveCategory,
    mmm_bridge: MMMToGeoXDesignBridge | None = None,
    standalone_request: StandaloneGeoXDesignRequest | None = None,
) -> ExperimentDesignIntake:
    """Assemble experiment design intake from session intent and entry path."""
    if entry_path == ExperimentDesignEntryPath.MMM_DRIVEN and mmm_bridge is None:
        msg = "mmm_driven entry_path requires mmm_bridge"
        raise ValueError(msg)
    if entry_path == ExperimentDesignEntryPath.STANDALONE_GEOX and standalone_request is None:
        msg = "standalone_geox entry_path requires standalone_request"
        raise ValueError(msg)

    objective = _build_objective_from_inputs(
        entry_path=entry_path,
        objective_category=objective_category,
        session=session,
        mmm_bridge=mmm_bridge,
        standalone_request=standalone_request,
    )
    data_requirements = build_experiment_design_data_requirements(objective)
    clarification_questions = _clarification_questions_for_objective(objective)

    if standalone_request and standalone_request.clarification_questions:
        for question in standalone_request.clarification_questions:
            if question not in clarification_questions:
                clarification_questions.append(question)

    warnings: list[str] = []
    blocking_reasons: list[str] = []
    status = ExperimentDesignStatus.DRAFT
    allowed_next_steps: list[str] = []
    blocked_next_steps: list[str] = []

    if objective.objective_category == ExperimentObjectiveCategory.UNKNOWN:
        status = ExperimentDesignStatus.NEEDS_CLARIFICATION
    elif clarification_questions:
        status = ExperimentDesignStatus.NEEDS_CLARIFICATION
    else:
        status = ExperimentDesignStatus.REQUIREMENTS_READY
        allowed_next_steps.append("review_experiment_design_data_requirements")
        allowed_next_steps.append("prepare_panel_exp_diagnostic_request")

    if status == ExperimentDesignStatus.REQUIREMENTS_READY:
        blocked_next_steps.append("execute_panel_exp_diagnostics")
        blocked_next_steps.append("claim_design_feasibility")

    if (
        objective_category == ExperimentObjectiveCategory.MMM_CALIBRATION
        and mmm_bridge is not None
        and not mmm_bridge.requires_calibration_signal_output
    ):
        mmm_bridge = mmm_bridge.model_copy(update={"requires_calibration_signal_output": True})
        warnings.append(
            "MMM calibration objective requires CalibrationSignal-compatible output; flag set."
        )

    return ExperimentDesignIntake(
        intake_id=f"{session.session_id}-exp-intake",
        session_id=session.session_id,
        recommendation_id=recommendation.recommendation_id,
        entry_path=entry_path,
        objective=objective,
        mmm_bridge=mmm_bridge,
        standalone_request=standalone_request,
        data_requirements=data_requirements,
        clarification_questions=clarification_questions,
        status=status,
        allowed_next_steps=allowed_next_steps,
        blocked_next_steps=blocked_next_steps,
        warnings=warnings,
        blocking_reasons=blocking_reasons,
        created_at=datetime.now(tz=UTC),
    )


def _collect_required_data_assets(
    intake: ExperimentDesignIntake,
) -> list[DataAssetType]:
    assets: list[DataAssetType] = []
    seen: set[str] = set()
    for requirement in intake.data_requirements:
        for asset in requirement.required_data_assets:
            key = asset.value if isinstance(asset, DataAssetType) else asset
            if key not in seen:
                seen.add(key)
                assets.append(asset)
    return assets


def build_experiment_diagnostic_request(
    intake: ExperimentDesignIntake,
) -> ExperimentDiagnosticRequest:
    """Build a future panel_exp diagnostic request without executing diagnostics."""
    objective = intake.objective
    geo_grain = objective.geo_grain
    is_geo_level = geo_grain in _GEO_LEVEL_GRAINS

    if intake.status == ExperimentDesignStatus.REQUIREMENTS_READY:
        status = ExperimentDiagnosticRequestStatus.READY_FOR_PANEL_EXP_DIAGNOSTICS
    elif intake.status == ExperimentDesignStatus.NEEDS_CLARIFICATION:
        status = ExperimentDiagnosticRequestStatus.NEEDS_DATA
    elif intake.status == ExperimentDesignStatus.BLOCKED:
        status = ExperimentDiagnosticRequestStatus.BLOCKED
    else:
        status = ExperimentDiagnosticRequestStatus.DRAFT

    requires_calibration = (
        objective.objective_category == ExperimentObjectiveCategory.MMM_CALIBRATION
        or (
            intake.mmm_bridge is not None
            and intake.mmm_bridge.requires_calibration_signal_output
        )
    )

    blocking_reasons = list(intake.blocking_reasons)
    if status == ExperimentDiagnosticRequestStatus.BLOCKED and not blocking_reasons:
        blocking_reasons.append("Experiment design intake is blocked.")

    return ExperimentDiagnosticRequest(
        diagnostic_request_id=f"{intake.intake_id}-diag-req",
        experiment_intake_id=intake.intake_id,
        session_id=intake.session_id,
        entry_path=intake.entry_path,
        objective_category=objective.objective_category,
        candidate_kpi_families=objective.candidate_kpi_families,
        product_scope=objective.product_scope,
        platform_scope=objective.platform_scope,
        channel_scope=objective.channel_scope,
        tactic_scope=objective.tactic_scope,
        geo_grain=geo_grain,
        market_scope=objective.market_scope,
        required_data_assets=_collect_required_data_assets(intake),
        requires_power_diagnostic=True,
        requires_matchability_diagnostic=is_geo_level,
        requires_duration_sensitivity=True,
        requires_calibration_signal_output=requires_calibration,
        status=status,
        warnings=list(intake.warnings),
        blocking_reasons=blocking_reasons,
        created_at=datetime.now(tz=UTC),
    )


def build_mmm_to_geox_bridge(
    *,
    bridge_id: str,
    trigger_reason: ExperimentDesignTriggerReason,
    why_experiment_needed: str,
    objective_category: ExperimentObjectiveCategory,
    source_mmm_artifact_id: str | None = None,
    source_trust_report_id: str | None = None,
    source_recommendation_id: str | None = None,
    channel_scope: str | None = None,
    platform_scope: str | None = None,
    product_scope: str | None = None,
    geo_scope: str | None = None,
    metric_id: str | None = None,
    estimand_id: str | None = None,
) -> MMMToGeoXDesignBridge:
    """Convenience builder for MMM→GeoX design bridge with calibration defaults."""
    requires_calibration = objective_category == ExperimentObjectiveCategory.MMM_CALIBRATION
    return MMMToGeoXDesignBridge(
        bridge_id=bridge_id,
        source_mmm_artifact_id=source_mmm_artifact_id,
        source_trust_report_id=source_trust_report_id,
        source_recommendation_id=source_recommendation_id,
        trigger_reason=trigger_reason,
        channel_scope=channel_scope,
        platform_scope=platform_scope,
        product_scope=product_scope,
        geo_scope=geo_scope,
        metric_id=metric_id,
        estimand_id=estimand_id,
        why_experiment_needed=why_experiment_needed,
        requires_calibration_signal_output=requires_calibration,
        created_at=datetime.now(tz=UTC),
    )
