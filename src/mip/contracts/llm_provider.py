"""Pluggable LLM provider and explanation governance contracts (P7b)."""

from datetime import datetime
from enum import StrEnum

from pydantic import Field, field_validator, model_validator

from mip.contracts.base import ContractBaseModel

EXCLUDED_PROVIDER_MODE_NAMES = frozenset(
    {
        "canned_demo",
        "sample_explanation",
        "template_llm_explanation",
    }
)

FORBIDDEN_LLM_PROVIDER_RESULT_FIELD_NAMES = frozenset(
    {
        "api_key",
        "secret_key",
        "token",
        "provider_secret",
        "generated_answer",
        "final_response",
    }
)

_DEFAULT_FORBIDDEN_CLAIM_TOPICS = (
    "roi",
    "causal_lift",
    "optimal_mix",
    "budget_optimization",
    "power_mde",
    "matched_markets",
    "decision_approval",
)

_FORBIDDEN_CLAIM_FRAGMENTS = (
    "roi is",
    "expected roi",
    "causal lift",
    "lift estimate",
    "optimal mix",
    "optimal allocation",
    "budget recommendation",
    "budget optimization",
    "power result",
    "mde result",
    "matched markets",
    "decision approval",
    "decision recommendation",
    "generated answer",
    "final response",
)


class LLMProviderMode(StrEnum):
    """Supported LLM provider modes for future explanation surfaces."""

    DISABLED = "disabled"
    LOCAL_OLLAMA = "local_ollama"
    HOSTED_OPEN_SOURCE = "hosted_open_source"
    BRING_YOUR_OWN_KEY = "bring_your_own_key"
    PLATFORM_MANAGED_KEY_LATER = "platform_managed_key_later"


class LLMUseCase(StrEnum):
    """Governed LLM explanation/routing use cases."""

    INTAKE_QUESTION_GENERATION = "intake_question_generation"
    MISSING_DATA_QUESTION_GENERATION = "missing_data_question_generation"
    READINESS_EXPLANATION = "readiness_explanation"
    ADVISORY_PLAN_EXPLANATION = "advisory_plan_explanation"
    CALIBRATION_MAPPING_EXPLANATION = "calibration_mapping_explanation"
    BLOCKED_CLAIM_EXPLANATION = "blocked_claim_explanation"
    TRUST_REPORT_EXPLANATION = "trust_report_explanation"
    REPORT_SUMMARIZATION = "report_summarization"
    CHAT_RESPONSE = "chat_response"


class LLMProviderStatus(StrEnum):
    """Configuration availability for a provider mode."""

    AVAILABLE = "available"
    NOT_CONFIGURED = "not_configured"
    DISABLED = "disabled"
    EXPERIMENTAL = "experimental"
    BLOCKED = "blocked"
    FUTURE_ONLY = "future_only"


class LLMInputSensitivity(StrEnum):
    """Sensitivity classification for LLM input references."""

    GOVERNED_SUMMARY = "governed_summary"
    REPORT_PAYLOAD = "report_payload"
    CLAIM_LABELS = "claim_labels"
    WARNING_PAYLOAD = "warning_payload"
    RAW_ROWS = "raw_rows"
    SECRET = "secret"
    PII_HEAVY = "pii_heavy"
    UNVALIDATED_SOURCE = "unvalidated_source"
    UNKNOWN = "unknown"


class LLMExplanationStatus(StrEnum):
    """Status of a planned LLM explanation (not a generated answer)."""

    READY = "ready"
    DETERMINISTIC_ONLY = "deterministic_only"
    NEEDS_PROVIDER = "needs_provider"
    BLOCKED = "blocked"
    FUTURE_ONLY = "future_only"


class LLMExplanationBlockingReason(StrEnum):
    """Structured blocking reason for LLM explanation planning."""

    PROVIDER_NOT_CONFIGURED = "provider_not_configured"
    PROVIDER_MODE_DISABLED = "provider_mode_disabled"
    PLATFORM_MANAGED_KEY_NOT_ALLOWED = "platform_managed_key_not_allowed"
    RAW_ROWS_NOT_ALLOWED = "raw_rows_not_allowed"
    SECRET_NOT_ALLOWED = "secret_not_allowed"
    PII_HEAVY_NOT_ALLOWED = "pii_heavy_not_allowed"
    UNVALIDATED_SOURCE_NOT_ALLOWED = "unvalidated_source_not_allowed"
    MISSING_GOVERNED_PAYLOAD = "missing_governed_payload"
    UNSUPPORTED_USE_CASE = "unsupported_use_case"
    CONFLICTING_CLAIM_LABELS = "conflicting_claim_labels"
    FORBIDDEN_CLAIM_REQUESTED = "forbidden_claim_requested"
    TRUST_REPORT_REQUIRED = "trust_report_required"


class LLMGovernedInputSourceType(StrEnum):
    """Allowed governed source types for LLM explanation inputs."""

    COMMON_INTAKE_WORKBENCH = "common_intake_workbench"
    WORKFLOW_READINESS_REPORT = "workflow_readiness_report"
    COLD_START_ADVISORY_PLAN = "cold_start_advisory_plan"
    CALIBRATION_MAPPING_REPORT = "calibration_mapping_report"
    TRUST_REPORT_SUMMARY = "trust_report_summary"
    ALLOWED_NEXT_STEPS = "allowed_next_steps"
    BLOCKED_NEXT_STEPS = "blocked_next_steps"
    CLAIM_LABELS = "claim_labels"
    EVIDENCE_LABELS = "evidence_labels"


_ALLOWED_INPUT_SENSITIVITIES = frozenset(
    {
        LLMInputSensitivity.GOVERNED_SUMMARY,
        LLMInputSensitivity.REPORT_PAYLOAD,
        LLMInputSensitivity.CLAIM_LABELS,
        LLMInputSensitivity.WARNING_PAYLOAD,
    }
)

_BLOCKED_INPUT_SENSITIVITIES = frozenset(
    {
        LLMInputSensitivity.RAW_ROWS,
        LLMInputSensitivity.SECRET,
        LLMInputSensitivity.PII_HEAVY,
        LLMInputSensitivity.UNVALIDATED_SOURCE,
        LLMInputSensitivity.UNKNOWN,
    }
)

_BLOCKED_OUTPUT_CLAIM_TYPES = (
    "causal_claim",
    "decision_recommendation",
    "roi_claim",
    "lift_claim",
    "budget_optimization_claim",
    "power_mde_claim",
    "matched_markets_claim",
)

BLOCKED_LLM_OUTPUT_CLAIM_TYPES = _BLOCKED_OUTPUT_CLAIM_TYPES


def _assert_no_forbidden_claims(*text_fields: str) -> None:
    combined = " ".join(text_fields).lower()
    for fragment in _FORBIDDEN_CLAIM_FRAGMENTS:
        if fragment in combined:
            msg = f"LLM provider contract must not contain forbidden claim: {fragment}"
            raise ValueError(msg)


def _collect_text(*groups: list[str] | None) -> list[str]:
    collected: list[str] = []
    for group in groups:
        if group:
            collected.extend(group)
    return collected


def default_forbidden_claim_topics() -> list[str]:
    """Return default forbidden claim topics for LLM explanation requests."""
    return list(_DEFAULT_FORBIDDEN_CLAIM_TOPICS)


class LLMProviderConfig(ContractBaseModel):
    """Provider mode configuration without secrets or live provider calls."""

    provider_config_id: str
    mode: LLMProviderMode = LLMProviderMode.DISABLED
    provider_name: str | None = None
    model_name: str | None = None
    status: LLMProviderStatus = LLMProviderStatus.DISABLED
    is_default: bool = False
    is_experimental: bool = False
    requires_user_key: bool = False
    requires_local_runtime: bool = False
    requires_auth: bool = False
    requires_rate_limits: bool = False
    requires_cost_controls: bool = False
    warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)
    created_at: datetime

    @field_validator("provider_config_id")
    @classmethod
    def provider_config_id_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "provider_config_id cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def provider_config_rules(self) -> "LLMProviderConfig":
        mode_value = str(self.mode)
        if mode_value in EXCLUDED_PROVIDER_MODE_NAMES:
            msg = f"excluded provider mode not supported: {mode_value}"
            raise ValueError(msg)

        if self.mode == LLMProviderMode.DISABLED:
            if self.status not in {LLMProviderStatus.DISABLED, LLMProviderStatus.NOT_CONFIGURED}:
                msg = "disabled mode requires disabled or not_configured status"
                raise ValueError(msg)
            if self.provider_name or self.model_name:
                msg = "disabled mode must not set provider_name or model_name"
                raise ValueError(msg)

        if self.mode == LLMProviderMode.LOCAL_OLLAMA and not self.requires_local_runtime:
            msg = "local_ollama mode requires requires_local_runtime=true"
            raise ValueError(msg)

        if self.mode == LLMProviderMode.HOSTED_OPEN_SOURCE and not self.is_experimental:
            msg = "hosted_open_source mode must be experimental by default"
            raise ValueError(msg)

        if self.mode == LLMProviderMode.BRING_YOUR_OWN_KEY and not self.requires_user_key:
            msg = "bring_your_own_key mode requires requires_user_key=true"
            raise ValueError(msg)

        if self.mode == LLMProviderMode.PLATFORM_MANAGED_KEY_LATER:
            if self.status not in {LLMProviderStatus.FUTURE_ONLY, LLMProviderStatus.BLOCKED}:
                msg = "platform_managed_key_later requires future_only or blocked status"
                raise ValueError(msg)
            if not (
                self.requires_auth and self.requires_rate_limits and self.requires_cost_controls
            ):
                msg = (
                    "platform_managed_key_later requires auth, rate limits, and cost controls"
                )
                raise ValueError(msg)

        _assert_no_forbidden_claims(
            *_collect_text(
                self.warnings,
                self.blocking_reasons,
                [self.provider_name or "", self.model_name or ""],
            )
        )
        return self


class LLMGovernedInputReference(ContractBaseModel):
    """Governed summary reference that may be passed to future LLM explanation."""

    input_ref_id: str
    source_type: LLMGovernedInputSourceType | str
    source_id: str
    sensitivity: LLMInputSensitivity = LLMInputSensitivity.GOVERNED_SUMMARY
    summary: str
    allowed_for_llm: bool = True
    warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)

    @field_validator("input_ref_id", "source_id", "summary")
    @classmethod
    def required_strings_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "input reference identifiers and summary cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="before")
    @classmethod
    def govern_input_data(cls, data: object) -> object:
        if not isinstance(data, dict):
            return data
        payload = dict(data)
        sensitivity = LLMInputSensitivity(
            str(payload.get("sensitivity", LLMInputSensitivity.GOVERNED_SUMMARY))
        )
        if sensitivity in _BLOCKED_INPUT_SENSITIVITIES:
            payload["allowed_for_llm"] = False
            if not payload.get("blocking_reasons"):
                reason = _blocking_reason_for_sensitivity(sensitivity)
                payload["blocking_reasons"] = [reason.value]
        elif sensitivity in _ALLOWED_INPUT_SENSITIVITIES:
            payload["allowed_for_llm"] = True
        else:
            payload["allowed_for_llm"] = False
            if not payload.get("blocking_reasons"):
                payload["blocking_reasons"] = [
                    LLMExplanationBlockingReason.MISSING_GOVERNED_PAYLOAD.value,
                ]
        return payload

    @model_validator(mode="after")
    def governed_input_rules(self) -> "LLMGovernedInputReference":
        _assert_no_forbidden_claims(
            self.summary,
            *_collect_text(self.warnings, self.blocking_reasons),
        )
        return self


def _blocking_reason_for_sensitivity(
    sensitivity: LLMInputSensitivity,
) -> LLMExplanationBlockingReason:
    mapping = {
        LLMInputSensitivity.RAW_ROWS: LLMExplanationBlockingReason.RAW_ROWS_NOT_ALLOWED,
        LLMInputSensitivity.SECRET: LLMExplanationBlockingReason.SECRET_NOT_ALLOWED,
        LLMInputSensitivity.PII_HEAVY: LLMExplanationBlockingReason.PII_HEAVY_NOT_ALLOWED,
        LLMInputSensitivity.UNVALIDATED_SOURCE: (
            LLMExplanationBlockingReason.UNVALIDATED_SOURCE_NOT_ALLOWED
        ),
        LLMInputSensitivity.UNKNOWN: LLMExplanationBlockingReason.MISSING_GOVERNED_PAYLOAD,
    }
    return mapping.get(
        sensitivity,
        LLMExplanationBlockingReason.MISSING_GOVERNED_PAYLOAD,
    )


class LLMExplanationRequest(ContractBaseModel):
    """Request to plan a governed LLM explanation (not a generated answer)."""

    request_id: str
    provider_config: LLMProviderConfig
    use_case: LLMUseCase
    input_references: list[LLMGovernedInputReference] = Field(default_factory=list)
    requested_output_style: str = "governed_explanation"
    must_preserve_labels: bool = True
    must_include_warnings: bool = True
    must_include_blocked_claims: bool = True
    forbidden_claim_topics: list[str] = Field(
        default_factory=default_forbidden_claim_topics,
    )
    warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)
    created_at: datetime

    @field_validator("request_id")
    @classmethod
    def request_id_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "request_id cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def explanation_request_rules(self) -> "LLMExplanationRequest":
        if not self.must_preserve_labels:
            msg = "must_preserve_labels must remain true for governed explanations"
            raise ValueError(msg)
        if not self.must_include_warnings:
            msg = "must_include_warnings must remain true for governed explanations"
            raise ValueError(msg)
        if not self.must_include_blocked_claims:
            msg = "must_include_blocked_claims must remain true for governed explanations"
            raise ValueError(msg)

        _assert_no_forbidden_claims(
            self.requested_output_style,
            *_collect_text(self.forbidden_claim_topics, self.warnings, self.blocking_reasons),
        )
        return self


class LLMExplanationPlan(ContractBaseModel):
    """Deterministic plan for future LLM explanation; not an LLM response."""

    plan_id: str
    request_id: str
    status: LLMExplanationStatus
    provider_mode: LLMProviderMode
    use_case: LLMUseCase
    allowed_inputs: list[str] = Field(default_factory=list)
    blocked_inputs: list[str] = Field(default_factory=list)
    system_guardrails: list[str] = Field(default_factory=list)
    required_labels: list[str] = Field(default_factory=list)
    required_warnings: list[str] = Field(default_factory=list)
    allowed_output_claim_types: list[str] = Field(default_factory=list)
    blocked_output_claim_types: list[str] = Field(default_factory=list)
    allowed_next_steps: list[str] = Field(default_factory=list)
    blocked_next_steps: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)
    created_at: datetime

    @field_validator("plan_id", "request_id")
    @classmethod
    def plan_ids_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "plan identifiers cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def explanation_plan_rules(self) -> "LLMExplanationPlan":
        _assert_no_forbidden_claims(
            *_collect_text(
                self.system_guardrails,
                self.required_labels,
                self.required_warnings,
                self.warnings,
                self.blocking_reasons,
                self.allowed_next_steps,
                self.blocked_next_steps,
            )
        )
        return self
