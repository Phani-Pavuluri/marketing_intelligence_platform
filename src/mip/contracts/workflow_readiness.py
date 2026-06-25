"""Workflow-specific readiness report contracts (P5 / I7–I8)."""

from datetime import datetime
from enum import StrEnum

from pydantic import Field, field_validator, model_validator

from mip.contracts.base import ContractBaseModel
from mip.contracts.common_intake import ProfileFindingSeverity, WorkflowSupportRoute

_FORBIDDEN_CLAIM_FRAGMENTS = (
    "roi is",
    "lift estimate",
    "lift is",
    "budget allocation",
    "coefficient",
    "causal effect",
    "production-ready",
    "matched market",
    "matched markets",
    "mde is",
    "mde result",
    "power is",
    "power result",
    "powered test",
    "treatment assignment",
    "control assignment",
    "effect estimate is",
    "design is valid",
    "final decision",
    "budget recommendation",
)


class WorkflowReadinessStatus(StrEnum):
    """Structural readiness status for a workflow branch."""

    READY = "ready"
    READY_WITH_WARNINGS = "ready_with_warnings"
    NEEDS_MORE_DATA = "needs_more_data"
    BLOCKED = "blocked"
    NOT_APPLICABLE = "not_applicable"


class WorkflowReadinessReportType(StrEnum):
    """Workflow-specific readiness report category."""

    MMM_DATA_READINESS = "mmm_data_readiness"
    GEOX_DESIGN_READINESS = "geox_design_readiness"
    CALIBRATION_SIGNAL_READINESS = "calibration_signal_readiness"
    DECISION_REVIEW_READINESS = "decision_review_readiness"


class ReadinessBlockingReason(StrEnum):
    """Structured blocking reason for workflow readiness."""

    MISSING_OUTCOME_DATA = "missing_outcome_data"
    MISSING_MEDIA_DATA = "missing_media_data"
    MISSING_GEO_LEVEL_DATA = "missing_geo_level_data"
    MISSING_TIME_COVERAGE = "missing_time_coverage"
    MISSING_METRIC_MAPPING = "missing_metric_mapping"
    MISSING_CALIBRATION_UNCERTAINTY = "missing_calibration_uncertainty"
    MISSING_TRUST_REPORT = "missing_trust_report"
    UNSUPPORTED_ROUTE = "unsupported_route"
    SCOPE_MISMATCH = "scope_mismatch"
    RAW_DATA_NOT_ALLOWED = "raw_data_not_allowed"
    DIAGNOSTIC_NOT_RUN = "diagnostic_not_run"


class ReadinessWarningCode(StrEnum):
    """Structured warning code for workflow readiness."""

    SPARSE_METRIC = "sparse_metric"
    INCOMPLETE_GEO_COVERAGE = "incomplete_geo_coverage"
    INCOMPLETE_MEDIA_COVERAGE = "incomplete_media_coverage"
    SHORT_HISTORY = "short_history"
    PROXY_KPI_USED = "proxy_kpi_used"
    CALIBRATION_OPTIONAL = "calibration_optional"
    DIAGNOSTIC_REQUIRED_NEXT = "diagnostic_required_next"


def _enum_slug(value: object) -> str:
    if isinstance(value, StrEnum):
        return value.value
    return str(value)


def _assert_no_forbidden_claims(*text_fields: str) -> None:
    combined = " ".join(text_fields).lower()
    for fragment in _FORBIDDEN_CLAIM_FRAGMENTS:
        if fragment in combined:
            msg = f"workflow readiness contract must not contain forbidden claim: {fragment}"
            raise ValueError(msg)


class WorkflowReadinessFinding(ContractBaseModel):
    """Single finding on a workflow readiness report."""

    finding_id: str
    severity: ProfileFindingSeverity
    code: str
    message: str
    related_source_ids: list[str] = Field(default_factory=list)
    related_profile_ids: list[str] = Field(default_factory=list)
    related_route: WorkflowSupportRoute | None = None
    warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)

    @field_validator("finding_id", "code", "message")
    @classmethod
    def finding_strings_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "finding_id, code, and message cannot be empty"
            raise ValueError(msg)
        return value


class BaseWorkflowReadinessReport(ContractBaseModel):
    """Shared fields for workflow-specific readiness reports."""

    report_id: str
    session_id: str
    recommendation_id: str
    manifest_id: str
    assessment_id: str
    report_type: WorkflowReadinessReportType
    status: WorkflowReadinessStatus = WorkflowReadinessStatus.NOT_APPLICABLE
    supported_route: WorkflowSupportRoute | None = None
    findings: list[WorkflowReadinessFinding] = Field(default_factory=list)
    required_next_inputs: list[str] = Field(default_factory=list)
    allowed_next_steps: list[str] = Field(default_factory=list)
    blocked_next_steps: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)
    created_at: datetime

    @field_validator(
        "report_id",
        "session_id",
        "recommendation_id",
        "manifest_id",
        "assessment_id",
    )
    @classmethod
    def report_ids_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "report identifiers cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def base_readiness_rules(self) -> "BaseWorkflowReadinessReport":
        if self.status == WorkflowReadinessStatus.BLOCKED and not self.blocking_reasons:
            msg = "blocked readiness report requires blocking_reasons"
            raise ValueError(msg)
        text_fields = [
            *(self.warnings or []),
            *(self.blocking_reasons or []),
            *(self.required_next_inputs or []),
            *(self.allowed_next_steps or []),
        ]
        for finding in self.findings:
            text_fields.append(finding.message)
            text_fields.extend(finding.warnings)
            text_fields.extend(finding.blocking_reasons)
        _assert_no_forbidden_claims(*text_fields)
        return self


class MMMDataReadinessReport(BaseWorkflowReadinessReport):
    """MMM-specific structural data readiness report."""

    report_type: WorkflowReadinessReportType = WorkflowReadinessReportType.MMM_DATA_READINESS
    mmm_route: WorkflowSupportRoute | None = None
    has_outcome_data: bool = False
    has_media_data: bool = False
    has_time_coverage: bool = False
    has_channel_mapping: bool = False
    has_geo_level_data: bool = False
    has_calibration_signal_data: bool = False
    calibration_required: bool = False


class GeoXDesignReadinessReport(BaseWorkflowReadinessReport):
    """GeoX experiment-design structural readiness report."""

    report_type: WorkflowReadinessReportType = WorkflowReadinessReportType.GEOX_DESIGN_READINESS
    has_geo_level_outcome: bool = False
    has_geo_level_media: bool = False
    has_geo_mapping: bool = False
    has_time_coverage: bool = False
    has_objective_kpi_alignment: bool = False
    requires_panel_exp_diagnostics: bool = False
    requires_power_diagnostic: bool = False
    requires_matchability_diagnostic: bool = False
    requires_duration_sensitivity: bool = False


class CalibrationSignalReadinessReport(BaseWorkflowReadinessReport):
    """CalibrationSignal intake structural readiness report."""

    report_type: WorkflowReadinessReportType = (
        WorkflowReadinessReportType.CALIBRATION_SIGNAL_READINESS
    )
    has_effect_estimate: bool = False
    has_uncertainty: bool = False
    has_metric_mapping: bool = False
    has_estimand_mapping: bool = False
    has_scope_mapping: bool = False
    has_time_window: bool = False
    calibration_signal_ready: bool = False


class DecisionReviewReadinessReport(BaseWorkflowReadinessReport):
    """Decision-review packet structural readiness report."""

    report_type: WorkflowReadinessReportType = WorkflowReadinessReportType.DECISION_REVIEW_READINESS
    has_trust_report: bool = False
    has_supported_artifacts: bool = False
    has_metric_estimand_scope: bool = False
    has_freshness_context: bool = False
    requires_human_approval: bool = True
    decision_review_ready: bool = False
