<!-- BEGIN MIP TASKCTL EXECUTION VIEW -->
# Active Task

**Status:** proposed

_Generated from `EXECUTION_STATE.json`; do not edit._

- **Task ID:** `MIP_CORRECTION_PUBLICATION_ACCOUNTING_REPAIR_001`
- **Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
- **Execution mode:** `branch_and_fast_forward`
- **Base SHA:** `a5ac85980131e29a947c6040f96b76a9c0112056`
- **Authorization provenance:** `a5ac85980131e29a947c6040f96b76a9c0112056`
- **Feature branch:** `fix/mip-correction-publication-accounting-001`
- **Feature branch created:** `false`
- **Task execution authorized:** `false`
- **Correction execution authorized:** `false`
- **Merge authorized:** `false`
- **PR creation authorized:** `false`
- **Implementation commit:** `null`
- **Reviewed head:** `null`
- **Rejected review head:** `null`
- **Rejected implementation commit:** `null`
- **Approval commit:** `null`
- **Blockers:** `none`
- **Maximum correction cycles:** `1`
- **Correction cycles completed:** `0`
- **Correction cycles remaining:** `1`
- **Review decision:** `proposed`
- **Local feature-branch cleanup:** `null`
- **Remote feature-branch cleanup:** `null`
- **Capability authorizations changed:** `false`
<!-- END MIP TASKCTL EXECUTION VIEW -->

## One primary mergeable outcome and authority

Repair existing correction-publication accounting in the native state machine. A correction publication currently consumes a cycle only if its immediately prior status is changes_requested; existing allowed blocked/in_progress detours can publish the same authorized correction without consuming the declared cycle. Source-verified audit proved this in historical Git. Owner requested continuity audit, reliability fixes, continued useful development and Muse-owned milestones. This task restores already-required accounting, not a different approval policy or budget. Muse owns implementation approach and execution; Codex independently reviews. Capability owner: mip execution reliability. This one state-machine invariant and its meaningful regressions form one independently mergeable outcome; other audit remedies remain separate.

## Exact observable contract and preserved boundaries

Input/output remains the existing transition_state state mapping and existing CLI. For every already-allowed transition to ready_for_review carrying an authorized correction, the existing explicit --complete-correction confirmation is required and exactly one correction cycle is consumed, irrespective of whether the immediate source is changes_requested, blocked or in_progress. Successful correction publication clears correction-execution authorization exactly as today. Normal initial publication with no authorized correction consumes no correction and needs no new confirmation. Existing block/resume detours preserve pending correction identity/authorization and counters; neither lose nor double-count a cycle. A missing completion confirmation or exhausted budget must reject the attempted correction publication under existing error families and leave all state/views unchanged. Preserve native E_TRANSITION_CORRECTION_COUNTER and E_STATE_CORRECTION_COUNTER behavior where applicable; do not add error codes or transitions. Existing --clear-blockers requirement remains unchanged for blocked routes. The declared maximum/completed/remaining arithmetic stays valid and nonnegative.

Preserve existing TRANSITIONS graph, caller signatures, canonical schema, authority checks, task identity, public CLI flags, rejected/implementation SHA requirements, correction maximum and exhaustion limit, approval semantics and protected capability flags. No new rejected-head or implementation-head guard, new transition edge, forced restart, automatic pause/release control, approval grant, retroactive counter repair or Git-history rewrite. No product, sibling, analytical, roadmap, policy, report, fixture, golden or independent-observer change. Existing record formats and explicit completion option are reused; compatibility is restored enforcement on already-allowed correction paths, without schema/data migration. Callers resuming a correction through a detour must use the already-existing completion confirmation; initial work remains unchanged. Revert of this bounded implementation restores prior code without state migration, but does not rewrite published history.

## Ownership and named acceptance evidence

Owned implementation: src/mip/execution/state.py and tests/execution/test_taskctl.py only, plus the three stable execution files for native lifecycle and evidence. Tests must meaningfully exercise supported routes and failures, preserving every existing assertion. Required evidence covers: direct correction ready publication; changes_requested to in_progress to ready; correction blocked to in_progress to ready; any already-supported direct blocked-to-ready route with existing clear-blockers requirement; missing completion confirmation rejected on correction-carrying paths; normal initial authorized/in_progress publication and initial blocked/resumed publication uncounted; block/resume round-trips do not change counters; exhausted correction publication fails closed and leaves inputs/files unchanged. Do not invent a new graph edge merely to make a matrix case possible. Pin existing counter/error/flag invariants through actual source-level/native CLI evidence. Historical audit references a5dde7b and 14ff63f prove the bypass but must never be edited or retroactively legitimized. Read-only local audit packet ~/.codex/quota-resume/continuity-audit/COUNTER_REPAIR_TASK_PACKET.md is preparation only, not replacement task authority.

## Risk-proportionate gate, publication and deferred work

Tier2 existing package/state-machine behavior repair, full_suite_validation_required true. Mandatory for execution, exact-head independent review and pre/post-fast-forward: meaningful focused tests/execution/test_taskctl.py regressions, full native controller and tests/governance/test_repo_native_execution_handoff.py, python -m mip.execution.taskctl check, JSON parsing, git diff --check, exact ownership/authorization ancestry and unchanged protected-authority evidence, Ruff/mypy according to the repository validation setup, and complete Docker-backed make validate. No host-only substitution, skipped mandatory category, newly excluded tests or duplicate Docker containers. Record actual commands, results, tested commit and actual Git tree; full validation failures are blockers. Native authoring must pass the full controller/handoff suite before publication. Use real independent reviewer evidence, strict receipt, existing activated delegated policy and native live preflight only if eligible; otherwise preserve existing owner-reserved decision boundaries. No task grants its own merge authority.

MIP-only WS-MIP-CORRECTION-ACCOUNTING-REPAIR-001, owner mip_execution_reliability; prerequisite owner report is merged/closed at the task base. No sibling files or dependency resolutions. Deferred successors: evidence-binding/substance-admission remedies, lock instrumentation, future fixture-report resolver, certified-pair bridge, R12 and analytical/production work. These do not block this precisely defined accounting repair.

Use native taskctl lifecycle and generated views; authorized human task meaning remains immutable. Record actual Current outcome before publication. Freeze the task-owned tree, run applicable gate on that exact tree, then final receipt names implementation parent, commands/results, raw evidence source, worktree state and authority impact. Any subsequent task-owned edit requires a new validated receipt. Push and verify exact remote feature head; stop ready_for_review or Git-durable blocked on a safe authorized branch. One correction cycle. No merge, PR, rebase, force-push, policy activation or successor execution by implementation. Unresolved execution-blocking design questions: none.
