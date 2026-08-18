# MIP Execution Lifecycle Single-Source Consistency — Authorized

- **Milestone:** `MIP_EXECUTION_LIFECYCLE_SINGLE_SOURCE_CONSISTENCY_001`
- **Current decision:** `authorized`
- **Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
- **Pre-authoring base:** `4a392c7ecf7b421dae9fbd11e50eed01c168efa9`
- **Authorization provenance:** `e1839bcfad482b2f79343202ac68d25a666acc42`
- **Planned feature branch:** `feat/mip-execution-lifecycle-single-source-consistency-001`
- **Risk tier:** Tier 2
- **Execution authorized:** `true`
- **Merge / PR authorized:** `false`

## Authorized outcome

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

The GeoX prerequisite is satisfied. A fresh read-only clone verified live
GeoX `origin/main` at `5ab881296c7c8248076bad61292b255aaade11d8`.
Its stable execution state and closure report record
`GEOX_D5_POWER_CONTROL_GEOMETRY_REPAIR_002` as merged and closed, with:

- externally approved review head: `9d17ad44f3a8cb860dfed36af860487c0877d12b`;
- implementation commit: `5a7b9ff9faecb50a28bab63688c9a53594fa733f`;
- authorization-bearing contract: `5503ef3b8214a0f2bdb1f444c9b673ddce1ed587`.

MIP was synchronized at `2c44a78ce3dd0852201021d479827bc44927fe18`
before this authorization update. MMM remains observed at
`fe8e784923994406a2e4907d28debd872d61fd73`; no sibling state was modified and
no coordination refresh was authorized.

## Why this is staged now

The current execution model already detects some cross-file inconsistencies, but
mutable lifecycle facts are still independently represented in multiple files.
That permits the historical class of correction-cycle, status, blocker, SHA,
and authority drift. The proposed milestone removes that duplication in the MIP
governance owner before GeoX resumes the rest of its baseline-repair sequence.

## Authorization validation

The authorization update is limited to the three stable execution metadata
files. JSON parsing, repository-authored execution-handoff validation,
`git diff --check`, exact changed-path checks, authority checks, authorization
ancestry, and local/remote equality are required before branch publication.

The future implementation must still run focused execution-governance tests,
JSON validation, Ruff, mypy, `git diff --check`, and the repository Docker-backed
`make validate` gate on the frozen candidate tree.

No implementation validation has run in this authorization-only session.

## Deferred adoption order

After MIP implementation and exact-head merge:

1. GeoX adopts the control before its next baseline-repair milestone.
2. GeoX resumes baseline repair and P2 isolation/certification sequencing.
3. MMM adopts the control before its next P2 implementation.
4. CI/git-hook enforcement and richer automation remain separate.

The first main authorization commit may contain `authorization_head_sha: null`.
A metadata-only finalization commit will record that first authorization commit
as immutable provenance, and the feature branch will start from the finalized
synchronized main. The intervening diff is restricted to the three stable
execution files.

No PR or merge is created by authorization. No product, analytical, P2,
sibling, calibration, simulation, optimization, planning, recommendation,
runtime, real-data, pilot, production, or capability authority changes.
