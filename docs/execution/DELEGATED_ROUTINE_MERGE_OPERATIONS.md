# Delegated Routine Merge Operations

Verifiable independent receipts and read-only preflight for delegated
routine merges. This tooling never merges, never activates delegation, never
approves anything, and never mutates branches, worktrees, or execution
state. The policy definition in `DELEGATED_ROUTINE_MERGE_POLICY.md` is
read-only; activation remains a separate explicit owner authority decision
recorded in Git after this prerequisite merges.

## Commands

From an installed MIP environment:

```sh
python -m mip.execution.delegated_merge validate-receipt --receipt PATH
python -m mip.execution.delegated_merge preflight --repository PATH --receipt PATH
python -m mip.execution.delegated_merge attach --repository PATH --receipt PATH --head SHA
```

`validate-receipt` checks receipt schema and structural invariants with no
Git contact. `preflight` verifies every eligibility condition against live
Git without fetching or writing anything. `attach` is reviewer-side only:
it writes exactly one Git note under the dedicated ref
`refs/notes/mip-delegated-routine-receipts` for the reviewed head, never
force-overwrites, and never pushes. Pushing the notes ref is always a
separate explicit operator step.

## Receipts and independence

Receipts follow the strict version-1 schema in the authorized task contract:
identity SHAs with auth→implementation→reviewed ancestry, reviewer UUID in
the Codex namespace kept distinct from the `ses_` implementation session,
observer report digest, tier-locked validation categories with exact-tree
references, explicit routine assertions, quoted canonical state re-verified
against the committed blob, delegation provenance pinned to a Git-recorded
activation, and unchanged-authority impact.

Reviewer independence is corroborated three ways, never self-asserted: the
UUIDs differ by namespace and value and the reviewer UUID appears in no
implementation session record; the observer report bundle for the reviewed
head validates strictly with a matching digest and a real `thread.started`
run UUID plus completed-turn artifacts; and the receipt note exists on the
live remote notes ref. Preflight additionally requires the receipt file to
equal the attached note byte-for-byte in canonical form, the local notes
value to equal the live remote value, the live branch head to still equal
the reviewed head, and live main to still equal the recorded baseline.

## Failure semantics

- Exit 0: valid receipt, eligible preflight, attached, or already-attached.
- Exit 2: ineligible or evidence failure — non-routine tier or semantics,
  self-approval or forged attribution, stale or replaced heads, moved main,
  absent or mismatched observer/binding/quoted-state evidence, digest or
  run-UUID mismatch, missing/stale/corrupt/conflicting notes, file↔note
  mismatch, absent or drifted activation or policy, wrong notes ref.
- Exit 3: transport or state failure — unsettled Git or remote reads, lock
  contention, invalid timeouts. Corrupt notes and local state are preserved,
  never repaired or erased.

Identical duplicate attaches report `already-attached` without mutation.
Conflicting notes fail closed without force-overwrite. Indeterminate,
unpushed, or stale notes are never repaired by fetching. Errors use stable
`E_DELEGATED_*` codes and carry no secrets.

## Boundaries

- Independent exact-head review stays a separate Codex reviewer-role act;
  this tool verifies receipt fields and evidence, never reviews or approves.
- The merge and closure workflow stays the existing task execution
  standard gated on a valid receipt; there is no merge executor here.
- Sibling repositories are read-only context. MIP only.
- Everything under `.codex/` is local-only and never committed; notes refs
  are pushed explicitly and verified against the live remote.

## Validation

Tier 3 gate:

```sh
poetry run pytest -q tests/test_delegated_merge.py tests/test_review_observer.py tests/test_opencode_advisory.py
make validate
poetry run python -m mip.execution.taskctl check
```

Tests use isolated Git remotes, synthetic observer bundles with fixture
run UUIDs, and fixture notes refs — never production sessions or the live
execution state. The full existing observer and advisory suites are
preserved.
