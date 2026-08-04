# Active Task

**Status:** ready_for_review
**Owner:** MIP program governance
**Last updated:** 2026-08-03
**Last verified:** 2026-08-03

## Identity

- **Task ID:** `MIP_GIT_AUTHORITATIVE_THIN_LAUNCHER_STANDARD_001`
- **Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
- **Pre-authoring base:** `976d3a1daeae9c52c8772e5112574f698951a57c`
- **Feature branch:** `docs/mip-git-authoritative-thin-launcher-standard-001`
- **Execution mode:** `branch_and_fast_forward`
- **Risk tier:** Tier 1 — repository execution-governance guidance and focused semantic test
- **Superseded predecessor task:** `MIP_P2_ROADMAP_AND_COORDINATION_RECONCILIATION_AFTER_GEOX_SUPERSESSION_001`
- **Superseded predecessor branch head:** `0629af616943c53e8d4a275dec147624bb9e040c`
- **Capability authorizations changed:** `false`

## Primary independently mergeable outcome

Replace MIP's overly strict invocation-only Codex prompt contract with a
Git-authoritative thin-launcher standard.

Git remains the sole durable source for task identity, scope, behavior, owned
paths, acceptance evidence, dependencies, validation, correction details,
authority, and stop conditions. The launcher may carry only stable operational
control needed for reliable execution: repository location, synchronization,
Git reads, exact branch resumption, continuation through durable publication,
non-terminal progress semantics, terminal outcomes, prohibited PR/merge actions,
and the externally approved exact SHA for merge.

This task changes no product, analytical, contract, adapter, fixture,
orchestration, LLM, UI, sibling-repository, or capability behavior.

## Why this task cannot be split further

The allowed launcher boundary, canonical execution/correction/merge launchers,
main-versus-feature-branch authority, progress and terminal semantics, and the
focused invariant test form one execution contract. Updating only guidance or
only tests would preserve contradictory behavior. MMM and GeoX adoption are
separate owner-repository successor tasks and are not part of this merge unit.

## Orientation and eligibility evidence at authorization

Connected GitHub established:

- MIP `main` is `976d3a1daeae9c52c8772e5112574f698951a57c`.
- `MIP_P2_ROADMAP_AND_COORDINATION_RECONCILIATION_AFTER_GEOX_SUPERSESSION_001`
  is superseded without merge on its preserved branch at
  `0629af616943c53e8d4a275dec147624bb9e040c`; it has no remaining task,
  correction, merge, or PR authority.
- MMM `main` is `b8878dfa4bcd178a0472c3b812492a5bb4ac0b45`; its separate protocol-adoption
  branch is `ready_for_review` at
  `c370dc7cd59a61cc2e19025d1a2328c7867b63be` and still targets the older
  invocation-only MIP standard. MIP cannot modify, approve, supersede, or merge
  that MMM work.
- GeoX `main` is `0a463ad96cda31dc2bdc962fd24f5481bb7aede9`; its branch-binding reauthoring
  branch records `changes_requested` at
  `377050f76ddc03d6feb6f4f75eb2c9c9f8c954d1`. It does not overlap MIP-owned
  files or authority.
- No live sibling task owns this MIP execution-standard surface.

A roadmap audit is not required: this is a direct correction to observed
executor reliability and does not change the P0–P8 product sequence.

## Exact observable behavior

### 1. Preserve Git as sole durable task authority

`AGENTS.md` and `docs/execution/TASK_EXECUTION_STANDARD.md` must state that the
launcher cannot define, repair, expand, override, or reinterpret task meaning.
The following remain Git-only:

- task ID, lifecycle state, authorization provenance, and feature branch;
- scope, observable behavior, owned/prohibited paths, and implementation decisions;
- acceptance criteria, exact validation commands/counts, dependencies, blockers,
  correction details, rejected or retained heads, and sibling state;
- authority, release, merge, cleanup, and terminal requirements.

Missing or contradictory Git-authored instructions remain a fail-closed blocker.

### 2. Allow only thin operational prompt content

A launcher may contain only:

- the local repository path;
- synchronization and required repository reads;
- resolution and resumption of the exact Git-declared feature branch;
- instruction to continue through implementation, required validation,
  exact-tree publication, push, and remote-head verification;
- explicit non-terminal progress semantics;
- the permitted durable terminal outcomes;
- prohibition on PR, merge, force operations, or capability changes as applicable;
- the exact externally approved remote head SHA for merge.

It must not copy task IDs, branch names, authorization or implementation SHAs,
rejected heads, scope, paths, tests, counts, dependencies, correction details,
implementation guidance, or sibling lifecycle state from chat. The approved
merge SHA is the sole task-instance value normally permitted externally.

### 3. Canonical execution launcher

The MIP standard must publish this canonical pattern:

```text
Work in <local repository path>.

Synchronize main from Git and read AGENTS.md and the repository execution files. Resolve authorization provenance and the exact feature branch from synchronized main, then fetch and resume that remote feature branch and read its current execution files.

Execute the active task through implementation, required validation, exact-tree publication, push, and remote-head verification.

Progress updates are non-terminal. Do not stop or return control merely to report orientation or progress. Stop only when the remote feature branch durably records ready_for_review or a genuine blocked state.

Do not create a pull request, merge, or change capability authority.
```

The placeholder may be replaced only by the actual local repository path.

### 4. Canonical correction launcher

The MIP standard must publish this canonical pattern:

```text
Work in <local repository path>.

Synchronize main from Git and read AGENTS.md and the repository execution files. Resolve authorization provenance and the exact feature branch from synchronized main, then fetch and resume that remote feature branch and read its current execution files.

Execute the Git-authored changes_requested correction through the complete required validation, a new exact-tree publication, push, and remote-head verification.

Progress updates are non-terminal. Do not stop or return control merely to report orientation or progress. Stop only when the remote feature branch durably records a new ready_for_review or a genuine blocked state.

Do not create a pull request, merge, or change capability authority.
```

Rejected SHAs and correction details must be resolved from Git and must not be
copied into this launcher.

### 5. Canonical merge launcher

The MIP standard must publish this canonical pattern:

```text
Work in <local repository path>.

Synchronize main from Git and read AGENTS.md and the repository execution files. Execute the active task's merge and closure workflow.

Approved exact remote head: <FULL_SHA>

Revalidate the approved head, fast-forward merge only, validate after fast-forward, push main, perform task-branch cleanup, create exactly one closure commit, and verify local and remote main equality.

Do not create a pull request, squash, rebase, force-push, or create a merge commit.
```

The local path and externally approved exact remote SHA are the only values
filled by the caller. All other merge and closure semantics remain Git-authored.

### 6. Preserve main and feature-branch authority

The guidance must preserve:

- synchronized `main` as authority for repository identity, task identity,
  authorization provenance, and declared feature branch; and
- the verified remote feature branch as authority for current lifecycle state,
  blockers, correction state, implementation evidence, and completion report.

The launcher may direct this resolution process but may not provide cached task
identity or branch state.

### 7. Progress is explicitly non-terminal

Orientation and progress updates are user-visible checkpoints only. They do not
return control, satisfy the task, or replace repository publication. After a
safe authorized branch is verified, the executor continues until the remote
branch durably records `ready_for_review` or a genuine `blocked` state with its
required evidence and resolution condition.

### 8. Preserve review, merge, and authority boundaries

Exact-head external review, risk-tier validation, exact-tree receipts,
fast-forward-only merge, one closure commit, branch cleanup, and local/remote
verification remain unchanged. The launcher does not create merge authority.
No PR, squash, rebase, force-push, merge commit, sibling adoption, or capability
change is authorized by this task.

## Named acceptance evidence

Update `tests/governance/test_repo_native_execution_handoff.py` with separate
semantic assertions covering:

1. `test_git_authoritative_thin_launcher_preserves_git_only_task_meaning` — Git
   remains authoritative and launchers cannot duplicate or repair durable task
   meaning.
2. `test_execution_and_correction_launchers_are_operational_and_non_terminal` —
   both launchers include path, synchronization, main-to-branch resolution,
   continuation, push/remote verification, non-terminal progress, durable
   terminal outcomes, and no PR/merge/capability action.
3. `test_merge_launcher_requires_only_path_and_approved_exact_sha` — merge uses
   the external exact SHA while all validation, fast-forward, closure, cleanup,
   synchronization, and prohibited-operation semantics remain enforced.
4. `test_launchers_forbid_task_instance_duplication` — task IDs, branch names,
   non-approved SHAs, scope, paths, tests/counts, dependencies, correction
   details, implementation instructions, and sibling state remain prohibited.
5. Existing bootstrap, exact-tree receipt, resumed-branch, validation, terminal,
   and authority invariants continue to pass.

Equivalent names are acceptable only if the four new semantic groups remain
separate and explicit.

## Owned paths

Implementation may modify only:

1. `AGENTS.md`
2. `docs/execution/TASK_EXECUTION_STANDARD.md`
3. `tests/governance/test_repo_native_execution_handoff.py`
4. `docs/execution/ACTIVE_TASK.md`
5. `docs/execution/EXECUTION_STATE.json`
6. `docs/execution/LATEST_COMPLETION_REPORT.md`

Do not modify any other path.

## Prohibited scope

Do not modify:

- roadmap, coordination, product, contract, adapter, fixture, orchestration,
  LLM, report, dashboard, UI, release, security, or capability files;
- MMM or GeoX repositories, branches, standards, tasks, or authority;
- analytical or numerical truth;
- the preserved superseded P2 branch; or
- package versions, CI workflows, runtime configuration, or deployment state.

Do not create a PR, merge, squash, rebase, force-push, merge commit, or delete
historical branches.

## Validation gate

This Tier-1 task requires on the frozen exact task-owned tree:

- parse `docs/execution/EXECUTION_STATE.json` as JSON;
- verify Markdown/current-state consistency;
- prove the task-authoring range changes only `ACTIVE_TASK.md` and
  `LATEST_COMPLETION_REPORT.md`, followed immediately by a state-only
  `EXECUTION_STATE.json` authorization commit;
- verify exact changed paths against the six owned paths;
- run `git diff --check`;
- run `pytest -q tests/governance/test_repo_native_execution_handoff.py` and
  record the exact count;
- run Ruff and configured mypy for the changed test file;
- inspect the final exact-tree validation-receipt trailers; and
- prove local/remote feature-branch head equality after push.

Docker-backed `make validate` and the full suite are `not_required` because this
changes only repository guidance, execution metadata, and one focused semantic
test. Discovery of a runtime or broader executable dependency is a blocker, not
permission to widen scope.

## External review decision — changes requested

- **Rejected exact remote head:** `e390f1b47f8a7c5dfaa7a05613c2c4de73e4a548`
- **Retained implementation SHA:** `dde6969b1192b97aea519c9589d27186f19b6db2`
- **Review state:** `changes_requested`
- **Correction execution:** one bounded correction cycle authorized
- **Merge and PR authority:** `false`
- **Capability authority:** unchanged

### Required correction

1. Remove the contradictory invocation-only contract from `AGENTS.md`. It must
   not say that Codex prompts remain invocation-only or that the exact execution
   invocation remains `Synchronize from Git and execute the active task.` The
   Git-authoritative thin launcher is the replacement standard, not an optional
   overlay on the superseded one-line rule.
2. Strengthen the focused tests so they enforce the replacement semantically:
   the old invocation-only and exact one-line requirements must be absent; the
   canonical execution, correction, and merge launcher contracts and their
   allowed/prohibited instance values must be asserted directly; and the four
   new semantic groups must remain separate rather than inheriting unrelated
   lifecycle assertions accidentally.
3. Refresh live sibling evidence before publication. MMM `main` is now
   `ac546548784385baab67d7c935e5a4fcdfc9e1af` with
   `MMM_REPOSITORY_EXECUTION_PROTOCOL_ADOPTION_001` merged at reviewed head
   `c370dc7cd59a61cc2e19025d1a2328c7867b63be`; that merge adopted the older
   standard and requires a future MMM-owned successor after this MIP standard
   merges. GeoX `main` is now
   `e9b7d311ecaf5a90e227d8299f745a0e8f332368`, and
   `GEOX_EXECUTION_BRANCH_BINDING_REAUTHORING_001` is superseded without merge
   with preserved branch head `9d0da6bb96dd7711ab8c91bbef21a80a4b816973`.
4. Run the complete frozen Tier-1 gate on the corrected exact tree, publish a
   new implementation SHA and exact-tree receipt, push, verify remote-head
   equality, and stop only at a new durable `ready_for_review` or genuine
   `blocked` state.

The passing locally reported focused tests at the rejected head do not satisfy
acceptance because the assertions preserve the superseded rule and do not catch
the contradiction. Do not merge or approve the rejected head.

## Task-authoring and authorization boundaries

- Pre-authoring base: `976d3a1daeae9c52c8772e5112574f698951a57c`.
- The authoring range may change only `docs/execution/ACTIVE_TASK.md` and
  `docs/execution/LATEST_COMPLETION_REPORT.md`.
- The final authoring commit is recorded as `authorization_head_sha` by the
  immediate next state-only commit.
- The immediate next commit may change only
  `docs/execution/EXECUTION_STATE.json` and authorizes the exact declared branch.
- Create the feature branch from the synchronized state-only `main` head.
- No other path or commit may occur between the authoring boundary and state-only
  authorization.

## Publication contract

On success publish one remote `ready_for_review` head containing:

- one implementation SHA and one exact-tree receipt;
- exact focused-test, Ruff, mypy, JSON, Markdown, boundary, changed-path, and
  diff-check results;
- Docker/full-suite disposition `not_required`;
- empty blockers;
- task execution true and correction execution false;
- merge and PR authority false;
- null reviewed and approval SHAs;
- unchanged capability authority;
- GitHub-observed evidence separated from locally reported validation;
- limitations, validation debt, sibling impact, and consumer-verification
  disposition; and
- exact local/remote branch-head equality.

A genuine external Git, authentication, filesystem, environment, missing-history,
or required-validation obstruction may publish Git-durable `blocked` with exact
diagnostics and a live resolution condition. Task-owned implementation or test
failures are unfinished work and must be corrected within scope.

## Deferred successors

- MMM has now merged the older invocation-only adoption on `main` at
  `ac546548784385baab67d7c935e5a4fcdfc9e1af`. MMM may separately authorize a
  successor adoption only after this corrected MIP standard is merged; MIP does
  not authorize or modify that work.
- GeoX has superseded its branch-binding reauthoring task without merge on
  `main` at `e9b7d311ecaf5a90e227d8299f745a0e8f332368`. Any future adoption remains a
  separate GeoX-owned authorization after this corrected MIP standard is merged.
- P2 coordination reconciliation, GeoX governed-readout capability, MMM
  normalization/fixtures, and MIP fixture-only planning remain separate tasks.
- No additional prompt, receipt, lifecycle, or navigation framework is
  authorized by this task.

**Unresolved execution-blocking design questions: none.**

## Corrected publication result

- **Implementation SHA:** `0e08dc1f77f91ce45e45d1f874c5ae505dfea129`
- **Review state:** `ready_for_review`
- **Correction execution:** closed
- **Blockers:** none
- **Merge and PR authority:** `false`
- **Capability authority:** unchanged

The final publication commit is the frozen exact-tree validation receipt. The
MMM merged older-standard adoption and GeoX superseded branch-binding task are
read-only sibling facts only; each future adoption remains separately owned and
unauthorized.
