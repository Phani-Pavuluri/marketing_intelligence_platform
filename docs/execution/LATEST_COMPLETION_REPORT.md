# TASK_COMPLETION_REPORT_V2

## Identity

- **Task ID:** `MIP_INVOCATION_ONLY_CODEX_PROMPT_STANDARD_001`
- **Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
- **Base / authorization head:** `2904334247980e564409b7815c812572d80c8419` /
  `39abc3d66a80054b2b293a73f2dbeb690eb2304b`
- **Feature branch:** `docs/mip-invocation-only-codex-prompt-standard-001`
- **Implementation commit:** `2f1ec3efdd6f68d5c8097e534c869d982ab2d6ec`
- **Current decision:** `ready_for_review`

## Deliverables and acceptance results

Canonical MIP guidance now makes Codex prompts invocation-only. Execution and
correction prompts identify only the Git-authored operation. Merge prompts may
add only the exact externally approved remote head SHA. Durable scope, paths,
behavior, validation, workflow, authority, and stop conditions stay in Git;
missing Git instructions fail closed.

| Acceptance criterion | Result |
| --- | --- |
| Invocation-only rule in `AGENTS.md` | passed |
| Operative execution/correction/merge prompt contract | passed |
| Exact approved merge SHA remains the external fact | passed |
| Focused governance assertion and fail-closed behavior | passed |
| MMM/GeoX adoption remains separately authorized | passed |
| Capability authority changed | false |

## Validation evidence

| Validation category | Result |
| --- | --- |
| JSON parse | passed |
| Markdown/current-state consistency | passed |
| Task-authoring boundary | passed |
| Six owned paths; three implementation and three publication paths | passed |
| `git diff --check` | passed |
| `poetry run pytest -q tests/governance/test_repo_native_execution_handoff.py` | passed; 1 passed |
| Docker, Ruff, mypy, full suite | not_required for Tier 1 |
| Receipt trailers | passed |
| Local/remote receipt-head equality | pending publication; verified after push |

## Evidence and authority

- **GitHub-observed:** synchronized MIP main, authorization boundary, and
  feature scope.
- **Locally observed:** JSON, Markdown consistency, path checks, diff hygiene,
  and focused test.
- **Blockers / validation debt:** none for Tier 1.
- **Sibling impact:** MMM and GeoX were not modified; adoption and the current
  GeoX builder task remain deferred and unauthorized.
- **Authority impact:** no product, runtime, analytical, data, persistence,
  recommendation, pilot, production, or capability authority changed.
- **Merge readiness:** exact-head external review only; merge and PR false.
  `.codex/` and `docs/tasks/` remain local-only.
