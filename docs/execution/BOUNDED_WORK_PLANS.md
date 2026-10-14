# Bounded Work Plans

**Status:** usage documentation for the read-only plan validator
**Owner:** MIP execution governance
**Applies to:** plan schema v1, `python -m mip.execution.work_plan`

## Proposal versus authorization

A bounded work plan is a proposal only. It describes goals, tasks, owned
paths, and sequencing so an owner can review them. A structurally valid plan
never authorizes execution: every validator result carries
`execution_authorized=false`, and materialization, dispatch, merge activation,
or any sibling change requires a separate Git-authorized task. The validator
itself performs no model call, network access, Git mutation, worker start, or
taskctl transition.

## Owner experience

1. Draft a plan JSON object following the contract below.
2. Run `python -m mip.execution.work_plan validate --plan PATH`.
3. Read the single JSON result on stdout. `valid=true` means the proposal is
   well-formed and sequenced; it does not mean prerequisites are complete,
   producers and consumers are compatible, or the owner has approved anything.
4. Fix reported `problems` (each names a `code` and a human message) and repeat.
5. Submit the valid plan through the separately authorized approval path.
   Deferred successors — approval provenance/materialization, session
   binding/occupancy, dependency-aware dispatch, sibling adoption, advisory
   delivery, shared reporting, and durable routine-merge activation — are not
   part of this checkpoint.

## CLI and result contract

```text
python -m mip.execution.work_plan validate --plan PATH
```

The input must be one UTF-8 JSON object of at most 1 MiB. The result object is:

```text
schema_version: 1
plan_id: string or null when unavailable
valid: boolean
execution_authorized: always false
plan_sha256: 64 lowercase hex when valid, else null
ordered_task_ids: deterministic topological order, empty when invalid
problems: array of {code, message}
```

Exit codes: `0` valid proposal; `2` well-formed JSON that violates plan
constraints (including a well-formed JSON value that is not an object);
`3` missing, unreadable, oversized, or malformed input (non-UTF-8,
bad JSON syntax, duplicate JSON keys, which are rejected rather than
silently overwritten, unprocessable nesting, or text unrepresentable as
UTF-8 such as lone surrogates). Failures never print tracebacks or
environment details; every failure still prints one JSON result with
`valid=false` and `execution_authorized=false` on stdout. The read is
bounded and the 1 MiB limit is enforced on the bytes actually read.

## Plan v1 reference

Top level has exactly `schema_version` (integer `1`; booleans rejected),
`repository` (exactly `Phani-Pavuluri/marketing_intelligence_platform`),
`plan_id` (stable ID), `goal` (nonempty text), `exclusions` (nonempty array of
nonempty text), and `tasks` (nonempty array, at most 100). Unknown fields are
rejected at every level.

Each task has exactly `task_id` (stable ID), `feature_branch` (valid Git
branch name, never `main`), `outcome` and `observable_behavior` (nonempty
text), `owned_paths` (nonempty array of exact repository-relative filenames),
`acceptance_evidence` (nonempty array of nonempty text), `risk_tier` (integer
1, 2, or 3), `depends_on` (array of task IDs in the same plan), and
`unresolved_design_questions` (must be an empty array).

Branch names follow `git check-ref-format --branch` semantics, verified
against real Git in both the `--branch` and `refs/heads/` forms: no
slash-separated component ending in `.lock`, no leading/trailing slashes or
dots, no `..`, `@{`, control characters, spaces, `~^:?*[\\`, or components
starting with a dot. The lone name `@` is legal per Git and accepted. Two
documented deviations: `main` is reserved, and leading-dash names are refused
as a CLI-safety rule (the `--branch` form parses a leading dash as flags).

Stable IDs start with a letter and contain only `A-Z`, `0-9`, `_`, at most 128
characters. Task IDs and branches must be unique. Dependencies must name
existing tasks, never the task itself, and never form a cycle. The reported
order is deterministic: at each step the lexicographically smallest ready task
runs first. This order is proposed sequencing, never live eligibility.

Owned paths are exact filenames, not globs or directories: no absolute paths,
no `..` traversal, no empty or `.` components, no backslashes, NUL, or
wildcard characters, no `.git/` content, no local-only `.codex/` or
`docs/tasks/` content, and never the three stable execution metadata files
(`docs/execution/ACTIVE_TASK.md`, `EXECUTION_STATE.json`,
`LATEST_COMPLETION_REPORT.md`), which are implicit lifecycle ownership. The
validator never checks that owned paths exist, so new files and isolated
proposal validation are allowed. When several tasks name the same path, one
must depend transitively on the other; otherwise the overlap is rejected as
unseparated independent work.

## Digest meaning

`plan_sha256` is the SHA256 hex of the canonical parsed plan JSON: sorted
keys, compact separators, `ensure_ascii=false`, UTF-8 bytes, no trailing
newline. It is stable across input key order and whitespace, so the same
logical proposal always digests identically. It identifies proposal content
only; it proves nothing about live prerequisites, approvals, or compatibility.
