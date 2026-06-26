"""API request/response contracts for P10b deterministic workflow routes."""

from __future__ import annotations

from mip.contracts.base import ContractBaseModel

FORBIDDEN_API_OUTPUT_PHRASES = (
    "causal lift",
    "roi proven",
    "power calculated",
    "matched markets selected",
    "treatment assigned",
    "optimized budget",
)


class GovernanceBoundary(ContractBaseModel):
    """Structured governance metadata returned with workflow API responses."""

    mode: str = "deterministic"
    advisory_only: bool = False
    causal_decision_support: bool = False
    roi_claims_allowed: bool = False
    optimized_budget_claims_allowed: bool = False
    measurement_engine_execution: bool = False
    llm_enabled: bool = False
    external_services_enabled: bool = False
    persistence_enabled: bool = False
    production_connector_enabled: bool = False


ADVISORY_GOVERNANCE = GovernanceBoundary(
    advisory_only=True,
    causal_decision_support=False,
    roi_claims_allowed=False,
    optimized_budget_claims_allowed=False,
)

READINESS_GOVERNANCE = GovernanceBoundary(
    causal_decision_support=False,
    roi_claims_allowed=False,
    optimized_budget_claims_allowed=False,
)

CALIBRATION_GOVERNANCE = GovernanceBoundary(
    causal_decision_support=False,
    roi_claims_allowed=False,
    optimized_budget_claims_allowed=False,
)

INTAKE_GOVERNANCE = GovernanceBoundary(
    causal_decision_support=False,
    roi_claims_allowed=False,
    optimized_budget_claims_allowed=False,
)


class ColdStartAdvisoryRequest(ContractBaseModel):
    """Request for deterministic cold-start advisory via demo fixture key."""

    sample_key: str = "dtc_skincare_ecommerce"


class ChannelHypothesisSummary(ContractBaseModel):
    """Summarized channel hypothesis for API output."""

    channel: str
    claim_type: str
    evidence_level: str
    summary: str
    why_to_test: str


class TrackingChecklistSummary(ContractBaseModel):
    """Summarized tracking checklist for API output."""

    required_items: list[str]
    missing_items: list[str]
    recommended_items: list[str]


class LearningAgendaSummary(ContractBaseModel):
    """Summarized learning agenda for API output."""

    agenda_id: str
    learning_questions: list[str]
    success_criteria: list[str]


class ColdStartAdvisoryResponse(ContractBaseModel):
    """Deterministic cold-start advisory API response."""

    status: str
    evidence_mode: str
    claim_types: list[str]
    channel_hypotheses: list[ChannelHypothesisSummary]
    tracking_checklist: TrackingChecklistSummary | None = None
    learning_agenda: LearningAgendaSummary | None = None
    warnings: list[str]
    blocking_reasons: list[str]
    allowed_next_steps: list[str]
    blocked_next_steps: list[str]
    governance: GovernanceBoundary


class ReadinessAssessRequest(ContractBaseModel):
    """Request for deterministic readiness assessment via demo fixture key."""

    sample_key: str = "national_mmm_ready_geox_blocked"


class ReadinessReportSummary(ContractBaseModel):
    """Summarized workflow readiness report for API output."""

    report_type: str
    status: str
    supported_route: str | None = None
    warnings: list[str]
    blocking_reasons: list[str]
    required_next_inputs: list[str]
    allowed_next_steps: list[str]
    blocked_next_steps: list[str]


class ReadinessAssessResponse(ContractBaseModel):
    """Deterministic readiness assessment API response."""

    sample_key: str
    reports: list[ReadinessReportSummary]
    warnings: list[str]
    blocking_reasons: list[str]
    governance: GovernanceBoundary


class CalibrationMapRequest(ContractBaseModel):
    """Request for deterministic calibration mapping via demo fixture key."""

    sample_key: str = "valid_governed_evidence"


class CalibrationMapResponse(ContractBaseModel):
    """Deterministic calibration mapping API response."""

    status: str
    mapped_signal_id: str | None = None
    blocking_reasons: list[str]
    missing_fields: list[str]
    incompatible_fields: list[str]
    warnings: list[str]
    lineage: dict[str, str]
    allowed_next_steps: list[str]
    blocked_next_steps: list[str]
    governance: GovernanceBoundary


class IntakeOverviewRequest(ContractBaseModel):
    """Request for deterministic intake overview via demo example key."""

    example_key: str = "national_mmm_diagnostic"


class IntakeOverviewResponse(ContractBaseModel):
    """Deterministic intake routing overview API response."""

    label: str
    business_question: str
    workflow_kind: str
    recommended_path: str
    status: str
    why_this_path: str
    why_other_paths_blocked: list[str]
    required_next_inputs: list[str]
    warnings: list[str]
    blocking_reasons: list[str]
    allowed_next_steps: list[str]
    blocked_next_steps: list[str]
    governance: GovernanceBoundary
