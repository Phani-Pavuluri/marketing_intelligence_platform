# TASK_AUTHORIZATION_REPORT

## Current decision

- **Task ID:** `MIP_GIT_AUTHORITATIVE_THIN_LAUNCHER_STANDARD_002`
- **Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
- **Status:** `authorized`
- **Pre-authoring base:** `45eca4e8ca75bd9f152c2d025f9c57773dfa27ee`
- **Feature branch:** `docs/mip-git-authoritative-thin-launcher-standard-002`
- **Risk tier:** Tier 1 repository execution governance
- **Implementation SHA:** not yet created
- **Capability authority:** unchanged

## Orientation and eligibility evidence

Connected GitHub verified that MIP `main` first recorded `MIP_GIT_AUTHORITATIVE_THIN_LAUNCHER_STANDARD_001` as superseded without merge at `45eca4e8ca75bd9f152c2d025f9c57773dfa27ee`. The predecessor consumed its single correction cycle and has no remaining task, correction, merge, or PR authority. Its preserved branch head `6e90f1a23b5ff952264e15e634b469be06f52c56`, final rejected head `69f7fd7178844576b8a3bdb84a881b3d38a3b8c5`, and candidate implementation `0e08dc1f77f91ce45e45d1f874c5ae505dfea129` are historical evidence only.

Live sibling evidence is read-only:

- MMM `main` is `f2e0eade0ad917c1b28ab5521e6d35a35047d988`. `MMM_GIT_AUTHORITATIVE_THIN_LAUNCHER_STANDARD_ADOPTION_001` is proposed and blocked pending an exact merged MIP thin-launcher standard.
- GeoX `main` is `e9b7d311ecaf5a90e227d8299f745a0e8f332368`. `GEOX_EXECUTION_BRANCH_BINDING_REAUTHORING_001` is superseded without merge.

Neither sibling owns MIP execution-standard files. MIP cannot authorize, correct, merge, supersede, or otherwise modify either sibling task.

## Primary outcome

The authorized task is a minimal replacement of the merged invocation-only prompt rule. It must:

- make the Git-authoritative thin launcher the sole MIP launcher standard;
- publish exact execution, correction, and merge launcher bodies;
- compare extracted launcher blocks directly to those frozen bodies;
- reject concrete task-instance values directly inside each block; and
- enforce one coherent current lifecycle state across `ACTIVE_TASK.md`, `EXECUTION_STATE.json`, and `LATEST_COMPLETION_REPORT.md`.

The complete behavior, canonical text, owned paths, prohibited scope, acceptance evidence, validation gate, publication contract, and sibling impact are recorded in `docs/execution/ACTIVE_TASK.md`.

## Supersession and overlap decision

The predecessor branch is not resumed, merged, rebased, or copied wholesale. Specific useful wording may be independently reimplemented only where it satisfies the new frozen contract and exact-tree validation.

No live MIP, MMM, or GeoX task owns the same MIP file surface. The task does not modify roadmap or coordination state and does not absorb product, GeoX, MMM, or method-promotion consumer work.

## Task-authoring boundary

The authoring range starts at `45eca4e8ca75bd9f152c2d025f9c57773dfa27ee` and changes only:

- `docs/execution/ACTIVE_TASK.md`
- `docs/execution/LATEST_COMPLETION_REPORT.md`

The commit containing this report is the final task-authoring head. The immediate next commit must be state-only, changing only `docs/execution/EXECUTION_STATE.json` to record that exact authoring head and authorize the declared feature branch. The feature branch must be created from the resulting synchronized state-only `main`.

## Validation requirement

The Tier-1 gate requires:

- JSON parsing;
- strengthened Markdown/current-state coherence validation;
- task-authoring and state-only authorization boundaries;
- exact six-path scope;
- `git diff --check`;
- focused governance pytest with exact count;
- configured Ruff and mypy for the changed test;
- exact-tree validation receipt;
- no task-owned changes after the receipt;
- local/remote feature-head equality.

Docker-backed `make validate` and the full suite are `not_required` for this documentation/governance-only surface.

## Execution invocation

Until this task merges, MIP `main` still contains the prior invocation-only rule. The exact Codex invocation for this successor is:

`Synchronize from Git and execute the active task.`

All task meaning, branch identity, validation, publication, and authority instructions remain in Git.

## Authority and non-actions

This authorization changes only MIP repository-execution governance. It does not modify or authorize product code, contracts, adapters, fixtures, orchestration, LLM behavior, reporting, UI, analytical truth, sibling work, live integration, real data, persistence, simulation, optimization, recommendations, assignment, pilot, production, or package-side agents.

Task execution becomes true only in the immediate state-only authorization commit. Merge authority, PR authority, correction authority, sibling authority, analytical authority, and capability authority remain false. No implementation occurred during task authoring.
