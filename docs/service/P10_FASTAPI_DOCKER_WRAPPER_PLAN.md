# P10 FastAPI/Docker Wrapper Plan

## Title and status

| Field | Value |
|-------|-------|
| **Title** | P10 FastAPI/Docker Wrapper Plan |
| **Status** | P10a–P10b.1 implemented; P10c planned |
| **Type** | Service wrapper (P10a–P10c implementation) |
| **Current baseline commit** | `841cca0` |
| **Public demo URL** | https://marketingintelligenceplatform.streamlit.app/ |

This document defines the **minimal, safe service-wrapper plan** for a future API/service layer. It does **not** authorize implementation in this phase.

## Purpose

P10 is intended to wrap **existing deterministic MIP workflow helpers** behind a thin HTTP/service boundary for future deployment and integration testing—not to add new measurement logic, statistical engines, or LLM behavior.

The service wrapper should:

- Expose governed workflow outputs already produced by `mip` and `app.demo_fixtures` helpers
- Provide health/version/metadata endpoints for operators and integrators
- Prepare for portable deployment via Docker without requiring secrets in deterministic mode
- Keep MIP as the **control plane**; MMM and GeoX/panel_exp remain separate engine repositories

P10 does **not** replace the Streamlit public demo. The hosted deterministic demo at https://marketingintelligenceplatform.streamlit.app/ remains the canonical reviewer-facing surface.

## Non-goals

P10 planning and future implementation must **not**:

- Run **MMM fitting** or production MMM execution
- Run **GeoX design/inference** or panel_exp execution
- Calculate or claim **lift, ROI, power/MDE, matched markets, treatment/control assignment**, or **budget optimization**
- Call **LLM providers** (OpenAI, Anthropic, Gemini, Ollama, Hugging Face inference, etc.)
- Add **production connectors**, persistent uploads, databases, queues, or cloud storage
- Add **auth, rate limits, secrets management, or BYOK** in the first service wrapper (deferred to **P11**)
- Replace or break the **Streamlit Community Cloud** public demo
- Expose **raw rows** or unbounded file contents via API
- Claim **production readiness** or decision authorization

MIP remains a **governance/control-plane shell**, not a statistical measurement engine.

## Proposed service boundary

The API is a **thin wrapper** around existing deterministic helpers. Business logic stays in `src/mip/` (and demo fixture wiring in `app/demo_fixtures.py` where appropriate for public-demo parity).

| Capability | Existing helper surface (representative) | Contract outputs |
|------------|----------------------------------------|------------------|
| Cold-start advisory | `build_cold_start_advisory_plan`, `app.demo_fixtures.build_advisory_plan` | `ColdStartAdvisoryPlan` |
| Demo profiling / readiness | `mip.workflows.intake.demo_profiling`, `build_workflow_readiness_reports`, `app.demo_fixtures.build_readiness_reports` | `DemoDatasetProfile`, `*ReadinessReport` |
| Calibration mapping | `map_evidence_to_calibration_signal`, `app.demo_fixtures.build_calibration_fixture` | `CalibrationMappingReport`, `CalibrationSignal` |
| Intake overview | `recommend_intake_path`, `app.demo_fixtures.build_intake_overview_examples` | `IntakePathRecommendation`, session summaries |
| Health / version | package metadata, deployment mode | structured JSON metadata |
| Public demo metadata | deterministic mode banner, fixture catalog, safety boundaries | read-only metadata payload |

The API layer may **serialize/deserialize Pydantic contracts** and apply route-level governance checks. It must **not** reimplement workflow rules inline.

## Candidate endpoints (design only)

All endpoints below are **proposed names only**. No routes are implemented in this phase.

### `GET /health`

| Aspect | Design |
|--------|--------|
| **Input** | None |
| **Output** | `{ "status": "ok", "mode": "deterministic" }` |
| **Governance** | Read-only liveness probe |
| **Blocked claims** | None |
| **Data source** | Service metadata only |

### `GET /version`

| Aspect | Design |
|--------|--------|
| **Input** | None |
| **Output** | Package version, commit/build marker if available, Python version |
| **Governance** | Read-only |
| **Blocked claims** | None |
| **Data source** | Installed `mip` package metadata |

### `GET /demo/metadata`

| Aspect | Design |
|--------|--------|
| **Input** | None |
| **Output** | Public demo mode, fixture catalog keys, safety boundaries summary, hosted demo URL reference |
| **Governance** | Read-only; mirrors Streamlit Public Demo Safety framing |
| **Blocked claims** | Must not imply production readiness or engine execution |
| **Data source** | Deterministic fixture labels + static safety copy |

### `POST /advisory/cold-start`

| Aspect | Design |
|--------|--------|
| **Input** | `ColdStartBusinessProfile` and/or **demo fixture key** (`sample_key`) for parity with public demo |
| **Output** | `ColdStartAdvisoryPlan` |
| **Governance** | Evidence mode and claim type labels preserved; blocked next steps returned structurally |
| **Blocked claims** | ROI, causal lift, optimal mix, budget optimization, decision approval |
| **Data source** | **Phase 1:** synthetic/demo fixture keys only. **Later:** caller-provided validated business profile summaries—never raw production rows by default |

### `POST /readiness/assess`

| Aspect | Design |
|--------|--------|
| **Input** | Demo profiling fixture key and/or governed `CommonDataProfileSummary` / workbench references |
| **Output** | List of workflow readiness reports (`MMMDataReadinessReport`, `GeoXDesignReadinessReport`, etc.) |
| **Governance** | Structural readiness only; blocking reasons and allowed/blocked next steps required |
| **Blocked claims** | Power/MDE, matched markets, treatment assignment, engine diagnostics |
| **Data source** | **Phase 1:** demo fixture path via `build_readiness_reports` / demo profiling helpers. **Later:** validated summaries only |

### `POST /calibration/map`

| Aspect | Design |
|--------|--------|
| **Input** | Demo calibration fixture key and/or governed `CalibrationEvidenceInput` |
| **Output** | `CalibrationMappingReport` (+ optional mapped `CalibrationSignal` reference) |
| **Governance** | Mapping status, lineage, missing/incompatible fields, blocked actions |
| **Blocked claims** | Causal certification, MMM calibration execution, decision approval |
| **Data source** | **Phase 1:** demo fixtures. **Later:** validated evidence inputs with lineage |

### `POST /intake/overview`

| Aspect | Design |
|--------|--------|
| **Input** | Intake session summary fields and/or demo example key |
| **Output** | `IntakePathRecommendation` with warnings, blocking reasons, allowed/blocked next steps |
| **Governance** | Path recommendation only; no execution |
| **Blocked claims** | Engine execution promises, ROI/lift claims |
| **Data source** | **Phase 1:** `build_intake_overview_examples` patterns. **Later:** governed intake session contracts |

## Request/response contract policy

Future P10 implementation must follow these rules:

1. **Use existing Pydantic contracts** from `mip.contracts.*` wherever possible—do not invent parallel DTOs for core workflow outputs.
2. **Prefer governed summaries** (`CommonDataProfileSummary`, readiness reports, advisory plans) over raw tabular rows.
3. **Typed validation errors** — return structured 422 responses with field-level detail; no generic string-only failures for contract violations.
4. **Structured governance status** — responses include `warnings`, `blocking_reasons`, `allowed_next_steps`, `blocked_next_steps`, evidence/claim labels where applicable.
5. **No silent inference** — missing geo, uncertainty/SE, spend, or causal status must surface as explicit blocks or required user inputs; never impute SE from point estimates or invent geo mapping.
6. **No forbidden claim fields** in API responses — align with agentic/LLM forbidden-topic guardrails (ROI, lift, optimal mix, power/MDE, matched markets, treatment assignment, model promotion).
7. **Deterministic mode default** — first service wrapper operates without LLM calls or external services.

## Docker plan (design only)

Future P10c should introduce a **minimal container** without secrets or external dependencies for deterministic mode:

```text
marketing_intelligence_platform/
  Dockerfile                 # added in P10c only
  service/                   # proposed future package (P10a/P10b)
    api/
      main.py                # FastAPI app factory
      routes/
      dependencies.py
```

**Image design (future):**

- Base: `python:3.11-slim` (or equivalent minimal image)
- Install package from repo (`pip install .` or poetry export equivalent)
- Run: `uvicorn service.api.main:app --host 0.0.0.0 --port 8000`
- **No secrets** required for deterministic mode
- **No external service dependencies** (no database, Redis, object storage)
- Health check: `GET /health`
- Production hardening (non-root user, read-only FS, resource limits) deferred to **P11**

**Do not add `Dockerfile` in this planning phase.**

## Streamlit relationship

| Surface | Role |
|---------|------|
| **Streamlit** (`app/streamlit_app.py`) | Canonical **public demo** and reviewer UI; remains deployed at https://marketingintelligenceplatform.streamlit.app/ |
| **FastAPI** (future `service/`) | Programmatic **service wrapper** for the same deterministic helpers |

Rules:

- Streamlit and FastAPI must call **shared MIP workflow helpers**, not duplicate business logic.
- P10 must **not break** Streamlit Community Cloud deployment (`requirements.txt`, `runtime.txt`, `.streamlit/config.toml` unchanged unless explicitly coordinated).
- Streamlit may later call FastAPI for integration tests, but the first P10 slice should prove API contracts against `mip` directly.
- Public demo reviewers are **not required** to use the API.

## Security/privacy posture

First P10 service wrapper (deterministic only):

| Control | Posture |
|---------|---------|
| **Mode** | Deterministic only |
| **Secrets** | None in repo or container for demo API |
| **Persistent storage** | None |
| **Raw production data** | Not accepted in first wrapper |
| **External calls** | None |
| **LLM calls** | None |
| **User uploads** | No production file upload endpoints in first wrapper |
| **Auth / rate limits** | Deferred to **P11** before any hosted production-like API |
| **CORS / public exposure** | Local/dev and smoke-test first; public API hosting requires P11 |

**P11 is required** before any hosted production-like API with auth, rate limits, privacy controls, cost controls, and observability.

## Validation plan for future implementation

When P10a/P10b/P10c are implemented, require:

| Check | Scope |
|-------|-------|
| Unit tests | Route contract serialization, error mapping |
| Route-level governance tests | Forbidden claims blocked; blocking reasons present |
| Import tests | `service.api` public surface |
| Docker build smoke test | Image builds and starts (P10c) |
| Local API smoke test | `/health`, `/version`, one workflow route |
| Streamlit regression | Public demo still runs; no behavior change |
| Full suite | `poetry run pytest`, `poetry run ruff check .`, `poetry run mypy src tests app` |

## Future phase split

| Phase | Scope |
|-------|-------|
| **P10a** | FastAPI contract skeleton; `GET /health`, `GET /version`, `GET /demo/metadata`; no workflow routes yet |
| **P10b** | Deterministic workflow routes: advisory, readiness, calibration, intake overview; fixture-key inputs first | ✓ |
| **P10b.1** | Service boundary cleanup; routes call `mip.workflows.*`; fixtures inputs-only; usage modes doc | ✓ |
| **P10c** | `Dockerfile` + local container smoke test; no public API hosting | Planned |
| **P11** | Hosted API hardening: auth, rate limits, privacy controls, cost controls, observability, secrets management |

Optional later: **P9c** governed Streamlit LLM mode selector (disabled default, BYOK only)—separate from P10 service wrapper.

## Acceptance criteria

P10 **planning** is complete when:

- [x] Service boundary is documented
- [x] Candidate endpoints are documented with inputs, outputs, governance, and blocked claims
- [x] Non-goals and blocked claims are explicit
- [x] Docker plan is documented without implementation
- [x] Streamlit relationship is documented
- [x] Roadmap/README pointers updated
- [x] No runtime/app/dependency changes are made

P10 **implementation** is **not** started in this phase.

## Related documents

- [PUBLIC_DEMO_DEPLOYMENT_RECORD_P9B.md](../demo/PUBLIC_DEMO_DEPLOYMENT_RECORD_P9B.md)
- [ROADMAP_EXECUTION_SEQUENCE.md](../roadmap/ROADMAP_EXECUTION_SEQUENCE.md)
- [REPO_INTEGRATION_STRATEGY.md](../architecture/REPO_INTEGRATION_STRATEGY.md)
