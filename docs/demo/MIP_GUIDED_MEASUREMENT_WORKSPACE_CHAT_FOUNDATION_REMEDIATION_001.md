# MIP Guided Measurement Workspace Chat Foundation Remediation 001

## Defects addressed

Human review found that normal chat messages expanded directly into the page and that unmatched free-form questions returned one long generic response. This remediation also incorporates the uncommitted shell-onboarding fixes: concise welcome copy, compact starter controls, one selected starter answer, and no premature sample references.

## Conversation workspace

Normal user-entered conversation now renders inside one native Streamlit container with a fixed 420px height and border. The composer appears directly after that container. Full session message state remains in product flow, but messages do not keep increasing the document height. Streamlit retains chat-message styling.

The implementation avoids global CSS and JavaScript. The native container provides internal scrolling. Automatic scroll-to-latest is not asserted: current browser visual review remains pending, so the interaction is documented as a limitation requiring user review rather than claimed as accepted.

## Starter selection

The visible question heading is removed. Four balanced starter controls sit beneath the welcome. active_starter_prompt_id selects one shared answer panel; a second selection replaces it and a repeated selection collapses it. Starter answers never enter normal conversation history. State reset, sample selection, upload-information selection, and activation clear starter state.

## Deterministic free-form routing

guided_workspace_intents.py provides a small priority-based router, not a general conversational framework. It recognizes greeting/smoke tests, platform capabilities, data requirements, MMM versus GeoX, planning, trust/uncertainty, sample story, Analyze my data, dataset-specific questions without context, ambiguity, and unsupported questions.

Examples: test receives a short readiness acknowledgement; what data do you need receives practical inputs; questions combining data with MMM/GeoX request clarification; unsupported requests receive a concise scope statement. The prior generic fallback is removed.

General answers are business-first and contain no SaaS, fixture, raw artifact, or contract language before selection. Dataset-specific questions without an active context ask the user to select a sample story or review Analyze my data; they do not make channel claims.

## Safety and boundaries

No vertical journey, upload runtime, CSV work, model fitting, GeoX execution, calibration runtime, simulation, optimization, recommendation, provider, or persistence behavior was added. The existing sample card and activated walkthrough preserve their scoped sample details and claim boundaries.

## Validation and review status

Automated AppTest validates one composer, actual message retention, starter selection, routing relevance, plain-language answers, and no duplicate messages. AppTest cannot inspect visual scrolling; local and hosted browser review are pending when a browser surface is available.

## Next artifact

MIP_GUIDED_MEASUREMENT_WORKSPACE_VERTICAL_JOURNEY_001
