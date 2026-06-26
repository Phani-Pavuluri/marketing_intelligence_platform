# P11 API Hardening and Service Packaging Plan 001

## 1. Title and status

| Field | Value |
|-------|-------|
| **Title** | P11 API Hardening and Service Packaging Plan 001 |
| **Status** | Accepted implementation plan |
| **Type** | Service / API hardening roadmap |
| **Baseline commit** | `b592fd3` (P10c Docker smoke merged) |
| **Public demo URL** | https://marketingintelligenceplatform.streamlit.app/ |
| **Related docs** | [P10 FastAPI/Docker wrapper plan](P10_FASTAPI_DOCKER_WRAPPER_PLAN.md), [P10c Docker smoke report](P10C_DOCKER_SERVICE_SMOKE_REPORT.md), [Deterministic usage modes](DETERMINISTIC_USAGE_MODES.md), [Synthetic demo dataset strategy](../product/SYNTHETIC_DEMO_DATASET_STRATEGY_PLAN_001.md) |

This document defines **what API hardening means** for MIP’s deterministic FastAPI service **before** adding more runtime features. It does **not** authorize implementation in this phase. Runtime behavior is unchanged.

## 2. Purpose

**P10** introduced the deterministic FastAPI service (`mip.service`) and a local Docker smoke path (**P10c**). **P11** defines the next hardening layer before:

- adding more routes
- LLM workbench behavior
- uploads or production data ingestion
- SDK / notebook examples (P12)
- Stage A synthetic fixture files
- hosted deployment assumptions

**P11 is about making the API predictable, testable, documented, and safe as a service surface**—not about turning MIP into a production-hosted measurement platform.

MIP remains the **control plane**, not the statistical engine.

## 3. Current service surface

### Endpoints (implemented)

| Method | Path | Input mode | Purpose |
|--------|------|------------|---------|
| `GET` | `/health` | — | Deterministic service health metadata |
| `GET` | `/version` | — | Package version, phase, governance flags |
| `POST` | `/advisory/cold-start` | `sample_key` (demo fixture) | Cold-start advisory plan |
| `POST` | `/readiness/assess` | `sample_key` (demo fixture) | Workflow readiness reports |
| `POST` | `/calibration/map` | `sample_key` (demo fixture) | CalibrationSignal mapping |
| `POST` | `/intake/overview` | `example_key` (demo fixture) | Intake path recommendation summary |

### Current phase metadata

| Field | Value | Notes |
|-------|-------|-------|
| **Runtime `api_phase`** | `P10b.1` | Unchanged by P10c |
| **P10c scope** | Docker packaging / local smoke only | No new routes or contract changes |
| **Service mode** | `deterministic` | No LLM, persistence, or engine execution |

Workflow routes resolve **demo fixture keys** into inputs, call `mip.workflows.*`, and return typed service responses with governance metadata.

## 4. API hardening dimensions

### Request contracts

**Goals (future implementation):**

- Stable typed request models per route (`mip.service.contracts`)
- Explicit **fixture-key vs structured-input** behavior documented per endpoint
- **No raw production rows** in public/demo service paths unless a later governed capability is explicitly approved
- Deterministic synthetic / demo input support only for near-term surfaces
- Validation errors surfaced consistently (422 for schema violations, 400 for unknown keys)

**Near-term rule:** Demo fixture keys are the supported input mode. Structured JSON payloads matching contracts may be added later with the same governance boundaries.

### Response contracts

**Goals (future implementation):**

- Stable typed response envelopes per route
- Consistent `status` / workflow status fields
- Consistent `governance` block on every workflow response (`llm_enabled`, `measurement_engine_execution`, `advisory_only`, etc.)
- Explicit `blocking_reasons`, `warnings`, `allowed_next_steps`, `blocked_next_steps`
- Explicit evidence mode / claim-type exposure where applicable
- Explicit unsupported / diagnostic-only markers (no implied ROI, lift, or budget optimization)

### Error semantics

**Planned error categories:**

| Category | Typical HTTP | Example |
|----------|--------------|---------|
| Validation error | `422` | Invalid JSON shape, wrong field types |
| Unknown fixture key | `400` | Unsupported `sample_key` / `example_key` |
| Missing required field | `422` | Required request field absent |
| Incompatible evidence | `200` with governed blocked artifact | Calibration mapping blocked—not a transport error |
| Internal deterministic workflow error | `500` | Unexpected exception in workflow helper |

**Principle:** Prefer **governed error responses** in workflow artifacts where the domain model already encodes blocking (e.g. calibration mapping `status: blocked`). Do **not** hide true service failures—unexpected exceptions should remain visible as service errors with safe messages (no stack traces in public responses by default).

**Future:** Optional explicit service error contract model (error code, category, safe message, governance context).

### OpenAPI / schema stability

**Goals (future implementation):**

- Inspect generated OpenAPI (`/openapi.json`) in CI or snapshot tests
- Clear route `summary` / `description` on each endpoint
- Request/response **examples** in OpenAPI or companion docs (after semantics stabilize)
- Schema stability tests before externalizing API to third parties
- Document forbidden output phrases remain absent from examples

### Versioning

**Current stance:**

- **No public stable API version** yet (`/v1/...` not introduced)
- `/version` reports internal **phase** (`P10b.1`) and package version—not a semver API guarantee
- Breaking route or schema changes should update phase metadata and tests explicitly

**Future options (deferred):**

- URL prefix `/v1/...` after route semantics mature
- Explicit API semver in `/version` separate from implementation phase
- Deprecation policy for fixture keys and response fields

### Determinism / reproducibility

**Requirements:**

- No randomness in service responses unless seeded and documented
- Demo fixtures and resolver outputs must remain **stable** across runs
- Docker smoke (`mip-service:p10c`) must reproduce the same `/health` and `/version` behavior as local `uvicorn`
- Same `sample_key` → same governed artifact shape (modulo non-semantic timestamps if any)

### Security / privacy non-goals (current P11 phase)

**Explicitly not in scope for near-term P11 implementation:**

| Capability | Status |
|------------|--------|
| Authentication / authorization | Deferred |
| Secrets management | Deferred |
| Rate limits / abuse controls | Deferred |
| Data persistence / databases | Deferred |
| Production file upload | Deferred |
| External services / connectors | Deferred |
| LLM providers (BYOK, Ollama, hosted) | Deferred |
| Customer production data handling | Deferred |

P11 **documents** the service surface and hardening path; **hosted** hardening (auth, rate limits, privacy controls, cost controls) remains a **later** milestone after contract stability and SDK examples.

### Observability (future, not P11 implementation)

Possible later additions:

- Structured request logs (non-sensitive)
- Request IDs / correlation IDs
- Agent `AgentRunManifest` integration for service calls
- Failure packets for deterministic workflow errors
- Trace IDs for multi-step intake flows
- Non-sensitive diagnostic headers

Do **not** implement observability infrastructure in the P11 docs-only phase.

## 5. Service boundary rules

Restated from P10b.1:

```text
Client → mip.service (HTTP adapter)
           → optional app.demo_fixtures resolve_* (inputs only)
           → mip.workflows.* (orchestration)
           → mip.contracts.* (governed structures)
           → mip.service response mapping + governance metadata
```

| Layer | Role |
|-------|------|
| `mip.service` | API adapter; request/response mapping; no business orchestration |
| `mip.workflows.*` | Deterministic workflow execution |
| `mip.contracts.*` | Governed structures, claim labels, blocking reasons |
| `app.demo_fixtures` | Sample input resolution only—not hidden orchestration |
| `app.ui_renderers` / Streamlit | **Outside** service; not imported by `mip.service` |
| MMM / GeoX engines | **Outside** MIP; handoff only when certified |

## 6. Docker / service packaging expectations

From **P10c** (unchanged in P11 docs phase):

| Expectation | Value |
|-------------|-------|
| Container runs | FastAPI (`uvicorn mip.service.app:app`) **only** |
| Streamlit | Not containerized in P10c/P11 |
| Purpose | Local deterministic packaging validation |
| Production claim | **None** — not production deployment |
| Orchestration | No compose / k8s / cloud deployment in P11 |
| Image tag example | `mip-service:p10c` |

Docker proves the service **installs and starts**; P11 proves the service **contracts and behavior** are stable enough for SDK and integrator use.

## 7. Future implementation candidates

After this plan is accepted, recommended **code** tasks (not authorized here):

| Task | Purpose |
|------|---------|
| Response envelope consistency tests | Every workflow route includes full governance block |
| OpenAPI schema snapshot / inspection test | Catch accidental schema drift |
| Clearer route summaries and descriptions | Integrator-facing clarity |
| Explicit service error contract model | Uniform non-domain errors |
| Deterministic fixture registry tests | Documented keys match resolvers |
| Request/response examples under `docs/service/` | curl/SDK quickstart input |
| Local API quickstart doc | Developer onboarding |
| P12 SDK/API usage examples | Python, curl, future notebooks |

**Out of scope for first P11 implementation slice:** auth, rate limits, uploads, new workflow routes, LLM endpoints.

## 8. Relationship to P12

**P12 — SDK / API usage examples** should consume the hardened service contract plan:

- Python package examples calling `mip.workflows.*` directly
- curl examples against `mip.service` routes
- Future notebook flows (deterministic only initially)
- No production data ingestion
- Same governance boundaries as Streamlit and FastAPI demo paths

P12 should **not** precede P11 contract/error/OpenAPI stability work—examples on a moving schema create churn.

**After P12:** Stage A synthetic fixture files per [SYNTHETIC_DEMO_DATASET_STRATEGY_PLAN_001.md](../product/SYNTHETIC_DEMO_DATASET_STRATEGY_PLAN_001.md).

## 9. Recommended sequence

| Step | Milestone |
|------|-----------|
| ✓ | P10a–P10c — service shell, routes, boundary cleanup, Docker smoke |
| ✓ | P11 plan — this document |
| → | P11 implementation — contract tests, OpenAPI stability, error/docs polish |
| → | P12 — SDK / API usage examples |
| → | Stage A synthetic deterministic fixtures |
| → | Landing-page guided demos (deterministic outputs only) |
| Later | Hosted API hardening (auth, rate limits, privacy, cost controls) |
| Later | Engine-backed demo outputs (Stage B) |

## 10. Acceptance criteria

This **planning** task is complete when:

- [x] Current API surface is documented
- [x] Hardening dimensions are documented
- [x] Service boundary rules are documented
- [x] Docker packaging expectations are documented
- [x] Future implementation candidates are listed
- [x] Relationship to P12 is documented
- [x] Roadmap updated
- [x] No runtime behavior changed

## Related documents

- [P10 FastAPI/Docker wrapper plan](P10_FASTAPI_DOCKER_WRAPPER_PLAN.md)
- [P10c Docker service smoke report](P10C_DOCKER_SERVICE_SMOKE_REPORT.md)
- [Deterministic usage modes](DETERMINISTIC_USAGE_MODES.md)
- [Product entrypoint plan](../product/PRODUCT_ENTRYPOINT_AND_DEMO_EXPERIENCE_PLAN_001.md)
- [Synthetic demo dataset strategy](../product/SYNTHETIC_DEMO_DATASET_STRATEGY_PLAN_001.md)
- [Roadmap execution sequence](../roadmap/ROADMAP_EXECUTION_SEQUENCE.md)
