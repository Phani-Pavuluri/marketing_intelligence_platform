# MIP Root README Information Architecture Refresh — Authorization

- **Milestone:** `MIP_ROOT_README_INFORMATION_ARCHITECTURE_REFRESH_001`
- **Current decision:** `authorized`
- **Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
- **Pre-authoring base:** `a293ce52a813709ca624332123019139928cc51e`
- **Authorization provenance:** `81b4d9934e59f8fd1bbe70e48d61cc2c199967d0`
- **Feature branch:** `docs/mip-root-readme-information-architecture-refresh-001`
- **Risk tier:** Tier 1
- **Compatibility/migration policy:** `not_applicable`
- **Implementation:** none
- **Task execution:** authorized
- **Correction, merge, and PR authority:** false
- **Capability authority:** unchanged

## Authorized outcome

Rewrite only the root `README.md` as MIP's progressively layered front door:
product definition, problem, user outcomes, governed workflow, example decision
journey, three-repository authority model, capability overview, LLM boundaries,
current implementation state, demo/quick start, differentiation, and canonical
documentation navigation.

The implementation must replace the current long phase ledger with a shorter,
capability-oriented narrative while preserving verified technical depth,
hosted-demo access, real local entrypoints, current maturity labels, and the
sole-authority invariants for `TrustReport`, `CalibrationSignal`, and full-panel
Δμ.

## Authorization provenance and branch baseline

The first task-contract commit,
`81b4d9934e59f8fd1bbe70e48d61cc2c199967d0`, is immutable
`authorization_head_sha` provenance. Because a Git commit cannot contain its
own SHA, that initial authorization record contained a null self-reference.
This subsequent metadata-only finalization records the first commit SHA.

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
contract, governance-standard, roadmap, P2 ledger, coordination, sibling, or
analytical surface is changed.

## Validation classification

- `python3 -m json.tool docs/execution/EXECUTION_STATE.json >/dev/null`:
  passed.
- `poetry run pytest -q tests/governance/test_repo_native_execution_handoff.py tests/test_cross_repository_coordination_control_plane.py`:
  passed, `2 passed in 0.01s`.
- `git diff --check`: passed.
- Authoring-boundary diff: passed; only the three stable execution files differ
  from immutable authorization provenance during metadata finalization.
- Full pytest, Ruff, mypy, and Docker `make validate`: `not_required` for this
  Tier-1 metadata authoring session.
- README/link/entrypoint tests: deferred to task execution because no README
  implementation exists yet.

## Authority and sequencing

The P2 capability sequence is unchanged. The next eligible GeoX milestone
remains `GEOX_MAIN_TEST_ISOLATION_AND_CHECKPOINT_CONTEXT_RECOVERY_001` and
remains unauthorized. GeoX certification, MMM implementation, the parked MIP
bridge, `CalibrationSignal`, simulation, optimization, planning,
recommendations, runtime integration, real data, pilot, and production remain
unauthorized. Sibling repositories remain read-only; no coordination refresh is
authorized.

No PR, merge, squash, rebase, force-push, cherry-pick, or merge commit is
authorized or created by task authoring.
