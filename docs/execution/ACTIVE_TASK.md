# Active Task

**Status:** ready_for_review
**Owner:** MIP program governance
**Last updated:** 2026-08-03
**Last verified:** 2026-08-03

## Identity

- **Task ID:** `MIP_INVOCATION_ONLY_CODEX_PROMPT_STANDARD_001`
- **Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
- **Pre-authoring base:** `main` / `2904334247980e564409b7815c812572d80c8419`
- **Feature branch:** `docs/mip-invocation-only-codex-prompt-standard-001`
- **Execution mode:** `branch_and_fast_forward`
- **Risk tier:** Tier 1 — documentation/governance rule plus focused governance test
- **Prior task:** `MIP_DEFINITION_READY_TASK_AUTHORIZATION_STANDARD_001`
- **Prior closure:** `2904334247980e564409b7815c812572d80c8419`
- **Capability authorizations changed:** `false`
- **Implementation commit:** `2f1ec3efdd6f68d5c8097e534c869d982ab2d6ec`

## Published review state

The invocation-only prompt contract is implemented and validated on the frozen
review-publication tree. This task is ready for exact-head review only. Merge,
PR creation, sibling adoption, and capability authority remain false.

## Primary mergeable outcome

Make Codex prompts invocation-only so Git remains the sole durable source for task scope, behavior, validation, paths, workflow, and stop conditions.

This is one independently reviewable outcome: the canonical prompt contract and its focused governance assertion establish one execution handoff rule. It cannot be split further without leaving either unenforced guidance or a test with no canonical requirement.

## Exact observable behavior

After this task merges:

1. A normal execution prompt identifies only the repository operation: synchronize from Git, read `AGENTS.md` and the active task, execute it, publish `ready_for_review` or accurate `blocked`, push the exact branch head, and stop.
2. A correction prompt identifies only the correction operation: synchronize, read the active `changes_requested` task, execute the authorized correction, publish the new exact review head or accurate `blocked`, push, and stop.
3. A merge prompt identifies only the merge/closure operation plus the exact externally approved remote head SHA, because external approval is not written into the reviewed tree.
4. Prompts must not restate durable scope, owned paths, implementation behavior, validation commands, expected repository SHAs already recorded in Git, workflow steps, or stop conditions.
5. A prompt may carry only an external fact unavailable in the reviewed repository state, such as the exact user-approved SHA, or a narrowly necessary connector/runtime fact explicitly allowed by the active task.
6. Chat, pasted summaries, and prompt text cannot repair, expand, override, or reinterpret an incomplete active task. If Git lacks sufficient durable instructions, Codex stops fail-closed.

The resulting standard must make short prompts safe because all durable execution meaning is already present in Git.

## Resolved design decisions

- The rule applies to future MIP Codex execution, correction, and merge invocations.
- Durable instructions belong in `AGENTS.md`, `TASK_EXECUTION_STANDARD.md`, the stable active task, and relevant repository evidence.
- The exact externally approved review-head SHA remains in the merge invocation because adding it to the reviewed branch would invalidate exact-head approval.
- No new prompt file, prompt registry, schema, resolver, CLI wrapper, bot, automation service, status, or checkpoint system is introduced.
- This task updates MIP only. MMM and GeoX adoption requires separate owner-repository authorization.
- The current GeoX builder task is not modified, superseded, blocked, or reinterpreted.

## Inputs and outputs

- **Input:** an already-authorized or externally approved repository-native operation represented in committed Git state.
- **Output:** canonical MIP guidance and a focused governance assertion requiring invocation-only prompts.
- **Public API/schema/migration compatibility:** `not_applicable`; this task changes documentation and governance tests only.

## Failure semantics

- If the active task, execution state, approval evidence, branch, or Git-authored workflow is incomplete or inconsistent, stop rather than supplementing it from chat.
- Prompt text must not broaden owned scope, reduce validation, change authority, invent an approval, or override repository state.
- A merge must fail closed without the exact externally approved remote head SHA.
- A normal execution or correction invocation must fail closed when Git does not contain a complete definition-ready task.

## Owned paths

Execution may modify only:

1. `AGENTS.md`
2. `docs/execution/TASK_EXECUTION_STANDARD.md`
3. `tests/governance/test_repo_native_execution_handoff.py`
4. `docs/execution/ACTIVE_TASK.md`
5. `docs/execution/EXECUTION_STATE.json`
6. `docs/execution/LATEST_COMPLETION_REPORT.md`

Do not modify the lean standard, context index, coordination files, roadmaps, contracts, adapters, fixtures, application/runtime/analytical code, MMM, or GeoX.

## Required implementation

1. Add a concise invocation-only prompt rule to `AGENTS.md`.
2. Add an operative prompt contract to `TASK_EXECUTION_STANDARD.md` covering execution, correction, and merge invocations.
3. State that durable instructions must not be duplicated in prompts and that missing Git instructions are a blocker, not permission to repair from chat.
4. Preserve the exact approved SHA as the only normally required external merge fact.
5. Strengthen the existing focused governance test to assert the canonical rule and fail-closed behavior.
6. Publish one current completion narrative and a durable exact-tree validation receipt.

## Named acceptance tests

The focused governance test must prove that canonical MIP guidance:

- names Codex prompts as invocation-only;
- requires synchronization and reading `AGENTS.md` plus the active task;
- covers execution, correction, and merge operations;
- permits the exact externally approved SHA in a merge invocation;
- says scope, owned paths, behavior, validation, workflow, and stop conditions belong in Git;
- prohibits prompt text from repairing, expanding, overriding, or reinterpreting the active task;
- requires fail-closed stopping when Git lacks sufficient durable instructions;
- preserves exact-head approval and repository authority; and
- preserves separate owner-repository adoption for MMM and GeoX.

## Validation gate

Run the Tier 1 gate on the frozen publication tree:

- JSON parsing for `docs/execution/EXECUTION_STATE.json`;
- Markdown/current-state consistency;
- exact task-authoring boundary verification;
- exact changed-path verification against the six owned paths;
- implementation-path verification against the three substantive paths;
- publication-path verification against the three stable execution files;
- `git diff --check`;
- `pytest -q tests/governance/test_repo_native_execution_handoff.py`;
- receipt-trailer inspection; and
- local/remote publication-head equality after push.

Docker, Ruff, mypy, and the full suite are `not_required` unless an unexpected executable dependency or another repository-authored gate makes them applicable. If a required check cannot run or fails, publish accurate `blocked` state rather than widening scope or claiming completion.

## Deferred successors

- `MMM_INVOCATION_ONLY_CODEX_PROMPT_STANDARD_ADOPTION_001` — proposed owner-repository adoption only; not authorized here.
- `GEOX_INVOCATION_ONLY_CODEX_PROMPT_STANDARD_ADOPTION_001` — proposed owner-repository adoption only; must not alter the current GeoX builder task.
- MMM and GeoX adoption of the combined lean, definition-ready, risk-tier, durable-receipt, and invocation-only structure remains separately owner-authorized.

## Unresolved execution-blocking design questions

`none`

## Authority and stop conditions

The implementation is complete and ready for review only. No product,
analytical, live-integration, real-data, persistence, recommendation, pilot,
production, MMM, GeoX, or capability authority changed.

Create the exact feature branch from synchronized post-authoring `main`, execute the task, publish a durable `ready_for_review` receipt or accurate `blocked` state, push the exact branch head, and stop without PR or merge.
