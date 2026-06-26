# Deterministic Usage Modes

## 1. Purpose

Marketing Intelligence Platform (MIP) works **without an LLM**. Deterministic contracts, validators, and workflow helpers are the governed core of the platform.

An LLM is an **optional conversational interface** over that core. It may explain, route, and summarize governed outputs—but it is **not** the source of measurement truth.

Deterministic usage modes keep MIP honest: the same contracts and workflows power notebooks, the public Streamlit demo, and the FastAPI service wrapper.

## 2. Interface model

MIP exposes multiple surfaces over one shared core:

| Surface | Role | Typical user |
|---------|------|--------------|
| **Python SDK / package** | Direct import of `mip.contracts.*` and `mip.workflows.*` | Developers, notebooks, tests |
| **FastAPI service** (`mip.service`) | HTTP boundary for applications and automation | Integrators, future agents |
| **Streamlit app** (`app/streamlit_app.py`) | Public demo and governance console | Reviewers, stakeholders |
| **Future CLI** | Local operator commands over the same workflows | Developers, operators |
| **Future LLM workbench** | Conversational interface over governed tools | End users with explicit provider config |

All surfaces should call the same workflow helpers where possible. Service and UI layers add transport and presentation only—they do not own measurement logic.

## 3. Shared core

Every interface should call:

- `mip.contracts.*` — governed structures, claim labels, blocking reasons
- `mip.workflows.*` — deterministic workflow execution (advisory, readiness, calibration mapping, intake routing)
- `mip.evaluation.*` — release gates and evaluation helpers where applicable

Service adapters (`mip.service`) translate HTTP requests/responses and attach governance metadata. They must not duplicate business logic or depend on UI rendering code.

**Preferred flow:**

```text
Interface (SDK / FastAPI / Streamlit / future CLI)
  → optional demo fixture input resolver (sample keys only)
  → mip.workflows.* helper
  → mip.contracts.* artifact
  → interface-specific presentation
```

## 4. Streamlit role

The current Streamlit UI is **not** the final product UI. It is a **deterministic public demo and governance console**.

It displays governed artifacts directly so reviewers can inspect:

- what is allowed
- what is blocked
- what data or evidence is missing
- evidence mode and claim type labels

The hosted public demo (https://marketingintelligenceplatform.streamlit.app/) runs in deterministic mode by default. It uses synthetic demo fixtures and does not require LLM providers, secrets, or external services.

## 5. FastAPI role

The FastAPI service (`mip.service`) is a **thin wrapper** for deterministic workflows. It enables future apps, agents, and an LLM workbench to call governed APIs over HTTP.

Responsibilities:

- Expose health/version and workflow routes with stable request/response contracts
- Resolve demo fixture keys into **inputs only** when no custom payload is supplied
- Call `mip.workflows.*` helpers for orchestration
- Attach governance boundary metadata to every response

The service must **not**:

- Duplicate business logic already in `mip.workflows.*`
- Import `app.ui_renderers` or Streamlit
- Use `app.demo_fixtures` as a hidden orchestration layer (orchestration belongs in `mip.workflows.*` or `mip.service.workflows`)

Current P10b routes (deterministic, demo-key inputs):

- `GET /health`
- `GET /version`
- `POST /advisory/cold-start`
- `POST /readiness/assess`
- `POST /calibration/map`
- `POST /intake/overview`

## 6. Python SDK role

Developers and notebooks import the package directly:

```python
from mip.workflows.intake.advisory import build_cold_start_advisory_plan, build_cold_start_business_profile
from mip.workflows.intake.readiness import build_workflow_readiness_reports
from mip.workflows.intake.calibration_mapping import map_evidence_to_calibration_signal
from mip.workflows.intake.recommendation import recommend_intake_path
```

Example — readiness from a constructed workbench:

```python
from mip.workflows.intake.readiness import build_workflow_readiness_reports

# workbench built from contracts + profiling summaries (not shown)
reports = build_workflow_readiness_reports(workbench)
```

Example — calibration mapping:

```python
from mip.workflows.intake.calibration_mapping import map_evidence_to_calibration_signal

signal, report = map_evidence_to_calibration_signal(evidence, requirement)
```

The SDK is the **source of truth** for workflow behavior. FastAPI and Streamlit are consumers.

## 7. Future CLI role

A future CLI would expose the same workflows for local operators, for example:

```bash
mip readiness assess --input data_summary.json
mip calibration map --input experiment_readout.json
mip advisory cold-start --input business_profile.json
mip intake overview --request "Can I use this data for GeoX?"
```

CLI commands would parse inputs into contracts, call `mip.workflows.*`, and print governed summaries—not raw rows or measurement-engine output.

## 8. LLM role

An LLM is **optional**. When enabled (local Ollama, BYOK, or future hosted providers with controls), it should:

- Explain governed outputs in plain language
- Ask follow-up intake questions
- Route users toward the correct workflow
- Summarize readiness, advisory, and mapping reports

An LLM must **not**:

- Estimate causal effects or invent ROI
- Calculate power, MDE, or matched markets
- Choose treatment assignment or optimize budgets
- Approve `TrustReport`s or override readiness/calibration gates
- Receive raw production rows by default

MIP contracts and validators remain authoritative. If LLM output conflicts with a governed artifact, **the deterministic result wins**.

## 9. Non-goals

Deterministic usage modes explicitly exclude:

- Production data ingestion or persistent uploads in the public demo
- Raw row upload or exposure via API
- LLM as a requirement for core functionality
- Measurement-engine execution inside MIP (MMM fitting, GeoX design/inference)
- Replacement of external MMM or GeoX/panel_exp packages

MIP is the **control plane**, not the statistical engine.

## Related documents

- [P10 FastAPI/Docker wrapper plan](P10_FASTAPI_DOCKER_WRAPPER_PLAN.md)
- [Roadmap execution sequence](../roadmap/ROADMAP_EXECUTION_SEQUENCE.md)
- [Repo integration strategy](../architecture/REPO_INTEGRATION_STRATEGY.md)
- [Public demo deployment record (P9b)](../demo/PUBLIC_DEMO_DEPLOYMENT_RECORD_P9B.md)
