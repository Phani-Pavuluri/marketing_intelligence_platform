# Active Task

**Status:** merged
**Task ID:** `MIP_ROOT_README_EXTERNAL_REVIEW_CLARITY_AND_ONBOARDING_POLISH_001`
**Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
**Local path:** `/Users/phani/Desktop/marketing_intelligence_platform`
**Pre-authoring base:** `7c6708d602093d415c0063e8607c19cdaff4b9a5`
**Authorization provenance:** `3792368d819fff363b908e5f2168bef766e8ded8`
**Finalized branch baseline:** `8db4178cf719526ecd66275031faa8f1360256be`
**Implementation commit:** `8722095e49b020b9165c75249b2f2724102354d5`
**Reviewed and merged head:** `e212751158b008b2b6bb1bc53f574362d8c301d4`
**Feature branch:** `docs/mip-root-readme-external-review-clarity-and-onboarding-polish-001`
**Execution mode:** `branch_and_fast_forward`
**Risk tier:** Tier 1 — routine repository-local documentation
**Compatibility or migration policy:** `not_applicable`
**Capability authority changed:** `false`
**Unresolved execution-blocking design questions:** none

## Primary outcome

Refine only the root `README.md` into a clearer, less repetitive, more
scannable, and more actionable front door for a first-time external reviewer,
marketer, technical leader, senior data scientist, or developer. The reader
journey must progress coherently from why MIP exists → user jobs → system
mechanics → concrete journeys → core capabilities → a successful first product
experience through the hosted demo, local app, API, package, or CLI.

This is one independently reviewable outcome because every edit serves one
front-door usability journey in one Markdown file. The conceptual sections and
onboarding instructions must be reviewed together: separating them would leave
either an understandable product with no usable entry path or runnable commands
without the product context needed to interpret their deterministic outputs.
This task changes no behavior, contract, architecture, source, test, fixture,
program state, or authority.

## Authorization provenance convention

`authorization_head_sha` identifies
`3792368d819fff363b908e5f2168bef766e8ded8`, the first `main` commit
establishing this authorized task contract. That commit contained a null
self-reference; this metadata-only finalization records its exact SHA as
immutable authorization provenance. It must never be replaced by the metadata-finalization,
feature-branch, implementation, publication, review, or merge head.

Create the feature branch only from synchronized metadata-finalized `main`. The
finalized baseline must descend from the immutable authorization provenance;
the intervening diff may contain only the three stable execution files. No
README or implementation change may precede feature-branch creation.

## Owned and prohibited paths

The sole implementation-owned path is:

- `README.md`

Lifecycle updates to these stable execution files are allowed only as required
by the execution standard:

- `docs/execution/ACTIVE_TASK.md`
- `docs/execution/EXECUTION_STATE.json`
- `docs/execution/LATEST_COMPLETION_REPORT.md`

Do not modify product/source code, tests, fixtures, apps, contracts,
architecture documents, roadmaps, program or P2 files, coordination state,
governance or execution standards, dependencies, CI, Docker, data, MMM, GeoX,
or any sibling repository.

## Required reader journey and section roles

Preserve the current major README information architecture, but remove or
shorten adjacent repetition so each section has exactly one primary job:

1. **Why MIP exists:** conceptual problem and continuous causal-learning loop.
2. **What can you do with MIP?:** high-level user jobs and questions.
3. **How MIP works:** routing, evidence reconciliation, governance, and answer
   mechanics.
4. **Example decision journeys:** short concrete end-to-end examples.
5. **Core capabilities:** structured capability inventory.
6. **Demo and quick start:** how someone actually experiences or runs MIP.

Do not broadly rewrite unrelated sections merely for stylistic consistency.

## 1. Refine “Why MIP exists”

Use approximately two or three compact paragraphs and one glanceable visual.
Explain why the integrated causal-learning system is needed:

- MMM provides the broad portfolio view across channels.
- Historical/observational variation can leave material channel or planning
  uncertainty.
- MIP assesses whether existing evidence is sufficient or stronger causal
  evidence would be valuable.
- Sufficient evidence can proceed toward scenario analysis and planning.
- When stronger causal evidence is needed, MIP can engage the GeoX arm for a
  targeted experiment.
- GeoX produces causal lift evidence; compatible learning can strengthen future
  MMM measurement.
- The updated portfolio view supports scenario analysis, planning, and a
  business decision/action.
- A new question or material uncertainty can initiate another measurement
  cycle.

The visual must use this conceptual shape without an accidental self-loop:

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

Do not imply every uncertainty requires an experiment. The next action may use
existing evidence, inspect or refresh MMM, require additional data, or engage
GeoX. Keep `TrustReport`, `CalibrationSignal`, detailed lineage/freshness and
estimand checks, full-panel Δμ, and gate implementation out of this high-level
visual. Preserve that MIP coordinates while GeoX and MMM retain numerical
authority.

## 2. Redesign “What can you do with MIP?”

Remove the current experiment → MMM → planning process diagram. Give this
section a distinct, concise, user-oriented purpose: the business questions and
jobs a user can bring to MIP. Organize a small number of scannable groups such
as measurement, experimentation, evidence learning, planning, and trust/next
action rather than presenting one long list.

Cover representative questions:

- Is this channel actually incremental?
- Where is additional measurement most valuable?
- Is existing evidence sufficient?
- What experiment should be run when evidence is weak?
- What does a completed experiment mean for the broader measurement system?
- How should compatible experimental evidence inform MMM?
- What happens under a different spend scenario?
- Can budget be reallocated across channels?
- Is the evidence trustworthy enough for the intended decision?
- What should be measured next?

Use natural product language, not architecture terminology. Do not present
deterministic/demo, partial, blocked, planned, or unauthorized functionality as
fully live.

## 3. Simplify “How MIP works”

Replace the dense current visual with five visually obvious stages:

1. Frame the question.
2. Route to the appropriate evidence or analytical path.
3. Reconcile and govern evidence.
4. Answer the user's decision need.
5. Explain the result and continue learning.

### Stage 1 — Frame the question

Begin with the business question. Summarize objective, KPI, channels,
geography/population, time horizon, constraints, available data, and available
evidence in one compact intake step.

### Stage 2 — Route to the right path

Retain three clear paths:

```text
┌────────────────────┬────────────────────┬─────────────────────┐
│ GeoX / Experiment  │ MMM                │ Existing Evidence   │
│ readiness          │ readiness          │ retrieve prior      │
│ → design           │ → fit / diagnose   │ evidence/artifacts  │
│ → inference        │ → portfolio view   │ → provenance/trust  │
│ → governed lift    │ → decision surface │ → assess sufficiency│
└──────────┬─────────┴──────────┬─────────┴──────────┬──────────┘
           └────────────────────┼─────────────────────┘
                                ↓
```

State compactly that GeoX owns experiment design, assignment, inference, and
causal-lift truth; MMM owns fitting, diagnostics, calibration application,
simulation, optimization, and MMM numerical truth; and existing evidence may
answer the question without forcing new execution.

### Stage 3 — Reconcile and govern evidence

Summarize rather than assigning every check a separate node:

```text
scope / estimand alignment
→ quality, provenance, freshness, uncertainty, and compatibility
→ calibration eligibility when relevant
→ TrustReport / decision eligibility
```

Keep `CalibrationSignal` visible only where it clarifies the sole authoritative
GeoX → MMM handoff. Do not imply raw experiment output edits coefficients, MIP
performs numerical calibration, or all experiments automatically calibrate MMM.

### Stage 4 — Answer the user need

Show three outcomes:

- **Measurement answer:** causal/incrementality evidence, uncertainty, and
  supporting evidence.
- **Planning answer:** eligible scenario comparison, trade-offs, and decision
  context.
- **Evidence insufficient:** what is missing and the appropriate additional
  data, measurement, or experiment.

### Stage 5 — Explain and continue learning

End with AI + MIP explaining evidence used, uncertainty, blockers, trade-offs,
trust/eligibility where relevant, and the recommended next action. A new
business question or material uncertainty may re-enter evidence assessment or
workflow routing; it must not force GeoX.

## 4. Rebuild “Demo and quick start”

Turn this section into first-time-user onboarding, not a command list.

### Hosted demo — try this first

Keep `https://marketingintelligenceplatform.streamlit.app/` prominent. State
that it uses synthetic fixtures, no production data, and demonstrates governed
intake, advisory, readiness, routing, profiling, and calibration-mapping
behavior without implying live MMM/GeoX execution. State from synchronized code
that the public demo has no configured LLM provider and uses deterministic
responses.

Give a short, code-verified walkthrough using only current UI behavior. It may
direct a reviewer to the Measurement Copilot's starter prompts and preloaded
SaaS growth-planning journey, inspect readiness/evidence/blocking explanations,
and use Advanced tools for cold-start advisory, readiness reports, calibration
mapping, demo profiling, or intake overview. Do not claim upload support,
persistence, live inference, lift/ROI/power estimation, or recommendations.

### Local prerequisites and complete install

Document verified requirements:

- Git and a clone of this repository;
- Python `>=3.11,<4.0`;
- Poetry, with a brief direction to install it if absent.

Provide a complete copyable HTTPS clone/install sequence using:

```bash
git clone https://github.com/Phani-Pavuluri/marketing_intelligence_platform.git
cd marketing_intelligence_platform
poetry install
```

### Canonical Streamlit app and first run

Use the exact canonical command:

```bash
poetry run streamlit run app/streamlit_app.py
```

Explain the local URL/startup expectation and provide two to four implemented
first-run actions. State that deterministic mode uses synthetic fixtures,
requires no LLM provider/API key/database/external service, persists no uploaded
data, and executes neither live MMM fitting nor live GeoX inference.

### FastAPI interface

Explain that developers/integrators can inspect the same deterministic workflow
layer through the service wrapper. Use the verified startup command:

```bash
poetry run uvicorn mip.service.app:app --reload --host 127.0.0.1 --port 8000
```

Document `GET /health`, `GET /version`, and these implemented POST routes:

- `/advisory/cold-start` with `{"sample_key":"dtc_skincare_ecommerce"}`;
- `/readiness/assess` with
  `{"sample_key":"national_mmm_ready_geox_blocked"}`;
- `/calibration/map` with `{"sample_key":"valid_governed_evidence"}`;
- `/intake/overview` with `{"example_key":"national_mmm_diagnostic"}`.

Include at least one copyable `curl` request that succeeds against synchronized
contracts. Validate every documented route/payload with the existing FastAPI
test client or a locally started service before publication. Make the
deterministic, advisory/non-production boundary visible.

### Python/package usage

Briefly show that notebooks and developers can call the shared deterministic
workflow layer. If included, use a validated concise example based on an actual
function such as:

```python
from mip.service.workflows import run_readiness_assess

result = run_readiness_assess("national_mmm_ready_geox_blocked")
print(result.model_dump_json(indent=2))
```

Run the final example against the synchronized installed package before
publication; omit it rather than publishing an unverified import or signature.

### CLI and contributor validation

Document `poetry run mip-demo --help` as the existing deterministic JSON-file
workflow CLI. Do not confuse it with a future design-only CLI. Mention
`poetry run mip-app` only as the current backward-compatible legacy Streamlit
shell; the root `app/streamlit_app.py` command remains canonical.

Expose only existing repository validation commands and explain their purpose:

- `make validate-host` — host validation;
- `make validate` or `make validate-docker` — Docker-backed validation;
- `make validate-public-deployment` — public deployment install/readiness gate.

### Current limitations

Finish onboarding with one concise boundary statement distinguishing the
deterministic/demo experience from live certified GeoX execution, generally
available MMM execution/calibration, production optimization/recommendations,
real production-data integration, and fully live LLM-backed behavior.

## Preserved factual and authority invariants

- `TrustReport` is the sole trust verdict.
- `CalibrationSignal` is the sole GeoX → MMM bridge.
- Full-panel Δμ is the sole MMM production decision surface.
- GeoX owns experiment design/inference and experiment numerical truth.
- MMM owns fitting, diagnostics, calibration application, simulation,
  optimization, and MMM numerical truth.
- MIP owns orchestration, governance, evidence routing, consumer workflows, UX,
  and LLM behavior.
- MIP neither recomputes GeoX lift nor edits MMM coefficients.
- Experiment evidence must satisfy required quality and compatibility conditions
  before becoming calibration evidence; no automatic calibration is implied.
- Demo, partial, blocked, planned, research-only, and unauthorized capabilities
  must not be upgraded into shipped production functionality.

## Acceptance evidence and failure semantics

The completed README must let a first-time reader understand the product without
section-level repetition and successfully choose a verified experience path.
“Why” must contain two correctly converging evidence branches and no self-loop;
“What” must present user jobs rather than repeat the learning process; “How”
must retain all three analytical/evidence paths in a materially simpler
five-stage visual; and onboarding must include verified hosted-demo guidance,
clean installation, Streamlit first run, API, package, CLI, validation, and
limitations.

Fail closed without publication if a link, command, import, route, payload, or
UI walkthrough is unverified; a required branch/path is missing; sections still
materially duplicate one another; an invariant is weakened; capability maturity
is overstated; or any implementation-content path other than `README.md`
changes.

## Tier-1 validation gate

On the frozen publication tree:

1. Run `git diff --check` and inspect the complete README diff.
2. Programmatically verify every relative README link resolves.
3. Verify every documented clone/install/run/CLI/Make command and entrypoint
   exists and matches `pyproject.toml`, the Makefile, or synchronized source.
4. Validate each documented FastAPI route and request payload against the
   actual request contracts and test client; validate every included Python
   import and call signature by execution.
5. Verify “Why MIP exists” has no self-loop; both evidence branches converge on
   planning/decision; and recurrence returns to assessment/routing without
   forcing GeoX.
6. Verify “What can you do with MIP?” contains no duplicate learning-loop
   process visual and presents grouped user jobs.
7. Verify “How MIP works” contains the five stages, all three paths, summarized
   governance, three outcomes, and a return-to-learning step while being
   materially simpler than the synchronized baseline.
8. Verify all authority invariants and conservative maturity language.
9. Discover and run relevant README/documentation/deployment tests plus the
   existing service-route/request-contract tests needed to prove examples.
10. Parse `docs/execution/EXECUTION_STATE.json` as JSON.
11. Verify implementation content changes only `README.md`, and P2, program,
    architecture, source, tests, fixtures, dependencies, CI, Docker, and sibling
    surfaces are unchanged.

Full-suite pytest, Ruff, mypy, and Docker-backed `make validate` are
`not_required` for this Tier-1 Markdown-only surface unless synchronized
repository-authored rules require them. The focused service tests validate
documented existing behavior; this task does not modify tests or service code.

## Publication and review workflow

Execute only after a fresh bootstrap verifies this authorization and exact
feature branch. Freeze the task-owned tree and run the Tier-1 gate. Update the
three stable execution files to `ready_for_review`, preserving
`task_execution_authorized: true`, `merge_authorized: false`, and
`pr_creation_authorized: false`. Publish the exact feature head with a durable
validation-receipt commit and stop for external review.

Do not create a PR or merge, squash, rebase, force-push, cherry-pick, or create
a merge commit. One correction cycle is available. No product, analytical,
runtime, planning, recommendation, sibling, capability, pilot, production,
merge, or PR authority follows from this task.

## Preserved P2 sequence and deferred work

The P2 program sequence remains unchanged. The parked MIP GeoX/MMM bridge
remains blocked. `GEOX_MAIN_TEST_ISOLATION_AND_CHECKPOINT_CONTEXT_RECOVERY_001`
remains next eligible and unauthorized. GeoX certification, MMM implementation,
`CalibrationSignal` construction, simulation, optimization, planning,
recommendations, runtime integration, real data, pilot, and production remain
unauthorized and outside this task.
