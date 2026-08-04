# Active Task

**Status:** authorized
**Owner:** MIP program governance
**Last updated:** 2026-08-03
**Last verified:** 2026-08-03

## Identity

- **Task ID:** `MIP_GIT_AUTHORITATIVE_THIN_LAUNCHER_STANDARD_002`
- **Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
- **Pre-authoring base:** `45eca4e8ca75bd9f152c2d025f9c57773dfa27ee`
- **Feature branch:** `docs/mip-git-authoritative-thin-launcher-standard-002`
- **Execution mode:** `branch_and_fast_forward`
- **Risk tier:** Tier 1 — repository execution-governance guidance and focused semantic tests
- **Superseded predecessor:** `MIP_GIT_AUTHORITATIVE_THIN_LAUNCHER_STANDARD_001`
- **Predecessor preserved branch head:** `6e90f1a23b5ff952264e15e634b469be06f52c56`
- **Predecessor final rejected head:** `69f7fd7178844576b8a3bdb84a881b3d38a3b8c5`
- **Historical corrected candidate:** `0e08dc1f77f91ce45e45d1f874c5ae505dfea129`
- **Capability authorizations changed:** `false`

## Primary independently mergeable outcome

Replace MIP's currently merged invocation-only Codex prompt rule with one unambiguous Git-authoritative thin-launcher standard, and enforce that standard with direct canonical-block and current-lifecycle-coherence tests.

This task is intentionally smaller than its superseded predecessor. It owns only:

1. replacement of the invocation-only guidance;
2. publication of the three exact canonical launcher blocks;
3. direct tests of those blocks and their prohibited task-instance values; and
4. coherent current lifecycle state across the three stable execution files.

It changes no product, analytical, contract, adapter, fixture, orchestration, LLM, UI, roadmap, coordination, sibling-repository, release, or capability behavior.

## Why this task cannot be split further

The guidance and its semantic tests form one contract. Updating only the documentation would leave the obsolete behavior unenforced. Updating only the tests would preserve contradictory repository guidance. Current-state coherence must be validated in the same merge unit because the predecessor failed specifically by publishing contradictory lifecycle metadata.

## Orientation and eligibility evidence

Connected GitHub established:

- MIP `main` is `45eca4e8ca75bd9f152c2d025f9c57773dfa27ee` before authoring this successor.
- `MIP_GIT_AUTHORITATIVE_THIN_LAUNCHER_STANDARD_001` is superseded without merge. Its branch and candidate implementation are historical evidence only and have no task, correction, merge, or PR authority.
- MMM `main` is `f2e0eade0ad917c1b28ab5521e6d35a35047d988`. `MMM_GIT_AUTHORITATIVE_THIN_LAUNCHER_STANDARD_ADOPTION_001` is proposed and blocked pending an exact merged MIP standard. MIP cannot authorize or modify that task.
- GeoX `main` is `e9b7d311ecaf5a90e227d8299f745a0e8f332368`. `GEOX_EXECUTION_BRANCH_BINDING_REAUTHORING_001` is superseded without merge. MIP cannot authorize or modify GeoX work.
- No live sibling task owns MIP's execution-standard files.

No roadmap or coordination rewrite is required. This is a bounded MIP repository-execution correction.

## Exact observable behavior

### 1. Replace the invocation-only rule

`AGENTS.md` must remove the heading and assertions that:

- Codex prompts are invocation-only;
- execution and correction must use only `Synchronize from Git and execute the active task.`; or
- the thin launcher is merely optional alongside the older rule.

It must instead state that Git is the sole durable task authority and that thin launchers may carry only stable operational execution control. Prompt text cannot define, repair, expand, override, or reinterpret Git-authored task meaning. Missing or contradictory Git instructions remain a fail-closed blocker.

### 2. Publish exactly three canonical launcher blocks

`docs/execution/TASK_EXECUTION_STANDARD.md` must contain the following exact fenced launcher bodies. Apart from Markdown heading and fence syntax, the body text must match exactly.

#### Canonical execution launcher

```text
Work in <local repository path>.

Synchronize main from Git and read AGENTS.md and the repository execution files. Resolve authorization provenance and the exact feature branch from synchronized main, then fetch and resume that remote feature branch and read its current execution files.

Execute the active task through implementation, required validation, exact-tree publication, push, and remote-head verification.

Progress updates are non-terminal. Do not stop or return control merely to report orientation or progress. Stop only when the remote feature branch durably records ready_for_review or a genuine blocked state.

Do not create a pull request, merge, or change capability authority.
```

#### Canonical correction launcher

```text
Work in <local repository path>.

Synchronize main from Git and read AGENTS.md and the repository execution files. Resolve authorization provenance and the exact feature branch from synchronized main, then fetch and resume that remote feature branch and read its current execution files.

Execute the Git-authored changes_requested correction through the complete required validation, a new exact-tree publication, push, and remote-head verification.

Progress updates are non-terminal. Do not stop or return control merely to report orientation or progress. Stop only when the remote feature branch durably records a new ready_for_review or a genuine blocked state.

Do not create a pull request, merge, or change capability authority.
```

#### Canonical merge launcher

```text
Work in <local repository path>.

Synchronize main from Git and read AGENTS.md and the repository execution files. Execute the active task's merge and closure workflow.

Approved exact remote head: <FULL_SHA>

Revalidate the approved head, fast-forward merge only, validate after fast-forward, push main, perform task-branch cleanup, create exactly one closure commit, and verify local and remote main equality.

Do not create a pull request, squash, rebase, force-push, or create a merge commit.
```

### 3. Preserve Git-only task meaning

Execution and correction launcher blocks may contain no task-instance data. The merge launcher may contain only the local-path placeholder and `<FULL_SHA>` approval placeholder.

The canonical blocks must not contain:

- the current task ID or any concrete task ID;
- the concrete feature branch or any concrete branch name;
- any actual 40-character SHA;
- owned or prohibited repository paths;
- test commands, test names, counts, validation gates, or implementation decisions;
- dependency or blocker IDs;
- rejected or retained heads;
- MMM or GeoX repository names, task IDs, lifecycle state, or checkpoints; or
- copied scope, correction findings, or completion-report content.

Exact equality to the frozen canonical bodies is the primary enforcement. Explicit negative assertions against current task-instance values are also required.

### 4. Enforce one coherent current lifecycle state

When `EXECUTION_STATE.json` records `ready_for_review`:

- `ACTIVE_TASK.md` must have exactly one current status of `ready_for_review`;
- `LATEST_COMPLETION_REPORT.md` must have exactly one current decision of `ready_for_review`;
- `correction_execution_authorized` must be `false`;
- the same non-null implementation SHA must appear in all three files;
- blockers must be empty;
- merge and PR authority must be false;
- no Markdown heading at levels one through six may contain `changes requested`, `required correction`, or `correction authorization`;
- no operative text may say a correction cycle is authorized, correction execution remains authorized, publication is unfinished, or a validation receipt is missing.

Prior rejected heads may remain only in a clearly non-operative `Historical provenance` section. Historical prose must not instruct execution or present a current required correction.

Equivalent coherent rules must remain for `blocked` and `merged` states. Status distinctions must remain fail-closed.

### 5. Preserve main and feature-branch authority

Synchronized `main` remains authority for repository identity, task identity, authorization provenance, and the declared feature branch. The verified remote feature branch remains authority for current lifecycle state, blockers, implementation evidence, and completion report. A stale lifecycle snapshot on `main` is not a terminal outcome after the exact authorized branch is safely verified.

### 6. Preserve terminal and authority boundaries

After a safe executable branch is verified, orientation and progress reports are non-terminal. Execution stops only after the remote branch durably records `ready_for_review` or a genuine `blocked` state.

No PR, merge, squash, rebase, force-push, merge commit, sibling adoption, analytical change, or capability change is authorized by task execution.

## Named acceptance evidence

Update `tests/governance/test_repo_native_execution_handoff.py` with separate focused tests that establish:

1. **Replacement rule** — obsolete invocation-only wording and the exact one-line execution rule are absent; Git-authoritative thin-launcher guidance is present.
2. **Exact canonical bodies** — extract each fenced block under its exact heading and compare its normalized body to the frozen canonical body from this task.
3. **Direct prohibited-instance enforcement** — inspect each extracted block directly; reject the current task ID, concrete branch, actual SHAs, owned paths, test commands/names/counts, dependency/blocker IDs, sibling names/state, and any other task-instance value. Reject any 40-character SHA in execution/correction blocks and allow only the literal `<FULL_SHA>` placeholder in the merge block.
4. **Current-state coherence** — validate the three stable execution files together. Inspect Markdown headings at levels one through six and reject operative correction headings or stale correction-authority wording in `ready_for_review` state.
5. **Semantic-group separation** — launcher-body tests, task-instance prohibition tests, and lifecycle-state tests remain separate functions. Do not hide lifecycle assertions inside the duplication test.
6. Existing bootstrap, authoring-boundary, exact-tree receipt, resumed-branch, validation, terminal, merge, and authority invariants continue to pass.

The tests must validate behavior, not merely the presence of descriptive prose.

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

- roadmap, coordination, product, contract, adapter, fixture, orchestration, LLM, report, dashboard, UI, release, security, runtime, or deployment files;
- MMM or GeoX repositories, branches, tasks, standards, or authority;
- analytical or numerical truth;
- the preserved predecessor branch; or
- package versions or CI workflows.

Do not copy or merge the predecessor branch wholesale. Specific useful wording may be independently reimplemented only where it satisfies this task and the current exact tree passes all validation.

Do not create a PR, merge, squash, rebase, force-push, merge commit, or delete historical branches.

## Validation gate

This Tier-1 task requires on the frozen exact task-owned tree:

- parse `docs/execution/EXECUTION_STATE.json` as JSON;
- verify Markdown/current-state consistency using the strengthened focused test;
- prove the task-authoring range changes only `ACTIVE_TASK.md` and `LATEST_COMPLETION_REPORT.md`, followed immediately by a state-only `EXECUTION_STATE.json` authorization commit;
- verify exact changed paths against the six owned paths;
- run `git diff --check`;
- run `poetry run pytest -q tests/governance/test_repo_native_execution_handoff.py` and record the exact count;
- run configured Ruff for `tests/governance/test_repo_native_execution_handoff.py`;
- run configured mypy for `tests/governance/test_repo_native_execution_handoff.py`;
- inspect the final exact-tree receipt trailers;
- prove local and remote feature-branch head equality after push; and
- verify no task-owned file changes after the receipt commit.

Docker-backed `make validate` and the full suite are `not_required` because this changes only repository guidance, execution metadata, and one focused semantic test. Discovery of a runtime or broader executable dependency is a blocker, not permission to widen scope.

## Task-authoring and authorization boundaries

- Pre-authoring base: `45eca4e8ca75bd9f152c2d025f9c57773dfa27ee`.
- The authoring range may change only `docs/execution/ACTIVE_TASK.md` and `docs/execution/LATEST_COMPLETION_REPORT.md`.
- The final authoring commit is recorded as `authorization_head_sha` by the immediate next state-only commit.
- The immediate next commit may change only `docs/execution/EXECUTION_STATE.json` and authorize the exact declared feature branch.
- Create the feature branch from the resulting synchronized state-only `main` head.
- No other path or commit may occur between the authoring boundary and state-only authorization.

## Publication contract

On success publish one remote `ready_for_review` head containing:

- one implementation SHA and one exact-tree receipt;
- exact focused-test count plus Ruff, mypy, JSON, Markdown, boundary, changed-path, and diff-check results;
- Docker/full-suite disposition `not_required`;
- empty blockers;
- task execution true and correction execution false;
- correction cycle counts consistent with actual history;
- merge and PR authority false;
- null reviewed and approval SHAs;
- unchanged capability authority;
- GitHub-observed evidence separated from locally reported validation;
- limitations, validation debt, sibling impact, consumer-verification disposition, and newly eligible work;
- exact local/remote branch-head equality; and
- no operative correction heading or stale correction-authority wording.

A genuine external Git, authentication, filesystem, environment, missing-history, or required-validation obstruction may publish Git-durable `blocked` with exact diagnostics and a live resolution condition. Task-owned implementation or test failures are unfinished work and must be corrected within scope.

## Execution invocation for this successor

Until this task is merged, the currently merged MIP rule remains invocation-only. Execute this task using exactly:

`Synchronize from Git and execute the active task.`

Do not add task details, branch names, SHAs, validation commands, workflow steps, or correction content to the Codex prompt. All durable instructions are in Git.

## Deferred successors and sibling impact

- MMM's proposed adoption remains blocked. After this task is merged, MMM must verify the new exact MIP pin and separately update or reauthorize its own proposal; MIP does not authorize that work.
- GeoX adoption remains separately owned and unauthorized.
- `MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_CONTRACT_001` remains the next intended product/integration task after this execution-standard task is merged and closed, subject to fresh live-Git orientation and separate authorization.
- No additional prompt, receipt, lifecycle, navigation, roadmap, or coordination framework is authorized by this task.

**Unresolved execution-blocking design questions: none.**
