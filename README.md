# Marketing Intelligence Platform (MIP)

MIP is a causal marketing intelligence platform and control plane that connects
incrementality measurement, experimentation, marketing mix modeling (MMM),
calibration, budget and scenario planning, governed decision workflows, and
conversational AI.

**Try the public demo:**
[marketingintelligenceplatform.streamlit.app](https://marketingintelligenceplatform.streamlit.app/)

> **Current version:** The public experience demonstrates the governed workflow
> with synthetic/demo data while live analytical and LLM integrations continue
> to mature.

Experiments strengthen what MMM can learn. MMM reveals where uncertainty
matters for planning. MIP coordinates that learning loop, while AI makes the
workflow accessible.

## Why MIP exists

Marketing teams rarely have a single source of causal truth. MMM measures the
portfolio: it helps explain how channels work together and supports planning
across the full media mix. But because MMM learns from observational data, some
channel estimates can remain uncertain, correlated, or sensitive to modeling
assumptions.

Controlled geo and incrementality experiments answer a different kind of
question. They can provide stronger causal evidence about the lift created by a
specific channel, campaign, population, geography, or period—but they are
narrower than the portfolio view and do not answer every planning question.

MIP connects these two evidence systems instead of leaving experiment results
in one workflow and planning models in another. Compatible experiment evidence
can provide causal anchors for MMM. In the other direction, weak or uncertain
MMM evidence can reveal where a targeted experiment would be most valuable.

```text
Measure
   ↓
Identify uncertainty
   ↓
Experiment
   ↓
Learn causal lift
   ↓
Calibrate / improve MMM
   ↓
Plan
   ↓
Identify the next measurement gap ──────────┐
   ↑                                        │
   └────────────────────────────────────────┘
```

The result is a continuous learning system: stronger causal anchoring where
evidence is compatible, better-informed channel-response beliefs, clearer
planning confidence, and an explicit path to the next measurement action.
Experiments do not automatically recalibrate a model; quality, uncertainty,
freshness, and compatibility must be established first.

Functionally, **GeoX provides experiment and incrementality truth**, **MMM
provides portfolio measurement and planning truth**, and **MIP connects both
into one governed decision workflow**.

## What can you do with MIP?

The product connects a progression of questions that teams usually answer in
separate tools:

```text
Measure channel incrementality
        ↓
Run targeted experiments where evidence is weak
        ↓
Bring compatible lift evidence back into MMM
        ↓
Improve channel-response understanding
        ↓
Compare alternative spend scenarios
        ↓
Plan or reallocate next-quarter budget
```

That progression supports questions such as:

- Is this channel incremental, and what lift did the campaign cause?
- Where should we run an experiment next?
- How should this experiment change what the MMM believes about the channel?
- Can we move budget between channels?
- What happens if we follow a different spend plan?
- How should we plan next quarter?

MIP turns these from isolated analyses into one learning and decision workflow:
measure, learn, update the evidence base, plan, and decide what to measure next.

## How MIP works

The experience begins with a business question, not a model configuration.

```text
User asks a business question
            ↓
MIP + AI understand the objective
            ↓
Ask clarifying questions and identify missing data
            ↓
Choose the measurement or planning workflow
            ↓
   ┌────────────────┬──────────────────┬──────────────────┐
   │ Experiment path│ MMM path         │ Existing evidence│
   │ GeoX design /  │ measurement /    │ prior experiments│
   │ incrementality │ scenario analysis│ and model outputs│
   └────────┬───────┴─────────┬────────┴─────────┬────────┘
            └─────────────────┼──────────────────┘
                              ↓
Reconcile evidence and check compatibility, quality, and trust
                              ↓
      ┌───────────────────────┴────────────────────────┐
      │ Evidence is sufficient   Evidence is incomplete│
      │ → support the decision   → identify what is     │
      │                          missing / what to test  │
      └───────────────────────┬────────────────────────┘
                              ↓
Explain the result, uncertainty, trade-offs, and next action
```

The conversational layer can ask about the KPI and business objective,
channels, geography, population, time horizon, available spend/outcome/control
data, planning constraints, and any existing experiments or models. It then
routes to the appropriate governed workflow rather than trying to answer every
question from language alone.

## Example decision journeys

These journeys describe how the platform connects evidence and decisions. The
[current maturity](#current-version-and-implementation-maturity) section below
distinguishes what is implemented today from the live integrations still in
progress.

### A. Channel incrementality

**“Is this channel actually incremental?”**

```text
Question
  → inspect available evidence
  → determine whether usable causal evidence already exists
  → use or recommend an appropriate experiment
  → obtain governed lift evidence
  → explain the result, uncertainty, and limits
```

If the evidence is missing or too weak, MIP should make that gap actionable:
what needs to be measured, for which channel or population, and why an
experiment would improve the decision.

### B. Experiment → MMM learning

**“We finished an experiment. What does this mean for our MMM?”**

```text
Experiment result
  → check channel, KPI, geography, population, timing, and estimand compatibility
  → determine whether the evidence is eligible for calibration
  → construct governed calibration evidence
  → MMM consumes eligible calibration through its own numerical behavior
  → future measurement and planning can reflect the stronger evidence
```

Raw experiment output never edits model coefficients directly. The only
GeoX-to-MMM bridge is `CalibrationSignal`, and MMM remains responsible for
compatibility decisions and the numerical application of calibration.

### C. Budget planning

**“How should I plan next quarter?”**

When the required artifacts and approvals exist:

```text
Planning objective
  → inspect the latest eligible MMM and experiment-informed evidence
  → define baseline and candidate spend plans
  → invoke MMM-owned simulation
  → compare full-panel Δμ decision surfaces
  → evaluate constraints and trust
  → explain trade-offs and the recommended next step
```

The alternate path is just as important:

```text
Evidence is insufficient
  → identify the material uncertainty
  → recommend additional measurement or a targeted experiment
  → feed the new learning into a future planning cycle
```

Together, the journeys form the broader loop: **experiment → model → planning →
next experiment**.

## Core capabilities

| Capability | What MIP does | Why it matters |
| --- | --- | --- |
| Objective and data guidance | Clarifies the decision, KPI, grain, history, controls, geography, and required inputs | Starts with the business decision and exposes missing information early |
| Channel incrementality | Connects a channel question to existing causal evidence or an appropriate experiment path | Separates causal lift from descriptive attribution |
| Experiment orchestration | Coordinates readiness, evidence intake, and governed handoff to/from GeoX | Makes targeted learning part of the measurement workflow |
| MMM measurement | Routes eligible data and artifacts to MMM-owned measurement and diagnostics | Preserves a portfolio view across channels without moving model truth into MIP |
| Experiment-to-MMM calibration | Checks whether experiment evidence is suitable to inform MMM and passes eligible evidence through the governed bridge | Adds causal anchors without blindly forcing narrow experiments into a broader model |
| Evidence compatibility and trust | Checks quality, uncertainty, freshness, lineage, scope, and release conditions | Prevents weak or mismatched evidence from silently becoming decision-grade |
| Scenario planning | Coordinates baseline/candidate plans and eligible MMM decision surfaces | Supports counterfactual trade-offs using producer-owned numerical results |
| Measurement-gap detection | Identifies uncertainty or missing evidence and suggests what should be measured next | Turns “we do not know” into a concrete learning agenda |
| Conversational decision support | Guides intake, connects relevant evidence, and explains results, blockers, and next actions | Makes sophisticated measurement workflows usable without hiding their limits |

### Technical foundations

MIP's checks and balances are implemented through typed contracts and evidence
lineage, deterministic routing and validation, compatibility and release gates,
and explicit confidence tiers. `CalibrationSignal` carries eligible experiment
evidence into MMM; `TrustReport` records the trust verdict; full-panel Δμ is the
counterfactual surface used for MMM planning decisions. These artifacts keep
the user experience explainable without turning prose into analytical truth.

## How AI fits into MIP

**The LLM is the conversational interface and orchestrator; it is not the
causal measurement engine.**

It can:

- understand the user's objective and ask clarifying questions;
- request missing information or data;
- route to governed workflows and select approved tools;
- summarize diagnostics and connect relevant artifacts; and
- explain results, blockers, uncertainty, trade-offs, and next actions.

It cannot:

- invent causal lift or independently calculate GeoX inference;
- hallucinate an MMM model or alter producer-owned numbers;
- bypass experiment-compatibility or calibration requirements;
- override `TrustReport`; or
- authorize production recommendations.

The LLM proposes and explains; deterministic tools, contracts, gates, and human
approvals decide what is allowed. See the
[LLM Decision Layer vision](docs/architecture/LLM_DECISION_LAYER_VISION.md) and
[LLM control-plane architecture](docs/architecture/MIP_LLM_CONTROL_PLANE_ARCHITECTURE_001.md).

## Architecture and trust model

The analytical and orchestration responsibilities remain deliberately
separate:

```text
GeoX → experiment design, inference, and experiment numerical truth
MMM  → model fitting, calibration application, simulation, optimization,
       and MMM numerical truth
MIP  → orchestration, governance, decision workflows, evidence routing,
       trust/reporting, UX, and LLM behavior
```

MIP consumes versioned, owner-produced artifacts. It does not edit MMM
coefficients, recompute GeoX lift, or supersede either engine's analytical
truth.

Three invariants define the decision boundary:

- **`TrustReport` is the sole trust verdict.**
- **`CalibrationSignal` is the sole GeoX → MMM bridge.**
- **Full-panel Δμ is the sole MMM decision surface for production planning and
  optimization.**

Experiment evidence must pass quality, uncertainty, freshness, compatibility,
and governance checks before it can inform MMM. See the
[architecture](docs/architecture/ARCHITECTURE.md),
[repository integration strategy](docs/architecture/REPO_INTEGRATION_STRATEGY.md),
[trust architecture](docs/architecture/TRUST_ARCHITECTURE.md), and ADRs for
[full-panel Δμ](docs/adr/ADR-001-full-panel-delta-mu-decision-surface.md),
[experiments as calibration evidence](docs/adr/ADR-002-experiments-as-calibration-evidence.md),
and [LLM orchestration](docs/adr/ADR-003-llm-orchestration-over-certified-tools.md).

## Current version and implementation maturity

| Capability | Current state |
| --- | --- |
| Governance and contracts | **Implemented:** typed contracts, evidence registry, gates, confidence tiers, calibration audit, and trust assembly |
| Objective, data, and readiness guidance | **Implemented:** deterministic intake and readiness workflows; several paths use fixtures |
| Demo and UI | **Deterministic/demo:** chat-first Streamlit experience over synthetic local assets; hosted publicly and not production-ready |
| Engine integration | **Partial/in progress:** MIP-side contracts, adapters, runtime boundaries, and static/fixture ingestion exist; a generally available certified live end-to-end engine path does not |
| Certified GeoX → MMM evidence | **Blocked/in progress:** GeoX producer certification and provenance-linked MMM compatibility evidence are incomplete; the MIP bridge remains parked |
| Planning and simulation | **Partial/planned:** readiness, governance, eligibility, and explanation contracts exist; live simulation, optimization, and recommendations are not authorized |
| LLM-backed conversation | **Partial/in progress:** guarded read-only provider seams and deterministic fallback exist; public-demo providers are disabled and live acceptance is incomplete |

The [P2 capability checkpoint ledger](docs/program/P2_CAPABILITY_CHECKPOINT_LEDGER.json)
and [current program state](docs/program/PROGRAM_CURRENT_STATE.md) are the
authoritative sources for current dependency and eligibility status. Roadmaps
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
synthetic/demo fixtures. It requires no LLM provider, API key, database, or
external service and does not execute MMM or GeoX inference.

The older `poetry run mip-app` entrypoint remains for backward compatibility
with the legacy workflow shell. For the deterministic JSON/CLI workflow, use
`poetry run mip-demo --help`.

The repository also includes a local deterministic FastAPI shell:

```bash
poetry run uvicorn mip.service.app:app --reload --host 127.0.0.1 --port 8000
curl http://127.0.0.1:8000/health
```

See the [public deployment record](docs/demo/PUBLIC_DEMO_DEPLOYMENT_RECORD_P9B.md),
[deterministic usage modes](docs/service/DETERMINISTIC_USAGE_MODES.md), and
[local development validation guide](docs/dev_validation_workflow.md).

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
