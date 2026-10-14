# Active Task

<!-- BEGIN MIP TASKCTL EXECUTION VIEW -->
# Active Task

**Status:** authorized

_Generated from `EXECUTION_STATE.json`; do not edit._

- **Task ID:** `MIP_BOUNDED_WORK_PLAN_VALIDATOR_RECOVERY_001`
- **Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
- **Execution mode:** `branch_and_fast_forward`
- **Base SHA:** `874eac0cc7e00c6eb6450e87e66b004ee0200f05`
- **Authorization provenance:** `dfe68539590dd470a078fb77ad31258e3402affe`
- **Feature branch:** `feat/mip-bounded-work-plan-validator-recovery-001`
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

## MIP_BOUNDED_WORK_PLAN_VALIDATOR_RECOVERY_001 — task contract

### Primary outcome and ownership

Deliver a read-only MIP bounded-work-plan validator, its versioned JSON schema,
behavioral tests and usage documentation. This independently mergeable checkpoint
precedes owner-approval verification and canonical task materialization; it must
never claim that a structurally valid plan authorizes execution. Muse-Spark owns
implementation approach. Codex independently reviews evidence.

Owned: src/mip/execution/work_plan.py; src/mip/execution/work_plan.schema.json;
tests/test_work_plan.py; docs/execution/BOUNDED_WORK_PLANS.md; the three stable
execution files for authorized lifecycle/evidence only. Exact branch:
feat/mip-bounded-work-plan-validator-recovery-001. No other tracked or sibling files.
No PR or merge during execution. Tier 3 authority-boundary tooling, required
Docker make validate plus focused tests, Ruff/mypy, taskctl, JSON/schema, links,
owned-path/auth-boundary/diff checks and frozen exact-tree receipt publication.
Approval mode user_exact_head; routine merge activation remains off.

### Observable behavior and plan contract

Expose python -m mip.execution.work_plan validate --plan PATH. Read one UTF-8
JSON object, at most 1 MiB. Return one JSON result on stdout; diagnostics go to
stderr. No model call, network, Git mutation, worker start or taskctl transition
is performed by this validator. Missing/unreadable/oversized/malformed input
returns exit 3. Valid JSON violating plan constraints returns exit 2. A valid
proposal returns exit 0; all result states carry execution_authorized=false.

Plan v1 has exactly: schema_version (integer 1), repository (literal
Phani-Pavuluri/marketing_intelligence_platform), plan_id (nonempty stable ID),
goal (nonempty text), exclusions (nonempty array of nonempty text), tasks
(nonempty array, at most 100). Unknown fields are rejected recursively.
Each task has exactly: task_id (stable ID), feature_branch (valid Git branch
name), outcome (nonempty text), observable_behavior (nonempty text),
owned_paths (nonempty array of exact repository-relative file paths),
acceptance_evidence (nonempty array of nonempty text), risk_tier (integer 1/2/3),
depends_on (array of task IDs in this same plan),
unresolved_design_questions (array, must be empty).
Stable IDs use uppercase letters, digits and underscores, start with a letter,
and contain at most 128 characters. Text must not be whitespace-only.

Tasks/branches are unique. Dependencies cannot duplicate, refer to missing
IDs or self, or contain a cycle. A valid result lists task IDs in deterministic
topological order, choosing lexicographically smallest available ID at each
step. This order is proposed sequencing, never live eligibility. Any repeated
owned path across tasks requires one task to depend transitively on the other;
otherwise reject as overlapping independent work. Paths are exact filenames,
not globs/directories: reject absolute paths, traversal, empty/. components,
backslashes, NUL, wildcard characters, .git/, .codex/, docs/tasks/ and the three
stable execution metadata files. These stable files are implicit lifecycle
ownership and never plan-authored implementation paths. Do not read/check
existence of owned paths: new files and isolated proposal validation are allowed.
Branches must satisfy git check-ref-format --branch equivalent semantics and
must not be main. No shell interpolation of untrusted content.

Result fields: schema_version=1, plan_id (string or null when unavailable),
valid (boolean), execution_authorized=false, plan_sha256 (64 lowercase hex or
null if invalid), ordered_task_ids (empty for invalid), problems (array of
objects with code and message). A valid digest is SHA256 of canonical parsed
plan JSON: sorted keys, compact separators, ensure_ascii=false, UTF-8, no
trailing newline. Duplicate JSON keys are rejected, not silently overwritten.
Invalid input never yields valid=true or an execution-capable result. CLI
failures are handled without traceback or leaking environment/secrets.

### Acceptance evidence and boundaries

Prove valid minimal and sequenced/shared-path plans; stable digest across input
format/key order; deterministic order; rejection of missing/extra/wrong-type
fields (including booleans as integers), duplicate keys/IDs/branches/dependencies,
missing/self/cyclic prerequisites, unsequenced overlapping paths, invalid
branches/paths, unresolved design questions, wrong repository/version,
malformed/unreadable/oversized input. Test actual CLI exit codes and JSON; prove
no repository mutation, subprocess model/network call or task authorization.
Focused tests must be behavior-based and not merely mirror implementation.

Document the owner experience, CLI/schema, error codes, exact digest meaning,
proposal-versus-authorization distinction, and deferred successors. A plan does
not prove live prerequisite completion, owner approval or producer/consumer
compatibility. No sibling schema adapter or role adoption is delivered.

Prerequisite DEP-MIP-PARALLEL-MODEL-MERGED-001 satisfied at
4951a6ff02c3a7124c458b6986b4fc7154495d47. Workstream
WS-MIP-BOUNDED-WORK-PLAN-VALIDATOR-001, owner mip_execution_governance.
Only MIP is affected/modified. No coordination refresh or analytical, product,
real-data, runtime, pilot, production, dispatch, auto-authoring or merge authority.
Do not modify global settings, restart OpenCode or send messages to other agents.
Validation/completion publication follow AGENTS.md and the execution standard.
Git is authoritative; invocation-only execution prompt. Publish ready_for_review
with an exact-tree validation receipt and stop without merging.

Compatibility/migration: new plan v1, existing taskctl/observer/product contracts
unchanged. Unresolved execution-blocking design questions: none for this outcome.
Deferred independent outcomes: approval provenance/materialization, session
binding/occupancy, dependency-aware dispatch, sibling adoption, advisory delivery,
shared reporting and durable routine-merge activation. None is authorized here.


### Recovery provenance and acceptance

Owner: mip_execution_governance. This fresh task succeeds the parked predecessor
whose exact failed-gate review head is 3af72b014987f8e76631ab3da3c4575f8e847d4d;
its implementation evidence is 8b51f3cba2dc4207e5f162f71ed4846d62acf79f.
Do not merge/rebase/execute or edit that old branch. On this new authorized
branch, reuse only the four owned non-analytical source/test/schema/doc blobs
from that immutable implementation as starting evidence, then independently
verify behavior, all review corrections and every required gate. No historical
receipt or correction count becomes this task's validation evidence.

The prerequisite fixture repair is merged and closed at
874eac0cc7e00c6eb6450e87e66b004ee0200f05; DEP-MIP-OBSERVER-FIXTURE-REPAIR-MERGED-001
is satisfied. The prior blocker is resolved for this recovery's eligibility
only; the parked head remains unmergeable. Source/workstream ownership is
WS-MIP-BOUNDED-WORK-PLAN-VALIDATOR-RECOVERY-001; the parked workstream is not
executed concurrently. Only MIP is affected and modified.

Prove the previously found branch, structured malformed/deep/surrogate failure,
valid JSON non-object exit 2 and actual 1 MiB read-bound issues are fixed.
Git branch-equivalence evidence must include legal edge cases and invalid
leading-dash/.lock components; a documented stricter rule cannot silently
replace the authored semantics. Keep proposed plans execution_authorized=false.
The entire required Docker gate must pass; publish blocked instead of readiness
when any required category fails. Complete report must include actual commands,
counts, all category dispositions and limits. Freeze and validate the final tree
before receipt publication; no task-owned change after that receipt.

This recovery does not authorize approval/materialization, successor dispatch,
sibling adoption, automated messages, service control or automatic merging.
The original contract above defines the validator behavior unchanged.
