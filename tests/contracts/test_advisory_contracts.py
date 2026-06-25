"""Tests for advisory and cold-start planning contracts."""

from datetime import UTC, datetime
from typing import Any

import pytest
from pydantic import ValidationError

from mip.contracts.advisory import (
    FORBIDDEN_ADVISORY_RESULT_FIELD_NAMES,
    AdvisoryClaimType,
    AdvisoryEvidenceMode,
    ChannelCandidateName,
    ColdStartAdvisoryPlan,
    ColdStartAdvisoryStatus,
    ColdStartBusinessProfile,
    ColdStartChannelHypothesis,
    ColdStartMediaObjective,
    EvidenceLevel,
    StarterMediaMixHypothesis,
)

_NOW = datetime(2026, 5, 28, 12, 0, tzinfo=UTC)


def _profile(**overrides: Any) -> ColdStartBusinessProfile:
    base: dict[str, Any] = {
        "profile_id": "prof-001",
        "created_at": _NOW,
    }
    base.update(overrides)
    return ColdStartBusinessProfile(**base)


def test_cold_start_business_profile_constructs() -> None:
    profile = _profile(
        product_or_service="Handmade skincare",
        target_audience="Women 25-45",
        monthly_budget="$2000",
        primary_objective=ColdStartMediaObjective.SALES,
    )
    assert profile.profile_id == "prof-001"


def test_advisory_contract_rejects_forbidden_claims() -> None:
    with pytest.raises(ValidationError, match="forbidden claim"):
        ColdStartChannelHypothesis(
            hypothesis_id="hyp-001",
            channel_candidate=ChannelCandidateName.META_INSTAGRAM,
            objective=ColdStartMediaObjective.SALES,
            evidence_level=EvidenceLevel.BUSINESS_PROFILE_SIGNAL,
            claim_type=AdvisoryClaimType.HYPOTHESIS_TO_TEST,
            hypothesis_text="The optimal mix is Meta only.",
            why_to_test="Visual product",
        )


def test_p5b_rejects_causal_claim_type_on_hypothesis() -> None:
    with pytest.raises(ValidationError, match="may not emit claim type"):
        ColdStartChannelHypothesis(
            hypothesis_id="hyp-002",
            channel_candidate=ChannelCandidateName.GOOGLE_SEARCH,
            objective=ColdStartMediaObjective.SALES,
            evidence_level=EvidenceLevel.BUSINESS_PROFILE_SIGNAL,
            claim_type=AdvisoryClaimType.CAUSAL_CLAIM,
            hypothesis_text="Search may be a reasonable starter test.",
            why_to_test="Intent",
        )


def test_starter_media_mix_rejects_optimal_allocation_wording() -> None:
    with pytest.raises(ValidationError, match="forbidden claim"):
        StarterMediaMixHypothesis(
            mix_id="mix-001",
            business_profile_id="prof-001",
            evidence_mode=AdvisoryEvidenceMode.BUSINESS_PROFILE_ONLY,
            suggested_test_budget_notes="Small initial test budget.",
            allocation_guidance="This is the optimal allocation for all spend.",
            claim_type=AdvisoryClaimType.HYPOTHESIS_TO_TEST,
            created_at=_NOW,
        )


def test_forbidden_result_field_names_documented() -> None:
    assert "lift_estimate" in FORBIDDEN_ADVISORY_RESULT_FIELD_NAMES
    assert "roi_estimate" in FORBIDDEN_ADVISORY_RESULT_FIELD_NAMES
    assert "optimal_mix" in FORBIDDEN_ADVISORY_RESULT_FIELD_NAMES


def test_advisory_plan_has_no_forbidden_result_fields() -> None:
    profile = _profile(product_or_service="Skincare")
    plan = ColdStartAdvisoryPlan(
        plan_id="adv-001",
        business_profile=profile,
        status=ColdStartAdvisoryStatus.NEEDS_BUSINESS_DETAILS,
        evidence_mode=AdvisoryEvidenceMode.GENERAL_KNOWLEDGE_ONLY,
        claim_types=[AdvisoryClaimType.GENERAL_MARKETING_GUIDANCE],
        created_at=_NOW,
    )
    assert FORBIDDEN_ADVISORY_RESULT_FIELD_NAMES.isdisjoint(plan.model_dump().keys())
