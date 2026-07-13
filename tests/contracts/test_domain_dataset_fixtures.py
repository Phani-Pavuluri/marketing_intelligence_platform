"""Contract tests for domain dataset fixture schema/manifests."""

from __future__ import annotations

import inspect

import mip.contracts as contracts
import mip.contracts.domain_dataset_fixtures as domain_dataset_fixtures
from mip.contracts.domain_dataset_fixtures import (
    ARTIFACT_ID,
    DomainDatasetFixtureManifest,
    DomainFixtureBusinessDomain,
    DomainFixtureCalibrationSignalExpectation,
    DomainFixtureColumnExpectation,
    DomainFixtureControlSignalExpectation,
    DomainFixtureControlSignalType,
    DomainFixtureDatasetFamily,
    DomainFixtureExpectedBehavior,
    DomainFixtureExpectedDecision,
    DomainFixtureExperimentMetadataExpectation,
    DomainFixtureIssueCode,
    DomainFixtureKPIType,
    DomainFixtureLLMDemoScenario,
    DomainFixtureOwner,
    DomainFixtureReadinessExpectation,
    DomainFixtureReadinessStatus,
    DomainFixtureTier,
    build_domain_dataset_fixture_manifest,
    summarize_domain_dataset_fixture_manifest,
)


def _base_columns() -> tuple[DomainFixtureColumnExpectation, ...]:
    return (
        DomainFixtureColumnExpectation(
            column_name="date",
            semantic_role="time",
            expected_dtype="date",
            description="Panel period key",
        ),
        DomainFixtureColumnExpectation(
            column_name="channel",
            semantic_role="spend_channel",
            expected_dtype="string",
            description="Marketing channel",
        ),
        DomainFixtureColumnExpectation(
            column_name="spend",
            semantic_role="spend",
            expected_dtype="float",
            description="Channel spend",
        ),
    )


def _blocked_behavior() -> DomainFixtureExpectedBehavior:
    return DomainFixtureExpectedBehavior(
        expected_decisions=(
            DomainFixtureExpectedDecision.ALLOW_DESCRIPTIVE_ANSWER.value,
            DomainFixtureExpectedDecision.BLOCK_RECOMMENDATION.value,
            DomainFixtureExpectedDecision.BLOCK_ROI_ROAS_LIFT_CLAIM.value,
            DomainFixtureExpectedDecision.DEFER_PENDING_HUMAN_REVIEW.value,
        ),
        can_say_expectations=(
            "Describe spend coverage and KPI trends",
            "State readiness and missing controls",
        ),
        cannot_say_expectations=(
            "Recommend budget reallocation",
            "Claim causal ROI or ROAS",
            "Invent incrementality",
        ),
        blocked_reason_expectations=("recommendation_not_authorized",),
        deferred_reason_expectations=("human_review_required",),
        human_review_required=True,
        forbidden_recommendations=(
            "increase_spend_on_channel_x",
            "reallocate_budget_to_maximize_roi",
        ),
        description="Descriptive answers allowed; recommendations blocked",
    )


def _demo_scenario(scenario_id: str, question: str) -> DomainFixtureLLMDemoScenario:
    return DomainFixtureLLMDemoScenario(
        scenario_id=scenario_id,
        user_question=question,
        expected_response_mode="descriptive_with_refusal",
        expected_can_say=("Describe panel coverage",),
        expected_cannot_say=("Recommend budget changes",),
        expected_refusal=True,
        expected_evidence_refs=("fixture_manifest",),
        description="Demo/eval scenario metadata only",
    )


def _panel_manifest(
    *,
    fixture_id: str,
    business_domain: DomainFixtureBusinessDomain,
    primary_kpis: tuple[str, ...],
    spend_channels: tuple[str, ...],
    control_types: tuple[DomainFixtureControlSignalType, ...],
    tier: DomainFixtureTier = DomainFixtureTier.TIER_1_TINY_DETERMINISTIC,
    owner: DomainFixtureOwner = DomainFixtureOwner.MIP,
) -> DomainDatasetFixtureManifest:
    return build_domain_dataset_fixture_manifest(
        fixture_id=fixture_id,
        tier=tier,
        business_domain=business_domain,
        dataset_family=DomainFixtureDatasetFamily.MMM_SPEND_KPI_PANEL,
        owner=owner,
        primary_kpis=primary_kpis,
        secondary_kpis=(),
        spend_channels=spend_channels,
        column_expectations=_base_columns(),
        control_signal_expectations=tuple(
            DomainFixtureControlSignalExpectation(
                signal_type=signal.value,
                required=True,
                expected_columns=(f"{signal.value.lower()}_flag",),
                description=f"Expect {signal.value}",
            )
            for signal in control_types
        ),
        calibration_signal_expectation=DomainFixtureCalibrationSignalExpectation(
            required=False,
            expected_channel=spend_channels[0] if spend_channels else "",
            expected_kpi=primary_kpis[0] if primary_kpis else "",
            expected_estimand="incremental_effect",
            requires_uncertainty=True,
            requires_time_window=True,
            description="Optional calibration metadata expectation",
        ),
        experiment_metadata_expectation=DomainFixtureExperimentMetadataExpectation(
            required=False,
            description="Optional experiment metadata",
        ),
        readiness_expectation=DomainFixtureReadinessExpectation(
            readiness_status=DomainFixtureReadinessStatus.PARTIALLY_READY.value,
            required_rows_min=12,
            required_time_periods_min=12,
            required_channel_count_min=len(spend_channels),
            required_control_signals=tuple(s.value for s in control_types),
            description="Minimum panel sufficiency",
        ),
        expected_behavior=_blocked_behavior(),
        llm_demo_scenarios=(
            _demo_scenario(
                f"{fixture_id}_q1",
                f"What can you say about {business_domain.value} spend?",
            ),
        ),
        metadata={"example": True},
    )


def test_required_enums_contain_required_values() -> None:
    assert DomainFixtureTier.TIER_1_TINY_DETERMINISTIC.value in {
        i.value for i in DomainFixtureTier
    }
    assert DomainFixtureTier.TIER_2_REALISTIC_SYNTHETIC_PANEL.value in {
        i.value for i in DomainFixtureTier
    }
    assert DomainFixtureTier.TIER_3_PACKAGE_EXPORTED_METHOD_SIMULATION_SNAPSHOT.value in {
        i.value for i in DomainFixtureTier
    }

    domains = {i.value for i in DomainFixtureBusinessDomain}
    for required in (
        "SAAS_SUBSCRIPTIONS",
        "ECOMMERCE",
        "MOBILE_APP",
        "B2B_PIPELINE",
        "GEO_LOCAL_EXPERIMENTS",
    ):
        assert required in domains

    families = {i.value for i in DomainFixtureDatasetFamily}
    for required in (
        "MMM_SPEND_KPI_PANEL",
        "GEOX_CALIBRATION_SIGNAL",
        "CONTROL_SIGNAL_CATALOG",
        "EXPERIMENT_METADATA",
        "DATA_SUFFICIENCY_READINESS",
        "LLM_DEMO_EVAL_SCENARIO",
        "PACKAGE_EXPORTED_SIMULATION_SNAPSHOT",
    ):
        assert required in families

    owners = {i.value for i in DomainFixtureOwner}
    for required in ("MIP", "MMM_PACKAGE", "GEOX_PACKAGE", "EXTERNAL_REFERENCE"):
        assert required in owners

    decisions = {i.value for i in DomainFixtureExpectedDecision}
    for required in (
        "ALLOW_DESCRIPTIVE_ANSWER",
        "ALLOW_DIAGNOSTIC_ANSWER",
        "ALLOW_REFUSAL_ONLY",
        "DEFER_PENDING_DATA",
        "DEFER_PENDING_MODEL",
        "DEFER_PENDING_CALIBRATION",
        "DEFER_PENDING_HUMAN_REVIEW",
        "BLOCK_RECOMMENDATION",
        "BLOCK_OPTIMIZATION",
        "BLOCK_ROI_ROAS_LIFT_CLAIM",
        "BLOCK_CAUSAL_CLAIM",
        "BLOCK_UNSUPPORTED_DATA",
    ):
        assert required in decisions

    readiness = {i.value for i in DomainFixtureReadinessStatus}
    for required in (
        "READY",
        "PARTIALLY_READY",
        "INSUFFICIENT_DATA",
        "SCHEMA_INCOMPATIBLE",
        "CONTROL_SIGNAL_MISSING",
        "CALIBRATION_INCOMPATIBLE",
        "MODEL_RUN_REQUIRED",
        "HUMAN_REVIEW_REQUIRED",
        "BLOCKED",
    ):
        assert required in readiness

    controls = {i.value for i in DomainFixtureControlSignalType}
    for required in (
        "PROMOTION_CALENDAR",
        "PRODUCT_LAUNCH",
        "PRICING_DISCOUNT",
        "MACRO_INDEX",
        "SALES_CAPACITY",
        "INVENTORY_STOCKOUT",
        "APP_RELEASE",
        "HOLIDAY",
        "SEASONALITY",
        "LOCAL_EVENT",
        "COMPETITOR_ACTIVITY",
    ):
        assert required in controls

    kpis = {i.value for i in DomainFixtureKPIType}
    for required in (
        "ARR",
        "TRIALS",
        "PAID_CONVERSIONS",
        "CHURN",
        "REVENUE",
        "ORDERS",
        "AOV",
        "NEW_CUSTOMERS",
        "INSTALLS",
        "D2P",
        "SUBSCRIPTIONS",
        "RETENTION",
        "LEADS",
        "MQLS",
        "SQLS",
        "PIPELINE",
        "BOOKINGS",
        "TRAFFIC",
        "STORE_VISITS",
    ):
        assert required in kpis

    issues = {i.value for i in DomainFixtureIssueCode}
    for required in (
        "FIXTURE_MANIFEST_DEFINED",
        "TIER_DEFINED",
        "DOMAIN_DEFINED",
        "DATASET_FAMILY_DEFINED",
        "OWNER_BOUNDARY_DEFINED",
        "SPEND_KPI_SCHEMA_EXPECTATION_DEFINED",
        "CONTROL_SIGNAL_SCHEMA_EXPECTATION_DEFINED",
        "CALIBRATION_SIGNAL_EXPECTATION_DEFINED",
        "EXPERIMENT_METADATA_EXPECTATION_DEFINED",
        "READINESS_EXPECTATION_DEFINED",
        "EXPECTED_DECISION_DEFINED",
        "CAN_SAY_CANNOT_SAY_EXPECTATION_DEFINED",
        "HUMAN_REVIEW_EXPECTATION_DEFINED",
        "FORBIDDEN_RECOMMENDATION_EXPECTATION_DEFINED",
        "LLM_DEMO_EVAL_SCENARIO_DEFINED",
        "NO_DATASET_GENERATION",
        "NO_MMM_FITTING",
        "NO_GEOX_ESTIMATOR_LOGIC",
        "NO_PRODUCTION_CONNECTOR",
        "NO_DECISION_SURFACE_GENERATION",
        "NO_RECOMMENDATION_CONTRACT_GENERATION",
        "NO_OPTIMIZER_SIMULATOR",
        "NO_ROI_ROAS_LIFT_INCREMENTALITY_COMPUTATION",
        "NO_LLM_PROVIDER_EXECUTION",
    ):
        assert required in issues


def test_column_expectation_serializes() -> None:
    model = DomainFixtureColumnExpectation(
        column_name="revenue",
        semantic_role="kpi",
        required=True,
        expected_dtype="float",
        allowed_values=(),
        description="Primary KPI",
    )
    payload = model.model_dump()
    assert payload["column_name"] == "revenue"
    assert payload["semantic_role"] == "kpi"


def test_control_signal_expectation_serializes() -> None:
    model = DomainFixtureControlSignalExpectation(
        signal_type=DomainFixtureControlSignalType.HOLIDAY.value,
        required=True,
        expected_columns=("holiday_flag",),
        description="Holiday control",
    )
    payload = model.model_dump()
    assert payload["signal_type"] == "HOLIDAY"
    assert payload["expected_columns"] == ("holiday_flag",)


def test_calibration_signal_expectation_serializes() -> None:
    model = DomainFixtureCalibrationSignalExpectation(
        required=True,
        expected_channel="paid_search",
        expected_kpi="ARR",
        expected_estimand="incremental_effect",
        requires_uncertainty=True,
        requires_time_window=True,
        requires_geo_scope=False,
        description="Calibration expectation",
    )
    payload = model.model_dump()
    assert payload["expected_channel"] == "paid_search"
    assert payload["requires_uncertainty"] is True


def test_experiment_metadata_expectation_serializes() -> None:
    model = DomainFixtureExperimentMetadataExpectation(
        required=True,
        requires_experiment_id=True,
        requires_assignment_metadata=True,
        requires_time_window=True,
        requires_treatment_control_scope=True,
        description="Experiment metadata",
    )
    payload = model.model_dump()
    assert payload["requires_experiment_id"] is True


def test_readiness_expectation_serializes() -> None:
    model = DomainFixtureReadinessExpectation(
        readiness_status=DomainFixtureReadinessStatus.READY.value,
        required_rows_min=52,
        required_time_periods_min=52,
        required_geo_count_min=0,
        required_channel_count_min=3,
        required_control_signals=("HOLIDAY",),
        description="Ready panel",
    )
    payload = model.model_dump()
    assert payload["readiness_status"] == "READY"
    assert payload["required_rows_min"] == 52


def test_expected_behavior_serializes() -> None:
    model = _blocked_behavior()
    payload = model.model_dump()
    assert DomainFixtureExpectedDecision.BLOCK_RECOMMENDATION.value in payload[
        "expected_decisions"
    ]
    assert payload["human_review_required"] is True
    assert "Recommend budget reallocation" in payload["cannot_say_expectations"]


def test_llm_demo_scenario_serializes() -> None:
    model = _demo_scenario("s1", "What happened to spend last quarter?")
    payload = model.model_dump()
    assert payload["scenario_id"] == "s1"
    assert payload["expected_refusal"] is True


def test_manifest_serializes() -> None:
    manifest = _panel_manifest(
        fixture_id="saas_tier1_panel",
        business_domain=DomainFixtureBusinessDomain.SAAS_SUBSCRIPTIONS,
        primary_kpis=(DomainFixtureKPIType.ARR.value,),
        spend_channels=("paid_search", "paid_social"),
        control_types=(DomainFixtureControlSignalType.PRODUCT_LAUNCH,),
    )
    payload = manifest.model_dump()
    assert payload["fixture_id"] == "saas_tier1_panel"
    assert payload["tier"] == DomainFixtureTier.TIER_1_TINY_DETERMINISTIC.value
    assert len(payload["column_expectations"]) == 3


def test_build_helper_creates_manifest_with_issue_codes() -> None:
    manifest = build_domain_dataset_fixture_manifest(
        fixture_id="minimal",
        tier=DomainFixtureTier.TIER_1_TINY_DETERMINISTIC,
        business_domain=DomainFixtureBusinessDomain.ECOMMERCE,
        dataset_family=DomainFixtureDatasetFamily.CONTROL_SIGNAL_CATALOG,
        owner=DomainFixtureOwner.MIP,
    )
    assert DomainFixtureIssueCode.FIXTURE_MANIFEST_DEFINED.value in manifest.issues
    assert DomainFixtureIssueCode.NO_DATASET_GENERATION.value in manifest.issues
    assert DomainFixtureIssueCode.NO_MMM_FITTING.value in manifest.issues
    assert ARTIFACT_ID in str(manifest.lineage.get("artifact_id"))


def test_summary_helper_returns_counts_only() -> None:
    manifest = _panel_manifest(
        fixture_id="summary_panel",
        business_domain=DomainFixtureBusinessDomain.ECOMMERCE,
        primary_kpis=(DomainFixtureKPIType.REVENUE.value, DomainFixtureKPIType.ORDERS.value),
        spend_channels=("paid_search", "display"),
        control_types=(
            DomainFixtureControlSignalType.PROMOTION_CALENDAR,
            DomainFixtureControlSignalType.INVENTORY_STOCKOUT,
        ),
    )
    summary = summarize_domain_dataset_fixture_manifest(manifest)
    assert summary == {
        "fixture_id": "summary_panel",
        "tier": DomainFixtureTier.TIER_1_TINY_DETERMINISTIC.value,
        "business_domain": DomainFixtureBusinessDomain.ECOMMERCE.value,
        "dataset_family": DomainFixtureDatasetFamily.MMM_SPEND_KPI_PANEL.value,
        "owner": DomainFixtureOwner.MIP.value,
        "primary_kpi_count": 2,
        "spend_channel_count": 2,
        "control_expectation_count": 2,
        "demo_scenario_count": 1,
        "expected_decision_count": 4,
        "issue_count": len(manifest.issues),
    }
    assert "recommendation" not in summary
    assert "rows" not in summary
    assert "dataframe" not in summary


def test_saas_mmm_panel_example_manifest_builds() -> None:
    manifest = _panel_manifest(
        fixture_id="saas_mmm_panel_v1",
        business_domain=DomainFixtureBusinessDomain.SAAS_SUBSCRIPTIONS,
        primary_kpis=(
            DomainFixtureKPIType.ARR.value,
            DomainFixtureKPIType.TRIALS.value,
        ),
        spend_channels=("paid_search", "paid_social", "content"),
        control_types=(
            DomainFixtureControlSignalType.PRODUCT_LAUNCH,
            DomainFixtureControlSignalType.SEASONALITY,
        ),
    )
    assert manifest.business_domain == "SAAS_SUBSCRIPTIONS"
    assert DomainFixtureKPIType.ARR.value in manifest.primary_kpis


def test_ecommerce_example_manifest_builds() -> None:
    manifest = _panel_manifest(
        fixture_id="ecom_mmm_panel_v1",
        business_domain=DomainFixtureBusinessDomain.ECOMMERCE,
        primary_kpis=(
            DomainFixtureKPIType.REVENUE.value,
            DomainFixtureKPIType.ORDERS.value,
            DomainFixtureKPIType.AOV.value,
        ),
        spend_channels=("paid_search", "paid_social", "affiliates"),
        control_types=(
            DomainFixtureControlSignalType.PROMOTION_CALENDAR,
            DomainFixtureControlSignalType.PRICING_DISCOUNT,
            DomainFixtureControlSignalType.INVENTORY_STOCKOUT,
        ),
    )
    assert manifest.business_domain == "ECOMMERCE"


def test_mobile_app_example_manifest_builds() -> None:
    manifest = _panel_manifest(
        fixture_id="mobile_mmm_panel_v1",
        business_domain=DomainFixtureBusinessDomain.MOBILE_APP,
        primary_kpis=(
            DomainFixtureKPIType.INSTALLS.value,
            DomainFixtureKPIType.D2P.value,
            DomainFixtureKPIType.RETENTION.value,
        ),
        spend_channels=("ua_paid", "ua_social"),
        control_types=(DomainFixtureControlSignalType.APP_RELEASE,),
    )
    assert manifest.business_domain == "MOBILE_APP"


def test_b2b_pipeline_example_manifest_builds() -> None:
    manifest = _panel_manifest(
        fixture_id="b2b_mmm_panel_v1",
        business_domain=DomainFixtureBusinessDomain.B2B_PIPELINE,
        primary_kpis=(
            DomainFixtureKPIType.LEADS.value,
            DomainFixtureKPIType.PIPELINE.value,
            DomainFixtureKPIType.BOOKINGS.value,
        ),
        spend_channels=("paid_search", "events", "content"),
        control_types=(
            DomainFixtureControlSignalType.SALES_CAPACITY,
            DomainFixtureControlSignalType.MACRO_INDEX,
        ),
    )
    assert manifest.business_domain == "B2B_PIPELINE"


def test_geo_local_experiment_example_manifest_builds() -> None:
    manifest = build_domain_dataset_fixture_manifest(
        fixture_id="geo_local_exp_meta_v1",
        tier=DomainFixtureTier.TIER_1_TINY_DETERMINISTIC,
        business_domain=DomainFixtureBusinessDomain.GEO_LOCAL_EXPERIMENTS,
        dataset_family=DomainFixtureDatasetFamily.EXPERIMENT_METADATA,
        owner=DomainFixtureOwner.MIP,
        primary_kpis=(DomainFixtureKPIType.STORE_VISITS.value,),
        experiment_metadata_expectation=DomainFixtureExperimentMetadataExpectation(
            required=True,
            requires_experiment_id=True,
            requires_assignment_metadata=True,
            requires_time_window=True,
            requires_treatment_control_scope=True,
            description="Geo experiment metadata",
        ),
        control_signal_expectations=(
            DomainFixtureControlSignalExpectation(
                signal_type=DomainFixtureControlSignalType.LOCAL_EVENT.value,
                required=True,
                expected_columns=("local_event_flag",),
            ),
        ),
        readiness_expectation=DomainFixtureReadinessExpectation(
            readiness_status=DomainFixtureReadinessStatus.HUMAN_REVIEW_REQUIRED.value,
            required_geo_count_min=8,
            description="Geo scope required",
        ),
        expected_behavior=_blocked_behavior(),
        llm_demo_scenarios=(
            _demo_scenario("geo_q1", "Can you estimate lift for this geo test?"),
        ),
    )
    assert manifest.business_domain == "GEO_LOCAL_EXPERIMENTS"
    assert manifest.experiment_metadata_expectation is not None
    assert manifest.experiment_metadata_expectation.required is True


def test_mip_owned_tier_1_and_tier_2_manifests_allowed() -> None:
    tier1 = build_domain_dataset_fixture_manifest(
        fixture_id="mip_tier1",
        tier=DomainFixtureTier.TIER_1_TINY_DETERMINISTIC,
        business_domain=DomainFixtureBusinessDomain.SAAS_SUBSCRIPTIONS,
        dataset_family=DomainFixtureDatasetFamily.MMM_SPEND_KPI_PANEL,
        owner=DomainFixtureOwner.MIP,
    )
    tier2 = build_domain_dataset_fixture_manifest(
        fixture_id="mip_tier2",
        tier=DomainFixtureTier.TIER_2_REALISTIC_SYNTHETIC_PANEL,
        business_domain=DomainFixtureBusinessDomain.ECOMMERCE,
        dataset_family=DomainFixtureDatasetFamily.MMM_SPEND_KPI_PANEL,
        owner=DomainFixtureOwner.MIP,
    )
    assert tier1.owner == DomainFixtureOwner.MIP.value
    assert tier2.owner == DomainFixtureOwner.MIP.value


def test_package_owned_tier_3_snapshot_manifests_allowed() -> None:
    mmm = build_domain_dataset_fixture_manifest(
        fixture_id="mmm_tier3_snapshot",
        tier=DomainFixtureTier.TIER_3_PACKAGE_EXPORTED_METHOD_SIMULATION_SNAPSHOT,
        business_domain=DomainFixtureBusinessDomain.SAAS_SUBSCRIPTIONS,
        dataset_family=DomainFixtureDatasetFamily.PACKAGE_EXPORTED_SIMULATION_SNAPSHOT,
        owner=DomainFixtureOwner.MMM_PACKAGE,
    )
    geox = build_domain_dataset_fixture_manifest(
        fixture_id="geox_tier3_snapshot",
        tier=DomainFixtureTier.TIER_3_PACKAGE_EXPORTED_METHOD_SIMULATION_SNAPSHOT,
        business_domain=DomainFixtureBusinessDomain.GEO_LOCAL_EXPERIMENTS,
        dataset_family=DomainFixtureDatasetFamily.PACKAGE_EXPORTED_SIMULATION_SNAPSHOT,
        owner=DomainFixtureOwner.GEOX_PACKAGE,
    )
    assert mmm.owner == DomainFixtureOwner.MMM_PACKAGE.value
    assert geox.owner == DomainFixtureOwner.GEOX_PACKAGE.value


def test_expected_blocked_recommendation_behavior_represented() -> None:
    behavior = _blocked_behavior()
    assert DomainFixtureExpectedDecision.BLOCK_RECOMMENDATION.value in (
        behavior.expected_decisions
    )
    assert behavior.forbidden_recommendations


def test_can_say_cannot_say_expectations_represented() -> None:
    behavior = _blocked_behavior()
    assert behavior.can_say_expectations
    assert behavior.cannot_say_expectations


def test_human_review_expectation_represented() -> None:
    behavior = _blocked_behavior()
    assert behavior.human_review_required is True
    assert DomainFixtureExpectedDecision.DEFER_PENDING_HUMAN_REVIEW.value in (
        behavior.expected_decisions
    )


def test_no_dataset_generation_fields_or_functions() -> None:
    source = inspect.getsource(domain_dataset_fixtures)
    # Lines below list forbidden tokens that must not appear in the contract module.
    for token in (
        "def generate_",  # forbidden
        "pd.read",  # forbidden
        "pandas",  # forbidden
        "open(",  # forbidden
        "read_text",  # forbidden
        "json.load",  # forbidden
        "requests",  # forbidden
        "httpx",  # forbidden
    ):
        assert token not in source
    assert "NO_DATASET_GENERATION" in {
        i.value for i in DomainFixtureIssueCode
    }


def test_no_mmm_fitting_or_geox_estimator_logic() -> None:
    source = inspect.getsource(domain_dataset_fixtures)
    # Forbidden fitting/estimator call shapes that must not be implemented here.
    for token in (
        "def fit(",  # forbidden
        ".fit(",  # forbidden
        "predict(",  # forbidden
        "sample(",  # forbidden
        "optimize(",  # forbidden
    ):
        assert token not in source
    assert DomainFixtureIssueCode.NO_MMM_FITTING.value in {
        i.value for i in DomainFixtureIssueCode
    }
    assert DomainFixtureIssueCode.NO_GEOX_ESTIMATOR_LOGIC.value in {
        i.value for i in DomainFixtureIssueCode
    }


def test_no_decision_surface_rec_contract_or_opt_fields() -> None:
    # Boundary: DecisionSurface / RecommendationContract / optimizer fields must not exist.
    fields = set(DomainDatasetFixtureManifest.model_fields)
    for token in (
        "decision_surface",  # forbidden
        "trust_report",  # forbidden
        "recommendation_contract",  # forbidden
        "optimizer",  # forbidden
        "simulator",  # forbidden
        "roi",  # forbidden
        "roas",  # forbidden
        "lift",  # forbidden
        "incrementality",  # forbidden
        "recommended_budget",  # forbidden
    ):
        assert token not in fields
    source = inspect.getsource(domain_dataset_fixtures)
    assert "DecisionSurface(" not in source  # forbidden
    assert "RecommendationContract(" not in source  # forbidden


def test_exported_from_mip_contracts() -> None:
    assert contracts.DomainDatasetFixtureManifest is DomainDatasetFixtureManifest
    assert contracts.DomainFixtureTier is DomainFixtureTier
    assert contracts.build_domain_dataset_fixture_manifest is (
        build_domain_dataset_fixture_manifest
    )
    assert contracts.summarize_domain_dataset_fixture_manifest is (
        summarize_domain_dataset_fixture_manifest
    )
    assert "DomainDatasetFixtureManifest" in contracts.__all__
    assert "build_domain_dataset_fixture_manifest" in contracts.__all__
