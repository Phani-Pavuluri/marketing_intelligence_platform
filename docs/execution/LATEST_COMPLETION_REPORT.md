# TASK_COMPLETION_REPORT_V2

## Current decision

- **Task ID:** `MIP_INVOCATION_ONLY_CODEX_PROMPT_STANDARD_001`
- **Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
- **Feature branch:** `docs/mip-invocation-only-codex-prompt-standard-001`
- **Authorization head:** `39abc3d66a80054b2b293a73f2dbeb690eb2304b`
- **Accepted minimal-prompt implementation:** `9bb63c02e476a8a13855192b9df77d4238a3673b`
- **Current decision:** `changes_requested`

## Runtime finding

The minimal invocation was exercised against the live repository:

`Synchronize from Git and execute the active task.`

Codex synchronized `main` successfully. `main` still recorded the task as
`authorized`, while the declared remote feature branch had advanced to newer
review and correction state. Because the repository did not define which ref was
authoritative for resumed lifecycle state, Codex stopped rather than guessing.

That stop was correct under the existing fail-closed rules. However, the result
was printed only in terminal/chat output. It was not written to the feature
branch as `blocked` evidence and did not update the completion report. This
violates the repository-native zero-copy-paste goal and proves the invocation-only
contract is incomplete.

## Root cause

The current bootstrap defines synchronization of `main`, but not deterministic
resumption precedence after a feature branch exists:

- `main` contains the original authorization snapshot and feature-branch name;
- the remote feature branch contains later `changes_requested`, correction,
  blocked, or `ready_for_review` state; and
- no canonical rule states that verified branch lifecycle state supersedes stale
  main lifecycle state while main remains authoritative for authorization
  provenance.

Without that rule, the minimal prompt cannot safely execute branch-resident
corrections.

## Required correction

Add a branch-aware active-state resolution rule:

1. Synchronize and read `main` first.
2. Obtain the task ID, authorization head, and exact feature-branch name from
   Git-authored main state.
3. Fetch the declared remote feature branch.
4. Verify repository identity, task ID, branch name, and ancestry from the
   authorization head.
5. Use `main` as authority for the original authorization boundary.
6. Use the verified feature branch as authority for the latest resumed lifecycle
   status, review decision, blockers, implementation SHA, and completion report.
7. Do not stop merely because main retains the original authorized snapshot.
8. Fail closed on mismatches, ambiguous branches, invalid ancestry, or
   inconsistent branch task/state/report.
9. When the authorized branch and write target are safely established, publish
   any fail-closed outcome as Git-durable `blocked` evidence before stopping.
10. Never treat terminal or chat output as the completion report.

The canonical prompt remains unchanged:

`Synchronize from Git and execute the active task.`

## Scope and authority

The correction is limited to:

- `AGENTS.md`
- `docs/execution/TASK_EXECUTION_STANDARD.md`
- `tests/governance/test_repo_native_execution_handoff.py`
- the three stable execution files

No product, analytical, contract, coordination, MMM, GeoX, or capability
authority changes. MMM and GeoX adoption remains separately owner-authorized.

## Validation required

The final corrected publication must record:

- JSON parsing;
- current-state consistency;
- authorization and correction boundaries;
- six-path task scope;
- three-path substantive implementation and three-path publication scope;
- exact preservation of the minimal invocation;
- focused governance test result and exact count;
- `git diff --check`;
- durable receipt inspection;
- GitHub-observed versus locally observed evidence; and
- local/remote publication-head equality.

Docker, Ruff, mypy, and the full suite remain `not_required` for this Tier 1
correction unless another repository-authored gate makes them applicable.
