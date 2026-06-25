"""Tests for LLM explanation governance helpers."""

from mip.contracts.llm_provider import (
    LLMExplanationStatus,
    LLMGovernedInputSourceType,
    LLMInputSensitivity,
    LLMProviderMode,
    LLMProviderStatus,
    LLMUseCase,
    default_forbidden_claim_topics,
)
from mip.workflows.intake.llm_explanation import (
    build_bring_your_own_key_provider_config,
    build_default_llm_provider_config,
    build_governed_input_reference,
    build_hosted_open_source_provider_config,
    build_llm_explanation_plan,
    build_llm_explanation_request,
    build_local_ollama_provider_config,
    build_platform_managed_key_later_config,
)


def test_build_default_provider_config_is_disabled() -> None:
    config = build_default_llm_provider_config()
    assert config.mode == LLMProviderMode.DISABLED
    assert config.status == LLMProviderStatus.DISABLED
    assert config.is_default is True


def test_build_local_ollama_provider_config_requires_local_runtime() -> None:
    config = build_local_ollama_provider_config()
    assert config.mode == LLMProviderMode.LOCAL_OLLAMA
    assert config.requires_local_runtime is True
    assert config.model_name == "llama3.1"


def test_build_hosted_open_source_provider_config_is_experimental() -> None:
    config = build_hosted_open_source_provider_config("mistral-7b")
    assert config.mode == LLMProviderMode.HOSTED_OPEN_SOURCE
    assert config.is_experimental is True
    assert config.status == LLMProviderStatus.EXPERIMENTAL


def test_build_byok_provider_config_requires_user_key_without_storing_key() -> None:
    config = build_bring_your_own_key_provider_config("openai", "gpt-4.1-mini")
    assert config.requires_user_key is True
    assert "api_key" not in config.model_dump()
    assert "secret_key" not in config.model_dump()


def test_build_platform_managed_key_later_config_is_future_only() -> None:
    config = build_platform_managed_key_later_config("openai")
    assert config.mode == LLMProviderMode.PLATFORM_MANAGED_KEY_LATER
    assert config.status == LLMProviderStatus.FUTURE_ONLY
    assert config.requires_auth is True
    assert config.requires_rate_limits is True
    assert config.requires_cost_controls is True


def test_build_governed_input_reference_allows_summary() -> None:
    ref = build_governed_input_reference(
        source_type=LLMGovernedInputSourceType.COLD_START_ADVISORY_PLAN.value,
        source_id="adv-001",
        summary="Cold-start advisory governed summary.",
    )
    assert ref.allowed_for_llm is True


def test_build_llm_explanation_request_defaults() -> None:
    config = build_default_llm_provider_config()
    ref = build_governed_input_reference(
        source_type=LLMGovernedInputSourceType.WORKFLOW_READINESS_REPORT.value,
        source_id="rdy-001",
        summary="Readiness report summary.",
        sensitivity=LLMInputSensitivity.REPORT_PAYLOAD,
    )
    request = build_llm_explanation_request(
        config,
        LLMUseCase.READINESS_EXPLANATION,
        [ref],
    )
    assert request.must_preserve_labels is True
    assert request.must_include_warnings is True
    assert request.must_include_blocked_claims is True
    assert set(default_forbidden_claim_topics()).issubset(set(request.forbidden_claim_topics))


def test_disabled_provider_creates_deterministic_only_plan() -> None:
    config = build_default_llm_provider_config()
    ref = build_governed_input_reference(
        source_type=LLMGovernedInputSourceType.COLD_START_ADVISORY_PLAN.value,
        source_id="adv-001",
        summary="Advisory summary.",
    )
    request = build_llm_explanation_request(
        config,
        LLMUseCase.ADVISORY_PLAN_EXPLANATION,
        [ref],
    )
    plan = build_llm_explanation_plan(request)
    assert plan.status == LLMExplanationStatus.DETERMINISTIC_ONLY
    assert plan.provider_mode == LLMProviderMode.DISABLED
    assert "generated_answer" not in plan.model_dump()
    assert "final_response" not in plan.model_dump()


def test_ready_provider_with_allowed_inputs_creates_ready_plan() -> None:
    config = build_hosted_open_source_provider_config("mistral-7b")
    ref = build_governed_input_reference(
        source_type=LLMGovernedInputSourceType.CALIBRATION_MAPPING_REPORT.value,
        source_id="cal-001",
        summary="Calibration mapping governed summary.",
        sensitivity=LLMInputSensitivity.REPORT_PAYLOAD,
    )
    request = build_llm_explanation_request(
        config,
        LLMUseCase.CALIBRATION_MAPPING_EXPLANATION,
        [ref],
    )
    plan = build_llm_explanation_plan(request)
    assert plan.status == LLMExplanationStatus.READY
    assert ref.input_ref_id in plan.allowed_inputs
    assert plan.blocked_inputs == []


def test_blocked_input_creates_blocked_plan() -> None:
    config = build_local_ollama_provider_config()
    blocked = build_governed_input_reference(
        source_type=LLMGovernedInputSourceType.COMMON_INTAKE_WORKBENCH.value,
        source_id="wb-001",
        summary="Raw row dump",
        sensitivity=LLMInputSensitivity.RAW_ROWS,
    )
    request = build_llm_explanation_request(
        config,
        LLMUseCase.READINESS_EXPLANATION,
        [blocked],
    )
    plan = build_llm_explanation_plan(request)
    assert plan.status == LLMExplanationStatus.BLOCKED
    assert blocked.input_ref_id in plan.blocked_inputs


def test_platform_managed_key_later_creates_future_only_plan() -> None:
    config = build_platform_managed_key_later_config()
    ref = build_governed_input_reference(
        source_type=LLMGovernedInputSourceType.TRUST_REPORT_SUMMARY.value,
        source_id="trust-001",
        summary="Trust report summary.",
        sensitivity=LLMInputSensitivity.GOVERNED_SUMMARY,
    )
    request = build_llm_explanation_request(
        config,
        LLMUseCase.TRUST_REPORT_EXPLANATION,
        [ref],
    )
    plan = build_llm_explanation_plan(request)
    assert plan.status == LLMExplanationStatus.FUTURE_ONLY
    assert "platform_managed_key_not_allowed" in plan.blocking_reasons


def test_plan_includes_forbidden_output_claim_types() -> None:
    config = build_hosted_open_source_provider_config("mistral-7b")
    ref = build_governed_input_reference(
        source_type=LLMGovernedInputSourceType.CLAIM_LABELS.value,
        source_id="labels-001",
        summary="claim labels payload",
        sensitivity=LLMInputSensitivity.CLAIM_LABELS,
    )
    request = build_llm_explanation_request(
        config,
        LLMUseCase.REPORT_SUMMARIZATION,
        [ref],
    )
    plan = build_llm_explanation_plan(request)
    blocked_types = set(plan.blocked_output_claim_types)
    assert "roi_claim" in blocked_types
    assert "lift_claim" in blocked_types
    assert "budget_optimization_claim" in blocked_types
    assert "power_mde_claim" in blocked_types
    assert "matched_markets_claim" in blocked_types
    assert "decision_recommendation" in blocked_types
