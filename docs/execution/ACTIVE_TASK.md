# Active Task

**Status:** ready_for_review
**Owner:** MIP cross-repository execution-governance owner
**Last updated:** 2026-08-04
**Last verified:** 2026-08-04

## Identity

- **Task ID:** `MIP_CODEX_EXECUTION_INCIDENT_EVIDENCE_MATRIX_001`
- **Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
- **Feature branch:** `docs/mip-codex-execution-incident-evidence-matrix-001`
- **Execution mode:** `branch_and_fast_forward`
- **Risk tier:** Tier 2 — cross-repository forensic evidence package
- **Coordination workstream:** `WS-MIP-CODEX-EXECUTION-EVIDENCE-MATRIX-001`
- **Capability owner:** MIP repository execution-governance evidence
- **Capability authorizations changed:** `false`

## Prior task disposition

`MIP_CROSS_REPOSITORY_CODEX_EXECUTION_ROOT_CAUSE_AND_ROI_AUDIT_001` is superseded without merge.

- rejected remote head: `3233f424ad388b30ef2181eab8198a45fb5edf03`
- rejected implementation: `c9134f0c036581290ef686ee7e5d1058055c952d`
- preserved branch: `docs/mip-cross-repository-codex-execution-root-cause-roi-audit-001-r1`
- correction cycles consumed: `1 of 1`
- supersession reason: the corrected audit remained factually unreliable because known Git lifecycle evidence was marked unavailable, MIP thin-launcher task 002 was misdiagnosed, and the semantic validator checked structural shape rather than evidence truthfulness.

The rejected branch is forensic source evidence only. Do not merge, modify, rebase, force-update, or treat it as an approved audit.

## Current repository pins at task authoring

- MIP `main`: `cda803790be15089412038ac33f2af8205b5e83f`
- MMM `main`: `f2e0eade0ad917c1b28ab5521e6d35a35047d988`
- GeoX `main`: `d0f0ba937c79528abd34d7ff89eb4601080805e9`
- GeoX live producer branch: `feat/geox-certified-calibration-source-manifest-001`; its branch execution state currently records `changes_requested`/blocked evidence after the sole correction cycle. That mutable branch is context only and must be refreshed during execution.

Before implementation, fetch and re-read all three current remote mains and the exact GeoX producer branch. Stop on inaccessible history or overlapping ownership. MMM and GeoX remain read-only.

## Primary independently reviewable outcome

Publish one exact, Git-grounded incident evidence package containing:

1. a normalized 12-record cross-repository incident/context/control matrix; and
2. a lookup ledger proving how every populated, null, not-applicable, or unavailable lifecycle field was resolved.

This milestone performs repository archaeology and evidence normalization only. It does **not** decide root causes, recommend controls, estimate ROI, authorize a pilot, update execution standards, or modify product workstreams.

## Why this milestone is split from the prior audit

The rejected audit combined historical reconstruction, causal attribution, ROI estimation, coordination refresh, recommendation, and lifecycle publication. That scope allowed incomplete evidence to be hidden behind schema-complete JSON. This task freezes the evidence layer first so a later decision task can consume an externally reviewed source rather than repeat repository archaeology.

## Required record sample

Create exactly these 12 separately identified records:

### MIP incidents

1. `MIP_GIT_AUTHORITATIVE_THIN_LAUNCHER_STANDARD_001`
2. `MIP_GIT_AUTHORITATIVE_THIN_LAUNCHER_STANDARD_002`
3. `MIP_P2_GEOX_MMM_COMPATIBILITY_FIXTURE_BRIDGE_001`

### MMM incidents and context

4. `MMM_REPOSITORY_EXECUTION_PROTOCOL_ADOPTION_001`
5. `MMM_GIT_AUTHORITATIVE_THIN_LAUNCHER_STANDARD_ADOPTION_001`
6. historical PR `#19` / `MMM_REPO_NATIVE_EXECUTION_HANDOFF_ADOPTION_001`

### GeoX incidents and context

7. `GEOX_EXECUTION_BRANCH_BINDING_001` and its reauthoring successor, represented as one linked incident family only when every materially distinct attempt is separately enumerated inside the record
8. `GEOX_CERTIFIED_CALIBRATION_HANDOFF_SOURCE_FIXTURE_001`
9. `GEOX_CERTIFIED_CALIBRATION_SOURCE_MANIFEST_001` as active context only

### Successful controls

10. one successful MIP product or contract task
11. `MMM_REPO_NATIVE_EXECUTION_HANDOFF_V2_RECONCILIATION_001`
12. `GEOX_CERTIFIED_GOVERNED_READOUT_FIXTURES_001`

Do not substitute a different incident identity without recording why the named identity is unavailable. Additional records are prohibited; use nested attempts inside the required record when needed.

## Required starting anchors

These anchors are mandatory lookup starting points, not permission to skip full-history inspection.

### MIP

- thin launcher 001 authoring: `4685d126f145e269f1b2e9f051fb8e5c14f55d1a`
- thin launcher 001 authorization: `a315d7ba8084188a8017f87ba67e7bc836a9aeb1`
- thin launcher 001 authorization boundary: `9bed0f30879e68473a37b0e65d449ea0b6a6e3f3`
- thin launcher 001 implementation: `dde6969b1192b97aea519c9589d27186f19b6db2`
- thin launcher 001 rejected head: `e390f1b47f8a7c5dfaa7a05613c2c4de73e4a548`
- thin launcher 001 supersession on main: `c277a3681dfad2d4e9261f5578748a4cb160504e`, `464b69c3ba197e5490dcfb76dd9b1613e3b33360`, `45eca4e8ca75bd9f152c2d025f9c57773dfa27ee`
- thin launcher 002 authoring: `92d327e1fc022fc20baf503b984fefc847a9cbf1`
- thin launcher 002 authorization: `786f7ddbf30dcdada794af6691d18e68bf762542`
- thin launcher 002 authorization boundary: `950ec89c9345caa506b0101774516fb89af8d0bc`
- thin launcher 002 supersession on main: `35bce9894a1726893a0123f575b86d62518a0962`, `b6006f6bc9b057c5def2303a046b2e9cf0886bc4`, `f8fb482e51697f004d3fa2a6b229f6729d423cef`
- P2 task authoring: `fdcf473dc2f42a3bcfeacc21719f1fa8c77b7675`
- P2 authorization record: `f8392e85016a39e5d729fa50bb2798c694936380`
- P2 state authorization: `0b4cd1fca73716e4968c2ceb70c594ad8aadd8ca`
- P2 blocked head: `480b32040ce185b8ff091435121c4bea6fc6c453`

### MMM

- protocol authoring: `f54bb07fdf749916e6219eeb1b1b1e5f9245e5d3`
- protocol task authorization: `c3c84956ad968532b81b36e8d5f41670cc96367c`
- protocol authorization boundary: `b8878dfa4bcd178a0472c3b812492a5bb4ac0b45`
- first implementation: `bde826a4b21e35c1b313db781c8d3c1d7f39d2cc`
- first receipt: `ccb25680b90fa6eb4ce4dc2d6f84051797641fa6`
- review/correction metadata: `999ceec479e0db4b8ed50177924858613353adff`, `e6fe3b8e3d0ee040bda5522acb3dbe512302bbb2`, `05aad8ede0fd939da1ee699e02fba331558a67de`
- corrected implementation: `0e77ce6b787bd508600c1496288a459b8d821edf`
- corrected receipt: `c370dc7cd59a61cc2e19025d1a2328c7867b63be`
- closure: `ac546548784385baab67d7c935e5a4fcdfc9e1af`
- thin-launcher proposal: `b93562a2c2a3aec2897e6196a6f2095bce6c16db`, `a7d45e0b6451e8c64cf3a94c8c888afd9fecf070`, `f2e0eade0ad917c1b28ab5521e6d35a35047d988`
- PR #19 implementation: `f0b0ae35619739a4ff3d95f2cf7c93bf7ec523a0`
- PR #19 ready head: `ea16ab7e7b1089f5de479eeffb236fad2767edf1`
- PR #19 merge commit: `ad55fef6799a8bd717108781ad44fc88fa116df7`
- reconciliation control authoring: `a90136e7e86a60cee0846381144d478e483269c4`
- reconciliation authorization: `dda1f31a1e429a4cede791b4f21a979aefe375c5`
- reconciliation implementation: `9187b5bfe7fe13c4a6b3be7aa742b627027eaa84`
- reconciliation review head: `5bc26f987d191bd2251cd12a35de5d0a49a3cbc5`
- reconciliation closure: `1b75d1d3c9f49d40f2b7ab71f524fbd2dc6d1421`

### GeoX

- branch-binding authoring: `d5e38b0c8c207be71374b6a7de97f5d04c557fdb`
- branch-binding authorization: `dc68853e87a65a494c942b3fe2794e321a22b036`, `d17bb81c9dbc67f773fd71068c26b14c92989f42`
- branch-binding supersession: `fc99f4a362ac1b7790e6a865c6232bb51e86de2d`, `799848c0d58ab4eda19bfa964c675822b298eb32`, `b6c714ced8a9c6e9c1fcb0f6b4f7f79a542c5a7f`
- reauthoring: `956daef5ce74d04b78bfdecccd5821fe9c607d08`, `584af216c390ef86aca0631f289fa0f4456a4375`, `94d512eeffc549cdd98d0dffa166caeb9d75c2c1`, `0a463ad96cda31dc2bdc962fd24f5481bb7aede9`
- reauthoring supersession: `d3f64937798234c45f1c7f473e27a2dc993551c6`, `944ffe0485f95d95b33a230c0dc220fb7e28a082`, `e9b7d311ecaf5a90e227d8299f745a0e8f332368`
- calibration handoff source authoring: `f72635c67c7d917759a9c5114bde3d2a404ef831`
- calibration handoff source authorization: `0c7f13509ba8569c132513405cc12f999ab57232`, `f8829922aa93ada66de5f8d36abd49bb4bcfe3eb`
- calibration handoff preserved implementation/review/correction anchors: `191ddbe918cde06ee30c12b3a3d3998e917b86f5`, `49059bf5baae58764c7c80e015c8ddccf590117a`, `1c08554dc4d50b1a73c33af49ff7b9f6e2756889`, `8986036c0c114b7ff75ac675e69cfbb69223b3ff`
- calibration handoff supersession on main: `f02e43af25a624ac3de97df3c9df2b26736d6e61`, `bb95b8a40c9b750a5a8db3b0650c851c041da540`, `80dbe14c6b2ce74b33a2b776c5e567afba582bf5`
- active source-manifest authoring/authorization: `dad4c1c5427dc7534eb8018e79d1d9bcbe8651ed`, `486c626dcf24d176ab30e034057348f92b6257d4`, `d12a46d191eb7998870a6f040af9c424f18a4e31`
- governed-readout fixture control: `9b74696bb930a06a3e2d4af78a1b9ea7b65cf99d`, `860182386c39f487747de5f43e67a31e9978e57c`, `2fbfaf14efd5701f22a8c34258c2a9873037e084`

## Matrix artifact

Create:

`docs/audits/archives/MIP_CODEX_EXECUTION_INCIDENT_EVIDENCE_MATRIX_001.json`

Top-level keys:

- `schema_version`
- `generated_at`
- `source_repository_pins`
- `record_count`
- `record_type_counts`
- `records`
- `known_limitations`

Every record must contain:

- `record_id`
- `repository`
- `task_id`
- `record_type` (`incident`, `active_context`, or `successful_control`)
- `attempts`
- `base_sha`
- `task_authoring_sha`
- `authorization_sha`
- `authorization_boundary_sha`
- `implementation_sha`
- `publication_or_receipt_sha`
- `rejected_review_sha`
- `correction_authoring_sha`
- `correction_implementation_sha`
- `correction_receipt_sha`
- `blocked_sha`
- `merged_sha`
- `closure_sha`
- `preserved_branch_sha`
- `branch_names`
- `risk_tier`
- `prompt_mode`
- `owned_paths`
- `observed_changed_paths`
- `commit_count`
- `validation_evidence`
- `first_pass_disposition`
- `final_disposition`
- `correction_cycles`
- `review_findings`
- `evidence_item_ids`
- `unavailable_fields`
- `evidence_confidence`
- `confidence_rationale`

Use JSON `null` only for not-applicable or genuinely unresolved values. Every null must be explained in `unavailable_fields` and linked to lookup-ledger evidence.

Do not include root-cause labels, counterfactual controls, solution recommendations, effort estimates, ROI, or pilot decisions.

## Lookup ledger artifact

Create:

`docs/audits/archives/MIP_CODEX_EXECUTION_INCIDENT_EVIDENCE_LOOKUP_LOG_001.json`

Every matrix lifecycle fact and evidence item must reference one or more ledger IDs. Every ledger entry must contain:

- `lookup_id`
- `repository`
- `source_type` (`commit`, `branch_file`, `main_file`, `pull_request`, `comparison`, or `command_result`)
- `requested_ref`
- `path_or_pr`
- `lookup_command_or_action`
- `lookup_status` (`found`, `not_applicable`, `not_found`, or `inaccessible`)
- `resolved_sha`
- `observed_subject_or_value`
- `evidence_classification` (`git_observed`, `locally_reported`, or `unavailable`)
- `proposition_proved`
- `captured_at`

A matrix field may be marked unavailable only when the ledger records an actual lookup attempt with status `not_found` or `inaccessible`. A not-applicable field must use `not_applicable`, not `unavailable`.

## Evidence rules

- Inspect exact commit diffs and the execution files at the exact relevant refs.
- Do not rely on current `main` alone to reconstruct a prior branch lifecycle.
- Do not infer one SHA from a nearby commit message.
- Do not treat a completion message as Git evidence unless the same fact exists in a committed artifact or commit object.
- Separate Git-observed validation from locally reported validation.
- Record exact validation commands and counts only when a committed receipt/report supports them.
- Record prompt mode only from a committed task, `AGENTS.md`, or execution-state field at the relevant ref.
- A current branch state is context, not a final incident disposition.
- The prior rejected audit is an evidence source for reviewer findings only; it is not authoritative when contradicted by underlying Git.

## Owned paths

Implementation may modify only:

1. `docs/audits/archives/MIP_CODEX_EXECUTION_INCIDENT_EVIDENCE_MATRIX_001.json`
2. `docs/audits/archives/MIP_CODEX_EXECUTION_INCIDENT_EVIDENCE_LOOKUP_LOG_001.json`
3. `docs/execution/ACTIVE_TASK.md`
4. `docs/execution/EXECUTION_STATE.json`
5. `docs/execution/LATEST_COMPLETION_REPORT.md`

No other path is authorized.

## Prohibited scope

Do not modify:

- MMM or GeoX;
- MIP coordination state/history;
- the rejected audit artifacts;
- `AGENTS.md` or execution standards;
- tests, validators, CI, Git hooks, application code, analytical code, contracts, adapters, fixtures, LLM, orchestration, UI, or deployment;
- product blockers or sibling workstream states.

Do not create a PR, merge, squash, rebase, force-push, or merge commit. Do not implement `taskctl`, a task schema, prompt generator, workflow engine, root-cause report, ROI model, or pilot.

## Acceptance requirements

The final exact tree must prove:

1. exactly 12 required records exist with counts `8 incidents`, `1 active_context`, and `3 successful_controls`;
2. every mandatory starting anchor is present in the lookup ledger with `found` status or an explicit repository contradiction;
3. every non-null lifecycle SHA is a lowercase 40-character commit verified by a successful lookup;
4. every null field is classified `not_applicable`, `not_found`, or `inaccessible` through a linked ledger entry;
5. every evidence item proves one narrow proposition and cites an exact repository/ref/path or PR;
6. current MIP, MMM, GeoX mains and the GeoX producer branch were refreshed during execution;
7. MIP thin-launcher task 002 includes the rejected semantic-review findings about narrowed/self-modified acceptance coverage rather than being described only as unmerged;
8. MMM protocol adoption includes its known authoring, authorization, first publication, rejection/correction, corrected receipt, merge, and closure lineage;
9. GeoX calibration-handoff source fixture includes implementation failure, rejected review, correction, invalid blocked publication, and supersession evidence;
10. successful controls use the same evidence depth as incidents;
11. no causal conclusion, recommendation, ROI assumption, or pilot decision appears;
12. no prohibited path changed.

## Validation gate

On the frozen final task-owned tree run:

- JSON parsing for both artifacts and `EXECUTION_STATE.json`;
- a non-committed semantic validator checking exact record identities, record counts, required keys, unique IDs, SHA syntax, matrix-to-ledger foreign keys, mandatory-anchor coverage, null/unavailable rules, evidence classifications, and prohibited analytical fields;
- a second independent script that verifies every `found` commit SHA exists in the declared local repository with `git cat-file -e <sha>^{commit}`;
- exact owned-path validation from the authorization baseline;
- `git diff --check`;
- a scan proving no root-cause, recommendation, ROI, or pilot fields appear in either artifact;
- local/remote branch equality after push;
- one exact-tree publication receipt.

Docker and the full application suite are not required because executable code and tests are prohibited.

## Publication contract

On success publish one remote `ready_for_review` head containing:

- one evidence-package implementation SHA;
- one exact-tree receipt;
- exact MIP/MMM/GeoX pins and GeoX branch context;
- exact record and ledger-entry counts;
- exact changed paths;
- exact validation commands and results;
- Git-observed versus locally reported evidence counts;
- unavailable/not-applicable counts and limitations;
- confirmation that no causal or ROI decision was made;
- empty task blockers;
- task execution true; correction, merge, and PR authority false;
- no sibling, product, analytical, runtime, pilot, production, or capability authority change;
- local/remote branch equality.

If a required repository object or preserved branch is genuinely inaccessible, publish Git-durable `blocked` with the exact object, attempted lookup, and resolution condition. Missing analysis is not a blocker because analysis is out of scope.

## Deferred successor

`MIP_CODEX_EXECUTION_ROOT_CAUSE_AND_ROI_DECISION_001` may be authored only after this evidence package is externally reviewed, approved, fast-forward merged, and closed. It must consume the merged matrix and lookup ledger without repeating repository archaeology.

**Unresolved execution-blocking design questions:** none.

## Publication result

- **Status:** `ready_for_review`
- **Evidence-package implementation SHA:** `3a3f4b99eb7ebaa6fa3869e34145cc111892fcc7`
- **Evidence package:** 12 records and 75 lookup-ledger entries.
- **Authority:** task execution remains true for this completed publication; correction, merge, PR, sibling, and capability authority remain false.
