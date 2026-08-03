# TASK_COMPLETION_REPORT_V2

## Identity

- **Task ID:** `MIP_INVOCATION_ONLY_CODEX_PROMPT_STANDARD_001`
- **Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
- **Feature branch:** `docs/mip-invocation-only-codex-prompt-standard-001`
- **Rejected review head:** `fa8ff9612732f34a4d90275da017c7125ec9cea0`
- **Rejected candidate implementation:** `2f1ec3efdd6f68d5c8097e534c869d982ab2d6ec`
- **Current decision:** `changes_requested`

## Review finding

The candidate is correctly scoped and its Tier 1 receipt is durable, but the
behavioral contract is internally inconsistent.

It says invocation text must not repeat workflow steps or stop conditions while
its prescribed execution and correction prompts still say to publish a review
state, push the exact branch head, and stop. Those are durable workflow and stop
instructions that belong in Git, not in the invocation. The candidate therefore
does not fully achieve the requested minimal prompt contract.

## Required correction

The corrected canonical invocations are:

- Execution or correction:
  `Synchronize from Git and execute the active task.`
- Merge and closure:
  `Synchronize from Git and execute the active task's merge and closure workflow. Approved exact remote head: <SHA>.`

The active task status and committed Git instructions determine whether the
operation is normal execution, correction, or merge. Invocation text must not
repeat publication states, push instructions, validation, cleanup, workflow, or
stop conditions.

Update only the six task-owned paths. Strengthen the focused governance test to
assert the exact minimal invocations and the prohibition on workflow/stop
restatement.

## Evidence reviewed

### GitHub-observed

- `main` remains `a7b4e1d3701ff163942f0c42a8e7a91388840b51`.
- Rejected branch head is
  `fa8ff9612732f34a4d90275da017c7125ec9cea0`.
- The rejected candidate is exactly two commits ahead of main.
- The complete candidate diff contains only the six authorized paths.
- Rejected implementation `2f1ec3efdd6f68d5c8097e534c869d982ab2d6ec`
  changes only `AGENTS.md`, `TASK_EXECUTION_STANDARD.md`, and the focused
  governance test.
- The rejected publication commit changes only the three stable execution
  files and carries a durable Tier 1 receipt.

### Candidate-reported local validation

The rejected receipt records JSON, Markdown/current-state, task-authoring,
changed-path, `git diff --check`, and receipt checks as passed; the focused test
reported `1 passed`; Docker, Ruff, mypy, and the full suite were `not_required`.
Those checks establish integrity of the rejected tree but do not resolve the
behavioral contradiction.

## Correction authorization

One bounded correction cycle is authorized on the existing branch.

- **Task execution authorized:** true
- **Correction execution authorized:** true
- **Merge authorized:** false
- **PR creation authorized:** false
- **Blockers:** none
- **Capability authority changed:** false
- **MMM/GeoX adoption:** deferred and separately unauthorized
- **GeoX active builder:** unchanged

Publish a new exact corrected review head with one correction implementation SHA,
a current completion report, the complete Tier 1 gate, and a durable exact-tree
receipt. Stop at `ready_for_review` or accurate `blocked`.
