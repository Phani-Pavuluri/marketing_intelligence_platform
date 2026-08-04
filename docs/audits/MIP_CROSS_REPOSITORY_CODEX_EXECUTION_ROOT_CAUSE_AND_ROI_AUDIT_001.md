# MIP Cross-Repository Codex Execution Root-Cause and ROI Audit 001

## Executive verdict

**Verdict: `proceed_with_bounded_pilot`.** The evidence supports a small,
repository-native control plane: one machine-readable task manifest, generated
task/prompt views, immutable policy checks outside task-owned paths, official
validation profiles, and atomic receipt/closure commands. It should be piloted
for six to eight tasks before wider adoption. This is not authorization to
implement the pilot, change execution standards, or change any product
capability.

## Orientation and method

This audit reads MIP Git history and live MMM/GeoX `origin/main` evidence. MIP
was observed at `cda803790be15089412038ac33f2af8205b5e83f`; MMM at
`f2e0eade0ad917c1b28ab5521e6d35a35047d988`; GeoX at
`7f829395bc305550ea1311421a4181dafed795b8`. Facts below are Git-observed
unless marked inference. Local validation counts and chat timing are unavailable
unless an execution report recorded them.

## Incident comparison and causal chains

| Repository | Incident | Observed disposition | Primary causes | Prevent/detect control |
|---|---|---|---|---|
| MIP | Thin-launcher standard 001 | superseded after rejected review | prompt/Git contradiction; self-modifiable test; lifecycle drift | immutable semantic oracle and generated canonical prompt |
| MIP | P2 GeoX/MMM bridge | blocked before implementation | preauthorization producer-pair proof absent | dependency resolver requiring paired certified provenance |
| MMM | protocol adoption / PR #19 history | external workflow bookkeeping debt | exact-head/closure evidence gap | atomic receipt and deterministic merge closure |
| MMM | thin-launcher adoption | non-executable stale proposal | stale upstream dependency evidence | live-overlay check at authorization and execution start |
| GeoX | branch-binding reauthoring | superseded after failed correction | correction anchored to patch, not frozen contract | immutable acceptance verifier and contract replay |
| GeoX | source-manifest task | active context only | not an incident or completion | exclude from conclusions until merged |

Successful controls exist in each repository: MIP coordination-control-plane
closure, MMM V2 reconciliation, and GeoX governed-readout fixture checkpoint.
They share bounded scope, exact evidence, and clear owner boundaries.

## Root-cause taxonomy

1. **Task-definition ambiguity/excessive scope:** prose allowed competing
   interpretations; inference is strong where review findings cite omitted
   contract requirements.
2. **Prompt/Git duplication:** observed in invocation-only versus thin-launcher
   wording; duplicated rules drifted.
3. **Prose-only and self-modifiable oracle:** tests accepted phrase presence or
   were changed with the behavior they judged; direct frozen-body checks were
   missing.
4. **Duplicated lifecycle state:** task, state, report, receipts, and branch
   topology could disagree without one atomic publication operation.
5. **Stale sibling evidence:** producer prerequisites were checked after, not
   before, MIP consumer authorization.
6. **Non-canonical validation/correction behavior:** local success did not
   demonstrate frozen semantic acceptance; corrections optimized recent diffs.
7. **Residual agent variability:** even complete controls do not eliminate
   reasoning mistakes; they make them fail closed earlier.

## Target operating model and alternatives

| Option | Addresses | Does not address | Effort | Recommendation |
|---|---|---|---|---|
| Full prompts + prose Git tasks | minimal change | drift, stale checks, self-modified oracle | 0–1 day | reject |
| Invocation-only + prose tasks | prompt repetition | ambiguous machine enforcement | 1–2 days | reject |
| Generated prompts from a manifest | duplication and prompt size | receipt/merge atomicity unless added | 3–5 days | candidate component |
| Bounded `taskctl` control plane | manifest, path/dependency checks, profiles, receipts, closure | human review and model variability | 8–15 engineer-days | **pilot** |
| External orchestration platform | centralized workflow | adds integration/maintenance burden | 20–40+ days | defer |

The minimum viable pilot is manifest parsing, immutable owned/prohibited path
checks, live sibling pin verification, named validation profiles, receipt
generation, and exact-head merge/closure helpers. Generated full prompts are
useful only when derived from the same manifest. CI, Git hooks, scheduler, and
external orchestration are not necessary for the pilot.

## ROI model and go/no-go criteria

No measured tokens, compute cost, or human minutes are in Git. Let `R` be
rework hours avoided per task, `V` be validation reruns avoided, `H` be review
hours avoided, and `C` be pilot implementation/maintenance hours. Net value is
`tasks × (R + H + V) − C`.

Conservative/base/aggressive assumptions: 6/12/20 tasks; 1/3/6 avoided hours
per task; 12/36/120 avoided validation runs. Break-even occurs when the avoided
review/rework time exceeds 8–15 implementation days plus one hour per task of
maintenance. Run a six-to-eight-task pilot and proceed only if: terminal state
is correct on at least 90% first publication; wrong-path changes are zero;
dependency proof and official validation profile are 100%; lifecycle
contradictions are zero; median corrections are at most one; review time falls
at least 25%; and generated prompts are materially shorter without reducing
acceptance coverage. Stop if controls merely add ceremony or fail to catch a
known class before publication.

## Product-workstream preservation

`MIP_P2_GEOX_MMM_COMPATIBILITY_FIXTURE_BRIDGE_001` remains parked at
`BLOCK-P2-GEOX-MMM-CERTIFIED-PAIR-PROVENANCE-001`; producer completion is not
consumer acceptance. GeoX's active
`GEOX_CERTIFIED_CALIBRATION_SOURCE_MANIFEST_001` remains producer-owned and
uncompleted. MMM's thin-launcher proposal remains non-executable. No audit
finding authorizes a sibling, product, runtime, data, simulation,
recommendation, pilot, or production capability.

## Limitations and unresolved questions

The sample contains execution metadata and Git history, not reliable token,
elapsed-time, or actual human-cost telemetry. Some historical GitHub review
details are unavailable from Git. The pilot hypothesis is therefore a strong
process inference, not measured causal proof. The remaining question is whether
the bounded manifest and immutable checker catch failures without creating a
larger workflow system; the proposed pilot is designed to answer that question.
