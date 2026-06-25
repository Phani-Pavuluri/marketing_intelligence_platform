"""General advisory and cold-start planning contracts (P5b / I8b)."""

from datetime import datetime
from enum import StrEnum

from pydantic import Field, field_validator, model_validator

from mip.contracts.base import ContractBaseModel

_P5B_ALLOWED_CLAIM_TYPES = frozenset(
    {
        "general_marketing_guidance",
        "hypothesis_to_test",
        "data_informed_hypothesis",
    }
)

_P5B_ALLOWED_EVIDENCE_LEVELS = frozenset(
    {
        "no_customer_data",
        "business_profile_signal",
        "organic_interest_signal",
        "organic_conversion_signal",
        "search_intent_signal",
        "referral_interest_signal",
        "crm_signal",
        "sales_signal",
        "paid_test_signal",
    }
)

_FORBIDDEN_CLAIM_FRAGMENTS = (
    "roi is",
    "roi estimate",
    "expected roi",
    "lift estimate",
    "expected lift",
    "optimal mix",
    "optimal allocation",
    "optimized budget",
    "budget recommendation",
    "causal effect",
    "incremental sales",
    "mde result",
    "power result",
    "matched markets",
    "highest roi",
    "guaranteed cac",
    "permanent budget",
)

_FORBIDDEN_RESULT_FIELD_NAMES = frozenset(
    {
        "lift_estimate",
        "roi_estimate",
        "expected_lift",
        "expected_roi",
        "optimal_mix",
        "optimized_budget",
        "budget_recommendation",
        "causal_effect",
        "incremental_sales",
        "mde_result",
        "power_result",
        "matched_markets",
    }
)


class AdvisoryEvidenceMode(StrEnum):
    """How advisory guidance is grounded."""

    GENERAL_KNOWLEDGE_ONLY = "general_knowledge_only"
    BUSINESS_PROFILE_ONLY = "business_profile_only"
    DATA_INFORMED_ADVISORY = "data_informed_advisory"
    MEASURED_DIAGNOSTIC = "measured_diagnostic"
    CAUSAL_DECISION_SUPPORT = "causal_decision_support"


class AdvisoryClaimType(StrEnum):
    """Claim type label for advisory outputs."""

    GENERAL_MARKETING_GUIDANCE = "general_marketing_guidance"
    HYPOTHESIS_TO_TEST = "hypothesis_to_test"
    DATA_INFORMED_HYPOTHESIS = "data_informed_hypothesis"
    MEASURED_OBSERVATION = "measured_observation"
    DIAGNOSTIC_EXPLANATION = "diagnostic_explanation"
    CAUSAL_CLAIM = "causal_claim"
    DECISION_RECOMMENDATION = "decision_recommendation"


class EvidenceLevel(StrEnum):
    """Evidence level backing an advisory statement."""

    NO_CUSTOMER_DATA = "no_customer_data"
    BUSINESS_PROFILE_SIGNAL = "business_profile_signal"
    ORGANIC_INTEREST_SIGNAL = "organic_interest_signal"
    ORGANIC_CONVERSION_SIGNAL = "organic_conversion_signal"
    SEARCH_INTENT_SIGNAL = "search_intent_signal"
    REFERRAL_INTEREST_SIGNAL = "referral_interest_signal"
    CRM_SIGNAL = "crm_signal"
    SALES_SIGNAL = "sales_signal"
    PAID_TEST_SIGNAL = "paid_test_signal"
    EXPERIMENT_SIGNAL = "experiment_signal"
    MMM_SIGNAL = "mmm_signal"
    TRUST_REPORT_AUTHORIZED = "trust_report_authorized"


class ColdStartAdvisoryStatus(StrEnum):
    """Cold-start advisory workflow status."""

    NEEDS_BUSINESS_DETAILS = "needs_business_details"
    NEEDS_TRACKING_SETUP = "needs_tracking_setup"
    ADVISORY_PLAN_READY = "advisory_plan_ready"
    READY_FOR_BASIC_TRACKING = "ready_for_basic_tracking"
    READY_FOR_STARTER_TEST = "ready_for_starter_test"
    NOT_READY_FOR_MMM = "not_ready_for_mmm"
    NOT_READY_FOR_GEOX = "not_ready_for_geox"
    READY_FOR_DATA_COLLECTION = "ready_for_data_collection"
    READY_FOR_REASSESSMENT = "ready_for_reassessment"
    BLOCKED = "blocked"


class ColdStartMediaObjective(StrEnum):
    """Primary media objective for cold-start planning."""

    AWARENESS = "awareness"
    TRAFFIC = "traffic"
    LEAD_GENERATION = "lead_generation"
    SALES = "sales"
    APP_INSTALLS = "app_installs"
    STORE_VISITS = "store_visits"
    RETENTION = "retention"
    REPEAT_PURCHASE = "repeat_purchase"
    MARKET_LAUNCH = "market_launch"
    PRODUCT_LAUNCH = "product_launch"
    UNKNOWN = "unknown"


class ChannelCategory(StrEnum):
    """Channel category for suitability assessment."""

    SEARCH = "search"
    PAID_SOCIAL = "paid_social"
    ORGANIC_SOCIAL = "organic_social"
    VIDEO = "video"
    DISPLAY = "display"
    EMAIL_CRM = "email_crm"
    SEO_CONTENT = "seo_content"
    CREATOR_INFLUENCER = "creator_influencer"
    AFFILIATE_PARTNERSHIP = "affiliate_partnership"
    RETARGETING = "retargeting"
    LOCAL_LISTINGS_MAPS = "local_listings_maps"
    MARKETPLACE = "marketplace"
    UNKNOWN = "unknown"


class ChannelCandidateName(StrEnum):
    """Named channel candidate for cold-start hypotheses."""

    GOOGLE_SEARCH = "google_search"
    GOOGLE_PERFORMANCE_MAX = "google_performance_max"
    META_INSTAGRAM = "meta_instagram"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    REDDIT = "reddit"
    DISPLAY = "display"
    CTV = "ctv"
    EMAIL_CRM = "email_crm"
    SEO_CONTENT = "seo_content"
    CREATORS_INFLUENCERS = "creators_influencers"
    AFFILIATE_PARTNERSHIPS = "affiliate_partnerships"
    RETARGETING = "retargeting"
    LOCAL_LISTINGS_MAPS = "local_listings_maps"
    MARKETPLACES = "marketplaces"


def _enum_slug(value: object) -> str:
    if isinstance(value, StrEnum):
        return value.value
    return str(value)


def _assert_no_forbidden_claims(*text_fields: str) -> None:
    combined = " ".join(text_fields).lower()
    for fragment in _FORBIDDEN_CLAIM_FRAGMENTS:
        if fragment in combined:
            msg = f"advisory contract must not contain forbidden claim: {fragment}"
            raise ValueError(msg)


def _assert_p5b_claim_type(claim_type: AdvisoryClaimType | str) -> None:
    slug = _enum_slug(claim_type)
    if slug not in _P5B_ALLOWED_CLAIM_TYPES:
        msg = f"P5b advisory contracts may not emit claim type: {slug}"
        raise ValueError(msg)


def _assert_p5b_evidence_level(level: EvidenceLevel | str) -> None:
    slug = _enum_slug(level)
    if slug not in _P5B_ALLOWED_EVIDENCE_LEVELS:
        msg = f"P5b advisory contracts may not emit evidence level: {slug}"
        raise ValueError(msg)


def _collect_text_fields(*field_groups: list[str] | None) -> list[str]:
    collected: list[str] = []
    for group in field_groups:
        if group:
            collected.extend(group)
    return collected


class ColdStartBusinessProfile(ContractBaseModel):
    """Structured business profile for cold-start advisory planning."""

    profile_id: str
    business_type: str | None = None
    product_or_service: str | None = None
    b2b_or_b2c: str | None = None
    average_order_value: str | None = None
    gross_margin: str | None = None
    sales_cycle_length: str | None = None
    geography: str | None = None
    target_audience: str | None = None
    monthly_budget: str | None = None
    primary_objective: ColdStartMediaObjective = ColdStartMediaObjective.UNKNOWN
    secondary_objectives: list[ColdStartMediaObjective] = Field(default_factory=list)
    existing_website: bool | None = None
    existing_tracking: bool | None = None
    creative_assets_available: bool | None = None
    customer_list_available: bool | None = None
    organic_channels_available: list[str] = Field(default_factory=list)
    seasonality_context: str | None = None
    constraints: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)
    created_at: datetime

    @field_validator("profile_id")
    @classmethod
    def profile_id_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "profile_id cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def advisory_profile_rules(self) -> "ColdStartBusinessProfile":
        text_fields = _collect_text_fields(
            self.warnings,
            self.blocking_reasons,
            self.constraints,
            self.organic_channels_available,
            [
                self.business_type or "",
                self.product_or_service or "",
                self.seasonality_context or "",
            ],
        )
        _assert_no_forbidden_claims(*text_fields)
        return self


class WebsiteTrafficSourceProfile(ContractBaseModel):
    """Governed website traffic/source summary for data-informed advisory."""

    traffic_profile_id: str
    source_summary: str | None = None
    channel_group_summary: str | None = None
    landing_page_summary: str | None = None
    geo_summary: str | None = None
    device_summary: str | None = None
    new_vs_returning_summary: str | None = None
    conversion_summary: str | None = None
    utm_coverage_summary: str | None = None
    warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)
    created_at: datetime

    @field_validator("traffic_profile_id")
    @classmethod
    def traffic_profile_id_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "traffic_profile_id cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def traffic_profile_rules(self) -> "WebsiteTrafficSourceProfile":
        text_fields = _collect_text_fields(
            self.warnings,
            self.blocking_reasons,
            [
                self.source_summary or "",
                self.channel_group_summary or "",
                self.conversion_summary or "",
            ],
        )
        _assert_no_forbidden_claims(*text_fields)
        return self


class TrafficSourceSignal(ContractBaseModel):
    """Single traffic-source signal for channel hypothesis support."""

    signal_id: str
    source_or_channel: str
    evidence_level: EvidenceLevel
    signal_summary: str
    engagement_signal: str | None = None
    conversion_signal: str | None = None
    tracking_quality: str | None = None
    warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)

    @field_validator("signal_id", "source_or_channel", "signal_summary")
    @classmethod
    def signal_strings_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "signal identifiers and summary cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def traffic_signal_rules(self) -> "TrafficSourceSignal":
        _assert_p5b_evidence_level(self.evidence_level)
        text_fields = _collect_text_fields(
            self.warnings,
            self.blocking_reasons,
            [
                self.signal_summary,
                self.engagement_signal or "",
                self.conversion_signal or "",
                self.tracking_quality or "",
            ],
        )
        _assert_no_forbidden_claims(*text_fields)
        return self


class ChannelCandidate(ContractBaseModel):
    """Advisory channel candidate for cold-start testing."""

    candidate_id: str
    channel_name: ChannelCandidateName
    channel_category: ChannelCategory
    supported_objectives: list[ColdStartMediaObjective] = Field(default_factory=list)
    why_relevant: str
    required_tracking: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)

    @field_validator("candidate_id", "why_relevant")
    @classmethod
    def candidate_strings_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "candidate_id and why_relevant cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def channel_candidate_rules(self) -> "ChannelCandidate":
        _assert_no_forbidden_claims(
            self.why_relevant,
            *_collect_text_fields(self.warnings, self.blocking_reasons, self.required_tracking),
        )
        return self


class ChannelSuitabilityAssessment(ContractBaseModel):
    """Assessment of channel suitability for a cold-start profile."""

    assessment_id: str
    business_profile_id: str
    traffic_profile_id: str | None = None
    channel_candidates: list[ChannelCandidate] = Field(default_factory=list)
    evidence_mode: AdvisoryEvidenceMode
    evidence_levels: list[EvidenceLevel] = Field(default_factory=list)
    claim_types: list[AdvisoryClaimType] = Field(default_factory=list)
    clarification_questions: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)
    created_at: datetime

    @field_validator("assessment_id", "business_profile_id")
    @classmethod
    def assessment_ids_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "assessment identifiers cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def suitability_assessment_rules(self) -> "ChannelSuitabilityAssessment":
        for claim_type in self.claim_types:
            _assert_p5b_claim_type(claim_type)
        for level in self.evidence_levels:
            _assert_p5b_evidence_level(level)
        text_fields = _collect_text_fields(
            self.warnings,
            self.blocking_reasons,
            self.clarification_questions,
        )
        for candidate in self.channel_candidates:
            text_fields.append(candidate.why_relevant)
        _assert_no_forbidden_claims(*text_fields)
        return self


class ColdStartChannelHypothesis(ContractBaseModel):
    """Advisory channel hypothesis to test."""

    hypothesis_id: str
    channel_candidate: ChannelCandidateName
    objective: ColdStartMediaObjective
    evidence_level: EvidenceLevel
    claim_type: AdvisoryClaimType
    hypothesis_text: str
    why_to_test: str
    what_would_increase_confidence: list[str] = Field(default_factory=list)
    required_tracking: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)

    @field_validator("hypothesis_id", "hypothesis_text", "why_to_test")
    @classmethod
    def hypothesis_strings_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "hypothesis identifiers and text cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def channel_hypothesis_rules(self) -> "ColdStartChannelHypothesis":
        _assert_p5b_claim_type(self.claim_type)
        _assert_p5b_evidence_level(self.evidence_level)
        text_fields = _collect_text_fields(
            self.warnings,
            self.blocking_reasons,
            self.required_tracking,
            self.what_would_increase_confidence,
            self.risks,
            [self.hypothesis_text, self.why_to_test],
        )
        _assert_no_forbidden_claims(*text_fields)
        return self


class StarterMediaMixHypothesis(ContractBaseModel):
    """Advisory starter media mix hypothesis — not an optimal allocation."""

    mix_id: str
    business_profile_id: str
    evidence_mode: AdvisoryEvidenceMode
    hypotheses: list[ColdStartChannelHypothesis] = Field(default_factory=list)
    suggested_test_budget_notes: str
    allocation_guidance: str
    claim_type: AdvisoryClaimType
    evidence_levels: list[EvidenceLevel] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)
    created_at: datetime

    @field_validator("mix_id", "business_profile_id")
    @classmethod
    def mix_ids_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "mix identifiers cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def starter_mix_rules(self) -> "StarterMediaMixHypothesis":
        _assert_p5b_claim_type(self.claim_type)
        for level in self.evidence_levels:
            _assert_p5b_evidence_level(level)
        text_fields = _collect_text_fields(
            self.warnings,
            self.blocking_reasons,
            [self.suggested_test_budget_notes, self.allocation_guidance],
        )
        _assert_no_forbidden_claims(*text_fields)
        return self


class TrackingReadinessChecklist(ContractBaseModel):
    """Tracking setup checklist for cold-start users."""

    checklist_id: str
    required_items: list[str] = Field(default_factory=list)
    recommended_items: list[str] = Field(default_factory=list)
    missing_items: list[str] = Field(default_factory=list)
    status: ColdStartAdvisoryStatus = ColdStartAdvisoryStatus.NEEDS_TRACKING_SETUP
    warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)

    @field_validator("checklist_id")
    @classmethod
    def checklist_id_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "checklist_id cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def tracking_checklist_rules(self) -> "TrackingReadinessChecklist":
        _assert_no_forbidden_claims(
            *_collect_text_fields(
                self.required_items,
                self.recommended_items,
                self.missing_items,
                self.warnings,
                self.blocking_reasons,
            ),
        )
        return self


class StarterMeasurementPlan(ContractBaseModel):
    """Starter measurement plan with qualitative timebox guidance."""

    plan_id: str
    primary_kpi: str
    secondary_kpis: list[str] = Field(default_factory=list)
    guardrail_metrics: list[str] = Field(default_factory=list)
    reporting_cadence: str
    test_timebox_guidance: str
    data_to_collect: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)

    @field_validator("plan_id", "primary_kpi", "reporting_cadence", "test_timebox_guidance")
    @classmethod
    def measurement_plan_strings_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "measurement plan identifiers and KPI fields cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def measurement_plan_rules(self) -> "StarterMeasurementPlan":
        _assert_no_forbidden_claims(
            *_collect_text_fields(
                self.secondary_kpis,
                self.guardrail_metrics,
                self.data_to_collect,
                self.warnings,
                self.blocking_reasons,
                [self.primary_kpi, self.reporting_cadence, self.test_timebox_guidance],
            ),
        )
        return self


class LearningAgenda(ContractBaseModel):
    """Learning agenda and reassessment plan for cold-start users."""

    agenda_id: str
    learning_questions: list[str] = Field(default_factory=list)
    success_criteria: list[str] = Field(default_factory=list)
    stop_scale_or_iterate_criteria: list[str] = Field(default_factory=list)
    reassessment_triggers: list[str] = Field(default_factory=list)
    future_measurement_path: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)

    @field_validator("agenda_id")
    @classmethod
    def agenda_id_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "agenda_id cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def learning_agenda_rules(self) -> "LearningAgenda":
        _assert_no_forbidden_claims(
            *_collect_text_fields(
                self.learning_questions,
                self.success_criteria,
                self.stop_scale_or_iterate_criteria,
                self.reassessment_triggers,
                self.future_measurement_path,
                self.warnings,
                self.blocking_reasons,
            ),
        )
        return self


class ColdStartAdvisoryPlan(ContractBaseModel):
    """Advisory-only cold-start plan with evidence and claim labeling."""

    plan_id: str
    business_profile: ColdStartBusinessProfile
    traffic_profile: WebsiteTrafficSourceProfile | None = None
    channel_suitability: ChannelSuitabilityAssessment | None = None
    channel_hypotheses: list[ColdStartChannelHypothesis] = Field(default_factory=list)
    starter_media_mix: StarterMediaMixHypothesis | None = None
    tracking_checklist: TrackingReadinessChecklist | None = None
    measurement_plan: StarterMeasurementPlan | None = None
    learning_agenda: LearningAgenda | None = None
    status: ColdStartAdvisoryStatus = ColdStartAdvisoryStatus.NEEDS_BUSINESS_DETAILS
    evidence_mode: AdvisoryEvidenceMode = AdvisoryEvidenceMode.GENERAL_KNOWLEDGE_ONLY
    claim_types: list[AdvisoryClaimType] = Field(default_factory=list)
    allowed_next_steps: list[str] = Field(default_factory=list)
    blocked_next_steps: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)
    created_at: datetime

    @field_validator("plan_id")
    @classmethod
    def plan_id_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "plan_id cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def advisory_plan_rules(self) -> "ColdStartAdvisoryPlan":
        for claim_type in self.claim_types:
            _assert_p5b_claim_type(claim_type)
        text_fields = _collect_text_fields(
            self.warnings,
            self.blocking_reasons,
            self.allowed_next_steps,
            self.blocked_next_steps,
        )
        _assert_no_forbidden_claims(*text_fields)
        return self


FORBIDDEN_ADVISORY_RESULT_FIELD_NAMES = _FORBIDDEN_RESULT_FIELD_NAMES
