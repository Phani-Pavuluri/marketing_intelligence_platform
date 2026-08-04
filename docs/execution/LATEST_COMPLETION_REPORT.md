# TASK_REVIEW_REPORT_V2

## Current decision

- **Current decision:** `changes_requested`
- **Task ID:** `MIP_GIT_AUTHORITATIVE_THIN_LAUNCHER_STANDARD_001`
- **Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
- **Feature branch:** `docs/mip-git-authoritative-thin-launcher-standard-001`
- **Rejected exact remote head:** `e390f1b47f8a7c5dfaa7a05613c2c4de73e4a548`
- **Retained implementation SHA:** `dde6969b1192b97aea519c9589d27186f19b6db2`
- **Pre-review MIP main:** `9bed0f30879e68473a37b0e65d449ea0b6a6e3f3`
- **Risk tier:** Tier 1 repository execution governance
- **Correction execution:** one bounded cycle authorized
- **Merge and PR authority:** false
- **Capability authority:** unchanged

## Exact remote review scope

Connected GitHub observed the rejected feature-branch head
`e390f1b47f8a7c5dfaa7a05613c2c4de73e4a548` two commits ahead of and zero
commits behind MIP `main` at `9bed0f30879e68473a37b0e65d449ea0b6a6e3f3`.
The branch changes exactly the six task-owned paths:

- `AGENTS.md`
- `docs/execution/TASK_EXECUTION_STANDARD.md`
- `tests/governance/test_repo_native_execution_handoff.py`
- `docs/execution/ACTIVE_TASK.md`
- `docs/execution/EXECUTION_STATE.json`
- `docs/execution/LATEST_COMPLETION_REPORT.md`

The publication receipt names implementation parent
`dde6969b1192b97aea519c9589d27186f19b6db2` and reports JSON, Markdown,
authoring-boundary, changed-path, diff-check, focused-test, Ruff, and mypy
success. These validation results are locally reported evidence; GitHub directly
verifies only the exact commit history, changed paths, file contents, and remote
branch topology.

## Review findings

### 1. Blocking contract contradiction

`AGENTS.md` still says that Codex prompts are invocation-only and that the exact
execution invocation remains `Synchronize from Git and execute the active task.`
That is the superseded rule this task is explicitly required to replace. The same
file then allows the new thin launcher, creating two competing prompt contracts.
The implementation therefore does not deliver one unambiguous
Git-authoritative thin-launcher standard.

### 2. Focused tests preserve the obsolete rule

The existing consistency test still requires the headings and phrases
`Invocation-only prompt rule`, `Codex prompts are invocation-only`, and
`Synchronize from Git and execute the active task.` The four added tests mostly
check for isolated phrase presence and do not prove that the old one-line rule is
absent, that the three canonical launcher blocks are the operative contract, or
that prohibited task-instance values are excluded from those blocks. The
launcher-duplication test also absorbs unrelated lifecycle-state assertions,
weakening the required separation of the four semantic groups.

The reported `5 passed` result is credible as a test-execution claim but is not
acceptance evidence for the frozen contract because the assertions encode the
wrong behavior.

### 3. Sibling evidence is stale at review

The rejected tree still records MMM as `ready_for_review` and GeoX as
`changes_requested`. Live GitHub now shows:

- MMM `main` at `ac546548784385baab67d7c935e5a4fcdfc9e1af`, with
  `MMM_REPOSITORY_EXECUTION_PROTOCOL_ADOPTION_001` merged at reviewed head
  `c370dc7cd59a61cc2e19025d1a2328c7867b63be`. That merge adopted the older
  invocation-only MIP standard and cannot be silently treated as current thin-
  launcher adoption.
- GeoX `main` at `e9b7d311ecaf5a90e227d8299f745a0e8f332368`, with
  `GEOX_EXECUTION_BRANCH_BINDING_REAUTHORING_001` superseded without merge and
  preserved branch head `9d0da6bb96dd7711ab8c91bbef21a80a4b816973`.

MIP does not own either sibling disposition, but its completion evidence must
accurately state the live impact and deferred owner-repository follow-up.

## Required correction

1. Remove the obsolete invocation-only and exact one-line execution contract
   from `AGENTS.md`; make the Git-authoritative thin launcher the sole execution
   and correction launcher standard.
2. Update the focused tests to enforce the replacement directly: reject the old
   rule, assert the canonical execution/correction/merge launcher contracts,
   verify their allowed and prohibited instance values, and keep each of the
   four named semantic groups focused and separate.
3. Refresh MMM and GeoX live evidence in the stable execution files without
   modifying or authorizing either sibling repository.
4. Run the complete frozen Tier-1 validation gate on the corrected exact tree,
   publish a new implementation SHA and exact-tree receipt, push, and verify
   local/remote branch-head equality.
5. Stop only at a new Git-durable `ready_for_review` or genuine `blocked` state.

## Validation disposition

- GitHub-observed changed paths and ancestry: PASS
- GitHub-observed semantic contract review: FAIL
- Locally reported JSON/Markdown/boundary/diff checks: retained, not independently rerun
- Locally reported focused pytest: `5 passed`, insufficient because assertions encode obsolete behavior
- Locally reported Ruff and mypy: retained, not independently rerun
- Docker-backed `make validate`: `not_required` by the active Tier-1 gate
- Full suite: `not_required`

## Blockers, limitations, and validation debt

The task is not externally blocked; one bounded in-scope correction is
available. Validation debt is the missing semantic enforcement of the actual
replacement contract and stale sibling evidence at the rejected head. No
product, analytical, runtime, contract, adapter, fixture, orchestration, LLM,
UI, recommendation, simulation, optimization, or capability behavior is under
review or changed.

## Sibling and consumer impact

MMM and GeoX remain authoritative for their own repositories. MIP cannot revise,
approve, supersede, or authorize their work. After this MIP standard is corrected
and merged, MMM may separately authorize a successor to replace its now-merged
older prompt standard; GeoX may separately authorize future adoption after its
superseded task. Consumer verification is `not_applicable` for this MIP-only
governance correction. No sibling successor is authorized by this review.

## Newly eligible work and authority impact

No new product or capability work becomes eligible from this rejected head.
Correction execution is authorized only on the existing MIP feature branch.
Merge, PR, sibling, analytical, release, and capability authority remain false.
