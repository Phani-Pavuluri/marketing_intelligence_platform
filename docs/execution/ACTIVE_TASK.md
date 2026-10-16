<!-- BEGIN MIP TASKCTL EXECUTION VIEW -->
# Active Task

**Status:** proposed

_Generated from `EXECUTION_STATE.json`; do not edit._

- **Task ID:** `MIP_DIAGNOSTIC_REVIEW_CHECKLIST_001`
- **Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
- **Execution mode:** `branch_and_fast_forward`
- **Base SHA:** `b0e7650718556316fa585ac9d9b953cdf9831efa`
- **Authorization provenance:** `null`
- **Feature branch:** `docs/mip-diagnostic-review-checklist-001`
- **Feature branch created:** `false`
- **Task execution authorized:** `false`
- **Correction execution authorized:** `false`
- **Merge authorized:** `false`
- **PR creation authorized:** `false`
- **Implementation commit:** `null`
- **Reviewed head:** `null`
- **Rejected review head:** `null`
- **Rejected implementation commit:** `null`
- **Approval commit:** `null`
- **Blockers:** `none`
- **Maximum correction cycles:** `1`
- **Correction cycles completed:** `0`
- **Correction cycles remaining:** `1`
- **Review decision:** `proposed`
- **Local feature-branch cleanup:** `null`
- **Remote feature-branch cleanup:** `null`
- **Capability authorizations changed:** `false`
<!-- END MIP TASKCTL EXECUTION VIEW -->

## One independently reviewable outcome

Publish docs/program/MIP_DIAGNOSTIC_REVIEW_CHECKLIST.md as a source-backed checklist for reviewing the published PROPOSED MMM diagnostic-curve definition against existing MIP consumer invariants. This is ordinary consumer-readiness documentation within the owner's existing coordination and reporting goals. It neither adopts the producer proposal nor adds executable acceptance policy. Muse owns content and approach; Codex reviews evidence.

## Observable behavior and boundaries

Each check names its review question, existing source rule, evidence required and a truthful mismatch/unknown result when unavailable. Cover quantity/units, scope and range, uncertainty availability, terminal failures/restrictions, provenance, diagnostic certification boundaries, and independence from calibration bridge prerequisites. Anchor existing rules to src/mip/contracts/enums.py, estimand.py, decision_surface.py and applicable envelope/report contracts. Read each referenced source before asserting a validator or field exists. Distinguish artifact types; do not require every diagnostic slope to become a causal quantity, assume different producer and consumer types interoperate, invent fields, or map units/semantics silently. A mismatch is recorded for the owning producer; the checklist does not resolve it.

Diagnostic curves cannot become certified decision evidence or replace full-panel delta-mu. Existing deterministic report claim prohibitions stay in force. Absent uncertainty stays unavailable; failure evidence never converts into success. A positive checklist result is documentation review only, never certification, contract adoption, parser support or executable compatibility. R12 is not a calibration-bridge prerequisite. Producer choices remain with their repository owners.

## Scope, dependencies and impact

Owned implementation is the one new checklist document plus the three stable execution files for native lifecycle/evidence. No navigation, code, tests, schema, parser, fixture, policy, ledger, historical snapshot, bridge, product or sibling changes. Modified MIP only; WS-MIP-DIAGNOSTIC-REVIEW-CHECKLIST-001; owner mip_consumer_acceptance_documentation. Preserve all parked blockers and protected authority.

Context live overlay: MMM proposal was published at e99768a8e43e020fe65a97e206a9e93101b364aa in docs/05_validation/mmm_response_surface_evidence_contract.md. It remains PROPOSED, with no contract adoption. GeoX callback repair is merged at 2ff493c884ac06aaf8359e349fc8008f1872528a, not producer certification. Reverify live source heads before publication and distinguish later ordinary task state from contract evidence. No shared snapshot refresh or sibling implementation is owned. Existing MIP consumer sources at base b0e7650718556316fa585ac9d9b953cdf9831efa are the checklist's normative references. No downstream blocker is resolved by publication.

## Acceptance, validation and publication

Tier 1 docs-only gate for execution, independent exact-tree review and pre/post-FF: all seven review families covered; each substantive rule has an exact resolving source path/pin; no invented fields or implicit adoption; unknowns/mismatches labeled; R12 and bridge separation explicit; source links verified against actual Git; taskctl check, JSON parsing, git diff --check, owned-path, ancestry and unchanged-authority checks. Required delegated receipt categories taskctl_check and git_diff_check need real logs tied to exact reviewed commit and Git tree. Full pytest/Docker/Ruff/mypy not_required for this docs-only surface. Existing activated delegated_routine route requires genuine native independent observer evidence, strict receipt and live eligible preflight; no new activation or per-head owner question for an eligible tree.

Use python -m mip.execution.taskctl for lifecycle/view changes. Freeze the exact tree, run its gate, publish a complete receipt with implementation parent, evidence, results, worktree and authority. Verify exact remote head and stop ready_for_review or genuine blocked. No merge, PR, history rewrite or successor execution. One correction cycle; compatibility/migration not_applicable. Deferred: any actual producer-contract adoption, runtime integration, schema/parser/fixtures, new analytical meaning or bridge execution. Unresolved execution-blocking design questions: none.
