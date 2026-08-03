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
- **Rejected first review head:** `fa8ff9612732f34a4d90275da017c7125ec9cea0`
- **Accepted behavioral correction implementation:** `9bb63c02e476a8a13855192b9df77d4238a3673b`
- **Rejected corrected publication head:** `c09ec85b43442f505e710625bad0e33f56b3d300`
- **Risk tier:** Tier 1 — documentation/governance plus focused governance test
- **Capability authorizations changed:** `false`

## Review decision

The invocation-only behavioral correction is accepted. Canonical execution and
correction invocation is exactly:

`Synchronize from Git and execute the active task.`

The merge invocation adds only the externally approved exact remote head SHA.
The substantive files and focused test correctly prohibit prompt-level
publication, push, validation, cleanup, workflow, and stop instructions.

The corrected publication head is rejected because the three stable execution
files do not represent one current state:

- `EXECUTION_STATE.json` says `ready_for_review` and correction authorization is
  false;
- `ACTIVE_TASK.md` still says one correction cycle is authorized and its final
  authority section says correction execution is true and unfinished; and
- `LATEST_COMPLETION_REPORT.md` remains the prior correction-authorization
  report rather than a current corrected completion report.

This is a final publication-state normalization correction, not a new behavioral
outcome or another substantive correction cycle.

## Primary mergeable outcome

Make MIP Codex prompts genuinely invocation-only while keeping one coherent,
Git-durable current task, state, and completion report.

## Exact observable behavior

1. Execution and correction invocation:
   `Synchronize from Git and execute the active task.`
2. Merge invocation:
   `Synchronize from Git and execute the active task's merge and closure workflow. Approved exact remote head: <SHA>.`
3. Invocation text carries no durable scope, paths, behavior, validation,
   publication, push, cleanup, workflow, authority, or stop conditions.
4. Missing or inconsistent Git instructions fail closed.
5. MMM and GeoX adoption remains separately owner-authorized.

## Correction-owned paths

This final normalization may modify only:

1. `docs/execution/ACTIVE_TASK.md`
2. `docs/execution/EXECUTION_STATE.json`
3. `docs/execution/LATEST_COMPLETION_REPORT.md`

Do not modify `AGENTS.md`, `TASK_EXECUTION_STANDARD.md`, the focused governance
test, any program or coordination file, product/runtime/analytical code, MMM, or
GeoX. Behavioral implementation `9bb63c02e476a8a13855192b9df77d4238a3673b`
must remain unchanged.

## Required correction

1. Replace this task with one current `ready_for_review` narrative that records
   the accepted behavioral implementation and no longer claims correction
   execution remains authorized or unfinished.
2. Replace the completion report with one current corrected completion report,
   including the accepted implementation SHA, exact validation counts, rejected
   heads, limitations, sibling impact, and authority impact.
3. Publish consistent `ready_for_review` state with correction authorization
   false, blockers empty, merge/PR false, and the final publication-normalization
   implementation SHA.
4. Freeze the exact tree, run the complete Tier 1 gate, create a new durable
   receipt commit, push the exact remote head, and stop.

## Validation gate

Run on the frozen final publication tree:

- JSON parsing;
- task/state/report current-state consistency;
- authorization and review-decision boundary checks;
- complete task diff limited to the six original owned paths;
- final normalization delta limited to the three stable execution files;
- behavioral implementation remains exactly `9bb63c02e476a8a13855192b9df77d4238a3673b`;
- `git diff --check`;
- `pytest -q tests/governance/test_repo_native_execution_handoff.py`;
- durable receipt inspection; and
- local/remote publication-head equality after push.

Docker, Ruff, mypy, and the full suite remain `not_required` for this Tier 1
correction unless another repository-authored gate makes them applicable.

## Unresolved execution-blocking design questions

`none`

## Authority and stop conditions

Task and final normalization execution are authorized on the existing branch.
Merge and PR creation are unauthorized. No product, analytical, data,
persistence, recommendation, production, MMM, GeoX, or capability authority
changes. Publish `ready_for_review` or accurate `blocked` and stop without merge.
