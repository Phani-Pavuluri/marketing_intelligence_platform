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

## End-to-end routine runbook

This section is the executable handoff for eligible tasks. No owner
prompt occurs anywhere inside the eligible path below.

### Activation status (observed, not asserted)

Delegation is activated by pushed Git-note evidence, not by the policy
definition's historical status header (which is preserved unchanged so
the pinned policy hash holds). Live verification on October 15, 2026:
activation receipt `205960c9-6c11-4c73-9cb7-a0d5f1b153ad` on
prerequisite `d69e0eb85425a471ccaef44caabfea35140bd701` under
`refs/notes/mip-delegated-routine-receipts` resolving to
`2e6c0a4eb3b2ef5ab2c6a0a6bbc95e20fdd2328b`; policy document SHA256
`b1c223d6d63133127d8358fcd8bcde00660817a349056e5b59e2534ff50affb4`.
Do not create another activation and do not edit the policy to flip its
status. Preflight re-verifies activation, policy hash, and note
presence on every use.

### Reviewer sequence (Codex reviewer role, separate session only)

1. Review the exact published remote head with the existing observer;
   result, run events, and model output land in the observer-owned
   report bundle. No other report location is accepted.
2. Run every required validation category on the exact tree and store
   the actual logs in that bundle. Executing tests is mandatory;
   parsing a claimed summary never counts. Never synthesize observer
   output or run UUIDs.
3. Compose the strict v1 approval receipt: SHAs with ancestry, reviewer
   UUID distinct from the `ses_` implementation session, report digest,
   tier-locked categories with exact-tree references and evidence paths
   inside the bundle, quoted canonical state, explicit routine
   assertions, activation reference above, and unchanged authority.
4. Verify actual session identity, activation currency, and semantic
   scope (no contract-meaning, architecture, authority, or sibling
   change) before writing anything.
5. `attach` the receipt to the reviewed head (dedicated ref only),
   push the notes ref explicitly, and verify the live remote value.
   Refuse: any validation failure, any semantic doubt, any missing
   evidence, any push ambiguity. A refusal stops the path with reasons;
   it never becomes an approval.

### Operator sequence (merge session)

1. Run read-only `preflight` against the receipt; exit 0 is required.
   Preflight fetches and writes nothing and repairs nothing.
2. Follow the existing execution-standard merge flow unchanged:
   re-verify ancestry and unchanged baselines, rerun the applicable
   gate on the exact approved tree, `merge --ff-only`, re-validate,
   push, observe branch cleanup, and record one closure commit with
   delegation provenance and the receipt identity.
3. Refuse and stop on any nonzero preflight, moved head or baseline,
   missing receipt, or required-gate failure. The worker never approves
   or merges on agent agreement, silence, or a passing test suite
   alone. Unclear classification escalates to the owner.

### Complete executable sequence

Each step names its exact command, evidence location, and stop
condition. Steps 1–7 run in the Codex reviewer session; steps 8–14 in
the operator merge session. Anything not listed here verbatim is not
part of the eligible path; see the policy and the task execution
standard for authoritative definitions.

1. `python -m mip.execution.review_observer --repository PATH status`
   — read ledger state. Evidence:
   `.codex/review-observer/ledger.json`. Stop on any `blocked` event
   or scan error.
2. `python -m mip.execution.review_observer --repository PATH review --ref <exact-head>`
   — review exactly the published head. Evidence (observer-owned,
   never hand-written):
   `.codex/review-observer/reports/<sha256(task:kind:sha)>/` containing
   `result.json`, `review.md`, `owner-update.md`, `events.jsonl`,
   `model-output.json`, `stderr.log`. Stop unless the exit status is 0
   with verdict `pass` and no open findings.
3. Run every required validation category on the exact tree and store
   the actual logs in that report bundle: focused
   `poetry run pytest -q <owned-tests>`; full native `make validate`
   where the tier requires it; `poetry run python -m
   mip.execution.taskctl check`; `git diff --check`. Stop on any
   failure or any blocked category. Log text, not summaries, is the
   evidence.
4. `python -m mip.execution.delegated_merge validate-receipt --receipt
   PATH` — strict schema and structural check, no Git contact. Stop on
   any rejection.
5. Verify the reviewer UUID in `events.jsonl` (`thread.started` with
   matching `thread_id`), the completed-turn artifact
   (`model-output.json`), and the report digest against the receipt.
   Stop on any mismatch; never synthesize these artifacts.
6. `python -m mip.execution.delegated_merge attach --repository PATH
   --receipt PATH --head <reviewed-sha>` — writes only the dedicated
   notes ref. `already-attached` with identical bytes is success;
   conflict, corruption, or lock contention stops the path.
7. `git push origin refs/notes/mip-delegated-routine-receipts`, then
   `git ls-remote origin refs/notes/mip-delegated-routine-receipts` and
   require the live value to equal the just-pushed value. Stop on any
   mismatch. Never push implicitly and never force-push.
8. `python -m mip.execution.delegated_merge preflight --repository
   PATH --receipt PATH` — exit 0 required. It verifies receipt↔note
   equality, live notes/branch/main values, observer evidence, quoted
   state, ancestry, and activation without fetching or writing. Any
   nonzero exit stops the merge with its stable code.
9. Exact-head checks: `git rev-parse --verify <reviewed-sha>`;
   `git merge-base --is-ancestor <auth> <impl>` and `<impl>
   <reviewed>`; `git ls-remote origin refs/heads/<branch>` equals the
   reviewed SHA; `git ls-remote origin refs/heads/main` equals the
   recorded baseline. Stop on any mismatch or moved ref.
10. Rerun the task's applicable validation gate on the exact approved
    tree, including Docker-backed `make validate` wherever required.
    Stop on any failure.
11. `git switch main` then `git merge --ff-only <reviewed-sha>` — no
    squash, rebase, merge commit, or force update. Rerun the gate on
    the fast-forwarded tree, then `git push origin main` and prove
    local main equals remote main. Stop on any divergence.
12. Delete the remote feature branch, delete the local feature branch
    where present, and observe both deletions
    (`git ls-remote origin refs/heads/<branch>` empty;
    `git branch --list <branch>` empty). Stop if cleanup is unobserved.
13. `python -m mip.execution.taskctl transition --to merged
    --reviewed-head-sha <reviewed-sha> --local-branch-cleanup
    observed_deleted --remote-branch-cleanup observed_deleted`, update
    only the human completion narrative, run `taskctl check`, and create
    exactly one closure commit recording approval provenance,
    validation, cleanup, lineage, limitations, and authority impact.
14. Push the closure commit and prove local and remote main are equal
    again. The independent reviewer receipt and observer result/run
    artifacts belong to the reviewer role after producer publication;
    the producer never fabricates them and never treats an unissued
    receipt as completion evidence.

### Owner-reserved decisions (unchanged policy)

Task authorization and goals, Tier 3 and non-routine work, scope and
architecture, capabilities and authority, policy and activation
changes, sibling matters, production actions, and substantive
disagreements stay owner-decided. No prompt is removed for any of
these; only the eligible routine path above runs without one.

## Evidence map

Every claim in the runbook above resolves to the concrete Git evidence
below. Re-run any verify command to confirm it independently; all reads
are non-mutating.

| Claim | Evidence | Verify (read-only) |
|---|---|---|
| Activation receipt exists | Receipt `205960c9-6c11-4c73-9cb7-a0d5f1b153ad` on prerequisite `d69e0eb85425a471ccaef44caabfea35140bd701` under `refs/notes/mip-delegated-routine-receipts`, live target `2e6c0a4eb3b2ef5ab2c6a0a6bbc95e20fdd2328b` | `git ls-remote origin refs/notes/mip-delegated-routine-receipts` shows the target; `git notes --ref mip-delegated-routine-receipts show d69e0eb…` (after an explicit fetch) shows the receipt |
| Policy hash current | SHA256 `b1c223d6…` of `docs/execution/DELEGATED_ROUTINE_MERGE_POLICY.md` as committed on main | `git diff --quiet HEAD -- <path>` (unmodified) plus `sha256sum` of the file; preflight recomputes this on every use |
| Required validation ran on the exact tree | `taskctl_check` and `git_diff_check` pass; Tier 1 records full pytest, Docker, Ruff, and mypy as `not_required` | `poetry run python -m mip.execution.taskctl check`; `git diff --check`; per-checkpoint outputs and tree SHAs are quoted in the task completion report and the publication receipt commit message |
| Observer artifacts | This Tier 1 docs surface produces no observer bundle; none is claimed | Independent review evidence for each checkpoint appears in the observer-owned report bundle (`.codex/review-observer/reports/`) and in the reviewer's receipt, never in this guide |
| This task's receipt and notes | Issued by the independent reviewer after publication, not by the worker | `delegated_merge validate-receipt`, then `attach` plus explicit push; `preflight` confirms file↔note equality and live-ref match |
| Publication evidence | Implementation commit, validation-receipt commit, branch name, and local/remote equality | `git log`, `git show --stat`, and `git rev-parse HEAD` versus the remote branch head, all quoted in the completion report |

No evidence is altered, repaired, or fetched into place by verification.
A missing or mismatched entry fails closed with its stable error code
instead of being reconstructed.
