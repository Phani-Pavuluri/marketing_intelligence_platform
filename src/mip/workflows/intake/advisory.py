"""Deterministic cold-start advisory planning helpers (P5b / I8b)."""

from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any

from mip.contracts.advisory import (
    AdvisoryClaimType,
    AdvisoryEvidenceMode,
    ChannelCandidate,
    ChannelCandidateName,
    ChannelCategory,
    ChannelSuitabilityAssessment,
    ColdStartAdvisoryPlan,
    ColdStartAdvisoryStatus,
    ColdStartBusinessProfile,
    ColdStartChannelHypothesis,
    ColdStartMediaObjective,
    EvidenceLevel,
    LearningAgenda,
    StarterMeasurementPlan,
    StarterMediaMixHypothesis,
    TrackingReadinessChecklist,
    TrafficSourceSignal,
    WebsiteTrafficSourceProfile,
)

_BLOCKED_NEXT_DEFAULT = [
    "claim_causal_effect",
    "claim_roi_or_lift",
    "claim_optimal_mix",
    "claim_final_budget_allocation",
    "claim_decision_authorization",
    "claim_mmm_readiness_without_report",
    "claim_geox_readiness_without_report",
]

_TRACKING_REQUIRED_ITEMS = [
    "UTM parameters on paid and campaign links",
    "Pixel or tag setup on website/app",
    "Conversion events defined and firing",
    "Lead capture form or CRM handoff",
    "Weekly reporting cadence",
]

_TRACKING_RECOMMENDED_ITEMS = [
    "Landing page readiness and load speed check",
    "Customer list or email capture for CRM",
    "Event naming consistency across platforms",
    "New vs returning user segmentation",
]

_VISUAL_ECOMMERCE_KEYWORDS = frozenset(
    {
        "ecommerce",
        "e-commerce",
        "retail",
        "skincare",
        "fashion",
        "handmade",
        "apparel",
        "beauty",
        "consumer",
        "shop",
        "store",
        "product",
    }
)

_LOCAL_SERVICE_KEYWORDS = frozenset(
    {
        "local",
        "service",
        "plumber",
        "dentist",
        "clinic",
        "contractor",
        "repair",
        "salon",
        "restaurant",
    }
)

_LONG_SALES_CYCLE_KEYWORDS = frozenset(
    {
        "long",
        "months",
        "enterprise",
        "quarter",
        "b2b",
    }
)


def _now() -> datetime:
    return datetime.now(tz=UTC)


def _slug(value: object) -> str:
    if hasattr(value, "value"):
        return str(value.value)
    return str(value).lower()


def _text_blob(*parts: str | None) -> str:
    return " ".join(part.lower() for part in parts if part)


def _is_sparse_profile(profile: ColdStartBusinessProfile) -> bool:
    return not all(
        [
            profile.product_or_service and profile.product_or_service.strip(),
            profile.target_audience and profile.target_audience.strip(),
            profile.primary_objective != ColdStartMediaObjective.UNKNOWN,
            profile.monthly_budget and profile.monthly_budget.strip(),
        ]
    )


def _missing_profile_questions(profile: ColdStartBusinessProfile) -> list[str]:
    questions: list[str] = []
    if not profile.product_or_service or not profile.product_or_service.strip():
        questions.append("What product or service are you marketing?")
    if not profile.target_audience or not profile.target_audience.strip():
        questions.append("Who is your target audience?")
    if profile.primary_objective == ColdStartMediaObjective.UNKNOWN:
        questions.append("What is your primary objective (awareness, leads, sales, traffic)?")
    if not profile.monthly_budget or not profile.monthly_budget.strip():
        questions.append("What monthly budget are you considering for paid media?")
    if profile.existing_tracking is None:
        questions.append("Do you have tracking pixels/tags and conversion events set up?")
    if not profile.geography or not profile.geography.strip():
        questions.append("What geography are you targeting?")
    return questions


def _is_visual_ecommerce(profile: ColdStartBusinessProfile) -> bool:
    blob = _text_blob(profile.business_type, profile.product_or_service)
    return any(keyword in blob for keyword in _VISUAL_ECOMMERCE_KEYWORDS)


def _is_local_service(profile: ColdStartBusinessProfile) -> bool:
    blob = _text_blob(profile.business_type, profile.product_or_service)
    return any(keyword in blob for keyword in _LOCAL_SERVICE_KEYWORDS)


def _is_b2b_long_cycle(profile: ColdStartBusinessProfile) -> bool:
    b2b = _slug(profile.b2b_or_b2c) == "b2b"
    cycle_blob = _text_blob(profile.sales_cycle_length, profile.business_type)
    long_cycle = any(keyword in cycle_blob for keyword in _LONG_SALES_CYCLE_KEYWORDS)
    return b2b and long_cycle


def _candidate(
    *,
    candidate_id: str,
    channel_name: ChannelCandidateName,
    channel_category: ChannelCategory,
    why_relevant: str,
    supported_objectives: list[ColdStartMediaObjective] | None = None,
    required_tracking: list[str] | None = None,
    warnings: list[str] | None = None,
) -> ChannelCandidate:
    return ChannelCandidate(
        candidate_id=candidate_id,
        channel_name=channel_name,
        channel_category=channel_category,
        supported_objectives=supported_objectives or [],
        why_relevant=why_relevant,
        required_tracking=required_tracking or ["UTM setup", "conversion events"],
        warnings=warnings or [],
    )


def build_cold_start_business_profile(
    *,
    profile_id: str,
    created_at: datetime | None = None,
    **fields: Any,
) -> ColdStartBusinessProfile:
    """Construct a cold-start business profile from keyword arguments."""
    return ColdStartBusinessProfile(
        profile_id=profile_id,
        created_at=created_at or _now(),
        **fields,
    )


def infer_advisory_evidence_mode(
    business_profile: ColdStartBusinessProfile,
    traffic_profile: WebsiteTrafficSourceProfile | None = None,
) -> AdvisoryEvidenceMode:
    """Infer advisory evidence mode from profile completeness and traffic summaries."""
    if traffic_profile is not None:
        return AdvisoryEvidenceMode.DATA_INFORMED_ADVISORY
    if _is_sparse_profile(business_profile):
        return AdvisoryEvidenceMode.GENERAL_KNOWLEDGE_ONLY
    return AdvisoryEvidenceMode.BUSINESS_PROFILE_ONLY


def build_traffic_source_signals(
    traffic_profile: WebsiteTrafficSourceProfile,
) -> list[TrafficSourceSignal]:
    """Derive governed traffic-source signals from summary fields."""
    signals: list[TrafficSourceSignal] = []
    blob = _text_blob(
        traffic_profile.source_summary,
        traffic_profile.channel_group_summary,
        traffic_profile.conversion_summary,
    )

    if "organic search" in blob or "search" in blob:
        has_conversion = any(
            token in blob for token in ("convert", "conversion", "purchase", "revenue", "lead")
        )
        signals.append(
            TrafficSourceSignal(
                signal_id=f"{traffic_profile.traffic_profile_id}-search",
                source_or_channel="organic_search",
                evidence_level=(
                    EvidenceLevel.ORGANIC_CONVERSION_SIGNAL
                    if has_conversion
                    else EvidenceLevel.SEARCH_INTENT_SIGNAL
                ),
                signal_summary=(
                    "Organic search traffic shows intent; conversion signal present."
                    if has_conversion
                    else "Organic search traffic shows intent; validate with tracking."
                ),
                engagement_signal=traffic_profile.source_summary,
                conversion_signal=traffic_profile.conversion_summary,
                tracking_quality=traffic_profile.utm_coverage_summary,
            )
        )

    social_tokens = ("instagram", "facebook", "tiktok", "social", "meta")
    if any(token in blob for token in social_tokens):
        has_conversion = "convert" in blob or "conversion" in blob
        signals.append(
            TrafficSourceSignal(
                signal_id=f"{traffic_profile.traffic_profile_id}-social",
                source_or_channel="social_referral",
                evidence_level=(
                    EvidenceLevel.REFERRAL_INTEREST_SIGNAL
                    if not has_conversion
                    else EvidenceLevel.ORGANIC_CONVERSION_SIGNAL
                ),
                signal_summary=(
                    "Social referral traffic shows audience interest; paid social is unproven."
                ),
                engagement_signal=traffic_profile.channel_group_summary,
                conversion_signal=traffic_profile.conversion_summary,
                tracking_quality=traffic_profile.utm_coverage_summary,
                warnings=["Referral traffic does not prove paid channel ROI."],
            )
        )

    if "email" in blob or "crm" in blob:
        signals.append(
            TrafficSourceSignal(
                signal_id=f"{traffic_profile.traffic_profile_id}-email",
                source_or_channel="email_crm",
                evidence_level=EvidenceLevel.CRM_SIGNAL,
                signal_summary="Email or CRM traffic indicates list/retention opportunity.",
                engagement_signal=traffic_profile.source_summary,
                conversion_signal=traffic_profile.conversion_summary,
            )
        )

    if any(token in blob for token in ("referral", "referrer", "affiliate", "creator")):
        signals.append(
            TrafficSourceSignal(
                signal_id=f"{traffic_profile.traffic_profile_id}-referral",
                source_or_channel="referral",
                evidence_level=EvidenceLevel.REFERRAL_INTEREST_SIGNAL,
                signal_summary="Referral domains suggest partnership or creator interest.",
                engagement_signal=traffic_profile.source_summary,
                warnings=["Referral interest is not paid ROI evidence."],
            )
        )

    if any(token in blob for token in ("sale", "purchase", "revenue", "order")):
        signals.append(
            TrafficSourceSignal(
                signal_id=f"{traffic_profile.traffic_profile_id}-sales",
                source_or_channel="conversion_summary",
                evidence_level=EvidenceLevel.SALES_SIGNAL,
                signal_summary="Conversion or sales summary available from governed traffic data.",
                conversion_signal=traffic_profile.conversion_summary,
            )
        )

    return signals


def suggest_channel_candidates(
    business_profile: ColdStartBusinessProfile,
    evidence_mode: AdvisoryEvidenceMode,
    traffic_signals: Sequence[TrafficSourceSignal] = (),
) -> list[ChannelCandidate]:
    """Suggest advisory channel candidates from business profile and traffic signals."""
    candidates: list[ChannelCandidate] = []
    seen: set[str] = set()

    def add(candidate: ChannelCandidate) -> None:
        key = _slug(candidate.channel_name)
        if key in seen:
            return
        seen.add(key)
        candidates.append(candidate)

    if _is_visual_ecommerce(business_profile):
        add(
            _candidate(
                candidate_id="cand-meta",
                channel_name=ChannelCandidateName.META_INSTAGRAM,
                channel_category=ChannelCategory.PAID_SOCIAL,
                why_relevant="Visual ecommerce products often test well on Meta/Instagram.",
                supported_objectives=[
                    ColdStartMediaObjective.AWARENESS,
                    ColdStartMediaObjective.SALES,
                    ColdStartMediaObjective.TRAFFIC,
                ],
            )
        )
        add(
            _candidate(
                candidate_id="cand-tiktok",
                channel_name=ChannelCandidateName.TIKTOK,
                channel_category=ChannelCategory.PAID_SOCIAL,
                why_relevant="Short-form video can support discovery for visual consumer products.",
                supported_objectives=[
                    ColdStartMediaObjective.AWARENESS,
                    ColdStartMediaObjective.TRAFFIC,
                ],
            )
        )
        add(
            _candidate(
                candidate_id="cand-search",
                channel_name=ChannelCandidateName.GOOGLE_SEARCH,
                channel_category=ChannelCategory.SEARCH,
                why_relevant="High-intent search can capture demand for product categories.",
                supported_objectives=[
                    ColdStartMediaObjective.SALES,
                    ColdStartMediaObjective.LEAD_GENERATION,
                    ColdStartMediaObjective.TRAFFIC,
                ],
            )
        )
        add(
            _candidate(
                candidate_id="cand-seo",
                channel_name=ChannelCandidateName.SEO_CONTENT,
                channel_category=ChannelCategory.SEO_CONTENT,
                why_relevant="SEO/content can compound organic demand while paid tests run.",
                supported_objectives=[
                    ColdStartMediaObjective.TRAFFIC,
                    ColdStartMediaObjective.AWARENESS,
                ],
            )
        )
        add(
            _candidate(
                candidate_id="cand-email",
                channel_name=ChannelCandidateName.EMAIL_CRM,
                channel_category=ChannelCategory.EMAIL_CRM,
                why_relevant="Email capture supports retention and list-based tests.",
                supported_objectives=[
                    ColdStartMediaObjective.RETENTION,
                    ColdStartMediaObjective.REPEAT_PURCHASE,
                ],
            )
        )

    if _is_local_service(business_profile):
        add(
            _candidate(
                candidate_id="cand-local-search",
                channel_name=ChannelCandidateName.GOOGLE_SEARCH,
                channel_category=ChannelCategory.SEARCH,
                why_relevant="Local services often start with high-intent search demand.",
                supported_objectives=[
                    ColdStartMediaObjective.LEAD_GENERATION,
                    ColdStartMediaObjective.STORE_VISITS,
                ],
            )
        )
        add(
            _candidate(
                candidate_id="cand-local-maps",
                channel_name=ChannelCandidateName.LOCAL_LISTINGS_MAPS,
                channel_category=ChannelCategory.LOCAL_LISTINGS_MAPS,
                why_relevant="Local listings/maps support discovery for geo-bound services.",
                supported_objectives=[
                    ColdStartMediaObjective.STORE_VISITS,
                    ColdStartMediaObjective.LEAD_GENERATION,
                ],
            )
        )
        add(
            _candidate(
                candidate_id="cand-retarget",
                channel_name=ChannelCandidateName.RETARGETING,
                channel_category=ChannelCategory.RETARGETING,
                why_relevant="Retargeting can support follow-up after site visits.",
                supported_objectives=[
                    ColdStartMediaObjective.LEAD_GENERATION,
                    ColdStartMediaObjective.SALES,
                ],
            )
        )

    if _is_b2b_long_cycle(business_profile):
        add(
            _candidate(
                candidate_id="cand-linkedin",
                channel_name=ChannelCandidateName.LINKEDIN,
                channel_category=ChannelCategory.PAID_SOCIAL,
                why_relevant="B2B long-cycle offers often test on LinkedIn for audience fit.",
                supported_objectives=[
                    ColdStartMediaObjective.LEAD_GENERATION,
                    ColdStartMediaObjective.AWARENESS,
                ],
            )
        )
        add(
            _candidate(
                candidate_id="cand-b2b-search",
                channel_name=ChannelCandidateName.GOOGLE_SEARCH,
                channel_category=ChannelCategory.SEARCH,
                why_relevant="Search captures active demand for B2B solutions.",
                supported_objectives=[
                    ColdStartMediaObjective.LEAD_GENERATION,
                    ColdStartMediaObjective.TRAFFIC,
                ],
            )
        )
        add(
            _candidate(
                candidate_id="cand-b2b-content",
                channel_name=ChannelCandidateName.SEO_CONTENT,
                channel_category=ChannelCategory.SEO_CONTENT,
                why_relevant="Content/SEO supports education across long sales cycles.",
                supported_objectives=[
                    ColdStartMediaObjective.LEAD_GENERATION,
                    ColdStartMediaObjective.AWARENESS,
                ],
            )
        )
        add(
            _candidate(
                candidate_id="cand-b2b-email",
                channel_name=ChannelCandidateName.EMAIL_CRM,
                channel_category=ChannelCategory.EMAIL_CRM,
                why_relevant="Email/CRM nurtures leads across long consideration periods.",
                supported_objectives=[
                    ColdStartMediaObjective.LEAD_GENERATION,
                    ColdStartMediaObjective.RETENTION,
                ],
            )
        )

    if not candidates:
        add(
            _candidate(
                candidate_id="cand-default-search",
                channel_name=ChannelCandidateName.GOOGLE_SEARCH,
                channel_category=ChannelCategory.SEARCH,
                why_relevant="Search is a common starter when objective and audience are defined.",
                supported_objectives=[
                    ColdStartMediaObjective.TRAFFIC,
                    ColdStartMediaObjective.LEAD_GENERATION,
                ],
            )
        )

    for signal in traffic_signals:
        level = _slug(signal.evidence_level)
        channel = signal.source_or_channel
        if level in {"search_intent_signal", "organic_conversion_signal"}:
            add(
                _candidate(
                    candidate_id="cand-traffic-search",
                    channel_name=ChannelCandidateName.GOOGLE_SEARCH,
                    channel_category=ChannelCategory.SEARCH,
                    why_relevant=(
                        "Organic search shows intent; paid search may be a reasonable first test."
                    ),
                    supported_objectives=[
                        ColdStartMediaObjective.SALES,
                        ColdStartMediaObjective.LEAD_GENERATION,
                    ],
                )
            )
        if channel == "social_referral" or level == "referral_interest_signal":
            add(
                _candidate(
                    candidate_id="cand-traffic-social",
                    channel_name=ChannelCandidateName.META_INSTAGRAM,
                    channel_category=ChannelCategory.PAID_SOCIAL,
                    why_relevant=(
                        "Social referral shows interest; small paid social test may be reasonable."
                    ),
                    supported_objectives=[
                        ColdStartMediaObjective.AWARENESS,
                        ColdStartMediaObjective.TRAFFIC,
                    ],
                    warnings=["Paid social performance is unproven without a limited test."],
                )
            )
        if level == "crm_signal":
            add(
                _candidate(
                    candidate_id="cand-traffic-email",
                    channel_name=ChannelCandidateName.EMAIL_CRM,
                    channel_category=ChannelCategory.EMAIL_CRM,
                    why_relevant="Email traffic converts well; prioritize list capture and CRM.",
                    supported_objectives=[
                        ColdStartMediaObjective.RETENTION,
                        ColdStartMediaObjective.REPEAT_PURCHASE,
                    ],
                )
            )
        if channel == "referral" or "referral" in channel:
            add(
                _candidate(
                    candidate_id="cand-traffic-creator",
                    channel_name=ChannelCandidateName.CREATORS_INFLUENCERS,
                    channel_category=ChannelCategory.CREATOR_INFLUENCER,
                    why_relevant="Referral domains may indicate creator or partnership potential.",
                    supported_objectives=[
                        ColdStartMediaObjective.AWARENESS,
                        ColdStartMediaObjective.TRAFFIC,
                    ],
                )
            )
            add(
                _candidate(
                    candidate_id="cand-traffic-affiliate",
                    channel_name=ChannelCandidateName.AFFILIATE_PARTNERSHIPS,
                    channel_category=ChannelCategory.AFFILIATE_PARTNERSHIP,
                    why_relevant="Referral traffic may support affiliate or partnership tests.",
                    supported_objectives=[
                        ColdStartMediaObjective.SALES,
                        ColdStartMediaObjective.TRAFFIC,
                    ],
                )
            )

    if evidence_mode == AdvisoryEvidenceMode.GENERAL_KNOWLEDGE_ONLY and len(candidates) < 2:
        add(
            _candidate(
                candidate_id="cand-general-content",
                channel_name=ChannelCandidateName.SEO_CONTENT,
                channel_category=ChannelCategory.SEO_CONTENT,
                why_relevant="Content/SEO is a low-risk starter while details are clarified.",
                supported_objectives=[
                    ColdStartMediaObjective.TRAFFIC,
                    ColdStartMediaObjective.AWARENESS,
                ],
            )
        )

    return candidates


def build_channel_hypotheses(
    candidates: Sequence[ChannelCandidate],
    evidence_mode: AdvisoryEvidenceMode,
    traffic_signals: Sequence[TrafficSourceSignal] = (),
) -> list[ColdStartChannelHypothesis]:
    """Build labeled channel hypotheses from advisory candidates."""
    claim_type = (
        AdvisoryClaimType.DATA_INFORMED_HYPOTHESIS
        if evidence_mode == AdvisoryEvidenceMode.DATA_INFORMED_ADVISORY
        else AdvisoryClaimType.HYPOTHESIS_TO_TEST
    )
    default_level = (
        EvidenceLevel.BUSINESS_PROFILE_SIGNAL
        if evidence_mode == AdvisoryEvidenceMode.BUSINESS_PROFILE_ONLY
        else EvidenceLevel.NO_CUSTOMER_DATA
    )
    if evidence_mode == AdvisoryEvidenceMode.DATA_INFORMED_ADVISORY and traffic_signals:
        default_level = EvidenceLevel(_slug(traffic_signals[0].evidence_level))

    hypotheses: list[ColdStartChannelHypothesis] = []
    for index, candidate in enumerate(candidates):
        level = default_level
        for signal in traffic_signals:
            if _slug(candidate.channel_name) in _slug(signal.source_or_channel) or (
                _slug(candidate.channel_name) in {"meta_instagram", "tiktok"}
                and signal.source_or_channel == "social_referral"
            ):
                level = EvidenceLevel(_slug(signal.evidence_level))
                break
        hypotheses.append(
            ColdStartChannelHypothesis(
                hypothesis_id=f"hyp-{candidate.candidate_id}-{index + 1}",
                channel_candidate=candidate.channel_name,
                objective=(
                    candidate.supported_objectives[0]
                    if candidate.supported_objectives
                    else ColdStartMediaObjective.UNKNOWN
                ),
                evidence_level=level,
                claim_type=claim_type,
                hypothesis_text=(
                    f"{_slug(candidate.channel_name).replace('_', ' ')} "
                    "may be a reasonable starter test."
                ),
                why_to_test=candidate.why_relevant,
                what_would_increase_confidence=[
                    "Run a limited budget test with verified tracking.",
                    "Collect 2-4 weeks of clean conversion data before scaling.",
                ],
                required_tracking=candidate.required_tracking,
                risks=["Paid performance is unproven until validated with tracking."],
                warnings=list(candidate.warnings),
            )
        )
    return hypotheses


def build_tracking_readiness_checklist(
    business_profile: ColdStartBusinessProfile,
) -> TrackingReadinessChecklist:
    """Build tracking setup checklist from business profile state."""
    missing_items = list(_TRACKING_REQUIRED_ITEMS)
    status = ColdStartAdvisoryStatus.NEEDS_TRACKING_SETUP
    if business_profile.existing_tracking is True:
        missing_items = []
        status = ColdStartAdvisoryStatus.READY_FOR_BASIC_TRACKING
    elif business_profile.existing_tracking is False:
        status = ColdStartAdvisoryStatus.NEEDS_TRACKING_SETUP

    return TrackingReadinessChecklist(
        checklist_id=f"track-{business_profile.profile_id}",
        required_items=list(_TRACKING_REQUIRED_ITEMS),
        recommended_items=list(_TRACKING_RECOMMENDED_ITEMS),
        missing_items=missing_items,
        status=status,
        warnings=(
            ["Tracking must be verified before scaling paid tests."]
            if missing_items
            else ["Re-verify events and UTMs before increasing spend."]
        ),
    )


def build_starter_measurement_plan(
    business_profile: ColdStartBusinessProfile,
    hypotheses: Sequence[ColdStartChannelHypothesis],
) -> StarterMeasurementPlan:
    """Build starter KPI plan from objective — no lift or ROI estimates."""
    objective = business_profile.primary_objective
    if objective == ColdStartMediaObjective.LEAD_GENERATION:
        primary_kpi = "Leads and cost per lead (CPL)"
        secondary = ["Lead quality proxy", "Landing-page conversion rate"]
        guardrails = ["Bounce rate", "Form abandonment"]
    elif objective == ColdStartMediaObjective.SALES:
        primary_kpi = "Purchases and conversion rate"
        secondary = ["Cost per acquisition (observed, not projected)", "Average order value"]
        guardrails = ["Return rate", "Checkout drop-off"]
    elif objective == ColdStartMediaObjective.AWARENESS:
        primary_kpi = "Reach and engaged sessions"
        secondary = ["Traffic to site", "Branded search if available"]
        guardrails = ["Frequency", "Engagement rate"]
    elif objective == ColdStartMediaObjective.TRAFFIC:
        primary_kpi = "Sessions and engaged sessions"
        secondary = ["Landing-page conversion rate", "Pages per session"]
        guardrails = ["Bounce rate"]
    else:
        primary_kpi = "Primary outcome aligned to stated objective"
        secondary = ["Secondary funnel metric", "Engagement metric"]
        guardrails = ["Spend pacing", "Tracking completeness"]

    data_to_collect = [
        "Spend by channel/campaign",
        "Impressions and clicks",
        "Conversion events with UTMs",
        "Weekly summary for reassessment",
    ]
    if hypotheses:
        data_to_collect.append(
            f"Channel-specific results for {_slug(hypotheses[0].channel_candidate)} starter test"
        )

    return StarterMeasurementPlan(
        plan_id=f"measure-{business_profile.profile_id}",
        primary_kpi=primary_kpi,
        secondary_kpis=secondary,
        guardrail_metrics=guardrails,
        reporting_cadence="Weekly summary during starter test period",
        test_timebox_guidance=(
            "Run a limited starter test long enough to collect clean weekly data; "
            "reassess after initial learning window."
        ),
        data_to_collect=data_to_collect,
        warnings=["Timebox is qualitative; do not treat as powered experiment duration."],
    )


def build_learning_agenda(
    business_profile: ColdStartBusinessProfile,
    hypotheses: Sequence[ColdStartChannelHypothesis],
) -> LearningAgenda:
    """Build learning agenda with future routing to formal measurement."""
    channel_names = (
        ", ".join(_slug(h.channel_candidate) for h in hypotheses[:3]) or "starter channels"
    )
    return LearningAgenda(
        agenda_id=f"learn-{business_profile.profile_id}",
        learning_questions=[
            f"Does {channel_names} produce acceptable cost per outcome at starter spend?",
            "Is tracking complete enough to compare channels fairly?",
            "Which audience or creative angles deserve the next limited test?",
        ],
        success_criteria=[
            "Conversion events fire reliably with UTMs",
            "At least one channel shows repeatable starter-test signal",
            "Weekly reporting supports iterate/stop/scale decision",
        ],
        stop_scale_or_iterate_criteria=[
            "Stop or fix tracking if events are missing or UTMs are incomplete",
            "Iterate creative/audience before scaling spend",
            "Scale only after reassessment with clean weekly data",
        ],
        reassessment_triggers=[
            "4+ weeks of clean weekly data",
            "Material change in budget or objective",
            "New traffic or CRM data becomes available",
        ],
        future_measurement_path=[
            "Route to common intake workbench when paid media history accumulates",
            "Reassess MMM readiness via workflow-specific readiness reports",
            "Reassess GeoX readiness when geo-level outcome/media data exists",
        ],
        warnings=["Learning agenda is advisory; not a causal readout or MMM result."],
    )


def _build_starter_media_mix(
    *,
    business_profile: ColdStartBusinessProfile,
    evidence_mode: AdvisoryEvidenceMode,
    hypotheses: list[ColdStartChannelHypothesis],
) -> StarterMediaMixHypothesis | None:
    if not hypotheses:
        return None
    claim_type = (
        AdvisoryClaimType.DATA_INFORMED_HYPOTHESIS
        if evidence_mode == AdvisoryEvidenceMode.DATA_INFORMED_ADVISORY
        else AdvisoryClaimType.HYPOTHESIS_TO_TEST
    )
    levels = list({EvidenceLevel(_slug(hypothesis.evidence_level)) for hypothesis in hypotheses})
    return StarterMediaMixHypothesis(
        mix_id=f"mix-{business_profile.profile_id}",
        business_profile_id=business_profile.profile_id,
        evidence_mode=evidence_mode,
        hypotheses=hypotheses,
        suggested_test_budget_notes=(
            "Hold back most budget until tracking is verified; allocate a small initial test "
            f"within stated budget ({business_profile.monthly_budget or 'unspecified'})."
        ),
        allocation_guidance=(
            "Starter allocation hypothesis: limited budget split to learn across 1-2 channels; "
            "advisory only, not a proven mix."
        ),
        claim_type=claim_type,
        evidence_levels=levels,
        warnings=[
            "Allocation guidance is advisory only; validate with tracking and limited tests."
        ],
        created_at=_now(),
    )


def _resolve_advisory_status(
    *,
    business_profile: ColdStartBusinessProfile,
    hypotheses: list[ColdStartChannelHypothesis],
    tracking_checklist: TrackingReadinessChecklist,
) -> ColdStartAdvisoryStatus:
    if _is_sparse_profile(business_profile):
        return ColdStartAdvisoryStatus.NEEDS_BUSINESS_DETAILS
    if tracking_checklist.status == ColdStartAdvisoryStatus.NEEDS_TRACKING_SETUP:
        return ColdStartAdvisoryStatus.NEEDS_TRACKING_SETUP
    if hypotheses and business_profile.existing_tracking is True:
        return ColdStartAdvisoryStatus.READY_FOR_STARTER_TEST
    if hypotheses:
        return ColdStartAdvisoryStatus.ADVISORY_PLAN_READY
    return ColdStartAdvisoryStatus.ADVISORY_PLAN_READY


def build_cold_start_advisory_plan(
    business_profile: ColdStartBusinessProfile,
    traffic_profile: WebsiteTrafficSourceProfile | None = None,
) -> ColdStartAdvisoryPlan:
    """Assemble a full cold-start advisory plan with evidence and claim labels."""
    evidence_mode = infer_advisory_evidence_mode(business_profile, traffic_profile)
    traffic_signals = (
        build_traffic_source_signals(traffic_profile) if traffic_profile is not None else []
    )
    candidates = suggest_channel_candidates(business_profile, evidence_mode, traffic_signals)
    hypotheses = build_channel_hypotheses(candidates, evidence_mode, traffic_signals)
    tracking_checklist = build_tracking_readiness_checklist(business_profile)
    measurement_plan = build_starter_measurement_plan(business_profile, hypotheses)
    learning_agenda = build_learning_agenda(business_profile, hypotheses)
    starter_media_mix = _build_starter_media_mix(
        business_profile=business_profile,
        evidence_mode=evidence_mode,
        hypotheses=hypotheses,
    )
    clarification_questions = _missing_profile_questions(business_profile)
    claim_types = list(
        {AdvisoryClaimType(_slug(hypothesis.claim_type)) for hypothesis in hypotheses}
    )
    if not claim_types:
        claim_types = [AdvisoryClaimType.GENERAL_MARKETING_GUIDANCE]

    evidence_levels = list(
        {EvidenceLevel(_slug(hypothesis.evidence_level)) for hypothesis in hypotheses}
    )
    if not evidence_levels:
        evidence_levels = [EvidenceLevel.NO_CUSTOMER_DATA]

    suitability = ChannelSuitabilityAssessment(
        assessment_id=f"suit-{business_profile.profile_id}",
        business_profile_id=business_profile.profile_id,
        traffic_profile_id=traffic_profile.traffic_profile_id if traffic_profile else None,
        channel_candidates=candidates,
        evidence_mode=evidence_mode,
        evidence_levels=evidence_levels,
        claim_types=claim_types,
        clarification_questions=clarification_questions,
        warnings=["Channel suitability is advisory only; not ROI-proven."],
        created_at=_now(),
    )

    status = _resolve_advisory_status(
        business_profile=business_profile,
        hypotheses=hypotheses,
        tracking_checklist=tracking_checklist,
    )

    allowed_next_steps = [
        "collect_business_details",
        "setup_tracking_checklist",
        "run_starter_limited_test",
        "reassess_after_data_collection",
        "route_to_common_intake_when_history_accumulates",
        "reassess_mmm_geox_readiness_via_p5_reports",
    ]
    if status == ColdStartAdvisoryStatus.NEEDS_BUSINESS_DETAILS:
        allowed_next_steps = ["collect_business_details", "clarify_objective_and_budget"]
    elif status == ColdStartAdvisoryStatus.NEEDS_TRACKING_SETUP:
        allowed_next_steps = ["setup_tracking_checklist", "collect_business_details"]

    return ColdStartAdvisoryPlan(
        plan_id=f"adv-{business_profile.profile_id}",
        business_profile=business_profile,
        traffic_profile=traffic_profile,
        channel_suitability=suitability,
        channel_hypotheses=hypotheses,
        starter_media_mix=starter_media_mix,
        tracking_checklist=tracking_checklist,
        measurement_plan=measurement_plan,
        learning_agenda=learning_agenda,
        status=status,
        evidence_mode=evidence_mode,
        claim_types=claim_types,
        allowed_next_steps=allowed_next_steps,
        blocked_next_steps=list(_BLOCKED_NEXT_DEFAULT),
        warnings=[
            "Advisory plan only; not causal, ROI-proven, or decision-authorizing.",
            "Referral/organic traffic informs hypotheses; it does not prove paid ROI.",
        ],
        created_at=_now(),
    )
