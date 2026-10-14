# Active Task

<!-- BEGIN MIP TASKCTL EXECUTION VIEW -->
# Active Task

**Status:** ready_for_review

_Generated from `EXECUTION_STATE.json`; do not edit._

- **Task ID:** `MIP_PARALLEL_AGENT_OPERATING_MODEL_001`
- **Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
- **Execution mode:** `branch_and_fast_forward`
- **Base SHA:** `cf0ac9feafc65c3f35266b550cf33f5a4183203a`
- **Authorization provenance:** `c5e05b873cf294f6694aea1e9c4636d353737f47`
- **Feature branch:** `docs/mip-parallel-agent-operating-model-001`
- **Feature branch created:** `true`
- **Task execution authorized:** `true`
- **Correction execution authorized:** `false`
- **Merge authorized:** `false`
- **PR creation authorized:** `false`
- **Implementation commit:** `2ae04be63c1dff4a29c7e1d6d1545f7a78a2ba8a`
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

## MIP_PARALLEL_AGENT_OPERATING_MODEL_001 — task contract

Primary mergeable outcome: document the owner-approved parallel-agent operating
model in docs/program/PARALLEL_AGENT_OPERATING_MODEL.md. This is one architecture
and authority-guidance artifact; runtime implementation is independently
mergeable and deferred. Codex authors coordination guidance only, not product
implementation.

Owned implementation path: docs/program/PARALLEL_AGENT_OPERATING_MODEL.md.
The three stable execution files are owned for lifecycle and evidence only.
Feature branch: docs/mip-parallel-agent-operating-model-001.
Risk: Tier 3 architecture/cross-repository authority guidance. Required gate:
Docker-backed make validate, taskctl check, JSON parse, relative-link check,
acceptance matrix, owned-path and authoring-boundary checks, git diff --check,
exact-tree publication receipt and local/remote feature-head equality.
Merge approval mode: user_exact_head. No PR or merge during execution.

Exact document meaning: one persistent Muse-Spark implementation worker per
repository, independent Codex review jobs may run concurrently, one writer per
repository, Git-authorized tasks only, dependency/ownership verification before
dispatch, exact-head advisory discussions without automatic abort or release
controls, owner-reserved major decisions, plain owner reporting. Record the
bounded-plan mechanism as approved direction but not operational authority:
a separately definition-ready governance implementation must adopt its format,
validation and canonical materialization before automatic task authorization.
Current explicit task authorization and merge policy remain operative.

Record source precedence, verified live MIP/MMM/GeoX observations with date,
existing GeoX checkpoint occupancy, model limitations and separate successor
outcomes. Do not cache mutable feature state in shared coordination snapshots.
No producer/consumer dependency is resolved by this documentation outcome.

Acceptance evidence: a completion matrix maps each requirement above to a
section in the document; live sibling remote main and GeoX feature heads match
recorded observations; inspect their canonical state and completion evidence;
no overlap with existing sibling workstreams; all document relative links
resolve; owned-path diff and authoring boundary are exact; full required gate
passes on frozen publication tree. Missing evidence blocks publication.

Affected repositories: MIP, MMM, GeoX; only MIP is modified. Workstream:
WS-MIP-PARALLEL-AGENT-OPERATING-MODEL-001; capability owner:
mip_execution_governance. Dependency DEP-MIP-REVIEW-OBSERVER-MERGED-001 is
satisfied at cf0ac9feafc65c3f35266b550cf33f5a4183203a. Sibling observations
are context, not prerequisite completion or authority. No blocker is created,
advanced or resolved; no sibling task is split or reauthorized.

Prohibited: sibling writes, coordination snapshot refresh, product/code changes,
starting implementation workers, OpenCode service restart, automatic messages,
automatic task authorization, merge activation or analytical/production changes.
No global configuration edits. Compatibility/migration: not_applicable.
Unresolved execution-blocking design questions: none for the document outcome.

Deferred successors: bounded-plan validation/materialization; owner-repository
role adoption; exclusive session binding; dependency-aware dispatch; sibling
review/advisory delivery; shared reporting; durable merge receipts/activation.
Each requires its own definition-ready owner-repository authorization.
