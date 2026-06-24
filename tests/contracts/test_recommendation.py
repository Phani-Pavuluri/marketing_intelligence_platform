"""Tests for recommendation contracts."""

from datetime import UTC, datetime
from typing import Any

import pytest
from pydantic import ValidationError

from mip.contracts import (
    ConfidenceTier,
    DiagnosticSummary,
    RecommendationContract,
    RecommendationType,
)


def _recommendation_kwargs(
    passing_diagnostics: DiagnosticSummary,
    **overrides: object,
) -> Any:
    base = {
        "recommendation_id": "rec-001",
        "recommendation_type": RecommendationType.MONITOR,
        "action": {"channel": "search"},
        "diagnostics_summary": passing_diagnostics,
        "confidence_tier": ConfidenceTier.DIRECTIONAL,
        "created_at": datetime(2025, 5, 1, tzinfo=UTC),
    }
    base.update(overrides)
    return base


def test_budget_shift_requires_decision_surface_id(
    passing_diagnostics: DiagnosticSummary,
) -> None:
    with pytest.raises(ValidationError, match="decision_surface_id"):
        RecommendationContract(
            **_recommendation_kwargs(
                passing_diagnostics,
                recommendation_type=RecommendationType.BUDGET_SHIFT,
                action={"shift_usd": 100000},
            )
        )


def test_blocked_recommendation_requires_risk_or_unsupported(
    passing_diagnostics: DiagnosticSummary,
) -> None:
    with pytest.raises(ValidationError, match="risks or unsupported"):
        RecommendationContract(
            **_recommendation_kwargs(
                passing_diagnostics,
                confidence_tier=ConfidenceTier.BLOCKED,
            )
        )


def test_block_action_requires_blocked_tier(
    passing_diagnostics: DiagnosticSummary,
) -> None:
    with pytest.raises(ValidationError, match="blocked confidence tier"):
        RecommendationContract(
            **_recommendation_kwargs(
                passing_diagnostics,
                recommendation_type=RecommendationType.BLOCK_ACTION,
                confidence_tier=ConfidenceTier.DIRECTIONAL,
            )
        )


def test_valid_budget_shift_with_surface(
    passing_diagnostics: DiagnosticSummary,
) -> None:
    rec = RecommendationContract(
        **_recommendation_kwargs(
            passing_diagnostics,
            recommendation_type=RecommendationType.BUDGET_SHIFT,
            action={"shift_usd": 50000},
            decision_surface_ids=["surf-004"],
            evidence_ids=["exp-001"],
            confidence_tier=ConfidenceTier.DECISION_READY,
        )
    )
    assert rec.decision_surface_ids == ["surf-004"]
