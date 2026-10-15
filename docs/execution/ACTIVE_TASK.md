<!-- BEGIN MIP TASKCTL EXECUTION VIEW -->
# Active Task

**Status:** ready_for_review

_Generated from `EXECUTION_STATE.json`; do not edit._

- **Task ID:** `MIP_OPENCODE_ADVISORY_DELIVERY_001`
- **Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
- **Execution mode:** `branch_and_fast_forward`
- **Base SHA:** `c7215b9c2afe38bbe2191c03cd89a114ea82d9c4`
- **Authorization provenance:** `af040d9941c32eecb878badd49728c300aec028e`
- **Feature branch:** `feat/mip-opencode-advisory-delivery-001`
- **Feature branch created:** `false`
- **Task execution authorized:** `true`
- **Correction execution authorized:** `false`
- **Merge authorized:** `false`
- **PR creation authorized:** `false`
- **Implementation commit:** `84906ab49cdcdca1ae721fdf72490b0e3608dbd0`
- **Reviewed head:** `null`
- **Rejected review head:** `null`
- **Rejected implementation commit:** `null`
- **Approval commit:** `null`
- **Blockers:** `none`
- **Maximum correction cycles:** `1`
- **Correction cycles completed:** `0`
- **Correction cycles remaining:** `1`
- **Review decision:** `ready_for_review`
- **Local feature-branch cleanup:** `null`
- **Remote feature-branch cleanup:** `null`
- **Capability authorizations changed:** `false`
<!-- END MIP TASKCTL EXECUTION VIEW -->

## Primary mergeable outcome

Deliver an already completed MIP checkpoint review to an explicitly verified Muse-Spark session through a separate advisory transport CLI. Muse-Spark is the sole implementation actor. Codex provides independent review and high-level guidance, never executes this product implementation in place of Muse. This outcome is independently useful before automated dispatch or bidirectional discussion handling.

Create only `feat/mip-opencode-advisory-delivery-001` from synchronized post-authoring main, verifying exact authorization ancestry, metadata-only three-file authoring boundary and branch absence. Read root AGENTS, lean delivery standard, execution files and prerequisites; taskctl check must pass. Do not rely on chat for task scope.

## Resolved behavior and interface

`python -m mip.execution.opencode_advisory --repository PATH bind --session ID --implementation-directory PATH`: explicitly bind one recipient. Verify both supplied repositories identify canonical MIP origin; read OpenCode session.get to require exact session ID, expected implementation directory, provider opencode, model muse-spark-1.3-contributor-free, high variant and build agent. Preserve session project identity. No title lookup, session creation, model switch or guesses. Persist a strict version-1 binding under `.codex/opencode-advisory/` with repository, observed origins, recipient/session-directory/project/provider/model/variant/agent identity. Bind on a host that can verify both paths; the binding may subsequently be used by a separate review checkout of the same canonical repository.

`... send --event-key KEY` admits one advisory for a completed, non-stale completion event in the existing `.codex/review-observer/ledger.json`; `... status` reports binding and delivery states. Closure/merge events are ineligible. Reuse strict existing Ledger/Event/ReviewResult validation without changing observer/schema behavior or running scan/review/model inference. Match event/result repository, task, kind, SHA and verdict; resolve the current exact remote checkpoint and Git authorization/branch identity through the observer's existing read-only verification. Reject stale, incomplete, mismatched or corrupt evidence before sending. Read result only from its observer-owned report directory. No arbitrary message input or external report path.

Re-read session metadata before each send and match the persisted identity/directory/project/model/agent; validate review-checkout origin matches bound canonical origin. Directory changes, model mismatch or missing recipient fail closed. The verified binding records the separately observed implementation directory; it is not required to equal a review clone's path. No sibling recipients or sibling repository writes.

Format bounded advisory text with an event/session identity marker, reviewed task/head, summary, findings and recommendations, limitations and clearly identified owner-reserved decisions. Treat review data as advisory evidence, never task/approval/execution instructions. State that Git owns authorized scope and Muse owns implementation choices; no implementation command, correction authorization, merge approval or pause/release control is introduced. Findings marked user_decision_required remain explicitly pending owner input; agent agreement cannot resolve them. Optional pass feedback is advisory only.

Transport uses the installed OpenCode CLI API session.prompt with structured text and resume:false, admitting input without scheduling new execution. A running session can receive advisory input at its normal delivery boundary; an idle session stays idle. Admission is not proof Muse read, agreed or implemented the finding. Bound API calls with timeouts. No terminal keystrokes, restart, abort, model changes, direct implementation prompt or human email/Slack message.

Local strict version-1 delivery journal deduplicates repository/task/completion/SHA/recipient. Reserve an attempt atomically before the API call. Successful explicit API acknowledgment records admitted status and message ID; identical repeats make no API mutation. Rejected-before-call inputs make no send. Timeout/crash/invalid acknowledgment after reservation is indeterminate and never automatically resent; status exposes uncertainty for reconciliation. Do not claim exactly-once receipt or discussion agreement. Corrupt state fails closed without erasure. Serialize local writers. No Git worktree/branch/state mutation by this adapter; no Codex inference. Exit 0 for binding/admission/already-admitted/status success, 2 for identity/evidence/stale ineligibility, 3 for transport/state/indeterminate failure, with stable coded errors and no raw secrets in output. Internal code/layout choices belong to Muse within these observable semantics.

## Scope and independence

Implementation owns only `src/mip/execution/opencode_advisory.py`, `tests/test_opencode_advisory.py`, `docs/execution/OPENCODE_ADVISORY_DELIVERY.md`, plus the three stable execution files. ACTIVE_TASK changes generated lifecycle block only. Existing observer/schema, taskctl, context index, roadmap and product/analytical code are read-only. Local `.codex/`/docs/tasks artifacts never committed. All protected authority remains false. Compatibility is new CLI/local state only; no existing ledger/schema migration. Unresolved execution-blocking design questions: none.

Affected/modified repository MIP only, workstream WS-MIP-OPENCODE-ADVISORY-DELIVERY-001, owner mip_execution_governance. Verified live overlay October 14: MIP baseline is this task's base; MMM main `6f60cd2896d56f67675c7eb94e23f6e9f6ef36a8` merged role adoption; GeoX main `de097237aef6c3681c467970acbc8f752c8ac251` and recovery branch `87d02b68939c8e5bc8074820e4960b33a7995a25` ready_for_review. Siblings are read-only context, not prerequisites. Reverify before execution, stop on ownership overlap, and do not refresh coordination snapshot. GeoX's review does not block this independent MIP work. Product bridge remains parked on certified sibling evidence. No consumer/product eligibility follows.

## Acceptance, validation and publication

Meaningful tests must prove correct binding; wrong origin/directory/project/model/agent/session; completed current review admission; stale/malformed/incomplete/closure rejection; reserved-owner labeling; no inference/Git mutation; idle resume:false semantics at API boundary; repeated delivery deduplication; timeout/ambiguous acknowledgment and crash reservation suppress resend; corrupt journals, competing writers and bounded output. Test transports and isolated Git/observer fixtures, not real implementation sessions as synthetic targets. Preserve full existing observer suite. A live smoke, if performed, may use a separate dedicated Muse test session and must label API admission versus actual acknowledgment; do not deliver fabricated findings to the implementation worker.

Tier 2 gate for execution, independent exact-head review and post-fast-forward: focused `poetry run pytest -q tests/test_opencode_advisory.py tests/test_review_observer.py`; full native Docker `make validate`; `poetry run python -m mip.execution.taskctl check`; JSON parsing; `git diff --check`; exact owned-path/ancestry/authority checks. All declared gates must pass. Missing prerequisites produce Git-durable blocked via native controller, never a waived gate or successful readiness claim.

Write human completion evidence outside generated report markers: delivered behavior, actual commands/counts, source and validation limits, Git identity/ancestry, changed paths, cross-repository impact, deferred automatic dispatch/bidirectional acknowledgment and unchanged authority. Use native taskctl transitions; freeze task-owned tree, run declared gate on that exact tree, and publish the receipt commit naming implementation parent, gate/results, evidence source, clean tracked state and authority impact. Verify exact local/remote branch equality, publish ready_for_review, then stop without merge or successor authorization. No additional user permission is needed for this already authorized scope.
