# Parallel Agent Operating Model

Status: owner-approved design, pending this task's exact-head merge.
Owner: MIP program owner. Owner decision: approval by “proceed” on October 14,
2026, following review of the parallel-workstream proposal.
Workstream: WS-MIP-PARALLEL-AGENT-OPERATING-MODEL-001.

## Roles and owner experience

One coordinating conversation and one plain-language project update cover MIP,
MMM and GeoX. Muse-Spark owns implementation approach and execution within
Git-authorized tasks. Codex guides alignment with agreed goals, independently
reviews evidence and discusses findings and recommendations. Codex does not
prescribe detailed execution prompts or take over product implementation.

The owner decides goals, conceptual direction, roadmap, capabilities outside
agreed scope, material architecture, authority, and unresolved substantive
agent disagreements. Agent agreement never expands authority. Explain choices
with options, a recommendation, goal impact and tradeoffs.

Owner reports describe completed, ongoing, planned and waiting work; outcomes
that matter; issues and their disposition; and decisions needed. Distinguish
verified results, agent claims and proposals. Link technical evidence without
requiring the owner to read completion reports. Never invent percentages or
claim monitoring is active before service verification.

## Workers and independent reviews

Use one persistent Muse-Spark implementation session for each repository,
with at most three concurrent implementation workers across MIP, MMM and GeoX.
Reuse verified sessions instead of creating duplicates. Each repository has one
writer on its authorized task branch and a separate checked-out worktree.
Independent Codex review jobs may run concurrently in isolated read-only
snapshots. Additional research/review helpers may not write the implementation
worktree. Multiple concurrent implementation tasks in one repository are deferred
because its current canonical execution state represents one active task.

A coordinator verifies eligibility, exclusive occupancy and dependencies;
records events; routes advisory discussions; and assembles owner updates.
It does not decide new product scope. Git records task contracts, authorization,
completion and approval provenance. OpenCode API messages carry discussions;
competing edits to shared branches are not a communication mechanism. Runtime
occupancy records are operational evidence, never task or capability authority.

## Eligibility and dependency sequencing

Apply the [coordination protocol](CROSS_REPOSITORY_COORDINATION_PROTOCOL.md):
verify live repository identity, main and authorized feature ancestry, canonical
state and generated views, task ownership, prerequisites, worker/session binding
and exclusive occupancy before dispatch. The owning repository remains
responsible for task authorization and implementation. An old snapshot or a
roadmap entry is insufficient. Stop on overlapping workstream IDs or ownership.

Independent authorized tasks may run concurrently. A dependent consumer waits
for the producer's required merged evidence and required consumer acceptance.
A review-ready feature branch alone cannot satisfy a merged dependency.
Independent preparation can proceed only as its own authorized task without an
unmet prerequisite. Resolve contract meaning, ownership and dependencies before
starting dependent implementation. A changed prerequisite stops dependent
dispatch for reassessment; unaffected authorized work may continue.

On restart, reconcile Git and verify actual process/session occupancy before
dispatch. An expired reservation alone must never permit another writer.
Reconnect a verified session when safe. Shared OpenCode service restart is not
routine dispatch because it can interrupt unrelated sessions. Runtime protocol,
lease fields, recovery rules and tests require a separately definition-ready task.

## Review and productive discussion

Review the completion report, validation receipt, task acceptance evidence and
necessary source files at the exact published remote head. Bind each discussion
to repository, task and SHA; deduplicate delivery and record acknowledgment,
findings, responses and disposition. Muse-Spark chooses how to implement agreed
corrections. Do not automatically abort workers or impose pause/release controls.
A substantive unresolved finding prevents approval of that checkpoint; unrelated
authorized work may continue. Correction execution requires an available
repository-authorized cycle or an authorized successor. Escalate unresolved
substantive disagreement rather than repeating agent debate indefinitely.

## Bounded work plans and approvals

The owner-approved direction is to approve bounded work plans containing
explicit definition-ready tasks, owned paths, observable behavior, acceptance
evidence, dependencies, risk tiers and exclusions. A future verified mechanism
may dispatch already approved eligible tasks without asking at every step.
Material scope or contract-meaning changes return to the owner. Broad project
goals are never executable authorization.

This document does not implement or activate plan-based task authorization.
Current [execution rules](../execution/TASK_EXECUTION_STANDARD.md) still require
explicit task authorization. A separately authorized governance task must define
the plan format, owner approval provenance, validation, immutable task contracts,
canonical materialization, amendments and fail-closed dispatch before that
mechanism operates. This avoids silently treating planning text as authority.

Routine eligible Tier 1/2 merges may use the
[delegated policy](../execution/DELEGATED_ROUTINE_MERGE_POLICY.md) only after its
independent durable receipt/preflight prerequisite and explicit activation.
Tier 3 and major/non-routine decisions remain owner decisions. This task uses
user_exact_head and cannot approve its own merge or policy changes.

Use narrow persistent tool permissions where available. Do not introduce
unrestricted shell approval, blanket auto-approval or sandbox bypass. Tool or
operating-system approval requests may remain outside granted permissions.
Technical permission to run a command does not grant project authority.

## Live readiness evidence — October 14, 2026

| Repository | Verified remote main | Current observed condition |
|---|---|---|
| MIP | cf0ac9feafc65c3f35266b550cf33f5a4183203a, pre-authoring baseline | Advisory observer merged; no background monitor or parallel dispatch |
| MMM | d91cebc85b48ea331c527566a1591cf18887855e | Current certification task merged; no authorized successor; role split not adopted |
| GeoX | 496c317bc44c31a89aff805896863bd7eb637b7e | Existing structured-completion task occupies its workstream; no authorized successor |

MIP authorization/progress for this document is in its canonical execution
files, not the historical row above. GeoX review state was read separately from
its exact remote feature head 81664df0d687746a8ee990eada702a2a54cc23c0 on
feat/geox-structured-completion-evidence-001: ready_for_review, one correction
cycle used, none remaining. This is dated readiness evidence, not a mutable
shared coordination snapshot or correctness approval. Its structured changed-path
list may describe the correction rather than the full outcome; exact-head review
must resolve that interpretation. Do not launch a duplicate worker on that task.

Sibling read-only audits verified remote identity/head and taskctl consistency.
Canonical execution state, active tasks and completion reports were inspected.
MMM's current workstream is WS-MMM-RIDGE-GEO-TIME-NUISANCE-TRUTH-RECOVERY-001;
GeoX's is WS-GEOX-STRUCTURED-COMPLETION-EVIDENCE-001. Neither overlaps this MIP
operating-model workstream. Historical coordination pins were not refreshed.
These observations are not sibling correctness reviews, producer certification,
consumer acceptance or permission to change sibling state. Reverify at dispatch.

MIP session ses_ec4679ffaffeLeDmAoTVLSPDxr was verified as Muse-Spark.
MMM session candidate ses_f4771d8acffesi1EN188IoCcYz needs adopted binding and
occupancy verification. No GeoX implementation binding is confirmed. A session's
existence does not prove a running or authorized implementation task.

## Separate delivery outcomes and preserved boundaries

1. Adopt this operating model in MIP through exact-head review and merge.
2. Define and validate bounded-plan authorization/materialization in MIP.
3. Independently review and close GeoX's existing checkpoint under its current
   rules; adopt worker/reviewer roles through separate MMM and GeoX owner tasks.
4. Deliver verified repository/session binding and exclusive writer occupancy,
   rejecting duplicate workers, wrong identity and ambiguous restart state.
5. Deliver dependency-aware dispatch of already authorized tasks using
   invocation-only prompts; prove independent concurrency and unmet-dependency,
   stale-evidence and ownership-conflict rejection.
6. Extend observation to adopted siblings and advisory delivery; prove exact-head
   routing, deduplication and delivery recovery without aborting workers.
7. Deliver shared plain-language owner reporting and supervised monitoring.
8. Deliver independent durable merge receipts/preflight and obtain the required
   owner activation decision for routine merging.

The sequence is planning, not successor authorization. Independent prerequisites
may be developed in parallel only after their owning repositories authorize them.
Each outcome requires a definition-ready task and proportionate validation under
[lean delivery](LEAN_REPOSITORY_DELIVERY_STANDARD.md).

Only MIP documentation is changed by this task. No sibling adoption, dispatcher,
worker startup, automatic messages, global configuration change, service restart,
coordination refresh, automatic task authorization or merge activation occurs.
No product, analytical, calibration, simulation, optimization, recommendation,
real-data, pilot or production authority is added. Existing authority and freeze
boundaries remain in force. No producer/consumer blocker is resolved and no
sibling successor becomes executable solely through this document.
