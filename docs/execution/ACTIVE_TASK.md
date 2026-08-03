# Active Task

**Status:** authorized
**Owner:** MIP program governance
**Last updated:** 2026-08-03
**Last verified:** 2026-08-03

## Identity

- **Task ID:** `MIP_EXECUTION_TERMINAL_OUTCOME_ENFORCEMENT_001`
- **Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
- **Pre-authoring base:** `main` / `6419600e09f5ad24248266d87e808b5405cce54b`
- **Feature branch:** `docs/mip-execution-terminal-outcome-enforcement-001`
- **Execution mode:** `branch_and_fast_forward`
- **Risk tier:** Tier 1 — documentation/governance rule plus focused governance test
- **Prior task:** `MIP_INVOCATION_ONLY_CODEX_PROMPT_STANDARD_001`
- **Prior closure:** `6419600e09f5ad24248266d87e808b5405cce54b`
- **Capability authorizations changed:** `false`

## Primary mergeable outcome

Make successful orientation a prerequisite rather than a terminal task outcome. Once Codex verifies the repository, active task, authority, branch, and safe writable target, it must continue until it publishes either `ready_for_review` or Git-durable `blocked` evidence.

This is one independently reviewable governance outcome: the execution standard and its focused assertion must agree on the only valid terminal outcomes after successful orientation.

## Exact observable behavior

After this task merges:

1. Orientation, synchronization, branch verification, and task summarization are non-terminal steps when an executable task and safe authorized write target have been established.
2. Codex must continue from successful orientation into implementation, validation, publication, and push without requiring a second user prompt.
3. A run may stop after successful orientation only after publishing one of:
   - `ready_for_review` with a durable exact-tree receipt; or
   - Git-durable `blocked` state with the exact blocker, evidence attempted, validation completed or not completed, and a live resolution condition.
4. A terminal or chat-only orientation summary such as “the task was verified; no changes were made” is not a valid task outcome.
5. When no safe authorized Git write target can be established, an external stop report remains allowed, but it must say why no durable write was safe; the controller must durably reconcile the finding before another execution attempt.
6. The canonical execution/correction prompt remains exactly `Synchronize from Git and execute the active task.` No additional prompt wording is required for normal future runs.
7. Exact-head review, merge, closure, sibling ownership, and capability-authority rules remain unchanged.

## Resolved design decisions

- The rule applies to future MIP execution and correction sessions after successful orientation.
- Orientation-only output is progress reporting, not completion evidence.
- `ready_for_review` and Git-durable `blocked` are the only valid terminal feature-branch lifecycle outcomes once a safe authorized branch is established.
- No runtime service, bot, wrapper, schema, status, or automation system is introduced.
- This task updates MIP only. MMM and GeoX adoption requires separate owner-repository authorization.
- The prior task's PR merge-method exception remains historical evidence and is not modified or normalized by this task.

## Inputs and outputs

- **Input:** an executable Git-authored MIP task whose repository identity, authority, branch, ancestry, and writable target have been verified.
- **Output:** permanent MIP execution guidance and focused governance coverage prohibiting orientation-only termination.
- **Public API/schema/migration compatibility:** `not_applicable`; this task changes documentation and governance tests only.

## Failure semantics

- If orientation cannot establish a safe authorized write target, stop externally and state the exact missing authority or identity evidence.
- If orientation succeeds but implementation or validation cannot continue, publish accurate Git-durable `blocked` state before stopping.
- Do not treat task discovery, task summarization, branch checkout, or “no changes made” as completion.
- Do not broaden scope, weaken validation, invent authority, or rely on chat to repair missing Git instructions.

## Owned paths

Execution may modify only:

1. `AGENTS.md`
2. `docs/execution/TASK_EXECUTION_STANDARD.md`
3. `tests/governance/test_repo_native_execution_handoff.py`
4. `docs/execution/ACTIVE_TASK.md`
5. `docs/execution/EXECUTION_STATE.json`
6. `docs/execution/LATEST_COMPLETION_REPORT.md`

Do not modify program or coordination files, roadmaps, contracts, adapters, fixtures, product/runtime/analytical code, MMM, or GeoX.

## Required implementation

1. Add a concise rule to `AGENTS.md` that successful orientation cannot terminate an executable task.
2. Add an operative terminal-outcome contract to `TASK_EXECUTION_STANDARD.md` covering successful orientation, required continuation, valid durable terminal states, and the no-safe-write exception.
3. Strengthen the focused governance test to assert:
   - orientation is non-terminal after authority and a writable branch are verified;
   - execution continues without another user prompt;
   - terminal outcomes are `ready_for_review` or Git-durable `blocked`;
   - orientation-only summaries and “no changes made” are invalid completion evidence;
   - no-safe-write stopping remains narrowly allowed and explicitly explained; and
   - the exact minimal invocation remains unchanged.
4. Publish one current completion report and durable exact-tree validation receipt.

## Named acceptance tests

The focused governance test must prove that canonical MIP guidance:

- names successful orientation as non-terminal;
- requires continuation without a second user prompt;
- requires `ready_for_review` or Git-durable `blocked` before stopping when a safe branch exists;
- rejects terminal/chat-only task summaries and “no changes made” as completion;
- permits an external stop only when no safe authorized Git write target exists;
- preserves the exact minimal execution prompt;
- preserves exact-head review, branch authority, and fail-closed behavior; and
- preserves separate MMM and GeoX owner-repository adoption.

## Validation gate

Run the Tier 1 gate on the frozen publication tree:

- JSON parsing for `docs/execution/EXECUTION_STATE.json`;
- Markdown/current-state consistency;
- exact task-authoring boundary verification;
- exact changed-path verification against the six owned paths;
- implementation-path verification against the three substantive paths;
- publication-path verification against the three stable execution files;
- exact minimal invocation verification;
- `git diff --check`;
- `pytest -q tests/governance/test_repo_native_execution_handoff.py` with exact count;
- durable receipt-trailer inspection; and
- local/remote publication-head equality after push.

Docker, Ruff, mypy, and the full suite are `not_required` unless an unexpected executable dependency or another repository-authored gate makes them applicable. If a required check cannot run or fails, publish accurate Git-durable `blocked` state.

## Deferred successors

- `MMM_EXECUTION_TERMINAL_OUTCOME_ENFORCEMENT_ADOPTION_001` — proposed owner-repository adoption only.
- `GEOX_EXECUTION_TERMINAL_OUTCOME_ENFORCEMENT_ADOPTION_001` — proposed owner-repository adoption only; must not alter the active GeoX builder task.

## Unresolved execution-blocking design questions

`none`

## Authority and stop conditions

Task execution is authorized only for this MIP Tier 1 outcome. Merge and PR creation are unauthorized. No product, analytical, live-integration, data, persistence, recommendation, pilot, production, MMM, GeoX, or capability authority changes.

Create the exact feature branch from synchronized post-authoring `main`, execute the task, publish a durable `ready_for_review` receipt or accurate `blocked` state, push the exact branch head, and stop without PR or merge.
