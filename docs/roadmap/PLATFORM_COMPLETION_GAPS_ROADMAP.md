# Platform Completion Gaps Roadmap

Addendum documenting **remaining platform-level completion tracks** beyond the current control-plane spine and LLM reasoning contracts.

Complements:

- [LLM Decision Layer Roadmap](./LLM_DECISION_LAYER_ROADMAP.md) — phased LLM and workbench delivery (Phases 0–8F implemented)
- [ROADMAP.md](./ROADMAP.md) — platform constitution and engine integration phases

## 1. Control plane vs execution engines

**MIP is the control plane, not the statistical engine.**

| Repository | Role |
|------------|------|
| **MIP** (`marketing_intelligence_platform`) | Contracts, governance, trust, orchestration, audit, approvals, LLM guidance, evidence comparison, user workflows |
| **MMM** (`mmm`) | Model fitting, calibration internals, replay/simulation, curve generation, decision-surface computation, optimizer internals |
| **panel_exp / GeoX** | Experiment design, power/MDE, estimator execution, inference, readout generation |

**Shared boundary:** file/API contracts plus `TrustReport`-governed handoff. MIP consumes structured exports; sibling repos produce them. MIP must not import sibling modules, run subprocesses, or trigger sibling execution through this contract.

### 1.1 Ownership table

| Area | MIP owns | MMM owns | panel_exp / GeoX owns |
|------|----------|----------|------------------------|
| Artifact contracts | yes | produces conforming exports | produces conforming exports |
| Model execution | no | yes | no |
| Experiment estimation | no | no | yes |
| TrustReport | yes | input evidence only | input evidence only |
| CalibrationSignal ingress | yes | consumes via governed calibration | produces experiment evidence |
| LLM explanation | yes | supplies explanation payload | supplies explanation payload |
| Optimizer internals | governance only | yes, if applicable | no |
| Decision approval | yes | no | no |
| Audit trail | yes | run metadata only | run metadata only |

### 1.2 What MIP has built (control-plane spine)

Implemented today:

- Contracts, gates, `TrustReport`, `EvidenceRegistry`
- `CalibrationSignal` governance and calibration audit
- Workflow manifests, planner/router, approval checkpoints (in-memory)
- LLM safety layer and `MockLLMProvider`
- Static sibling export ingestion (8B–8E)
- Compatibility registry and local path wiring
- Producer specifications (8F)

This spine is **safe for governance ingestion** but not yet a **durable causal marketing intelligence platform**. The tracks below define what remains.

### 1.3 Hard boundaries (unchanged)

This addendum is **documentation only**. No runtime logic, model execution, optimizer execution, sibling imports, path dependencies, subprocesses, LLM provider calls, production recommendations, or new runtime decision behavior.

## 2. Key roadmap decision

**Do not proceed to live engine execution or optimizer-backed recommendations until:**

1. LLM explanation/usage contracts are specified (Phases 8G–8N; see LLM reasoning addendum when merged).
2. Artifact lifecycle and schema migration policies are specified (Track P1–P2).
3. Decision-surface certification gates are specified (Track P6).
4. Cross-evidence reconciliation semantics are specified (Track P4).
5. Durable audit/approval records are designed (Track P9).
6. Scenario-level safety tests exist (Track P10).

**Producer writers** in `mmm` and `panel_exp` should emit enough structured payload to satisfy both MIP governance ingestion (8F envelope) and future LLM explanation/use-guidance contracts.

## 3. Platform completion tracks

### Track P1 — Artifact Lifecycle + Freshness

**Why:** Stale exports, old `TrustReport` values, and superseded model/readout artifacts must not remain silently usable.

**Future lifecycle states:**

`created` → `validated` → `registered` → `explained` → `approved` → `archived` | `superseded` | `deprecated` | `expired`

**Required future fields:**

| Field | Purpose |
|-------|---------|
| `artifact_version` | Version within artifact family |
| `created_at` | Creation timestamp |
| `expires_at` | Freshness cutoff |
| `supersedes` | Prior artifact replaced |
| `superseded_by` | Successor artifact |
| `freshness_status` | `fresh`, `stale`, `expired`, `unknown` |
| `archival_reason` | Why archived or deprecated |

**Ownership:**

- **MIP** owns lifecycle state and policy.
- **Sibling repos** provide source timestamps and run lineage.

---

### Track P2 — Schema Versioning + Migration Policy

**Why:** Once MMM and panel_exp produce exports, schema drift is guaranteed.

**Future contracts:**

| Concept | Purpose |
|---------|---------|
| `SchemaCompatibilityPolicy` | Which schema versions MIP accepts |
| `SchemaMigrationRegistry` | Known migrations between versions |
| Backward compatibility tests | CI blocks silent breakage |
| Deprecated schema handling | Downgrade or block with reason |
| Blocked schema versions | Explicit deny list |
| Migration audit notes | Human-readable migration record |

**Ownership:**

- **MIP** owns accepted schema versions and migrations.
- **Sibling repos** own producing current schema versions.

---

### Track P3 — Evidence Readiness Ladder

**Why:** Labels alone are not enough; all artifacts need a common readiness vocabulary.

**Readiness ladder:**

| Tier | Meaning |
|------|---------|
| `placeholder` | Structural fixture only |
| `diagnostic_only` | May inform exploration, not decisions |
| `research_only` | Internal research use |
| `shadow_validated` | Validated in shadow, not production |
| `decision_support` | May support human decisions with review |
| `production_decision_ready` | Eligible for governed production paths |
| `blocked` | Must not be used |

**Ownership:**

- **MIP** owns readiness taxonomy and gate interpretation.
- **Sibling repos** provide diagnostics/evidence needed for classification.

---

### Track P4 — Cross-Evidence Reconciliation

**Why:** The platform must explain whether evidence agrees, conflicts, or cannot be compared—not present isolated model summaries.

**Evidence sources (future comparison):**

MMM · GeoX · CLS · A/B tests · holdouts · replay evidence · synthetic controls

**Required comparison fields:**

| Field | Purpose |
|-------|---------|
| `estimand_alignment` | Same estimand or incompatible |
| `KPI_alignment` | KPI definition match |
| `geo_scope_alignment` | Geographic scope compatibility |
| `time_window_alignment` | Period overlap or gap |
| `channel_scope_alignment` | Channel scope compatibility |
| `effect_direction_agreement` | Same sign or conflict |
| `magnitude_agreement` | Comparable scale |
| `uncertainty_overlap` | Interval overlap assessment |
| `conflict_severity` | Governed conflict tier |
| `recommended_resolution_path` | Human review or more evidence |

**Ownership:**

- **MIP** owns reconciliation contracts and conflict explanation.
- **MMM / GeoX** provide comparable structured evidence summaries.

*Related:* Phase 8L in the LLM reasoning addendum (when merged) covers LLM-facing comparison payloads; Track P4 is the platform-level reconciliation contract.

---

### Track P5 — CalibrationSignal Quality + Replay Governance

**Why:** MMM calibration is high-risk. MIP must govern when experiment evidence can influence model calibration.

**Quality tiers:**

| Tier | Meaning |
|------|---------|
| `fresh_causal_signal` | Within freshness window, gates passed |
| `stale_but_usable_signal` | Stale but explicitly downweighted |
| `diagnostic_only_signal` | May inform diagnostics, not calibration update |
| `observational_only_signal` | Not causal; blocked from calibration |
| `expired_signal` | Outside validity window |
| `conflicting_signal` | Conflicts with other evidence |

**Future contracts:**

- `CalibrationReplayResult`
- `CalibrationStressTestSummary`
- `SignalDownweightingReason`
- `PriorVsLikelihoodDecisionRecord`

**Ownership:**

- **MIP** owns `CalibrationSignal` quality policy and audit.
- **MMM** owns calibration/replay implementation.
- **GeoX/panel_exp** owns experiment evidence production.

---

### Track P6 — Decision-Surface Certification

**Why:** Full-panel Δμ can become decision-support only after explicit certification. Diagnostic curves must not become production recommendations.

**Certification requirements (future gates):**

- Input completeness
- Data readiness
- Model readiness
- Calibration readiness
- Uncertainty checks
- Stability checks
- Sensitivity checks
- `TrustReport` decision-ready verdict
- Human approval

**Ownership:**

- **MIP** owns certification gates and decision-readiness status.
- **MMM** owns decision-surface computation and diagnostics.

---

### Track P7 — Optimizer Governance

**Why:** Budget allocation is the highest-risk path and must be blocked until evidence and approval gates are mature.

**Future optimizer governance:**

| Concept | Purpose |
|---------|---------|
| `optimizer_input_contract` | Governed optimizer inputs |
| `allowed_objectives` | Permitted optimization goals |
| `constraints` | Budget, risk, channel bounds |
| `risk_policy` | Risk tier requirements |
| `minimum_evidence_threshold` | Evidence bar before optimization |
| `counterfactual_validity_checks` | Surface validity gates |
| `approval_requirement` | Human approval mandatory |
| `recommendation_audit_trail` | Full audit of recommendation path |

**Ownership:**

- **MIP** owns optimizer governance, approval, and recommendation audit.
- **MMM** may own optimizer computation.
- **MIP must not** allow optimizer output unless decision-surface certification (P6) passes.

---

### Track P8 — Data Contracts + Observability

**Why:** Bad data should downgrade or block workflows before model interpretation.

**Future data checks:**

| Check | Purpose |
|-------|---------|
| Input schema profile | Expected vs actual schema |
| Missingness report | Coverage gaps |
| Schema drift | Drift from baseline profile |
| Freshness SLA | Data recency |
| Grain consistency | Time/geo/channel grain alignment |
| KPI definition consistency | KPI mapping quality |
| Geo mapping quality | Geo code alignment |
| Channel mapping quality | Channel taxonomy alignment |
| Lineage | Source system and transform chain |

**Ownership:**

- **MIP** owns data-readiness contracts and workflow gating.
- **Sibling repos** own native data diagnostics and export summaries.

---

### Track P9 — Durable Run / Approval / Audit Logging

**Why:** Local/in-memory governance is not enough for reproducible decision support.

**Future durable objects:**

| Record | Purpose |
|--------|---------|
| `RunRecord` | Workflow or engine run lineage |
| `WorkflowManifestRecord` | Persisted manifest snapshot |
| `ApprovalRecord` | Approval decision audit |
| `TrustReportRecord` | Trust verdict at point in time |
| `LLMAnswerRecord` | LLM answer audit trail |
| `ArtifactLineageRecord` | Artifact dependency graph |

**Required fields (common):**

`run_id`, `artifact_refs`, `approval_status`, `approver_identity_or_role`, `decision_reason`, `timestamps`, `revocation_or_expiration`, `audit_log`

**Ownership:**

- **MIP** owns persistence and audit semantics.
- **Sibling repos** provide source run IDs and commit markers.

---

### Track P10 — LLM Answer Audit + Scenario Evaluation

**Why:** If LLM guidance is part of the product, its behavior must be regression tested like software.

**LLM answer audit fields:**

| Field | Purpose |
|-------|---------|
| `user_question` | Raw user input |
| `classified_intent` | Router classification |
| `artifact_refs_used` | Artifacts cited |
| `trust_report_refs_used` | Trust verdicts cited |
| `answer_mode` | `answer_allowed`, `answer_blocked_with_reason`, etc. |
| `blocked_claims` | Claims explicitly refused |
| `grounding_fields` | Structured field paths cited |
| `final_answer` | Rendered response |
| `safety_verdict` | Pass/fail safety check |

**Scenario tests (examples):**

| Scenario | Expected behavior |
|----------|-------------------|
| Valid GeoX export → TrustReport → safe explanation | Grounded diagnostic summary |
| Stale calibration → no recommendation | Block or downgrade |
| MMM positive + GeoX negative → conflict explanation | Cite conflict, no silent average |
| User asks for budget move → blocked or approval-required | No autonomous recommendation |
| Old schema version → downgraded or blocked | Schema policy enforced |

**Ownership:**

- **MIP** owns LLM safety, answer audit, and evaluation harness.
- **Sibling repos** provide structured payloads and diagnostics.

*Related:* Phase 8N in the LLM reasoning addendum (when merged).

---

### Track P11 — Product Workflows + UX Journeys

**Why:** Users need guided workflows, not just components.

**Named workflows (future):**

| Workflow | Purpose |
|----------|---------|
| Diagnose MMM readiness | Data + model readiness path |
| Import GeoX evidence | Governed experiment import |
| Explain experiment readout | Grounded readout explanation |
| Compare MMM vs experiment evidence | Cross-evidence reconciliation UI |
| Prepare decision review | Approval package assembly |
| Generate executive-safe summary | Audience-aware explanation |
| Prepare remediation plan | Blocker → fix guidance |

**Ownership:**

- **MIP** owns workflow orchestration and UI.
- **Sibling repos** provide source artifacts and diagnostics.

---

### Track P12 — Security + Filesystem Hardening

**Why:** Local export ingestion can become a leakage or unsafe parsing surface.

**Future safety checks:**

| Check | Purpose |
|-------|---------|
| Path allowlist | Only approved directories |
| No symlink traversal | Block symlink escapes |
| File size limits | Prevent resource exhaustion |
| JSON depth limits | Safe parsing bounds |
| Safe parsing errors | No exception leakage |
| Secret scanning | Block credential exports |
| PII/sensitive field scanning | Detect sensitive data |
| Export payload redaction | Redact before display/storage |

**Ownership:**

- **MIP** owns file ingestion safety.
- **Sibling repos** avoid exporting secrets/PII.

---

### Track P13 — Package Ergonomics + Public API

**Why:** The platform should be maintainable as a real package, not just a collection of internal modules.

**Future needs:**

- Stable public APIs
- CLI commands (`mip-demo`, `mip-app`, future commands)
- Example configs and sample exports
- Developer docs and typed examples
- Changelog and semantic versioning
- Release checklist

**Ownership:**

- **MIP** owns package ergonomics for the control plane.
- **Sibling repos** own their own public export writer APIs.

## 4. Track summary and dependencies

```text
P1  Artifact lifecycle + freshness
P2  Schema versioning + migration        ← depends on P1 for supersession semantics
P3  Evidence readiness ladder            ← gates P4, P6, P7
P4  Cross-evidence reconciliation        ← needs P3 + sibling evidence summaries
P5  CalibrationSignal quality            ← MIP policy; MMM/GeoX producers
P6  Decision-surface certification       ← needs P3, P5, P8
P7  Optimizer governance                 ← blocked until P6 passes
P8  Data contracts + observability         ← upstream of P6
P9  Durable audit logging                ← needed before production approval paths
P10 LLM answer audit + scenario eval      ← complements 8G–8N
P11 Product workflows + UX              ← consumes P1–P10 contracts
P12 Security + filesystem hardening      ← hardens 8B–8F ingestion
P13 Package ergonomics + public API      ← ongoing; supports all tracks
```

## 5. MIP-owned vs sibling-owned implementation

| Track | MIP implements | Sibling repos implement |
|-------|----------------|-------------------------|
| P1 | Lifecycle state machine, freshness policy | `created_at`, run lineage in exports |
| P2 | Schema acceptance, migration registry | Current `export_schema_version` |
| P3 | Readiness taxonomy, gate mapping | Diagnostic payloads for classification |
| P4 | Reconciliation contracts, conflict UI | Comparable evidence summaries |
| P5 | Quality policy, audit trail | Calibration/replay results |
| P6 | Certification gates | Δμ surface + diagnostics |
| P7 | Governance, approval, audit | Optimizer computation (MMM) |
| P8 | Data-readiness contracts | Native data diagnostic exports |
| P9 | Persistence, audit records | Run IDs, commit markers |
| P10 | Safety harness, answer audit | Explanation payloads |
| P11 | Workflows, UI | Source artifacts |
| P12 | Ingestion hardening | Safe export content |
| P13 | Public API, docs, releases | Export writer APIs |

**Product intake workflow:** [CONVERSATIONAL_INTAKE_AND_DATA_HANDOFF_ROADMAP.md](./CONVERSATIONAL_INTAKE_AND_DATA_HANDOFF_ROADMAP.md) (I1–I15) implements P8 data contracts and P11 product workflows for the LLM → upload/connect → readiness → handoff path. P9 audit and P12 security align with I13–I14.

## 6. Related documents

- [LLM_DECISION_LAYER_ROADMAP.md](./LLM_DECISION_LAYER_ROADMAP.md)
- [ROADMAP.md](./ROADMAP.md)
- [REPO_INTEGRATION_STRATEGY.md](../architecture/REPO_INTEGRATION_STRATEGY.md)
- [AGENTIC_WORKFLOW_GOVERNANCE_ROADMAP.md](../architecture/AGENTIC_WORKFLOW_GOVERNANCE_ROADMAP.md)
- [CONVERSATIONAL_INTAKE_AND_DATA_HANDOFF_ROADMAP.md](./CONVERSATIONAL_INTAKE_AND_DATA_HANDOFF_ROADMAP.md)
- [MIP_SIBLING_EXPORT_PRODUCER_SPEC.md](../integrations/MIP_SIBLING_EXPORT_PRODUCER_SPEC.md)
