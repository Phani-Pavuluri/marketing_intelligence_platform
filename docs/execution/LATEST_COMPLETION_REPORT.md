# MIP Root README Narrative Flow Polish — Authorized

- **Milestone:** `MIP_ROOT_README_NARRATIVE_FLOW_POLISH_001`
- **Current decision:** `authorized`
- **Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
- **Execution mode:** `branch_and_fast_forward`
- **Pre-authoring base:** `ebe2aae41433bf315f0da999c498d65c92e0030d`
- **Authorization provenance:** `null` until metadata finalization
- **Feature branch:** `docs/mip-root-readme-narrative-flow-polish-001`
- **Risk tier:** Tier 1 — routine repository-local documentation
- **Compatibility/migration policy:** `not_applicable`
- **Unresolved execution-blocking design questions:** none

## Authorized outcome

Polish only the root README's opening product definition, causal-learning
transition and visual, high-level system-flow visual, four representative
journeys, and ordered capability table. Preserve the existing section-level
information architecture and make only local consistency edits elsewhere.

The task owns only `README.md` for implementation. It must make the MMM →
uncertainty → targeted experiment → compatible governed evidence → MMM-owned
calibration → planning → next-gap loop explicit, while preserving analytical
and trust authority boundaries.

## Authorization provenance

The first authorization commit may contain `authorization_head_sha: null`
because it cannot embed its own Git SHA. One later metadata-only commit will
record that first commit as immutable authorization provenance. The finalized
feature-branch baseline must descend from it, and the intervening diff may
contain only the three stable execution files. No README or implementation
change may occur before branch creation.

## Definition-ready evidence

- One primary, independently reviewable Markdown outcome is defined.
- Exact opening, loop, system-flow, journey, and capability-order behavior is
  specified in `ACTIVE_TASK.md`.
- Owned and prohibited paths, factual invariants, failure semantics, and the
  focused Tier-1 validation gate are explicit.
- Compatibility/migration is `not_applicable`.
- Unresolved execution-blocking design questions: none.
- One correction cycle is available.

## Authoring boundary and validation

Only these files may change during task authoring:

- `docs/execution/ACTIVE_TASK.md`
- `docs/execution/EXECUTION_STATE.json`
- `docs/execution/LATEST_COMPLETION_REPORT.md`

Authoring validation requires JSON parsing, `git diff --check`, changed-path
verification, README unchanged verification, focused execution-state governance
tests, authorization ancestry, and local/remote equality after publication.
Full pytest, Ruff, mypy, and Docker-backed `make validate` are `not_required`
for this Tier-1 authoring-only metadata surface.

## Authority and program impact

Task execution is authorized only for the declared README outcome. Correction,
merge, and PR authority are false. Capability authorizations are unchanged.
No product, analytical, runtime, planning, recommendation, real-data, sibling,
coordination, capability, pilot, or production authority is granted.

The P2 sequence is unchanged. The parked MIP GeoX/MMM bridge remains blocked,
and `GEOX_MAIN_TEST_ISOLATION_AND_CHECKPOINT_CONTEXT_RECOVERY_001` remains next
eligible and unauthorized. GeoX certification, MMM implementation,
`CalibrationSignal` construction, simulation, optimization, planning, and
recommendations remain unauthorized.

`README.md` has not been modified during this authoring session. No PR or merge
has been created.
