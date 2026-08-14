# MIP Root README External-Review Clarity and Onboarding Polish — Authorized

- **Milestone:** `MIP_ROOT_README_EXTERNAL_REVIEW_CLARITY_AND_ONBOARDING_POLISH_001`
- **Current decision:** `authorized`
- **Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
- **Execution mode:** `branch_and_fast_forward`
- **Pre-authoring base:** `7c6708d602093d415c0063e8607c19cdaff4b9a5`
- **Authorization provenance:** `null` until metadata finalization
- **Feature branch:** `docs/mip-root-readme-external-review-clarity-and-onboarding-polish-001`
- **Risk tier:** Tier 1 — routine repository-local documentation
- **Compatibility/migration policy:** `not_applicable`
- **Unresolved execution-blocking design questions:** none

## Authorized outcome

Refine only the root README so a first-time reader can understand why MIP
exists, identify the business jobs it supports, follow its evidence-routing
model, see concrete decision journeys, understand its capability inventory, and
successfully try the deterministic product through verified hosted, local app,
API, package, CLI, and contributor-validation paths.

The work must simplify the top-level learning loop, distinguish user jobs from
process, replace the dense system visual with five stages and three paths, and
turn Demo and quick start into verified onboarding. Implementation owns only
`README.md` and changes no behavior or authority.

## Verified authoring inputs

Synchronized repository evidence establishes:

- Python `>=3.11,<4.0` and Poetry packaging in `pyproject.toml`;
- canonical Streamlit entrypoint `app/streamlit_app.py`;
- deterministic `mip-demo` and backward-compatible `mip-app` Poetry scripts;
- FastAPI `GET /health`, `GET /version`, and deterministic POST routes
  `/advisory/cold-start`, `/readiness/assess`, `/calibration/map`, and
  `/intake/overview`, with request contracts in `src/mip/service/contracts.py`;
- shared deterministic workflow functions in `src/mip/service/workflows.py`;
- repository commands `make validate-host`, `make validate`,
  `make validate-docker`, and `make validate-public-deployment`;
- a deterministic fixture-backed public UI with Measurement Copilot starter and
  sample-journey paths plus Advanced tools for advisory, readiness, calibration,
  profiling, and intake.

Execution must re-verify these surfaces and examples on the synchronized branch
before publishing them.

## Authorization provenance

The first authorization commit may contain `authorization_head_sha: null`
because it cannot embed its own Git SHA. One later metadata-only commit will
record that first commit as immutable authorization provenance. The finalized
feature-branch baseline must descend from it, and the intervening diff may
contain only the three stable execution files. No README or implementation
change may occur before branch creation.

## Definition-ready evidence

- One primary, independently reviewable README front-door usability outcome is
  defined.
- Exact section roles, learning-loop semantics, five-stage system visual,
  onboarding surfaces, examples, boundaries, and failure semantics are in
  `ACTIVE_TASK.md`.
- Owned and prohibited paths and the focused Tier-1 validation gate are explicit.
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

The previous README task remains merged and closed. The P2 sequence is
unchanged; the parked MIP GeoX/MMM bridge remains blocked; and
`GEOX_MAIN_TEST_ISOLATION_AND_CHECKPOINT_CONTEXT_RECOVERY_001` remains next
eligible and unauthorized.

`README.md` has not been modified during this authoring session. No PR or merge
has been created.
