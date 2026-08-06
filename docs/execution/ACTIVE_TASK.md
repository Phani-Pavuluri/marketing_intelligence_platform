# Active Task

**Status:** changes_requested
**Task ID:** `MIP_P2_CAPABILITY_CHECKPOINT_LEDGER_RECOVERY_001`
**Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
**Feature branch:** `docs/mip-p2-capability-checkpoint-ledger-recovery-001`
**Execution mode:** `branch_and_fast_forward`
**Risk tier:** Tier 3
**Capability authority changed:** `false`
**Unresolved execution-blocking design questions:** none

## Objective

Create one machine-readable P2 capability-checkpoint ledger and align MIP program-navigation documents. The ledger distinguishes implementation on main, component validation, producer certification, consumer verification, and downstream eligibility. This task does not modify or certify GeoX/MMM, resume the parked bridge, construct CalibrationSignal, alter TrustReport/DecisionSurface, or authorize analytical, runtime, planning, recommendation, real-data, pilot, or production behavior.

## Prerequisite evidence

- MIP main: `c3897ed0b1ca096d186a9cabda36e1b926c4e71f`.
- MMM main: `fe8e784923994406a2e4907d28debd872d61fd73`.
- GeoX main: `b11646bab1f461964644a6526ef4967a8f04624d`.
- Reviewed and rejected remote head: `35e03b2852022ef510f8fff409a06e26f975f29e`.
- Existing implementation commit: `3727a7973f046a8046f6c349856949c7df1555eb`.

## Owned paths

The task may modify only:

- `docs/program/P2_CAPABILITY_CHECKPOINT_LEDGER.json`
- `docs/program/PROGRAM_CURRENT_STATE.md`
- `docs/program/REPOSITORY_CHECKPOINTS.md`
- `docs/program/NEXT_EXECUTION_SEQUENCE.md`
- `docs/execution/REPOSITORY_CONTEXT_INDEX.md`
- `tests/docs/test_p2_capability_checkpoint_ledger.py`
- `tests/test_cross_repository_coordination_control_plane.py` only for the correction specified below
- `docs/execution/ACTIVE_TASK.md`
- `docs/execution/EXECUTION_STATE.json`
- `docs/execution/LATEST_COMPLETION_REPORT.md`

Source/runtime code, other tests or fixtures, coordination history/state, standards, CI, Docker, dependencies, MMM, GeoX, and the parked bridge are prohibited.

## Preserved ledger behavior

Preserve schema `mip_p2_capability_checkpoint_ledger_v1`, the exact current repository pins, seven acyclic capability records, the exact six-item unauthorized execution sequence, and all false authority flags. Preserve paragraph-context-aware historical-pin validation: historical coordination provenance is permitted only when explicitly historical and remains rejected as current state.

## Correction cycle 1 of 1

The full Docker gate at rejected head `35e03b2852022ef510f8fff409a06e26f975f29e` failed because `tests/test_cross_repository_coordination_control_plane.py` validates a historical coordination snapshot but also hard-codes `MIP_COORDINATION_POST_MERGE_CLOSURE_RECONCILIATION_001` as the task ID in the mutable current execution files.

Modify only the stale mutable-current-task portion of that test. Preserve every assertion covering the historical coordination snapshot, historical repository pins, workstreams, blockers, ownership, authority, ordered historical sequence, protocol, history, and historical provenance.

Replace the obsolete current-task assertions with generic lifecycle-coherence checks:

- current `EXECUTION_STATE.json` repository is MIP;
- current task ID is a non-empty string and appears in `ACTIVE_TASK.md` and `LATEST_COMPLETION_REPORT.md`;
- current status is represented consistently in the active task and report;
- `merge_authorized`, `pr_creation_authorized`, and `capability_authorizations_changed` remain false;
- the test must not require task-specific fields from the superseded closure task, including `current_mip_main_at_review` or `prior_task_closure_sha`.

Do not change historical coordination JSON or documentation to satisfy the test. Do not weaken the test into a simple existence check.

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

Task-owned failures must be corrected. Publish `ready_for_review` only when every required gate passes and an exact-tree validation receipt is created. Otherwise publish an evidenced `blocked` state.

## Git workflow

Use the existing feature branch. Commit and push the correction and exact-tree validation receipt. Do not create a PR, merge, squash, rebase, force-push, or merge commit. Do not modify sibling repositories or change analytical, capability, merge, PR, pilot, or production authority.
