# Active Task

**Status:** changes_requested
**Owner:** MIP program governance
**Last updated:** 2026-08-03
**Last verified:** 2026-08-03

## Identity

- **Task ID:** `MIP_EXECUTION_TERMINAL_OUTCOME_ENFORCEMENT_001`
- **Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
- **Feature branch:** `docs/mip-execution-terminal-outcome-enforcement-001`
- **Authorization head:** `7012add4baa284107a88f953e4d10d91c9e31b04`
- **Accepted implementation head:** `d8ba108faba403019845d7b72a71b791d7ab819f`
- **Rejected publication head:** `8dae4069c166aa638360e4295ae3d50a93843e13`
- **Risk tier:** Tier 1 documentation/governance plus focused test
- **Capability authorizations changed:** `false`

## Review decision

The substantive implementation is accepted. It makes successful orientation
non-terminal, requires continuation without a second prompt, permits only
`ready_for_review` or Git-durable `blocked` after a safe branch is established,
and preserves the exact minimal invocation.

Exact publication head `8dae4069c166aa638360e4295ae3d50a93843e13` is
not approvable because `LATEST_COMPLETION_REPORT.md` remains primarily an
authorization brief rather than a current completion report. It still instructs
Codex to publish `ready_for_review` or `blocked` after already claiming
`ready_for_review`, and it does not record complete current-task evidence for
GitHub-observed versus locally reported validation, limitations, validation
debt, consumer verification, newly eligible work, and exact review readiness.

## Primary mergeable outcome

Publish one coherent exact-tree `ready_for_review` state for accepted
implementation `d8ba108faba403019845d7b72a71b791d7ab819f`, with a complete
current completion report and no stale authorization or unfinished-work prose.

## Correction-owned paths

1. `docs/execution/ACTIVE_TASK.md`
2. `docs/execution/EXECUTION_STATE.json`
3. `docs/execution/LATEST_COMPLETION_REPORT.md`

Do not modify `AGENTS.md`, `docs/execution/TASK_EXECUTION_STANDARD.md`,
`tests/governance/test_repo_native_execution_handoff.py`, program or
coordination files, product/runtime/analytical code, MMM, or GeoX.

## Required correction

1. Replace this file completely at publication time with a concise current
   `ready_for_review` narrative naming implementation
   `d8ba108faba403019845d7b72a71b791d7ab819f`.
2. Publish consistent `EXECUTION_STATE.json` with:
   - `status: ready_for_review`;
   - `implementation_commit_sha: d8ba108faba403019845d7b72a71b791d7ab819f`;
   - correction execution false;
   - merge and PR creation false;
   - blockers empty;
   - reviewed head and approval commit null; and
   - sibling adoption and capability authority unchanged.
3. Replace `LATEST_COMPLETION_REPORT.md` completely. It must include:
   - exact implementation SHA and feature branch;
   - completed deliverables;
   - exact validation results and focused-test count;
   - GitHub-observed versus locally reported evidence;
   - blockers, limitations, and validation debt;
   - sibling impact;
   - consumer verification status;
   - newly eligible work;
   - authority impact; and
   - exact review readiness.
4. Remove authorization-era or unfinished-work instructions, including any
   current instruction to publish `ready_for_review` or `blocked` after the
   report already declares `ready_for_review`.
5. Freeze the corrected tree, run the complete Tier 1 gate, create one exact-tree
   validation-receipt commit, push the exact remote branch head, verify remote
   equality, and stop without PR or merge.

## Validation gate

Run on the frozen final publication tree:

- JSON parsing;
- task/state/report current-state consistency;
- authorization and correction-boundary checks;
- complete task diff limited to the original six owned paths;
- this correction delta limited to the three stable execution files;
- implementation head recorded exactly as
  `d8ba108faba403019845d7b72a71b791d7ab819f` in task, state, report, and receipt;
- exact minimal invocation remains unchanged;
- `git diff --check`;
- `pytest -q tests/governance/test_repo_native_execution_handoff.py` with exact count;
- durable receipt inspection; and
- local/remote publication-head equality after push.

Docker, Ruff, mypy, and the full suite remain `not_required` unless another
repository-authored gate makes them applicable. A required failure must be
published as accurate Git-durable `blocked` state.

## Unresolved execution-blocking design questions

`none`

## Authority and stop conditions

This bounded publication correction is authorized on the existing feature
branch. Merge and PR creation remain unauthorized. MMM and GeoX adoption remain
unauthorized. Product, analytical, recommendation, production, and capability
authority remain unchanged.
