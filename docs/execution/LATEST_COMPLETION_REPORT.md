# TASK_REVIEW_DECISION_V1

## Current decision

- **Current decision:** `changes_requested`
- **Task ID:** `MIP_CROSS_REPOSITORY_CODEX_EXECUTION_ROOT_CAUSE_AND_ROI_AUDIT_001`
- **Feature branch:** `docs/mip-cross-repository-codex-execution-root-cause-roi-audit-001-r1`
- **Rejected implementation SHA:** `26f6a2e8d9d2fa64a5a095113feb7458d90945f2`
- **Rejected review head:** `9794085ad55014b4c104ccce74f9bbd87a255049`
- **Correction decision:** one bounded correction cycle authorized
- **Capability authority:** unchanged

## GitHub-observed publication facts

Exact remote review established:

- MIP `main` remains `cda803790be15089412038ac33f2af8205b5e83f`.
- The rejected branch is exactly two commits ahead of that base and is fast-forwardable.
- The rejected range changes only the eight authorized paths.
- The implementation commit is `26f6a2e8d9d2fa64a5a095113feb7458d90945f2`.
- The publication receipt head is `9794085ad55014b4c104ccce74f9bbd87a255049`.
- No sibling repository, execution standard, product code, analytical code, test harness, tooling, workflow, or capability was changed.

These structural facts pass. They do not establish substantive audit acceptance.

## Rejection findings

### 1. Mandatory evidence sample is incomplete

The committed matrix contains six incident/context records and three controls, but omits required separately evidenced records, including:

- `MIP_GIT_AUTHORITATIVE_THIN_LAUNCHER_STANDARD_002`;
- `MMM_REPOSITORY_EXECUTION_PROTOCOL_ADOPTION_001` through initial rejection, correction, reviewed head, implementation, merge, and closure;
- historical MMM PR #19 as a distinct incident;
- `GEOX_CERTIFIED_CALIBRATION_HANDOFF_SOURCE_FIXTURE_001` through implementation failure, rejected review, correction, invalid blocked claim, supersession, and preserved branch.

The active GeoX source-manifest task is context only and cannot substitute for a required historical incident.

### 2. Incident and control records do not satisfy the frozen schema

Most records omit the required authorization and lifecycle SHAs, prompt evidence, risk tier, scope size, changed paths, commit counts, validation commands/counts, first-pass disposition, observed failure modes, evidence classification, unavailable facts, counterfactual controls, and confidence rationale.

Generic paths without repository and exact ref/SHA are not sufficient Git evidence pointers.

### 3. Causal analysis is too compressed and partly unverified

The main report supplies a short comparison table and taxonomy but not the required evidence-backed causal chains across authoring, execution, validation, review, correction, and disposition.

Distinct MIP thin-launcher attempts are collapsed, making it impossible to verify whether self-modifiable-oracle and lifecycle failures are attributed to the correct task. Major claims do not point to exact matrix evidence IDs or exact Git items.

### 4. The ROI model is materially incomplete

The solution JSON lists option names, effort ranges, and statuses but omits the required per-option:

- problems addressed and not addressed;
- implementation components;
- per-repository migration effort;
- expected effects across all named operational metrics;
- risks, maintenance burden, reversibility, and rationale.

The three scenarios do not contain complete cost, maintenance, avoided-rework, break-even, or sensitivity formulas. Required thresholds for correction cycles, repeated validation, and prompt-size reduction are incomplete.

### 5. Reported schema validation is not accepted

The completion report states that required-key/schema sanity passed, but the committed matrix and ROI model visibly omit required identities and fields. Therefore the validator did not enforce the frozen contract, or the reported validation claim is inaccurate.

JSON parsing, owned paths, prohibited-path scanning, `git diff --check`, and documentation-only validation scope remain appropriate, but they do not cure missing semantic acceptance evidence.

## Current live context at review

- MIP `main`: `cda803790be15089412038ac33f2af8205b5e83f`.
- MMM `main`: `f2e0eade0ad917c1b28ab5521e6d35a35047d988`; its thin-launcher task remains proposed and non-executable.
- GeoX `main`: `7f829395bc305550ea1311421a4181dafed795b8`; `GEOX_CERTIFIED_CALIBRATION_SOURCE_MANIFEST_001` remains active producer work.
- MIP P2 blocker `BLOCK-P2-GEOX-MMM-CERTIFIED-PAIR-PROVENANCE-001` remains unresolved and parked.

No producer completion, consumer acceptance, product capability, or execution-tooling authority follows from this review.

## Required correction

The complete correction requirements are durable in `docs/execution/ACTIVE_TASK.md` on this branch. The frozen task contract at rejected head `9794085ad55014b4c104ccce74f9bbd87a255049` remains fully applicable.

The correction must complete the evidence sample, implement the full incident/control and ROI schemas, rebuild causal attribution from exact Git evidence, run a deterministic validator that enforces all required records and keys, reverify live coordination context, and publish a complete corrected exact-tree receipt.

## Correction authority and stop condition

One correction cycle is authorized on the same branch. Task execution and correction execution are true. Merge, PR, sibling, product, analytical, runtime, pilot, production, and capability authority remain false.

The correction must stop at a new remote `ready_for_review` head with correction authority turned off. No merge is authorized.
