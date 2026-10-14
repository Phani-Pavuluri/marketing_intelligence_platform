# Active Task

<!-- BEGIN MIP TASKCTL EXECUTION VIEW -->
# Active Task

**Status:** authorized

_Generated from `EXECUTION_STATE.json`; do not edit._

- **Task ID:** `MIP_DELEGATED_ROUTINE_MERGE_POLICY_001`
- **Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
- **Execution mode:** `branch_and_fast_forward`
- **Base SHA:** `d8b100c9fa87e3af7b5a2af565a31b442ff7b46b`
- **Authorization provenance:** `fc5d4ce487c12e4f90017b787674facb5863563c`
- **Feature branch:** `docs/mip-delegated-routine-merge-policy-001`
- **Feature branch created:** `true`
- **Task execution authorized:** `true`
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
- **Review decision:** `authorized`
- **Local feature-branch cleanup:** `null`
- **Remote feature-branch cleanup:** `null`
- **Capability authorizations changed:** `false`
<!-- END MIP TASKCTL EXECUTION VIEW -->

## MIP_DELEGATED_ROUTINE_MERGE_POLICY_001 — authorized task contract

User authorization: the user explicitly confirmed delegation of routine merge
approval on 2026-10-14. This is a MIP-owned approval-policy decision, not product
implementation or authority for MMM/GeoX changes.

## Primary mergeable outcome

Define one documentation-only policy for delegated routine merge approval and
make AGENTS.md and TASK_EXECUTION_STANDARD.md consistently reference it.
This policy is independently reviewable before building any coordinator or
merge-verification tooling. Do not implement either tool in this task.

## Exact observable behavior and resolved decisions

Future MIP tasks default to user exact-head approval. Delegation is opt-in only
when a Git-authored authorized task explicitly declares delegated_routine,
resolves acceptance evidence, and stays within already authorized goals and
architecture. Tier 3 work and authority changes are not routine. Delegation
requires independent exact-head review, no unresolved material findings, the
full applicable validation gate, unchanged authorization baseline, and durable
review evidence external to the reviewed implementation tree. It cannot be
based on a completion report's claims or on agent agreement alone.

Roadmap, capability, goal, scope, architecture, governance/approval, security,
real-data, production, analytical-truth, cross-repository contract/ownership,
and unresolved substantive disagreement decisions remain user-reserved.
Unclear eligibility fails closed to user review. A policy cannot approve its
own adoption or future changes to itself. This task uses user_exact_head.

Define a review receipt with repository, task ID, branch, authorization SHA,
implementation and exact reviewed head SHAs, reviewer identity independent of
implementation, decision, validation evidence, eligibility/authority findings,
limitations and issuance time. A later automation task must define and validate
its persistence/transport. Until that task is merged and adopted, delegated
merges remain unavailable. This policy does not grant blanket automatic merging.

Preserve fast-forward-only merging, frozen tree receipts, re-fetch/head checks,
pre-merge/post-fast-forward gates, branch cleanup, taskctl transitions and one
closure commit. Persisted merge_authorized remains false and taskctl v2 schemas
and code do not change. Record user delegation provenance and exact reviewer
receipt in future delegated closures. No capability authority follows.

Codex provides high-level guidance, independent review, productive evidence-based
discussion, and plain-language owner updates. Muse-Spark owns implementation
approach and execution. Do not prescribe its exact implementation prompts,
write its product code, enforce automatic pause/release gates, or restart it.

## Owned paths and prohibited scope

Owned implementation paths: AGENTS.md;
docs/execution/TASK_EXECUTION_STANDARD.md;
docs/execution/DELEGATED_ROUTINE_MERGE_POLICY.md.
The three stable execution files are owned only for lifecycle/evidence updates.
No src/tests/schema changes, coordinator code, sibling changes, roadmap or
capability updates, runtime/product changes, PR, merge, or automatic service
installation. No review branch or review receipt is implemented in this task.

## Risk and named acceptance evidence

Tier 3 approval-authority documentation. Gate: taskctl check; JSON parsing;
existing tests/governance/test_repo_native_execution_handoff.py; Docker-backed
make validate (pytest, Ruff, mypy); diff check; relative-link check; changed-path
boundary and exact remote publication head verification.

Review deterministic eligibility examples: opt-in routine Tier 1/2 work can
qualify only after independent review and validation; missing mode, Tier 3,
major decisions, failed tests, changed head, stale authorization, or missing
independent evidence cannot qualify. Verify default behavior, independence,
user-reserved decisions, activation prerequisite, taskctl compatibility,
non-prescriptive collaboration, and owner reporting in the written policy.

Compatibility/migration: not_applicable; documentation only, existing taskctl
v2 retained. Unresolved execution-blocking design questions: none.

## Deferred successors and stop

Deferred: review observer; independently durable receipt/verifier; OpenCode
advisory discussions and owner reporting; delegated merge executor activation;
sibling adoption. Publish ready_for_review with a frozen-tree validated receipt
and stop without merging. Exact-head user approval remains required for this
approval-authority task.
