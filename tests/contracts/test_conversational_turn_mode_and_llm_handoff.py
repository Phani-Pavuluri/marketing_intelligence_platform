# mypy: ignore-errors
import pytest

# Builders intentionally keep contract fields visually aligned with the specification.
# ruff: noqa: E501
from pydantic import ValidationError

from mip.contracts.conversation import (
    FallbackPolicy,
    FallbackRoute,
    GovernedActionProposal,
    GroundingRequirements,
    GroundingSource,
    InteractionMode,
    InterpretationSource,
    ProviderDisclosure,
    ProviderInvocationStatus,
    TurnClaimPolicy,
    TurnDecision,
)


def policy(mode):
    return TurnClaimPolicy.for_mode(mode)


def fallback():
    return FallbackPolicy(
        fallback_order=[FallbackRoute.SAFE_CLARIFICATION, FallbackRoute.UNSUPPORTED_RESPONSE],
        allow_safe_clarification=True,
    )


def decision(mode, **kwargs):
    values = dict(
        interaction_mode=mode, topic="measurement", domain="mip", user_goal="explain",
        confidence=0.8, grounding_requirements=GroundingRequirements(sources=[GroundingSource.GENERAL_MODEL_KNOWLEDGE]),
        claim_policy=policy(mode), fallback_policy=fallback(), provider_disclosure=ProviderDisclosure(),
    )
    values.update(kwargs)
    return TurnDecision(**values)


@pytest.mark.parametrize("mode", list(InteractionMode))
def test_modes_round_trip_deterministically(mode):
    value = decision(mode, candidate_capability_id="measurement.explain" if mode in {InteractionMode.TYPED_UI_ACTION, InteractionMode.GOVERNED_ACTION} else None,
                     requires_platform_truth=mode == InteractionMode.PLATFORM_GUIDANCE,
                     requires_artifact=mode == InteractionMode.ARTIFACT_INTERPRETATION,
                     grounding_requirements=GroundingRequirements(sources=[GroundingSource.CLAIM_VERIFICATION, GroundingSource.ACTIVE_ARTIFACT] if mode == InteractionMode.ARTIFACT_INTERPRETATION else [GroundingSource.GENERAL_MODEL_KNOWLEDGE]))
    assert value.model_dump_json() == type(value).model_validate_json(value.model_dump_json()).model_dump_json()


def test_mode_invariants_are_fail_closed():
    with pytest.raises(ValidationError):
        decision(InteractionMode.GENERAL_EXPLANATION, requires_execution=True)
    with pytest.raises(ValidationError):
        decision(InteractionMode.PLATFORM_GUIDANCE)
    with pytest.raises(ValidationError):
        decision(InteractionMode.ARTIFACT_INTERPRETATION, requires_artifact=True)
    with pytest.raises(ValidationError):
        decision(InteractionMode.UNSUPPORTED, requires_artifact=True)


def test_action_proposal_is_not_authorization_and_has_no_executor():
    proposal = GovernedActionProposal(
        requested_capability_id="mmm.fit", user_goal="fit model", confidence=0.6,
        proposal_source=InterpretationSource.CONSTRAINED_LLM,
    )
    assert "executor" not in proposal.model_dump()
    assert "callable" not in proposal.model_dump()
    with pytest.raises(ValidationError):
        GovernedActionProposal(requested_capability_id="bad id", user_goal="fit model", confidence=0.6,
                               proposal_source=InterpretationSource.CONSTRAINED_LLM)


def test_proposal_and_clarification_boundaries():
    with pytest.raises(ValidationError):
        GovernedActionProposal(requested_capability_id="mmm.fit", user_goal="fit", confidence=1.1, proposal_source=InterpretationSource.CONSTRAINED_LLM)
    with pytest.raises(ValidationError):
        decision(InteractionMode.GOVERNED_ACTION, clarification_required=True)


def test_claim_policy_defaults_block_unsafe_categories():
    p = policy(InteractionMode.GENERAL_EXPLANATION)
    assert not p.allows_recommendations
    assert not p.allows_execution_claims
    assert not p.allows_platform_status_claims
    assert not p.allows_user_data_claims
    assert not p.allows_numeric_artifact_claims


def test_provider_disclosure_supports_failure_fallback_without_private_reasoning():
    disclosure = ProviderDisclosure(invocation_status=ProviderInvocationStatus.FALLBACK_USED, fallback_used=True)
    assert disclosure.model_dump_json() == ProviderDisclosure.model_validate_json(disclosure.model_dump_json()).model_dump_json()
    assert "chain_of_thought" not in disclosure.model_dump()
