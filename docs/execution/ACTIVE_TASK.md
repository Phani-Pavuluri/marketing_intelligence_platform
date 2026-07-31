# Active Task

**Status:** ready for review
**Owner:** MIP program governance
**Last updated:** 2026-07-31
**Last verified:** 2026-07-31

## Identity

- **Task ID:** `MIP_CROSS_REPOSITORY_COORDINATION_CONTROL_PLANE_001`
- **Pre-authoring base:** `main` / `4ddbe8323de6af44086da34001ec60072b58c1e8`
- **Feature branch:** `docs/mip-cross-repository-coordination-control-plane-001`
- **Execution mode:** `branch_and_fast_forward`
- **Supersedes before execution:** `MIP_P2_CROSS_REPOSITORY_READINESS_RECONCILIATION_001`
- **Current MIP checkpoint:** `4ddbe8323de6af44086da34001ec60072b58c1e8`
- **Current MMM checkpoint:** `1b75d1d3c9f49d40f2b7ab71f524fbd2dc6d1421`
- **Current GeoX checkpoint:** `e0cef94c063b03b29e1e1760fb1c2320ce497b56`
- **Capability authorizations changed:** `false`

## Why the prior task is superseded

The prior readiness reconciliation would refresh stale checkpoints and publish a
one-time sequence, but it would not prevent future coordination drift. MIP,
MMM, and GeoX need a durable Git-native mechanism that tells every arm:

- what each repository is working on now;
- what it completed recently and at which exact closure SHA;
- which cross-repository blockers are open, in progress, awaiting consumer
  verification, resolved, or superseded;
- which tasks depend on those blockers;
- what becomes eligible when evidence is merged;
- where ownership lies so two repositories do not implement the same contract,
  adapter, policy, or analytical responsibility;
- when a cached coordination snapshot is stale and must not be trusted.

This replacement task includes the readiness reconciliation but adds the
coordination protocol and state needed for ongoing program execution.

## Purpose

Create the MIP-owned cross-repository coordination control plane while keeping
each repository authoritative for its own execution state and completion
report. The coordination layer is a verified, pinned program view; it never
overrides live sibling Git state.

This is documentation, governance, machine-readable coordination state, and
focused consistency testing only. It does not implement P2 consumers, engine
contracts, adapters, package entrypoints, simulations, recommendations,
orchestration, or runtime integration.

## Source-of-truth and staleness rules

1. Each repository's synchronized `main`, `docs/execution/EXECUTION_STATE.json`,
   `ACTIVE_TASK.md`, and `LATEST_COMPLETION_REPORT.md` remain authoritative for
   that repository.
2. MIP owns the cross-repository coordination snapshot and dependency ledger.
3. Every repository entry in the coordination snapshot must record the exact
   observed remote-main SHA and evidence paths.
4. If live remote `main` differs from the recorded SHA, the coordination entry
   is stale. Agents must re-read the sibling repository directly and may not
   infer status from the stale snapshot.
5. A producer task marked completed does not automatically resolve a consumer
   blocker. Resolution requires merged producer evidence and the declared
   consumer-verification condition.
6. Chats, pasted summaries, local feature branches, and unmerged files are not
   coordination authority.

## Prerequisites and source evidence

Complete the mandatory bootstrap in `AGENTS.md`, prove local
`main == origin/main`, and verify the task-authoring boundary.

Verify current remote mains and read the stable execution files in all three
repositories:

- MIP: `Phani-Pavuluri/marketing_intelligence_platform@4ddbe8323de6af44086da34001ec60072b58c1e8`;
- MMM: `Phani-Pavuluri/MMM@1b75d1d3c9f49d40f2b7ab71f524fbd2dc6d1421`;
- GeoX: `Phani-Pavuluri/panel_exp@e0cef94c063b03b29e1e1760fb1c2320ce497b56`.

Read at minimum:

- all three repositories' `AGENTS.md`;
- all three repositories' stable execution files;
- MIP `PROGRAM_CURRENT_STATE.md`, `REPOSITORY_CHECKPOINTS.md`,
  `NEXT_EXECUTION_SEQUENCE.md`, `DECISION_REGISTER.md`, and P2 consumer design;
- MMM `mmm/contracts/calibration_compatibility.py` and current producer evidence;
- GeoX `panel_exp/contracts/geox_governed_experiment_readout.py` and current
  governed-readout evidence.

Compare the prior MIP-recorded engine checkpoints to current engine `main` and
separate workflow-only changes from product-contract changes.

## Owned files

Execution may modify only:

- `AGENTS.md`;
- `docs/execution/TASK_EXECUTION_STANDARD.md`;
- `docs/execution/REPOSITORY_CONTEXT_INDEX.md`;
- `docs/program/CROSS_REPOSITORY_COORDINATION_PROTOCOL.md`;
- `docs/program/CROSS_REPOSITORY_COORDINATION_STATE.json`;
- `docs/program/CROSS_REPOSITORY_COORDINATION_HISTORY.md`;
- `docs/program/PROGRAM_CURRENT_STATE.md`;
- `docs/program/REPOSITORY_CHECKPOINTS.md`;
- `docs/program/NEXT_EXECUTION_SEQUENCE.md`;
- `docs/program/DECISION_REGISTER.md`;
- `docs/roadmap/MIP_P2_CROSS_REPOSITORY_READINESS_RECONCILIATION_001.md`;
- `tests/test_cross_repository_coordination_control_plane.py`;
- `docs/execution/ACTIVE_TASK.md`;
- `docs/execution/EXECUTION_STATE.json`;
- `docs/execution/LATEST_COMPLETION_REPORT.md`.

No other path is authorized. Do not modify MMM or GeoX.

## Required coordination artifacts

### 1. Coordination protocol

Add `docs/program/CROSS_REPOSITORY_COORDINATION_PROTOCOL.md` defining:

- source precedence and stale-snapshot behavior;
- repository ownership boundaries;
- workstream identity and duplicate-work prevention;
- dependency and blocker lifecycle;
- producer-completion versus consumer-verification distinction;
- required cross-repository impact section in task completion reports;
- task proposal, execution, review, closure, and coordination refresh rules;
- how new chats and Codex sessions orient across repositories;
- no capability authority from coordination metadata.

Before any cross-repository-affecting task is proposed, the proposing arm must
read the live execution state and latest completion report from all affected
repositories, then check the coordination ledger for overlapping active
workstreams and ownership conflicts. An unresolved overlap is a blocker, not an
invitation to duplicate implementation.

### 2. Machine-readable coordination state

Add `docs/program/CROSS_REPOSITORY_COORDINATION_STATE.json` with a strict,
deterministic schema containing at least:

- schema version, program ID, coordinator repository, and verification date;
- exact observed MIP, MMM, and GeoX remote-main SHAs;
- per-repository active task ID/status, current work summary, latest completed
  task and closure SHA, next eligible tasks, validation debt, and authority
  boundary;
- workstreams with unique IDs, owner repository, capability area, task ID,
  status, dependencies, blocked/unblocked tasks, evidence paths, and verified
  SHA;
- blockers with unique IDs, owner, affected consumers, state, evidence,
  resolution criteria, consumer-verification requirement, and tasks unblocked;
- ordered program sequence;
- explicit stale-state behavior.

Allowed blocker states must distinguish at least:

- `open`;
- `in_progress`;
- `producer_completed_pending_consumer_verification`;
- `resolved`;
- `superseded`.

Resolved blockers must cite merged evidence and the required consumer
verification. No blocker may be resolved solely because a task report says
"completed."

### 3. Coordination history

Add `docs/program/CROSS_REPOSITORY_COORDINATION_HISTORY.md` as an append-only,
human-readable ledger of material program events. Seed it with:

- MIP V2 workflow closure;
- MMM V2 workflow closure;
- GeoX import-health recovery and V2 workflow closure;
- the current P2 readiness reconciliation;
- exact closure SHAs and cross-repository impact;
- historical/nonconforming merge events only where they remain relevant to
  execution governance.

Git history preserves every version, but this ledger must let a fresh chat see
recent program progression without reconstructing all commits.

## Required program reconciliation

Update MIP program memory to current exact pins and classify the P2 dependencies
using stable IDs. At minimum record:

- `P2-GEOX-TEMPORAL-VERSION-SEMANTICS`;
- `P2-GEOX-READOUT-BUILDER-ENTRYPOINT`;
- `P2-MMM-GEOX-NORMALIZATION`;
- `P2-MMM-CROSS-REPOSITORY-FIXTURES`;
- `P2-D6-RELEASE-COMPATIBILITY-EVIDENCE`.

Reverify each against current Git. Preserve only blockers actually supported by
current evidence. Separate blockers from unrelated validation debt, including
the unresolved full GeoX suite.

Update:

- `PROGRAM_CURRENT_STATE.md`;
- `REPOSITORY_CHECKPOINTS.md`;
- `NEXT_EXECUTION_SEQUENCE.md`;
- `DECISION_REGISTER.md` only for newly supported decisions;
- `REPOSITORY_CONTEXT_INDEX.md`.

The current proposed sequence must become:

1. this MIP coordination-control-plane task;
2. `GEOX_CROSS_REPOSITORY_COORDINATION_PROTOCOL_ADOPTION_001` and
   `MMM_CROSS_REPOSITORY_COORDINATION_PROTOCOL_ADOPTION_001` in parallel;
3. `GEOX_GOVERNED_READOUT_TEMPORAL_VERSION_AND_ENVELOPE_SEMANTICS_001`;
4. `GEOX_GOVERNED_READOUT_BUILDER_ENTRYPOINT_001`;
5. `MMM_GEOX_READOUT_NORMALIZATION_AND_CROSS_REPOSITORY_FIXTURES_001`;
6. `MIP_P2_FIXTURE_ONLY_PLANNING_EVIDENCE_JOURNEY_001`;
7. D6 reconciliation and fixture-only cross-repository dry run;
8. separate authorization before live package integration.

The protocol-adoption tasks are proposed only; do not modify sibling repos or
authorize those tasks here.

## MIP bootstrap and execution-standard changes

Update MIP `AGENTS.md` and `TASK_EXECUTION_STANDARD.md` so every new or resumed
MIP task that affects another repository must:

1. read the coordination protocol and state;
2. verify recorded sibling SHAs against connected GitHub;
3. read live sibling execution state and completion reports when a recorded SHA
   is stale or the task depends on that sibling;
4. check for overlapping workstream IDs and ownership conflicts;
5. record dependency IDs in the active task;
6. include a cross-repository impact section in the completion report;
7. leave coordination state unchanged unless the task owns a verified refresh.

Future GeoX and MMM adoption tasks must apply equivalent bootstrap rules in
those repositories.

## Cross-repository completion impact contract

The protocol must require every task affecting another arm to report:

- affected repositories;
- workstream ID and capability owner;
- dependency/blocker IDs created, advanced, resolved, or superseded;
- exact merged evidence SHA and paths;
- consumer verification still required;
- newly eligible tasks;
- validation debt introduced or retired;
- authority impact.

This is coordination metadata only. It cannot declare analytical compatibility,
production readiness, or consumer acceptance without the owning repository's
evidence.

## Focused test requirements

Add `tests/test_cross_repository_coordination_control_plane.py` verifying:

- exact current MIP/MMM/GeoX pins appear in coordination and program files;
- stale old engine pins are historical, not current;
- repository/workstream/blocker IDs are unique;
- every dependency and `unblocks` reference resolves to a declared ID/task;
- no two active workstreams claim the same owner/capability area;
- every resolved blocker has merged evidence and consumer verification;
- coordination entries contain exact observed SHAs and evidence paths;
- bootstrap rules require live sibling verification and duplicate-work checks;
- current P2 blocker IDs and ordered follow-on tasks are present;
- workflow completion is not equated with product readiness;
- runtime integration, recommendations, optimization, production, and
  package-side-agent authority remain blocked or false.

## Validation gate

Run:

- the new focused coordination test;
- relevant existing execution, documentation, and governance tests;
- JSON parsing and Markdown/path consistency checks;
- Ruff and mypy for changed Python files;
- `git diff --check`;
- exact changed-path verification;
- Docker-backed `make validate` on the exact feature-branch tree.

Record exact pass/skip/warning counts. On any prerequisite or validation
failure, publish an accurate `blocked` state and stop.

## State transition and completion

On success:

- publish `ready_for_review`;
- record the full implementation SHA;
- keep task execution authorized and merge authorization false;
- keep reviewed and approval SHAs null;
- keep blockers empty;
- keep capability authorizations unchanged;
- push and verify the exact remote feature head;
- stop without a PR, merge, or branch deletion.

The completion report must record the superseded unexecuted readiness task, the
new coordination artifacts, exact live pins, blocker decisions, workstream and
dependency state, validation, limitations, proposed sibling adoption tasks, and
authority impact.

## Acceptance criteria

- Every arm can discover current work, recent completion, blockers, dependencies,
  next eligibility, validation debt, and ownership from Git.
- A stale MIP coordination snapshot fails closed and triggers direct sibling
  orientation.
- Duplicate or overlapping cross-repository work is detected before task
  authorization.
- Blocker resolution requires producer evidence and declared consumer
  verification.
- MIP program memory uses current exact pins.
- The P2 sequence and ownership are explicit.
- No product, analytical, runtime, recommendation, optimization, treatment,
  pilot, production, or agent capability is introduced or authorized.
- Full validation passes or the task stops blocked.

## Prohibited actions

Implementation, validation, and publication are complete. The exact remote
review head must receive separate external approval before any merge session.
No pull request, merge, branch deletion, sibling modification, or capability
authorization is permitted while this task remains `ready_for_review`.

Do not modify MMM or GeoX. Do not create a PR. Do not merge, squash, rebase,
force-push, or delete branches. Do not implement P2 consumers, adapters, engine
contracts, package entrypoints, orchestration, LLM behavior, persistence,
uploads, real data, simulations, recommendations, optimization, or production
paths.
