# MIP Chat-First Demo UI Manual Review Checklist 001

**Artifact ID:** `MIP_CHAT_FIRST_DEMO_UI_MANUAL_REVIEW_CHECKLIST_001`

**Status:** ready for reviewer use

**Review surface:** deterministic SaaS subscriptions chat-first demo

## 1. Scope

This artifact defines a human manual review checklist for the chat-first demo UI. It
validates the human-visible demo flow from local launch through deterministic answers,
claim guardrails, evidence, and lifecycle context.

This checklist does not implement features, does not replace automated smoke tests,
and does not authorize production claims. A completed checklist records what a human
reviewer observed; it does not expand what MIP is allowed to say.

## 2. Preconditions

Confirm these artifacts are complete before review:

- [ ] `MIP_DEMO_DOMAIN_DATASETS_001`
- [ ] `MIP_MMM_LLM_RESPONSE_VERIFIER_AUDIT_001`
- [ ] `MIP_DEMO_ONBOARDING_AND_USE_CASE_GUIDE_001`
- [ ] `MIP_CHAT_FIRST_DEMO_UI_DESIGN_PLAN_001`
- [ ] `MIP_CHAT_FIRST_DEMO_UI_IMPLEMENTATION_PLAN_001`
- [ ] `MIP_CHAT_FIRST_DEMO_UI_IMPLEMENTATION_001`
- [ ] `MIP_CHAT_FIRST_DEMO_UI_SMOKE_VALIDATION_001`

Confirm the reviewed history contains these commits:

- [ ] `1662b92` — demo domain datasets
- [ ] `0430e07` — MMM LLM response verifier audit
- [ ] `fccb2fe` — demo onboarding guide
- [ ] `5616ac9` — chat-first UI design plan
- [ ] `ecec3e5` — chat-first UI implementation plan
- [ ] `95c3ded` — chat-first UI smoke validation

## 3. Local launch checklist

From the repository root, prepare the reviewed revision:

```bash
git switch main
git pull --ff-only origin main
poetry install
```

Repository inspection confirms this canonical app entrypoint:

```bash
poetry run streamlit run app/streamlit_app.py
```

- [ ] Record the commit shown by `git rev-parse HEAD`.
- [ ] Run the confirmed command above; do not substitute an unverified entrypoint.
- [ ] Record the local URL printed by Streamlit.
- [ ] Open the URL and confirm the initial page finishes rendering.
- [ ] Record every warning or error shown in the terminal and browser.

## 4. Demo entry checklist

- [ ] The app opens without a crash.
- [ ] The page/header identifies **Marketing Intelligence Platform**.
- [ ] The **Chat-first SaaS demo** area is visible.
- [ ] The SaaS subscriptions demo is visible or selected.
- [ ] The fixture identity `saas_subscriptions_demo_v1` or fixture path
  `data/demo/domain_fixtures/saas_subscriptions/v1/` is clear.
- [ ] No uploaded-data workflow is required to use this demo.
- [ ] No provider or API key is requested.

## 5. Sample question checklist

Confirm the sample-question selector exposes these categories:

- [ ] `mmm_readiness`
- [ ] `geox_readiness`
- [ ] `grain_compatibility`
- [ ] `budget_planning_guardrail`
- [ ] `calibration_context`
- [ ] `data_missingness`

Select every example and wait for its deterministic answer:

- [ ] “Can this dataset support MMM readiness?”
- [ ] “What data is missing for MMM?”
- [ ] “Can I run a DMA-level GeoX experiment for Meta?”
- [ ] “Explain the grain difference between raw spend and KPI.”
- [ ] “Can I use this to recommend a budget shift next quarter?”
- [ ] “What does the calibration signal let me say?”
- [ ] “What can you safely say from this data?”
- [ ] “What can you not say yet?”

## 6. Expected answer checklist

For each selected question, confirm:

- [ ] The answer is labeled deterministic or fixture-backed.
- [ ] The answer remains identical when the same question is selected again.
- [ ] The readiness or refusal explanation is understandable to a non-engineering user.
- [ ] Allowed claims are clearly separated from cannot-say or blocked claims.
- [ ] The next required artifact is shown whenever a requested result is blocked.
- [ ] Evidence inspected is visible and names fixture-backed evidence.
- [ ] No invented numeric ROI, ROAS, contribution, lift, assignment, or optimized-spend
  result appears.

## 7. Claim-safety checklist

Confirm the UI refuses, blocks, or explicitly defers every item below:

- [ ] channel ROI
- [ ] ROAS
- [ ] incremental contribution
- [ ] channel contribution
- [ ] budget shift recommendation
- [ ] future spend recommendation
- [ ] optimized spend
- [ ] MMM model fit result
- [ ] MMM posterior/effect result
- [ ] GeoX treatment/control assignment
- [ ] GeoX lift
- [ ] GeoX readout
- [ ] causal claim

A readiness statement is not permission to infer any item above. Mark the review failed
if an answer supplies, implies, or recommends one without its required governed future
artifact.

## 8. Panel checklist

- [ ] Sample question area is visible and selectable.
- [ ] Deterministic answer panel is visible.
- [ ] Allowed claims panel is visible.
- [ ] Cannot-say / blocked-claims panel is visible.
- [ ] Next-required-artifact panel is visible.
- [ ] Evidence inspected panel is visible.
- [ ] Lifecycle walkthrough panel is visible and expandable.

## 9. Lifecycle walkthrough checklist

Expand **Full MMM + GeoX lifecycle walkthrough** and confirm it includes:

1. [ ] Select demo dataset.
2. [ ] Inspect raw spend and KPI grain.
3. [ ] Use canonical MMM-ready panel.
4. [ ] Evaluate MMM readiness.
5. [ ] Ask for channel ROI.
6. [ ] Ask for budget shift.
7. [ ] Evaluate GeoX readiness.
8. [ ] Ask for GeoX assignment.
9. [ ] Review calibration context.
10. [ ] Explain full MMM + GeoX lifecycle.

For each row, review the displayed status columns and next-artifact value. Confirm the
row is identifiable as **available now**, **fixture-backed**, **blocked**, or dependent
on a **future integration**. A future integration is explanatory only and must not
display a generated result.

## 10. No-runtime-execution checklist

During the complete review, confirm there is no evidence of:

- [ ] LLM provider execution
- [ ] prompt execution
- [ ] MMM fitting
- [ ] MMM export adapter execution
- [ ] ROI/ROAS computation
- [ ] channel contribution computation
- [ ] optimizer/simulator execution
- [ ] budget recommendation generation
- [ ] GeoX assignment
- [ ] GeoX lift/readout
- [ ] uploaded-data workflow

The expected path reads static fixture metadata and renders it. Network/provider
requests, model progress, optimizer progress, generated assignments, or computed causal
results are failures of this review boundary.

## 11. Docker validation checklist

Run Docker validation independently of the UI review:

```bash
docker version
docker info
docker ps
make validate-docker
```

- [ ] Record Docker client/server availability.
- [ ] Record the Python version printed inside Docker.
- [ ] Record Docker pytest, Ruff, and mypy results separately.
- [ ] Record the exact `make validate-docker` exit status.
- [ ] Confirm no host result was substituted for the Docker result.

Required reporting language:

- If `make validate-docker` exits 0: “Docker validation passed.”
- If it exits nonzero only due to known full-repo Ruff debt: “Docker validation
  executed; tests passed inside Docker; strict full-repo Ruff gate failed on known
  pre-existing lint debt. This is not a full Docker validation pass.”

Do not report host validation as Docker validation. Docker pass cannot be claimed
unless `make validate-docker` exits 0.

## 12. Manual review result template

Copy and complete this template without deleting failed or unknown fields:

```markdown
## Manual review result

Reviewer:
Date:
Commit reviewed:
Environment:
Local URL:

### Launch
- App launched: yes/no
- Entry command used:
- Errors:

### Demo flow
- SaaS demo visible: yes/no
- Sample questions visible: yes/no
- Deterministic answers render: yes/no
- Evidence panel visible: yes/no
- Lifecycle panel visible: yes/no

### Claim safety
- ROI/ROAS blocked: yes/no
- Budget recommendation blocked: yes/no
- GeoX assignment/lift blocked: yes/no
- No causal claims overexposed: yes/no

### Docker validation
- Docker daemon available: yes/no
- `make validate-docker` result:
- Docker tests:
- Docker Ruff:
- Docker mypy:
- Host fallback used: yes/no

### Verdict
- Pass / pass with known limitations / fail
- Notes:
```

## 13. Pass/fail criteria

Pass requires all of the following:

- the app launches;
- the SaaS demo is visible;
- all sample questions are visible;
- deterministic answers render;
- blocked claims are visible;
- evidence and lifecycle panels are visible;
- no provider, model, optimizer, or GeoX runtime execution path is invoked; and
- Docker validation is attempted and reported honestly.

Fail if any of the following occurs:

- the app crashes;
- sample questions are unavailable;
- blocked claims are hidden;
- the UI invents ROI, ROAS, lift, contribution, assignment, or recommendations;
- provider, model, optimizer, or GeoX runtime execution occurs; or
- Docker status is misreported.

A known unrelated full-repo Ruff failure may support “pass with known limitations” for
the manual UI review only. It is never a full Docker validation pass.

## 14. Recommended next artifact

`MIP_CHAT_FIRST_DEMO_UI_RELEASE_READINESS_AUDIT_001`

That audit should decide whether the demo is ready for external/user-facing release or
still needs narrowly scoped UI fixes.
