# TASK_COMPLETION_REPORT_V2

## Current decision

- **Task ID:** `MIP_INVOCATION_ONLY_CODEX_PROMPT_STANDARD_001`
- **Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
- **Feature branch:** `docs/mip-invocation-only-codex-prompt-standard-001`
- **Accepted implementation head:** `312d6461fceaba882729e47c60b17f88b4f565f3`
- **Rejected publication head:** `a50a8dd05b2bc856cf67cad2286d3df904ae7710`
- **Current decision:** `changes_requested`

## Review finding

The implementation behavior is accepted. Exact publication head
`a50a8dd05b2bc856cf67cad2286d3df904ae7710` is not approvable for four reasons:

1. Its receipt, task, state, and report identify
   `9376284a35f6dda7d1b9a535e5cf23c565f759ad` as the implementation, but the
   stale-review-narrative governance guard was added later at accepted
   implementation head `312d6461fceaba882729e47c60b17f88b4f565f3`.
2. `EXECUTION_STATE.json` is `ready_for_review` with correction authority false,
   while its task-authoring note still says one final correction is authorized.
3. The completion report says MMM and GeoX adoption remains separately
   authorized, conflicting with the explicit false adoption flags. MMM and GeoX
   invocation-only adoption remain unauthorized; the existing GeoX builder is a
   separate owner-authorized task and remains unchanged.
4. The report omits explicit consumer-verification status and newly eligible
   work required by the completion-report contract.

## GitHub-observed evidence

- Live MIP `main` remains `a7b4e1d3701ff163942f0c42a8e7a91388840b51`.
- Rejected remote feature head was
  `a50a8dd05b2bc856cf67cad2286d3df904ae7710`.
- The complete branch diff remains limited to the six authorized paths.
- The rejected head advanced from `312d6461...` by one commit and changed only
  the three stable execution files.
- Accepted final implementation head
  `312d6461fceaba882729e47c60b17f88b4f565f3` contains the stale-prose governance
  guard; accepted earlier substantive guidance remains at
  `9376284a35f6dda7d1b9a535e5cf23c565f759ad`.
- Live sibling checkpoints remain MMM
  `1b75d1d3c9f49d40f2b7ab71f524fbd2dc6d1421` and GeoX
  `ee9673c13e69082367c1727568946ac4c1a01015`.

## Receipt-reported local validation

The rejected receipt reports:

- JSON parsing: passed;
- Markdown/current-state consistency: passed;
- changed paths: passed;
- `git diff --check`: passed;
- focused governance test: `1 passed`;
- full suite: `not_required`;
- worktree: clean except allowed local-only paths; and
- capability authority: unchanged.

Those results support the implementation but do not cure the incorrect
implementation identity and contradictory authority/reporting evidence.

## Required correction

1. Replace the three stable execution files with one current
   `ready_for_review` narrative.
2. Record `312d6461fceaba882729e47c60b17f88b4f565f3` as the final implementation SHA
   in the active task, execution state, completion report, and receipt.
3. Remove stale claims that another correction remains authorized after
   publication.
4. State unambiguously that MMM and GeoX invocation-only adoption remain
   unauthorized; the existing GeoX builder remains separately owner-authorized
   and unchanged.
5. Include blockers, limitations, validation debt, sibling impact, consumer
   verification, newly eligible work, authority impact, and exact review
   readiness.
6. Run the complete Tier 1 gate on the frozen corrected tree, publish one new
   exact-tree receipt, verify remote equality, and stop without PR or merge.

## Authority impact

Task and this bounded publication correction remain authorized. Merge and PR
creation remain false. MMM and GeoX invocation-only adoption remain unauthorized.
The existing GeoX builder and all product, analytical, recommendation,
production, and capability authority remain unchanged.
