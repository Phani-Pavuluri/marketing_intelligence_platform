# Active Task

<!-- BEGIN MIP TASKCTL EXECUTION VIEW -->
# Active Task

**Status:** merged

_Generated from `EXECUTION_STATE.json`; do not edit._

- **Task ID:** `MIP_REVIEW_OBSERVER_FIXTURE_ISOLATION_001`
- **Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
- **Execution mode:** `branch_and_fast_forward`
- **Base SHA:** `ea5bb210a471a0356d8b180c0aeee356e35b2b78`
- **Authorization provenance:** `6393452e8e2f4cf4c9617d099aa73aa53d174c45`
- **Feature branch:** `fix/mip-review-observer-fixture-isolation-001`
- **Feature branch created:** `false`
- **Task execution authorized:** `false`
- **Correction execution authorized:** `false`
- **Merge authorized:** `false`
- **PR creation authorized:** `false`
- **Implementation commit:** `c23cef613850e3cd6d56a78547006a3d20c1d248`
- **Reviewed head:** `6428afaa495b15f315f2ba6961cd5ca87b29cdb1`
- **Rejected review head:** `null`
- **Rejected implementation commit:** `null`
- **Approval commit:** `null`
- **Blockers:** `none`
- **Maximum correction cycles:** `1`
- **Correction cycles completed:** `0`
- **Correction cycles remaining:** `1`
- **Review decision:** `merged`
- **Local feature-branch cleanup:** `observed_deleted`
- **Remote feature-branch cleanup:** `observed_deleted`
- **Capability authorizations changed:** `false`
<!-- END MIP TASKCTL EXECUTION VIEW -->

## MIP_REVIEW_OBSERVER_FIXTURE_ISOLATION_001 — task contract

Primary mergeable outcome: make observer test fixtures independent of the
repository's current execution lifecycle and task-specific authority metadata.
This is a standalone test-isolation repair discovered while implementing the
owner-authorized autopilot setup. Muse-Spark owns implementation; Codex reviews.

Only tests/test_review_observer.py is owned for implementation, plus the three
stable execution files for lifecycle/evidence. Exact branch:
fix/mip-review-observer-fixture-isolation-001. Tier 2 fixture repair; no observer
runtime, taskctl, product, schema or validator source changes. No PR or merge.
Required gate: all observer tests, explicit regression evidence against current
and corrected/exhausted canonical lifecycle templates, Docker make validate,
Ruff/mypy, taskctl, JSON, diff/auth-boundary/owned-path checks, frozen publication
receipt and local/remote feature-head equality. Approval mode user_exact_head.

Observed defect: environment fixture copies live EXECUTION_STATE.json then
replaces selected fields. Post-correction flags/rejected heads/counters and task
metadata contaminate synthetic proposed/authorized/ready/merged scenarios.
At validator head 3af72b014987f8e76631ab3da3c4575f8e847d4d, Docker reports
9 failing observer tests, 2676 passing and 5 skipped; the isolated validator
suite independently passes 84. This is evidence, not permission to skip gates.

Observable behavior: every synthetic observer repository is authored from a
complete, deterministic fixture-owned canonical state valid under the existing
state validator, with fixture-owned authorization/branch/implementation/evidence
and authority provenance. Live task metadata is not an input to that fixture.
Preserve all existing behavior assertions and negative cases; do not weaken
observer/state validation, remove tests, skip failures or alter canonical live
repository state to make tests pass. Any live-schema drift must fail explicit
fixture validation instead of importing mutable execution facts. New required
schema fields can be consciously adopted in fixture data by a future task.

Acceptance: prove the full observer suite passes without reading the real
EXECUTION_STATE as a fixture template, and the fixture remains valid when the
real task is authorized, changes_requested, ready_for_review after correction
with completed=1/remaining=0 and rejected history, or merged. Demonstrate this
with isolated/in-memory temporary fixtures; never rewrite live canonical files.
Tests must retain dedup, historical review, closure, wrong-origin/corruption,
lock/recovery, failure/staleness, multiple checkpoints and archived-ref cases.
Use meaningful regressions proving independence rather than implementation-only
assertions. Validate the exact final task-owned tree under the required gate.

Prerequisite DEP-MIP-OBSERVER-IMPLEMENTATION-MERGED-001 is satisfied at
cf0ac9feafc65c3f35266b550cf33f5a4183203a in current main ancestry.
WS-MIP-REVIEW-OBSERVER-FIXTURE-ISOLATION-001 owns test isolation only; parked
WS-MIP-BOUNDED-WORK-PLAN-VALIDATOR-001 owns different paths and is not executed.
Only MIP affected/modified; siblings read-only; no coordination refresh.

The prior validator head is blocked for review and must not merge. Its canonical
ready state cannot legally transition to blocked (E_TRANSITION_EDGE), and its
correction cycle is exhausted. The parked_setup_workstreams record preserves
this blocker durably without editing duplicated lifecycle fields or inventing
another correction cycle. Do not merge, rebase, modify or execute the parked
validator branch. Recovery on a fresh main baseline is a separately authored
successor after this repair is merged; this task does not authorize recovery.

No product, analytical, sibling, runtime, worker dispatch, global settings,
service restart, automated message, plan materialization, merge activation or
capability authority. Documentation policy changes are prohibited. Missing
owned-scope remedy must publish blocked rather than ready_for_review with a
failed required gate. Completion must explicitly record every required gate
category as passed/failed/blocked, limits and deferred recovery.
Compatibility/migration: not_applicable. Unresolved execution-blocking design
questions: none for fixture isolation. Publish ready_for_review only when all
required gates pass, with a durable exact-tree receipt; stop without merging.
