# TASK_COMPLETION_REPORT_V2

## Identity

- **Task ID:** `MIP_INVOCATION_ONLY_CODEX_PROMPT_STANDARD_001`
- **Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
- **Feature branch:** `docs/mip-invocation-only-codex-prompt-standard-001`
- **Authorization head:** `39abc3d66a80054b2b293a73f2dbeb690eb2304b`
- **Rejected first review head:** `fa8ff9612732f34a4d90275da017c7125ec9cea0`
- **Rejected first implementation:** `2f1ec3efdd6f68d5c8097e534c869d982ab2d6ec`
- **Accepted behavioral implementation:** `9bb63c02e476a8a13855192b9df77d4238a3673b`
- **Rejected corrected publication head:** `c09ec85b43442f505e710625bad0e33f56b3d300`
- **Current decision:** `changes_requested`

## Review finding

The behavioral correction is accepted. `AGENTS.md` and
`TASK_EXECUTION_STANDARD.md` now define exactly the minimal execution/correction
invocation:

`Synchronize from Git and execute the active task.`

The merge invocation adds only the exact externally approved remote head SHA.
The focused governance test checks the minimal invocation and prohibits the
prior publication/push workflow text.

The corrected publication is not approvable because its stable files disagree:

- execution state says `ready_for_review` and correction authorization is false;
- the active task still says correction execution is authorized and unfinished;
- this completion report still describes correction authorization rather than
  the completed correction and current review candidate.

The exact corrected head `c09ec85b43442f505e710625bad0e33f56b3d300`
is therefore rejected only for current-state publication inconsistency.

## Required final normalization

Update only the three stable execution files so they present one current
`ready_for_review` state. Preserve behavioral implementation
`9bb63c02e476a8a13855192b9df77d4238a3673b` unchanged. Publish a new exact-tree
receipt with one final normalization implementation SHA and the complete Tier 1
gate.

## Evidence reviewed

### GitHub-observed

- MIP `main` remains `a7b4e1d3701ff163942f0c42a8e7a91388840b51`.
- The branch head reviewed was
  `c09ec85b43442f505e710625bad0e33f56b3d300`.
- The complete branch diff remains limited to the six authorized paths.
- The correction delta from review-decision head
  `bad58d7bc683dbe77ee0e2d234b18409b7c92e79` contains exactly two commits.
- Behavioral implementation `9bb63c02e476a8a13855192b9df77d4238a3673b`
  changes only `AGENTS.md`, `TASK_EXECUTION_STANDARD.md`, and the focused test.
- Publication commit `c09ec85b43442f505e710625bad0e33f56b3d300`
  changes only the three stable execution files and carries a durable receipt.

### Receipt-reported local validation

The rejected corrected receipt records JSON, Markdown consistency, changed-path,
`git diff --check`, and receipt checks as passed; the focused governance test
reported `1 passed`; Docker, Ruff, mypy, and full-suite validation were
`not_required` for the Tier 1 gate.

These results support the behavioral implementation but do not cure the stable
current-state disagreement.

## Final normalization authorization

- **Task execution authorized:** true
- **Final normalization execution authorized:** true
- **Merge authorized:** false
- **PR creation authorized:** false
- **Blockers:** none
- **Capability authority changed:** false
- **MMM/GeoX adoption:** deferred and separately unauthorized
- **GeoX active builder:** unchanged

The final normalization is limited to `ACTIVE_TASK.md`,
`EXECUTION_STATE.json`, and `LATEST_COMPLETION_REPORT.md`. Publish a consistent
new `ready_for_review` receipt or accurate `blocked` state and stop without
merge.
