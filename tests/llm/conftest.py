"""Builders for LLM safety and context tests."""

from datetime import UTC, datetime
from typing import Any

import pytest

from mip.contracts import ConfidenceTier, DiagnosticSummary, TrustReport


@pytest.fixture
def passing_diagnostics() -> DiagnosticSummary:
    return DiagnosticSummary(passed=True)


def build_trust_report(**overrides: Any) -> TrustReport:
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
