# TASK_COMPLETION_REPORT_V2

## Current decision

- **Task ID:** `MIP_INVOCATION_ONLY_CODEX_PROMPT_STANDARD_001`
- **Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
- **Feature branch:** `docs/mip-invocation-only-codex-prompt-standard-001`
- **Authorization head:** `39abc3d66a80054b2b293a73f2dbeb690eb2304b`
- **Accepted substantive implementation:** `9376284a35f6dda7d1b9a535e5cf23c565f759ad`
- **Rejected review head:** `0bb05e3a9d5024c9107b131a00d547f5587c3f86`
- **Current decision:** `changes_requested`

## Review finding

The invocation-only and resumed-feature-branch behavior is accepted. Exact head
`0bb05e3a9d5024c9107b131a00d547f5587c3f86` is rejected only because its stable
publication files contradict their `ready_for_review` status:

- the active task still contains a current `Required correction` section;
- the active task still claims correction execution is authorized;
- the completion report still narrates the prior publication defect and missing
  work as current; and
- the receipt claims Markdown consistency despite those contradictions.

The repeated failure mode is incremental editing of status fields while stale
body text survives. Another status-only patch is not acceptable.

## Durable correction

The active task now authorizes one deterministic final correction:

1. add a focused governance guard that rejects stale correction or missing-work
   prose whenever state is `ready_for_review`;
2. replace the three stable execution files completely rather than patching the
   prior narratives;
3. preserve accepted substantive implementation
   `9376284a35f6dda7d1b9a535e5cf23c565f759ad` and the canonical minimal
   invocation unchanged; and
4. run the complete Tier 1 gate and publish one exact-tree receipt.

## GitHub-observed evidence

- Live MIP `main` remains `a7b4e1d3701ff163942f0c42a8e7a91388840b51`.
- Rejected remote feature head was
  `0bb05e3a9d5024c9107b131a00d547f5587c3f86`.
- The complete task remains limited to the original six authorized paths.
- Accepted substantive implementation remains
  `9376284a35f6dda7d1b9a535e5cf23c565f759ad`.
- Live sibling checkpoints remain MMM
  `1b75d1d3c9f49d40f2b7ab71f524fbd2dc6d1421` and GeoX
  `ee9673c13e69082367c1727568946ac4c1a01015`.

## Validation required

The final frozen tree must pass:

- JSON parsing;
- task/state/report consistency, including stale-prose rejection in
  `ready_for_review` state;
- authorization and correction-boundary checks;
- complete task diff limited to the original six owned paths;
- final correction delta limited to the governance test and three stable files;
- exact preservation of the accepted substantive implementation and minimal
  invocation;
- `git diff --check`;
- `pytest -q tests/governance/test_repo_native_execution_handoff.py` with exact
  count;
- durable receipt inspection; and
- local/remote publication-head equality.

Docker, Ruff, mypy, and the full suite remain `not_required` for this Tier 1
correction unless another repository-authored gate makes them applicable.

## Authority impact

Task and final correction execution are authorized. Merge and PR creation remain
false. MMM and GeoX adoption remain separately unauthorized. The active GeoX
builder and all product, analytical, recommendation, production, and capability
authority remain unchanged.
