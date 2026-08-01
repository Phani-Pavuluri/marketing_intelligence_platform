# Active Task

**Status:** superseded
**Owner:** MIP program governance
**Last updated:** 2026-07-31
**Last verified:** 2026-07-31

## Identity

- **Task ID:** `MIP_ACTIVE_TASK_CONTEXT_RESOLVER_001`
- **Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
- **Main before supersession:** `11c062eb785b3518d531992aa554d0a3a4c0b84b`
- **Feature branch:** `feat/mip-active-task-context-resolver-001`
- **Superseded branch head:** `b96dfc4365d5aadf9425d31aa576664f58270fa5`
- **Preserved candidate implementation:** `785d83f25891274a42a5a82efbd17103563c29a7`
- **Capability authorizations changed:** `false`

## Supersession decision

This task is superseded without merge. Its branch combined repository resolution,
lifecycle and authority enforcement, human-view normalization, correction
resumption, coordination-test repair, and a 25-case semantic matrix under one
long-lived task. The branch reached thirteen commits ahead of `main` and then
blocked on a governance-test contract outside its owned paths.

The candidate implementation and its validation evidence remain useful, but the
task boundary is not an acceptable merge unit under the project-wide delivery
model now authorized by the user. Do not resume, merge, or widen this branch.
Preserve it as historical partial evidence for later narrowly scoped resolver
work.

## Preserved evidence

The superseded branch reports:

- pointer-first repository task resolution;
- final candidate implementation `785d83f25891274a42a5a82efbd17103563c29a7`;
- exact branch head `b96dfc4365d5aadf9425d31aa576664f58270fa5`;
- focused resolver and governance validation: 46 passed;
- Docker-backed `make validate`: 2585 passed, 5 skipped, 1 warning;
- Ruff and mypy success across 472 source files; and
- one remaining governance-test contract conflict.

These validation results are execution-reported historical evidence, not an
approval or merge authorization.

## Authority and next work

- Task and correction execution are disabled.
- Merge and PR creation are disabled.
- No product, analytical, runtime, recommendation, pilot, or production
  capability changed.
- MMM remains merged with no active implementation task.
- GeoX retains independent authority over its active builder task; MIP does not
  split, block, or modify it.
- `MIP_LEAN_REPOSITORY_DELIVERY_STANDARD_001` is the next eligible MIP task but
  remains unauthorized until its task-authoring and state-only commits are
  recorded on synchronized `main`.
