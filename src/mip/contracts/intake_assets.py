"""Required data asset and sample schema contracts (P2 / I3)."""

from enum import StrEnum

from pydantic import Field, field_validator, model_validator

from mip.contracts.base import ContractBaseModel
from mip.contracts.intake import DataGrain, GeoGrain, IntakeCandidatePath

_FORBIDDEN_CLAIM_FRAGMENTS = (
    "roi is",
    "lift estimate",
    "lift is",
    "budget allocation",
    "coefficient",
    "causal effect",
    "production-ready",
)


class DataAssetType(StrEnum):
    """Governed intake data asset categories."""

    OUTCOME_KPI_DATA = "outcome_kpi_data"
    MEDIA_SPEND_DATA = "media_spend_data"
    MEDIA_EXPOSURE_DATA = "media_exposure_data"
    CONTROL_DATA = "control_data"
    CALENDAR_SEASONALITY_DATA = "calendar_seasonality_data"
    PRICING_PROMO_DATA = "pricing_promo_data"
    CHANNEL_MAPPING = "channel_mapping"
    GEO_MAPPING = "geo_mapping"
    PRODUCT_MAPPING = "product_mapping"
    METRIC_MAPPING = "metric_mapping"
    CALIBRATION_SIGNAL_DATA = "calibration_signal_data"
    EXPERIMENT_EXPORT_DATA = "experiment_export_data"


class DataAssetRequirementLevel(StrEnum):
    """How strongly an asset is required for a path."""

    REQUIRED = "required"
    RECOMMENDED = "recommended"
    OPTIONAL = "optional"
    CONDITIONAL = "conditional"
    BLOCKED_UNTIL_LATER_PHASE = "blocked_until_later_phase"


class DataAssetPurpose(StrEnum):
    """Why an asset is needed in the intake plan."""

    MODEL_OUTCOME = "model_outcome"
    MEDIA_INPUT = "media_input"
    EXPOSURE_DIAGNOSTIC = "exposure_diagnostic"
    CONFOUNDER_CONTROL = "confounder_control"
    SEMANTIC_MAPPING = "semantic_mapping"
    CALIBRATION_EVIDENCE = "calibration_evidence"
    EXPERIMENT_EVIDENCE = "experiment_evidence"
    GOVERNANCE_CONTEXT = "governance_context"


class SampleColumnRole(StrEnum):
    """Semantic role for sample schema columns."""

    DATE = "date"
    GEO = "geo"
    MARKET = "market"
    COUNTRY = "country"
    PRODUCT = "product"
    METRIC_ID = "metric_id"
    METRIC_VALUE = "metric_value"
    CHANNEL = "channel"
    PLATFORM = "platform"
    CAMPAIGN = "campaign"
    SPEND = "spend"
    IMPRESSIONS = "impressions"
    CLICKS = "clicks"
    CONTROL = "control"
    MAPPING_SOURCE = "mapping_source"
    MAPPING_TARGET = "mapping_target"
    EFFECT_ESTIMATE = "effect_estimate"
    STANDARD_ERROR = "standard_error"
    TIME_WINDOW = "time_window"
    STATUS = "status"


class SampleColumnSpec(ContractBaseModel):
    """Column expectation for a sample schema."""

    name: str
    role: SampleColumnRole
    required: bool = True
    description: str
    example_value: str | int | float | None = None
    allowed_missing: bool = False

    @field_validator("name", "description")
    @classmethod
    def required_strings_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "name and description cannot be empty"
            raise ValueError(msg)
        return value


class SampleRow(ContractBaseModel):
    """Illustrative sample row for schema preview only."""

    values: dict[str, str | int | float | bool]


class SampleSchemaExpectation(ContractBaseModel):
    """Expected shape of a data asset before upload/connect."""

    schema_id: str
    asset_type: DataAssetType
    description: str
    minimum_grain: DataGrain = DataGrain.UNKNOWN
    required_columns: list[SampleColumnSpec]
    optional_columns: list[SampleColumnSpec] = Field(default_factory=list)
    sample_rows: list[SampleRow] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

    @field_validator("schema_id", "description")
    @classmethod
    def schema_strings_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "schema_id and description cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def required_columns_non_empty(self) -> "SampleSchemaExpectation":
        if not self.required_columns:
            msg = "required_columns must be non-empty for sample schema expectations"
            raise ValueError(msg)
        return self


class RequiredDataAsset(ContractBaseModel):
    """Required, recommended, or optional data asset for an intake plan."""

    asset_id: str
    asset_type: DataAssetType
    requirement_level: DataAssetRequirementLevel
    purpose: DataAssetPurpose
    description: str
    required_for_paths: list[IntakeCandidatePath] = Field(default_factory=list)
    minimum_time_grain: DataGrain = DataGrain.UNKNOWN
    minimum_geo_grain: GeoGrain = GeoGrain.UNKNOWN
    sample_schema: SampleSchemaExpectation | None = None
    blocks_if_missing: bool = False
    warnings: list[str] = Field(default_factory=list)

    @field_validator("asset_id", "description")
    @classmethod
    def asset_strings_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "asset_id and description cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def blocks_if_missing_rules(self) -> "RequiredDataAsset":
        if self.blocks_if_missing and self.requirement_level not in {
            DataAssetRequirementLevel.REQUIRED,
            DataAssetRequirementLevel.CONDITIONAL,
        }:
            msg = "blocks_if_missing may be true only for required or conditional assets"
            raise ValueError(msg)
        return self


class IntakePlan(ContractBaseModel):
    """Data asset checklist for a recommended intake path."""

    plan_id: str
    session_id: str
    recommendation_id: str
    recommended_path: IntakeCandidatePath
    required_assets: list[RequiredDataAsset] = Field(default_factory=list)
    recommended_assets: list[RequiredDataAsset] = Field(default_factory=list)
    optional_assets: list[RequiredDataAsset] = Field(default_factory=list)
    blocked_assets: list[RequiredDataAsset] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)
    next_user_actions: list[str] = Field(default_factory=list)

    @field_validator("plan_id", "session_id", "recommendation_id")
    @classmethod
    def plan_ids_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "plan_id, session_id, and recommendation_id cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def intake_plan_rules(self) -> "IntakePlan":
        if self.blocking_reasons and not self.required_assets:
            return self._assert_no_forbidden_claims()
        if self.required_assets:
            return self._assert_no_forbidden_claims()
        if not self.blocking_reasons:
            msg = (
                "intake plan without required_assets must include blocking_reasons "
                "for blocked paths"
            )
            raise ValueError(msg)
        return self._assert_no_forbidden_claims()

    def _assert_no_forbidden_claims(self) -> "IntakePlan":
        text_fields = [
            *self.warnings,
            *self.blocking_reasons,
            *self.next_user_actions,
        ]
        for asset in (
            *self.required_assets,
            *self.recommended_assets,
            *self.optional_assets,
            *self.blocked_assets,
        ):
            text_fields.append(asset.description)
            text_fields.extend(asset.warnings)
        combined = " ".join(text_fields).lower()
        for fragment in _FORBIDDEN_CLAIM_FRAGMENTS:
            if fragment in combined:
                msg = f"intake plan must not contain forbidden claim fragment: {fragment}"
                raise ValueError(msg)
        return self
