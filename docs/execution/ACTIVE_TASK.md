# Active Task

**Status:** changes_requested
**Owner:** MIP program governance
**Last updated:** 2026-08-03
**Last verified:** 2026-08-03

## Identity

- **Task ID:** `MIP_INVOCATION_ONLY_CODEX_PROMPT_STANDARD_001`
- **Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
- **Feature branch:** `docs/mip-invocation-only-codex-prompt-standard-001`
- **Authorization head:** `39abc3d66a80054b2b293a73f2dbeb690eb2304b`
- **Accepted implementation head:** `312d6461fceaba882729e47c60b17f88b4f565f3`
- **Rejected publication head:** `a50a8dd05b2bc856cf67cad2286d3df904ae7710`
- **Risk tier:** Tier 1 documentation/governance plus focused test
- **Capability authorizations changed:** `false`

## Review decision

The invocation-only prompt rule, resumed-feature-branch resolution, durable
blocked reporting, and stale-review-narrative guard are accepted through exact
implementation head `312d6461fceaba882729e47c60b17f88b4f565f3`.

Exact publication head `a50a8dd05b2bc856cf67cad2286d3df904ae7710` is
rejected because its receipt and stable files identify only
`9376284a35f6dda7d1b9a535e5cf23c565f759ad` as the implementation even though
the accepted stale-state governance guard was added later at `312d6461...`.
`EXECUTION_STATE.json` also retains a stale note claiming one final correction
is authorized while the state says `ready_for_review` and correction authority
is false. The completion report ambiguously says MMM and GeoX adoption remains
separately authorized even though both adoption flags are false, and it omits
explicit consumer verification and newly eligible work.

## Primary mergeable outcome

Publish one coherent exact-tree `ready_for_review` state that accurately records
`312d6461fceaba882729e47c60b17f88b4f565f3` as the final implementation head and
contains complete, non-contradictory authority and completion evidence.

## Correction-owned paths

1. `docs/execution/ACTIVE_TASK.md`
2. `docs/execution/EXECUTION_STATE.json`
3. `docs/execution/LATEST_COMPLETION_REPORT.md`

Do not modify any other path. Preserve `AGENTS.md`,
`docs/execution/TASK_EXECUTION_STANDARD.md`, the focused governance test,
program and coordination files, product/runtime/analytical code, MMM, and GeoX.

## Required correction

1. Replace this file completely at publication time with a current
   `ready_for_review` narrative containing final implementation head
   `312d6461fceaba882729e47c60b17f88b4f565f3`.
2. Publish consistent `EXECUTION_STATE.json` with:
   - `status: ready_for_review`;
   - `implementation_commit_sha: 312d6461fceaba882729e47c60b17f88b4f565f3`;
   - correction execution false;
   - merge and PR creation false;
   - blockers empty;
   - reviewed head and approval commit null;
   - a current task-authoring note with no claim that further correction remains authorized; and
   - sibling adoption and capability authority unchanged.
3. Replace `LATEST_COMPLETION_REPORT.md` completely. It must include:
   - exact implementation SHA and feature branch;
   - completed deliverables;
   - exact validation results and test count;
   - GitHub-observed versus locally reported evidence;
   - blockers, limitations, and validation debt;
   - sibling impact;
   - consumer verification status;
   - newly eligible work;
   - authority impact; and
   - exact review readiness.
4. State unambiguously that MMM and GeoX invocation-only adoption remain
   unauthorized. The existing GeoX builder remains separately owner-authorized
   and unchanged.
5. Freeze the corrected tree, run the complete Tier 1 gate, create one exact-tree
   validation-receipt commit, push the exact remote branch head, and stop without
   PR or merge.

## Validation gate

Run on the frozen final publication tree:

- JSON parsing;
- task/state/report current-state consistency;
- authorization and correction-boundary checks;
- complete task diff limited to the original six owned paths;
- this correction delta limited to the three stable execution files;
- final implementation head recorded exactly as
  `312d6461fceaba882729e47c60b17f88b4f565f3` in task, state, report, and receipt;
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

Task and this publication correction are authorized on the existing feature
branch. Merge and PR creation remain unauthorized. MMM and GeoX invocation-only
adoption remain unauthorized. The active GeoX builder and all product,
analytical, recommendation, production, and capability authority remain
unchanged.
