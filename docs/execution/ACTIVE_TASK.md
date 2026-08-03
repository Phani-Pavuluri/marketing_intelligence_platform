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
- **Accepted substantive implementation:** `9376284a35f6dda7d1b9a535e5cf23c565f759ad`
- **Rejected publication head:** `0bb05e3a9d5024c9107b131a00d547f5587c3f86`
- **Risk tier:** Tier 1 — governance test plus stable execution publication
- **Capability authorizations changed:** `false`

## Review decision

The invocation-only and resumed-feature-branch behavior is accepted. No changes
are authorized to `AGENTS.md` or `docs/execution/TASK_EXECUTION_STANDARD.md`.

Exact head `0bb05e3a9d5024c9107b131a00d547f5587c3f86` is rejected because it marks the
task `ready_for_review` while retaining a current `Required correction` section,
claims correction execution remains authorized, and preserves a completion
report that describes the prior publication defect as though it were still
current.

The repeated failure mode is incremental status editing without replacing stale
current-state prose. This correction must make that contradiction impossible to
publish as passing evidence.

## Primary mergeable outcome

Publish one coherent exact-tree `ready_for_review` state for accepted
implementation `9376284a35f6dda7d1b9a535e5cf23c565f759ad`, enforced by a focused
governance assertion that rejects stale correction prose in review-ready state.

## Correction-owned paths

1. `tests/governance/test_repo_native_execution_handoff.py`
2. `docs/execution/ACTIVE_TASK.md`
3. `docs/execution/EXECUTION_STATE.json`
4. `docs/execution/LATEST_COMPLETION_REPORT.md`

Do not modify any other path. In particular, preserve `AGENTS.md`,
`docs/execution/TASK_EXECUTION_STANDARD.md`, program and coordination files,
product/runtime/analytical code, MMM, and GeoX unchanged.

## Required implementation

1. Strengthen the focused governance test so that when execution state is
   `ready_for_review` it requires:
   - the active task and completion report to declare the same current status;
   - the recorded implementation SHA to appear in both files;
   - no `Required correction` or `Required final correction` heading;
   - no claim that correction execution remains authorized or unfinished;
   - no claim that a current completion report, validation evidence, or receipt
     is missing; and
   - no stale `changes_requested` current-decision marker.
2. Replace this file completely at publication time. The final active task must
   contain only current review-ready identity, accepted outcome, validation,
   limitations, and authority. It must not retain this correction section.
3. Replace `LATEST_COMPLETION_REPORT.md` completely. The final report must contain
   the completed outcome, exact implementation SHA, exact validation results,
   GitHub-observed versus locally reported evidence, limitations, validation
   debt, sibling impact, consumer verification, authority impact, and exact
   review readiness. Prior rejected heads may appear only in a clearly historical
   review-history section.
4. Publish consistent `EXECUTION_STATE.json` with:
   - `status: ready_for_review`;
   - the final implementation SHA for this correction;
   - `correction_execution_authorized: false`;
   - merge and PR creation false;
   - blockers empty;
   - reviewed head and approval commit null; and
   - sibling and capability authority unchanged.
5. Freeze the final tree, run the complete Tier 1 gate, create one exact-tree
   validation-receipt commit, push the exact remote branch head, and stop without
   PR or merge.

## Validation gate

Run on the frozen final publication tree:

- JSON parsing;
- task/state/report current-state consistency, including the new stale-prose
  rejection assertions;
- authorization and correction-boundary checks;
- complete task diff limited to the original six owned paths;
- this final correction delta limited to the four correction-owned paths;
- accepted substantive implementation remains exactly
  `9376284a35f6dda7d1b9a535e5cf23c565f759ad`;
- exact minimal invocation remains unchanged;
- `git diff --check`;
- `pytest -q tests/governance/test_repo_native_execution_handoff.py` with exact
  count;
- durable receipt inspection; and
- local/remote publication-head equality after push.

Docker, Ruff, mypy, and the full suite remain `not_required` unless another
repository-authored gate makes them applicable. A required failure must be
published as accurate Git-durable `blocked` state.

## Unresolved execution-blocking design questions

`none`

## Authority and stop conditions

Task and this final correction are authorized on the existing feature branch.
Merge and PR creation remain unauthorized. MMM and GeoX adoption remain
separately unauthorized. The active GeoX builder and all product, analytical,
recommendation, production, and capability authority remain unchanged.
