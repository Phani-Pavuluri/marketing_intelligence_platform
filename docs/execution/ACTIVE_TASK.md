# Active Task

**Status:** changes_requested
**Owner:** MIP program governance
**Last updated:** 2026-08-03
**Last verified:** 2026-08-03

## Identity

- **Task ID:** `MIP_LEAN_REPOSITORY_DELIVERY_STANDARD_001`
- **Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
- **Feature branch:** `docs/mip-lean-repository-delivery-standard-001`
- **Rejected review head:** `9f829c3e12ca79698c6cabda1e8089e9d4567fa1`
- **Prior correction implementation commit:** `9dda47f3f90877161175c02a736694d5ee253f48`
- **Risk tier:** Tier 1 — documentation and governance guidance only
- **Capability authorizations changed:** `false`

## Review decision

The lean task-sizing standard and operative risk-tier validation rules are
accepted. Exact head `9f829c3e12ca79698c6cabda1e8089e9d4567fa1`
is rejected only because its final validation results exist in Codex-local
terminal output but are not durably recoverable from Git.

A reviewer must not need pasted chat or terminal output to determine the exact
commands run, test counts, changed-path checks, validation debt, worktree state,
or authority impact for a published review head.

## Primary mergeable correction outcome

Make final validation evidence repository-durable before `ready_for_review` by
requiring the review-publication commit itself to carry the exact-tree validation
receipt. Preserve the existing lean workflow; do not introduce a new resolver,
automation framework, task schema, status file, or checkpoint system.

This is one outcome because the execution rule and the current task's durable
receipt close the same verified handoff gap.

## Correction-owned paths

Correction execution may modify only:

1. `AGENTS.md`
2. `docs/execution/TASK_EXECUTION_STANDARD.md`
3. `docs/execution/ACTIVE_TASK.md`
4. `docs/execution/EXECUTION_STATE.json`
5. `docs/execution/LATEST_COMPLETION_REPORT.md`

Do not modify the lean standard, context index, tests, Makefiles, resolver or
automation code, coordination files, contracts, product/runtime/analytical code,
MMM, or GeoX.

## Required correction

### 1. Durable publication rule

Update `AGENTS.md` and `TASK_EXECUTION_STANDARD.md` so that:

- the task-owned tree is frozen before final publication validation;
- the task-authorized risk-tier gate runs on the exact tree to be published;
- locally observed command results and GitHub-observed evidence are clearly
  distinguished;
- `LATEST_COMPLETION_REPORT.md` records deliverables, validation categories,
  exact counts, blockers, limitations, validation debt, sibling impact, and
  authority impact;
- the final review-publication commit message is the durable validation receipt
  for that commit's exact Git tree;
- no task-owned file may change after that publication commit; any change
  invalidates the receipt and requires a new validated publication head; and
- review must use Git evidence and must not depend on pasted Codex output.

Do not require validation results to self-reference the commit SHA that contains
them. The commit already cryptographically binds its message to its exact tree.
The publication commit may reference its implementation parent SHA.

### 2. Required receipt trailers

The review-publication commit message must include, at minimum:

```text
Task-ID: MIP_LEAN_REPOSITORY_DELIVERY_STANDARD_001
Implementation-SHA: <correction-implementation-sha>
Receipt-Scope: exact-commit-tree
Validation-Gate: tier_1_docs_only
Validation-Result: passed
JSON-Parse: passed
Markdown-Consistency: passed
Changed-Paths: passed
Git-Diff-Check: passed
Focused-Tests: 1 passed
Full-Suite: not_required
Worktree-State: clean_except_allowed_local_only
Evidence-Source: codex_local_plus_github_remote
Capability-Authority: unchanged
```

Use accurate values. If any required check fails or cannot run, publish
`blocked`; do not create a passing receipt.

### 3. Current correction publication

Implement the rule change in one correction implementation commit. Then prepare
the three stable execution files for `ready_for_review`, run the final Tier 1
publication checks on the exact tree to be committed, and create one
review-publication commit containing the receipt trailers above.

The publication state must record:

- one real correction implementation SHA;
- `status: ready_for_review`;
- `task_execution_authorized: true`;
- `correction_execution_authorized: false`;
- empty blockers;
- merge and PR creation false;
- reviewed head and approval commit null; and
- unchanged capability and sibling authority.

## Validation gate

Run:

- JSON parsing for `EXECUTION_STATE.json`;
- Markdown/current-state consistency;
- exact correction-delta changed-path verification against the five
  correction-owned paths;
- complete task-diff verification against the seven original task-owned paths;
- `git diff --check`;
- `pytest -q tests/governance/test_repo_native_execution_handoff.py`;
- inspection of the final publication commit trailers; and
- proof that local and remote feature-branch heads equal the published receipt
  commit.

Docker, Ruff, mypy, and the full suite are `not_required` for this Tier 1
correction unless an unexpected executable dependency or repository-authored
gate is discovered. In that case, publish accurate `blocked` state rather than
widening scope.

## Authority and stop conditions

Correction execution is authorized. Merge, PR creation, sibling adoption, and
capability authority remain false. Do not force-push, merge, rebase, squash,
delete branches, modify siblings, or create additional process artifacts.

Push the exact receipt head and stop at `ready_for_review`.
