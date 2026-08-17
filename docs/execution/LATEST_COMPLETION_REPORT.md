# MIP Execution Lifecycle Single-Source Consistency — Proposed

- **Milestone:** `MIP_EXECUTION_LIFECYCLE_SINGLE_SOURCE_CONSISTENCY_001`
- **Current decision:** `proposed`
- **Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
- **Pre-authoring base:** `4a392c7ecf7b421dae9fbd11e50eed01c168efa9`
- **Planned feature branch:** `feat/mip-execution-lifecycle-single-source-consistency-001`
- **Risk tier:** Tier 2
- **Execution authorized:** `false`
- **Merge / PR authorized:** `false`

## Proposed outcome

Create the MIP-owned single-source execution lifecycle control that makes
`EXECUTION_STATE.json` canonical for mutable lifecycle facts and makes the
lifecycle snapshots in `ACTIVE_TASK.md` and `LATEST_COMPLETION_REPORT.md`
deterministic generated views.

The milestone includes a `taskctl` checker/synchronizer/transition controller,
state-machine invariants, regression coverage for status/blocker/SHA/correction
counter drift, and MIP executor/agent instructions that require lifecycle
changes to pass through that control surface.

No GeoX/MMM adoption, product/analytical behavior, P2 capability work, CI/git
hook, planning, calibration, recommendation, pilot, or production authority is
included.

## Scheduling state

Execution is intentionally deferred until the in-flight GeoX task
`GEOX_D5_POWER_CONTROL_GEOMETRY_REPAIR_002` is merged/closed on GeoX
`origin/main`.

Observed during authoring:

- MIP main: `4a392c7ecf7b421dae9fbd11e50eed01c168efa9`
- GeoX main: `79be6ca2656381672c3617fe71c5ffefbcb836e9`
- GeoX blocked feature head: `ff148324a668ff8abf696758f0b78461d5ca4994`
- MMM main: `fe8e784923994406a2e4907d28debd872d61fd73`

The blocked GeoX feature branch is not merged dependency evidence.

## Why this is staged now

The current execution model already detects some cross-file inconsistencies, but
mutable lifecycle facts are still independently represented in multiple files.
That permits the historical class of correction-cycle, status, blocker, SHA,
and authority drift. The proposed milestone removes that duplication in the MIP
governance owner before GeoX resumes the rest of its baseline-repair sequence.

## Validation planned

The future implementation must run focused execution-governance tests, JSON
validation, Ruff, mypy, `git diff --check`, and the repository Docker-backed
`make validate` gate on the frozen candidate tree.

No implementation validation has run for this proposed task because execution is
not authorized and the GeoX scheduling prerequisite is unresolved.

## Deferred adoption order

After MIP implementation and exact-head merge:

1. GeoX adopts the control before its next baseline-repair milestone.
2. GeoX resumes baseline repair and P2 isolation/certification sequencing.
3. MMM adopts the control before its next P2 implementation.
4. CI/git-hook enforcement and richer automation remain separate.

No PR or merge is created by task authoring. No capability authority changes.
