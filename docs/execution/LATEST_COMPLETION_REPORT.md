# MIP P2 Capability Checkpoint Ledger Recovery — Changes Requested

- **Milestone:** `MIP_P2_CAPABILITY_CHECKPOINT_LEDGER_RECOVERY_001`
- **Branch:** `docs/mip-p2-capability-checkpoint-ledger-recovery-001`
- **Reviewed and rejected remote head:** `35e03b2852022ef510f8fff409a06e26f975f29e`
- **Implementation commit under review:** `3727a7973f046a8046f6c349856949c7df1555eb`
- **Current decision:** `changes_requested`
- **Correction cycles authorized:** one of one

## Review finding

The ledger implementation and its paragraph-context-aware stale-pin correction are acceptable in direction. JSON parsing, the focused ledger test, Ruff, mypy, and `git diff --check` passed. The required Docker gate failed with `1 failed, 2545 passed, 5 skipped, 1 warning`.

The remaining failure is in `tests/test_cross_repository_coordination_control_plane.py`. That test correctly validates the immutable historical coordination snapshot, but its final mutable-execution section incorrectly requires `MIP_COORDINATION_POST_MERGE_CLOSURE_RECONCILIATION_001` to remain the current task in `docs/execution/EXECUTION_STATE.json`. The current authorized task is `MIP_P2_CAPABILITY_CHECKPOINT_LEDGER_RECOVERY_001`, so the assertion is obsolete.

Creating and merging a separate prerequisite task would move `main` and make this branch non-fast-forwardable under the repository's no-rebase and no-merge-commit rules. The defect is directly adjacent to the execution-document alignment changed by this milestone. The task's single correction cycle therefore owns only this existing test path in addition to the prior task-owned paths.

## Required correction

Preserve every assertion covering the historical coordination snapshot, historical repository pins, workstreams, blockers, ownership, authority, ordered historical sequence, protocol, history, and provenance.

Replace only the obsolete assertions against mutable current execution files with generic lifecycle-coherence checks:

- current execution repository is MIP;
- current task ID is non-empty and appears in `ACTIVE_TASK.md` and this report;
- lifecycle status is represented consistently across the three execution files;
- merge, PR, and capability-authority flags remain false;
- superseded task-specific fields such as `current_mip_main_at_review` and `prior_task_closure_sha` are not required from the current execution state.

Do not edit `CROSS_REPOSITORY_COORDINATION_STATE.json`, coordination history, sibling repositories, runtime or analytical code, CI, Docker, dependencies, or authority rules.

## Required validation

Run on one frozen task-owned tree:

```bash
python3 -m json.tool docs/program/P2_CAPABILITY_CHECKPOINT_LEDGER.json >/dev/null
poetry run pytest -q tests/docs/test_p2_capability_checkpoint_ledger.py
poetry run pytest -q tests/test_cross_repository_coordination_control_plane.py
poetry run pytest -q tests/docs
poetry run ruff check tests/docs/test_p2_capability_checkpoint_ledger.py tests/test_cross_repository_coordination_control_plane.py
poetry run mypy
git diff --check
make validate
```

Publish `ready_for_review` and the exact-tree validation receipt only if every required command passes. Otherwise publish a Git-durable blocked state with exact diagnostics.

## Authority and Git

No PR or merge is authorized. No sibling, analytical, runtime, capability, pilot, or production authority changes. Do not merge, squash, rebase, force-push, or create a merge commit.

Two transient metadata-history commits created and then removed an empty `docs/tasks/.placeholder`; they leave no tree diff. They must not appear in final changed paths or be represented as implementation evidence.
