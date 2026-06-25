"""Tests for cold-start advisory planning helpers."""

from datetime import UTC, datetime
from typing import Any

from mip.contracts.advisory import (
    FORBIDDEN_ADVISORY_RESULT_FIELD_NAMES,
    AdvisoryClaimType,
    AdvisoryEvidenceMode,
    ChannelCandidateName,
    ColdStartMediaObjective,
    EvidenceLevel,
)
from mip.workflows.intake.advisory import (
    build_cold_start_advisory_plan,
    build_cold_start_business_profile,
    build_starter_measurement_plan,
    build_tracking_readiness_checklist,
    build_traffic_source_signals,
    infer_advisory_evidence_mode,
    suggest_channel_candidates,
)

_NOW = datetime(2026, 5, 28, 12, 0, tzinfo=UTC)

_FORBIDDEN_FRAGMENTS = (
    "lift estimate",
    "roi is",
    "optimal mix",
    "optimal allocation",
    "causal effect",
    "budget recommendation",
    "expected lift",
    "matched markets",
)


def _profile(**fields: Any) -> Any:
    return build_cold_start_business_profile(
        profile_id="prof-adv-001",
        created_at=_NOW,
        **fields,
    )


def _traffic_profile(**fields: Any) -> Any:
    from mip.contracts.advisory import WebsiteTrafficSourceProfile

    base: dict[str, Any] = {
        "traffic_profile_id": "traffic-001",
        "created_at": _NOW,
    }
    base.update(fields)
    return WebsiteTrafficSourceProfile(**base)


def _assert_no_forbidden_claims(*objects: Any) -> None:
    combined = " ".join(str(obj.model_dump()) for obj in objects).lower()
    for fragment in _FORBIDDEN_FRAGMENTS:
        assert fragment not in combined


def test_sparse_profile_infers_general_knowledge_only() -> None:
    profile = _profile()
    mode = infer_advisory_evidence_mode(profile)
    assert mode == AdvisoryEvidenceMode.GENERAL_KNOWLEDGE_ONLY


def test_business_profile_only_infers_business_profile_only() -> None:
    profile = _profile(
        product_or_service="Handmade skincare",
        target_audience="Women 25-45",
        monthly_budget="$2000",
        primary_objective=ColdStartMediaObjective.SALES,
        business_type="ecommerce retail",
    )
    mode = infer_advisory_evidence_mode(profile)
    assert mode == AdvisoryEvidenceMode.BUSINESS_PROFILE_ONLY


def test_traffic_profile_infers_data_informed_advisory() -> None:
    profile = _profile(
        product_or_service="Handmade skincare",
        target_audience="Women 25-45",
        monthly_budget="$2000",
        primary_objective=ColdStartMediaObjective.SALES,
    )
    traffic = _traffic_profile(source_summary="organic search converts well")
    mode = infer_advisory_evidence_mode(profile, traffic)
    assert mode == AdvisoryEvidenceMode.DATA_INFORMED_ADVISORY


def test_organic_search_conversion_creates_search_signal() -> None:
    traffic = _traffic_profile(
        source_summary="organic search traffic",
        conversion_summary="organic search converts well on product pages",
    )
    signals = build_traffic_source_signals(traffic)
    levels = {signal.evidence_level for signal in signals}
    assert (
        EvidenceLevel.SEARCH_INTENT_SIGNAL in levels
        or EvidenceLevel.ORGANIC_CONVERSION_SIGNAL in levels
    )


def test_social_referral_creates_referral_or_organic_interest_not_paid_test() -> None:
    traffic = _traffic_profile(
        source_summary="instagram referral traffic with engagement",
        channel_group_summary="social referrals",
    )
    signals = build_traffic_source_signals(traffic)
    assert signals
    assert all(signal.evidence_level != EvidenceLevel.PAID_TEST_SIGNAL for signal in signals)
    levels = {signal.evidence_level for signal in signals}
    assert (
        EvidenceLevel.REFERRAL_INTEREST_SIGNAL in levels
        or EvidenceLevel.ORGANIC_INTEREST_SIGNAL in levels
        or EvidenceLevel.ORGANIC_CONVERSION_SIGNAL in levels
    )


def test_ecommerce_visual_product_suggests_meta_tiktok_search() -> None:
    profile = _profile(
        product_or_service="handmade skincare ecommerce",
        target_audience="Women 25-45",
        monthly_budget="$2000",
        primary_objective=ColdStartMediaObjective.SALES,
        business_type="ecommerce",
    )
    candidates = suggest_channel_candidates(profile, AdvisoryEvidenceMode.BUSINESS_PROFILE_ONLY)
    names = {candidate.channel_name for candidate in candidates}
    assert ChannelCandidateName.META_INSTAGRAM in names
    assert ChannelCandidateName.TIKTOK in names
    assert ChannelCandidateName.GOOGLE_SEARCH in names


def test_local_service_suggests_search_and_local_listings() -> None:
    profile = _profile(
        product_or_service="local plumbing service",
        target_audience="Homeowners",
        monthly_budget="$1500",
        primary_objective=ColdStartMediaObjective.LEAD_GENERATION,
        business_type="local service",
    )
    candidates = suggest_channel_candidates(profile, AdvisoryEvidenceMode.BUSINESS_PROFILE_ONLY)
    names = {candidate.channel_name for candidate in candidates}
    assert ChannelCandidateName.GOOGLE_SEARCH in names
    assert ChannelCandidateName.LOCAL_LISTINGS_MAPS in names


def test_b2b_long_cycle_suggests_linkedin_search_content() -> None:
    profile = _profile(
        product_or_service="B2B analytics platform",
        target_audience="Marketing leaders",
        monthly_budget="$10000",
        primary_objective=ColdStartMediaObjective.LEAD_GENERATION,
        b2b_or_b2c="b2b",
        sales_cycle_length="6 months enterprise",
    )
    candidates = suggest_channel_candidates(profile, AdvisoryEvidenceMode.BUSINESS_PROFILE_ONLY)
    names = {candidate.channel_name for candidate in candidates}
    assert ChannelCandidateName.LINKEDIN in names
    assert ChannelCandidateName.GOOGLE_SEARCH in names
    assert ChannelCandidateName.SEO_CONTENT in names


def test_data_informed_plan_uses_data_informed_hypothesis() -> None:
    profile = _profile(
        product_or_service="Handmade skincare",
        target_audience="Women 25-45",
        monthly_budget="$2000",
        primary_objective=ColdStartMediaObjective.SALES,
    )
    traffic = _traffic_profile(
        source_summary="organic search converts well; instagram referral traffic",
        conversion_summary="email traffic converts well",
    )
    plan = build_cold_start_advisory_plan(profile, traffic)
    assert plan.evidence_mode == AdvisoryEvidenceMode.DATA_INFORMED_ADVISORY
    assert AdvisoryClaimType.DATA_INFORMED_HYPOTHESIS in plan.claim_types
    assert all(
        hypothesis.claim_type == AdvisoryClaimType.DATA_INFORMED_HYPOTHESIS
        for hypothesis in plan.channel_hypotheses
    )


def test_business_profile_only_plan_uses_hypothesis_to_test() -> None:
    profile = _profile(
        product_or_service="handmade skincare ecommerce",
        target_audience="Women 25-45",
        monthly_budget="$2000",
        primary_objective=ColdStartMediaObjective.SALES,
    )
    plan = build_cold_start_advisory_plan(profile)
    assert plan.evidence_mode == AdvisoryEvidenceMode.BUSINESS_PROFILE_ONLY
    assert AdvisoryClaimType.HYPOTHESIS_TO_TEST in plan.claim_types


def test_tracking_checklist_requires_items_when_tracking_missing() -> None:
    profile = _profile(
        product_or_service="Skincare",
        target_audience="Women",
        monthly_budget="$2000",
        primary_objective=ColdStartMediaObjective.SALES,
        existing_tracking=False,
    )
    checklist = build_tracking_readiness_checklist(profile)
    assert "UTM parameters on paid and campaign links" in checklist.required_items
    assert "Pixel or tag setup on website/app" in checklist.required_items
    assert "Conversion events defined and firing" in checklist.required_items
    assert checklist.missing_items


def test_starter_measurement_plan_maps_lead_generation_kpis() -> None:
    profile = _profile(
        product_or_service="B2B SaaS",
        target_audience="Ops leaders",
        monthly_budget="$5000",
        primary_objective=ColdStartMediaObjective.LEAD_GENERATION,
    )
    plan = build_starter_measurement_plan(profile, [])
    assert "lead" in plan.primary_kpi.lower()


def test_starter_measurement_plan_maps_awareness_kpis() -> None:
    profile = _profile(
        product_or_service="Consumer app",
        target_audience="Gen Z",
        monthly_budget="$3000",
        primary_objective=ColdStartMediaObjective.AWARENESS,
    )
    plan = build_starter_measurement_plan(profile, [])
    assert "reach" in plan.primary_kpi.lower() or "engaged" in plan.primary_kpi.lower()


def test_cold_start_advisory_plan_blocks_forbidden_claims() -> None:
    profile = _profile(
        product_or_service="handmade skincare ecommerce",
        target_audience="Women 25-45",
        monthly_budget="$2000",
        primary_objective=ColdStartMediaObjective.SALES,
        existing_tracking=True,
    )
    plan = build_cold_start_advisory_plan(profile)
    _assert_no_forbidden_claims(plan)
    assert FORBIDDEN_ADVISORY_RESULT_FIELD_NAMES.isdisjoint(plan.model_dump().keys())
    assert "claim_causal_effect" in plan.blocked_next_steps
    assert "claim_roi_or_lift" in plan.blocked_next_steps


def test_referral_traffic_cannot_authorize_paid_roi_evidence() -> None:
    traffic = _traffic_profile(
        source_summary="instagram referral traffic is strong",
        channel_group_summary="social referral",
    )
    signals = build_traffic_source_signals(traffic)
    assert all(signal.evidence_level != EvidenceLevel.PAID_TEST_SIGNAL for signal in signals)
    for signal in signals:
        if "referral" in signal.source_or_channel or "social" in signal.source_or_channel:
            assert "does not prove" in " ".join(signal.warnings).lower() or signal.warnings


def test_plan_routes_to_future_measurement_paths() -> None:
    profile = _profile(
        product_or_service="handmade skincare ecommerce",
        target_audience="Women 25-45",
        monthly_budget="$2000",
        primary_objective=ColdStartMediaObjective.SALES,
        existing_tracking=True,
    )
    plan = build_cold_start_advisory_plan(profile)
    assert plan.learning_agenda is not None
    future_path = " ".join(plan.learning_agenda.future_measurement_path).lower()
    assert "common intake" in future_path
    assert "mmm" in future_path or "geox" in future_path
    assert "reassess_mmm_geox_readiness_via_p5_reports" in plan.allowed_next_steps
