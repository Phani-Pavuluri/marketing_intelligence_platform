# MIP Chat-First Demo UI Manual Review Result 001

**Artifact ID:** `MIP_CHAT_FIRST_DEMO_UI_MANUAL_REVIEW_RESULT_001`
**Reviewed commit:** `cc08490` — `Align chat-first demo UX`
**Verdict:** `FAILED_REMEDIATION_REQUIRED`

## Review scope

The local canonical application at `http://localhost:8501` was reviewed by a
human. No hosted URL was reviewed.

## Results

| Review item | Result |
| --- | --- |
| Local URL reviewed | Yes |
| Hosted URL reviewed | No |
| Application launch | Pass |
| Chat-first landing begins rendering | Partial |
| Sample-question interaction | Fail |
| Chat input visible | Fail |
| Typed questions | Fail / not testable |
| Conversation history | Not testable |
| Suggested follow-ups | Not testable |
| Reset behavior | Not fully testable |
| Primary-answer clarity | Not testable |
| Progressive disclosure | Not testable |
| Readiness presentation | Not fully testable |
| Blocked claims preserved | Not fully testable |
| Legacy tools de-emphasized | Partial |
| Desktop layout | Partial |
| Narrow layout | Not tested |
| Local/hosted consistency | Not tested |
| Onboarding prompt relevance | Fail |

## Runtime defect

The page began rendering its new landing page and sample-prompt buttons, then
stopped with:

```text
streamlit.errors.StreamlitDuplicateElementKey:
There are multiple elements with the same key='sample_prompt_data_missingness_1'
```

The traceback located the failure in `_render_chat_first_demo_tab` at
`column.button(label, key=f"sample_prompt_{question_id}")`. The blocked render
prevented the chat input from appearing and prevented in-browser testing of
typed questions, history, suggested follow-ups, reset behavior, and claim-safety
presentation.

## Product-flow defect

The opening guided prompts are measurement-assessment questions, including MMM
readiness, current-data conclusions, ROI/channel contribution, budget movement,
GeoX readiness, and next measurement steps. They may be useful after onboarding,
but they do not provide a first-time user with a clear explanation of platform
capabilities, needed data, MMM-versus-GeoX routing, onboarding-data start,
trust/claim boundaries, or sample-workflow orientation.

This review records that product mismatch only. It does not redesign the opening
conversation or prompt taxonomy.

## Outcome and next steps

The overall verdict is `FAILED_REMEDIATION_REQUIRED`. The immediate required
artifact is `MIP_CHAT_FIRST_DEMO_UI_WIDGET_KEY_HOTFIX_001`. After that hotfix,
the required follow-on artifact is
`MIP_CHAT_FIRST_DEMO_UI_ONBOARDING_CONVERSATION_REDESIGN_001`; a formal rereview
is required after the onboarding redesign.
