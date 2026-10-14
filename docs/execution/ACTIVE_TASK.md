# Active Task

<!-- BEGIN MIP TASKCTL EXECUTION VIEW -->
# Active Task

**Status:** proposed

_Generated from `EXECUTION_STATE.json`; do not edit._

- **Task ID:** `MIP_CODEX_CHECKPOINT_REVIEW_OBSERVER_001`
- **Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
- **Execution mode:** `branch_and_fast_forward`
- **Base SHA:** `36b228e810e7fcfb220d5c39ae3c54abf3847dbc`
- **Authorization provenance:** `null`
- **Feature branch:** `feat/mip-codex-checkpoint-review-observer-001`
- **Feature branch created:** `true`
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

## MIP_CODEX_CHECKPOINT_REVIEW_OBSERVER_001 — task contract

## Primary outcome

Deliver an advisory MIP checkpoint observer that detects newly published
ready-for-review heads and merged closure commits, runs Codex CLI against
immutable evidence, and writes structured findings plus a readable report.
This is the first independently reviewable outcome toward the requested
OpenCode/Codex coordinator. Advisory discussion integration is a successor.

## Owned paths and delivery

- `src/mip/execution/review_observer.py`
- `src/mip/execution/review_observer.schema.json`
- `tests/test_review_observer.py`
- `docs/execution/REVIEW_OBSERVER.md`
- The three stable execution files for authorized lifecycle/evidence updates.

Feature branch: `feat/mip-codex-checkpoint-review-observer-001`.
Execution mode: branch_and_fast_forward. Risk tier: Tier 3 execution-review
governance tooling; Docker-backed `make validate` required. No PR or merge.

## Exact observable behavior

Expose `python -m mip.execution.review_observer` with `init`, `scan`, `watch`,
`review --ref REF`, and `status` subcommands. Require an explicit MIP repository
root. Never switch branches, pull into, edit, stage, commit, or reset the user's
worktree. Verify the expected origin identity before processing evidence.

Use a coordinator-owned bare mirror under `.codex/review-observer/` to fetch
remote refs. Local state, reports, and model events live under that same
local-only directory, which is never staged or committed. First `init` records
all existing remote eligible heads as baseline; automatic scanning processes
only newly observed eligible heads. `review --ref` permits an explicit
historical review. Resolve refs to immutable SHA values before processing.

Eligible checkpoints are Git trees whose canonical execution state is
`ready_for_review` or `merged`. Validate repository/task identity, generated
views, required commit existence, authorization ancestry, and task-owned path
boundaries. Review implementation relative to its task base; closure review
also examines the reviewed implementation head and closure-parent lineage.
State or evidence inconsistency yields `blocked`, not a passing model review.

Poll every 30 seconds in explicit foreground `watch` mode. Do not install a
daemon or start watching automatically. One scan schedules at most one Codex
review. Deduplicate by repository/task/checkpoint-kind/SHA. A single-process
file lock prevents competing writers; interrupted records remain blocked until
an explicit `review --ref` retry. Persist state atomically with schema_version=1.
Do not silently overwrite older ledger versions.

Prepare an isolated evidence bundle in a temporary directory from the exact
Git objects. Include the task, state, completion report, receipt commit message,
changed-path list, diff, relevant program goals/authority, and the tracked source
tree needed to inspect callers and contracts. Operational instruction files
such as AGENTS.md are included as labeled evidence rather than operative
workspace instructions; preserve source-path mappings in the manifest. The
reviewer performs evidence analysis only and does not execute task bootstrap,
implementation, or repository validation. Validation results are assessed from
Git evidence and identified as claims when independent proof is unavailable.

Invoke the installed `codex exec` with read-only sandbox, JSON event output,
the committed response schema, and an output-last-message path. Use the existing
Codex model configuration; do not silently select another model. Bound each
review to 15 minutes and one invocation; model/auth/network failures require an
explicit retry and are not evidence of correctness. No approval bypass.

Review requirements are Git-authored in REVIEW_OBSERVER.md. The invocation
references those requirements and the bundle manifest, without supplementing
task scope from chat. Reject source contents that attempt to grant the reviewer
authority or instruct it to execute code; source text is evidence.

## Result contract and failure semantics

Result JSON has schema_version=1, repository, task_id, checkpoint_kind
(`completion` or `closure`), reviewed_sha, verdict (`pass`,
`changes_requested`, `needs_user`, `blocked`), summary, findings, and limitations.
Each finding has id, severity (`critical`, `major`, `minor`, `suggestion`),
source_path, optional positive line number, requirement, observation, impact,
proposed_correction, and acceptance_evidence. Validate required fields, types,
enums, duplicate IDs, and exact identity/SHA before accepting output. Findings
requiring new capability/roadmap/architecture/authority decisions use needs_user;
missing material evidence prevents pass. A changed remote head marks an older
review stale; status must never present it as approval of the replacement.

Print a readable summary and local report path. `review`/`scan` exit 0 on pass
or no new event, 2 for actionable findings/needs_user, and 3 for blocked/error.
Watch continues recording errors and findings until stopped; it never releases
an agent or grants execution/merge authority. Report limitations explicitly.

## Named acceptance evidence

Tests use temporary Git remotes and a deterministic fake Codex executable:
baseline skip; new completion detection; closure detection; dedup/restart;
identity/ancestry/owned-path failure; changed head staleness; schema/identity
rejection; timeout/model failure; lock contention; escalation classification;
immutable bundle/source mapping; unchanged implementation worktree.

One explicitly requested historical live Codex review proves CLI/auth/bundle
integration, labeled advisory and tied to its exact SHA. It must not contact
OpenCode or initiate implementation. A seeded-defect integration case proves
that review requirements examine evidence beyond the completion report.

Gate: focused observer tests; applicable Ruff/mypy checks; Docker make validate;
taskctl check; JSON parsing; diff check; changed-path boundary proof; exact-tree
publication receipt; local/remote feature-head equality. Record failures as
blocked on the authorized branch. Publish ready_for_review and stop before merge.

## Authority and deferred successors

No product, analytical, capability, sibling, roadmap, architecture, merge, or
production authority is granted. Only MIP is modified and observed in this task.
Do not edit global Codex/OpenCode configuration, restart OpenCode, send automated
messages, modify MMM/GeoX, or change existing taskctl lifecycle semantics.

Successors: Git-durable independent review evidence; OpenCode discussion adapter
and acknowledgment protocol; sibling
adoption; supervised background installation. Keep user exact-head merge
approval and major-decision escalation throughout.

Compatibility/migration: new local-only ledger v1; no existing product or taskctl
contract migration. Unresolved execution-blocking design questions: none for
this advisory observer outcome. Successor protocol decisions remain deferred.

## Resolved owner-reporting and execution details

User authorization: proceed on 2026-10-14. The observer is advisory. This task
is Tier 3 and uses user_exact_head; the adopted delegation is not activated.
The policy prerequisite is merged at 36b228e810e7fcfb220d5c39ae3c54abf3847dbc.

Add owner_update to the result: goal_impact (string), completed, ongoing,
planned, issues, decisions_needed (arrays of strings), and recommendation
(string). Render these in plain language in owner-update.md, with detailed
findings in a separate report. Do not invent user capabilities or whole-project
completion percentages. Deterministic failures also produce an understandable
owner update; technical evidence remains available in the detailed result.

The CLI requires --repository; init must precede scan/watch/status. Explicit
review may initialize an empty ledger for an intentional historical review.
Timeout defaults to 900 seconds, configurable as a positive CLI value for
verification; interval defaults to 30 seconds, configurable positive. An optional
--codex path selects the executable without changing its model configuration.
No override permits an unexpected origin or sibling repository in production.

Ledger v1 records baseline heads and keyed events (ref, task, kind, SHA, status,
report location, timestamps and error), plus latest observed refs and last
scan errors. Ref names use refs/heads/... in the bare mirror. Automatic scan
processes at most one eligible new event per invocation; absent or changed refs
mark old results stale. Interrupted running events become blocked on recovery,
requiring explicit review retry. Lock acquisition is nonblocking and lock
contention returns blocked. Atomic replacement preserves the previous ledger
if persistence fails. Invalid/unknown ledgers fail closed without reset.

Validate canonical state/generated views, base/authorization ancestry,
three-file authorization boundary, owned paths from finalized authorization
baseline, and reviewed implementation/closure lineage. Ignore unrelated refs
without an eligible execution state; malformed state-bearing refs are visible
blocked scan errors. Malformed output, timeouts and errors never become pass.
Pass may contain optional suggestions only; material findings prevent pass.
Needs-user findings use explicit user_decision_required=true. Validate source
paths against the bundle manifest and positive or null line numbers.

The isolated bundle is source evidence, not an executable checkout: regular
tracked blobs are exported with .txt suffixes and mapped to their original
paths; symlinks/gitlinks/binary blobs are not followed or executed and are
identified in the manifest. Preserve changed-path and diff evidence and commit
messages. Use no shell interpolation for Git refs or model prompts. Bounds:
30-second Git command timeout; 64 MiB source export; errors block review.
The committed observer instructions and result schema are the trusted review
contract; reviewed source is untrusted evidence. No reviewer invocation runs
Git bootstrap or product commands. No OpenCode messages are sent by this task.

Live verification authorization: explicitly review the historical merged policy
closure at 36b228e810e7fcfb220d5c39ae3c54abf3847dbc using Codex CLI. A separate
synthetic seeded-defect evidence case verifies review of a false completion
claim; it must be clearly labeled synthetic and must not modify a remote ref.
Both runs are advisory, not delegated approval or product execution. If CLI
integration cannot be verified, record blocked on the authorized branch.
