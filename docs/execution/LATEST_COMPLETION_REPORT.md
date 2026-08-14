# MIP Root README Product Story Refinement — Authorization

- **Milestone:** `MIP_ROOT_README_PRODUCT_STORY_REFINEMENT_001`
- **Current decision:** `authorized`
- **Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
- **Pre-authoring base:** `fb3d4448c29eea5387e102777bf6bc1981ad6208`
- **Feature branch:** `docs/mip-root-readme-product-story-refinement-001`
- **Risk tier:** Tier 1
- **Compatibility/migration policy:** `not_applicable`
- **Implementation:** none
- **Task execution:** authorized
- **Correction, merge, and PR authority:** false
- **Capability authority:** unchanged

## Authorized outcome

Refine only the root README so the product and continuous causal-learning story
comes before implementation detail: marketing problem, GeoX/MMM learning loop,
progressive user outcomes, a marketer-friendly workflow visual, three short
decision journeys, capability purpose, the AI role, precise architecture/trust
boundaries, current maturity, demo access, and canonical documentation.

The rewrite must preserve factual maturity and the sole-authority invariants
for `TrustReport`, `CalibrationSignal`, and full-panel Δμ. It changes no product
behavior, architecture, program state, sibling repository, or authority.

## Authorization provenance and branch baseline

The first task-contract commit is immutable `authorization_head_sha`
provenance. Because a Git commit cannot contain its own SHA, this initial
authorization record temporarily leaves that field null. One subsequent
metadata-only commit must populate it with the first commit SHA.

The feature branch is created only after finalization, from synchronized final
`main`. Its starting head must descend from immutable authorization provenance,
and the intervening diff may contain only the three stable execution files.
The branch head is not the authorization identity, and implementation must not
rewrite authorization provenance.

## Authoring boundary

This authoring session may change only:

- `docs/execution/ACTIVE_TASK.md`
- `docs/execution/EXECUTION_STATE.json`
- `docs/execution/LATEST_COMPLETION_REPORT.md`

`README.md` is not modified during authoring. No product, source, test,
fixture, app, architecture, roadmap, P2 ledger, coordination, governance,
dependency, CI/Docker, data, or sibling surface is changed.

## Validation classification

- Metadata JSON parsing: required during finalization.
- Stable-file coherence/governance test: required during finalization.
- `git diff --check`: required during finalization.
- Authoring-boundary and README-unchanged checks: required during finalization.
- Full pytest, Ruff, mypy, and Docker `make validate`: `not_required` for this
  Tier-1 metadata-authoring session.
- README story/link/entrypoint tests: deferred to task execution because no
  README implementation exists yet.

## Authority and sequencing

The prior README information-architecture task is merged and closed. The P2
capability sequence is unchanged. The next eligible GeoX milestone remains
`GEOX_MAIN_TEST_ISOLATION_AND_CHECKPOINT_CONTEXT_RECOVERY_001` and remains
unauthorized. GeoX certification, MMM implementation, the parked MIP bridge,
`CalibrationSignal`, simulation, optimization, planning, recommendations,
runtime integration, real data, pilot, and production remain unauthorized.
Sibling repositories remain read-only; no coordination refresh is authorized.

No PR, merge, squash, rebase, force-push, cherry-pick, or merge commit is
authorized or created by task authoring.
