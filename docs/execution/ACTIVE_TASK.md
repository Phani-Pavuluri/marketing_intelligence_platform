# Active Task

**Status:** ready_for_review
**Owner:** MIP cross-repository coordination and execution-governance owner
**Last updated:** 2026-08-04
**Last verified:** 2026-08-04

## Identity

- **Task ID:** `MIP_CROSS_REPOSITORY_CODEX_EXECUTION_ROOT_CAUSE_AND_ROI_AUDIT_001`
- **Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
- **Feature branch:** `docs/mip-cross-repository-codex-execution-root-cause-roi-audit-001-r1`
- **Authorization head:** `3d514206a2746b16dc1de3e56a92b6d79389aece`
- **Authorized branch baseline:** `cda803790be15089412038ac33f2af8205b5e83f`
- **Rejected implementation SHA:** `26f6a2e8d9d2fa64a5a095113feb7458d90945f2`
- **Rejected review head:** `9794085ad55014b4c104ccce74f9bbd87a255049`
- **Correction cycles:** one authorized, one completed, zero remaining
- **Execution mode:** `branch_and_fast_forward`
- **Risk tier:** Tier 2 — cross-repository forensic governance and ROI audit
- **Capability authorizations changed:** `false`

## Review decision

Exact remote head `9794085ad55014b4c104ccce74f9bbd87a255049` is rejected. It is not approved or merge-authorized.

The publication reached a durable terminal state and stayed within the authorized path set, but it did not satisfy the frozen evidence, analysis, structured-data, or validation contract. The reported schema-sanity success is not accepted because the committed JSON omits required records and required per-record fields.

## Frozen task contract

The complete task contract at the rejected head remains authoritative and must be re-read in full:

```bash
git show 9794085ad55014b4c104ccce74f9bbd87a255049:docs/execution/ACTIVE_TASK.md
```

This correction section adds precision. It does not replace, narrow, waive, or reinterpret any original requirement, owned-path boundary, validation requirement, sibling boundary, product-workstream preservation rule, or authority restriction.

## Required corrections

### 1. Complete the mandatory evidence sample

The incident matrix currently contains six incident/context records and omits required evidence. Add separately identifiable, evidence-grounded records for all mandatory items, including:

- `MIP_GIT_AUTHORITATIVE_THIN_LAUNCHER_STANDARD_002`;
- `MMM_REPOSITORY_EXECUTION_PROTOCOL_ADOPTION_001`, including its initial rejected head, correction, reviewed head, implementation, merge, and closure lineage;
- historical MMM PR #19 as a distinct nonconforming external-workflow incident rather than an unexplained substitute task record;
- `GEOX_CERTIFIED_CALIBRATION_HANDOFF_SOURCE_FIXTURE_001`, including failed implementation, rejected review, correction, invalid blocked claim, supersession, and preserved branch evidence;
- the required MIP, MMM, and GeoX successful controls with the same evidence discipline as incidents.

Keep `GEOX_CERTIFIED_CALIBRATION_SOURCE_MANIFEST_001` as concurrent context only. Do not treat it as a completed failure or success.

### 2. Implement the full incident/control schema

Every incident and control record must include the original task's required fields, using explicit null or `unavailable` values where Git does not support a fact. At minimum include:

- repository and exact task or PR identity;
- base, authoring/authorization, implementation, rejected/reviewed, correction, blocked, merged, closure, and preserved-branch SHAs when applicable;
- prompt mode with evidence classification;
- risk tier and Git-derived scope size;
- changed paths and commit count;
- reported validation commands and counts, separated into GitHub-observed and locally reported evidence;
- exact first-pass and final disposition;
- correction-cycle count;
- observed failure modes;
- primary and contributing root causes;
- exact evidence repository, path, ref/SHA, and evidence classification;
- unavailable facts;
- counterfactual prevention/detection controls;
- confidence level and rationale.

A single generic path such as `docs/execution/LATEST_COMPLETION_REPORT.md` is not an adequate evidence pointer without repository and exact ref/SHA.

### 3. Rebuild causal attribution from exact evidence

Do not collapse distinct incidents or transfer a failure observed in one task to another without evidence. In particular, separately verify the first and second MIP thin-launcher attempts before assigning self-modifiable-oracle, lifecycle, or prompt/Git root causes.

For every material conclusion, distinguish:

- `git_observed`;
- `locally_reported`;
- `strong_inference`;
- `weak_inference`;
- `unavailable`.

The main report must cite exact matrix evidence IDs or exact Git items for each major causal claim.

### 4. Expand the main audit to the required analytical depth

The report must contain evidence-backed causal chains for authoring, execution, validation, review, correction, and disposition—not only a summary table and taxonomy list.

It must separately analyze:

- why invocation-only prompts did and did not help;
- why manually repeated full prompts also carry drift and cost risk;
- how self-modifiable acceptance tests produced false confidence;
- how duplicated lifecycle state created contradictions;
- how stale sibling pins and missing producer proof delayed blocker discovery;
- why ad hoc validation paths or invalid environment blockers occurred;
- why corrections optimized recent patches rather than replaying the frozen contract;
- which failures are system-design defects versus residual model variability;
- which control would prevent, detect, or merely reduce each incident.

### 5. Complete the solution and ROI model

For each of the five required options, record all originally required dimensions:

- problems addressed and not addressed;
- implementation components;
- engineering-effort range;
- migration effort separately for MIP, MMM, and GeoX;
- expected effect on wrong-path changes, stale dependency discovery, lifecycle contradictions, validation compliance, correction cycles, review time, repeated validation, and prompt/token repetition;
- operational risks;
- maintenance burden;
- reversibility;
- recommended status and rationale.

Conservative, base, and aggressive scenarios must contain consistent formulas, assumptions, implementation/maintenance cost, avoided-rework inputs, break-even conditions, and sensitivity. Do not present assumed task counts or avoided hours as observed measurements.

Pilot thresholds must separately cover all original dimensions, including correction cycles, repeated validation, and prompt-size reduction.

### 6. Correct the validation evidence

The prior claim that required-key/schema sanity passed is rejected because the JSON does not contain the required sample or record fields.

Before republishing, run a deterministic non-committed validator that asserts:

- every mandatory incident/context/control identity exists;
- task IDs are unique where required;
- all applicable SHA fields are either valid 40-character SHAs or explicitly unavailable;
- every incident/control contains all required keys;
- evidence classifications use the declared vocabulary;
- all five solution options contain every required dimension;
- conservative, base, and aggressive scenarios are present and ordered;
- the final verdict is one allowed value;
- the parked MIP blocker and active GeoX workstream remain preserved.

Record the exact command and result in the completion report. JSON parsing alone is insufficient.

### 7. Reverify live repository and coordination context

Before corrected publication, re-fetch MIP, MMM, and GeoX mains and execution files. Preserve the parked MIP P2 blocker, current GeoX producer task, MMM non-executable proposal, and producer-completion-versus-consumer-acceptance distinction.

Do not rewrite historical coordination state as current truth. Any live overlay must record the verification date, exact source SHAs, current task identities/statuses, and no-authority effect.

### 8. Publish a complete exact-tree report

The corrected completion report must state:

- exact corrected implementation SHA;
- exact final review head after receipt;
- exact incident, context, and control counts;
- exact changed paths;
- exact validation commands and results;
- GitHub-observed versus locally reported evidence;
- limitations and unavailable measurements;
- sibling impact and consumer-verification status;
- parked blocker and concurrent GeoX work;
- empty blockers only when all audit requirements pass;
- correction cycle used and remaining;
- task execution true, correction execution false after publication, merge/PR false, and capability authority unchanged.

Do not self-reference the future receipt head inside the commit creating it.

## Correction scope and authority

The correction may modify only the original eight owned paths:

1. `docs/audits/MIP_CROSS_REPOSITORY_CODEX_EXECUTION_ROOT_CAUSE_AND_ROI_AUDIT_001.md`
2. `docs/audits/archives/MIP_CROSS_REPOSITORY_CODEX_EXECUTION_ROOT_CAUSE_AND_ROI_AUDIT_001_incident_matrix.json`
3. `docs/audits/archives/MIP_CROSS_REPOSITORY_CODEX_EXECUTION_ROOT_CAUSE_AND_ROI_AUDIT_001_solution_roi.json`
4. `docs/program/CROSS_REPOSITORY_COORDINATION_STATE.json`
5. `docs/program/CROSS_REPOSITORY_COORDINATION_HISTORY.md`
6. `docs/execution/ACTIVE_TASK.md`
7. `docs/execution/EXECUTION_STATE.json`
8. `docs/execution/LATEST_COMPLETION_REPORT.md`

No sibling repository, execution standard, test, tool, product code, analytical code, fixture, runtime, workflow, PR, merge, pilot, production, or capability change is authorized.

## Validation and terminal state

Re-run the complete frozen Tier-2 audit gate plus the correction-specific deterministic validator on the final task-owned tree.

Publish one corrected implementation commit and one exact-tree receipt. Stop at a new remote `ready_for_review` head with correction authority false, merge and PR authority false, and local/remote equality.

A missing historical fact that Git genuinely cannot prove must be represented as unavailable with evidence limitations. It is not permission to omit a required record. Gaps in reasoning, schema completeness, incident coverage, or ROI analysis are unfinished work, not external blockers.

## Corrected publication result

- **Status:** `ready_for_review`
- **Corrected implementation SHA:** `c9134f0c036581290ef686ee7e5d1058055c952d`
- **Correction cycle:** `1 of 1` completed; no further correction execution is authorized.
- **Review boundary:** this is review evidence only. Merge, PR, sibling, product, analytical, runtime, pilot, production, and capability authority remain false.
- **Historical review evidence:** rejected head `9794085ad55014b4c104ccce74f9bbd87a255049` and rejected implementation `26f6a2e8d9d2fa64a5a095113feb7458d90945f2` remain preserved for the reviewer.
