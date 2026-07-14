# MIP Chat-First Demo UI Smoke Validation 001

**Artifact ID:** `MIP_CHAT_FIRST_DEMO_UI_SMOKE_VALIDATION_001`

**Status:** validated with Docker Ruff exception

**Implementation under validation:** `MIP_CHAT_FIRST_DEMO_UI_IMPLEMENTATION_001`

**Mode:** deterministic fixture-backed smoke validation only

## 1. Scope

This artifact validates the first chat-first demo UI implementation at a basic,
deterministic end-to-end level. It checks the implemented fixture loader, response
builder, canonical Streamlit import surface, visible safety panels, and lifecycle
metadata without launching a server or activating any provider, model, optimizer, or
GeoX execution path.

## 2. What was validated

- **Fixture loading:** the helper loaded and cross-referenced `manifest.json`,
  `sample_questions.json`, `expected_answer_behavior.json`, and
  `lifecycle_walkthrough.json` from the SaaS subscriptions fixture.
- **Sample question rendering:** all six required categories are available: MMM
  readiness, GeoX readiness, grain compatibility, budget planning guardrail,
  calibration context, and data missingness.
- **Deterministic answer rendering:** fixture metadata produced the expected MMM
  readiness, GeoX readiness, grain compatibility, and budget guardrail answers.
- **Allowed claims panel:** the canonical tab exposes only fixture-backed readiness,
  grain/missing-data explanation, evidence/calibration context, blocked reason, and
  next-artifact information. Calibration context explicitly does not calibrate a live
  model or authorize ROI, lift, or recommendations.
- **Cannot-say / blocked-claims panel:** per-answer refusals and fixture-wide forbidden
  claims remain visible.
- **Next-required-artifact panel:** each deterministic answer renders the fixture's
  next dependency or an explicit none value.
- **Evidence inspected panel:** each answer renders its fixture-provided evidence list,
  while the readiness panel lists all four governed JSON inputs.
- **Lifecycle walkthrough panel:** available-now, blocked, and future-integration
  dependencies are exposed from the ten static lifecycle rows; the rows are displayed,
  not executed.
- **App/import smoke behavior:** `app.streamlit_app` imports without launching a server,
  and its canonical `main` and chat-first tab renderer are callable.

The executable smoke coverage is in
`tests/demo/test_chat_first_demo_ui_smoke_validation_001.py`.

## 3. Docker validation status

Docker validation was attempted via make validate-docker.

Docker validation executed; tests passed inside Docker; strict full-repo Ruff gate failed on known pre-existing lint debt. This is not reported as a full Docker validation pass.

The container used Python 3.11.13. Pytest completed with 2,374 passed and 5 skipped.
Ruff then reported the known 21 full-repo findings and exited nonzero. Because the
validation script is fail-fast, global mypy did not run inside Docker. Host validation
was not used as a substitute for the Docker result.

Host validation was reported separately. The prescribed `python -m pytest ...`
commands could not start because the host shell has no `python` executable. Equivalent
Poetry-environment commands passed: 11 smoke tests, 20 dataset regression tests, 10
targeted implementation-plan tests, 317 governance tests, and 2,391 full tests. Targeted
Ruff, targeted mypy, and global mypy also passed on the host.

## 4. Claim-safety result

Claim safety passed. The fixture and rendered deterministic answers continue to block:

- ROI and ROAS;
- channel and incremental contribution;
- budget recommendations and optimized spend;
- GeoX market/treatment-control assignment;
- GeoX lift and readout; and
- causal claims.

No numeric result, assignment, or recommendation is inferred from fixture data.

## 5. Boundary result

No new runtime execution paths were added. This artifact adds tests and documentation
only. It does not execute an LLM provider or prompt, fit MMM, consume an MMM export,
compute ROI/ROAS or channel contribution, run an optimizer/simulator, recommend a
budget, assign GeoX markets, compute GeoX lift/readout, ingest calibration signals at
runtime, generate a decision surface or recommendation contract, or add an uploaded
data workflow.

## 6. Recommended next artifact

`MIP_CHAT_FIRST_DEMO_UI_MANUAL_REVIEW_CHECKLIST_001`
