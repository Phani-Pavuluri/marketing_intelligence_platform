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
- **Incomplete branch-state implementation head:** `3c34b29564292e4d2728d3a69e950774e3e2a748`
- **Risk tier:** Tier 1 — documentation/governance plus focused governance test
- **Capability authorizations changed:** `false`

## Review decision

Commit `3c34b29564292e4d2728d3a69e950774e3e2a748` implements the branch-aware
guidance; the completed frozen tree is ready for exact-head review only.

Codex stopped after the substantive commit and did not:

- replace the three stable execution files with one current completion state;
- record the implementation SHA in execution state;
- run and publish the complete Tier 1 gate on the frozen final tree;
- create a durable exact-tree validation receipt; or
- publish `ready_for_review` or accurate `blocked` state.

The focused governance test also must assert the full branch-resolution contract rather than only selected phrases.

## Primary mergeable outcome

Complete the invocation-only prompt standard with deterministic resumed-feature-branch state resolution and Git-durable fail-closed reporting.

## Required correction

Continue on the existing feature branch. Do not create a replacement task or branch.

1. Preserve the exact minimal execution/correction invocation:
   `Synchronize from Git and execute the active task.`
2. Preserve branch-state implementation commit `3c34b29564292e4d2728d3a69e950774e3e2a748` unless a test-strengthening commit requires a new implementation head.
3. Strengthen `tests/governance/test_repo_native_execution_handoff.py` to assert that canonical guidance:
   - synchronizes and reads `main` before resolving resumed branch state;
   - obtains task ID, authorization head, and exact feature branch from Git-authored `main` state;
   - verifies repository identity, task ID, branch name, and authorization ancestry;
   - keeps `main` authoritative for authorization provenance;
   - makes the verified feature branch authoritative for current lifecycle state;
   - does not stop merely because `main` has an older lifecycle snapshot;
   - fails closed on identity, ancestry, ambiguity, or task/state/report mismatches;
   - requires Git-durable `blocked` evidence when a safe authorized branch write exists;
   - rejects terminal/chat output as completion evidence; and
   - preserves separate MMM and GeoX authority.
4. Replace `ACTIVE_TASK.md`, `EXECUTION_STATE.json`, and `LATEST_COMPLETION_REPORT.md` with one current `ready_for_review` or accurate `blocked` narrative.
5. Freeze the exact final tree and run the complete Tier 1 gate:
   - JSON parsing;
   - task/state/report consistency;
   - authorization and correction-boundary checks;
   - complete task diff limited to the six owned paths;
   - substantive implementation limited to `AGENTS.md`, `TASK_EXECUTION_STANDARD.md`, and the focused governance test;
   - publication limited to the three stable execution files;
   - exact minimal invocation preserved;
   - `git diff --check`;
   - `pytest -q tests/governance/test_repo_native_execution_handoff.py` with exact count;
   - durable receipt inspection; and
   - local/remote publication-head equality after push.
6. Create the durable exact-tree receipt commit, push the exact branch head, and stop without PR or merge.

Docker, Ruff, mypy, and the full suite remain `not_required` unless another repository-authored gate makes them applicable.

## Owned paths

1. `AGENTS.md`
2. `docs/execution/TASK_EXECUTION_STANDARD.md`
3. `tests/governance/test_repo_native_execution_handoff.py`
4. `docs/execution/ACTIVE_TASK.md`
5. `docs/execution/EXECUTION_STATE.json`
6. `docs/execution/LATEST_COMPLETION_REPORT.md`

Do not modify program or coordination files, roadmaps, contracts, adapters, fixtures, product/runtime/analytical code, MMM, or GeoX.

## Unresolved execution-blocking design questions

`none`

## Authority and stop conditions

Task and correction execution remain authorized on the existing feature branch. Merge and PR creation remain unauthorized. No product, analytical, data, persistence, recommendation, production, MMM, GeoX, or capability authority changes.
