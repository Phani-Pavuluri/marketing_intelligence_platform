# MIP Roadmap Audit Ratification Brief 001

## Status and source reconciliation

`MIP_ROADMAP_BLOCKED_BY_MULTIPLE_CRITICAL_GAPS`: 2 critical, 2 high, 0 medium,
0 low, 8 silent gaps, and 3 sequence errors. Sources: MIP `86a10af`, MMM
`da8bdbe`, panel_exp `ce0168f`; dirty sibling work was excluded. The gap matrix
governs counts/IDs, the audit report governs supporting concerns, and the
amendment plan governs Option C. D1–D10 are `approved_with_modifications` by
Phani. The ratification decision review is complete. Option B remains a
recommendation only; the hybrid R0–R6-plus-lanes structure is the approved D10
governance structure.
only. No work is unfrozen. Acceptance-004, Phase F, the resolver, and
`MIP_ROADMAP_AMENDMENT_AND_EXECUTION_REBASE_001` remain unauthorized.

## Canonical gaps and concerns

Formal gaps: `llm_core_benchmark` (critical), `production_lifecycle` (critical),
`artifact_grounded_benchmark` (high), `cross_repo_release` (high). Silent gaps:
core benchmark, artifact benchmark, pilot/production lifecycle, runtime
operations, security/privacy/tenancy, release/rollback, dataset governance, and
recommendation lifecycle. Contract migration, artifact persistence, provider
cost policy, workflow failure ownership, and human approval remain supporting
concerns, not additional formal count entries.

## Candidate sequences

**Option A — strict authorization-first**

`core benchmark → resolver/artifact lifecycle → artifact-grounded benchmark →
cross-repo release gate → security/operations gate → pilot authorization →
controlled live engines → simulation/optimization → production authorization`.

Safest for authorization; delays private integration.

**Option B — controlled integration before pilot**

`core benchmark → resolver/artifact lifecycle → artifact-grounded benchmark →
cross-repo contract/release design → security/data-lifecycle architecture →
fixture/private engine integration → integrated runtime certification/rollback →
limited pilot → pilot evaluation → production authorization`.

Architecture recommendation only: it can collect contained integration evidence
before pilot. It requires fixture/synthetic data only unless separately
authorized; local/private environment only; no external users, production
credentials, persistent real customer data, scheduled execution, automatic
engine execution, budget recommendation, treatment-market assignment, or pilot/
production claim. The named gate owner is the MIP platform-production owner with
MMM and panel_exp release-owner concurrence. Stop on missing containment,
contract failure, security/privacy issue, rollback failure, or any execution/
recommendation claim; rollback is fixture-only operation.

**Option C — committed auditor proposal**

`R0 ownership/environment matrix → R1 core LLM benchmark → R2 resolver/artifact
lifecycle → R3 artifact-grounded benchmark → R4 integration release gate → R5
pilot security/operations gate → R6 limited pilot/production authorization`.

It is easiest to trace to the audit, but does not explicitly separate private
integration certification from pilot; that is the principal difference from B.

## D1–D10 decision records

D1–D10 are `approved_with_modifications`. “Eligible” means
**would become eligible for authorization only after Phani approves this decision
and the canonical roadmap is amended**.

| ID | Question / options | Auditor / architecture recommendation | Tradeoff | Default | Eligible after approval | Still blocked |
|---|---|---|---|---|---|---|
| D1 | Must benchmark pass before provider/prompt/model promotion? Options: required; operational-only; none. | Auditor: benchmark gate. Architecture: required. | rigor vs speed | approved with modifications | roadmap amendment/benchmark design | promotion until both gates and explicit approval |
| D2 | Should acceptance-004 be operational-only? Options: operational-only; promotion authority; defer. | Auditor: not separately stated. Architecture: operational-only. | reliability vs authority | approved with modifications | roadmap amendment/operational-acceptance design | acceptance execution and promotion |
| D3 | Resolver after core benchmark and before artifact benchmark? Options: yes; after grounded benchmark; defer. | Auditor: R1→R2→R3. Architecture: yes. | progress vs evidence | approved with modifications | roadmap amendment/benchmark design approval for contracts; fixture implementation after R1 pass | user-facing promotion, uploads, Phase F, live engines, pilot, production, provider promotion |
| D4 | What security/data lifecycle precedes persistence/uploads? Options: full R5 first; architecture first; defer. | Auditor: R5 prerequisite. Architecture: architecture first, implementation gate before data. | early design vs data risk | approved with modifications | roadmap amendment/fixture-only nonpersistent development under containment | persistence, uploads, live engines, pilot, production |
| D5 | May controlled private integration precede pilot? Options: A; B; none. | Auditor: not separately stated. Architecture: B. | evidence vs containment | approved with modifications | roadmap amendment/contract-adapter design and authorized certified fixture integration | private real-data execution, live-engine, pilot, production, simulation, optimization, treatment assignment, recommendations |
| D6 | Split release governance into design then certification? Options: split; one gate; defer. | Auditor: R4. Architecture: split. | clarity vs process cost | approved with modifications | roadmap amendment/Gate 1 contract, adapter, fixture, and deterministic-test work | live engines, real data, pilot, production, recommendation execution |
| D7 | Standalone MMM/GeoX numerical truth milestone? Options: standalone; embedded; defer. | Auditor: truth owners stated. Architecture: standalone. | visibility vs milestone count | approved with modifications | roadmap amendment/truth-program and registry design; non-analytical core benchmark design | analytical evaluation, certified integration, engine-output claims, simulation/optimization evaluation, analytical promotion pending certified truth |
| D8 | Define four environment boundaries? Options: explicit; demo/pilot only; defer. | Auditor: R0. Architecture: explicit. | clarity vs planning effort | approved with modifications | roadmap amendment/environment-matrix design only | environment promotion, live execution, real data, pilot, production, simulation, optimization, recommendations |
| D9 | When may simulation/optimization/recommendations occur? Options: after governed evidence; pilot; production only. | Auditor: deferred. Architecture: after governed evidence with later authorization. | value vs decision risk | approved with modifications | roadmap amendment/recommendation-lifecycle architecture and RecommendationContract design only | simulation, optimization, recommendation generation/approval/execution, external action, pilot, production |
| D10 | Linear R0–R6 or lanes? Options: linear; lanes with gates; hybrid. | Auditor: R0–R6. Architecture: lanes with gates. | simplicity vs parallel visibility | approved with modifications: hybrid R0–R6 plus governed lanes | structure only; no later governance artifact is authorized | amendment, execution rebase, task generation, implementation, all frozen capabilities |

## Lane-based recommendation only

Lanes: governance; evaluation/dataset; product/control-plane; cross-repository
integration; platform-production; pilot/production authorization. Mandatory
edges: governance/R0 authorizes evaluation R1; R1 authorizes R2; R2 authorizes
R3 and R4 design; R3/R4 authorize R5; R5 plus R4 certification authorizes R6.
Each edge requires a named gate owner and recorded evidence; parallel work may
prepare designs only and cannot cross an edge. A unified status model is
`planned → documented → implemented → tested → validated → promoted →
production_authorized → operationally_supported`, with blocked/deferred reasons.

## D1 approved-with-modifications record

Approved by: **Phani**. A versioned benchmark must pass before provider, prompt,
or model promotion. Target-environment operational acceptance is also required.
Neither benchmark success nor operational acceptance has independent promotion
authority; explicit approval is required after both gates pass. Benchmark
development and provider evaluation become eligible only after the canonical
roadmap amendment. Benchmark design must define regression tolerances, rollback
triggers, and the last-known-good provider/model/prompt configuration. Numeric
thresholds remain deferred and unapproved.

## D2 approved-with-modifications record

Approved by: **Phani**. Acceptance-004 is an operational reliability and
deployment-acceptance gate for the exact target environment and exact
provider/model/prompt configuration. It has no independent authority to promote
a provider, model, prompt, or conversational configuration. Promotion requires
a core benchmark pass, target-environment operational acceptance pass, and
explicit promotion approval.

Its operational scope must cover provider connectivity and authentication,
environment configuration, strict structured-output parsing, live wire-to-domain
mapping, claim/action guards, deterministic fallback, timeout/rate-limit/provider
failure handling, durable acceptance-runner checkpoints and conservative call
counting, conversation continuity, applicable local-browser and hosted
public-demo behavior, secret handling/disclosure, operational latency and cost
evidence, and rollback/provider-disable behavior. The core benchmark remains
authoritative for factuality, grounding, domain coverage, multi-turn quality,
context interpretation, refusal/governance quality, comparative
provider/model/prompt quality, human-review scoring, and regression thresholds.
Structured-output reliability, governance guards, fallback, continuity, latency,
and cost may appear in both: the benchmark evaluates representative scenarios;
operational acceptance verifies the deployed target environment.

Acceptance-004 design must identify the target environment, exact configuration,
acceptance thresholds, call budget, failure criteria, last-known-good
configuration, rollback/provider-disable path, and sanitized evidence
requirements. Its execution would become eligible for authorization only after
the canonical roadmap is amended; this decision does not authorize execution.
Until then, acceptance-004, provider/prompt/model promotion, Phase F, and the
artifact-and-requirement resolver remain unauthorized.

## D3 approved-with-modifications record

Approved by: **Phani**. The governing order is: core conversational benchmark
→ fixture-backed resolver implementation → artifact-grounded benchmark →
user-facing artifact capability. Resolver contract and lifecycle design may
become eligible only after the canonical roadmap amendment and approval of the
core benchmark design, including its schema, scope, and governance
expectations. This design work covers artifact identity, requirement contracts,
resolution statuses, missing/blocked/incompatible behavior, deterministic
interfaces, and lifecycle requirements; it exposes no artifacts to users and
executes no engines.

Deterministic fixture-backed resolver implementation may become eligible only
after the core benchmark v1 gate passes—not merely when the benchmark is
defined. It is limited to synthetic or certified fixtures, with no real customer
uploads, automatic MMM or GeoX execution, persistent production artifacts, or
user-facing promotion. Deterministic tests must use known expected outcomes.

The resolver may not be promoted for user-facing artifact-grounded use until
artifact identity, lineage, compatibility, staleness, persistence, access,
retention, deletion, migration, and failure states are governed; MMM and GeoX
expected-truth fixtures are available; the artifact-grounded benchmark and
target-environment operational acceptance pass; and explicit
artifact-capability authorization is granted. D3 does not authorize uploads,
live MMM or GeoX execution, Phase F, pilot use, production use, or provider
promotion.

## D4 approved-with-modifications record

Approved by: **Phani**. Security and data-lifecycle architecture must be
approved before resolver contract and lifecycle design begins. Fixture-only,
nonpersistent resolver development may become eligible after the canonical
roadmap amendment only when it uses synthetic or certified fixtures and cannot
handle persistent customer data, external users, production credentials, or live
analytical execution.

Persistent artifacts or real uploaded data require implemented authentication and
authorization; workspace ownership and isolation; artifact access controls; data
classification and minimization; encryption where data is persisted; retention
and deletion; audit logging; migration and supersession; secrets and
provider-exposure controls; and operational ownership. Pilot and production data
operation additionally require validated jobs, recovery, incident response,
observability, SLOs, rollback, support ownership, and explicit authorization.

D4 does not authorize artifact persistence, uploads, live MMM or GeoX, pilot
operation, or production operation.

## D5 approved-with-modifications record

Approved by: **Phani**. Contract and adapter design may become eligible only
after the canonical roadmap amendment and applicable contract, ownership, and
release-design gates. Certified fixture-backed MMM, GeoX, and MIP integration
may be authorized before pilot only when inputs are synthetic or analytically
certified fixtures; expected numerical truth is owned by MMM or GeoX; the
environment is explicitly labeled `fixture/private-test`; and no external users,
production credentials, persistent customer data, scheduled jobs, or automatic
workflow execution are involved.

Deterministic integration tests and typed failure evidence are required. Named
MIP, MMM, and GeoX owners must approve the integration boundary. Any containment
failure triggers an immediate stop and rollback to fixture-only operation.
Private-local real-data engine execution is not authorized by D5; it requires a
separate security, data-use, release, environment, and operational
authorization. Pilot and production engine execution remain subject to later
authorization gates.

Fixture-backed integration does not imply live-engine, pilot, production,
simulation, optimization, treatment-assignment, or recommendation authority.

## D6 approved-with-modifications record

Approved by: **Phani**. Cross-repository release governance is split into two
gates. **Gate 1 — Contract and Release Design** defines producer and consumer
ownership, contract versions, compatibility, parser behavior, migrations,
fixtures, failure semantics, release order, rollback design, environment scope,
deprecation, and approval authority. After the canonical roadmap amendment,
Gate 1 may make contract work, adapter implementation, certified fixtures, and
deterministic integration tests eligible. It does not authorize live engines,
real data, pilot, production, or recommendation execution.

**Gate 2 — Integrated Runtime Certification and Rollback** must prove
compatibility against real package entrypoints, agreement between fixtures and
runtime behavior, typed failure propagation, safe partial failure, executable
release order, tested rollback, last-known-good versions, observability evidence,
satisfied security boundaries, target-environment operational acceptance, and
named-owner approval. Gate 2 may make a bounded integration eligible for a later
explicit authorization decision; it does not independently authorize pilot or
production.

Every integrated release requires a versioned release packet containing repository
commits, contract versions, compatibility evidence, test results, limitations,
authorization flags, release and rollback order, last-known-good versions,
environment scope, and named approvers. MMM remains the MMM analytical engine,
GeoX remains the experimentation engine, neither directly orchestrates the
other, and MIP remains the control plane and integration boundary.

## D7 approved-with-modifications record

Approved by: **Phani**. Establish a standalone, versioned Numerical Truth
Dataset Program with separate engine-owned truth suites. MMM owns and certifies
MMM numerical truth, including model inputs, response behavior, calibration
compatibility, diagnostics, uncertainty, `DecisionSurface`, simulation, and
failure cases. GeoX/panel_exp owns and certifies experimentation numerical truth,
including feasibility, assignment geometry, power/MDE, estimator and inference
suitability, treatment effects, readouts, calibration exports, post-test
evidence, and failure cases.

MIP does not create or certify statistical truth. MIP owns the cross-repository
dataset registry, conversational and workflow scenario wrappers, artifact
states, expected routing, allowed and prohibited claims, and evaluation scoring.
Every numerical-truth dataset must define stable identity and semantic version;
repository and maintenance owner; provenance or deterministic generation method;
schema and data dictionary; known parameters, expected outputs, and tolerances;
supported and unsupported use; covered methods and failure modes; validation
evidence; compatibility requirements; change history; and promotion,
replacement, deprecation, and retirement policy.

The initial program uses one primary end-to-end domain plus structured expansion
and stress cases. Specific domains, KPIs, grains, channels, and expansion
criteria require separate approval. Core conversational benchmark design may
proceed without the complete engine-truth program where cases do not require
analytical ground truth. Certified MMM or GeoX truth is required before
artifact-grounded analytical evaluation, certified fixture-backed engine
integration, engine-output compatibility claims, simulation or optimization
evaluation, and analytical-result promotion. Fixtures and numerical truth provide
evaluation evidence only; they do not authorize real data, live engines, pilot,
production, simulation, optimization, or recommendations.

## D8 approved-with-modifications record — environment and operating boundaries

Approved by: **Phani**. D8 establishes four explicit environments—Public Fixture
Demo, Internal Fixture-Backed Integration Environment, Limited Pilot, and
Production—with capability boundaries, permitted data, execution mode, access
scope, persistence rules, named owner, entry and exit criteria, required evidence,
approval authority, and rollback target. Evidence from one environment does not
establish readiness or authorization for the next.

Public Fixture Demo is limited to synthetic or approved public fixtures, has no
customer uploads, persistent private user/customer data, live MMM/GeoX execution,
or production credentials, and keeps analytical journeys fixture-backed. A live
LLM provider is separately gated by D1 benchmark passage, D2 target-environment
operational acceptance, and explicit provider/model/prompt promotion. Analytical
outputs carry demo-only disclosure; authorized recommendations and treatment
assignment are prohibited, with provider cost/rate-limit controls required.

The Internal Fixture-Backed Integration Environment has named internal users,
an explicit `fixture/private-test` label, and certified fixtures by default.
Fixture-backed package integration means certified fixtures are passed to real
MMM or GeoX package entrypoints, typed outputs pass through real MIP adapters,
and deterministic expected results and typed failure evidence are produced. It
does not use real customer data or claim live analytical, pilot, or production
execution. Real package entrypoints may be exercised only with certified fixtures
after D5 and D6 gates; external users, production credentials, scheduled or
automatic execution, persistent customer data, and live analytical/pilot/
production claims remain prohibited. “Live MMM” and “live GeoX” are reserved for
separately authorized approved-real-data execution in a pilot or production
environment. The rollback target is fixture-only operation.

Storage has three distinct categories: (1) fixture execution with no durable
evidence; (2) isolated non-customer test-evidence storage; and (3) persistent
product/customer artifact storage. Category 2 may later be authorized only in
the Internal Fixture-Backed Integration Environment for certified fixture
outputs, run manifests, repository commits and contract versions, typed failure
packets, sanitized integration logs, deterministic test evidence, compatibility
and release packets, rollback evidence, hashes, lineage, and timestamps. It
requires explicitly labeled test-only storage, named internal access, no external
access, no real customer or uploaded data, no production credentials or secrets,
sanitized evidence only, defined retention/deletion, no provider exposure, no
production backup/replication, access/deletion auditability, purge on containment
or security failure, and rollback to fixture-only operation. It never authorizes
persistent user/customer data, uploaded CSV storage, user-facing artifact
persistence, production model artifacts, real-data analytical outputs, general
artifact discovery, or pilot/production persistence.

This clarifies rather than overrides D4: **D4 continues to prohibit persistent
user/customer data and product artifact storage before the persistent-artifact
gate. Narrowly approved, sanitized, non-customer test evidence may later be
stored only under the isolated-test-storage containment defined by D8.**

Limited Pilot requires named users/organizations, separately approved real-data
use, implemented authentication/authorization, workspace or tenant isolation,
retention/deletion, persistent-artifact governance, audit logging, durable jobs,
retries, idempotency, recovery, observability/SLOs, incident handling, support,
runtime certification, tested rollback, human review, measurable success criteria,
and explicit pilot authorization. Controlled live MMM or GeoX execution is
possible only after those gates. Production requires all pilot controls plus
production authorization, production SLO/support/DR, capacity and cost controls,
security/privacy review, dependency/provider lifecycle management,
lifecycle/deprecation/migration management, release and rollback procedures,
kill-switch authority, and decision accountability. Production authorizes only
specifically approved capabilities; neither environment inherits authorization
for simulation, optimization, recommendations, automated decisions, or treatment
assignment.

MIP and the LLM do not perform or replace engine-owned analytical computations or
approval-owned decisions. Authority is governed by the canonical
capability-authority matrix, which will cover computation, validation,
explanation, and approval ownership across major capabilities. Treatment-market
assignment is a high-risk example: GeoX owns governed assignment computation;
MIP may validate contracts, invoke an authorized entrypoint, register evidence,
and explain results; the LLM does not independently choose treatment markets;
required human or governance approval remains separate.

D8 does not authorize an environment transition, acceptance-004, private
real-data integration, uploads, persistent customer/product artifacts, live MMM
or GeoX, pilot, production, simulation, optimization, recommendations, automated
decisions, or treatment assignment. The work freeze remains unchanged and
`MIP_ROADMAP_AMENDMENT_AND_EXECUTION_REBASE_001` remains unauthorized.

## D9 approved-with-modifications record

Approved by: **Phani**. Recommendation-lifecycle architecture and
`RecommendationContract` design may become eligible only after the canonical
roadmap amendment. This design eligibility does not authorize simulation,
optimization, recommendation generation, approval, execution, or external
action. The lifecycle must separately govern analytical evidence; `DecisionSurface`
or equivalent response evidence; simulation evidence; optimization candidates;
recommendation proposals; analytical/business review; recommendation approval;
execution authorization/handoff; execution confirmation; outcome and
incrementality monitoring; expiration, override, disagreement, and revocation;
and rollback/corrective action.

The canonical capability-authority matrix must distinguish engine computation,
technical validation, artifact promotion or authorization for decision use,
explanation, recommendation proposal, decision approval, and external execution.
Engine-owned analytical artifacts do not require business approval merely to be
computed or tested; named governance authority is required before promotion or
decision-authoritative use. A simulation is not a recommendation, an optimization
result is only a candidate plan, a recommendation proposal is not approval,
approval is not execution, and execution must be separately authorized, confirmed,
and auditable.

MMM owns governed MMM analytical computation; GeoX/panel_exp owns governed
experiment computation; MIP owns contracts, workflow state, evidence assembly,
routing, lifecycle state, and audit evidence. The LLM may explain governed
evidence and formulate a recommendation proposal only when explicitly authorized.
It may not replace engine computation, alter certified engine outputs, promote
analytical artifacts, approve recommendations, self-approve an automated proposal,
execute external actions, or revoke/override accountable human authority.

A versioned `RecommendationContract` must track proposal, review, approval,
execution, monitoring, expiration, revocation, and rollback states while
referencing—not recreating—the governed analytical artifacts supporting the
recommendation. Fixture-backed recommendation evaluation may later be authorized
under contained test conditions using certified truth and deterministic expected
behavior; it does not authorize real-data decision support, pilot/production use,
or external execution. Recommendation proposal, artifact promotion, decision
approval, execution, pilot use, and production use each require separate explicit
authorization.

## D10 approved-with-modifications record

Approved by: **Phani**. D10 selects a hybrid roadmap structure: R0–R6 remain
the authoritative audit-aligned milestone and dependency sequence. Work within
those milestones is organized into governed lanes for governance/ownership/
authorization; benchmarks/evaluation/numerical-truth datasets; MIP product and
control-plane architecture; resolver/artifact lifecycle; MMM/GeoX integration
and release governance; security/data lifecycle/platform/operations; and pilot,
production, and recommendation authorization.

Every lane item must define its governing R0–R6 milestone; prerequisite decisions,
commits, and artifacts on `main`; named owner; entry/exit criteria; required
evidence packet; current authorization state; blocking and cross-repository
dependencies; stop/rollback conditions; and promotion/release boundary. Lanes may
proceed in parallel only when their governing milestone and prerequisites permit.
No lane may bypass an R0–R6 gate, benchmark/numerical-truth requirement,
resolver/artifact-lifecycle sequence, D4 security/persistence boundary, D5
fixture-containment boundary, D6 release design/runtime certification, D8
environment boundary, canonical capability-authority matrix, D9
recommendation-lifecycle gate, or explicit Phani authorization.

The unified governance states are `OBSERVED → PROPOSED → APPROVED →
AUTHORIZED_FOR_EXECUTION`. Approval is not execution authorization; authorization
for one governance artifact does not authorize later artifacts or implementation.
Every later task must cite its authorizing roadmap section/evidence, verify
prerequisite commits and artifacts on `main`, and old task files retain no
authority after execution rebase unless explicitly retained and reauthorized.

D10 answers only the roadmap-structure question and completes the D1–D10
ratification decision set. It does not authorize canonical-roadmap-amendment
drafting, `MIP_ROADMAP_AMENDMENT_AND_EXECUTION_REBASE_001`, execution-rebase
planning, implementation-task generation, frozen implementation, or runtime,
provider, engine, data, recommendation, pilot, or production capability. After
this brief is validated, committed, reviewed, merged, and verified on `main`, a
separate canonical-roadmap-amendment task still requires new explicit Phani
authorization.

Any future separately authorized canonical amendment must incorporate D1–D10,
preserve R0–R6 traceability, define governed lanes/mappings and revised
dependencies, name owners/approval authorities, define entry/exit/validation/
stop/rollback criteria and evidence packets, identify superseded roadmap
language and migration, record cross-repository sequence, preserve remaining
freezes/non-authorizations, and define task-generation/execution-rebase rules.

## Freeze matrix and review order

All remain fully frozen: acceptance-004/provider promotion (D1/D2/R1), resolver/
Phase F (D3/R1/R2), uploads (D4/R5), live MMM/GeoX (D5/D6/R4/R5), and
simulation/optimization/recommendations (D9). Review D1–D10, choose a structure,
ratify owners/gates/environments, then—and only then—consider the canonical
execution-rebase task. Benchmark implementation, acceptance-004, Groq/OpenAI
promotion, Phase F, the resolver, and the execution-rebase task remain
unauthorized until the canonical roadmap is amended.
