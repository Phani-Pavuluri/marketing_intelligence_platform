# Cross-Repository Coordination Protocol

**Status:** active coordination protocol; no capability authority
**Coordinator:** MIP program governance
**Last verified:** 2026-07-31

## Purpose and source precedence

MIP maintains a pinned program view for `marketing_intelligence_platform`,
`MMM`, and `panel_exp`. Each repository remains authoritative for its own
synchronized `main`, `docs/execution/EXECUTION_STATE.json`, `ACTIVE_TASK.md`,
and `LATEST_COMPLETION_REPORT.md`. The coordination view cannot override live
sibling Git state, producer truth, consumer acceptance, or authority gates.

Source precedence is synchronized repository state, then repository execution
files, then this protocol and coordination state, then active contracts and
roadmaps, then archived material, then chats. A lower-ranked source cannot
override a higher-ranked source.

## Snapshot freshness, live overlay, and orientation

Every repository entry records an observed remote-main SHA and evidence paths.
When a live remote SHA differs, the entry is **stale**: agents must read the
live sibling execution state and completion report before planning or acting.
Cached state, local branches, unmerged files, and chats are never authority.

A stale snapshot is reconciled through a **live overlay**. The overlay reads
the affected repository's current `origin/main`, execution state, active task,
and completion report without rewriting historical snapshot observations. It
records the observed source SHA, verification date, and the live condition used
to evaluate eligibility. A live merged execution state can therefore satisfy a
dependency even if an older cached ledger entry says `in_progress`; a cached
entry can never permanently block work after live Git proves the dependency is
merged. The overlay does not itself authorize work or silently mutate the
append-only history.

New or resumed cross-repository work must:

1. verify all affected remote-main SHAs and execution files;
2. inspect the coordination ledger for workstream overlap and ownership
   conflicts;
3. record dependency and blocker IDs in the active task;
4. stop on unresolved duplicate ownership or stale evidence; and
5. include the cross-repository impact contract in its completion report.

## Workstreams, dependencies, and blockers

A workstream has a unique ID, owner repository, capability area, task ID,
status, dependencies, evidence paths, observed SHA, and a live resolution
condition for each dependency. Only the declared owner may implement its
contract, adapter, or analytical responsibility. An overlap is a blocker, not
permission to duplicate work. Repository-main observation, feature-branch
review state, producer completion, consumer verification, and this
coordination-ledger state are distinct facts.

Blockers use `open`, `in_progress`,
`producer_completed_pending_consumer_verification`, `resolved`, or
`superseded`. Producer completion does not resolve a consumer blocker. A
resolved blocker must cite merged producer evidence and the declared consumer
verification; a task report alone is insufficient.

## Task lifecycle and impact contract

Task proposal, execution, review, closure, and coordination refresh follow each
repository's execution standard. A task affecting another arm must report:

- affected repositories, workstream ID, and capability owner;
- dependency/blocker IDs created, advanced, resolved, or superseded;
- merged evidence SHA and paths;
- consumer verification still required;
- newly eligible tasks and validation debt introduced or retired; and
- authority impact.

This metadata cannot assert analytical compatibility, production readiness, or
consumer acceptance without the owning repository's evidence. Coordination
never authorizes live engines, real data, persistence, optimization,
recommendations, pilot, production, or package-side agents.

## Refresh and closure

The coordinator refreshes the state only after verifying all listed remote
evidence. Completion reports preserve cross-repository impact, while the
append-only history records material changes for fresh chats. Proposed sibling
adoption tasks remain proposed until their owning repository authorizes them.
MIP may observe and sequence owner-repository work but cannot retroactively add
a dependency to, split, block, or authorize it.
