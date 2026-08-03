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
- **Rejected review head:** `fa8ff9612732f34a4d90275da017c7125ec9cea0`
- **Rejected candidate implementation:** `2f1ec3efdd6f68d5c8097e534c869d982ab2d6ec`
- **Capability authorizations changed:** `false`

## Review decision

The bounded correction is complete. Execution and correction now use exactly
`Synchronize from Git and execute the active task.` The corrected tree is ready
for exact-head review only.

The candidate says prompts must not restate workflow steps or stop conditions,
while also prescribing execution and correction prompts that say to publish a
review state, push the exact branch head, and stop. That is internally
contradictory and does not achieve the requested minimal invocation.

One bounded correction cycle is authorized. Do not create a replacement task or
branch.

## Primary mergeable outcome

Make Codex prompts genuinely invocation-only so Git remains the sole durable
source for task scope, behavior, validation, paths, workflow, authority, and
stop conditions.

This remains one independently reviewable outcome: the canonical prompt contract
and its focused governance assertion establish one execution handoff rule.

## Corrected exact observable behavior

After this task merges:

1. The canonical normal execution invocation is:
   `Synchronize from Git and execute the active task.`
2. The same canonical invocation applies when the active task is
   `changes_requested`; the task status and Git-authored instructions determine
   that the authorized correction is executed.
3. The canonical merge invocation identifies only the merge operation and the
   external approval fact:
   `Synchronize from Git and execute the active task's merge and closure workflow. Approved exact remote head: <SHA>.`
4. Invocation text must not repeat publication states, push instructions,
   validation commands, paths, workflow steps, cleanup steps, stop conditions,
   expected repository SHAs already in Git, or implementation details.
5. A prompt may carry only an external fact unavailable in reviewed Git state,
   principally the exact externally approved remote head SHA for merge, or a
   narrowly necessary runtime/connector fact explicitly allowed by the active
   task.
6. Chat, pasted summaries, and prompt text cannot repair, expand, override, or
   reinterpret an incomplete active task. If Git lacks sufficient durable
   instructions, Codex stops fail-closed.

## Resolved design decisions

- Execution and correction use the same minimal invocation because Git state
  determines which authorized operation is active.
- Merge adds only the exact approved SHA because that approval cannot be written
  into the reviewed tree without changing it.
- Durable execution, publication, validation, push, cleanup, and stop behavior
  remain in `AGENTS.md`, `TASK_EXECUTION_STANDARD.md`, and the active task—not in
  the invocation.
- No new prompt file, registry, schema, resolver, wrapper, bot, service, status,
  or checkpoint system is introduced.
- This task updates MIP only. MMM and GeoX adoption requires separate
  owner-repository authorization.
- The current GeoX builder task remains unmodified and uninterpreted.

## Inputs and outputs

- **Input:** an authorized or externally approved repository-native operation
  represented in committed Git state.
- **Output:** canonical MIP guidance and a focused governance assertion requiring
  truly minimal invocation-only prompts.
- **Public API/schema/migration compatibility:** `not_applicable`.

## Failure semantics

- If the active task, execution state, approval evidence, branch, or Git-authored
  workflow is incomplete or inconsistent, stop rather than supplementing it
  from chat.
- Prompt text must not broaden scope, reduce validation, change authority,
  invent approval, or override repository state.
- A merge fails closed without the exact externally approved remote head SHA.
- Execution or correction fails closed when Git lacks a complete definition-ready
  active task.

## Owned paths

Correction execution may modify only:

1. `AGENTS.md`
2. `docs/execution/TASK_EXECUTION_STANDARD.md`
3. `tests/governance/test_repo_native_execution_handoff.py`
4. `docs/execution/ACTIVE_TASK.md`
5. `docs/execution/EXECUTION_STATE.json`
6. `docs/execution/LATEST_COMPLETION_REPORT.md`

Do not modify the lean standard, context index, coordination files, roadmaps,
contracts, adapters, fixtures, application/runtime/analytical code, MMM, or
GeoX.

## Required correction

1. Revise `AGENTS.md` so its invocation-only rule does not imply that prompt
   text carries workflow or stop instructions.
2. Revise the prompt contract in `TASK_EXECUTION_STANDARD.md` to use the exact
   minimal execution/correction and merge invocations above.
3. Remove prompt-level publication, push, cleanup, validation, and stop language;
   retain those obligations only in Git-authored workflow sections.
4. Strengthen the focused governance test to assert the exact minimal
   invocations and the prohibition on workflow/stop duplication.
5. Replace the current completion report with one current correction narrative.
6. Freeze the corrected tree, run the full Tier 1 gate, publish a new durable
   exact-tree receipt, push the exact branch head, and stop at
   `ready_for_review` or accurate `blocked`.

## Named acceptance tests

The focused governance test must prove that canonical MIP guidance:

- contains exactly the minimal execution/correction invocation
  `Synchronize from Git and execute the active task.`;
- contains a minimal merge invocation plus only the exact approved SHA external
  fact;
- uses active Git status to distinguish normal execution from correction;
- says durable scope, paths, behavior, validation, workflow, authority, cleanup,
  and stop conditions belong in Git;
- forbids invocation text from repeating publication, push, validation, cleanup,
  or stop instructions;
- prohibits prompt text from repairing, expanding, overriding, or
  reinterpreting the active task;
- requires fail-closed stopping when Git lacks sufficient durable instructions;
- preserves exact-head approval and repository authority; and
- preserves separate owner-repository adoption for MMM and GeoX.

## Validation gate

Run the Tier 1 gate on the frozen corrected publication tree:

- JSON parsing for `docs/execution/EXECUTION_STATE.json`;
- Markdown/current-state consistency;
- exact task-authoring and review-correction boundary verification;
- exact complete task diff against the six owned paths;
- exact correction delta against the six correction-owned paths;
- implementation-path verification against the three substantive paths;
- publication-path verification against the three stable execution files;
- `git diff --check`;
- `pytest -q tests/governance/test_repo_native_execution_handoff.py`;
- receipt-trailer inspection; and
- local/remote publication-head equality after push.

Docker, Ruff, mypy, and the full suite are `not_required` unless an unexpected
executable dependency or another repository-authored gate makes them applicable.
If a required check cannot run or fails, publish accurate `blocked` state rather
than widening scope or claiming completion.

## Deferred successors

- `MMM_INVOCATION_ONLY_CODEX_PROMPT_STANDARD_ADOPTION_001` — proposed
  owner-repository adoption only; not authorized here.
- `GEOX_INVOCATION_ONLY_CODEX_PROMPT_STANDARD_ADOPTION_001` — proposed
  owner-repository adoption only; must not alter the current GeoX builder task.
- MMM and GeoX adoption of the combined lean, definition-ready, risk-tier,
  durable-receipt, and invocation-only structure remains separately
  owner-authorized.

## Unresolved execution-blocking design questions

`none`

## Authority and stop conditions

Correction execution is authorized only for this bounded MIP Tier 1 correction.
Task execution remains true; correction execution is true. Merge and PR creation
remain unauthorized. No product, analytical, live-integration, real-data,
persistence, recommendation, pilot, production, MMM, GeoX, or capability
authority changes.

Execute the correction on the existing feature branch, publish a new durable
`ready_for_review` receipt or accurate `blocked` state, push the exact branch
head, and stop without PR or merge.
