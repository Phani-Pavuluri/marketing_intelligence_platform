# Active Task

**Status:** superseded
**Owner:** MIP program governance
**Last updated:** 2026-08-03
**Last verified:** 2026-08-03

## Identity

- **Task ID:** `MIP_GIT_AUTHORITATIVE_THIN_LAUNCHER_STANDARD_002`
- **Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
- **Feature branch:** `docs/mip-git-authoritative-thin-launcher-standard-002`
- **Authorization head:** `786f7ddbf30dcdada794af6691d18e68bf762542`
- **Rejected exact remote head:** `4c682711365ba8255fcb1e4a9a3643cf5842efec`
- **Implementation candidate:** `fe767166b08522764976f987368c8df5f6a9279f`
- **Disposition:** superseded without merge
- **Capability authorizations changed:** `false`

## Final decision

This task is superseded without merge. The thin launcher successfully drove Codex to a remote `ready_for_review` outcome in one invocation, but the implementation did not satisfy the frozen acceptance contract and weakened existing repository safeguards.

The branch is historical evidence only. Do not resume, merge, rebase, force-update, delete, or create a pull request from it.

## Final review findings

1. `tests/governance/test_repo_native_execution_handoff.py` removed substantial existing coverage for bootstrap commands, stable execution paths, shallow-history recovery, task-authoring range semantics, definition-ready requirements, merge/closure invariants, resumed-branch behavior, blocked-state requirements, and merged-state requirements. The active task explicitly required those existing invariants to continue passing.
2. `test_current_lifecycle_state_is_coherent` validates only `ready_for_review` and returns immediately for every other state. It does not implement the task's required coherent rules for `blocked` and `merged` states.
3. The lifecycle test rejects certain correction headings but does not enforce the task's required stale operative-text exclusions, including correction-cycle authorization, unfinished publication, or missing-receipt language.
4. The direct prohibited-instance test checks only the current task ID, current branch, `MMM`, `GeoX`, and `pytest`. Exact launcher equality provides some protection, but the explicit negative assertions do not cover the full frozen set of paths, commands, test names/counts, dependency IDs, blocker IDs, rejected heads, correction details, or sibling lifecycle values.
5. The locally reported `6 passed`, Ruff, mypy, JSON, boundary, changed-path, and diff-check results are credible execution evidence but not acceptance evidence because the test suite passed after removing required safeguards.

## Process decision

Do not continue investing in a repository-wide thin-launcher standard before product integration. Future product checkpoints should use full, task-specific Codex prompts authored from live Git evidence. Durable task state remains in Git; the execution prompt may restate the exact implementation scope, acceptance criteria, validation, commit/push, and stop conditions to keep them salient during execution.

## Authority

Task execution, correction execution, merge, pull-request creation, sibling authority, analytical authority, release authority, and capability authority are false. No product or package integration work is authorized by this supersession.

## Next direction

After MIP `main` records this supersession, the next product task should be selected from live Git, with `MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_CONTRACT_001` as the current roadmap candidate. It must be separately authored and authorized.
