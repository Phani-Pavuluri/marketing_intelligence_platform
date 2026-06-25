# Platform Critical Invariants and Golden Scenarios

Final roadmap addendum covering **critical platform invariants, golden end-to-end scenarios, demo artifacts, conformance testing, and execution sequencing**.

Complements:

- [LLM Decision Layer Roadmap](./LLM_DECISION_LAYER_ROADMAP.md) — phased delivery including static sibling export bridge (8B–8F)
- [Platform Completion Gaps Roadmap](./PLATFORM_COMPLETION_GAPS_ROADMAP.md) — P1–P13 lifecycle, audit, certification (when merged)
- [Platform Semantic and Decision Readiness Roadmap](./PLATFORM_SEMANTIC_AND_DECISION_READINESS_ROADMAP.md) — S1–S12 metrics, estimands, scope, decision packets (when merged)
- [MIP Sibling Export Producer Spec](../integrations/MIP_SIBLING_EXPORT_PRODUCER_SPEC.md) — thin governance envelope

**After this addendum, stop adding roadmap layers.** The next implementation phase is LLM Explanation Payload Contract + Usage Policy + Diagnostic Taxonomy (Phases 8G–8H).

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

## 2. Required platform decisions

1. **Structurally valid exports are not sufficient for decision guidance.**
2. **LLM explanations** require explanation payload, usage policy, diagnostics, grounding, and `TrustReport` status.
3. **Decision packets** require semantic completeness, evidence alignment, uncertainty, approval state, and safe wording.
4. **Readiness may not be silently upgraded** by adapters, UI, LLM, or downstream workflow steps.
5. **Live engine execution remains blocked** until golden scenarios and safety evaluations exist.
6. **Optimizer-backed recommendations remain blocked** until decision-surface certification and optimizer governance are implemented.

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

## 5. Relationship to other roadmap layers

| Layer | Proves |
|-------|--------|
| **8B–8F** | Safe static ingestion |
| **8G–8N** | Safe LLM behavior |
| **P1–P13** | Durable platform operations |
| **S1–S12** | Semantic correctness |
| **G1–G10** (this doc) | **End-to-end product behavior** |
| **I1–I15** | **Conversational intake → data handoff workflow** |

Together these layers move MIP from a collection of safe components to a **proven causal marketing intelligence platform** with a governed intake-to-execution workflow.

## 6. Next implementation phase

Do not add further governance roadmap addenda without product need. Implement next:

1. **I1–I3** — `MMMIntakeSession`, `IntakePlan`, `RequiredDataAsset` (see [intake roadmap](./CONVERSATIONAL_INTAKE_AND_DATA_HANDOFF_ROADMAP.md))
2. **Phase 8G** — LLM explanation payload contract
3. **Phase 8H** — Usage policy + diagnostic taxonomy

Golden scenarios (G1) and conformance suite (G3) follow once explanation and usage contracts exist.

## 7. Related documents

- [LLM_DECISION_LAYER_ROADMAP.md](./LLM_DECISION_LAYER_ROADMAP.md)
- [PLATFORM_COMPLETION_GAPS_ROADMAP.md](./PLATFORM_COMPLETION_GAPS_ROADMAP.md)
- [PLATFORM_SEMANTIC_AND_DECISION_READINESS_ROADMAP.md](./PLATFORM_SEMANTIC_AND_DECISION_READINESS_ROADMAP.md)
- [CONVERSATIONAL_INTAKE_AND_DATA_HANDOFF_ROADMAP.md](./CONVERSATIONAL_INTAKE_AND_DATA_HANDOFF_ROADMAP.md)
- [REPO_INTEGRATION_STRATEGY.md](../architecture/REPO_INTEGRATION_STRATEGY.md)
- [AGENTIC_WORKFLOW_GOVERNANCE_ROADMAP.md](../architecture/AGENTIC_WORKFLOW_GOVERNANCE_ROADMAP.md)
- [MIP_SIBLING_EXPORT_PRODUCER_SPEC.md](../integrations/MIP_SIBLING_EXPORT_PRODUCER_SPEC.md)
