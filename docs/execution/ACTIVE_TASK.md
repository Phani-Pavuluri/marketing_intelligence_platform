# Active Task

**Status:** changes_requested
**Owner:** MIP cross-repository execution-governance owner
**Last updated:** 2026-08-04
**Last verified:** 2026-08-04

## Identity

- **Task ID:** `MIP_CODEX_EXECUTION_INCIDENT_EVIDENCE_MATRIX_001`
- **Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
- **Feature branch:** `docs/mip-codex-execution-incident-evidence-matrix-001`
- **Execution mode:** `branch_and_fast_forward`
- **Risk tier:** Tier 2 — cross-repository forensic evidence package
- **Rejected implementation SHA:** `3a3f4b99eb7ebaa6fa3869e34145cc111892fcc7`
- **Rejected review head:** `5e01767b0cf4a86262631c607bc2b0365f12253a`
- **Correction cycles:** one maximum; zero completed; one remaining
- **Capability authorizations changed:** `false`

## Review decision

Exact remote head `5e01767b0cf4a86262631c607bc2b0365f12253a` is rejected. It is structurally limited to the five owned paths, but its evidence matrix and lookup ledger do not satisfy the frozen truthfulness contract.

The frozen original task at the rejected head remains applicable. This correction section adds exact defects and replacement requirements; it does not narrow the original record set, owned paths, evidence rules, validation, sibling boundaries, or prohibited scope.

## Rejection findings

### 1. Generic null proofs do not satisfy field-specific lookup evidence

The lookup ledger uses one generic `not_applicable` entry and one generic `not_found` entry for many unrelated fields across all repositories and tasks. Those entries do not identify the task, field, requested ref, path, command, search scope, or failed lookup specific to each null.

The frozen contract requires every unavailable field to be supported by an actual field-specific `not_found` or `inaccessible` lookup, and every not-applicable field to have a task-specific applicability determination. A shared cross-repository catch-all entry is insufficient.

### 2. MIP thin-launcher task 001 omits its known correction lifecycle

`MIP-INC-001` incorrectly records:

- `rejected_review_sha: null`;
- no correction implementation or correction receipt;
- `correction_cycles: 0`.

Git contains:

- rejected review head `e390f1b47f8a7c5dfaa7a05613c2c4de73e4a548`;
- correction implementation `0e08dc1f77f91ce45e45d1f874c5ae505dfea129`;
- corrected receipt `69f7fd7178844576b8a3bdb84a881b3d38a3b8c5`;
- one correction cycle consumed.

These facts must be represented in the record and lookup ledger.

### 3. MIP thin-launcher task 002 marks known implementation evidence not found

`MIP-INC-002` incorrectly records null `implementation_sha` and `publication_or_receipt_sha` with generic `not_found` evidence.

Git contains:

- implementation `fe767166b08522764976f987368c8df5f6a9279f`;
- exact-tree publication receipt `4c682711365ba8255fcb1e4a9a3643cf5842efec`;
- branch `docs/mip-git-authoritative-thin-launcher-standard-002`;
- Tier-1 validation and changed-path evidence in that receipt.

The record must include those facts and the semantic-review evidence showing that the six-test harness narrowed or self-modified prior acceptance coverage. Failure to merge is not the only observed issue.

### 4. MMM PR #19 marks known authorization evidence not found

`MMM-INC-003` marks task authoring and authorization evidence `not_found` even though Git contains:

- task authorization/authoring record `02aaf1f29247a7aa95a783107c0e16bffdaa365e`;
- authorized state `ef63068c37041bdde55373cc08ef19333aa0fb5e`;
- base SHA `9a3aa5cb9a48c9a59d45e266685228835237f328`;
- branch `feat/mmm-repo-native-execution-handoff-adoption-001`.

Preserve implementation `f0b0ae35619739a4ff3d95f2cf7c93bf7ec523a0`, ready head `ea16ab7e7b1089f5de479eeffb236fad2767edf1`, PR #19, and merge commit `ad55fef6799a8bd717108781ad44fc88fa116df7`.

### 5. GeoX active-context record contradicts its own pinned branch

The package pins GeoX producer branch head `c18f56341b50c58505b59fc6cacf2337ca7f9fc4`, but `GEOX-CTX-001` records no implementation, rejection, correction, blocked state, or consumed correction cycle.

At that exact branch head, `docs/execution/EXECUTION_STATE.json` records:

- status `blocked`;
- rejected review head `6860d54796ae999184b9ffe3ac5bd16b69e5d745`;
- rejected implementation `8002e83556c324a73b9b51e8cbcb2038a9a2888f`;
- correction implementation `89c3ded7620b85e382cecec5243ca84f8fb93c95`;
- correction-authoring head `0b5d7c0fc580b6bbd7706aa208218a166527a869`;
- one correction cycle used and zero remaining.

The record type remains `active_context`, not a completed incident, but it must accurately represent the mutable lifecycle observed at its pinned branch head.

### 6. GeoX preserved-branch identity is incorrect

`GEOX-INC-002` places main commit `80dbe14c6b2ce74b33a2b776c5e567afba582bf5` in `preserved_branch_sha`. That commit disables the superseded task on main; it is not the preserved branch head.

Live GeoX execution evidence records prior-task preserved branch head:

`a84d85277f9bbc35c08a40308d65858adbd36713`

Use separate fields/evidence for main-line disable/supersession commits and the preserved branch head.

### 7. Successful controls are not reconstructed to the required depth

The MIP and GeoX successful controls rely primarily on one to three implementation/checkpoint commits and then mark task-authoring, authorization, publication, validation, or closure fields unavailable through generic ledger entries.

Either reconstruct the full task lifecycle through exact task/branch history, or provide separate, field-specific failed lookup entries proving why each lifecycle position cannot be established. Do not label one implementation checkpoint simultaneously as implementation, merged and closure without evidence for those distinct propositions.

### 8. The semantic validator checks shape and commit existence, not evidence truth

The validator accepts syntactically valid SHAs and generic null markers but does not reject:

- a known commit classified as not found;
- a field populated with the wrong lifecycle type;
- a current branch record contradicting the exact branch file;
- a generic lookup entry reused for unrelated missing fields;
- a proposition unsupported by the cited commit.

The corrected validator must include explicit truth assertions for the known anchors above and field-specific lookup foreign keys.

## Required corrected behavior

Correct only the evidence package and lifecycle publication. The corrected artifacts must:

1. retain exactly 12 records: 8 incidents, 1 active context, and 3 successful controls;
2. retain every required record key from the frozen contract;
3. replace generic `not_found` and `not_applicable` catch-all evidence with field-specific ledger entries;
4. add a stable field-level lookup identifier for each null, such as `<record_id>:<field_name>`;
5. identify repository, task, field, requested ref/search expression, path or PR, exact command/action, status, result, and proposition for every missing or not-applicable field;
6. populate every known lifecycle fact listed in the review findings;
7. verify every populated SHA is a commit in the declared repository;
8. verify every branch-file fact against the exact pinned branch head;
9. separate implementation, receipt, rejected review, correction, blocked, main-line supersession, preserved branch, merged and closure meanings;
10. record exact observed changed paths, risk tier, prompt mode and validation evidence when committed task/report evidence supports them;
11. preserve observed review findings without adding root-cause, counterfactual, ROI, or pilot analysis;
12. preserve MMM and GeoX as read-only evidence sources and the MIP P2 blocker as unresolved.

## Required record corrections

At minimum, correct these records:

- `MIP-INC-001`: add rejected head, correction implementation, corrected receipt and correction-cycle count.
- `MIP-INC-002`: add implementation, receipt, branch, risk tier, changed paths, validation evidence and semantic review evidence.
- `MMM-INC-003`: add task authorization/authoring record, authorized state, base, branch and exact PR evidence.
- `GEOX-INC-002`: correct preserved branch head and separate it from main-line disable/supersession commits.
- `GEOX-CTX-001`: accurately reproduce the lifecycle at pinned branch `c18f56341b50c58505b59fc6cacf2337ca7f9fc4` while retaining `record_type: active_context`.
- `MIP-CTRL-001` and `GEOX-CTRL-001`: reconstruct full available lifecycle or prove each missing field through specific failed lookups.

Review all remaining records for the same defect classes; do not limit correction to the named examples.

## Owned paths

Only these five paths may change:

1. `docs/audits/archives/MIP_CODEX_EXECUTION_INCIDENT_EVIDENCE_MATRIX_001.json`
2. `docs/audits/archives/MIP_CODEX_EXECUTION_INCIDENT_EVIDENCE_LOOKUP_LOG_001.json`
3. `docs/execution/ACTIVE_TASK.md`
4. `docs/execution/EXECUTION_STATE.json`
5. `docs/execution/LATEST_COMPLETION_REPORT.md`

No other path is authorized.

## Prohibited scope

Do not modify MMM or GeoX. Do not modify coordination files, rejected audit artifacts, standards, tests, CI, Git hooks, application code, analytical code, contracts, adapters, fixtures, LLM, orchestration, UI, deployment, or capability authority.

Do not perform root-cause analysis, counterfactual control design, ROI modeling, break-even analysis, or pilot recommendation.

Do not create a PR, merge, squash, rebase, force-push, or create a merge commit.

## Correction validation

Create a non-committed semantic validator that fails unless:

- exactly 12 records exist with counts 8/1/3;
- all required keys and identities exist;
- every non-null SHA is valid in the declared repository;
- every matrix fact references one or more ledger IDs;
- every null references a unique field-specific `not_applicable`, `not_found`, or `inaccessible` ledger entry;
- no generic cross-repository null-proof ledger ID is referenced;
- every `not_found` or `inaccessible` entry records the concrete attempted ref/search, path, command/action and result for that record and field;
- known MIP-001 correction SHAs are present;
- known MIP-002 implementation and receipt SHAs are present;
- known MMM PR #19 authoring/authorization SHAs are present;
- GeoX fixture preserved branch is `a84d85277f9bbc35c08a40308d65858adbd36713`, not `80dbe14c6b2ce74b33a2b776c5e567afba582bf5`;
- GeoX active-context record matches the exact execution state at `c18f56341b50c58505b59fc6cacf2337ca7f9fc4`;
- all mandatory anchors and all newly required anchors have ledger entries;
- no prohibited analysis fields exist;
- only the five owned paths changed.

Also run JSON parsing, `git diff --check`, exact changed-path checks, the independent `git cat-file -e '<SHA>^{commit}'` validator, and exact local/remote branch-head equality.

Docker and the full application suite remain not required because code and tests are prohibited.

## Corrected publication

Publish one corrected implementation commit containing only the two evidence artifacts, then one exact-tree receipt updating only the three execution files.

The final state must record:

- `ready_for_review`;
- corrected implementation SHA;
- rejected head and rejected implementation preserved;
- correction cycles completed `1` and remaining `0`;
- correction execution false;
- merge and PR authority false;
- exact record and ledger counts;
- exact validation commands and results;
- limitations and field-specific unavailable counts;
- no root-cause, ROI, or pilot decision;
- no sibling or capability changes;
- no PR or merge.

Stop after pushing and verifying one new exact remote `ready_for_review` head.

**Unresolved execution-blocking design questions:** none.
