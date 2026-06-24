# Platform Critical Invariants and Golden Scenarios

Final roadmap addendum covering **critical platform invariants, golden end-to-end scenarios, demo artifacts, conformance testing, and execution sequencing**.

Complements:

- [LLM Decision Layer Roadmap](./LLM_DECISION_LAYER_ROADMAP.md) — phased delivery including static sibling export bridge (8B–8F)
- [Platform Completion Gaps Roadmap](./PLATFORM_COMPLETION_GAPS_ROADMAP.md) — P1–P13 lifecycle, audit, certification (when merged)
- [Platform Semantic and Decision Readiness Roadmap](./PLATFORM_SEMANTIC_AND_DECISION_READINESS_ROADMAP.md) — S1–S12 metrics, estimands, scope, decision packets (when merged)
- [MIP Sibling Export Producer Spec](../integrations/MIP_SIBLING_EXPORT_PRODUCER_SPEC.md) — thin governance envelope

**After this addendum, stop adding roadmap layers beyond artifact-selection policies (G11–G20).** The next implementation phase is LLM Explanation Payload Contract + Usage Policy + Diagnostic Taxonomy (Phases 8G–8H), with G11–G20 as design constraints.

## 1. Why this addendum exists

Previous roadmap tracks define:

- **Safety and governance** — contracts, gates, `TrustReport`, static export bridge
- **LLM reasoning** — explanation payloads, usage policy, question router (8G–8N, when specified)
- **Platform completion** — lifecycle, schema migration, audit (P1–P13, when specified)
- **Semantic correctness** — metrics, estimands, scope, decision packets (S1–S12, when specified)

This addendum defines the **critical invariants and golden scenarios** needed to **prove the platform works end-to-end**. Without them, individual modules may be correct while **product behavior remains unproven**.

### 1.1 Control plane vs execution engines

| Responsibility | MIP | MMM | panel_exp / GeoX |
|----------------|-----|-----|------------------|
| Product-level invariants | yes | no | no |
| Golden scenario tests | yes | provides demo exports | provides demo exports |
| Conformance suite rules | yes | runs in sibling CI | runs in sibling CI |
| Audit semantics | yes | run metadata only | run metadata only |
| Decision-readiness proof | yes | source diagnostics | source diagnostics |
| Statistical execution | no | yes | yes |

**Shared boundary:** contract conformance plus `TrustReport`-governed handoff.

### 1.2 Hard boundaries (unchanged)

This addendum is **documentation only**. No model execution, optimizer execution, sibling imports, path dependencies, subprocesses, LLM provider calls, production recommendations, or new runtime decision behavior.

### 1.3 Governance-valid vs answer-valid

**Governance-valid does not mean answer-valid.**

A structurally valid, registered artifact can still be the **wrong evidence** for the user's question. The LLM must not answer with the wrong artifact, wrong scope, stale result, superseded model, ambiguous metric, ambiguous estimand, or unsupported claim.

| Question type | Evidence requirements |
|---------------|----------------------|
| **Current performance** | Current, non-superseded, scope-matched, metric-matched, estimand-matched, non-blocked evidence |
| **Historical / trend** | Older artifacts allowed; must be labeled **historical** |
| **Decision / action** | Stricter evidence than diagnostic or explanation questions |

**Artifact selection rules:**

- The LLM must **never** select artifacts only because they are available in the registry.
- Selection must be governed by: user intent, time context, scope, metric, estimand, freshness, readiness, approval state, and `TrustReport` status.
- **Latest** means latest for the requested scope, metric, estimand, and artifact type—not globally latest.

## 2. Required platform decisions

1. **Structurally valid exports are not sufficient for decision guidance.**
2. **LLM explanations** require explanation payload, usage policy, diagnostics, grounding, and `TrustReport` status.
3. **Decision packets** require semantic completeness, evidence alignment, uncertainty, approval state, and safe wording.
4. **Readiness may not be silently upgraded** by adapters, UI, LLM, or downstream workflow steps.
5. **Live engine execution remains blocked** until golden scenarios and safety evaluations exist.
6. **Optimizer-backed recommendations remain blocked** until decision-surface certification and optimizer governance are implemented.
7. **The LLM must never answer current-performance questions** from historical, superseded, expired, blocked, or stale artifacts unless explicitly framed as historical context.
8. **The LLM must not infer scope, metric, or estimand** when multiple plausible artifacts exist.
9. **The LLM must distinguish** no result, inconclusive result, blocked result, stale result, and zero effect.
10. **The LLM must not answer counterfactual, forecast, budget, or curve-based planning questions** unless the artifact is certified for that use.
11. **Artifact selection must be scope-specific**, not globally latest.
12. **Claim-level readiness governs answers**; artifact-level validity is not enough.

## 3. Critical invariant and golden-scenario tracks

### Track G1 — Golden End-to-End Scenarios

**Why:** Unit tests validate modules. Golden scenarios validate **product behavior**.

**Required scenarios:**

| Scenario | Expected product behavior |
|----------|---------------------------|
| GeoX export → `EvidenceRegistry` → `TrustReport` → LLM explanation → safe next action | Grounded diagnostic summary; no invented lift |
| MMM export → `DecisionSurface` diagnostic → `TrustReport` blocked → remediation guidance | Cites blockers; suggests valid next checks |
| MMM + GeoX conflict → evidence comparison → no silent averaging → resolution path | Explains conflict; human-review path |
| User asks unsafe budget question → blocked / approval required | No autonomous recommendation |
| Old schema export → downgraded or blocked | Schema policy enforced |
| Stale calibration → no production recommendation | Downgrade or block with reason |
| Decision-ready artifact → approval-gated decision packet | Packet requires approval state |

**Ownership:**

- **MIP** owns golden scenarios and expected outcomes.
- **Sibling repos** provide conforming demo exports.

---

### Track G2 — Minimal Demo Artifacts

**Why:** Stable demos are needed for onboarding, Streamlit, CLI, scenario tests, regression tests, and documentation.

**Required demo artifacts:**

| Artifact | Purpose |
|----------|---------|
| Valid GeoX export | Happy-path experiment ingestion |
| Blocked GeoX export | Blocker explanation path |
| Valid MMM diagnostic export | Diagnostic-only MMM flow |
| Blocked MMM export | MMM blocker path |
| Stale calibration export | Calibration freshness gate |
| Conflicting MMM vs GeoX exports | Cross-evidence conflict |
| Schema-mismatch export | Schema downgrade/block |
| Metric-mismatch export | Semantic alignment failure |
| Estimand-mismatch export | Non-comparable evidence |
| Unsafe prompt examples | Red-team corpus (S8) |
| Decision-review packet example | Stakeholder artifact (S6/G9) |

**Ownership:**

- **MIP** owns demo fixture structure and expected behavior.
- **Sibling repos** may provide source examples later.

---

### Track G3 — Sibling Contract Conformance Suite

**Why:** MIP can be correct while sibling repos drift. The conformance suite prevents producer-side contract erosion.

**Conformance checks:**

| Check | When required |
|-------|---------------|
| Schema valid | Always |
| Required labels present | Always |
| `source_repo`, `engine_kind`, `artifact_kind` correct | Always |
| `source_commit_marker` present | Always |
| `export_schema_version` accepted | Always |
| No forbidden claims | Always |
| `metric_id` present | When explanation-ready |
| `estimand_id` present | When explanation-ready |
| Scope metadata present | When comparison-ready |
| `usage_policy` present | When LLM-guidance-ready |
| Diagnostics mapped to MIP codes | When diagnostic-ready |

**Ownership:**

- **MIP** owns conformance rules and test harness.
- **MMM and panel_exp** run conformance in their own CI or local validation before handoff.

---

### Track G4 — Backward / Forward Compatibility Policy

**Why:** Once multiple repos emit exports, version drift is unavoidable.

**Required policies:**

| Policy | Purpose |
|--------|---------|
| Accepted schema versions | Explicit allow list |
| Warn-only schema versions | Downgrade with warning |
| Blocked schema versions | Hard reject |
| Deprecated schema versions | Sunset path |
| Minimum schema by readiness level | Higher readiness requires newer schema |
| Migration notes | Human-readable change log |
| Never silently upgrade decision readiness | Tied to G6 invariant |

**Ownership:**

- **MIP** owns accepted schema versions and migration semantics.
- **Sibling repos** own producing current schema versions.

*Related:* Track P2 (platform completion).

---

### Track G5 — TrustReport Severity Normalization

**Why:** LLM, UI, workflows, approvals, and `TrustReport` need one consistent interpretation of severity across MMM, GeoX, data, calibration, exports, and approvals.

**Severity levels:**

| Level | Typical meaning |
|-------|-----------------|
| `info` | Informational; no action required |
| `warning` | Caution; may proceed with limits |
| `degraded` | Reduced confidence; not decision-ready |
| `blocked` | Must not proceed on this path |
| `requires_approval` | Human approval mandatory |
| `decision_ready` | Eligible for governed decision support |

**Per-severity future fields:**

`meaning` · `user_facing_wording` · `llm_response_mode` · `ui_display_behavior` · `blocks_decision` · `requires_approval` · `allowed_next_actions`

**Ownership:**

- **MIP** owns severity taxonomy.
- **Sibling repos** provide native diagnostics that map into MIP severity.

---

### Track G6 — No Silent Upgrade / No Silent Downgrade Invariant

**Why:** Prevents governance erosion as artifacts move through adapters, `TrustReport`, LLM explanations, UI, and decision packets.

**Core invariant:**

> Readiness can only become **stricter** automatically.
> Readiness can become **less strict** only through explicit gate evidence plus approval.

**Examples (must never happen silently):**

| Forbidden silent change |
|-------------------------|
| `diagnostic_only` → `decision_support` |
| `blocked` → `usable_with_caution` |
| `research_only` → `production_decision_ready` |
| `expired` evidence → `fresh` |
| `approval_required` → `approved` |

**Ownership:**

- **MIP** owns readiness monotonicity rules.
- **Sibling repos** declare source readiness but **cannot** elevate final MIP readiness.

---

### Track G7 — Local Persistence Plan

**Why:** If every run disappears after a Streamlit refresh, the platform cannot support audit, review, reproducibility, or decision history.

**Proposed local structure:**

```text
.mip/runs/
.mip/artifacts/
.mip/trust_reports/
.mip/approvals/
.mip/llm_answers/
.mip/decision_packets/
.mip/audit/
```

**Future records:**

`RunRecord` · `ArtifactRecord` · `TrustReportRecord` · `ApprovalRecord` · `LLMAnswerRecord` · `DecisionPacketRecord` · `AuditEvent`

**Ownership:**

- **MIP** owns local persistence semantics.
- **Sibling repos** provide source run IDs and export lineage.

*Related:* Track P9 (durable audit logging).

---

### Track G8 — Explanation Quality Rubric

**Why:** An answer can be safe but vague. The platform needs a standard for useful, trustworthy explanations.

**Quality dimensions:**

| Dimension | Pass criterion |
|-----------|----------------|
| Grounded | Cites artifact fields |
| Complete | Covers question scope without invention |
| Non-overclaiming | No ROI/lift/causal claims beyond tier |
| Audience-appropriate | Matches requested mode (S7) |
| Actionable | Suggests valid next checks when applicable |
| Mentions blockers | Surfaces `blocking_reasons` |
| Mentions uncertainty | Surfaces uncertainty summary |
| States allowed uses | From usage policy |
| States forbidden uses | From usage policy |
| Cites artifact fields | Grounding map (8J) |
| Respects `TrustReport` | Tier and verdict honored |

**Ownership:**

- **MIP** owns rubric and evaluation.
- LLM answers are tested against the rubric.

*Related:* Phase 8N (LLM evaluation harness).

---

### Track G9 — Decision Packet Acceptance Gate

**Why:** The platform's useful output is a governed **decision-review artifact**, not just a model result.

**Required gate conditions:**

| Condition | Purpose |
|-----------|---------|
| Business question defined | Framed stakeholder question |
| Metric and estimand aligned | S1/S2 semantic check |
| Scope/time window aligned | S3 alignment check |
| Evidence used and excluded listed | Transparency |
| `TrustReport` non-blocked for intended use | Trust gate |
| Uncertainty summarized | Risk communication |
| Risks summarized | Limitation communication |
| Blocked claims listed | Safe wording |
| Allowed claims listed | Supported claims only |
| Approval status known | S5/S6 gate |
| Recommended wording safe | Template check (S7) |
| Appendix diagnostics attached | Technical depth available |

**Ownership:**

- **MIP** owns decision packet gate and approval status.
- **MMM/GeoX** provide source evidence and diagnostics.

*Related:* Track S6 (decision review packet).

---

### Track G10 — Roadmap Dependency Graph

**Why:** The roadmap is now broad. A dependency graph prevents premature work on high-risk layers before foundations are ready.

**Initial dependency graph:**

```text
Sibling export producer specs (8F)
  → explanation payload contract (8G)
  → usage policy + diagnostic taxonomy (8H)
  → metric / estimand / scope contracts (S1–S3)
  → artifact selection + ambiguity policies (G11–G20)
  → export completeness scoring (S9)
  → question router / safe answer policy (8I)
  → grounding map (8J)
  → LLM evaluation harness (8N)
  → golden scenarios (G1)
  → decision review packet (S6 / G9)
  → optimizer governance (P7)
  → live engine execution consideration (explicitly gated)
```

**Ownership:**

- **MIP** owns roadmap sequencing and release gates.

---

### Track G11 — Temporal Result Selection + Current-State Policy

**Why:** A stale or superseded result can be more dangerous than no result because it sounds precise.

**User terms requiring resolution:** `current`, `latest`, `recent`, `historical`, `trend`, `previous`, `refreshed`, `last model`, `current model`.

**Required future fields:**

`artifact_time_window` · `created_at` · `source_run_at` · `published_at` · `valid_from` · `valid_until` · `freshness_status` · `is_current` · `is_latest_for_scope` · `supersedes` · `superseded_by` · `model_version` · `data_snapshot_id` · `reporting_period` · `refresh_cadence` · `historical_only`

**Rules:**

- If user asks **current**, use only current/latest non-superseded artifacts for the requested scope.
- If no current artifact exists, say current performance is unavailable; optionally show the most recent artifact as **historical context**.
- If user asks **recent**, use a configured recency window or latest completed reporting period—do not invent a window silently.
- If user asks **trend** or **compare over time**, historical artifacts are allowed but must be labeled historical.
- Never use superseded, expired, blocked, or stale artifacts for decision guidance unless the user explicitly asks about historical records.
- **Latest** means latest for scope, metric, estimand, and artifact type—not globally latest.

**Ownership:** **MIP** owns selection policy; sibling repos provide timestamps and lineage.

---

### Track G12 — Scope / Metric / Estimand Ambiguity Resolution

**Why:** The LLM can sound right while mixing different channels, products, geos, metrics, or estimands.

**Ambiguous question examples:** “How is Meta doing?” · “Did Display work?” · “What was ROI?” · “How are conversions doing?” · “What was lift?”

**Ambiguity dimensions:** channel · platform · campaign · market · geo · product · audience · metric · estimand · time window · artifact type · source system

**Rules:**

- If multiple artifacts match different scopes, ask for clarification or return a scoped comparison.
- If `metric_id` is missing or ambiguous, answer only at diagnostic level and request metric clarification.
- If `estimand_id` is missing or ambiguous, do not answer causal/performance claims.
- Do not collapse Meta/FB/Instagram/paid social or Display/programmatic/source-system channel names without canonical mapping.

**Ownership:** **MIP** owns ambiguity resolution; sibling repos tag exports with S1/S2/S3 metadata.

---

### Track G13 — Artifact Precedence + Comparability Gate

**Why:** Evidence comparison is only useful when compared artifacts mean the same thing.

**Precedence examples:**

| Question type | Prefer |
|---------------|--------|
| Experiment readout | Governed experiment evidence |
| Model planning | Certified MMM decision surfaces |
| Current decision guidance | Aligned, current, non-blocked evidence |
| Historical explanation | Older artifacts (labeled historical) |
| Conflict questions | Only artifacts passing comparability checks |

**Comparability dimensions:** KPI alignment · estimand alignment · time-window alignment · geo/channel/product/audience scope · spend/exposure definition · metric transformation alignment

**Rules:**

- Do not compare artifacts just because they mention the same channel.
- If not comparable, state which dimensions differ.
- Do not silently average conflicting evidence.
- If old and new conflict, prefer current for current-state questions; mention prior results only as history.

**Ownership:** **MIP** owns precedence and comparability gates.

---

### Track G14 — Claim-Level Governance

**Why:** An artifact may support some statements but not others.

**Examples:**

| Claim | Status |
|-------|--------|
| “Diagnostics passed.” | Allowed (if grounded) |
| “Experiment was underpowered.” | Allowed (if grounded) |
| “ROI is production-ready.” | Blocked |
| “Channel does not work.” | Blocked |
| “Lift is causal” | Blocked unless governed causal evidence supports it |

**Future fields:** `allowed_claims` · `blocked_claims` · `claim_scope` · `claim_evidence_required` · `claim_readiness` · `claim_expiration` · `claim_grounding_fields`

**Rules:**

- LLM may answer supported diagnostic claims while blocking unsupported decision claims from the same artifact.
- No downstream layer may upgrade a blocked claim without explicit gate evidence plus approval.

**Ownership:** **MIP** owns claim-level policy.

---

### Track G15 — Counterfactual / Forecast / Curve Eligibility Policy

**Why:** Users naturally turn diagnostics into counterfactual decisions unless the platform blocks that path.

**User examples:** “What if I increase spend 20%?” · “What if I cut Display?” · “What will happen next month?” · “Can we launch nationally?” · “Use the response curve for budget planning.”

**Rules:**

- Counterfactual answers require certified simulation or decision-surface support.
- Forecast answers require forecast-eligible artifacts; historical contribution is not a forecast.
- Diagnostic curves are not optimizer-eligible unless explicitly certified.
- Do not extrapolate beyond observed/calibrated spend support unless certified.
- If unsupported, provide limitation and required evidence instead of an answer.

**Ownership:** **MIP** owns eligibility policy; **MMM** owns surface/curve computation.

---

### Track G16 — Freshness Decomposition Policy

**Why:** “Fresh” is multi-dimensional; one timestamp must not imply all evidence is current.

**Separate freshness timestamps:**

`model_run_at` · `data_snapshot_at` · `calibration_signal_period` · `experiment_period` · `export_created_at` · `TrustReport_created_at` · `approval_created_at` · `approval_valid_until`

**Rules:**

- Freshly run model + stale calibration ≠ fully current.
- Fresh export + old data snapshot ≠ current for performance.
- Current `TrustReport` does not make stale source evidence fresh.
- Approval must apply to the artifact version and claim scope being used.

**Ownership:** **MIP** owns freshness interpretation; sibling repos provide source timestamps.

---

### Track G17 — External Validity + Support Guard

**Why:** Evidence can be valid in one context and invalid in another.

**Required concepts:** `valid_geos` · `valid_products` · `valid_channels` · `valid_audiences` · `valid_spend_range` · `observed_support_range` · `calibrated_support_range` · `transportability_notes` · `extrapolation_allowed`

**Rules:**

- Do not generalize a geo experiment globally unless transportability is certified.
- Do not use MMM curves outside supported spend range unless certified.
- Do not infer performance for unsupported products, audiences, or channels.

**Ownership:** **MIP** owns transportability policy; sibling repos declare support ranges.

---

### Track G18 — Primary Metric / Multiplicity / Exploratory Analysis Policy

**Why:** The LLM must avoid turning cherry-picked or exploratory evidence into confirmed findings.

**Future fields:** `primary_metric_id` · `secondary_metric_ids` · `guardrail_metric_ids` · `exploratory_metric_ids` · `number_of_tests` · `slice_selection_policy` · `pre_registered_primary_metric` · `exploratory_vs_confirmatory` · `multiplicity_adjustment`

**Rules:**

- Do not declare success from secondary/exploratory metrics if primary failed or is blocked.
- Do not overstate one significant slice when many slices were tested.
- Clearly label exploratory findings.
- Guardrail harms may block action even if primary metric is positive.

**Ownership:** **MIP** owns multiplicity policy; sibling repos declare metric roles.

---

### Track G19 — Answer Lineage + Best Available Evidence Policy

**Why:** Users need to know what evidence an answer is based on and what limitations apply.

**Required answer lineage:** `artifact_id` · `source_repo` · `source_commit_marker` · `model_version` · `data_snapshot_id` · `reporting_window` · `TrustReport_id` · `freshness_status` · `approval_status` · `grounding_fields`

**Rules:**

- Every LLM answer should be grounded in specific artifact fields.
- “Best available evidence” does not mean decision-ready.
- Best available evidence must list limitations.
- Blocked artifacts cannot be used for action guidance.
- If only historical evidence exists, label it historical.

**Ownership:** **MIP** owns answer lineage and best-available policy.

---

### Track G20 — Missing Evidence / No Result / Zero Effect Distinction

**Why:** No result, inconclusive result, and zero effect are different states with different business implications.

**States to distinguish:**

| State | Meaning |
|-------|---------|
| No artifact available | No governed result exists |
| Artifact blocked | Governance blocked use |
| Artifact stale | Outside freshness window |
| Artifact inconclusive | Insufficient signal |
| Artifact underpowered | Below MDE / power threshold |
| Effect estimated near zero | Governed estimate ≈ 0 |
| Negative effect | Governed negative estimate |
| Guardrail harm | Guardrail metric violated |

**Rules:**

- Do not say “no lift” when no governed result exists.
- Do not say “channel did not work” when evidence is inconclusive or underpowered.
- Do not equate missing evidence with zero effect.
- When evidence is missing, state what artifact/evidence is needed next.

**Ownership:** **MIP** owns state taxonomy and response policy.

## 4. Track summary

| Track | Focus |
|-------|--------|
| G1 | Golden end-to-end scenarios — product proof |
| G2 | Minimal demo artifacts — onboarding and regression |
| G3 | Sibling conformance suite — producer-side drift prevention |
| G4 | Schema compatibility policy — version drift |
| G5 | TrustReport severity normalization — consistent UX/LLM |
| G6 | No silent upgrade invariant — governance monotonicity |
| G7 | Local persistence plan — audit and reproducibility |
| G8 | Explanation quality rubric — useful LLM answers |
| G9 | Decision packet acceptance gate — stakeholder artifact |
| G10 | Roadmap dependency graph — sequencing discipline |
| G11 | Temporal result selection + current-state policy |
| G12 | Scope / metric / estimand ambiguity resolution |
| G13 | Artifact precedence + comparability gate |
| G14 | Claim-level governance |
| G15 | Counterfactual / forecast / curve eligibility |
| G16 | Freshness decomposition policy |
| G17 | External validity + support guard |
| G18 | Primary metric / multiplicity / exploratory policy |
| G19 | Answer lineage + best available evidence |
| G20 | Missing evidence / no result / zero effect distinction |

## 5. Relationship to other roadmap layers

| Layer | Proves |
|-------|--------|
| **8B–8F** | Safe static ingestion |
| **8G–8N** | Safe LLM behavior |
| **P1–P13** | Durable platform operations |
| **S1–S12** | Semantic correctness |
| **G1–G10** | End-to-end product behavior proof |
| **G11–G20** (this doc) | **Artifact selection, ambiguity, and answer-validity policies** |

Together these layers move MIP from a collection of safe components to a **proven, semantically correct causal marketing intelligence platform**.

## 6. Next implementation phase (final roadmap expansion)

**Do not add further roadmap addenda.** Implement next—with **G11–G20 as design constraints** for 8G/8H contracts:

1. **Phase 8G** — LLM explanation payload contract (include temporal, scope, freshness fields)
2. **Phase 8H** — Usage policy + diagnostic taxonomy (include claim-level and ambiguity rules)
3. Minimal fixtures and validation helpers reusing `load_sibling_fixture_export()` from 8B

Golden scenarios (G1) and conformance suite (G3) follow once explanation and usage contracts exist.

## 7. Related documents

- [LLM_DECISION_LAYER_ROADMAP.md](./LLM_DECISION_LAYER_ROADMAP.md)
- [PLATFORM_COMPLETION_GAPS_ROADMAP.md](./PLATFORM_COMPLETION_GAPS_ROADMAP.md)
- [PLATFORM_SEMANTIC_AND_DECISION_READINESS_ROADMAP.md](./PLATFORM_SEMANTIC_AND_DECISION_READINESS_ROADMAP.md)
- [REPO_INTEGRATION_STRATEGY.md](../architecture/REPO_INTEGRATION_STRATEGY.md)
- [AGENTIC_WORKFLOW_GOVERNANCE_ROADMAP.md](../architecture/AGENTIC_WORKFLOW_GOVERNANCE_ROADMAP.md)
- [MIP_SIBLING_EXPORT_PRODUCER_SPEC.md](../integrations/MIP_SIBLING_EXPORT_PRODUCER_SPEC.md)
