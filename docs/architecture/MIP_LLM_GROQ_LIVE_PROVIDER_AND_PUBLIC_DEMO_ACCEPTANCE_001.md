# MIP LLM Groq Live Provider and Public Demo Acceptance 001

## Verdict

`GROQ_LIVE_ACCEPTANCE_BLOCKED_BY_PROVIDER_FAILURE`

Groq remains an implemented public-demo candidate. OpenAI remains an implemented quality benchmark, and the deterministic router remains the active fallback. Groq is not promoted as the public-demo default.

## Preflight and deterministic evidence

On 2026-07-15, `main` at `6408ee9` matched `origin/main`; all required commits were ancestors, `requirements.txt` retained `-e .`, the working tree had only the task's permitted untracked `.codex/` and `docs/tasks/` paths, and Docker was available. The configured path was `GroqResponsesProvider` in `src/mip/conversation/provider.py`, selected through `ConfiguredProvider` only for `MIP_LLM_PROVIDER=groq`.

The explicit Groq configuration was enabled for `openai/gpt-oss-20b`, with template `mip_read_only_front_door` version `1`, a 20-second timeout, zero retries, and a 900-token output limit. Credentials were present, the SDK client was lazily constructed, and OpenAI SDK version was `1.109.1`. The prescribed automated suites passed with provider invocation disabled: 6 front-door, 10 provider/front-door, 2 evaluation-gate, 64 app, 62 demo, and 339 governance tests. A narrow Streamlit session-state defect was corrected so a serialized `InteractionMode` is stored safely as a string; no control-plane behavior changed.

## Live evidence

Four earlier Streamlit test-triggered provider attempts inherited the configured environment. The remaining deliberate live-call plan was capped at 11, keeping the known total at the 15-call maximum. The mandatory regression (6 turns), comparison (4 turns), and unresolved-artifact question (1 turn) each returned deterministic fallback before a Groq provider disclosure could be produced. The mandatory regression fallback rate was therefore 100%; its old generic fallback appeared on 3 of 6 turns. No provider/model/template identity, provider request ID, source validation outcome, action validation outcome, or claim-guard outcome was exposed by the failed path.

No raw request, response, prompt, transcript, API key, or hidden reasoning was retained. The sanitized per-turn record is in the accompanying evaluation archive.

## Boundaries and incomplete layers

Automated safety evidence remains passing, but it cannot substitute for a successful live provider response. The required controlled provider-failure check was not separately run because successful live calls never occurred. Browser automation was unavailable. The hosted URL was network-reachable but redirected to Streamlit authentication, so public deployment acceptance and hosted secret verification could not be performed. Local browser acceptance is also pending the supplied manual checklist.

The observed live failure prevents quality scoring, platform-truth factuality, source-reference validity, capability/workflow validity, and action-boundary compliance from being certified. This acceptance result does not alter the historical Groq-adapter artifact; `GROQ_HOSTED_OPEN_WEIGHT_PROVIDER_ADAPTER_READY` versus the completion report's `GROQ_CONCRETE_PROVIDER_ADAPTER_READY` is a naming mismatch only.

## Required follow-up

Investigate the sanitized Groq invocation failure through the existing provider seam, preserve the 15-call budget for a fresh acceptance run, then complete the remaining structured-intake, platform-guidance, governed-action, controlled-failure, local-browser, and authenticated-hosted-browser cases. The next architecture artifact remains `MIP_CONVERSATIONAL_CONTROL_PLANE_ARTIFACT_AND_REQUIREMENT_RESOLVER_001`; it is not implemented by this acceptance task.

## Local and deployment checklist

1. Launch `poetry run streamlit run app/streamlit_app.py` and use its emitted URL.
2. Verify the initial composer/starter controls, no empty transcript, no duplicate key, and no exception.
3. Submit the mandatory continuous conversation; verify Groq disclosure, natural answers, compact sources, continuity, and no internal-ID-dominated answer.
4. Verify the MMM action is blocked naturally, the unresolved Meta question requests a result, typed actions work with the provider disabled, and injected provider failure preserves one conversation with one fallback response.
5. In Streamlit Cloud secrets, set the required enabled/Groq/model/timeout/retry/output-token values and the secret `GROQ_API_KEY`; do not commit that file.
6. After deployment refresh, verify the hosted app loads, Groq disclosure and continuity work, governance/artifact boundaries hold, and no duplicate/widget/secret issue appears.
