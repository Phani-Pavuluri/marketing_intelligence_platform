"""Column mapping and semantic confirmation contracts (P4 / I6)."""

from datetime import datetime
from enum import StrEnum

from pydantic import Field, field_validator, model_validator

from mip.contracts.base import ContractBaseModel
from mip.contracts.intake_assets import DataAssetType, SampleColumnRole

_FORBIDDEN_CLAIM_FRAGMENTS = (
    "roi is",
    "lift estimate",
    "lift is",
    "budget allocation",
    "coefficient",
    "causal effect",
    "production-ready",
    "data is compatible",
    "model-ready",
    "readiness report",
)


class ColumnMappingStatus(StrEnum):
    """Lifecycle status for a column mapping proposal."""

    PROPOSED = "proposed"
    CONFIRMED = "confirmed"
    NEEDS_USER_CONFIRMATION = "needs_user_confirmation"
    AMBIGUOUS = "ambiguous"
    REJECTED = "rejected"
    BLOCKED = "blocked"


class ColumnMappingConfidence(StrEnum):
    """Confidence in a proposed column mapping."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class SemanticMappingDimension(StrEnum):
    """Canonical semantic dimension for intake column mapping."""

    DATE = "date"
    METRIC = "metric"
    METRIC_ID = "metric_id"
    METRIC_VALUE = "metric_value"
    GEO = "geo"
    MARKET = "market"
    COUNTRY = "country"
    PRODUCT = "product"
    CHANNEL = "channel"
    PLATFORM = "platform"
    CAMPAIGN = "campaign"
    SPEND = "spend"
    IMPRESSIONS = "impressions"
    CLICKS = "clicks"
    CONTROL = "control"
    CURRENCY = "currency"
    TIMEZONE = "timezone"
    WEEK_DEFINITION = "week_definition"
    SOURCE_TO_CANONICAL_MAPPING = "source_to_canonical_mapping"
    EFFECT_ESTIMATE = "effect_estimate"
    STANDARD_ERROR = "standard_error"
    TIME_WINDOW = "time_window"
    STATUS = "status"


class CanonicalMappingStatus(StrEnum):
    """Resolution status for a canonical mapping candidate."""

    NOT_REQUIRED = "not_required"
    UNRESOLVED = "unresolved"
    CANDIDATE_SELECTED = "candidate_selected"
    CONFIRMED = "confirmed"
    BLOCKED = "blocked"


class CanonicalMappingCandidate(ContractBaseModel):
    """Candidate canonical resolution for a source value (registry stubs deferred)."""

    candidate_id: str
    dimension: SemanticMappingDimension
    source_value: str
    canonical_id: str = ""
    canonical_label: str | None = None
    confidence: ColumnMappingConfidence = ColumnMappingConfidence.UNKNOWN
    why_candidate: str | None = None
    warnings: list[str] = Field(default_factory=list)

    @field_validator("candidate_id", "source_value")
    @classmethod
    def candidate_strings_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "candidate_id and source_value cannot be empty"
            raise ValueError(msg)
        return value


class ColumnMappingProposal(ContractBaseModel):
    """Proposed mapping from a source column to a semantic dimension."""

    proposal_id: str
    source_id: str
    asset_type: DataAssetType
    source_column: str
    semantic_dimension: SemanticMappingDimension
    sample_column_role: SampleColumnRole | None = None
    confidence: ColumnMappingConfidence = ColumnMappingConfidence.UNKNOWN
    status: ColumnMappingStatus = ColumnMappingStatus.PROPOSED
    why_proposed: str | None = None
    canonical_candidates: list[CanonicalMappingCandidate] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)

    @field_validator("proposal_id", "source_id", "source_column")
    @classmethod
    def proposal_strings_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "proposal_id, source_id, and source_column cannot be empty"
            raise ValueError(msg)
        return value


class ColumnMappingConfirmation(ContractBaseModel):
    """User confirmation or rejection of a column mapping proposal."""

    confirmation_id: str
    proposal_id: str
    source_id: str
    asset_type: DataAssetType
    source_column: str
    semantic_dimension: SemanticMappingDimension
    confirmed: bool
    confirmed_by: str | None = None
    confirmed_at: datetime | None = None
    selected_canonical_id: str | None = None
    notes: str | None = None
    warnings: list[str] = Field(default_factory=list)

    @field_validator("confirmation_id", "proposal_id", "source_id", "source_column")
    @classmethod
    def confirmation_strings_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "confirmation_id, proposal_id, source_id, and source_column cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def rejected_requires_explanation(self) -> "ColumnMappingConfirmation":
        if not self.confirmed and not (self.notes or self.warnings):
            msg = "rejected confirmation requires notes or warnings explaining why"
            raise ValueError(msg)
        return self


class SemanticMappingReport(ContractBaseModel):
    """Aggregated mapping proposals and confirmations for an intake manifest."""

    report_id: str
    manifest_id: str
    session_id: str
    recommendation_id: str
    plan_id: str
    mapping_status: ColumnMappingStatus
    proposals: list[ColumnMappingProposal] = Field(default_factory=list)
    confirmations: list[ColumnMappingConfirmation] = Field(default_factory=list)
    unconfirmed_required_mappings: list[str] = Field(default_factory=list)
    ambiguous_mappings: list[ColumnMappingProposal] = Field(default_factory=list)
    blocked_mappings: list[ColumnMappingProposal] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)
    created_at: datetime

    @field_validator(
        "report_id",
        "manifest_id",
        "session_id",
        "recommendation_id",
        "plan_id",
    )
    @classmethod
    def report_ids_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "report and manifest identifiers cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def report_rules(self) -> "SemanticMappingReport":
        return self._assert_no_forbidden_claims()

    def _assert_no_forbidden_claims(self) -> "SemanticMappingReport":
        text_fields = [
            *self.warnings,
            *self.blocking_reasons,
            *self.unconfirmed_required_mappings,
        ]
        for proposal in (
            *self.proposals,
            *self.ambiguous_mappings,
            *self.blocked_mappings,
        ):
            if proposal.why_proposed:
                text_fields.append(proposal.why_proposed)
            text_fields.extend(proposal.warnings)
            text_fields.extend(proposal.blocking_reasons)
        for confirmation in self.confirmations:
            if confirmation.notes:
                text_fields.append(confirmation.notes)
            text_fields.extend(confirmation.warnings)
        combined = " ".join(text_fields).lower()
        for fragment in _FORBIDDEN_CLAIM_FRAGMENTS:
            if fragment in combined:
                msg = (
                    "semantic mapping report must not contain "
                    f"forbidden claim fragment: {fragment}"
                )
                raise ValueError(msg)
        return self
