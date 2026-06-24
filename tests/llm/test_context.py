"""Tests for LLM explanation context assembly."""

from typing import Any

import pytest
from pydantic import ValidationError

from mip.contracts import ConfidenceTier, DiagnosticSummary, TrustReport
from mip.llm.context import LLMExplanationContext, context_from_trust_report


def _build_trust_report(**overrides: Any) -> TrustReport:
    from datetime import UTC, datetime

    base: dict[str, Any] = {
        "trust_report_id": "tr_llm_001",
        "output_id": "out-llm-001",
        "output_type": "recommendation",
        "confidence_tier": ConfidenceTier.DIRECTIONAL,
        "diagnostics": DiagnosticSummary(passed=True),
        "warnings": [],
        "unsupported_claims": [],
        "trace_uri": "s3://traces/out-llm-001",
        "created_at": datetime(2025, 5, 1, tzinfo=UTC),
    }
    base.update(overrides)
    return TrustReport(**base)


def test_context_from_trust_report_directional() -> None:
    report = _build_trust_report(
        output_id="rec-42",
        output_type="recommendation",
        confidence_tier=ConfidenceTier.DIRECTIONAL,
        warnings=["stale calibration"],
        diagnostics=DiagnosticSummary(
            passed=True,
            warnings=["low sample size"],
            failures=[],
        ),
    )

    context = context_from_trust_report(report)

    assert context.artifact_id == "rec-42"
    assert context.artifact_type == "recommendation"
    assert context.confidence_tier == ConfidenceTier.DIRECTIONAL
    assert context.summary == "Artifact rec-42 is directional for recommendation."
    assert context.warnings == ["stale calibration", "low sample size"]
    assert context.failures == []
    assert context.allowed_actions == ["explain", "summarize", "suggest_review"]
    assert context.blocked_actions == ["production_automation", "bypass_gates"]
    assert context.source_trace_uri == "s3://traces/out-llm-001"


def test_context_from_trust_report_decision_ready() -> None:
    report = _build_trust_report(
        confidence_tier=ConfidenceTier.DECISION_READY,
        diagnostics=DiagnosticSummary(passed=True),
    )
    context = context_from_trust_report(report)
    assert context.allowed_actions == ["explain", "summarize", "recommend_with_evidence"]
    assert context.blocked_actions == ["bypass_gates"]


def test_context_from_trust_report_blocked() -> None:
    report = _build_trust_report(
        confidence_tier=ConfidenceTier.BLOCKED,
        warnings=["gate failure"],
        unsupported_claims=["incremental roi"],
        diagnostics=DiagnosticSummary(
            passed=False,
            failures=["diagnostics_failed"],
            warnings=[],
        ),
    )
    context = context_from_trust_report(report)
    assert context.allowed_actions == ["explain"]
    assert context.failures == ["diagnostics_failed"]
    assert context.unsupported_claims == ["incremental roi"]


def test_llm_context_blocked_requires_detail() -> None:
    with pytest.raises(ValidationError, match="blocked tier requires"):
        LLMExplanationContext(
            artifact_id="out-1",
            artifact_type="recommendation",
            confidence_tier=ConfidenceTier.BLOCKED,
            summary="blocked artifact",
            allowed_actions=["explain"],
            blocked_actions=["recommendation"],
        )


def test_llm_context_empty_summary_rejected() -> None:
    with pytest.raises(ValidationError):
        LLMExplanationContext(
            artifact_id="out-1",
            artifact_type="recommendation",
            confidence_tier=ConfidenceTier.DIRECTIONAL,
            summary="   ",
        )
