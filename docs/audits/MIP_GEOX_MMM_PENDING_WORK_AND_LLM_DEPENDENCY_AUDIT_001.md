# MIP, GeoX, and MMM Pending Work and LLM Dependency Audit 001

**Audit date:** 2026-09-15  
**Owner:** MIP  
**Workstream:** `MIP_GEOX_MMM_PENDING_WORK_AND_LLM_DEPENDENCY_AUDIT_001`  
**Decision class:** read-only coordination evidence; no execution or capability
authorization

## 1. Evidence boundary and source precedence

This is a dated Git snapshot, not a task queue or a substitute for any
repository's execution state. Future users must fetch Git again. Synchronized
remote repository evidence outranks this audit, MIP coordination snapshots,
roadmaps, archives, task handoffs, and chat. A feature branch is authoritative
for its mutable lifecycle state only after its identity and authorization
ancestry are verified; it does not establish merged-main capability truth.

Fresh refs observed after `git fetch --prune origin` in each clone:

| Repository | Fresh remote main | Lifecycle-authoritative feature ref | Observed head |
|---|---|---|---|
| MIP (`Phani-Pavuluri/marketing_intelligence_platform`) | `origin/main` = `9bc48e04a932e3f89b91d7e9be7eb3bae9dcee7d` | `origin/audit/mip-geox-mmm-pending-work-and-llm-dependency-audit-001` | `9bc48e04a932e3f89b91d7e9be7eb3bae9dcee7d` before this audit implementation |
| GeoX (`Phani-Pavuluri/panel_exp`) | `origin/main` = `2111cfb2197ea62531919791a1e794a5f601ee6e` | `origin/audit/geox-main-test-isolation-and-checkpoint-context-reassessment-001` | `0f79d277afac4a8675bc3a1365ae89c6da8dcbf9` |
| MMM (`Phani-Pavuluri/MMM`) | `origin/main` = `fe8e784923994406a2e4907d28debd872d61fd73` | none: the merged task's declared branch is absent remotely | not applicable |

Verification used `git rev-parse`, `git ls-remote --heads`, `git show`,
`git merge-base --is-ancestor`, and ref-scoped `git grep`/`git ls-tree`.
MIP main and its feature ref descended from authorization provenance
`688dbe6d780d12a8e8964524326439f16729c746`. GeoX's feature head descended
from repository-local authorization head
`b003d7915d635413fd45fcb98e4ee36ccbc0c7b8`, and its branch execution state
matched repository, task, and declared branch identity. MMM main declared a
merged task and no resumable branch, so no sibling feature ref was inspected.

GeoX's branch is live concurrent work. It was inspected read-only and was not
treated as merged. The GeoX and MMM worktrees were checked before and after
evidence collection. GeoX was clean. MMM's pre-existing `.DS_Store` changes
and untracked `docs/tasks/*.md` files were left unchanged; all MMM evidence was
read from remote refs rather than by switching its worktree. No sibling file,
branch, task, or authority state was changed.

Evidence notation below is `repository@ref:path`. Unless a different ref is
shown, MIP means `9bc48e04...`, GeoX main means `2111cfb2...`, GeoX branch
means `0f79d277...`, and MMM means `fe8e7849...`.

## 2. Repository lifecycle and authority

| Repository | Current task and status | Authority | Blockers/corrections | Validation debt and recent prerequisite evidence |
|---|---|---|---|---|
| MIP | This audit is `authorized` on `audit/mip-geox-mmm-pending-work-and-llm-dependency-audit-001`. | Task execution `true`; correction, merge, and PR `false`; capability changes `false`. Authorization: `688dbe6d...`. | No task blocker; 0 of 1 correction cycles used. The parked P2 bridge is a separate blocked task and is not resumable. | Lifecycle single-source consistency is merged; `taskctl check` passed at bootstrap. The program snapshot still lacks a certified GeoX producer and verified bridge. Evidence: `MIP@origin/main:docs/execution/EXECUTION_STATE.json`, `ACTIVE_TASK.md`, `LATEST_COMPLETION_REPORT.md`; `docs/program/PROGRAM_CURRENT_STATE.md`; `P2_CAPABILITY_CHECKPOINT_LEDGER.json`. |
| GeoX | `GEOX_MAIN_TEST_ISOLATION_AND_CHECKPOINT_CONTEXT_REASSESSMENT_001` is `ready_for_review` on the exact branch above, not merged. | Task execution `true`; correction, merge, and PR `false`; capability changes `false`. | No lifecycle blocker; 1 of 1 correction cycles used. The corrected review head reports four current-main defect classes. | Full Docker gate: `15 failed, 6174 passed, 28 skipped`; all 15 failures reproduced on untouched base `d819fb17...`. Focused manifest: 68 passed; adjacent checks: 3 passed. Defects cover handoff-status parsing, BRB golden equivalence, design-validation callback injection, and design Tier-1 contract emission. Evidence: `GeoX@0f79d277:docs/execution/EXECUTION_STATE.json`, `LATEST_COMPLETION_REPORT.md`, `docs/track_d/GEOX_MAIN_TEST_ISOLATION_AND_CHECKPOINT_CONTEXT_REASSESSMENT_001.md`. |
| MMM | `MMM_EXECUTION_AUTHORITY_CLOSURE_CONSISTENCY_FIX_001` is `merged` on main. Its former remote branch is absent. | Task, correction, merge, and PR `false`; capability changes `false`. Reviewed head `60998f50...`; implementation `d930ecf...`; rejected head `bacf406...`. | No active blocker or correction cycle. No task is currently authorized. | Closure gate recorded 1324 passed, 6 skipped, 28 deselected, 36 warnings. Host Poetry absence was recorded, while the required Docker gate passed. Evidence: `MMM@origin/main:docs/execution/EXECUTION_STATE.json`, `LATEST_COMPLETION_REPORT.md`. |

No overlapping active workstream owns this MIP audit. GeoX's active branch owns
only its reassessment evidence; this audit neither supersedes it nor assigns
its remediation. The parked MIP bridge retains its own workstream and stays
blocked. MMM has no active execution workstream. Repository-local authority is
required for every successor named below.

Recently completed work that changes eligibility includes GeoX's lifecycle
single-source adoption, D5 geometry repair closure, import-boundary repair, TBR
recovery contract alignment, artifact-lineage repair, and placebo repair on
main; MMM's calibration compatibility foundation, schema policy, golden
fixtures, calibration lineage, supported-range contract, and public simulation
export on main; and MIP's P2 consumer design and lifecycle control. These are
prerequisites, not producer certification or end-to-end authorization.

## 3. Lane 1 — Repository execution-governance work

1. **GeoX current-main validation defects — blocked pending review outcome.**
   The ready-for-review branch establishes a reproducible classification, not
   a merged repair. The next eligible action depends on external exact-head
   review and repository-local authorization. Each defect then needs its own
   appropriately scoped repair or an explicitly authorized grouping. No MIP
   task may make that choice. Evidence: `GeoX@0f79d277:docs/execution/` and
   `docs/track_d/GEOX_MAIN_TEST_ISOLATION_AND_CHECKPOINT_CONTEXT_REASSESSMENT_001.md`.
2. **GeoX producer checkpoint — blocked.** Current-main validation health and
   the remaining producer/combined-validation evidence must be resolved before
   certification. A ready-for-review reassessment cannot satisfy this gate.
3. **MMM — eligible but unauthorized.** There is no active task. Any provenance
   fixture work or methodological remediation first requires a definition-ready
   MMM task authored under its current `AGENTS.md` and lifecycle state.
4. **MIP parked bridge — blocked and unauthorized to resume.** Branch
   `feat/mip-p2-geox-mmm-compatibility-fixture-bridge-001` was recorded at
   `480b32040ce185b8ff091435121c4bea6fc6c453`; the task remains blocked until
   its producer inputs are certified and a new Git-local resume authorization
   exists. Evidence: `MIP@origin/main:docs/execution/EXECUTION_STATE.json` and
   `docs/program/NEXT_EXECUTION_SEQUENCE.md`.
5. **Snapshot reconciliation — not a silent state edit.** MIP coordination
   files contain older repository SHAs. The protocol requires a live overlay;
   this task does not own `CROSS_REPOSITORY_COORDINATION_STATE.json`, the P2
   ledger, or repository checkpoints, so they remain unchanged.

## 4. Lane 2 — GeoX methodological roadmap

GeoX main remains a research/promotion system, not a blanket production-ready
method catalog. `docs/METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md`,
`docs/METHOD_SELECTION_AND_PROMOTION_FRAMEWORK_001.md`, and
`docs/track_d/METHOD_FAMILY_PRODUCTION_COMPATIBILITY_AND_REMEDIATION_ROADMAP_001.md`
separate implementation from method-family promotion:

- SCM is a gated production candidate, not production-authorized.
- AugSynth still carries diagnostic/remediation and promotion-evidence work.
- DID is conditional; Synthetic DID remains research.
- TBRRidge remains diagnostic; classic TBR is on a retire/replace path;
  Bayesian TBR and TROP remain research.
- Multi-cell designs remain restricted pending shared-control dependence,
  multiplicity calibration, and design-aware placebo evidence.

The live investigation registry at
`GeoX@origin/main:docs/governance/OPEN_INVESTIGATIONS_001.json` contains 144
resolved, 4 planned, and 3 deferred-with-trigger items. Planned work covers P0
governed-runtime hardening, Bayesian TBR calibration replay, a TBRRidge
diagnostic-remediation decision, and a TROP evidence scout. The three deferred
multi-cell investigations trigger on the observed-panel diagnostic
requirements milestone. Counts do not imply promotion.

Remaining GeoX work is therefore:

- obtain disposition of the live reassessment, then repair and validate the
  four current-main defect classes under new GeoX authority;
- complete method-specific statistical and numerical-truth evidence, promotion
  review, and explicit production decisions rather than inferring them from
  implementation;
- close or trigger the planned/deferred investigation items where their gates
  require it;
- validate the governed calibration-source/readout pair, combined producer
  behavior, lineage, failure semantics, and release evidence; and
- publish a producer-certification checkpoint that downstream repositories can
  verify from merged GeoX main.

GeoX already has a strict source-manifest validator and a 12-case source
fixture manifest at
`tests/fixtures/geox_calibration_handoff_sources/v1/manifest.json`. The
manifest explicitly sets `mmm_compatibility_emitted=false`,
`calibration_signal_emitted=false`, and `production_authorized=false`; its
authorization flags are false. That is useful producer-component evidence,
but it deliberately neither constructs `CalibrationSignal` nor certifies MMM
compatibility or production. Evidence:
`GeoX@origin/main:panel_exp/contracts/geox_calibration_source_manifest.py` and
the fixture manifest above.

## 5. Lane 3 — MMM methodological roadmap

MMM main contains deterministic building blocks:

- `mmm/contracts/calibration_compatibility.py` evaluates normalized GeoX
  readout/model context into typed compatible, warning, stale, incompatible,
  or blocked outcomes. It does not import the sibling schema, refit, simulate,
  or authorize planning.
- `mmm/contracts/public_simulation.py` exports a Ridge-only full-panel
  baseline/candidate mean comparison and `delta_mu`, with supported-range and
  blocked/failed states. It is not an optimizer or recommendation engine.
- Versioned fixtures exist under
  `tests/fixtures/mip_export/calibration_compatibility_v1/`,
  `tests/fixtures/mip_export/simulation_v1/`, and the supported-range fixture
  surface. Calibration-treatment lineage contracts are documented in
  `docs/05_validation/mmm_calibration_treatment_lineage_contract.md`.

The remaining work is not “implement delta-mu from scratch.” It is to:

- link MMM fixtures to a certified, exact GeoX producer artifact and preserve
  source hashes, schema/version pins, treatment decisions, warnings, and
  failure provenance;
- verify MMM-owned compatibility treatment of the GeoX evidence at the actual
  certified producer/consumer pair, including stale, blocked, unsupported, and
  migration behavior;
- complete the reliability and calibration evidence still recorded by
  `docs/05_validation/monte_carlo_reliability_program.md`,
  `reliability_scorecard.md`, `reliability_threshold_governance.md`, and the
  investigation registry, including critical threshold and causal-boundary
  questions;
- validate that the canonical decision surface is the full-panel
  baseline-versus-candidate `delta_mu`, never a diagnostic curve;
- keep public simulation distinct from optimization, and separately govern
  optimizer fingerprints, replay, release, waiver, and failure semantics; and
- publish provenance-linked P2 fixture evidence under a newly authorized MMM
  task for MIP consumer verification.

Bayesian work and package-side agents remain research/deferred. Public
simulation's merged contract is component evidence, not certified cross-repo
simulation, recommendation, or runtime authority.

## 6. Lane 4 — P2 cross-repository integration

### 6.1 Exact dependency chain

```text
GeoX governed experiment/readout truth and handoff eligibility
→ CalibrationSignal as the sole governed GeoX-to-MMM bridge
→ MMM-owned experiment-to-model compatibility and calibration treatment
→ MMM baseline-versus-candidate full-panel delta-mu evidence
→ MIP consumer verification, evidence assembly, and governed explanation
```

MIP is not an analytical step in the GeoX-to-MMM bridge. The current MIP P2
consumer contract does not define a producer schema, construct
`CalibrationSignal`, translate GeoX handoff eligibility into MMM compatibility,
or determine calibration treatment. It normalizes producer artifacts without
changing producer analytical values, validates shape/provenance, routes them,
assembles evidence, and reports or explains the producer-owned states.

MMM main contains an export-only GeoX/CLS adapter contract and implementation
surface that can serialize offline source records as `CalibrationSignal`, but
that component evidence does not by itself establish the exact certified
serialized-artifact producer for the current P2 journey. Until a certified
cross-repository producer/adapter contract names that role, serialized
`CalibrationSignal` production is contract-defined and unresolved for P2; it
is not assigned to MIP. GeoX retains its numerical truth and handoff-eligibility
authority, while MMM alone owns model-specific compatibility, calibration
treatment/model lineage, and MMM numerical truth. Evidence:
`MIP:docs/roadmap/MIP_P2_CONSUMER_CONTRACT_AND_FIXTURE_JOURNEY_DESIGN_001.md`;
`MMM:docs/05_validation/geox_cls_to_calibration_signal_adapter_contract.md`;
`MMM:docs/05_validation/mmm_calibration_treatment_lineage_contract.md`.

| Edge | Owner and required input | Required output/gate | Current blocker and authority boundary |
|---|---|---|---|
| GeoX evidence → `CalibrationSignal` bridge eligibility | GeoX owns governed readout/source artifacts, numerical values, exact schema/version pins, lineage, method eligibility, warnings, handoff eligibility, and producer certification. | A merged, certified GeoX producer checkpoint whose output is eligible for the governed bridge. | Live GeoX branch is only ready for review and reports base defects. Existing source fixtures explicitly emit neither `CalibrationSignal` nor compatibility. Evidence: GeoX source manifest/validator; `MIP:docs/program/P2_CAPABILITY_CHECKPOINT_LEDGER.json`. |
| Governed source → serialized `CalibrationSignal` | The exact P2 serializer/producer must be named by the certified producer/adapter contract. MMM main has an export-only GeoX/CLS adapter surface, but the current MIP P2 consumer contract assigns no construction role to MIP. | A versioned, fail-closed signal artifact that preserves GeoX values and immutable provenance without making the model-specific decision. | Current P2 evidence has not certified the exact producer/adapter pair. MIP may validate, normalize losslessly, route, and verify the artifact, but may not construct it or infer compatibility/treatment. Evidence: MIP P2 consumer contract; MMM GeoX/CLS adapter contract; GeoX source manifest. |
| `CalibrationSignal` → MMM compatibility/treatment | MMM owns experiment-to-model compatibility state, calibration treatment, model lineage, supported range, and failures. | Provenance-linked MMM compatibility and treatment evidence validated against the exact certified producer/contract pair. | Native compatibility code/fixtures exist, but are not certified against the pending producer artifact. Requires a new MMM task after producer certification; neither GeoX nor MIP may declare or replace MMM compatibility. Evidence: MMM compatibility code and calibration-lineage contract. |
| Treatment → full-panel `delta_mu` | MMM owns model execution and the canonical baseline/candidate full-panel comparison. | Typed simulation evidence with exact input lineage, baseline/candidate means, `delta_mu`, supported-range and failure state. | Component contract exists; certified P2 pair and provenance-linked consumer evidence do not. Optimization is outside this edge. Evidence: `MMM:mmm/contracts/public_simulation.py` and versioned fixtures. |
| `delta_mu` → MIP planning evidence | MIP owns orchestration, report assembly, governed explanation, UX, and consumer verification. | Verified bridge, D6 release packet, fixture-only planning journey, then explicit later release decisions. | Bridge blocked; D6 and planning journey are downstream. An LLM may explain only validated artifacts and may not alter the analytical result. Evidence: `MIP:docs/program/NEXT_EXECUTION_SEQUENCE.md`, `PROGRAM_CURRENT_STATE.md`, and P2 consumer design. |

Consumer verification remains required at every repository boundary. Schema
shape alone is insufficient: exact commits, versions, lineage, expected
failures, and authorization flags must agree.

### 6.2 Strictly sequential work

1. GeoX review disposition and current-main health precede producer
   certification because a failing required base gate cannot certify its
   output.
2. GeoX producer certification precedes provenance-linked MMM fixture
   production because MMM cannot truthfully pin a producer artifact that is not
   merged and certified.
3. Certified GeoX evidence, an explicitly named/certified
   `CalibrationSignal` producer/adapter, and MMM-owned compatibility/treatment
   evidence precede resuming/re-authoring the MIP bridge because MIP must
   consume and verify immutable upstream artifacts rather than construct or
   reinterpret their analytical states.
4. The verified MIP bridge precedes D6 evidence; D6 must name the real producer
   and consumer versions, compatibility behavior, release/rollback order, and
   last-known-good set.
5. D6 precedes the fixture-only planning-evidence journey, which in turn
   precedes any claim of end-to-end P2 readiness.
6. Certified analytical artifacts and their lifecycle precede a benchmark that
   claims artifact-grounded analytical correctness.

### 6.3 Safely parallel work

- GeoX may pursue independently authorized method-family investigations that
  do not mutate the P2 source contract, while its defect disposition proceeds.
- MMM may pursue independently authorized internal reliability/calibration
  research on versioned native fixtures without claiming GeoX provenance or
  P2 readiness.
- MIP may design and test deterministic conversational boundaries on immutable
  synthetic or approved public fixtures under the containment in section 7.
- Documentation, benchmark specifications, threat models, and fixture-only
  negative cases may proceed in separate owned paths if separately authorized
  and if they neither change shared semantics nor consume mutable sibling work.

These are parallel only because repository ownership and immutable fixture
boundaries isolate semantic truth. Contract changes, cross-repo fixture claims,
or release claims collapse the isolation and return to the sequential chain.

### 6.4 Advisory eligibility sequence — not authorization

1. Review the exact GeoX reassessment head; authorize and merge any necessary
   defect remediation under GeoX rules.
2. Complete and certify the GeoX combined producer checkpoint on GeoX main.
3. Establish the exact serialized `CalibrationSignal` producer/adapter in the
   certified handoff contract, then authorize MMM provenance-linked
   compatibility/calibration/full-panel `delta_mu` fixture evidence and
   publish it on MMM main. The present evidence does not assign serialization
   to MIP.
4. Re-author or explicitly resume the MIP bridge only after verifying those
   exact merged refs.
5. Produce D6 compatibility, release-order, rollback, last-known-good, and
   ownership evidence.
6. Execute the fixture-only MIP planning-evidence journey.
7. Reconcile capability ledgers only through explicitly owned evidence-refresh
   work, then consider later R3/R4/R5 work.

This ordering describes eligibility. It authorizes no task, branch, repair,
merge, analytical decision, provider promotion, or capability.

## 7. Lane 5 — LLM and artifact-grounding evaluation

MIP main already contains deterministic safety/intake/readiness/configuration,
local orchestration, `MockLLMProvider`, a thin Streamlit shell, typed turn and
handoff contracts, a packaged truth corpus, deterministic retrieval, and a
provider-neutral read-only front door with fake-provider coverage. It also has
concrete provider-adapter work and recorded Groq acceptance/remediation
evidence; none of that promotes a provider. Evidence:
`docs/roadmap/LLM_DECISION_LAYER_ROADMAP.md`,
`docs/roadmap/ROADMAP_EXECUTION_SEQUENCE.md`, and
`docs/architecture/MIP_LLM_*` / `MIP_CONVERSATIONAL_*` artifacts.

| LLM-layer work | Dependency and safe artifact boundary | Current classification and prohibited claim |
|---|---|---|
| Benchmark design | Versioned scenario specification, synthetic or approved public inputs, immutable expected outputs, explicit scoring and refusal cases. | Eligible but unauthorized as a new task. It may run before P2 only if it claims response-boundary quality, not analytical or end-to-end P2 correctness. |
| Deterministic orchestration/response tests | Fake/mock provider; packaged truth corpus; no live GeoX/MMM calls; no customer/real data; no persistent product artifacts. | Safely parallel when separately authorized. It cannot construct analytical truth, recommendations, or provider promotion evidence. |
| Artifact-grounding harness on surrogate fixtures | Clearly labeled synthetic/versioned fixtures with immutable expected values and negative provenance cases. | Eligible but unauthorized for harness mechanics. Results are not certified-engine grounding or R3 completion. |
| Artifact-grounded analytical benchmark | Certified analytical artifacts, resolver/artifact lifecycle, exact provenance, and consumer verification. | Blocked by the P2 chain and artifact-lifecycle prerequisites. Surrogates cannot satisfy this gate. |
| Provider/model/prompt evaluation and promotion | Versioned benchmark plus target-environment operational, safety, fallback, and cost evidence; explicit approval. | Evaluation may be independently authorized within fixture containment. Promotion is blocked/unauthorized; recorded Groq provider failures and structured-wire/domain mapping evidence must not be erased. |
| Package integration | Certified GeoX/MMM artifacts, verified bridge, D6 Gate 1/2 evidence, environment and rollback acceptance. | Blocked. No direct engine orchestration or live-package claim is allowed. |
| Artifact persistence/lifecycle | R2 resolver, identity, versioning, retention, access, invalidation, reconciliation, and security controls. | Deferred/unauthorized unless separately scoped. In-memory or test fixtures must not be represented as persistent product artifacts. |
| Live runtime and recommendations | Completed R3/R4/R5 gates, production-grade artifact truth, recommendation governance, environment acceptance, and named approval. | Deferred and blocked. No real data, autonomous action, recommendation authority, pilot, or production follows from LLM component work. |

Thus some LLM evaluation and infrastructure can safely precede full P2, but
only inside a test-only fixture boundary: immutable synthetic/approved public
fixtures; fake or explicitly test-scoped providers; deterministic expected
outputs; no sibling invocation; no alteration of numerical truth; no customer
data; no durable user artifact; no provider/model/prompt promotion; and no P2,
recommendation, pilot, or production claim. LLM prose is never analytical
authority. Once an evaluation claims grounding in actual GeoX/MMM outputs, it
becomes sequentially dependent on certified artifacts and lifecycle controls.

## 8. Lane 6 — Later recommendation, runtime, pilot, and production work

The canonical MIP roadmap orders P3 LLM/artifact-grounding evaluation, P4
certified package integration, P5 artifact lifecycle, P6 governed simulation
and recommendations, P7 pilot, and P8 production. The R0–R6 gate sequence
requires core benchmark, resolver/artifact lifecycle, artifact-grounded
benchmark, integration release governance, security/operations, and then
pilot/production evidence. Evidence: `MIP:docs/roadmap/ROADMAP.md`,
`MIP_DECISION_LIFECYCLE_ROADMAP_CONSOLIDATION_001.md`,
`AUTHORITY_AND_FREEZE_MATRIX.md`, and `DEFERRED_AND_PARKED_WORK.md`.

Remaining later work includes certified package entrypoints; compatibility and
migration matrices; D6 release and tested rollback packets; persistent artifact
identity/lifecycle; observability, security, and environment acceptance;
scenario/simulation governance; optimizer and recommendation policies; human
review and override; pilot exit criteria; and production release/rollback.
Live GeoX/MMM integration, MIP exports, optimization, recommendations, real
data, external users, pilots, and production remain blocked or deferred. No
component implementation, fixture pass, audit, or LLM evaluation changes those
authority freezes.

## 9. Status summary

| Classification | Work |
|---|---|
| Strictly sequential | GeoX defect disposition → GeoX producer certification → certified contract-defined `CalibrationSignal` serialization → MMM-owned compatibility/treatment and full-panel evidence → MIP consumer bridge → D6 → planning journey → certified artifact-grounded evaluation/integration. |
| Safely parallel within isolation | Repository-local method research; MMM native-fixture reliability work; MIP benchmark design and fake-provider deterministic tests on immutable synthetic/approved public fixtures. |
| Eligible but unauthorized | New GeoX repair/certification tasks after review disposition; MMM provenance task after producer certification; contained MIP benchmark/harness tasks; bridge resume only after its explicit prerequisites and new authority. |
| Blocked | GeoX producer certification by current-main gate failures; cross-repo MMM fixture claim by missing certified producer; MIP bridge by upstream evidence; D6 by bridge; planning journey by D6; certified grounding/package integration by P2 plus lifecycle gates. |
| Deferred | Bayesian/package-side research as recorded; optimizer/recommendation governance; persistent product artifact rollout; live runtime; real-data use; pilot; production. |

## 10. Orientation and handoff prompts

### MIP chat

```text
Synchronize Phani-Pavuluri/marketing_intelligence_platform from Git. Read the
root AGENTS.md and perform its bootstrap, then read EXECUTION_STATE.json,
ACTIVE_TASK.md, REPOSITORY_CONTEXT_INDEX.md, and LATEST_COMPLETION_REPORT.md.
Resolve and verify any exact remote feature branch named by main, including
authorization ancestry. Read the applicable program/roadmap evidence. Treat
MIP_GEOX_MMM_PENDING_WORK_AND_LLM_DEPENDENCY_AUDIT_001 as a dated orientation
snapshot only; freshly fetched Git is authority. Do not infer execution,
merge, analytical, LLM-provider, recommendation, pilot, or production authority
from the audit. Preserve MIP as a lossless consumer/orchestrator: do not assign
it `CalibrationSignal` construction, GeoX-to-MMM compatibility, or calibration
treatment. Report the exact refs and current authorized action before work.
```

When MIP Git contains an authorized executable task, the invocation-only
execution/correction launcher is exactly:

```text
Synchronize from Git and execute the active task.
```

A MIP merge invocation may add only the exact externally approved remote head
SHA to the repository's committed merge invocation. Never use an audit SHA as
approval.

### GeoX chat

```text
Synchronize/fetch Phani-Pavuluri/panel_exp from Git without disturbing local
work. Read the root AGENTS.md and the repository's EXECUTION_STATE.json,
ACTIVE_TASK.md, REPOSITORY_CONTEXT_INDEX.md, and LATEST_COMPLETION_REPORT.md.
If main names an active or resumable branch, fetch that exact remote branch and
verify repository identity, task identity, branch name, and authorization
ancestry before interpreting status. Treat the MIP cross-repository audit as a
dated orientation snapshot only; GeoX Git owns GeoX truth and authority. Do not
resume, repair, merge, certify, or promote anything unless current GeoX Git and
an exact external approval authorize it. Preserve GeoX ownership of readout
truth and handoff eligibility without assigning it MMM model compatibility.
```

GeoX already has a ready-for-review branch at this snapshot; do not issue a new
execution launcher for it. For future work, use only the then-current launcher
model committed in GeoX `AGENTS.md` and execution files. Exact-head review or
merge approval must identify the current remote head and cannot be supplied by
this audit.

### MMM chat

```text
Synchronize/fetch Phani-Pavuluri/MMM from Git without disturbing local work.
Read the root AGENTS.md and the repository's EXECUTION_STATE.json,
ACTIVE_TASK.md, REPOSITORY_CONTEXT_INDEX.md, and LATEST_COMPLETION_REPORT.md.
Resolve any main-declared active/resumable branch from its exact remote ref and
verify identity and authorization ancestry. Treat the MIP cross-repository
audit as dated orientation only; MMM Git owns compatibility, calibration,
model, provenance, simulation, and optimization truth. Report current refs and
authority, preserve `CalibrationSignal` as the governed bridge, and do not
assign its construction or MMM analytical decisions to MIP. Do not execute
merely because the audit calls work eligible.
```

MMM has no authorized task at this snapshot, so there is no execution launcher
to use. First author and authorize a definition-ready repository-local task;
then use only MMM's then-current committed invocation model.

## 11. Cross-repository impact contract and conclusion

- **Affected repositories:** MIP, GeoX, MMM. **Modified repository:** MIP only.
- **Owner:** MIP owns this audit and future consumer/reporting work. GeoX owns
  experiment and producer truth. MMM owns compatibility, calibration/model,
  full-panel `delta_mu`, simulation, and optimization truth.
- **Observed dependency/blocker IDs:** the P2 GeoX producer checkpoint, MMM
  provenance-linked fixture checkpoint, `P2_MIP_GEOX_MMM_COMPATIBILITY_BRIDGE`,
  `P2-D6-RELEASE-COMPATIBILITY-EVIDENCE`, and the fixture-only planning journey,
  as recorded in MIP program state/ledger/sequence. The GeoX branch additionally
  records four named current-main defect classes.
- **Consumer verification still required:** exact producer/consumer commits,
  contract versions, lineage, compatibility states, full-panel evidence,
  failure behavior, release/rollback order, last-known-good versions, and MIP
  fixture-only journey results.
- **Newly clarified eligibility:** contained deterministic LLM benchmark and
  fake-provider harness work can proceed before full P2 only under section 7's
  boundaries. This is not task authorization.
- **Validation debt:** GeoX's 15 reproduced base failures; pending producer
  combined validation/certification; MMM provenance-linked cross-repo evidence;
  bridge/D6/planning validation; certified artifact-grounding and environment
  acceptance.
- **Authority impact:** none. No analytical/runtime/capability authority flag,
  coordination state, contract, fixture, product behavior, or sibling state is
  changed.

The present critical path is not “wait for all LLM work.” Deterministic LLM
quality mechanics can be isolated and separately authorized now, while any
claim grounded in live analytical truth must wait for certified GeoX truth and
handoff eligibility → contract-defined `CalibrationSignal` serialization →
MMM-owned compatibility/treatment and full-panel evidence → MIP consumer
verification and planning evidence. MIP does not compute or replace any of the
upstream analytical states. Every successor requires fresh Git verification
and its own repository-local authorization.
