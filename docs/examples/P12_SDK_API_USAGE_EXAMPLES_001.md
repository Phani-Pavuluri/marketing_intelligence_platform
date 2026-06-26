# P12 SDK and API Usage Examples 001

## 1. Title and status

| Field | Value |
|-------|-------|
| **Title** | P12 SDK and API Usage Examples 001 |
| **Status** | Implemented deterministic usage examples |
| **Type** | Developer usage / SDK / API examples |
| **Baseline** | P10a–P10c service + P11 API hardening merged; `api_phase` remains `P10b.1` |
| **Related docs** | [Deterministic usage modes](../service/DETERMINISTIC_USAGE_MODES.md), [P11 API hardening plan](../service/P11_API_HARDENING_AND_SERVICE_PACKAGING_PLAN_001.md), [Product entrypoint plan](../product/PRODUCT_ENTRYPOINT_AND_DEMO_EXPERIENCE_PLAN_001.md), [Synthetic demo dataset strategy](../product/SYNTHETIC_DEMO_DATASET_STRATEGY_PLAN_001.md) |

These examples are **documentation only**. They do not add routes, fixtures, notebooks, or runtime behavior.

## 2. Purpose

P12 shows how **technical users** can use MIP **without the LLM** or Streamlit UI:

- import deterministic contracts and workflows from the Python package
- call the existing FastAPI service locally or in Docker
- interpret governed outputs and blocked claims

Examples use **today’s** import paths and demo fixture keys. P12 records current package usage; future ergonomics may introduce thinner public SDK helpers.

MIP is the **control plane**, not the statistical engine. These examples do **not** run MMM fitting, GeoX design/inference, or production data ingestion.

## 3. Usage modes covered

| Mode | When to use |
|------|-------------|
| **Python package / SDK** | Notebooks, tests, backend jobs calling `mip.workflows.*` directly |
| **FastAPI local service** | HTTP integration, curl, future agents |
| **Dockerized service** | Local packaging smoke, reproducible service runs |
| **Governance workflow** | Inspect `governance` blocks, blocking reasons, evidence modes |

**Not covered here:** production uploads, LLM providers, auth, persistence, MMM/GeoX engine execution.

## 4. Python SDK / package examples

Install and run from the repo root:

```bash
cd marketing_intelligence_platform
poetry install
poetry run python
```

### 4.1 Cold-start advisory

Uses demo fixture input resolution + workflow helper (same boundary as the FastAPI service):

```python
from app.demo_fixtures import resolve_advisory_demo_inputs
from mip.workflows.intake.advisory import build_cold_start_advisory_plan

inputs = resolve_advisory_demo_inputs("dtc_skincare_ecommerce")
plan = build_cold_start_advisory_plan(inputs.business_profile, inputs.traffic_profile)

print(plan.status)
print(plan.evidence_mode)
print(plan.claim_types)
print(plan.channel_hypotheses[0].hypothesis_text)
print(plan.blocking_reasons)
```

Valid advisory `sample_key` values (demo fixtures): `dtc_skincare_ecommerce`, `local_fitness_studio`, `traffic_informed_advisory`.

You can also build a profile directly:

```python
from datetime import UTC, datetime

from mip.contracts.advisory import ColdStartMediaObjective
from mip.workflows.intake.advisory import (
    build_cold_start_advisory_plan,
    build_cold_start_business_profile,
)

profile = build_cold_start_business_profile(
    profile_id="example-profile-001",
    created_at=datetime.now(tz=UTC),
    product_or_service="Local fitness studio",
    monthly_budget="$1500",
    primary_objective=ColdStartMediaObjective.LEAD_GENERATION,
    geography="Austin, TX",
)
plan = build_cold_start_advisory_plan(profile)
```

### 4.2 Readiness assessment

```python
from app.demo_fixtures import resolve_readiness_demo_context
from mip.workflows.intake.readiness import (
    build_geox_design_readiness_report,
    build_mmm_data_readiness_report,
    build_workflow_readiness_reports,
)

context = resolve_readiness_demo_context("national_mmm_ready_geox_blocked")
reports = list(build_workflow_readiness_reports(context.primary_workbench))

if context.geo_level_mmm_workbench is not None and context.geox_workbench is not None:
    reports.append(build_mmm_data_readiness_report(context.geo_level_mmm_workbench))
    reports.append(build_geox_design_readiness_report(context.geox_workbench))

for report in reports:
    print(report.report_type, report.status, report.blocking_reasons)
```

Valid readiness `sample_key` values: `national_mmm_ready_geox_blocked`, `dma_week_structurally_ready`.

**Stage A fixtures:** JSON summaries and calibration payloads live under `examples/fixtures/stage_a/`. See [Stage A fixture README](../../examples/fixtures/stage_a/README.md) and `manifest.json` for the canonical index.

### 4.3 Calibration mapping

```python
from app.demo_fixtures import resolve_calibration_demo_inputs
from mip.workflows.intake.calibration_mapping import map_evidence_to_calibration_signal

inputs = resolve_calibration_demo_inputs("valid_governed_evidence")
signal, report = map_evidence_to_calibration_signal(inputs.evidence, inputs.requirement)

print(report.status)
print(report.mapped_signal_id)
print(report.blocking_reasons)
if signal is not None:
    print(signal.calibration_id)
```

Other calibration demo keys: `missing_uncertainty`, `metric_mismatch`.

**Stage A fixtures:** Load `evidence` and `requirement` from `examples/fixtures/stage_a/calibration/*.json` into the same contracts (see [fixture README](../../examples/fixtures/stage_a/README.md)).

### 4.4 Intake path overview

```python
from app.demo_fixtures import resolve_intake_demo_inputs
from mip.workflows.intake.recommendation import recommend_intake_path

demo = resolve_intake_demo_inputs("national_mmm_diagnostic")
recommendation = recommend_intake_path(demo.session)

print(recommendation.recommended_path)
print(recommendation.status)
print(recommendation.why_this_path)
print(recommendation.required_next_questions)
```

Valid intake `example_key` values: `national_mmm_diagnostic`, `geox_experiment_design`.

### 4.5 Governance metadata (API responses)

Workflow HTTP responses include a `governance` object (`mip.service.contracts.GovernanceBoundary`). In Python, inspect plan/report fields directly—`blocking_reasons`, `allowed_next_steps`, `blocked_next_steps`, evidence modes, and claim types.

`TrustReport` assembly and decision authorization remain deferred; do not infer production readiness from advisory or readiness outputs alone.

## 5. FastAPI local service examples

Start the service:

```bash
poetry run uvicorn mip.service.app:app --host 127.0.0.1 --port 8000
```

### Health and version

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/version
```

Expected: `status: ok`, `mode: deterministic`, `api_phase: P10b.1`, all capability flags false (no LLM, persistence, or engine execution).

### Workflow POST routes

**Cold-start advisory:**

```bash
curl -s -X POST http://127.0.0.1:8000/advisory/cold-start \
  -H 'Content-Type: application/json' \
  -d '{"sample_key":"dtc_skincare_ecommerce"}'
```

**Readiness assess:**

```bash
curl -s -X POST http://127.0.0.1:8000/readiness/assess \
  -H 'Content-Type: application/json' \
  -d '{"sample_key":"national_mmm_ready_geox_blocked"}'
```

**Calibration map:**

```bash
curl -s -X POST http://127.0.0.1:8000/calibration/map \
  -H 'Content-Type: application/json' \
  -d '{"sample_key":"valid_governed_evidence"}'
```

**Intake overview:**

```bash
curl -s -X POST http://127.0.0.1:8000/intake/overview \
  -H 'Content-Type: application/json' \
  -d '{"example_key":"national_mmm_diagnostic"}'
```

### Validation errors

Unknown fields or wrong types return **422** (Pydantic `extra=forbid` on request models). Unknown fixture keys return **400**.

```bash
# 422 — wrong type
curl -s -X POST http://127.0.0.1:8000/advisory/cold-start \
  -H 'Content-Type: application/json' \
  -d '{"sample_key":123}'

# 400 — unknown key
curl -s -X POST http://127.0.0.1:8000/advisory/cold-start \
  -H 'Content-Type: application/json' \
  -d '{"sample_key":"unknown"}'
```

OpenAPI schema: `http://127.0.0.1:8000/openapi.json` (six routes only; see P11 contract tests).

## 6. Docker usage examples

Build and run (map host port if 8000 is busy):

```bash
docker build -t mip-service:p12 .
docker run --rm -p 8001:8000 mip-service:p12
```

Smoke:

```bash
curl http://127.0.0.1:8001/health
curl http://127.0.0.1:8001/version
```

Docker runs **FastAPI only**—not Streamlit, not LLM, not production hosting. Streamlit remains the canonical public demo: https://marketingintelligenceplatform.streamlit.app/

## 7. Output interpretation

### Cold-start advisory

| Signal | Meaning |
|--------|---------|
| `evidence_mode` | e.g. `business_profile_only`, `data_informed_advisory` |
| `claim_types` | e.g. `hypothesis_to_test` — **not** causal proof |
| `channel_hypotheses` | Starter channels to **test**, not ROI-optimal mix |
| `tracking_checklist` | What to set up before paid tests |
| `governance.advisory_only` | `true` on advisory route |

### Readiness

| Signal | Meaning |
|--------|---------|
| `reports[].status` | Structurally ready, blocked, or needs more data |
| `blocking_reasons` | Why a workflow path is blocked |
| `required_next_inputs` | Missing data checklist |
| `supported_route` | Which intake path structure allows |

Readiness does **not** mean MMM is fitted or GeoX design is powered.

### Calibration mapping

| Signal | Meaning |
|--------|---------|
| `status: mapped` | Evidence can map to a diagnostic-tier `CalibrationSignal` |
| `mapped_signal_id` | Governed signal id when mapped |
| `missing_uncertainty` key | Blocked when standard error absent |
| `metric_mismatch` key | Blocked on incompatible metric |

Calibration mapping does **not** certify causal lift or approve budget moves.

### Intake overview

| Signal | Meaning |
|--------|---------|
| `recommended_path` | Suggested next workflow (e.g. national MMM diagnostic) |
| `why_this_path` | Routing rationale from contracts |
| `why_other_paths_blocked` | Why alternatives are not recommended yet |
| `required_next_inputs` | Questions/data needed next |

Intake routing is **not** a measurement conclusion.

## 8. Unsupported claims

MIP deterministic examples must **not** be read as:

| Claim | Status |
|-------|--------|
| Causal lift from advisory | **Not supported** |
| ROI proof without certified evidence | **Not supported** |
| Budget optimization without governed `DecisionSurface` | **Not supported** |
| GeoX matched markets / power / MDE | **Not supported** unless certified GeoX engine path exists |
| MMM channel ROI / response curves | **Not supported** unless certified MMM engine outputs exist |
| Production readiness | **Not supported** — demo/control-plane only |

API `governance` fields (`causal_decision_support`, `roi_claims_allowed`, `measurement_engine_execution`) are `false` for current workflow routes.

## 9. Relationship to product plans

| Plan | How P12 connects |
|------|------------------|
| [Product entrypoint plan](../product/PRODUCT_ENTRYPOINT_AND_DEMO_EXPERIENCE_PLAN_001.md) | Guided demo journeys map to the same workflows shown here |
| [Synthetic demo dataset strategy](../product/SYNTHETIC_DEMO_DATASET_STRATEGY_PLAN_001.md) | **Stage A** fixtures at `examples/fixtures/stage_a/` reuse these workflow patterns |

P12 is the **developer-facing** usage path. Landing-page and notebook work build on these examples later.

## 10. Future notebooks (not created in P12)

| Notebook | Purpose |
|----------|---------|
| `01_cold_start_advisory.ipynb` | Advisory plan from business profile / fixtures |
| `02_check_data_readiness.ipynb` | Readiness reports from summary data |
| `03_map_experiment_evidence.ipynb` | Calibration mapping walkthrough |
| `04_api_service_usage.ipynb` | curl / HTTP client against `mip.service` |

Engine-backed notebooks (`05+`) wait for certified MMM/GeoX wiring per synthetic dataset strategy Stage B.

## Related documents

- [P10c Docker service smoke report](../service/P10C_DOCKER_SERVICE_SMOKE_REPORT.md)
- [P11 API hardening plan](../service/P11_API_HARDENING_AND_SERVICE_PACKAGING_PLAN_001.md)
- [Roadmap execution sequence](../roadmap/ROADMAP_EXECUTION_SEQUENCE.md)
