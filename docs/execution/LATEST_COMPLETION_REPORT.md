# TASK_COMPLETION_REPORT_V2

## Identity and review decision

- **Task ID:** `MIP_LEAN_REPOSITORY_DELIVERY_STANDARD_001`
- **Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
- **Feature branch:** `docs/mip-lean-repository-delivery-standard-001`
- **Rejected review head:** `9f829c3e12ca79698c6cabda1e8089e9d4567fa1`
- **Prior correction implementation commit:** `9dda47f3f90877161175c02a736694d5ee253f48`
- **Current decision:** `changes_requested`

## Review result

The lean task-sizing standard and risk-tier validation behavior are accepted.
The candidate is rejected only because the final exact-head validation results
were available in Codex-local terminal output but were not durably recoverable
from Git.

The missing evidence included the exact command outcomes, focused test count,
complete and normalization changed-path checks, local worktree state, and the
distinction between GitHub-observed and locally observed evidence. Requiring the
user to paste those results into chat violates the repository-native handoff
objective.

## Authorized bounded correction

Correction execution is authorized for one Tier 1 outcome:

- make the review-publication commit message the durable validation receipt for
  that commit's exact Git tree;
- require the completion report to record substantive validation, exact counts,
  blockers, limitations, validation debt, sibling impact, and authority impact;
- require final publication trailers containing the implementation SHA, gate,
  result, changed-path checks, focused test count, full-suite disposition,
  worktree state, evidence source, and authority impact;
- forbid task-owned changes after receipt publication; and
- make review reconstructable from Git without pasted terminal or chat output.

Only these paths are correction-owned:

- `AGENTS.md`
- `docs/execution/TASK_EXECUTION_STANDARD.md`
- `docs/execution/ACTIVE_TASK.md`
- `docs/execution/EXECUTION_STATE.json`
- `docs/execution/LATEST_COMPLETION_REPORT.md`

No new resolver, automation, task schema, status file, checkpoint system,
product/runtime/analytical code, coordination record, MMM change, or GeoX change
is authorized.

## Required validation

- JSON parsing: required.
- Markdown/current-state consistency: required.
- Complete task diff limited to the seven original task-owned paths: required.
- Correction delta limited to the five correction-owned paths: required.
- `git diff --check`: required.
- Focused governance test
  `tests/governance/test_repo_native_execution_handoff.py`: required.
- Final publication commit trailer inspection: required.
- Local/remote receipt-head equality: required.
- Docker, Ruff, mypy, and full suite: `not_required` unless an unexpected
  executable dependency or repository-authored gate is discovered.

If any required validation fails or cannot run, publish accurate `blocked`
state. Do not create a passing receipt from incomplete evidence.

## Publication and authority

On success, publish one real correction implementation SHA and one final
review-publication commit whose message contains the exact-tree validation
receipt. Set `ready_for_review`, close correction execution, clear blockers, and
leave merge, PR creation, sibling adoption, and capability authority false.

Push the exact receipt head and stop without merge, PR, rebase, squash,
force-push, branch deletion, or sibling modification.
