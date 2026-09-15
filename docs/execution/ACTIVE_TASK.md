<!-- BEGIN MIP TASKCTL EXECUTION VIEW -->
# Active Task

**Status:** ready_for_review

_Generated from `EXECUTION_STATE.json`; do not edit._

- **Task ID:** `MIP_GEOX_MMM_PENDING_WORK_AND_LLM_DEPENDENCY_AUDIT_001`
- **Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
- **Execution mode:** `branch_and_fast_forward`
- **Base SHA:** `b0f57701a55d5cbe1d94692bf378a23d03945646`
- **Authorization provenance:** `688dbe6d780d12a8e8964524326439f16729c746`
- **Feature branch:** `audit/mip-geox-mmm-pending-work-and-llm-dependency-audit-001`
- **Feature branch created:** `true`
- **Task execution authorized:** `true`
- **Correction execution authorized:** `false`
- **Merge authorized:** `false`
- **PR creation authorized:** `false`
- **Implementation commit:** `3d323478320400c34fe9454b796fb638d9ac2eae`
- **Reviewed head:** `null`
- **Rejected review head:** `null`
- **Rejected implementation commit:** `null`
- **Approval commit:** `null`
- **Blockers:** `none`
- **Maximum correction cycles:** `1`
- **Correction cycles completed:** `0`
- **Correction cycles remaining:** `1`
- **Review decision:** `ready_for_review`
- **Local feature-branch cleanup:** `null`
- **Remote feature-branch cleanup:** `null`
- **Capability authorizations changed:** `false`
<!-- END MIP TASKCTL EXECUTION VIEW -->

## Primary outcome

Create one Git-authoritative MIP coordination audit at
`docs/audits/MIP_GEOX_MMM_PENDING_WORK_AND_LLM_DEPENDENCY_AUDIT_001.md` that
reconstructs the remaining work across MIP, GeoX, and MMM from freshly fetched
repository evidence and explains exactly how that work gates, or can proceed in
parallel with, the MIP LLM layer.

The audit is a read-only evidence and sequencing milestone. It must distinguish
observed state, dependency eligibility, repository-local authorization, and
capability authority. It does not execute, authorize, repair, certify, or change
any analytical, integration, LLM, runtime, pilot, or production capability.

## Why this is one independently reviewable outcome

Repository state, analytical-roadmap state, P2 integration state, and LLM
dependency state must be reconciled in one artifact because the central audit
question is the relationship among them. Splitting the inventory from the
dependency/parallelism analysis or from the handoff prompts would produce an
incomplete and potentially misleading coordination view. Any implementation,
state refresh, task authorization, methodology change, or runtime change is an
independent successor and is excluded.

## Authoring evidence and live concurrency boundary

Task authoring observed:

- MIP `origin/main` at `b0f57701a55d5cbe1d94692bf378a23d03945646`,
  with `MIP_EXECUTION_LIFECYCLE_SINGLE_SOURCE_CONSISTENCY_001` merged and
  `poetry run python -m mip.execution.taskctl check` passing;
- GeoX `origin/main` at `2111cfb2197ea62531919791a1e794a5f601ee6e`;
- GeoX lifecycle-authoritative branch
  `origin/audit/geox-main-test-isolation-and-checkpoint-context-reassessment-001`
  at `0f79d277afac4a8675bc3a1365ae89c6da8dcbf9`, descending from authorization
  head `b003d7915d635413fd45fcb98e4ee36ccbc0c7b8`, with task
  `GEOX_MAIN_TEST_ISOLATION_AND_CHECKPOINT_CONTEXT_REASSESSMENT_001` at
  `ready_for_review`, one correction cycle consumed, and four current-main
  validation-defect classes reported;
- MMM `origin/main` at `fe8e784923994406a2e4907d28debd872d61fd73`,
  with `MMM_EXECUTION_AUTHORITY_CLOSURE_CONSISTENCY_FIX_001` merged and no
  declared active remote task branch.

These are authoring observations, not frozen execution truth. The audit executor
must fetch all three remotes again and report the newly observed exact SHAs.
GeoX activity is live concurrent work: do not modify, supersede, sequence inside,
or treat its feature branch as merged evidence. If the branch moves, is merged,
is rejected, becomes blocked, or disappears, use the repository's current Git
evidence and preserve the authoring observation as provenance.

## Required evidence bootstrap

Perform the root `AGENTS.md` bootstrap exactly and run
`poetry run python -m mip.execution.taskctl check` before audit work. Re-fetch
GeoX and MMM without modifying their worktrees. Read each sibling's root
`AGENTS.md`, `EXECUTION_STATE.json`, `ACTIVE_TASK.md`,
`REPOSITORY_CONTEXT_INDEX.md`, and `LATEST_COMPLETION_REPORT.md` from exact
remote refs. When a synchronized sibling main declares an active or resumable
feature branch, inspect that exact remote branch and verify repository identity,
task identity, declared branch, authorization ancestry, and remote head.

At minimum, use these MIP sources:

- `docs/execution/EXECUTION_STATE.json`
- `docs/execution/ACTIVE_TASK.md`
- `docs/execution/REPOSITORY_CONTEXT_INDEX.md`
- `docs/execution/LATEST_COMPLETION_REPORT.md`
- `docs/program/LEAN_REPOSITORY_DELIVERY_STANDARD.md`
- `docs/program/CROSS_REPOSITORY_COORDINATION_PROTOCOL.md`
- `docs/program/CROSS_REPOSITORY_COORDINATION_STATE.json`
- `docs/program/CROSS_REPOSITORY_COORDINATION_HISTORY.md`
- `docs/program/PROGRAM_CURRENT_STATE.md`
- `docs/program/NEXT_EXECUTION_SEQUENCE.md`
- `docs/program/P2_CAPABILITY_CHECKPOINT_LEDGER.json`
- `docs/program/AUTHORITY_AND_FREEZE_MATRIX.md`
- `docs/program/DEFERRED_AND_PARKED_WORK.md`
- `docs/program/REPOSITORY_CHECKPOINTS.md`
- `docs/roadmap/ROADMAP.md`
- `docs/roadmap/ROADMAP_EXECUTION_SEQUENCE.md`
- `docs/roadmap/LLM_DECISION_LAYER_ROADMAP.md`
- `docs/roadmap/LLM_REASONING_AND_MODEL_GUIDANCE_ROADMAP.md`
- `docs/roadmap/PLATFORM_COMPLETION_GAPS_ROADMAP.md`
- `docs/roadmap/MIP_P2_CONSUMER_CONTRACT_AND_FIXTURE_JOURNEY_DESIGN_001.md`

Use the sibling context indexes to select current methodological, validation,
contract, roadmap, investigation, and fixture evidence. The source set must
include GeoX method-soundness/promotion/production-readiness and calibration
source evidence, and MMM platform/reliability/calibration/provenance/public
simulation evidence. Do not rely on filename inventories alone: read the
evidence supporting every material conclusion.

Git source precedence is mandatory. Synchronized remote repository evidence
outranks coordination snapshots, roadmaps, archives, task documents in another
repository, and chat. A feature branch can describe mutable lifecycle state but
cannot satisfy a merged dependency.

## Required audit structure

The audit must have a dated evidence header with exact MIP, GeoX, and MMM remote
main SHAs; exact lifecycle-authoritative feature-branch names and heads where
present; commands or Git operations used to verify them; and an explicit
snapshot/freshness limitation.

It must explicitly separate these six lanes:

1. repository execution-governance work;
2. GeoX methodological roadmap;
3. MMM methodological roadmap;
4. P2 cross-repository integration;
5. LLM/artifact-grounding evaluation; and
6. later recommendation/runtime/pilot/production work.

For every repository, record current task, lifecycle status, exact authoritative
ref/head, execution/correction/merge/PR authority, capability authority,
blockers, correction state, validation debt, recently completed prerequisites
that materially affect eligibility, and the evidence path/ref for each claim.
Separate current branch lifecycle from merged-main capability truth.

## Required remaining-work inventory

The audit must identify and evidence, without inventing task authority:

- remaining GeoX methodological, validation, current-main defect remediation,
  producer-certification, calibration-source, and P2 integration work;
- remaining MMM methodological/reliability, GeoX compatibility, calibration,
  provenance, full-panel delta-mu, public simulation/optimization, and P2
  integration work;
- remaining MIP P2 integration, parked bridge, D6, planning-evidence, LLM
  benchmark/evaluation, package integration, artifact lifecycle, recommendation,
  pilot, and production work;
- completed or superseded items that materially change current eligibility; and
- validation debt, deferred work, and frozen authority that must not be mistaken
  for unfinished implementation.

Do not flatten roadmap aspiration, implemented code, component validation,
producer certification, consumer verification, merged capability, and execution
authorization into one state. Where committed sources disagree because a
snapshot is stale, apply the coordination protocol's live overlay and cite both
the stale claim and the higher-precedence live resolution.

## Dependency and parallelism analysis

Render and explain the exact analytical chain:

```text
GeoX governed experiment/calibration-source evidence
→ MIP-owned CalibrationSignal mapping/governance boundary
→ MMM calibration compatibility and treatment
→ MMM baseline-versus-candidate full-panel delta-mu evidence
→ MIP planning-evidence assembly and governed explanation
```

The audit must map every edge to exact repository evidence and identify the
owner, required input artifact/contract, output, validation or certification
gate, consumer verification, current blocker, and authority boundary. It must
not construct a `CalibrationSignal`, run calibration, simulate, optimize, or
claim that a proposed/ready-for-review branch satisfies a merged prerequisite.

Classify remaining work as:

- strictly sequential, with the exact prerequisite and why it cannot overlap;
- safely parallel, with the isolation boundary that prevents semantic drift;
- eligible but unauthorized, naming the repository-local authority still
  required;
- blocked, naming the exact blocker and live resolution condition; or
- deferred, naming the governing roadmap/gate.

Every sequential-versus-parallel conclusion must be justified. The recommended
eligibility sequence must be explicitly labeled advisory and must not be
represented as task, merge, analytical, or capability authorization.

## Deterministic work versus LLM work

State exactly which LLM-layer activities depend on certified analytical truth
and which may safely proceed earlier. Any pre-P2 LLM evaluation or infrastructure
work may be described as safely parallel only when evidence supports explicit
containment such as versioned synthetic or approved public fixtures, immutable
expected outputs, no live MMM/GeoX invocation, no construction or alteration of
analytical truth, no customer or real data, no persistent product artifacts, no
provider/model/prompt promotion, no recommendation authority, and no claim of
end-to-end P2 readiness.

Distinguish benchmark design, deterministic orchestration/response-boundary
tests, artifact-grounding evaluation, provider/model/prompt promotion, package
integration, artifact persistence, and live runtime. For each, state its
prerequisites, permitted fixture/artifact boundary, prohibited claims, and
whether it is blocked, eligible-but-unauthorized, or deferred. Do not infer that
LLM work is safe merely because it does not compute numerical truth.

## Handoff and launch material

Include ready-to-use orientation/handoff prompts for separate MIP, GeoX, and MMM
chats. Each prompt must instruct the future chat to synchronize/fetch Git, read
that repository's root `AGENTS.md` and execution files, resolve any exact remote
feature branch, and treat the audit as a dated orientation snapshot rather than
authority. The prompts must not embed mutable task meaning as an override.

Include future Codex launch instructions only where consistent with the target
repository's committed execution model. MIP execution/correction must use the
invocation-only text `Synchronize from Git and execute the active task.`; a MIP
merge launcher may add only the exact externally approved remote head SHA.
For GeoX and MMM, quote or faithfully point to their then-current committed
launcher model without broadening scope or authority. If no task is authorized,
provide orientation text, not an execution launcher.

## Inputs, outputs, invariants, and failure semantics

- **Inputs:** freshly fetched exact remote refs and the committed evidence named
  above, including any lifecycle-authoritative sibling branch.
- **Output:** only
  `docs/audits/MIP_GEOX_MMM_PENDING_WORK_AND_LLM_DEPENDENCY_AUDIT_001.md`, plus
  the required MIP lifecycle publication updates.
- **Invariants:** MIP owns the audit; GeoX and MMM remain read-only; Git authority
  and repository ownership are preserved; no product/analytical truth,
  capability semantics, coordination ledger, or runtime behavior changes.
- **Compatibility/migration:** `not_applicable`; no API, schema, state machine,
  persisted artifact, version, or migration changes.
- **Failure semantics:** stale/unfetchable refs, missing required history,
  inconsistent task/branch identity or ancestry, an ownership/workstream
  conflict, unsupported dependency claims, or inability to run a required gate
  must fail closed. If a safe authorized MIP branch exists, publish a durable
  `blocked` state with exact evidence and a live resolution condition.

Unresolved execution-blocking design questions: none.

## Owned paths

Implementation may change only:

- `docs/audits/MIP_GEOX_MMM_PENDING_WORK_AND_LLM_DEPENDENCY_AUDIT_001.md`
- `docs/execution/EXECUTION_STATE.json`
- the generated lifecycle block in `docs/execution/ACTIVE_TASK.md`
- `docs/execution/LATEST_COMPLETION_REPORT.md`

The stable execution files are lifecycle publication paths, not additional audit
deliverables. No coordination-state refresh is required or authorized.

## Prohibited scope

Do not modify GeoX or MMM; authorize or execute sibling tasks; alter product or
analytical truth; repair GeoX defects; certify a producer; construct
`CalibrationSignal`; run MMM calibration, fitting, simulation, or optimization;
resume or modify the parked MIP bridge; change P2 capability semantics; modify
LLM prompts/providers/runtime behavior; implement evaluation or infrastructure;
change packages, contracts, schemas, fixtures, code, tests, CI, hooks, Docker,
roadmaps, ledgers, coordination state, or repository standards; use real or
customer data; create persistent product artifacts; make recommendations;
authorize pilot/production; or modify any capability-authority flag.

Do not create a PR, merge, squash, rebase, force-push, cherry-pick, create a
merge commit, or modify/delete any sibling branch. Do not resume
`feat/mip-p2-geox-mmm-compatibility-fixture-bridge-001`.

## Acceptance evidence

The completed artifact and report must prove:

1. all three remote mains were freshly fetched and recorded at exact SHAs;
2. every main-declared active/resumable sibling branch was checked at its exact
   remote head with identity and authorization ancestry verified;
3. repository ownership boundaries were preserved and sibling worktrees/files
   were not changed;
4. the six required lanes are visibly separate;
5. each repository's current lifecycle, authority, blockers, corrections,
   validation debt, recent prerequisites, and remaining work are evidence-linked;
6. every dependency edge and blocked/eligible/deferred classification maps to an
   exact Git ref and repository path;
7. sequential and parallel work are explicitly justified;
8. recommendation order is labeled eligibility guidance, never authorization;
9. pre-P2 LLM work, if any, has explicit artifact/fixture containment and
   prohibited-claim boundaries;
10. handoff prompts force future chats to re-read Git and do not treat the audit
    snapshot as authority;
11. no coordination state, analytical/runtime behavior, capability semantics,
    or authority flag changed; and
12. changed paths are limited to the owned MIP paths.

The completion report must include the protocol's cross-repository impact
contract: affected/modified repositories, workstream and capability owner,
dependency/blocker IDs observed or clarified, exact evidence refs/paths,
consumer verification still required, newly eligible work, validation debt, and
authority impact. Observing or recommending a successor never authorizes it.

## Validation

On the frozen exact implementation tree run and record:

```bash
poetry run python -m mip.execution.taskctl check
python3 -m json.tool docs/execution/EXECUTION_STATE.json >/dev/null
git diff --check
git diff --name-only <authorization-head>...HEAD
make validate
```

Also perform a manual link/ref/evidence review of every SHA, branch, task ID,
dependency, blocker, and path in the audit; verify local/remote MIP branch-head
equality; record sibling pre/post worktree status and remote refs proving no
sibling file changes; and classify each validation category as `passed`,
`failed`, `blocked`, or `not_required`. Tier 3 and this task require the full
Docker-backed repository gate.

## Deferred successors

All execution implied by the audit is deferred to separately authored and
repository-locally authorized tasks, including GeoX defect remediation and
producer certification; MMM compatibility/calibration/provenance/simulation or
optimization; the parked MIP bridge, D6, and planning journey; LLM benchmark or
infrastructure implementation; package integration; artifact lifecycle;
recommendations; real-data runtime; pilot; and production. The audit may refine
eligibility order but must not pre-authorize or silently define those tasks.

## Git workflow and stop condition

Execute only on
`audit/mip-geox-mmm-pending-work-and-llm-dependency-audit-001` from the exact
finalized synchronized authorization baseline. Create one independently
reviewable audit implementation and a final exact-tree validation receipt,
transition with explicit evidence to `ready_for_review`, push, verify the exact
remote head, and stop for external exact-head review.

No audit implementation occurs during task authoring. No PR or merge is
authorized.
