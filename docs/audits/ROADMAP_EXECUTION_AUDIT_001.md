# Roadmap Execution Consolidation Audit 001

**Status:** Complete (docs-only)  
**Base commit:** `1faf0cb` — Merge restore critical invariants G11–G20 sections  
**Date:** 2026-05-28

## Purpose

Consolidate the merged roadmap stack (8G–8N, P1–P13, S1–S12, G1–G20, I1–I15) into a single execution sequence. This audit answers what has been roadmapped, where concepts overlap, what is foundational vs later-stage, what blocks key capabilities, and what should be implemented next.

**Hard boundaries (unchanged):** No model execution, optimizer execution, sibling imports, subprocesses, LLM provider calls, production recommendations, Streamlit upload/connect implementation, or table connectors in this audit phase.

---

## 1. Roadmap inventory

### [LLM_DECISION_LAYER_ROADMAP.md](../roadmap/LLM_DECISION_LAYER_ROADMAP.md)

- Master phased delivery plan for the LLM Decision Layer and local workbench (Phases 0–11).
- **Implemented:** Phases 0–5D (safety, intake, readiness, configs, orchestrator, CLI, MockLLM, Streamlit shell), 6A–6C (adapters, governance, MMM fixture report), 7A–7C (manifest, router, approvals), 8A–8F (fixture engines, sibling export bridge, producer specs).
- **Documented, not implemented:** S1–S12, G1–G20, I1–I15 cross-references; 8G–8N LLM reasoning phases; live engine orchestration (Phase 8+), scenario workbench, governed recommendations.
- Anchors product vision to contract-driven workflows and blocks live engine execution until golden scenarios and 8G–8N exist.
- Primary index for what is **done vs planned** in the LLM layer.

### [LLM_REASONING_AND_MODEL_GUIDANCE_ROADMAP.md](../roadmap/LLM_REASONING_AND_MODEL_GUIDANCE_ROADMAP.md)

- Phases **8G–8N:** explanation payload, usage policy, question router, grounding map, remediation playbooks, evidence comparison, audience modes, LLM eval harness.
- Defines minimum contracts before live engine execution or advanced LLM analyst behavior.
- Incorporates **G11–G20** as design constraints for temporal selection, ambiguity, claim-level governance, and answer lineage.
- Producer writers in sibling repos should target richer explanation/usage contracts, not only the thin `SiblingFixtureExport` envelope.
- **Docs-only** until 8G contracts are implemented.

### [PLATFORM_COMPLETION_GAPS_ROADMAP.md](../roadmap/PLATFORM_COMPLETION_GAPS_ROADMAP.md)

- Tracks **P1–P13:** artifact lifecycle, schema migration, evidence readiness ladder, cross-evidence reconciliation, CalibrationSignal quality, decision-surface certification, optimizer governance, data contracts, audit logging, LLM answer audit, product workflows, security, package ergonomics.
- Positions MIP as durable control plane beyond ingestion and LLM explanation.
- **P11** overlaps with conversational intake (I1–I15); intake roadmap owns product workflow detail.
- **Docs-only**; foundational for production hardening and refresh governance.

### [PLATFORM_SEMANTIC_AND_DECISION_READINESS_ROADMAP.md](../roadmap/PLATFORM_SEMANTIC_AND_DECISION_READINESS_ROADMAP.md)

- Tracks **S1–S12:** metric/KPI registry, estimand registry, scope alignment, business action ontology, decision rights, decision review packet, explanation templates, red-team prompts, export completeness scoring, source-of-truth policy, failure-mode catalog, package release gates.
- **Prerequisites for G11–G20** artifact selection and **I6–I8** intake validation.
- Establishes: structurally valid exports ≠ decision-useful exports.
- **Docs-only**; S1–S3 are the first semantic implementation slice after intake session contracts.

### [PLATFORM_CRITICAL_INVARIANTS_AND_GOLDEN_SCENARIOS.md](../roadmap/PLATFORM_CRITICAL_INVARIANTS_AND_GOLDEN_SCENARIOS.md)

- Tracks **G1–G10:** golden scenarios, demo artifacts, conformance suite, schema policy, severity normalization, no-silent-upgrade, persistence, explanation rubric, decision packet gate, dependency graph.
- Tracks **G11–G20:** temporal selection, ambiguity resolution, comparability, claim-level governance, counterfactual eligibility, freshness decomposition, external validity, multiplicity, answer lineage, missing-vs-zero-effect distinction.
- Proves end-to-end product behavior; **governance-valid ≠ answer-valid**.
- Golden scenarios (G1) and conformance (G3) follow 8G–8H specification.

### [CONVERSATIONAL_INTAKE_AND_DATA_HANDOFF_ROADMAP.md](../roadmap/CONVERSATIONAL_INTAKE_AND_DATA_HANDOFF_ROADMAP.md)

- Tracks **I1–I15:** intake session, path recommendation, required data assets, source mode selection, manifest, column mapping, profiling, readiness report, CalibrationSignal mapping, Streamlit workflow, production connection, config/refresh handoff, audit trail, security, demo/production mode separation.
- Defines product workflow: LLM guides → MIP validates → sibling executes → MIP imports export.
- **First implementation:** I1–I3 only (session, plan, required assets)—no upload UI yet.
- Manifest is intake source of truth; readiness report is compatibility source of truth.

### [REPO_INTEGRATION_STRATEGY.md](../architecture/REPO_INTEGRATION_STRATEGY.md)

- Three-repo model: MIP (control plane), mmm, panel_exp/GeoX (engines).
- **Implemented:** 8A–8F read-only static export bridge; no sibling Python imports.
- **Blocked:** Live engine execution until 8G–8N minimally specified and golden scenarios exist.
- Adapters are thin field-mapping layers into `EvidenceRegistry` and `TrustReport`.

### [AGENTIC_WORKFLOW_GOVERNANCE_ROADMAP.md](../architecture/AGENTIC_WORKFLOW_GOVERNANCE_ROADMAP.md)

- Agentic behavior is advisory/routing only—not statistical computation or production automation.
- **Implemented:** 7A–7C manifest, router, approvals; 8A fixture orchestration; 8B–8F static bridge.
- Documents S1–S12, G1–G20, I1–I15 as governance layers above ingestion.
- Live engine adapters deferred until 8G–8N and golden scenarios.

---

## 2. Theme grouping

| Theme | Roadmap sources | Nature |
|-------|-----------------|--------|
| **T1 — Core semantic contracts** | S1–S3, S4–S5, S9–S10 | Foundational; blocks G11–G20 enforcement |
| **T2 — LLM-guided intake** | I1–I3, Phase 2 intake, 5C MockLLM | **Next implementation**; connects conversation to workflow |
| **T3 — Data source handoff and manifests** | I4–I5, P8, P9 | After intake contracts; manifest = source of truth |
| **T4 — Data compatibility/readiness** | I6–I8, Phase 3 readiness, S1–S3 | Profiling + semantic confirmation + readiness report |
| **T5 — CalibrationSignal/evidence intake** | I9, P5, ADR-002 | Governed experiment → MMM path only |
| **T6 — Artifact lifecycle and current-state selection** | P1, G11, G16, G19 | Blocks current-performance LLM answers |
| **T7 — LLM answer governance** | 8G–8N, G12–G14, G19–G20, P10 | Blocks safe current/historical answers |
| **T8 — Refresh governance** | I12, P1, P5, G11, G16 | Blocks model refresh promotion |
| **T9 — Streamlit/product workflow** | I10, I15, 5D shell, P11 | UI after contracts validated |
| **T10 — Golden scenarios/evaluation** | G1–G3, G8, 8N, P10 | Proves end-to-end product behavior |
| **T11 — Production hardening/security** | I11, I13–I14, P12, P9 | Production intake and audit |
| **T12 — Deferred live execution/optimizer** | Phase 8+, P6–P7, G15, ADR-001 | Explicitly deferred |

---

## 3. Overlap and canonical ownership

| Concept | Canonical owner | Also referenced in |
|---------|-----------------|----------------------|
| Metric / KPI / estimand / scope semantics | **Semantic roadmap (S1–S3)** | I6, G12, 8G payload fields |
| Current vs historical artifact selection | **Critical invariants (G11, G16)** | P1 lifecycle, 8G temporal fields |
| Upload / connect / manifest workflow | **Conversational intake (I4–I5, I11)** | P8 data contracts, P11 UX |
| Model refresh promotion | **Intake I12 + P1 + P5 + G16** | Refresh request handoff, freshness decomposition |
| LLM safe answering | **LLM reasoning (8G–8N) + critical invariants (G12–G20)** | P10 answer audit |
| Decision packet readiness | **Semantic S6 + critical invariants G9** | S7 templates, G8 rubric |
| Sibling repo handoff | **Repo integration strategy + 8F producer specs** | I4 sibling mode, G3 conformance |
| No silent readiness upgrade | **Critical invariants G6** | P3 evidence ladder, gates |
| Optimizer / budget recommendations | **Platform completion P6–P7 + G15** | ADR-001 Δμ estimand |
| Audit trail | **Intake I13 + platform completion P9** | G7 persistence |
| Demo vs production mode | **Intake I15** | P12 security, release gates |

**Deduplication rule:** When two roadmaps define the same concept, the **track-specific roadmap** owns detail; the LLM Decision Layer roadmap owns phase numbering and delivery status only.

---

## 4. Dependency graph

```text
[S1–S3] semantic registries (metric, estimand, scope)
  ↓
[I1–I3] intake session + path recommendation + required data assets
  ↓
[I4] data source mode selection (demo upload / local / table ref / sibling export)
  ↓
[I5] DataSourceRef + intake manifest                    ← P8 data contracts
  ↓
[I6] column mapping + semantic confirmation             ← S1–S3 IDs required
  ↓
[I7–I8] profiling + MMM readiness report                ← Phase 3 readiness extends
  ↓
[I9] CalibrationSignal intake mapping                   ← ADR-002, P5
  ↓
[I12] config draft + refresh request handoff
  ↓
[8F] sibling execution/export (external)                ← MMM/GeoX runs outside MIP
  ↓
[8B–8E] static export import + TrustReport
  ↓
[P1, G11, G16] artifact lifecycle + current-state selection
  ↓
[8G–8H] explanation payload + usage policy              ← G11–G20 constraints
  ↓
[8I–8J] question router + grounding map
  ↓
[G1, G3, 8N] golden scenarios + conformance + eval harness
  ↓
[S6, G9] decision review packet
  ↓
[P6–P7] decision-surface certification + optimizer governance
  ↓
[Phase 8+] live engine execution consideration (explicitly gated)
```

**Parallel foundations (can start after I1–I3 or in parallel with early intake):**

- **S1–S3** before I6/I8 semantic validation is strict
- **8G–8H** can be specified in parallel with I1–I5 but blocks LLM answers on artifacts
- **P9, I13** audit trail should attach once manifests exist

---

## 5. Blockers by capability

### LLM current-performance answers

**Blocked until:**

- Artifact lifecycle and supersession policy (**P1, G11**)
- Current-state vs historical selection rules (**G11**)
- Freshness decomposition (**G16**)
- `TrustReport` tier and severity normalization (**G5**, existing gates)
- Answer lineage and grounding (**G19, 8J**)
- Claim-level governance (**G14, 8H**)
- Explanation payload with temporal/scope fields (**8G**)
- Scope/metric/estimand disambiguation (**G12, S1–S3**)

### MMM refresh

**Blocked until:**

- Intake manifest with source lineage (**I5**)
- Readiness report gating refresh eligibility (**I8**)
- Refresh request contract (**I12**)
- Sibling export handoff (**8F**, external execution)
- Refresh comparison and promotion gate (**P1, P5, G16**)
- No silent upgrade invariant enforced (**G6**)

### Production data intake

**Blocked until:**

- `DataSourceRef` and governed manifest (**I5, P8**)
- Source ownership and schema validation (**I5, I7**)
- Snapshot ID and versioning (**P1, P2**)
- Security / filesystem policy (**I14, P12**)
- Conversation-to-manifest audit trail (**I13, P9**)
- Demo/production mode separation (**I15**)

### Budget / optimizer recommendations

**Blocked until:**

- Certified decision surface (**P6**)
- Optimizer governance and uncertainty policy (**P7**)
- Counterfactual eligibility rules (**G15**)
- Human approval workflow (**7C**, S5)
- Golden safety scenarios for unsafe budget questions (**G1**)
- Full-panel Δμ estimand alignment (**ADR-001, S2**)

### Live engine execution

**Blocked until:**

- Static export handoff proven (**8B–8F** — consumer side done; producer writers pending)
- Sibling conformance suite (**G3**)
- Golden end-to-end scenarios (**G1**)
- Refresh governance (**P1, I12, G16**)
- 8G–8N minimally specified
- Operational ownership and production signoff (**S12, release gates**)

---

## 6. Recommended implementation phases

Implementation phases below use **audit IDs (P0–P16)** to avoid confusion with platform-completion tracks **P1–P13**.

### P0 — Roadmap consolidation audit ✓

| Field | Value |
|-------|-------|
| **Goal** | Consolidate roadmap stack into execution sequence |
| **Files** | `docs/audits/ROADMAP_EXECUTION_AUDIT_001.md`, `docs/roadmap/ROADMAP_EXECUTION_SEQUENCE.md` |
| **Contracts/docs/tests** | Audit docs only |
| **Blocked capabilities** | None (meta) |
| **Acceptance** | Inventory, themes, ownership, dependency graph, phase plan, next-phase recommendation |
| **Runtime allowed** | None |

### P1 — Intake session and path recommendation contracts

| Field | Value |
|-------|-------|
| **Goal** | I1–I2: `MMMIntakeSession`, path recommendation helpers |
| **Files** | `src/mip/workflows/intake/`, `src/mip/contracts/`, `tests/workflows/intake/` |
| **Contracts** | `MMMIntakeSession`, `GeoXIntakeSession`, `IntakePathRecommendation` |
| **Blocked until done** | Structured LLM→workflow bridge, I3 planning |
| **Acceptance** | Pydantic contracts + fixtures + deterministic path rules; no LLM provider calls |
| **Runtime allowed** | Contract validation, fixture loading only |

### P2 — Required data assets and sample schema expectations

| Field | Value |
|-------|-------|
| **Goal** | I3: `IntakePlan`, `RequiredDataAsset` catalog |
| **Files** | `src/mip/workflows/intake/`, contracts, tests |
| **Contracts** | `IntakePlan`, `RequiredDataAsset`, sample schema expectations |
| **Blocked until done** | Manifest design, readiness asset checklist |
| **Acceptance** | Plan links session → required assets; fixtures for MMM minimum columns |
| **Runtime allowed** | Contract validation only |

### P3 — DataSourceRef and manifest contracts

| Field | Value |
|-------|-------|
| **Goal** | I5: governed intake manifest |
| **Files** | `src/mip/contracts/`, `src/mip/workflows/intake/` |
| **Contracts** | `DataSourceRef`, `IntakeManifest` |
| **Blocked until done** | Production intake, audit trail attachment |
| **Acceptance** | Manifest is source of truth; references mode from I4 |
| **Runtime allowed** | In-memory manifest records; no file I/O connectors |

### P4 — Column mapping and semantic confirmation contracts

| Field | Value |
|-------|-------|
| **Goal** | I6 + S1–S3 stubs |
| **Files** | contracts, `workflows/intake/`, semantic registry modules (new) |
| **Contracts** | `ColumnMappingProposal`, `SemanticConfirmation`; S1–S3 registry stubs |
| **Blocked until done** | Strict readiness semantic validation |
| **Acceptance** | Mapping references `metric_id`, `estimand_id`, scope metadata |
| **Runtime allowed** | Validation against registry fixtures |

### P5 — Data compatibility and MMM readiness report contracts

| Field | Value |
|-------|-------|
| **Goal** | I7–I8; extend Phase 3 readiness |
| **Files** | `src/mip/workflows/readiness/`, contracts, tests |
| **Contracts** | `DataCompatibilityReport`, `MMMDataReadinessReport` (governed extensions) |
| **Blocked until done** | Refresh eligibility, production intake signoff |
| **Acceptance** | Readiness report is compatibility source of truth |
| **Runtime allowed** | Profiling on fixture/local demo files only |

### P6 — CalibrationSignal intake mapping contracts

| Field | Value |
|-------|-------|
| **Goal** | I9; governed experiment evidence path |
| **Files** | `src/mip/contracts/calibration.py`, intake modules |
| **Contracts** | `CalibrationSignalIntakeMapping` |
| **Blocked until done** | MMM calibration from experiment exports |
| **Acceptance** | No raw experiment payloads; ADR-002 enforced |
| **Runtime allowed** | Mapping validation on fixtures |

### P7 — Streamlit intake shell with placeholders

| Field | Value |
|-------|-------|
| **Goal** | I10 panels wired to contracts (no upload implementation) |
| **Files** | `src/mip/app/streamlit_app.py`, tests |
| **Contracts** | UI displays session, plan, manifest placeholders |
| **Blocked until done** | Full product workflow |
| **Acceptance** | Shell shows governed labels; demo mode banner (I15) |
| **Runtime allowed** | Display only; no file upload handlers |

### P8 — Local/demo file profiling

| Field | Value |
|-------|-------|
| **Goal** | I4 demo upload path for sandbox only |
| **Files** | `workflows/readiness/`, app, tests |
| **Contracts** | Sandbox-labeled profiling pipeline |
| **Blocked until done** | Production intake |
| **Acceptance** | Demo mode only; audit event recorded |
| **Runtime allowed** | Local CSV read for profiling; sandbox labels required |

### P9 — Production manifest/table-reference design

| Field | Value |
|-------|-------|
| **Goal** | I11 design + P8/P12 policies |
| **Files** | docs + contracts (design-first) |
| **Contracts** | Table reference schema, ownership metadata |
| **Blocked until done** | Production decision support intake |
| **Acceptance** | Design doc + contract stubs; security review checklist |
| **Runtime allowed** | None (design phase) |

### P10 — Model refresh governance contracts

| Field | Value |
|-------|-------|
| **Goal** | I12 + P1 + P5 refresh promotion |
| **Files** | contracts, orchestration, docs |
| **Contracts** | `RefreshRequest`, `RefreshComparison`, promotion gate |
| **Blocked until done** | Automated refresh promotion |
| **Acceptance** | Refresh requires readiness + no silent upgrade (G6) |
| **Runtime allowed** | Contract validation; no model execution |

### P11 — Artifact lifecycle / current artifact selection

| Field | Value |
|-------|-------|
| **Goal** | P1 + G11 + G16 implementation |
| **Files** | `src/mip/evidence/`, contracts |
| **Contracts** | Lifecycle state machine, freshness fields, `is_current` |
| **Blocked until done** | LLM current-performance answers |
| **Acceptance** | Temporal selection rules enforceable on fixture exports |
| **Runtime allowed** | Registry metadata only |

### P12 — LLM answer governance and usage policy

| Field | Value |
|-------|-------|
| **Goal** | 8G–8H (+ 8I–8J minimum) |
| **Files** | `src/mip/llm/`, contracts, tests |
| **Contracts** | Explanation payload, usage policy, question router stubs |
| **Blocked until done** | Grounded current/historical LLM answers |
| **Acceptance** | G11–G20 constraints reflected in payload/policy fixtures |
| **Runtime allowed** | MockLLM + deterministic context only |

### P13 — Golden scenario evaluation harness

| Field | Value |
|-------|-------|
| **Goal** | G1–G3, G8, 8N |
| **Files** | `tests/`, `docs/`, evaluation modules |
| **Contracts** | Golden scenario fixtures, conformance suite, eval rubric |
| **Blocked until done** | Production signoff, live engine consideration |
| **Acceptance** | GeoX/MMM golden paths pass with fixture exports |
| **Runtime allowed** | Fixture-based tests only |

### P14 — Decision review packet contracts

| Field | Value |
|-------|-------|
| **Goal** | S6 + G9 |
| **Files** | contracts, trust, docs |
| **Contracts** | `DecisionReviewPacket`, acceptance gate |
| **Blocked until done** | Stakeholder decision artifacts |
| **Acceptance** | Gate conditions from G9 enforced in fixtures |
| **Runtime allowed** | Assembly from governed artifacts only |

### P15 — Optimizer governance (no execution)

| Field | Value |
|-------|-------|
| **Goal** | P6–P7 + G15 contracts only |
| **Files** | contracts, docs |
| **Contracts** | Decision-surface certification, optimizer policy, eligibility rules |
| **Blocked until done** | Budget recommendations |
| **Acceptance** | Counterfactual questions blocked without certification |
| **Runtime allowed** | Policy validation only; **no optimizer execution** |

### P16 — Live execution consideration (explicitly deferred)

| Field | Value |
|-------|-------|
| **Goal** | Phase 8+ gate review only |
| **Files** | docs, release gates |
| **Contracts** | Production signoff checklist |
| **Blocked until done** | All P1–P15 acceptance criteria for relevant tracks |
| **Acceptance** | Explicit human signoff; golden scenarios green |
| **Runtime allowed** | **Deferred** — no live engine execution from MIP |

---

## 7. Immediate next phase recommendation

### Recommended: **P1 — Intake session and path recommendation contracts (I1–I2)**

**Why P1 over S1–S3 or 8G/8H:**

| Option | Rationale |
|--------|-----------|
| **P1 (recommended)** | Smallest useful implementation step; connects LLM conversation to structured product workflow; does not require uploads, connectors, model execution, or sibling integration; enables I3, manifest, readiness, and Streamlit work |
| S1–S3 | Foundational for semantic validation but does not advance product workflow; best as **P4 parallel** once I1–I3 exist |
| 8G/8H | Critical for artifact answers but blocked on exports with semantic metadata; intake contracts unblock the user journey first |

**P1 deliverables:**

1. `MMMIntakeSession` / `GeoXIntakeSession` Pydantic contracts + JSON fixtures  
2. Deterministic `IntakePathRecommendation` helpers (MMM vs GeoX vs measurement gap)  
3. Tests proving session state machine and path gating without LLM provider calls  

**Not in P1:** `IntakePlan` (P2), uploads (P8), manifests (P3), 8G payloads.

---

## 8. Do-not-build-yet list

Explicitly defer until gated phases complete:

- Real model execution from MIP
- Optimizer-backed budget recommendations
- Live sibling Python imports or subprocess execution
- Automatic scheduled refresh
- Production table connectors (warehouse/DB)
- External LLM provider integration (Ollama/cloud) beyond MockLLM
- Decision-ready budget actions or autonomous spend changes
- Automatic artifact promotion or silent readiness upgrade
- Production recommendations without approval where policy requires

---

## 9. Acceptance criteria (audit complete)

| Criterion | Status |
|-----------|--------|
| All major roadmap themes identified | ✓ Section 2 |
| Overlapping concepts deduplicated | ✓ Section 3 |
| Canonical ownership defined | ✓ Section 3 |
| Dependency graph created | ✓ Section 4 |
| Implementation phase sequence created | ✓ Section 6, [ROADMAP_EXECUTION_SEQUENCE.md](../roadmap/ROADMAP_EXECUTION_SEQUENCE.md) |
| Next concrete phase recommended | ✓ Section 7 — **P1** |
| No-live-execution boundaries preserved | ✓ Throughout |
| No-production-recommendation boundaries preserved | ✓ Sections 5, 8 |

---

## Related documents

- [ROADMAP_EXECUTION_SEQUENCE.md](../roadmap/ROADMAP_EXECUTION_SEQUENCE.md) — condensed phase plan
- [LLM_DECISION_LAYER_ROADMAP.md](../roadmap/LLM_DECISION_LAYER_ROADMAP.md)
- [CONVERSATIONAL_INTAKE_AND_DATA_HANDOFF_ROADMAP.md](../roadmap/CONVERSATIONAL_INTAKE_AND_DATA_HANDOFF_ROADMAP.md)
- [PLATFORM_SEMANTIC_AND_DECISION_READINESS_ROADMAP.md](../roadmap/PLATFORM_SEMANTIC_AND_DECISION_READINESS_ROADMAP.md)
- [PLATFORM_CRITICAL_INVARIANTS_AND_GOLDEN_SCENARIOS.md](../roadmap/PLATFORM_CRITICAL_INVARIANTS_AND_GOLDEN_SCENARIOS.md)
