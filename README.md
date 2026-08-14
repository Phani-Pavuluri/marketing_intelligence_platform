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
Because it relies heavily on observational variation, however, some channel
estimates can remain uncertain, correlated, or weakly identified.

Those uncertainties reveal where stronger causal evidence would be useful.
Targeted geo and incrementality experiments answer narrower questions about a
specific channel, campaign, population, geography, or period. When that
evidence is high quality and compatible with the model's scope, it can return
through MIP's governed calibration bridge. MMM—not MIP—then applies the eligible
evidence through MMM-owned fitting and calibration behavior.

The stronger portfolio model can support better-informed scenario and planning
decisions. Whatever remains uncertain becomes the next measurement question.
MIP coordinates this learning cycle, and AI makes it easier for users to frame
the question, follow the evidence, and understand the next action.

```text
Business / portfolio question
              ↓
MMM provides the current portfolio view
              ↓
Assess what is known confidently and what remains uncertain
              ↓
If evidence is weak, identify the material measurement gap
              ↓
Design and run a targeted experiment
              ↓
GeoX produces governed causal lift evidence
              ↓
Check quality, scope, uncertainty, freshness, and compatibility
              ↓
Eligible evidence becomes CalibrationSignal
              ↓
MMM applies calibration through MMM-owned numerical behavior
              ↓
Updated, eligible MMM evidence supports scenarios and planning
              ↓
Observe remaining uncertainty or new business questions
              ↓
Identify the next measurement gap ───────────────────────────┐
              ↑                                              │
              └──────────────────────────────────────────────┘
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
AI + MIP understand the objective
  ↓
Clarify KPI, channels, geography / population, time horizon,
constraints, and available data or evidence
  ↓
Build the required measurement or decision plan
  ↓
┌────────────────────────┬────────────────────────┬────────────────────────┐
│ Experiment / GeoX path │ MMM path               │ Existing-evidence path │
│                        │                        │                        │
│ Check experiment and   │ Check data and model   │ Retrieve prior         │
│ data readiness         │ readiness              │ experiments            │
│          ↓             │          ↓             │          ↓             │
│ Design / assignment    │ MMM-owned fitting and  │ Retrieve eligible MMM  │
│ when needed            │ diagnostics            │ and model artifacts    │
│          ↓             │          ↓             │          ↓             │
│ GeoX inference         │ Current portfolio      │ Retrieve prior trust   │
│          ↓             │ measurement            │ and provenance         │
│ Governed experiment    │          ↓             │          ↓             │
│ readout                │ Eligible MMM decision  │ Decide whether existing│
│                        │ surfaces               │ evidence answers the Q │
└────────────┬───────────┴────────────┬───────────┴────────────┬───────────┘
             └────────────────────────┼────────────────────────┘
                                      ↓
Normalize scope and estimand; check lineage, freshness, uncertainty,
quality, and compatibility
                                      ↓
Determine whether experiment evidence is calibration-eligible
  → if eligible: CalibrationSignal enters MMM-owned calibration behavior
  → if not eligible: preserve relevant evidence as decision context
                                      ↓
Assemble trust and evaluate decision eligibility
                                      ↓
┌──────────────────────┬────────────────────────┬─────────────────────────┐
│ Measurement answer   │ Planning answer        │ Evidence insufficient   │
│ Explain causal lift  │ Compare eligible       │ Identify what is missing│
│ and supporting       │ full-panel Δμ scenario │ and recommend additional│
│ evidence             │ surfaces               │ measurement / experiment│
└──────────┬───────────┴────────────┬───────────┴────────────┬────────────┘
           └────────────────────────┼────────────────────────┘
                                    ↓
AI + MIP explain the result, evidence used, uncertainty, trade-offs,
blockers, and recommended next action
                                    ↓
Return the result to the continuous learning loop
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
