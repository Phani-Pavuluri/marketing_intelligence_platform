"""Tests for LLM provider and explanation governance contracts."""

from datetime import UTC, datetime
from typing import Any

import pytest
from pydantic import ValidationError

from mip.contracts.llm_provider import (
    EXCLUDED_PROVIDER_MODE_NAMES,
    FORBIDDEN_LLM_PROVIDER_RESULT_FIELD_NAMES,
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

_NOW = datetime(2026, 5, 28, 12, 0, tzinfo=UTC)

_ALL_CONTRACT_MODELS = (
    LLMProviderConfig,
    LLMGovernedInputReference,
    LLMExplanationRequest,
    LLMExplanationPlan,
)

_FORBIDDEN_FIELD_FRAGMENTS = (
    "api_key",
    "secret_key",
    "token",
    "provider_secret",
    "generated_answer",
    "final_response",
)


def _provider_config(**overrides: Any) -> LLMProviderConfig:
    base: dict[str, Any] = {
        "provider_config_id": "cfg-test-001",
        "mode": LLMProviderMode.DISABLED,
        "status": LLMProviderStatus.DISABLED,
        "created_at": _NOW,
    }
    base.update(overrides)
    return LLMProviderConfig(**base)


def _input_ref(**overrides: Any) -> LLMGovernedInputReference:
    base: dict[str, Any] = {
        "input_ref_id": "input-001",
        "source_type": LLMGovernedInputSourceType.COLD_START_ADVISORY_PLAN,
        "source_id": "adv-001",
        "summary": "Advisory plan summary with hypothesis labels only.",
        "sensitivity": LLMInputSensitivity.GOVERNED_SUMMARY,
    }
    base.update(overrides)
    return LLMGovernedInputReference(**base)


def test_default_provider_config_is_disabled() -> None:
    config = _provider_config()
    assert config.mode == LLMProviderMode.DISABLED
    assert config.status == LLMProviderStatus.DISABLED
    assert config.provider_name is None
    assert config.model_name is None


def test_local_ollama_config_requires_local_runtime() -> None:
    config = _provider_config(
        mode=LLMProviderMode.LOCAL_OLLAMA,
        provider_name="ollama",
        model_name="llama3.1",
        status=LLMProviderStatus.NOT_CONFIGURED,
        requires_local_runtime=True,
    )
    assert config.requires_local_runtime is True
    assert config.mode == LLMProviderMode.LOCAL_OLLAMA


def test_local_ollama_rejects_missing_local_runtime_flag() -> None:
    with pytest.raises(ValidationError, match="requires_local_runtime"):
        _provider_config(
            mode=LLMProviderMode.LOCAL_OLLAMA,
            provider_name="ollama",
            model_name="llama3.1",
            status=LLMProviderStatus.NOT_CONFIGURED,
        )


def test_hosted_open_source_config_is_experimental() -> None:
    config = _provider_config(
        mode=LLMProviderMode.HOSTED_OPEN_SOURCE,
        provider_name="hosted_open_source",
        model_name="mistral-7b",
        status=LLMProviderStatus.EXPERIMENTAL,
        is_experimental=True,
    )
    assert config.is_experimental is True
    assert config.status == LLMProviderStatus.EXPERIMENTAL


def test_hosted_open_source_rejects_non_experimental() -> None:
    with pytest.raises(ValidationError, match="experimental"):
        _provider_config(
            mode=LLMProviderMode.HOSTED_OPEN_SOURCE,
            provider_name="hosted_open_source",
            model_name="mistral-7b",
            status=LLMProviderStatus.AVAILABLE,
            is_experimental=False,
        )


def test_byok_config_requires_user_key() -> None:
    config = _provider_config(
        mode=LLMProviderMode.BRING_YOUR_OWN_KEY,
        provider_name="openai",
        model_name="gpt-4.1-mini",
        status=LLMProviderStatus.NOT_CONFIGURED,
        requires_user_key=True,
    )
    assert config.requires_user_key is True


def test_platform_managed_key_config_is_future_only_and_gated() -> None:
    config = _provider_config(
        mode=LLMProviderMode.PLATFORM_MANAGED_KEY_LATER,
        status=LLMProviderStatus.FUTURE_ONLY,
        requires_auth=True,
        requires_rate_limits=True,
        requires_cost_controls=True,
    )
    assert config.status in {LLMProviderStatus.FUTURE_ONLY, LLMProviderStatus.BLOCKED}
    assert config.requires_auth is True
    assert config.requires_rate_limits is True
    assert config.requires_cost_controls is True


def test_governed_summary_input_allowed() -> None:
    ref = _input_ref(sensitivity=LLMInputSensitivity.GOVERNED_SUMMARY)
    assert ref.allowed_for_llm is True


def test_report_payload_input_allowed() -> None:
    ref = _input_ref(
        source_type=LLMGovernedInputSourceType.WORKFLOW_READINESS_REPORT,
        sensitivity=LLMInputSensitivity.REPORT_PAYLOAD,
        summary="Readiness report structural summary only.",
    )
    assert ref.allowed_for_llm is True


def test_claim_and_warning_payload_inputs_allowed() -> None:
    claim_ref = _input_ref(
        source_type=LLMGovernedInputSourceType.CLAIM_LABELS,
        sensitivity=LLMInputSensitivity.CLAIM_LABELS,
        summary="claim_type=hypothesis_to_test",
    )
    warning_ref = _input_ref(
        source_type=LLMGovernedInputSourceType.COLD_START_ADVISORY_PLAN,
        sensitivity=LLMInputSensitivity.WARNING_PAYLOAD,
        summary="Advisory-only warning payload.",
    )
    assert claim_ref.allowed_for_llm is True
    assert warning_ref.allowed_for_llm is True


def test_raw_rows_blocked_by_default() -> None:
    ref = _input_ref(sensitivity=LLMInputSensitivity.RAW_ROWS, summary="row-level export")
    assert ref.allowed_for_llm is False
    assert "raw_rows_not_allowed" in ref.blocking_reasons


def test_secrets_blocked_by_default() -> None:
    ref = _input_ref(sensitivity=LLMInputSensitivity.SECRET, summary="credential export")
    assert ref.allowed_for_llm is False
    assert "secret_not_allowed" in ref.blocking_reasons


def test_pii_heavy_blocked_by_default() -> None:
    ref = _input_ref(sensitivity=LLMInputSensitivity.PII_HEAVY, summary="customer export")
    assert ref.allowed_for_llm is False
    assert "pii_heavy_not_allowed" in ref.blocking_reasons


def test_unvalidated_source_blocked_by_default() -> None:
    ref = _input_ref(
        sensitivity=LLMInputSensitivity.UNVALIDATED_SOURCE,
        summary="unvalidated upload",
    )
    assert ref.allowed_for_llm is False
    assert "unvalidated_source_not_allowed" in ref.blocking_reasons


def test_explanation_request_preserves_labels_warnings_blocked_claims() -> None:
    config = _provider_config()
    request = LLMExplanationRequest(
        request_id="req-001",
        provider_config=config,
        use_case=LLMUseCase.ADVISORY_PLAN_EXPLANATION,
        input_references=[_input_ref()],
        created_at=_NOW,
    )
    assert request.must_preserve_labels is True
    assert request.must_include_warnings is True
    assert request.must_include_blocked_claims is True
    topics = default_forbidden_claim_topics()
    assert "roi" in topics
    assert "causal_lift" in topics
    assert "optimal_mix" in topics


def test_forbidden_claim_topics_include_required_guardrails() -> None:
    topics = set(default_forbidden_claim_topics())
    assert {
        "roi",
        "causal_lift",
        "optimal_mix",
        "budget_optimization",
        "power_mde",
        "matched_markets",
        "decision_approval",
    }.issubset(topics)


def test_no_contract_exposes_api_key_fields() -> None:
    for model in _ALL_CONTRACT_MODELS:
        for field_name in model.model_fields:
            for fragment in _FORBIDDEN_FIELD_FRAGMENTS:
                assert fragment not in field_name


def test_forbidden_result_field_names_documented() -> None:
    assert "api_key" in FORBIDDEN_LLM_PROVIDER_RESULT_FIELD_NAMES
    assert "generated_answer" in FORBIDDEN_LLM_PROVIDER_RESULT_FIELD_NAMES
    assert "final_response" in FORBIDDEN_LLM_PROVIDER_RESULT_FIELD_NAMES


def test_excluded_provider_modes_documented() -> None:
    assert "canned_demo" in EXCLUDED_PROVIDER_MODE_NAMES
    assert "sample_explanation" in EXCLUDED_PROVIDER_MODE_NAMES
    assert "template_llm_explanation" in EXCLUDED_PROVIDER_MODE_NAMES


def test_llm_provider_mode_enum_excludes_canned_modes() -> None:
    mode_values = {mode.value for mode in LLMProviderMode}
    assert EXCLUDED_PROVIDER_MODE_NAMES.isdisjoint(mode_values)


def test_explanation_plan_rejects_forbidden_claim_text() -> None:
    with pytest.raises(ValidationError, match="forbidden claim"):
        LLMExplanationPlan(
            plan_id="plan-001",
            request_id="req-001",
            status=LLMExplanationStatus.READY,
            provider_mode=LLMProviderMode.DISABLED,
            use_case=LLMUseCase.CHAT_RESPONSE,
            system_guardrails=["This budget recommendation is final."],
            created_at=_NOW,
        )
