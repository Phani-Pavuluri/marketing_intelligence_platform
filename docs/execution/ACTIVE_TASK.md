# Active Task

**Status:** ready_for_review
**Task ID:** `MIP_ROOT_README_PRODUCT_STORY_REFINEMENT_001`
**Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
**Local path:** `/Users/phani/Desktop/marketing_intelligence_platform`
**Pre-authoring base:** `fb3d4448c29eea5387e102777bf6bc1981ad6208`
**Authorization provenance:** `fc5124e88d6f7bae58236eaa07d06c45d7d3ef16`
**Implementation commit:** `4b942e94d2da6347b3f89afd7387b4fd1c3823c1`
**Feature branch:** `docs/mip-root-readme-product-story-refinement-001`
**Execution mode:** `branch_and_fast_forward`
**Risk tier:** Tier 1 — routine repository-local documentation
**Compatibility or migration policy:** `not_applicable`
**Capability authority changed:** `false`
**Unresolved execution-blocking design questions:** none

## Primary outcome

Refine only the root `README.md` so it tells a compelling, easy-to-follow
product and causal-learning story before introducing implementation detail and
governance terminology. A marketer, technical leader, or senior data scientist
should quickly understand how MIP connects causal experimentation, GeoX, MMM,
calibration, planning, and an AI-guided workflow into a continuous learning
system that improves marketing decisions over time.

This is one independently reviewable outcome because it refines one existing
product-navigation surface without changing product behavior, contracts,
governance, architecture, code, tests, or authority. Splitting the narrative
flow, journeys, and capability presentation would leave an incoherent front
door rather than a useful standalone checkpoint.

## Authorization provenance convention

`authorization_head_sha` identifies
`fc5124e88d6f7bae58236eaa07d06c45d7d3ef16`, the first commit on `main` that
establishes this authorized task contract. That commit contained a null
self-reference; this subsequent metadata-only commit records the first commit
SHA. The recorded SHA is immutable authorization provenance and must never be
replaced by the metadata-finalization commit, feature-branch head,
implementation head, or review head.

Create the feature branch only from synchronized metadata-finalized `main`.
That finalized branch baseline must descend from immutable authorization
provenance, and the intervening diff may contain only:

- `docs/execution/ACTIVE_TASK.md`
- `docs/execution/EXECUTION_STATE.json`
- `docs/execution/LATEST_COMPLETION_REPORT.md`

No README or implementation change may precede feature-branch creation.
Execution must resolve the finalized branch baseline from Git and must not
infer or retroactively change authorization provenance.

## Owned and prohibited paths

The sole implementation-owned path is:

- `README.md`

Lifecycle updates to the three stable execution files are permitted only as
required by the repository execution standard to record `in_progress`,
`blocked`, or `ready_for_review` state and completion evidence. They do not
expand the implementation outcome.

Prohibited changes include all product/source code, tests, fixtures, apps,
contracts, architecture documents, roadmaps, program ledger/state,
coordination state, governance or execution standards, dependencies, CI,
Docker, data, and sibling repositories. Do not modify MMM or GeoX.

## Editorial principle and required flow

The README must explain before it qualifies and use business/measurement
language before software terminology. The target progression is:

1. **What is MIP?**
2. **Why MIP exists**
3. **What can you do with MIP?**
4. **How MIP works**
5. **Example decision journeys**
6. **Core capabilities**
7. **How AI fits into MIP**
8. **Architecture and trust model**
9. **Current version / implementation maturity**
10. **Demo and quick start**
11. **Deeper documentation**
12. **License**

Exact heading wording may vary, but the narrative must progress from marketing
problem → causal learning loop → user outcomes → workflow → journeys →
capabilities → AI role → technical architecture/trust → current maturity →
demo/docs. Do not lead with implementation caveats, fixture limitations,
contract names, or repository governance.

## Required product story

### Opening

Preserve a concise definition of MIP as a causal marketing intelligence
platform/control plane connecting incrementality measurement, experimentation,
MMM, calibration, budget/scenario planning, governed decision workflows, and
conversational AI. Keep the hosted demo prominent.

Replace the current large opening disclaimer with one short, visually secondary
current-version note: the public experience demonstrates the governed workflow
with synthetic/demo data while live analytical and LLM integrations continue
to mature. Do not describe MIP as merely a portfolio workflow.

### Why MIP exists: GeoX/MMM learning loop

Explain in plain language that MMM provides portfolio-level channel measurement
and planning but observational estimates can contain uncertainty or bias;
controlled geo/incrementality experiments provide stronger causal evidence but
usually answer narrower channel, geography, population, or period questions.
MIP connects these systems so compatible experiment evidence can inform MMM
channel-response beliefs, while model uncertainty can identify where targeted
experimentation is most valuable.

Make this loop glanceable:

```text
Measure
→ identify uncertainty
→ experiment
→ learn causal lift
→ calibrate / improve MMM
→ plan
→ identify the next measurement gap
```

Explain the conceptual benefits—stronger causal anchoring, correction of weak
or confounded estimates where evidence is compatible, better-informed response
and contribution beliefs, and improved planning confidence—without claiming
automatic calibration. Introduce GeoX as causal experiment/incrementality
truth, MMM as portfolio measurement/planning truth, and MIP as the governed
workflow connecting them. Repository ownership is not the main story here.

### Progressive user outcomes

Replace the disconnected question list with a progression from channel
incrementality through targeted experiments, compatible experiment-to-MMM
learning, improved response understanding, scenario comparison, and
next-quarter planning. Representative questions should include a concise
selection from:

- Is this channel incremental?
- What lift did the campaign cause?
- Where should we run an experiment next?
- How should this experiment change what the MMM believes about this channel?
- Can we move budget between channels?
- What happens under a different spend plan?
- How should we plan next quarter?

Follow the progression with a short statement that MIP connects these questions
into one learning and decision workflow. Avoid contract-heavy jargon here.

### How MIP works

Make this a centerpiece visual that begins with the user's business question.
Show MIP/AI understanding the objective, asking clarifying questions,
identifying missing data, selecting the appropriate measurement/planning path,
using GeoX/MMM/existing evidence as appropriate, checking compatibility and
trust, supporting a decision or identifying the missing evidence, and
explaining results, uncertainty, and next action.

The conversational layer may clarify KPI, objective, channels, geography, time
horizon, spend/outcome/control data, constraints, and existing experiments or
models. Use marketer-friendly labels first and visually show the GeoX/MMM
branch where useful. `CalibrationSignal` and `TrustReport` must not dominate
this visual.

### Example decision journeys

Replace the single long journey with at least three short, scannable journeys:

1. **Channel incrementality — “Is this channel actually incremental?”**
   Inspect evidence → determine whether causal evidence exists → use or
   recommend an appropriate experiment → obtain governed lift evidence →
   explain result and uncertainty.
2. **Experiment → MMM learning — “We finished an experiment. What does this
   mean for our MMM?”** Check channel, KPI, geography, population, timing, and
   estimand compatibility → determine calibration eligibility → construct
   governed calibration evidence → MMM consumes eligible calibration → future
   MMM measurement/planning can reflect stronger evidence. Raw experiment
   outputs never directly edit coefficients; `CalibrationSignal` remains the
   sole GeoX-to-MMM bridge and MMM owns calibration behavior.
3. **Budget planning — “How should I plan next quarter?”** Inspect eligible MMM
   and experiment-informed evidence → define baseline/candidate spend → invoke
   producer-owned simulation → compare full-panel Δμ → evaluate constraints
   and trust → explain trade-offs and the next step. Also show the alternate
   insufficient-evidence path to targeted measurement/experimentation.

Together the journeys must communicate experiment → model → planning → next
experiment without presenting target/live paths as generally available today.

### Core capabilities

Completely replace implementation-jargon bullets with a reader-oriented table:

| Capability | What MIP does | Why it matters |
| --- | --- | --- |

Cover objective/data guidance, channel incrementality and experiment
orchestration, MMM measurement, experiment-to-MMM calibration, compatibility
and trust, scenario planning, measurement-gap detection, and conversational
decision support. Use plain language first.

A short **Technical foundations** subsection may then explain typed contracts,
lineage, compatibility gates, `CalibrationSignal`, `TrustReport`, full-panel
Δμ, and deterministic routers/validation. Explain the purpose of these checks
and balances rather than listing internal classes or package surfaces.

### How AI fits into MIP

Frame the LLM as the conversational interface and orchestrator, not the causal
measurement engine. It may understand objectives, ask clarifying questions,
request missing information/data, route to governed workflows, select approved
tools, summarize diagnostics/evidence, connect artifacts, and explain results,
blockers, uncertainty, and next actions.

It may not invent causal lift, independently calculate GeoX inference,
hallucinate an MMM model, alter producer-owned numerical truth, bypass
compatibility/calibration requirements, override `TrustReport`, or authorize
production recommendations. Keep this conceptual before linking to detailed
LLM documentation.

### Architecture, maturity, and navigation

Place detailed architecture/trust boundaries after the journeys, capabilities,
and AI explanation. Use a concise authority model:

```text
GeoX → experiment numerical truth
MMM  → model / simulation / optimization numerical truth
MIP  → orchestration / governance / decision workflow / UX / LLM behavior
```

Then state the exact invariants. Keep one compact maturity table distinguishing
implemented, deterministic/demo, partial/in-progress, and planned/blocked
capabilities. Disclose the public demo's current limitations once, concisely,
rather than repeatedly. Preserve verified demo/quick-start commands and clean
canonical documentation navigation.

Remove the standalone “Why MIP is different” section unless the final rewrite
proves a distinct need. Prefer one early callout conveying that experiments
strengthen what MMM can learn, MMM exposes uncertainty relevant to planning,
and MIP coordinates that loop while AI makes it accessible.

## Factual constraints and preserved invariants

- Experiment evidence must satisfy quality, compatibility, uncertainty,
  freshness, and governance requirements before it can inform MMM.
- `CalibrationSignal` remains the sole GeoX → MMM bridge.
- MMM owns calibration application, model fitting, simulation, optimization,
  and all MMM numerical truth.
- GeoX owns experiment design/inference and experiment numerical truth.
- MIP does not edit coefficients or recompute/supersede analytical truth.
- `TrustReport` remains the sole trust verdict.
- Full-panel Δμ remains the sole MMM decision surface for production planning
  and optimization.
- Live planning, engine, and LLM paths must not be described as generally
  available unless synchronized evidence proves that claim.
- The public demo's deterministic/synthetic maturity is disclosed accurately
  but must not overwhelm the product story.
- The hosted demo, canonical local command, legacy `mip-app` compatibility
  reference required by tests, API shell command, and valid canonical links
  must remain accurate.

## Acceptance evidence and failure semantics

The first half of the final README must let a non-specialist understand the
complete product idea and continuous causal-learning loop without reading the
implementation-status section. The README must remain skimmable, use short
paragraphs, and use diagrams/tables only where they clarify the story.

Execution must provide deterministic evidence that:

- the major headings exist in the intended order;
- the learning loop and three required journeys are present;
- all relative Markdown links resolve to repository paths;
- hosted-demo links and displayed commands remain valid;
- current/demo/in-progress/planned claims remain distinguishable;
- the three authority invariants remain exact;
- the implementation-content diff is limited to `README.md`;
- no P2 sequence or product/analytical/sibling/capability authority changed.

A missing required journey, broken link, stale command, overstated live
capability, weakened invariant, scope violation, or failed required validation
is a fail-closed blocker. Do not repair source, tests, architecture, roadmap,
program, or governance files under this task.

## Required Tier-1 validation

Execution, exact-head review, and post-fast-forward validation require:

```bash
git diff --check
git diff -- README.md
find tests -type f \( -iname '*readme*.py' -o -iname '*documentation*.py' -o -iname '*docs*.py' \) -print
```

Also run a programmatic relative-link check; verify the intended major-heading
order and the three journeys; verify documented entrypoints/commands against
the working tree and package configuration; run relevant existing
README/documentation tests, including README-sensitive app/deployment tests;
JSON-parse execution state after lifecycle updates; verify the implementation
diff is only `README.md`; and verify the P2 ledger/authority flags are
unchanged.

Full pytest, Ruff, mypy, and Docker-backed `make validate` are `not_required`
for this Tier-1 Markdown-only surface unless synchronized repository rules or a
discovered repository-authored gate explicitly requires them.

Before publication, freeze the task-owned tree and rerun the complete Tier-1
gate on the exact tree represented by the durable validation-receipt commit.
Any later task-owned change requires a new validated receipt head.

## Publication and review workflow

Execute only on `docs/mip-root-readme-product-story-refinement-001` after
verifying repository/task identity, remote equality, the finalized branch
baseline, and descent from immutable authorization provenance. Publish
`ready_for_review` with task execution still authorized, correction authority
false, merge/PR authority false, reviewed/approval SHAs null, and capability
authority unchanged. Stop for external exact-head review.

Do not create a PR, merge, squash, rebase, force-push, cherry-pick, or merge
commit. One correction cycle is available only after an explicit review
decision. Merge requires separate approval naming the exact remote head and
the repository fast-forward/closure workflow.

## Deferred successors and authority

This task does not authorize or alter
`GEOX_MAIN_TEST_ISOLATION_AND_CHECKPOINT_CONTEXT_RECOVERY_001`, GeoX
certification, MMM implementation, the parked MIP GeoX/MMM bridge,
`CalibrationSignal` construction, simulation, optimization, planning,
recommendations, runtime integration, real data, pilot, or production. The P2
capability sequence remains unchanged; the current GeoX milestone remains next
eligible and unauthorized.

All product, analytical, integration, LLM-provider, planning, recommendation,
real-data, pilot, production, and sibling-repository work remains deferred and
requires separate repository-local authoring and authorization.

## Completion state

The README-only implementation is complete at
`4b942e94d2da6347b3f89afd7387b4fd1c3823c1`. The final Tier-1 gate passed on
the frozen publication tree: the learning loop and three journeys were
verified, every relative link resolved, heading order and entrypoints were
verified, `git diff --check` passed, and the focused README/deployment/docs plus
execution-coherence tests passed. The durable publication receipt is the exact
remote feature-branch head after push; `reviewed_head_sha` remains null until
external review.

No product, source, test, fixture, architecture, roadmap, governance, P2
program, sibling-repository, analytical, runtime, planning, recommendation,
pilot, production, merge, or PR authority changed.
