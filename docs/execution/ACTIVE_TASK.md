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
- **Current review-decision head before this correction:** `18743001a1a462e8e237c9adc34af601c353a83c`
- **Accepted minimal-prompt implementation:** `9bb63c02e476a8a13855192b9df77d4238a3673b`
- **Risk tier:** Tier 1 — documentation/governance plus focused governance test
- **Capability authorizations changed:** `false`

## Review decision

The minimal invocation text is accepted, but the repository-native execution
protocol is incomplete.

A real invocation of:

`Synchronize from Git and execute the active task.`

synchronized `main`, found `main` still at the original `authorized` state, then
observed that the remote feature branch had advanced to branch-only review and
correction state. Codex stopped rather than deciding whether `main` or the
feature branch controlled the resumed lifecycle.

That stop was reasonable under the existing rules, but its result remained only
in terminal/chat output. No Git-durable blocked report or completion evidence
was published. The invocation-only contract is therefore not safe yet.

## Primary mergeable outcome

Make the minimal invocation operational by defining deterministic, branch-aware
active-state resolution and durable fail-closed reporting for resumed tasks.

This is not a separate product outcome. It is required for the already accepted
invocation-only prompt contract to function without chat-provided branch or
status instructions.

## Exact observable behavior

After correction:

1. Codex synchronizes `main` first and reads the task ID, authorization boundary,
   and exact feature-branch name from `main`.
2. When that feature branch exists remotely and descends from the authorization
   head, Codex fetches it before deciding the executable lifecycle state.
3. For a resumed task, `main` remains authoritative for the original
   authorization boundary, while the verified remote feature branch is
   authoritative for the latest task status, correction decision, completion
   report, implementation SHA, blockers, and publication state.
4. Codex executes the latest verified branch state when task IDs, branch identity,
   ancestry, and authority agree. It must not stop merely because `main` retains
   the original `authorized` snapshot.
5. Codex fails closed on a missing branch required by the task, wrong ancestry,
   task-ID mismatch, branch-name mismatch, inconsistent branch task/state/report,
   duplicate candidate branches, moved authorization boundary, or unauthorized
   scope.
6. When the active branch and write authority can be safely established, any
   fail-closed execution result must be written to that branch as accurate
   `blocked` Git evidence before stopping. Terminal or chat output is not the
   completion report.
7. Only when no authorized Git write target can be established may Codex stop
   without a Git write; that limitation and the exact unverifiable condition must
   be reported externally.
8. The canonical invocation remains exactly:
   `Synchronize from Git and execute the active task.`
9. The merge invocation still adds only the externally approved exact remote
   head SHA.

## Resolved design decisions

- No prompt-level branch name, expected SHA, publication instruction, or stop
  instruction is added.
- Branch resolution belongs in `AGENTS.md` and
  `docs/execution/TASK_EXECUTION_STANDARD.md`.
- `main` owns authorization provenance; the verified feature branch owns the
  latest in-task lifecycle state after branch creation.
- A remote branch does not become authoritative merely by existing; task ID,
  declared branch name, authorization ancestry, and repository identity must
  all agree.
- Durable blocked reporting is required whenever an authorized branch write is
  safe.
- No resolver service, registry, new status schema, bot, wrapper, CLI, or
  automation system is introduced.
- MMM and GeoX adoption remains separately owner-authorized.

## Inputs and outputs

- **Input:** synchronized `main`, its declared feature branch and authorization
  boundary, and the corresponding remote feature-branch state.
- **Output:** deterministic selection of the current executable task state or a
  Git-durable blocked result.
- **Public API/schema/migration compatibility:** `not_applicable`.

## Correction-owned paths

1. `AGENTS.md`
2. `docs/execution/TASK_EXECUTION_STANDARD.md`
3. `tests/governance/test_repo_native_execution_handoff.py`
4. `docs/execution/ACTIVE_TASK.md`
5. `docs/execution/EXECUTION_STATE.json`
6. `docs/execution/LATEST_COMPLETION_REPORT.md`

Do not modify the lean standard, context index, coordination files, roadmaps,
contracts, adapters, fixtures, product/runtime/analytical code, MMM, or GeoX.

## Required correction

1. Add branch-aware resumed-task resolution to `AGENTS.md`.
2. Add the operative precedence and verification rules to
   `TASK_EXECUTION_STANDARD.md`.
3. Require Git-durable `blocked` publication when the active branch and write
   authority are safely established.
4. Preserve the exact minimal execution/correction and merge invocations.
5. Strengthen the focused governance test for main/branch precedence, ancestry
   and identity checks, no false stop on stale main lifecycle state, and durable
   blocked reporting.
6. Replace the stable task/state/report with one current publication narrative.
7. Freeze the corrected tree, run the Tier 1 gate, publish a durable exact-tree
   receipt, push the exact remote branch head, and stop at `ready_for_review` or
   accurate `blocked`.

## Named acceptance tests

The focused governance test must prove that canonical guidance:

- retains `Synchronize from Git and execute the active task.` exactly;
- synchronizes and reads `main` before branch resolution;
- obtains the exact feature branch and authorization head from Git-authored main
  state rather than prompt text;
- requires feature-branch identity, task-ID, ancestry, and repository agreement;
- makes verified branch lifecycle state authoritative for resumed execution;
- preserves main as authorization-boundary authority;
- does not treat stale main lifecycle state as a reason to stop when the verified
  active branch has newer state;
- fails closed on mismatches or inconsistent branch evidence;
- requires a Git-durable `blocked` result when a safe authorized branch write is
  possible;
- never treats terminal/chat output as the completion report; and
- preserves separate MMM and GeoX adoption authority.

## Validation gate

Run on the frozen publication tree:

- JSON parsing;
- task/state/report current-state consistency;
- authorization and correction-boundary checks;
- complete task diff limited to the six owned paths;
- substantive correction limited to `AGENTS.md`,
  `TASK_EXECUTION_STANDARD.md`, and the focused governance test;
- publication limited to the three stable execution files;
- accepted minimal invocation remains unchanged;
- `git diff --check`;
- `pytest -q tests/governance/test_repo_native_execution_handoff.py`;
- durable receipt inspection; and
- local/remote publication-head equality after push.

Docker, Ruff, mypy, and the full suite are `not_required` for this Tier 1
correction unless another repository-authored gate makes them applicable.

## Unresolved execution-blocking design questions

`none`

## Authority and stop conditions

Task and correction execution are authorized on the existing feature branch.
Merge and PR creation are unauthorized. No product, analytical, data,
persistence, recommendation, production, MMM, GeoX, or capability authority
changes.
