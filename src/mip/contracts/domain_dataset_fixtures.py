"""Domain dataset fixture schema/manifest contracts (metadata only).

Defines typed expectations for MIP-owned domain fixtures:
spend/KPI panels, controls, calibration, experiment metadata, readiness,
expected allowed/blocked behaviors, and LLM demo/eval scenarios.

Does not generate datasets, fit MMM models, run GeoX estimators, call LLM
providers, construct DecisionSurface/TrustReport/RecommendationContract, or
compute ROI/ROAS/lift/incrementality.
"""

from __future__ import annotations

from collections.abc import Mapping
from enum import StrEnum
from typing import Any

from pydantic import Field, field_validator

from mip.contracts.base import ContractBaseModel

ARTIFACT_ID = "MIP_DOMAIN_DATASET_SCHEMA_CONTRACT_001"
CONTRACT_MODULE = "mip.contracts.domain_dataset_fixtures"
RECOMMENDED_NEXT_ARTIFACT = "MIP_DOMAIN_DATASET_SCHEMA_CONTRACT_CHECKPOINT_AUDIT_001"
DOMAIN_DATASET_SCHEMA_CONTRACT_ARTIFACT_ID = ARTIFACT_ID
RECOMMENDED_NEXT_DOMAIN_DATASET_SCHEMA_CONTRACT_ARTIFACT = RECOMMENDED_NEXT_ARTIFACT

_DEFAULT_ISSUES: tuple[str, ...] = (
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
)


class DomainFixtureTier(StrEnum):
    """Fixture tier ownership/size class."""

    TIER_1_TINY_DETERMINISTIC = "TIER_1_TINY_DETERMINISTIC"
    TIER_2_REALISTIC_SYNTHETIC_PANEL = "TIER_2_REALISTIC_SYNTHETIC_PANEL"
    TIER_3_PACKAGE_EXPORTED_METHOD_SIMULATION_SNAPSHOT = (
        "TIER_3_PACKAGE_EXPORTED_METHOD_SIMULATION_SNAPSHOT"
    )


class DomainFixtureBusinessDomain(StrEnum):
    """Business domains covered by fixture strategy."""

    SAAS_SUBSCRIPTIONS = "SAAS_SUBSCRIPTIONS"
    ECOMMERCE = "ECOMMERCE"
    MOBILE_APP = "MOBILE_APP"
    B2B_PIPELINE = "B2B_PIPELINE"
    GEO_LOCAL_EXPERIMENTS = "GEO_LOCAL_EXPERIMENTS"


class DomainFixtureDatasetFamily(StrEnum):
    """Dataset family categories."""

    MMM_SPEND_KPI_PANEL = "MMM_SPEND_KPI_PANEL"
    GEOX_CALIBRATION_SIGNAL = "GEOX_CALIBRATION_SIGNAL"
    CONTROL_SIGNAL_CATALOG = "CONTROL_SIGNAL_CATALOG"
    EXPERIMENT_METADATA = "EXPERIMENT_METADATA"
    DATA_SUFFICIENCY_READINESS = "DATA_SUFFICIENCY_READINESS"
    LLM_DEMO_EVAL_SCENARIO = "LLM_DEMO_EVAL_SCENARIO"
    PACKAGE_EXPORTED_SIMULATION_SNAPSHOT = "PACKAGE_EXPORTED_SIMULATION_SNAPSHOT"


class DomainFixtureOwner(StrEnum):
    """Who owns generation/authority for a fixture."""

    MIP = "MIP"
    MMM_PACKAGE = "MMM_PACKAGE"
    GEOX_PACKAGE = "GEOX_PACKAGE"
    EXTERNAL_REFERENCE = "EXTERNAL_REFERENCE"


class DomainFixtureExpectedDecision(StrEnum):
    """Expected MIP decision/behavior for a fixture scenario."""

    ALLOW_DESCRIPTIVE_ANSWER = "ALLOW_DESCRIPTIVE_ANSWER"
    ALLOW_DIAGNOSTIC_ANSWER = "ALLOW_DIAGNOSTIC_ANSWER"
    ALLOW_REFUSAL_ONLY = "ALLOW_REFUSAL_ONLY"
    DEFER_PENDING_DATA = "DEFER_PENDING_DATA"
    DEFER_PENDING_MODEL = "DEFER_PENDING_MODEL"
    DEFER_PENDING_CALIBRATION = "DEFER_PENDING_CALIBRATION"
    DEFER_PENDING_HUMAN_REVIEW = "DEFER_PENDING_HUMAN_REVIEW"
    BLOCK_RECOMMENDATION = "BLOCK_RECOMMENDATION"
    BLOCK_OPTIMIZATION = "BLOCK_OPTIMIZATION"
    BLOCK_ROI_ROAS_LIFT_CLAIM = "BLOCK_ROI_ROAS_LIFT_CLAIM"
    BLOCK_CAUSAL_CLAIM = "BLOCK_CAUSAL_CLAIM"
    BLOCK_UNSUPPORTED_DATA = "BLOCK_UNSUPPORTED_DATA"


class DomainFixtureReadinessStatus(StrEnum):
    """Expected data/model readiness status for a fixture."""

    READY = "READY"
    PARTIALLY_READY = "PARTIALLY_READY"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
    SCHEMA_INCOMPATIBLE = "SCHEMA_INCOMPATIBLE"
    CONTROL_SIGNAL_MISSING = "CONTROL_SIGNAL_MISSING"
    CALIBRATION_INCOMPATIBLE = "CALIBRATION_INCOMPATIBLE"
    MODEL_RUN_REQUIRED = "MODEL_RUN_REQUIRED"
    HUMAN_REVIEW_REQUIRED = "HUMAN_REVIEW_REQUIRED"
    BLOCKED = "BLOCKED"


class DomainFixtureControlSignalType(StrEnum):
    """Control-signal categories for domain fixtures."""

    PROMOTION_CALENDAR = "PROMOTION_CALENDAR"
    PRODUCT_LAUNCH = "PRODUCT_LAUNCH"
    PRICING_DISCOUNT = "PRICING_DISCOUNT"
    MACRO_INDEX = "MACRO_INDEX"
    SALES_CAPACITY = "SALES_CAPACITY"
    INVENTORY_STOCKOUT = "INVENTORY_STOCKOUT"
    APP_RELEASE = "APP_RELEASE"
    HOLIDAY = "HOLIDAY"
    SEASONALITY = "SEASONALITY"
    LOCAL_EVENT = "LOCAL_EVENT"
    COMPETITOR_ACTIVITY = "COMPETITOR_ACTIVITY"


class DomainFixtureKPIType(StrEnum):
    """KPI semantic types for domain fixtures."""

    ARR = "ARR"
    TRIALS = "TRIALS"
    PAID_CONVERSIONS = "PAID_CONVERSIONS"
    CHURN = "CHURN"
    REVENUE = "REVENUE"
    ORDERS = "ORDERS"
    AOV = "AOV"
    NEW_CUSTOMERS = "NEW_CUSTOMERS"
    INSTALLS = "INSTALLS"
    D2P = "D2P"
    SUBSCRIPTIONS = "SUBSCRIPTIONS"
    RETENTION = "RETENTION"
    LEADS = "LEADS"
    MQLS = "MQLS"
    SQLS = "SQLS"
    PIPELINE = "PIPELINE"
    BOOKINGS = "BOOKINGS"
    TRAFFIC = "TRAFFIC"
    STORE_VISITS = "STORE_VISITS"


class DomainFixtureIssueCode(StrEnum):
    """Deterministic schema-contract issue codes."""

    FIXTURE_MANIFEST_DEFINED = "FIXTURE_MANIFEST_DEFINED"
    TIER_DEFINED = "TIER_DEFINED"
    DOMAIN_DEFINED = "DOMAIN_DEFINED"
    DATASET_FAMILY_DEFINED = "DATASET_FAMILY_DEFINED"
    OWNER_BOUNDARY_DEFINED = "OWNER_BOUNDARY_DEFINED"
    SPEND_KPI_SCHEMA_EXPECTATION_DEFINED = "SPEND_KPI_SCHEMA_EXPECTATION_DEFINED"
    CONTROL_SIGNAL_SCHEMA_EXPECTATION_DEFINED = (
        "CONTROL_SIGNAL_SCHEMA_EXPECTATION_DEFINED"
    )
    CALIBRATION_SIGNAL_EXPECTATION_DEFINED = "CALIBRATION_SIGNAL_EXPECTATION_DEFINED"
    EXPERIMENT_METADATA_EXPECTATION_DEFINED = "EXPERIMENT_METADATA_EXPECTATION_DEFINED"
    READINESS_EXPECTATION_DEFINED = "READINESS_EXPECTATION_DEFINED"
    EXPECTED_DECISION_DEFINED = "EXPECTED_DECISION_DEFINED"
    CAN_SAY_CANNOT_SAY_EXPECTATION_DEFINED = "CAN_SAY_CANNOT_SAY_EXPECTATION_DEFINED"
    HUMAN_REVIEW_EXPECTATION_DEFINED = "HUMAN_REVIEW_EXPECTATION_DEFINED"
    FORBIDDEN_RECOMMENDATION_EXPECTATION_DEFINED = (
        "FORBIDDEN_RECOMMENDATION_EXPECTATION_DEFINED"
    )
    LLM_DEMO_EVAL_SCENARIO_DEFINED = "LLM_DEMO_EVAL_SCENARIO_DEFINED"
    NO_DATASET_GENERATION = "NO_DATASET_GENERATION"
    NO_MMM_FITTING = "NO_MMM_FITTING"
    NO_GEOX_ESTIMATOR_LOGIC = "NO_GEOX_ESTIMATOR_LOGIC"
    NO_PRODUCTION_CONNECTOR = "NO_PRODUCTION_CONNECTOR"
    NO_DECISION_SURFACE_GENERATION = "NO_DECISION_SURFACE_GENERATION"
    NO_RECOMMENDATION_CONTRACT_GENERATION = "NO_RECOMMENDATION_CONTRACT_GENERATION"
    NO_OPTIMIZER_SIMULATOR = "NO_OPTIMIZER_SIMULATOR"
    NO_ROI_ROAS_LIFT_INCREMENTALITY_COMPUTATION = (
        "NO_ROI_ROAS_LIFT_INCREMENTALITY_COMPUTATION"
    )
    NO_LLM_PROVIDER_EXECUTION = "NO_LLM_PROVIDER_EXECUTION"


class DomainFixtureColumnExpectation(ContractBaseModel):
    """Expected column shape for a domain fixture panel."""

    column_name: str
    semantic_role: str
    required: bool = True
    expected_dtype: str = "string"
    allowed_values: tuple[str, ...] = ()
    description: str = ""

    @field_validator("column_name", "semantic_role")
    @classmethod
    def required_text_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "column_name and semantic_role cannot be empty"
            raise ValueError(msg)
        return value


class DomainFixtureControlSignalExpectation(ContractBaseModel):
    """Expected control-signal availability for a fixture."""

    signal_type: str
    required: bool = False
    expected_columns: tuple[str, ...] = ()
    description: str = ""

    @field_validator("signal_type")
    @classmethod
    def signal_type_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "signal_type cannot be empty"
            raise ValueError(msg)
        return value


class DomainFixtureCalibrationSignalExpectation(ContractBaseModel):
    """Expected CalibrationSignal-shaped fixture metadata (no runtime mapping)."""

    required: bool = False
    expected_channel: str = ""
    expected_kpi: str = ""
    expected_estimand: str = ""
    requires_uncertainty: bool = True
    requires_time_window: bool = True
    requires_geo_scope: bool = False
    description: str = ""


class DomainFixtureExperimentMetadataExpectation(ContractBaseModel):
    """Expected experiment metadata fields (no estimator execution)."""

    required: bool = False
    requires_experiment_id: bool = True
    requires_assignment_metadata: bool = True
    requires_time_window: bool = True
    requires_treatment_control_scope: bool = True
    description: str = ""


class DomainFixtureReadinessExpectation(ContractBaseModel):
    """Expected readiness/sufficiency outcomes for a fixture."""

    readiness_status: str
    required_rows_min: int = 0
    required_time_periods_min: int = 0
    required_geo_count_min: int = 0
    required_channel_count_min: int = 0
    required_control_signals: tuple[str, ...] = ()
    description: str = ""

    @field_validator("readiness_status")
    @classmethod
    def readiness_status_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "readiness_status cannot be empty"
            raise ValueError(msg)
        return value


class DomainFixtureExpectedBehavior(ContractBaseModel):
    """Expected allowed/blocked planning and LLM response behaviors."""

    expected_decisions: tuple[str, ...] = ()
    can_say_expectations: tuple[str, ...] = ()
    cannot_say_expectations: tuple[str, ...] = ()
    blocked_reason_expectations: tuple[str, ...] = ()
    deferred_reason_expectations: tuple[str, ...] = ()
    human_review_required: bool = False
    forbidden_recommendations: tuple[str, ...] = ()
    description: str = ""


class DomainFixtureLLMDemoScenario(ContractBaseModel):
    """LLM demo/eval scenario expectations (metadata only)."""

    scenario_id: str
    user_question: str
    expected_response_mode: str
    expected_can_say: tuple[str, ...] = ()
    expected_cannot_say: tuple[str, ...] = ()
    expected_refusal: bool = False
    expected_evidence_refs: tuple[str, ...] = ()
    description: str = ""

    @field_validator("scenario_id", "user_question", "expected_response_mode")
    @classmethod
    def required_text_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "scenario_id, user_question, and expected_response_mode cannot be empty"
            raise ValueError(msg)
        return value


class DomainDatasetFixtureManifest(ContractBaseModel):
    """Typed manifest for a MIP domain dataset fixture (no data payload)."""

    fixture_id: str
    version: str = "1"
    tier: str
    business_domain: str
    dataset_family: str
    owner: str
    primary_kpis: tuple[str, ...] = ()
    secondary_kpis: tuple[str, ...] = ()
    spend_channels: tuple[str, ...] = ()
    column_expectations: tuple[DomainFixtureColumnExpectation, ...] = ()
    control_signal_expectations: tuple[DomainFixtureControlSignalExpectation, ...] = ()
    calibration_signal_expectation: DomainFixtureCalibrationSignalExpectation | None = (
        None
    )
    experiment_metadata_expectation: (
        DomainFixtureExperimentMetadataExpectation | None
    ) = None
    readiness_expectation: DomainFixtureReadinessExpectation | None = None
    expected_behavior: DomainFixtureExpectedBehavior | None = None
    llm_demo_scenarios: tuple[DomainFixtureLLMDemoScenario, ...] = ()
    lineage: Mapping[str, Any] = Field(default_factory=dict)
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)
    issues: tuple[str, ...] = ()

    @field_validator(
        "fixture_id",
        "version",
        "tier",
        "business_domain",
        "dataset_family",
        "owner",
    )
    @classmethod
    def required_text_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "required manifest identity fields cannot be empty"
            raise ValueError(msg)
        return value


def build_domain_dataset_fixture_manifest(
    *,
    fixture_id: str,
    tier: DomainFixtureTier | str,
    business_domain: DomainFixtureBusinessDomain | str,
    dataset_family: DomainFixtureDatasetFamily | str,
    owner: DomainFixtureOwner | str,
    version: str = "1",
    primary_kpis: tuple[str, ...] | list[str] = (),
    secondary_kpis: tuple[str, ...] | list[str] = (),
    spend_channels: tuple[str, ...] | list[str] = (),
    column_expectations: (
        tuple[DomainFixtureColumnExpectation, ...]
        | list[DomainFixtureColumnExpectation]
    ) = (),
    control_signal_expectations: (
        tuple[DomainFixtureControlSignalExpectation, ...]
        | list[DomainFixtureControlSignalExpectation]
    ) = (),
    calibration_signal_expectation: DomainFixtureCalibrationSignalExpectation
    | None = None,
    experiment_metadata_expectation: DomainFixtureExperimentMetadataExpectation
    | None = None,
    readiness_expectation: DomainFixtureReadinessExpectation | None = None,
    expected_behavior: DomainFixtureExpectedBehavior | None = None,
    llm_demo_scenarios: (
        tuple[DomainFixtureLLMDemoScenario, ...] | list[DomainFixtureLLMDemoScenario]
    ) = (),
    lineage: Mapping[str, Any] | None = None,
    metadata: dict[str, str | int | float | bool] | None = None,
) -> DomainDatasetFixtureManifest:
    """Build a metadata-only domain fixture manifest with default issue codes."""

    issues = list(_DEFAULT_ISSUES)
    return DomainDatasetFixtureManifest(
        fixture_id=fixture_id,
        version=version,
        tier=_enum_value(tier),
        business_domain=_enum_value(business_domain),
        dataset_family=_enum_value(dataset_family),
        owner=_enum_value(owner),
        primary_kpis=tuple(primary_kpis),
        secondary_kpis=tuple(secondary_kpis),
        spend_channels=tuple(spend_channels),
        column_expectations=tuple(column_expectations),
        control_signal_expectations=tuple(control_signal_expectations),
        calibration_signal_expectation=calibration_signal_expectation,
        experiment_metadata_expectation=experiment_metadata_expectation,
        readiness_expectation=readiness_expectation,
        expected_behavior=expected_behavior,
        llm_demo_scenarios=tuple(llm_demo_scenarios),
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
            "schema_contract_only": True,
        },
        issues=tuple(dict.fromkeys(issues)),
    )


def summarize_domain_dataset_fixture_manifest(
    manifest: DomainDatasetFixtureManifest,
) -> dict[str, object]:
    """Return counts/flags only — no raw panel data or recommendations."""

    expected_decisions: tuple[str, ...] = ()
    if manifest.expected_behavior is not None:
        expected_decisions = manifest.expected_behavior.expected_decisions
    return {
        "fixture_id": manifest.fixture_id,
        "tier": manifest.tier,
        "business_domain": manifest.business_domain,
        "dataset_family": manifest.dataset_family,
        "owner": manifest.owner,
        "primary_kpi_count": len(manifest.primary_kpis),
        "spend_channel_count": len(manifest.spend_channels),
        "control_expectation_count": len(manifest.control_signal_expectations),
        "demo_scenario_count": len(manifest.llm_demo_scenarios),
        "expected_decision_count": len(expected_decisions),
        "issue_count": len(manifest.issues),
    }


def _enum_value(value: object) -> str:
    if isinstance(value, StrEnum):
        return str(value.value)
    return str(value)


__all__ = [
    "ARTIFACT_ID",
    "CONTRACT_MODULE",
    "RECOMMENDED_NEXT_ARTIFACT",
    "DOMAIN_DATASET_SCHEMA_CONTRACT_ARTIFACT_ID",
    "RECOMMENDED_NEXT_DOMAIN_DATASET_SCHEMA_CONTRACT_ARTIFACT",
    "DomainFixtureTier",
    "DomainFixtureBusinessDomain",
    "DomainFixtureDatasetFamily",
    "DomainFixtureOwner",
    "DomainFixtureExpectedDecision",
    "DomainFixtureReadinessStatus",
    "DomainFixtureControlSignalType",
    "DomainFixtureKPIType",
    "DomainFixtureIssueCode",
    "DomainFixtureColumnExpectation",
    "DomainFixtureControlSignalExpectation",
    "DomainFixtureCalibrationSignalExpectation",
    "DomainFixtureExperimentMetadataExpectation",
    "DomainFixtureReadinessExpectation",
    "DomainFixtureExpectedBehavior",
    "DomainFixtureLLMDemoScenario",
    "DomainDatasetFixtureManifest",
    "build_domain_dataset_fixture_manifest",
    "summarize_domain_dataset_fixture_manifest",
]
