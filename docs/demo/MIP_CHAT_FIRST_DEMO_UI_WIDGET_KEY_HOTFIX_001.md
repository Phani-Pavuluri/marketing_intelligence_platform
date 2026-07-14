# MIP Chat-First Demo UI Widget-Key Hotfix 001

**Artifact ID:** `MIP_CHAT_FIRST_DEMO_UI_WIDGET_KEY_HOTFIX_001`

## Defect and root cause

A human review of `cc08490` found
`StreamlitDuplicateElementKey` for `sample_prompt_data_missingness_1`. The
initial guided-prompt configuration deliberately reuses
`data_missingness_1` for two distinct semantic prompts, but the page previously
derived its button key from `question_id` alone. Streamlit therefore stopped the
canonical page render before the chat input appeared.

## Implementation

The hotfix adds a small pure `build_prompt_widget_key` helper. Guided prompts
use the deterministic `guided_prompt` namespace plus their rendered position and
question ID. Conversation follow-ups use the distinct
`conversation_follow_up` namespace plus their stable message/position context
and question ID. The prompt taxonomy, classification, deterministic answers, and
claim-safety behavior are unchanged.

## Regression coverage and local result

Focused unit coverage proves deterministic keys, uniqueness across namespaces
and positions, uniqueness for all configured initial prompts and follow-ups, and
safe handling of duplicate semantic question IDs. A
`streamlit.testing.v1.AppTest` regression executes canonical widget registration
and verifies that the page renders without an exception, exposes its chat input
and initial prompts, completes a sample-prompt interaction and rerun, renders a
follow-up, accepts typed input, renders/reset controls, and loads the fixture.

The local hotfix validation passed all of those runtime checks. This confirms
only the widget-key repair. It does not supersede
`MIP_CHAT_FIRST_DEMO_UI_MANUAL_REVIEW_RESULT_001`: the recorded onboarding
prompt mismatch remains unresolved.

## Scope and next step

No onboarding conversation redesign, LLM/provider execution, MMM fitting/export
ingestion, ROI/ROAS computation, budget optimization, GeoX assignment, or GeoX
lift was implemented. The editable-install deployment marker remains `-e .`.

Formal rereview must occur after
`MIP_CHAT_FIRST_DEMO_UI_ONBOARDING_CONVERSATION_REDESIGN_001`.
