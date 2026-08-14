# Marketing Intelligence Platform (MIP)

MIP is a causal marketing intelligence platform and control plane that connects
experimentation, channel incrementality, MMM calibration, strategic planning,
governed decision workflows, and conversational AI. It turns analytical
evidence into explainable decision support without moving causal or statistical
authority into the application—or into an LLM.

**Try the deterministic public demo:**
[marketingintelligenceplatform.streamlit.app](https://marketingintelligenceplatform.streamlit.app/)

The hosted experience uses synthetic fixtures, calls no MMM or GeoX engine,
uses no LLM or external service, and requires no secrets or API key. It is a
portfolio/demo workflow, not a production measurement system.

## Why MIP exists

Experimentation and marketing mix modeling often live in separate workflows.
An experiment may establish incrementality for one channel and period, while an
MMM supports broader planning, but teams still have to decide whether the
evidence is compatible, current, traceable, and strong enough to influence a
budget decision.

MIP provides the layer between analytical engines and decision workflows. It
standardizes evidence and lineage, applies compatibility and release gates,
routes only eligible artifacts, and makes uncertainty and blockers visible. A
generic AI assistant cannot safely fill those gaps by inventing lift, fitting a
model in prose, or upgrading weak evidence. MIP lets an LLM guide and explain
the governed process while contracts, engines, gates, and human approvals keep
their authority.

## What users can achieve

MIP is designed to help teams answer questions such as:

- Which channels are actually incremental?
- How should eligible experiment evidence affect an MMM?
- Is the current evidence trustworthy enough for planning?
- What data, KPI, controls, geography, history, and grain does this question
  require?
- What would change under a different spend scenario?
- Can spend be reallocated next quarter, or is another experiment needed first?

Today, the repository supports governed intake, data/readiness inspection,
typed evidence and decision contracts, trust gates, fixture-backed journeys,
and safe explanations of what is answerable or blocked. Live end-to-end engine
execution, certified GeoX-to-MMM calibration, numerical planning, optimization,
and production recommendations remain gated or planned; the demo does not
fabricate substitutes for them.

## How MIP works

The governed target flow is:

```text
Business question
  → objective and data intake
  → readiness checks and workflow selection
  → eligible GeoX / MMM engine artifacts
  → governed evidence and calibration compatibility
  → TrustReport
  → eligible simulation / planning / recommendation surfaces
  → artifact-grounded conversational explanation
```

Each stage runs only when its inputs and authority exist. In the current public
demo, the path stops at fixture-backed intake, readiness, mapping, and governed
explanation. Missing certified engine artifacts produce explicit blockers—not
synthetic causal effects, ROI, or budget recommendations.

## Example decision journey

Suppose a user asks: **“Help me plan next quarter's media budget.”**

MIP first clarifies the decision objective, KPI, planning horizon, channel
scope, constraints, and available data. It evaluates whether the data has the
required time, geography, controls, spend variation, and grain, then identifies
which MMM or GeoX workflow—and which governed artifacts—would be needed.

If eligible experiment evidence exists, MIP checks its quality, provenance, and
compatibility before it can become calibration input. If a promoted MMM exposes
an eligible full-panel Δμ surface, MIP can route that producer-owned artifact
into the appropriate simulation or planning workflow. Gates then determine the
`TrustReport`, confidence tier, limitations, and required human review. The
conversation layer presents the certified results and their lineage without
changing the numbers.

Today, this journey is intentionally partial: MIP can demonstrate intake,
readiness, evidence requirements, and governed refusal. The current P2 program
does not yet have the certified GeoX/MMM evidence chain or authorized planning
path needed to produce a next-quarter allocation.

## MIP, MMM, and GeoX

MIP coordinates three repositories with deliberately separate authority:

| Repository | Authority |
| --- | --- |
| **MIP** | Orchestration, governance, consumer contracts, evidence routing, trust/reporting, LLM behavior, coordination, and UX |
| **MMM** | Model fitting, diagnostics, calibration compatibility, simulation, optimization, and MMM numerical truth |
| **GeoX / panel_exp** | Experiment design, assignment, inference, governed readouts, handoff eligibility, and experiment numerical truth |

MIP consumes versioned artifacts and owner-repository evidence. It does not
recompute, silently reinterpret, or supersede MMM or GeoX analytical truth.

Three invariants define the decision boundary:

- **`TrustReport` is the sole trust verdict.**
- **`CalibrationSignal` is the sole GeoX → MMM bridge.**
- **Full-panel Δμ is the sole MMM decision surface for production planning and
  optimization.**

See the [architecture](docs/architecture/ARCHITECTURE.md),
[repository integration strategy](docs/architecture/REPO_INTEGRATION_STRATEGY.md),
and the ADRs for [full-panel Δμ](docs/adr/ADR-001-full-panel-delta-mu-decision-surface.md),
[experiments as calibration evidence](docs/adr/ADR-002-experiments-as-calibration-evidence.md),
and [LLM orchestration](docs/adr/ADR-003-llm-orchestration-over-certified-tools.md).

## Core capabilities

### Measurement and causal evidence

- Typed estimand, experiment-evidence, calibration, MMM-result, and
  decision-surface contracts are implemented.
- Data, objective, MMM, and GeoX readiness/intake workflows are implemented for
  governed and fixture-backed use.
- Static sibling-export discovery, compatibility checking, and MIP-side
  ingestion boundaries are implemented; they do not constitute live engine
  execution.
- The certified GeoX producer → provenance-linked MMM compatibility → MIP
  bridge is in progress at the program level and currently blocked.

### Decision intelligence

- Planning-input readiness, artifact-governance checks, answer eligibility,
  and response-envelope contracts are implemented.
- Fixture reports demonstrate the intended governed product shape.
- Live scenario simulation, optimizer-backed allocations, and budget
  recommendations are not currently authorized or shipped by MIP.

### Governance

- Pydantic contracts, evidence lineage, registries, deterministic release
  gates, confidence tiers, calibration audit, and `TrustReport` assembly are
  implemented and tested.
- Unsupported claims and missing prerequisites are surfaced as warnings or
  blockers rather than silently upgraded.
- Production trust assembly, real-data workflows, and production release remain
  separately gated.

### AI interaction

- Deterministic intent handling, guided intake, knowledge retrieval, dialogue
  routing, grounded fallback, explanation helpers, and a read-only
  conversational front door are implemented.
- Provider adapters/configuration exist for guarded OpenAI and Groq paths, but
  providers are disabled by default and the canonical hosted demo is
  deterministic-only. Controlled live-provider/public acceptance remains
  incomplete.
- Broader artifact-grounded follow-up and governed action handoff are still
  evolving; no LLM path receives analytical or approval authority.

## LLM Decision Layer

**The LLM decides how to interact with governed capabilities and explains
certified artifacts; it does not create causal or statistical truth.**

The LLM may guide intake, route among allowed workflows, draft configurations,
summarize diagnostics and artifacts, explain trust and uncertainty, and answer
follow-up questions grounded in approved evidence. Deterministic contracts and
routers validate those interactions and provide safe fallback behavior.

The LLM may not invent causal effects, run ungoverned inference, fit MMM by
hallucination, create calibration authority, alter numerical contract fields,
override `TrustReport`, bypass release gates, or approve production
recommendations. Human and owner-repository approvals remain explicit.

For the detailed design and current provider boundaries, see the
[LLM Decision Layer vision](docs/architecture/LLM_DECISION_LAYER_VISION.md) and
[LLM control-plane architecture](docs/architecture/MIP_LLM_CONTROL_PLANE_ARCHITECTURE_001.md).

## Current implementation state

| Capability | Current state |
| --- | --- |
| Governance and contracts | **Implemented:** typed contracts, evidence registry, gates, confidence tiers, calibration audit, and trust assembly |
| Intake and readiness | **Implemented:** deterministic objective/data intake and readiness workflows; several paths are fixture-oriented |
| Demo and UI | **Fixture/demo:** chat-first deterministic Streamlit experience over synthetic local assets; hosted publicly, not production-ready |
| Engine integration | **Partial:** MIP-side contracts, adapters, runtime boundaries, and static/fixture ingestion exist; no generally available certified live end-to-end engine path |
| Certified GeoX → MMM evidence | **Blocked/in progress:** GeoX producer certification and provenance-linked MMM compatibility evidence are incomplete; the MIP bridge remains parked |
| Planning and simulation | **Partial/planned:** readiness, governance, eligibility, and explanation contracts exist; live simulation, optimization, and recommendations are not authorized |
| LLM-backed conversation | **Partial:** guarded read-only provider seams and deterministic fallback exist; public demo providers are disabled and live acceptance is incomplete |

The machine-readable [P2 capability checkpoint ledger](docs/program/P2_CAPABILITY_CHECKPOINT_LEDGER.json)
and [current program state](docs/program/PROGRAM_CURRENT_STATE.md) are the
authoritative sources for present dependency and eligibility status. Roadmaps
describe direction, not shipped capability.

## Demo and quick start

Open the
[hosted deterministic demo](https://marketingintelligenceplatform.streamlit.app/)
or run the canonical app locally with Python 3.11+ and Poetry:

```bash
poetry install
poetry run streamlit run app/streamlit_app.py
```

The canonical app at `app/streamlit_app.py` runs in deterministic mode with
synthetic/demo fixtures by default. It requires no LLM provider, API key,
database, or external service and does not execute MMM or GeoX inference.

The older `poetry run mip-app` entrypoint is retained for backward compatibility
with the legacy workflow shell. For a deterministic JSON/CLI workflow, use
`poetry run mip-demo --help`.

The repository also contains a local deterministic FastAPI shell:

```bash
poetry run uvicorn mip.service.app:app --reload --host 127.0.0.1 --port 8000
curl http://127.0.0.1:8000/health
```

See the [public deployment record](docs/demo/PUBLIC_DEMO_DEPLOYMENT_RECORD_P9B.md),
[deterministic usage modes](docs/service/DETERMINISTIC_USAGE_MODES.md), and
[local development validation guide](docs/dev_validation_workflow.md).

## Why MIP is different

Traditional analytics systems produce models. Generic AI assistants produce
answers. MIP connects causal analytical engines to an AI decision layer through
typed evidence, authority-preserving contracts, release gates, lineage, and
explicit decision workflows. Its central product behavior is not merely to
answer—it is to show what the evidence supports, what remains uncertain, and
why a requested decision is allowed or blocked.

## Deeper documentation

- **Product and architecture:** [platform vision](docs/vision/PLATFORM_VISION.md),
  [architecture](docs/architecture/ARCHITECTURE.md), and
  [orchestration boundaries](docs/architecture/ORCHESTRATION_BOUNDARIES.md)
- **LLM Decision Layer:** [vision](docs/architecture/LLM_DECISION_LAYER_VISION.md),
  [control-plane architecture](docs/architecture/MIP_LLM_CONTROL_PLANE_ARCHITECTURE_001.md),
  and [roadmap](docs/roadmap/LLM_DECISION_LAYER_ROADMAP.md)
- **Local-first product:** [app and deployment strategy](docs/architecture/LOCAL_FIRST_APP_AND_DEPLOYMENT_STRATEGY.md)
  and [demo deployment record](docs/demo/PUBLIC_DEMO_DEPLOYMENT_RECORD_P9B.md)
- **MMM / GeoX integration:** [repository integration strategy](docs/architecture/REPO_INTEGRATION_STRATEGY.md)
  and [producer specifications](docs/integrations/MIP_SIBLING_EXPORT_PRODUCER_SPEC.md)
- **Trust and governance:** [trust architecture](docs/architecture/TRUST_ARCHITECTURE.md),
  [release gates](docs/operating_model/RELEASE_GATES.md), and
  [authority/freeze matrix](docs/program/AUTHORITY_AND_FREEZE_MATRIX.md)
- **Roadmap:** [platform roadmap](docs/roadmap/ROADMAP.md) and
  [execution sequence](docs/roadmap/ROADMAP_EXECUTION_SEQUENCE.md)
- **Current program state:** [current state](docs/program/PROGRAM_CURRENT_STATE.md),
  [P2 checkpoint ledger](docs/program/P2_CAPABILITY_CHECKPOINT_LEDGER.json), and
  [repository context index](docs/execution/REPOSITORY_CONTEXT_INDEX.md)

## License

TBD.
