# Delegated Routine Merge Policy

Status: policy definition; delegated merge execution is not activated.
Owner: MIP program owner. Decision source: the user's explicit confirmation on
2026-10-14 that routine merges should proceed after independent review and
required validation, without asking the user each time.

## User experience and agent responsibilities

The user receives plain-language progress updates instead of routine technical
merge reviews. Muse-Spark owns implementation approach and execution within
the authorized task. Codex provides high-level guidance against agreed goals,
reviews completed work and supporting evidence, and discusses findings and
recommendations. Discussions do not prescribe exact implementation prompts,
take over product implementation, or impose automatic pause/release controls.

The user may give goals, priorities, context, and feedback in the coordinating
conversation. Decisions that change durable scope or authority must be recorded
in Git before execution. Agent agreement cannot replace that record.

## Default and eligibility

The default approval mode is `user_exact_head`. A future task may declare
`merge_approval_mode: delegated_routine` in its Git-authored canonical state and
explain its eligibility in the active task. No mode, unknown mode, or ambiguous
eligibility requires user approval of the exact remote head.

Delegated approval is limited to Tier 1 or Tier 2 work delivering previously
authorized behavior within the agreed goals, capability boundaries, architecture,
owned paths, and acceptance criteria. A public contract can be Tier 2 but is
not automatically routine: any material change to its meaning or architecture
requires the user. Tier 3 work is never delegated under this policy.

All eligibility conditions must hold:

- The task is definition-ready, explicitly authorized, and opts into delegation.
- Its prerequisites and ownership are verified against live Git.
- An independent Codex review examines the exact published remote head,
  implementation diff, relevant files, completion report, durable validation
  receipt, acceptance evidence, and alignment with agreed goals.
- Review finds no unresolved correctness, scope, authority, or validation issue.
  Optional suggestions may be deferred with a recorded explanation.
- Every required validation category passes on the exact tree; none is blocked.
- Main remains at the authorized baseline and the remote feature head still
  matches the review receipt when the merge begins.
- The activation prerequisite below has been satisfied.

An implementation agent cannot approve its own work. A distinct session of the
same implementation role is insufficient: the reviewer must be a separate Codex
review role that did not author the reviewed implementation. An agent's claim of
completion, passing tests alone, mutual agreement, or silence cannot grant approval.

## Decisions reserved for the user

User approval remains required for changes to project goals or priorities;
roadmap direction; capabilities outside agreed goals; material architecture or
scope; approval/governance policy; security, data-use, pilot or production
authority; analytical truth; cross-repository contracts or ownership; and
substantive disagreements that the agents cannot resolve with existing evidence.
Unclear classification is escalated with options, a recommendation, and impact.

This policy's adoption, activation decision, and later changes are themselves
approval-authority decisions. They cannot approve themselves or use delegated
routine approval. Delegation does not authorize new tasks, capabilities,
roadmap changes, sibling work, or production actions.

## Independent exact-head receipt

Approval evidence must be durable and independently verifiable outside the
reviewed implementation tree. It must identify:

- Repository, task ID, feature branch, and approval mode.
- Authorization SHA, implementation SHA, and exact reviewed remote head SHA.
- Independent reviewer role and session identity, with authoring independence.
- Decision, issuance time, evidence source, and immutable receipt identity.
- Required validation categories, results, and exact-tree evidence references.
- Eligibility findings, authority impact, limitations, and disposition of findings.
- User delegation provenance and policy version used for approval.

A changed implementation or publication head invalidates its receipt. Re-review
and revalidate the replacement. A review receipt is merge evidence only; it does
not grant product or analytical authority. Do not insert a pre-merge
approval-metadata commit into the reviewed implementation branch.

## Activation prerequisite

The observer, discussion channel, and merge executor do not exist as a result
of this document. Delegated routine merges remain unavailable until a separately
authorized, reviewed, and merged MIP task defines the receipt schema and durable
persistence/transport, verifies reviewer identity and independence, validates
eligibility and exact-head evidence, and proves fail-closed merge preflight.
Activation must be recorded in Git with exact evidence and the user's authority
decision. Chat agreement or an untracked local report is not activation.

That successor must prove acceptance and rejection cases for missing approval,
non-routine work, self-approval, stale/replaced heads, absent evidence, failed
validation, moved main, and changed policy. It must not expand capability
authority. MMM/GeoX adoption requires separate owner-repository authorization;
this policy applies only to MIP.

## Merge and closure invariants

Follow [TASK_EXECUTION_STANDARD.md](TASK_EXECUTION_STANDARD.md): synchronize;
re-fetch; verify repository/task/branch identity, authorization ancestry,
owned-path boundaries, exact reviewed head, and unchanged main baseline; rerun
the applicable gate; use `git merge --ff-only`; validate after fast-forward;
push; observe branch cleanup; use taskctl transition to merged; and produce
exactly one closure commit. Persisted `merge_authorized` remains false and
`approval_commit_sha` remains null under taskctl V2.

For delegated merges, closure records the user's delegation provenance,
independent reviewer receipt, eligibility, exact head, required gate results,
resulting main lineage, cleanup, limitations, and authority impact. Never
force-push, rebase, squash, skip required validation, or merge an obsolete head
to make a delegated workflow succeed. Any failure stops merging and is recorded
on a safe authorized write target under existing lifecycle rules.

## Plain-language owner updates

Codex reports what is completed, ongoing, and planned; what users can do now;
why progress matters; important issues and discussions; and decisions needed
from the user, with recommendations and tradeoffs. Separate verified outcomes,
agent-reported progress, and proposals. Link detailed evidence without requiring
the user to read completion reports, task IDs, commit receipts, or test logs.
Do not invent completion percentages or claim unattended reporting is running
before a verified reporting service is active.

## Eligibility examples

| Situation | Outcome |
|---|---|
| Opt-in Tier 1 documentation correction within agreed scope, independent review and all gates pass | Eligible only after activation |
| Opt-in Tier 2 implementation of already authorized behavior without new architecture or contract meaning | Eligible only after activation and exact-head evidence |
| No explicit approval mode, missing receipt, or unknown eligibility | User approval required; no delegated merge |
| Tier 3 or roadmap, capability, architecture, authority, or governance change | User decision required |
| Required validation fails or evidence is missing | Block merge |
| Remote head changes, authorization is stale, or main moves | Block merge; re-establish evidence under existing rules |
| Implementation agent agrees with its own completion report | No independent approval |
| Agents disagree about a material requirement | Discuss evidence, then escalate unresolved disagreement |
