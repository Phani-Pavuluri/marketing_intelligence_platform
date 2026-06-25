"""Deterministic LLM provider and explanation governance helpers (P7b)."""

from collections.abc import Sequence
from datetime import UTC, datetime

from mip.contracts.llm_provider import (
    BLOCKED_LLM_OUTPUT_CLAIM_TYPES,
    LLMExplanationBlockingReason,
    LLMExplanationPlan,
    LLMExplanationRequest,
    LLMExplanationStatus,
    LLMGovernedInputReference,
    LLMGovernedInputSourceType,
    LLMInputSensitivity,
    LLMProviderConfig,
    LLMProviderMode,
    LLMProviderStatus,
    LLMUseCase,
    default_forbidden_claim_topics,
)

_SYSTEM_GUARDRAILS = (
    "The LLM explains governed MIP outputs; it does not create measurement authority.",
    "MIP contracts, readiness reports, advisory claim guards, calibration mapping reports, "
    "and TrustReports remain authoritative.",
    "If LLM narrative conflicts with MIP constraints, the deterministic MIP result wins.",
    "Do not invent ROI, incremental impact, spend allocation optimality, automated spend changes, "
    "power/MDE estimates, or matched-market assignments.",
    "Preserve evidence labels, claim labels, warnings, and blocked next steps.",
)

_ALLOWED_OUTPUT_CLAIM_TYPES = (
    "general_marketing_guidance",
    "hypothesis_to_test",
    "data_informed_hypothesis",
    "measured_observation",
    "diagnostic_explanation",
)

_DEFAULT_BLOCKED_NEXT_STEPS = (
    "authorize_decision",
    "approve_budget_change",
    "certify_causal_effect",
    "override_trust_report",
)


def _now() -> datetime:
    return datetime.now(tz=UTC)


def build_default_llm_provider_config() -> LLMProviderConfig:
    """Return disabled deterministic provider mode (default)."""
    return LLMProviderConfig(
        provider_config_id="llm-provider-disabled-default",
        mode=LLMProviderMode.DISABLED,
        status=LLMProviderStatus.DISABLED,
        is_default=True,
        warnings=["Deterministic mode only; no LLM provider configured."],
        created_at=_now(),
    )


def build_local_ollama_provider_config(
    model_name: str = "llama3.1",
) -> LLMProviderConfig:
    """Return local Ollama provider config without making runtime calls."""
    return LLMProviderConfig(
        provider_config_id=f"llm-provider-ollama-{model_name}",
        mode=LLMProviderMode.LOCAL_OLLAMA,
        provider_name="ollama",
        model_name=model_name,
        status=LLMProviderStatus.NOT_CONFIGURED,
        requires_local_runtime=True,
        warnings=[
            "Local Ollama mode requires a local runtime; no provider call is made here.",
        ],
        created_at=_now(),
    )


def build_hosted_open_source_provider_config(model_name: str) -> LLMProviderConfig:
    """Return experimental hosted open-source provider config without inference calls."""
    return LLMProviderConfig(
        provider_config_id=f"llm-provider-hosted-oss-{model_name}",
        mode=LLMProviderMode.HOSTED_OPEN_SOURCE,
        provider_name="hosted_open_source",
        model_name=model_name,
        status=LLMProviderStatus.EXPERIMENTAL,
        is_experimental=True,
        warnings=[
            "Hosted open-source mode is experimental; inference is not invoked in P7b.",
        ],
        created_at=_now(),
    )


def build_bring_your_own_key_provider_config(
    provider_name: str,
    model_name: str | None = None,
) -> LLMProviderConfig:
    """Return BYOK provider config without accepting or storing API keys."""
    return LLMProviderConfig(
        provider_config_id=f"llm-provider-byok-{provider_name}",
        mode=LLMProviderMode.BRING_YOUR_OWN_KEY,
        provider_name=provider_name,
        model_name=model_name,
        status=LLMProviderStatus.NOT_CONFIGURED,
        requires_user_key=True,
        warnings=[
            "Bring-your-own-key mode requires a user-supplied key at runtime; "
            "keys are not stored in contracts.",
        ],
        created_at=_now(),
    )


def build_platform_managed_key_later_config(
    provider_name: str | None = None,
) -> LLMProviderConfig:
    """Return future platform-managed key config gated behind controls."""
    return LLMProviderConfig(
        provider_config_id="llm-provider-platform-managed-later",
        mode=LLMProviderMode.PLATFORM_MANAGED_KEY_LATER,
        provider_name=provider_name,
        status=LLMProviderStatus.FUTURE_ONLY,
        requires_auth=True,
        requires_rate_limits=True,
        requires_cost_controls=True,
        blocking_reasons=[
            LLMExplanationBlockingReason.PLATFORM_MANAGED_KEY_NOT_ALLOWED.value,
        ],
        warnings=[
            "Platform-managed keys are not allowed until auth, rate limits, monitoring, "
            "and cost controls exist.",
        ],
        created_at=_now(),
    )


def build_governed_input_reference(
    source_type: str,
    source_id: str,
    summary: str,
    sensitivity: LLMInputSensitivity = LLMInputSensitivity.GOVERNED_SUMMARY,
) -> LLMGovernedInputReference:
    """Build a governed input reference with default allow/block by sensitivity."""
    return LLMGovernedInputReference(
        input_ref_id=f"llm-input-{source_id}",
        source_type=source_type,
        source_id=source_id,
        sensitivity=sensitivity,
        summary=summary,
    )


def build_llm_explanation_request(
    provider_config: LLMProviderConfig,
    use_case: LLMUseCase,
    input_references: Sequence[LLMGovernedInputReference],
) -> LLMExplanationRequest:
    """Build a governed LLM explanation request with default label preservation."""
    return LLMExplanationRequest(
        request_id=f"llm-req-{provider_config.provider_config_id}",
        provider_config=provider_config,
        use_case=use_case,
        input_references=list(input_references),
        must_preserve_labels=True,
        must_include_warnings=True,
        must_include_blocked_claims=True,
        forbidden_claim_topics=default_forbidden_claim_topics(),
        created_at=_now(),
    )


def _collect_label_requirements(
    input_references: Sequence[LLMGovernedInputReference],
) -> list[str]:
    labels: list[str] = []
    for ref in input_references:
        source_type = str(ref.source_type)
        if source_type in {
            LLMGovernedInputSourceType.CLAIM_LABELS.value,
            LLMGovernedInputSourceType.EVIDENCE_LABELS.value,
        }:
            labels.append(f"{source_type}:{ref.source_id}")
    if not labels:
        labels.append("evidence_labels")
        labels.append("claim_labels")
    return labels


def _collect_warning_requirements(
    input_references: Sequence[LLMGovernedInputReference],
) -> list[str]:
    warnings: list[str] = []
    for ref in input_references:
        warnings.extend(ref.warnings)
        if ref.sensitivity == LLMInputSensitivity.WARNING_PAYLOAD:
            warnings.append(ref.summary)
    if not warnings:
        warnings.append("include_contract_warnings")
    return warnings


def _resolve_plan_status(
    request: LLMExplanationRequest,
    *,
    has_allowed_input: bool,
    has_blocked_input: bool,
) -> tuple[LLMExplanationStatus, list[str]]:
    config = request.provider_config
    blocking: list[str] = list(request.blocking_reasons)

    if config.mode == LLMProviderMode.DISABLED:
        blocking.append(LLMExplanationBlockingReason.PROVIDER_MODE_DISABLED.value)
        return LLMExplanationStatus.DETERMINISTIC_ONLY, blocking

    if config.mode == LLMProviderMode.PLATFORM_MANAGED_KEY_LATER:
        blocking.append(LLMExplanationBlockingReason.PLATFORM_MANAGED_KEY_NOT_ALLOWED.value)
        return LLMExplanationStatus.FUTURE_ONLY, blocking

    if has_blocked_input:
        blocking.extend(
            reason
            for ref in request.input_references
            if not ref.allowed_for_llm
            for reason in ref.blocking_reasons
        )
        return LLMExplanationStatus.BLOCKED, blocking

    if config.status in {
        LLMProviderStatus.NOT_CONFIGURED,
        LLMProviderStatus.BLOCKED,
        LLMProviderStatus.DISABLED,
    }:
        blocking.append(LLMExplanationBlockingReason.PROVIDER_NOT_CONFIGURED.value)
        return LLMExplanationStatus.NEEDS_PROVIDER, blocking

    if not has_allowed_input:
        blocking.append(LLMExplanationBlockingReason.MISSING_GOVERNED_PAYLOAD.value)
        return LLMExplanationStatus.BLOCKED, blocking

    if (
        request.use_case == LLMUseCase.TRUST_REPORT_EXPLANATION
        and not _has_trust_report_input(request.input_references)
    ):
        blocking.append(LLMExplanationBlockingReason.TRUST_REPORT_REQUIRED.value)
        return LLMExplanationStatus.BLOCKED, blocking

    return LLMExplanationStatus.READY, blocking


def _has_trust_report_input(
    input_references: Sequence[LLMGovernedInputReference],
) -> bool:
    return any(
        str(ref.source_type) == LLMGovernedInputSourceType.TRUST_REPORT_SUMMARY.value
        for ref in input_references
    )


def build_llm_explanation_plan(request: LLMExplanationRequest) -> LLMExplanationPlan:
    """Build a deterministic explanation plan without generating answer text."""
    allowed_inputs = [
        ref.input_ref_id for ref in request.input_references if ref.allowed_for_llm
    ]
    blocked_inputs = [
        ref.input_ref_id for ref in request.input_references if not ref.allowed_for_llm
    ]
    has_allowed_input = bool(allowed_inputs)
    has_blocked_input = bool(blocked_inputs)

    status, blocking_reasons = _resolve_plan_status(
        request,
        has_allowed_input=has_allowed_input,
        has_blocked_input=has_blocked_input,
    )

    warnings = list(request.warnings)
    if request.provider_config.is_experimental:
        warnings.append("Provider mode is experimental.")

    return LLMExplanationPlan(
        plan_id=f"llm-plan-{request.request_id}",
        request_id=request.request_id,
        status=status,
        provider_mode=request.provider_config.mode,
        use_case=request.use_case,
        allowed_inputs=allowed_inputs,
        blocked_inputs=blocked_inputs,
        system_guardrails=list(_SYSTEM_GUARDRAILS),
        required_labels=_collect_label_requirements(request.input_references),
        required_warnings=_collect_warning_requirements(request.input_references),
        allowed_output_claim_types=list(_ALLOWED_OUTPUT_CLAIM_TYPES),
        blocked_output_claim_types=list(BLOCKED_LLM_OUTPUT_CLAIM_TYPES),
        allowed_next_steps=["explain_governed_report", "ask_for_missing_data"],
        blocked_next_steps=list(_DEFAULT_BLOCKED_NEXT_STEPS),
        warnings=warnings,
        blocking_reasons=blocking_reasons,
        created_at=_now(),
    )
