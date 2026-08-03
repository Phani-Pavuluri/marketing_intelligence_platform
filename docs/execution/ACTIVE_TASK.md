# Active Task

**Status:** merged
**Owner:** MIP program governance
**Last updated:** 2026-08-03
**Last verified:** 2026-08-03

## Identity

- **Task ID:** `MIP_LEAN_REPOSITORY_DELIVERY_STANDARD_001`
- **Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
- **Feature branch:** `docs/mip-lean-repository-delivery-standard-001`
- **Rejected review head:** `9f829c3e12ca79698c6cabda1e8089e9d4567fa1`
- **Correction implementation commit:** `ee0905feb962150f850c33f5e20aa6fde03c8caf`
- **Risk tier:** Tier 1 — documentation and governance guidance only
- **Capability authorizations changed:** `false`

## Closure

The user explicitly approved exact reviewed head
`dd870de03d9a214f427f12e680b1f1f8ab4ad20b` in ChatGPT. It was fast-forwarded
to `main` and pushed without a pull request or merge commit.

The resulting main lineage before this closure commit is
`106f428de44e0e37405355f73e90ba6cbacd82a0 →
dd870de03d9a214f427f12e680b1f1f8ab4ad20b`. The sole correction implementation
commit is `ee0905feb962150f850c33f5e20aa6fde03c8caf`.

The local and remote feature branches were deleted after main synchronization.
Approval provenance is the user's explicit ChatGPT approval; no separate
approval-metadata commit exists. This task is closed. No capability authority
changed.

## Completed correction outcome

Final validation evidence is repository-durable: the review-publication commit
itself carries the exact-tree validation receipt. The lean workflow remains
unchanged; no resolver, automation framework, task schema, status file, or
checkpoint system was introduced.

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

## Correction record

### Durable publication rule

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

### Required receipt trailers

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

### Current correction publication

The rule change was implemented in
`ee0905feb962150f850c33f5e20aa6fde03c8caf`. The review-publication commit
`dd870de03d9a214f427f12e680b1f1f8ab4ad20b` carried the durable receipt and was
fast-forwarded exactly to main.

The closed state records:

- one real correction implementation SHA;
- `status: merged`;
- `task_execution_authorized: false`;
- `correction_execution_authorized: false`;
- empty blockers;
- merge and PR creation false;
- reviewed head `dd870de03d9a214f427f12e680b1f1f8ab4ad20b` and approval commit
  null; and
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

Correction execution is closed. Merge, PR creation, sibling adoption, and
capability authority remain false. The task must not be re-executed; a later
task requires separate authorization.

The receipt head is on main; stop at `merged`.
