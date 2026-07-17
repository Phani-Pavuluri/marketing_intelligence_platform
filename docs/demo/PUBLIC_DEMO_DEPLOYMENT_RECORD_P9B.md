# P9b Public Demo Deployment Record

## Status

| Field | Value |
|-------|-------|
| **Phase** | P9b — Public demo deployment verification |
| **Status** | Verified |
| **Deployment target** | Streamlit Community Cloud |
| **App entrypoint** | `app/streamlit_app.py` |
| **Deployed commit** | `96cf98c` |
| **Hosted URL** | https://marketingintelligenceplatform.streamlit.app/ |
| **Mode** | Deterministic |
| **Secrets** | None |
| **LLM** | Disabled |

## Hosted URL

**Hosted URL:** https://marketingintelligenceplatform.streamlit.app/

Live deterministic public demo on Streamlit Community Cloud. No login, secrets, or LLM provider required.

## Deployment configuration

| Setting | Value |
|---------|-------|
| **Repository** | `Phani-Pavuluri/marketing_intelligence_platform` |
| **Branch** | `main` |
| **Main file path** | `app/streamlit_app.py` |
| **Runtime** | `runtime.txt` → `python-3.11` |
| **Dependencies** | `requirements.txt` |
| **Secrets** | None |

## Smoke-test result

Smoke test **passed** on the deployed deterministic public demo:

- [x] App loads without traceback
- [x] Deterministic mode visible
- [x] Public Demo Safety section visible
- [x] Cold-start advisory samples work
- [x] Demo profiling / readiness samples work
- [x] Calibration mapping samples work
- [x] No LLM / API-key / BYOK / Ollama fields exposed
- [x] No persistent upload or production connector flow
- [x] No causal lift, ROI, power/MDE, matched-market, treatment assignment, or optimized-budget claims

## Public demo safety boundaries

This public demo is intentionally constrained:

- **Deterministic-only** public demo — no LLM provider calls
- **Synthetic/local demo fixtures only** — no production customer data
- **No external services** — no APIs, databases, or cloud storage
- **No secrets** — no platform-managed keys, BYOK fields, or tokens in the app
- **No raw production data** — summaries and fixtures only
- **No persistent storage** — no uploaded file persistence
- **No MMM or GeoX engines run** — no model fitting, design, or inference execution
- **MIP acts as control plane / workflow shell**, not a measurement engine

Outputs are advisory, readiness, and mapping demonstrations — not production measurement decisions.

## Known limitations

- **Not a production deployment** — portfolio/stakeholder demo only
- **Not an API service** — no FastAPI or programmatic HTTP boundary (P10)
- **Not authenticated** — no auth, rate limits, or abuse controls (P11)
- **Not connected to production data** — synthetic fixtures and governed summaries only
- **Does not run MMM fitting or GeoX design/inference engines**
- **LLM explanations are intentionally disabled** in the first public demo

## Next recommended phases

1. **P10 — FastAPI/Docker service wrapper** — only after the public demo remains stable
2. **Optional later P9c/P10-lite** — governed Streamlit LLM mode selector with **disabled default** and **BYOK only**
3. **No platform-managed LLM key** until privacy, cost, auth, and rate-limit controls exist (P11)

## Completion report template

Use this template when updating this record after future deploys or smoke tests:

```text
Hosted URL:
Commit:
Files changed:
Validation:
Smoke-test:
Known issues:
Next recommendation:
```

## Provider deployment status

The later [Groq live/public-demo acceptance record](../architecture/MIP_LLM_GROQ_LIVE_PROVIDER_AND_PUBLIC_DEMO_ACCEPTANCE_001.md) is `GROQ_LIVE_ACCEPTANCE_BLOCKED_BY_PROVIDER_FAILURE`. This P9B deterministic deployment record is unchanged: the hosted Groq secret configuration and authenticated-browser verification remain pending, and Groq is not promoted as the public default.
