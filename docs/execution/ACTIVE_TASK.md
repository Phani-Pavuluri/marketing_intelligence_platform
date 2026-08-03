# Active Task

**Status:** ready_for_review
**Owner:** MIP program governance
**Last updated:** 2026-08-03
**Last verified:** 2026-08-03

## Identity

- **Task ID:** `MIP_INVOCATION_ONLY_CODEX_PROMPT_STANDARD_001`
- **Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
- **Feature branch:** `docs/mip-invocation-only-codex-prompt-standard-001`
- **Authorization head:** `39abc3d66a80054b2b293a73f2dbeb690eb2304b`
- **Accepted minimal-prompt implementation:** `9bb63c02e476a8a13855192b9df77d4238a3673b`
- **Accepted branch-aware implementation and test head:** `9376284a35f6dda7d1b9a535e5cf23c565f759ad`
- **Rejected publication head:** `cdaa1c9c69fee7445b9c5a04b3d5996dbd5a4a91`
- **Risk tier:** Tier 1 — documentation/governance plus focused governance test
- **Capability authorizations changed:** `false`

## Review decision

The substantive implementation is accepted and this final publication is ready
for exact-head review. Canonical guidance now:

- preserves the exact invocation `Synchronize from Git and execute the active task.`;
- reads synchronized `main` for task identity, authorization provenance, and the declared feature branch;
- verifies repository identity, task ID, branch name, and authorization ancestry;
- uses the verified feature branch for current resumed lifecycle state;
- does not stop merely because `main` retains an older lifecycle snapshot; and
- requires Git-durable `blocked` evidence when a safe authorized branch write exists.

Implementation `9376284a35f6dda7d1b9a535e5cf23c565f759ad` also strengthens the focused governance test for identity, ancestry, mismatch, and durable blocked reporting.

The final stable task, state, and report now present one coherent review state.

## Primary mergeable outcome

Publish one coherent, exact-tree `ready_for_review` state for the accepted invocation-only and branch-aware execution standard.

## Correction-owned paths

1. `docs/execution/ACTIVE_TASK.md`
2. `docs/execution/EXECUTION_STATE.json`
3. `docs/execution/LATEST_COMPLETION_REPORT.md`

Do not modify program or coordination files, roadmaps, contracts, adapters, fixtures, product/runtime/analytical code, MMM, GeoX, `AGENTS.md`, `TASK_EXECUTION_STANDARD.md`, or the focused governance test unless validation fails and the task is accurately published as `blocked`.

## Required correction

1. Replace this file with one current `ready_for_review` narrative that records accepted implementation `9376284a35f6dda7d1b9a535e5cf23c565f759ad` and no longer describes execution work as missing.
2. Publish consistent execution state with:
   - `status: ready_for_review`;
   - `implementation_commit_sha: 9376284a35f6dda7d1b9a535e5cf23c565f759ad`;
   - task execution true;
   - correction execution false;
   - merge and PR creation false;
   - blockers empty;
   - reviewed head and approval commit null; and
   - sibling and capability authority unchanged.
3. Replace the completion report with one current report containing:
   - exact implementation SHA and branch;
   - complete deliverables;
   - GitHub-observed versus locally observed evidence;
   - exact Tier 1 validation results and test count;
   - limitations and validation debt;
   - sibling impact and consumer verification;
   - authority impact; and
   - exact review readiness.
4. Freeze the corrected tree, run the complete Tier 1 gate, create a new durable exact-tree receipt commit, push the exact remote branch head, and stop without PR or merge.

## Validation gate

Run on the frozen final publication tree:

- JSON parsing;
- task/state/report current-state consistency;
- authorization and correction-boundary checks;
- complete task diff limited to the six original owned paths;
- final correction delta limited to the three stable execution files;
- accepted substantive implementation remains exactly `9376284a35f6dda7d1b9a535e5cf23c565f759ad`;
- exact minimal invocation remains unchanged;
- `git diff --check`;
- `pytest -q tests/governance/test_repo_native_execution_handoff.py` with exact count;
- durable receipt inspection; and
- local/remote publication-head equality after push.

Docker, Ruff, mypy, and the full suite remain `not_required` unless another repository-authored gate makes them applicable. A required failure must be published as accurate Git-durable `blocked` state.

## Unresolved execution-blocking design questions

`none`

## Authority and stop conditions

Task and final publication correction execution are authorized on the existing feature branch. Merge and PR creation remain unauthorized. No product, analytical, data, persistence, recommendation, production, MMM, GeoX, or capability authority changes.
