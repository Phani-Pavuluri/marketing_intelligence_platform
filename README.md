# Marketing Intelligence Platform (MIP)

MIP connects marketing mix modeling (MMM) and causal experimentation into a
continuous measurement and planning system. MMM provides the portfolio view;
targeted experiments provide stronger causal evidence where observational
measurement is uncertain. MIP carries compatible learning into future
measurement and planning, while AI helps people navigate the workflow without
becoming the analytical authority.

**Try the public demo:**
[marketingintelligenceplatform.streamlit.app](https://marketingintelligenceplatform.streamlit.app/)

> **Current version:** The public experience demonstrates the governed workflow
> with synthetic/demo data while live analytical and LLM integrations continue
> to mature.

## Why MIP exists

Marketing planning starts with the broad portfolio view. MMM helps teams
understand how channels work together and compare choices across the media mix.
Because it learns largely from historical, observational variation, some
important channel and planning questions can remain uncertain.

MIP makes that uncertainty actionable. If existing evidence is sufficient, a
team can move toward scenario analysis and planning. If stronger causal
evidence would materially improve the decision, MIP can route a narrower
question to GeoX for a targeted experiment. Compatible experimental learning
can then strengthen future MMM measurement and the portfolio view used for
planning.

MIP coordinates this cycle; GeoX and MMM retain authority over their own
numerical work. The cycle ends in a business decision—not another analysis for
its own sake—and begins again only when a new question or material uncertainty
requires it.

```text
Business / portfolio question
            ↓
MMM provides the portfolio view
            ↓
Where does material uncertainty remain?
       ┌──────────────┴──────────────┐
       │                             │
Evidence sufficient          Stronger causal
       │                      evidence needed
       ↓                             ↓
Scenario / planning          GeoX targeted experiment
                                     ↓
                              Causal lift evidence
                                     ↓
                             Compatible learning
                              informs future MMM
                                     ↓
                             Updated portfolio view
                                     ↓
                              Scenario / planning
       └──────────────┬──────────────┘
                      ↓
               Decision / action
                      ↓
        New question or material uncertainty
                      ↓
 Return to evidence assessment / routing when needed
```

The next route may use existing evidence, refresh MMM, require more data, or
engage GeoX; uncertainty does not automatically require an experiment.

## What can you do with MIP?

Bring MIP a decision or measurement job—not a choice of internal architecture.
Current availability varies by capability; see
[implementation maturity](#current-version-and-implementation-maturity).

| User job | Questions MIP helps organize |
| --- | --- |
| **Measure** | Is this channel actually incremental? Do we already have enough evidence to answer? |
| **Experiment** | Where is additional measurement most valuable? What targeted experiment would address weak evidence? |
| **Connect the learning** | What does a completed experiment mean for the broader measurement system? Can compatible evidence inform future MMM measurement? |
| **Plan** | What happens under a different spend scenario? Is cross-channel budget reallocation supportable? |
| **Decide the next action** | Is the evidence trustworthy enough for this decision? What data, measurement, or experiment should come next? |

MIP keeps the question, evidence, limitations, and next action connected even
when the analytical work spans different systems.

## How MIP works

The experience begins with a business question, not a model configuration. The
same five stages apply whether existing evidence is enough or new analytical
work is needed.

```text
1. FRAME THE QUESTION
   Business question → objective, KPI, channels, geography / population,
   horizon, constraints, available data and evidence
                                ↓
2. ROUTE TO THE RIGHT PATH
   ┌────────────────────┬────────────────────┬─────────────────────┐
   │ GeoX / Experiment  │ MMM                │ Existing Evidence   │
   │ readiness          │ readiness          │ retrieve prior      │
   │ → design           │ → fit / diagnose   │ evidence/artifacts  │
   │ → inference        │ → portfolio view   │ → provenance/trust  │
   │ → governed lift    │ → decision surface │ → assess sufficiency│
   └──────────┬─────────┴──────────┬─────────┴──────────┬──────────┘
              └────────────────────┼─────────────────────┘
                                   ↓
3. RECONCILE AND GOVERN EVIDENCE
   Scope / estimand alignment
   → quality, provenance, freshness, uncertainty and compatibility
   → calibration eligibility when relevant
     (eligible GeoX evidence crosses to MMM only as CalibrationSignal)
   → TrustReport / decision eligibility
                                   ↓
4. ANSWER THE USER NEED
   ┌───────────────────┬───────────────────┬──────────────────────┐
   │ Measurement       │ Planning          │ Evidence insufficient│
   │ causal evidence,  │ eligible scenario │ explain what is       │
   │ uncertainty and   │ comparison,       │ missing; identify the │
   │ support           │ trade-offs/context│ right next measurement│
   └─────────┬─────────┴─────────┬─────────┴──────────┬───────────┘
             └───────────────────┼────────────────────┘
                                 ↓
5. EXPLAIN AND CONTINUE LEARNING
   AI + MIP explain evidence used, uncertainty, blockers, trade-offs,
   trust / eligibility and the recommended next action
                                 ↓
   A new question or material uncertainty may return to assessment / routing
```

GeoX owns experiment design, assignment, inference, and causal-lift truth. MMM
owns fitting, diagnostics, calibration application, simulation, optimization,
and MMM numerical truth. Existing evidence may answer the question without
forcing a new model run or experiment; MIP coordinates and explains these
governed paths rather than replacing their analytical authority.

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

### D. Measurement strategy / cold start

**“We want to evaluate a new channel. What should we measure first?”**

```text
Business objective
  → clarify the KPI, geography, and decision to be made
  → inspect historical data and existing evidence
  → assess whether MMM, an experiment, or more data collection is feasible
  → identify missing information
  → recommend the next measurement workflow
```

Together, the journeys form the broader loop: **choose what to measure →
experiment → model → plan → choose the next measurement**.

## Core capabilities

| Capability | What MIP does | Why it matters |
| --- | --- | --- |
| Business decision framing | Clarifies the objective, KPI, channels, geography, time horizon, and constraints | Starts from the decision the user needs to make rather than a model configuration |
| Data and evidence readiness | Checks required history, grain, spend, outcomes, controls, and available analytical artifacts | Exposes missing or unusable inputs before they undermine the workflow |
| Measurement-gap and workflow selection | Identifies the material uncertainty and routes to existing evidence, MMM, GeoX, or additional data collection | Directs effort toward the evidence most likely to improve the decision |
| Incrementality and targeted experimentation | Coordinates readiness and governed handoffs while GeoX owns design, assignment, inference, and lift | Turns a narrow causal question into usable experiment evidence without moving numerical truth into MIP |
| Evidence reconciliation and calibration eligibility | Checks scope, estimand, quality, uncertainty, freshness, lineage, and compatibility throughout the workflow, then passes only eligible evidence through the governed bridge | Adds causal anchors without forcing every experiment into a broader model |
| MMM portfolio measurement | Routes eligible data and calibration evidence to MMM-owned fitting, diagnostics, and portfolio measurement | Builds or refreshes the cross-channel view needed for planning while MMM retains numerical authority |
| Scenario and budget planning | Coordinates baselines, candidate plans, constraints, and eligible MMM-owned decision surfaces | Supports counterfactual trade-offs using producer-owned full-panel Δμ results |
| Trust and decision eligibility | Applies governance and release checks throughout, then assembles the sole trust verdict for the proposed use | Prevents weak, stale, or mismatched evidence from silently becoming decision-grade |
| Explanation and next action | Connects the evidence, explains results and blockers, and recommends the next measurement or decision step | Makes sophisticated workflows usable while keeping uncertainty and authority visible |

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

### Hosted demo — try this first

Open the
[hosted deterministic demo](https://marketingintelligenceplatform.streamlit.app/).
It uses synthetic fixtures and no production data. It demonstrates governed
intake, advisory, readiness, evidence routing, profiling, and calibration
mapping; it does not run live MMM, GeoX, or LLM inference.

A useful first review takes only a few minutes:

1. In **Measurement copilot**, try “Should I use MMM, GeoX, or both?” to see how
   the deterministic assistant explains method choice and its limits.
2. Open the preloaded **SaaS growth-planning example** and move through its
   measurement stages. Inspect the evidence, uncertainty, readiness, blocking
   reasons, and required next artifact rather than treating fixture outputs as
   live analysis.
3. Switch to **Advanced tools** and compare a readiness report or calibration
   mapping case that succeeds with one that is blocked. Cold-start advisory,
   demo profiling, and intake-overview examples are available there too.

The public app accepts no file uploads, persists no uploaded data, calls no
external service, and has no configured LLM provider. Its responses are
deterministic governed demonstrations—not production measurement decisions.

### Local prerequisites and installation

You need Git, [Poetry](https://python-poetry.org/docs/#installation), and Python
`>=3.11,<4.0`. Clone and install the project from a clean directory:

```bash
git clone https://github.com/Phani-Pavuluri/marketing_intelligence_platform.git
cd marketing_intelligence_platform
poetry install
```

### Run the canonical Streamlit app

```bash
poetry run streamlit run app/streamlit_app.py
```

Streamlit normally opens `http://localhost:8501`. The canonical app runs with
the same synthetic fixtures as the hosted demo. After launch:

1. Use a starter prompt to understand available workflows or required data.
2. Activate the SaaS sample journey and inspect why later planning steps remain
   blocked.
3. Open **Advanced tools** to compare cold-start, readiness, calibration,
   profiling, and intake cases.

Deterministic mode requires no LLM provider, API key, database, or external
service. It persists no uploaded data and executes neither live MMM fitting nor
live GeoX inference.

### Use the deterministic FastAPI interface

Developers and integrators can inspect the shared deterministic workflow layer
through a local API:

```bash
poetry run uvicorn mip.service.app:app --reload --host 127.0.0.1 --port 8000
```

In another terminal, check service metadata and run a fixture-backed readiness
assessment:

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/version
curl -X POST http://127.0.0.1:8000/readiness/assess \
  -H 'Content-Type: application/json' \
  -d '{"sample_key":"national_mmm_ready_geox_blocked"}'
```

The service also exposes interactive OpenAPI documentation at
`http://127.0.0.1:8000/docs`.

| Method and route | Deterministic request body | Purpose |
| --- | --- | --- |
| `POST /advisory/cold-start` | `{"sample_key":"dtc_skincare_ecommerce"}` | Build a fixture-backed advisory plan |
| `POST /readiness/assess` | `{"sample_key":"national_mmm_ready_geox_blocked"}` | Report structural workflow readiness and blockers |
| `POST /calibration/map` | `{"sample_key":"valid_governed_evidence"}` | Demonstrate governed calibration mapping |
| `POST /intake/overview` | `{"example_key":"national_mmm_diagnostic"}` | Explain deterministic workflow routing |

These routes are advisory and non-production: their governance responses report
that measurement-engine execution, LLMs, external services, persistence, and
production connectors are disabled.

### Use the Python package

Notebooks and Python applications can call the same workflow layer directly:

```python
from mip.service.workflows import run_readiness_assess

result = run_readiness_assess("national_mmm_ready_geox_blocked")
print(result.model_dump_json(indent=2))
```

### CLI and contributor validation

The existing CLI runs the deterministic JSON-file workflow; inspect its input
options with:

```bash
poetry run mip-demo --help
```

The older `poetry run mip-app` entrypoint remains for backward compatibility
with the legacy Streamlit workflow shell. The root
`app/streamlit_app.py` command is canonical.

Contributors can use the repository's existing validation targets:

```bash
make validate-host              # run the validation suite on the host
make validate                   # run the Docker-backed validation suite
make validate-docker            # explicit alias for Docker-backed validation
make validate-public-deployment # verify public-demo installation/readiness
```

### Current limitations

The hosted and local experiences are deterministic demonstrations. They do not
provide live certified GeoX execution, a generally available live MMM fitting
or calibration path, production budget optimization or recommendations, real
production-data integration, or a fully live LLM-backed workflow. See
[implementation maturity](#current-version-and-implementation-maturity) for the
current boundary.

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
