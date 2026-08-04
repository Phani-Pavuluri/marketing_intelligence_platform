# MIP Repository Execution Handoff V2

**Status:** active execution standard
**Owner:** MIP program governance
**Last updated:** 2026-07-30
**Last verified:** 2026-07-30
**Verified against:** authorized task boundary
`f83e91ef883af88808e03184b96bea26fba5eef8`
**Update trigger:** an approved execution-governance change.

## Source precedence

1. Synchronized Git repository state and committed behavior.
2. `docs/program/` canonical state.
3. `docs/execution/` active task and execution state.
4. Active contracts, roadmaps, ADRs, and validation evidence.
5. Archived or superseded documents.
6. Chats and pasted summaries.

A lower-ranked source cannot override a higher-ranked one. Repository evidence
is not synchronized until the bootstrap below passes.

## Mandatory session bootstrap

Every new or resumed session must perform this sequence before task discovery:

1. Resolve the repository root, `origin`, and expected repository identity.
2. Inspect `git status --porcelain=v1 --untracked-files=all`.
3. Fail on unrelated tracked changes. During an authorized resumption, every
   tracked change must be task-owned and explained.
4. Permit local-only untracked paths only below `.codex/` and `docs/tasks/`.
   Never stage or commit them. Fail on every other unexpected untracked path.
5. Run `git fetch --prune origin`.
6. If the clone is shallow, use `git fetch --unshallow origin`; if a required
   ancestor is still absent, fetch sufficient additional history and verify the
   required commit explicitly.
7. Run `git switch main`.
8. Run `git pull --ff-only origin main`.
9. Prove `git rev-parse main` equals `git rev-parse origin/main`.
10. Only then read `EXECUTION_STATE.json`, `ACTIVE_TASK.md`, the context index,
    relevant program files, prerequisites, and sibling-repository checkpoints.

Missing credentials, remote refs, history, Docker, dependencies, or verifiable
state is a blocker. Do not substitute cached chat context.

## Stable paths, task authoring, and default mode

Exactly one current copy exists at `docs/execution/ACTIVE_TASK.md`,
`docs/execution/LATEST_COMPLETION_REPORT.md`, and
`docs/execution/EXECUTION_STATE.json`. Future tasks replace these files in
place; Git history preserves prior versions.

### Required delivery shape

Every future MIP task must declare only its primary mergeable outcome, risk
tier, why it cannot be split further, owned paths, focused validation, and
deferred successor tasks. Authors must stop and split work when a meaningful
portion can be validated and merged independently. Apply
`docs/program/LEAN_REPOSITORY_DELIVERY_STANDARD.md` for the tier and its
minimum validation; this does not weaken Git authority, exact-head review,
ownership, or authority boundaries.

After explicit user authorization, task authoring may replace only those three
stable files on `main`. The task's `base_sha` identifies the pre-authoring
content base. The synchronized post-authoring `main` is the
`authorization_head_sha`; its `base_sha..authorization_head_sha` diff must
contain only those three files. Create the feature branch from the authorization
head, never from stale local state.

### Definition-ready executable authorization

Before an executable MIP task is authorized, its stable active task must define
one primary mergeable outcome; exact observable behavior and preserved
boundaries; resolved design, schema, authority, and policy decisions; and
inputs/outputs appropriate to the changed surface. It must also define failure
semantics, named acceptance tests or deterministic evidence, owned paths and
prohibited scope, focused validation, and deferred successors.

Compatibility or migration policy is required only when public contracts,
versions, persisted artifacts, or migration surfaces change; otherwise it must
be explicitly `not_applicable`. Public API, schema, state-machine, and migration
work must define their relevant signatures, fields/types/invariants,
transitions/failures, or source/target/rollback behavior. Surface proportionality
does not permit an executable task to omit decisions material to its changed
surface.

An executable authorization requires `unresolved execution-blocking design
questions: none`. If a material decision remains unresolved, retain `proposed`,
mark it design-blocked, or split a bounded decision/evidence task. Codex must
not select among materially different contract meanings during implementation.
This MIP rule does not authorize MMM or GeoX adoption; each is a separately
authorized owner-repository decision.

The default mode is `branch_and_fast_forward`:

```text
task proposed → user authorization → stable task metadata on main
→ synchronized feature-branch execution → completion report
→ ready_for_review → exact remote-head review and external approval
→ validation → fast-forward implementation → push and cleanup
→ one closure commit → synchronized merged state
```

No pull request is required. `direct_to_main` is permitted only when the active
task explicitly authorizes it.

## Statuses and fail-closed rules

Allowed V2 statuses are `idle`, `proposed`, `authorized`, `in_progress`,
`blocked`, `ready_for_review`, `changes_requested`, `merged`, and `superseded`.
`approved_for_merge` is a legacy V1 persisted state and is not used in V2.

Codex must stop if synchronization fails; main differs from remote main; the
task-authoring boundary contains other paths; task status is not executable;
task authorization is false; a prerequisite is absent; task/state disagree;
the branch does not match; unrelated tracked changes or unexpected untracked
paths exist; scope or authority is exceeded; required validation cannot
complete; exact-head approval is absent; main moved; or the remote feature head
changes after approval. Proposed, implemented, or validated never means
authorized.

## Execution and completion reporting

Execution remains within owned files. Before review, Codex writes the completion
report with:

- task, repository, execution mode, base, authorization head, feature branch,
  implementation commit, and exact published review head;
- task-authoring boundary and prerequisite evidence;
- changed files, deliverables, and acceptance results;
- each validation category marked `passed`, `failed`, `blocked`, or
  `not_required`, including focused checks, full suite, Ruff, mypy,
  `git diff --check`, Docker-backed `make validate`, and GitHub-observed versus
  local evidence;
- limitations, deferred work, authority impact, merge readiness, and local-only
  paths.

For a task affecting MMM or GeoX, the active task and completion report must
also identify affected repositories, workstream and capability owner,
dependency/blocker IDs advanced or resolved, merged evidence SHA/paths,
consumer verification still required, newly eligible work, validation debt, and
authority impact. Before authoring or executing it, agents must read the MIP
coordination protocol/state, verify affected sibling remote mains, and stop on
stale snapshots or duplicate ownership.

The published feature branch ends at `ready_for_review` with
`task_execution_authorized: true`, `merge_authorized: false`,
`reviewed_head_sha: null`, and `approval_commit_sha: null`. The exact review head
is the remote branch ref; it cannot be embedded in its own commit.

### Operative risk-tier validation

The active task's declared risk-tier gate controls execution, exact-head review,
and post-fast-forward validation. Tier 1 may use its explicitly declared narrow
documentation/governance gate. Tier 2 uses the focused and surface-required
validation stated by its task. Docker-backed full validation is mandatory for
Tier 3 and whenever the active task, changed public/analytical/package surface,
or another repository-authored gate requires it. A required category that cannot
run is `blocked`; a category outside the applicable gate is `not_required`.

### Durable exact-tree publication receipt

Before `ready_for_review`, freeze the task-owned tree and run the active task's
applicable validation gate on that exact tree. `LATEST_COMPLETION_REPORT.md`
must distinguish GitHub-observed repository evidence from locally observed
command results and record deliverables, validation-category statuses and exact
counts, blockers, limitations, validation debt, sibling impact, and authority
impact.

The final review-publication commit message is the durable validation receipt
for that commit's exact tree. It identifies the implementation parent, gate,
results, changed-path evidence, worktree state, evidence source, and authority
impact. The receipt need not self-reference its own SHA: Git cryptographically
binds its message to the exact tree. No task-owned file may change after the
receipt commit; any change requires a new validated publication head. Review
uses this Git evidence and must not depend on pasted terminal or chat output.

## Git-authoritative thin launcher contract

Launchers are operational only; Git remains the sole durable source for task
meaning. The execution launcher must direct synchronization, reading execution
files, main-to-feature-branch resolution, implementation, validation,
exact-tree publication, push, remote-head verification, non-terminal progress,
durable `ready_for_review` or `blocked`, and no PR/merge/capability action. The
correction launcher differs only by directing the Git-authored `changes_requested`
correction. The merge launcher may additionally carry only the approved exact
remote head SHA; all validation, fast-forward, closure, cleanup, and authority
semantics remain Git-authored.

### Canonical execution launcher

```text
Work in <local repository path>.

Synchronize main from Git and read AGENTS.md and the repository execution files. Resolve authorization provenance and the exact feature branch from synchronized main, then fetch and resume that remote feature branch and read its current execution files.

Execute the active task through implementation, required validation, exact-tree publication, push, and remote-head verification.

Progress updates are non-terminal. Do not stop or return control merely to report orientation or progress. Stop only when the remote feature branch durably records ready_for_review or a genuine blocked state.

Do not create a pull request, merge, or change capability authority.
```

### Canonical correction launcher

```text
Work in <local repository path>.

Synchronize main from Git and read AGENTS.md and the repository execution files. Resolve authorization provenance and the exact feature branch from synchronized main, then fetch and resume that remote feature branch and read its current execution files.

Execute the Git-authored changes_requested correction through the complete required validation, a new exact-tree publication, push, and remote-head verification.

Progress updates are non-terminal. Do not stop or return control merely to report orientation or progress. Stop only when the remote feature branch durably records a new ready_for_review or a genuine blocked state.

Do not create a pull request, merge, or change capability authority.
```

### Canonical merge launcher

```text
Work in <local repository path>.

Synchronize main from Git and read AGENTS.md and the repository execution files. Execute the active task's merge and closure workflow.

Approved exact remote head: <FULL_SHA>

Revalidate the approved head, fast-forward merge only, validate after fast-forward, push main, perform task-branch cleanup, create exactly one closure commit, and verify local and remote main equality.

Do not create a pull request, squash, rebase, force-push, or create a merge commit.
```

Prompts must not restate durable scope, owned paths, behavior, validation,
workflow, cleanup, or stop conditions. Those instructions belong in committed Git state.
Prompt text cannot repair, expand, override, or reinterpret an incomplete active
task. Missing Git-authored instructions are a fail-closed blocker, not authority
to supplement the task from chat. This MIP rule does not authorize MMM or GeoX
adoption; each remains a separately authorized owner-repository decision.

## Successful-orientation terminal outcomes

After successful orientation establishes an executable task and safe authorized
branch, continue without another user prompt through implementation, validation,
publication, and push. The only terminal outcomes are `ready_for_review` with a
durable receipt or Git-durable `blocked` with blocker, attempted evidence,
validation status, and resolution condition. An orientation-only, chat-only, or
“no changes made” summary is invalid completion evidence. External stopping is
allowed only when no safe authorized write target exists and must explain why.

## Resumed feature-branch state

Synchronize `main` first and obtain task ID, authorization head, and feature
branch from its committed state. Verify the declared remote feature branch's
repository identity, task ID, branch name, and ancestry. Main remains authority
for authorization provenance; the verified feature branch is authority for the
latest resumed lifecycle state, blockers, implementation SHA, and report. Do
not stop on a stale main lifecycle snapshot. Fail closed on mismatches or
inconsistent evidence, and publish `blocked` to the safe authorized branch when
one exists; terminal or chat output is not a completion report.

## Exact-head approval and merge

Approval is an external user decision that names or unambiguously accepts the
exact remote feature-branch head SHA reported for review. No pre-merge
approval-metadata commit is created. Persisted `merge_authorized` remains false
until closure because changing it would change the reviewed branch.

A merge session must:

1. Complete the mandatory bootstrap and verify unchanged
   `authorization_head_sha` on `main`.
2. Fetch the remote feature branch and prove its head equals the approved SHA.
3. Verify the approved head descends from the authorization head and its diff is
   limited to owned files.
4. Run the active task's required risk-tier gate on the exact approved tree,
   including Docker-backed `make validate` whenever it is required.
5. Run `git switch main` and `git merge --ff-only <approved-sha>`.
6. Rerun that required gate on the fast-forwarded tree, push `main`, and prove
   local and remote main equal the approved implementation head.
7. Delete the remote feature branch, delete the local feature branch where
   present, and observe the cleanup results.

Any mismatch stops the merge. A pull request, squash, rebase, merge commit, or
force update does not satisfy this workflow.

## Single closure commit

After the approved implementation is on remote `main` and cleanup has been
observed, update only the stable task/state/report files and create exactly one
post-merge closure commit. It records:

- approval source and exact reviewed head;
- authorization head and implementation/merged-main head;
- validation evidence and GitHub/local synchronization;
- validation-category statuses for the execution, exact-head, and
  post-fast-forward gates;
- branch-cleanup results;
- limitations, deferred work, and authority impact.

The merged state sets both authorization booleans false, preserves
`approval_commit_sha: null`, and records the reviewed head. Validate the closure
metadata, push the one closure commit, and again prove local main equals remote
main. The closure commit does not authorize a product or engine capability.
