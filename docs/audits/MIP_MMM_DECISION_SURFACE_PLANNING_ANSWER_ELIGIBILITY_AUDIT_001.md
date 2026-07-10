# MMM DecisionSurface Planning-Answer Eligibility Audit 001

**Artifact ID:** `MIP_MMM_DECISION_SURFACE_PLANNING_ANSWER_ELIGIBILITY_AUDIT_001`  
**Type:** audit / governance checkpoint only  
**Repo checkpoint:** `d8578e7` (MMM runtime/control-plane lane closed)  
**Status:** completed  
**Scope:** audit-only — did not add or modify production code under `src/mip/`  
**Lane:** `MMM_DECISION_SURFACE_PLANNING_ANSWER_ELIGIBILITY_LANE`

---

## 1. Purpose

Determine whether MIP already has enough **DecisionSurface**, **RecommendationContract**, **TrustReport**, artifact governance/use-readiness, evaluation gates, planning-answer, and orchestration infrastructure to decide **which MMM-backed planning questions can be safely answered**.

This audit starts the new lane safely and prevents overbuilding. It does **not** implement new production functionality and does **not** reopen runtime/control-plane plumbing unless a concrete blocker is found (none found).

---

## 2. Verdict

**`PARTIALLY_COVERED_NEEDS_THIN_PLANNING_ANSWER_ELIGIBILITY_GATE`**

**Question-level planning-answer eligibility already exists?** **No.**

Upstream artifact readiness, DecisionSurface/Recommendation/Trust contracts, and release gates exist, but they are **not connected** into a question-level eligibility decision (e.g. “can we reallocate spend?” vs “what drove performance?”).

**Recommended next artifact:** `MIP_MMM_PLANNING_ANSWER_ELIGIBILITY_GATE_001` — thin metadata-only gate that maps planning question class + `MMMArtifactGovernanceUseReadinessResult` (+ optional DecisionSurface/Trust/Recommendation gate outcomes) into answerable / diagnostic-only / blocked / deferred eligibility **without** constructing DecisionSurface, executing optimizers/simulators, or generating RecommendationContract.

---

## 3. What exists (evidence)

| Component | Location | What it covers |
|-----------|----------|----------------|
| `DecisionSurface` | `mip.contracts.decision_surface` | Certified vs diagnostic surfaces; `FULL_PANEL_DELTA_MU` required for certified budget planning |
| `DecisionSurfaceType` | `mip.contracts.enums` | `full_panel_delta_mu`, `diagnostic_curve`, `decomposition`, `forecast`, `research_surface` |
| `check_decision_surface_gate` | `mip.evaluation.gates` | Blocks non–full-panel Δμ for `BUDGET_PLANNING`; caps tiers |
| `RecommendationContract` | `mip.contracts.recommendation` | Structured recommendation; budget_shift requires `decision_surface_ids`; decision_ready requires evidence/surface |
| `check_recommendation_gate` | `mip.evaluation.gates` | Blocks blocked tier, failed diagnostics, missing surface for budget_shift |
| `TrustReport` | `mip.contracts.trust` | Tiered trust envelope; decision_ready requires passing diagnostics |
| `check_trust_report_gate` | `mip.evaluation.gates` | Gates trust reports for downstream decision support |
| Release gates (policy) | `docs/operating_model/RELEASE_GATES.md` | MMM promotion, recommendation readiness, LLM workflow promotion |
| Governance adapter (fixture) | `mip.adapters.governance` | Maps MMM **placeholder** outputs → diagnostic DecisionSurface + TrustReport |
| Use-readiness gate | `mip.contracts.mmm_artifact_governance_use_readiness`, `mip.workflows.mmm_artifact_governance_use_readiness` | `planning_ready`, `diagnostic_only`, Trust/DecisionSurface/diagnostic **review routes**, blocked/deferred, human review |
| LLM safety | `mip.llm.safety` | Blocks bypass-gate / ignore-TrustReport phrases; high-risk budget reallocation requires human review; blocks recommendation actions by tier |
| Orchestration fixtures | `mip.orchestration.plans`, `mip.orchestration.router` | MMM fixture report routing; diagnostic DecisionSurface fixture notes only |
| Lane closure audit | `docs/audits/MIP_MMM_RUNTIME_ORCHESTRATION_LANE_COMPLETION_AUDIT_001.md` | Runtime lane closed; next lane = this one |

---

## 4. Audit questions answered

### 4.1 What DecisionSurface contracts already exist?

`DecisionSurface` with `surface_type`, `decision_estimand`, `certification_status`, `supported_scenarios`, `reliability_scorecard_id`, warnings/unsupported claims. Validators enforce: certified surfaces must be `full_panel_delta_mu` with scorecard; diagnostic curves/decomposition cannot be certified.

### 4.2 What DecisionSurface gates already exist?

`check_decision_surface_gate(surface, purpose)` — for `BUDGET_PLANNING`, blocks non–full-panel Δμ, blocked certification, missing reliability scorecard; otherwise may WARN and cap tier. Non–budget purposes return diagnostic-only tier PASS.

### 4.3 What RecommendationContract contracts/gates already exist?

`RecommendationContract` + `RecommendationType` (`budget_shift`, `hold_budget`, `investigate`, `block_action`, …). Contract validators + `check_recommendation_gate` enforce decision-ready / budget_shift / blocked rules.

### 4.4 What TrustReport requirements already gate decision or recommendation use?

`TrustReport` requires passing diagnostics for `decision_ready`. `check_trust_report_gate` blocks failed diagnostics / blocked tier. Recommendation readiness policy in `RELEASE_GATES.md` requires full contract validation and no upstream blocked tiers. Fixture governance builds TrustReport via gate paths for adapter placeholders.

### 4.5 Can MIP already distinguish descriptive / diagnostic / scenario-comparison / simulation-only / recommendation-eligible / blocked / deferred **answers**?

**No as first-class planning-answer types.**

Adjacent concepts exist (`ConfidenceTier`, `DecisionSurfaceType`, `RecommendationType`, use-readiness statuses), but there is **no** planning-answer taxonomy that classifies a user question into those answer modes.

### 4.6 Can MIP already decide whether a planning question is answerable from a planning-ready MMM artifact?

**Partially / no at question level.**

`MMMArtifactGovernanceUseReadinessResult.planning_ready` says the **artifact** may support planning-style downstream use and DecisionSurface **review**. It does **not** decide whether a specific question (“reallocate spend?”, “what happened?”) is answerable, diagnostic-only, or blocked.

### 4.7 Can MIP already represent allowed planning question types (“what happened?”, “reallocate spend?”, “recommend a budget?”, …)?

**No dedicated question-type contract.** LLM intent classification has related intents (`EXPLAIN_DECISION_SURFACE`, `EXPLORE_SCENARIO`, …) but not an MMM planning-answer eligibility matrix keyed by question class.

### 4.8 Can MIP separate explanation / scenario comparison / simulation request / optimizer request / recommendation request?

**Partially at adjacent layers only** (intents, recommendation types, surface types). **No** unified planning-answer request separation that gates each class against use-readiness + DecisionSurface/Trust/Recommendation rules.

### 4.9 Does MIP already block RecommendationContract generation unless required gates pass?

**Yes for constructed RecommendationContract objects** — validators + `check_recommendation_gate` block invalid/decision-ready misuse. This is **artifact-level**, not question-level eligibility before generation.

### 4.10 Does MIP already prevent LLM-generated recommendations from bypassing DecisionSurface / TrustReport / RecommendationContract?

**Yes at safety/intent layer** — `mip.llm.safety` blocks bypass/ignore-TrustReport patterns; high-risk budget language requires human review; blocked actions include `recommendation` / `production_use` for restricted tiers. Vision docs forbid LLM approval of production recommendations. This is **not** a planning-answer eligibility gate.

### 4.11 Does `MMMArtifactGovernanceUseReadinessResult` provide enough upstream metadata for planning-answer eligibility?

**Yes as upstream input.** It supplies `planning_ready`, `diagnostic_only`, review-route flags, blocked/deferred reasons, human-review, lineage, and artifact URI metadata. A thin eligibility gate can consume it without new runtime plumbing.

### 4.12 What is missing before MIP can safely answer MMM-backed planning questions?

1. **Question-level planning-answer eligibility gate** mapping question class → allowed answer mode  
2. Explicit separation of explanation vs scenario vs simulation vs optimizer vs recommendation **requests** for MMM  
3. Wiring eligibility outcomes to DecisionSurface / Trust / Recommendation **gates** (consume outcomes; do not construct artifacts yet)  
4. Clear blocked/deferred reasons when `planning_ready=false` or only diagnostic routes are enabled  

**Not missing for this lane start:** runtime adapter, result ingestion, or a separate model-promotion system.

### 4.13 Should next implementation be no-op / thin gate / thin DecisionSurface adapter / larger new contract?

**Thin planning-answer eligibility gate.**

| Option | Why not / why |
|--------|----------------|
| No-op | Question-level eligibility does not exist |
| Thin DecisionSurface eligibility adapter | DecisionSurface contracts/gates already exist; constructing/adapting surfaces is premature |
| Larger new planning-answer contract | Overbuild; reuse existing contracts + use-readiness |
| **Thin planning-answer eligibility gate** | **Preferred** — connects existing pieces without execution |

---

## 5. Coverage matrix

| Capability | Supported? | Notes |
|------------|------------|-------|
| DecisionSurface contract | **Yes** | `mip.contracts.decision_surface` |
| DecisionSurface gate | **Yes** | `check_decision_surface_gate` |
| TrustReport contract | **Yes** | `mip.contracts.trust` |
| RecommendationContract + gate | **Yes** | contract + `check_recommendation_gate` |
| MMM artifact use-readiness | **Yes** | governance/use-readiness gate |
| Planning-ready / diagnostic-only states | **Yes** | use-readiness result |
| Trust / DecisionSurface review routes | **Yes** | metadata routes only |
| Recommendation blocking (artifact-level) | **Yes** | validators + gates |
| Descriptive answer type | **No** | no planning-answer taxonomy |
| Diagnostic answer type | **No** | diagnostic surfaces ≠ answer type |
| Scenario-comparison answer type | **No** | |
| Simulation-only answer type | **No** | |
| Recommendation-eligible answer type | **No** | |
| Blocked / deferred answer types | **No** | blocked/deferred **artifact** states exist; not answer types |
| Question-level eligibility gate | **No** | primary gap |
| LLM recommendation bypass prevention | **Yes** | safety/intent + policy docs |
| Optimizer/simulator execution required in MIP | **No** | remains external / future |

---

## 6. What is missing (summary)

- Question-level planning-answer eligibility does **not** exist  
- No first-class planning question / answer-mode taxonomy for MMM-backed Q&A  
- Existing DecisionSurface / Trust / Recommendation gates are not composed against a planning question + use-readiness result  
- Fixture governance constructs diagnostic DecisionSurface for placeholders only — not a substitute for eligibility  

---

## 7. Recommended next artifact

**`MIP_MMM_PLANNING_ANSWER_ELIGIBILITY_GATE_001`**

Thin metadata-only gate:

`planning question class` + `MMMArtifactGovernanceUseReadinessResult` (+ optional gate outcomes / surface refs)  
→ eligibility result (descriptive / diagnostic / scenario / simulation / recommendation-eligible / blocked / deferred)

Must **not**: construct DecisionSurface, execute DecisionSurface, generate RecommendationContract, run optimizer/simulator, compute ROI/ROAS/lift, load artifacts, or change LLM provider behavior.

---

## 8. Audit-only confirmation

This audit:

- added documentation and a governance test only  
- did **not** add or modify production code under `src/mip/`  
- did not construct TrustReport / DecisionSurface / RecommendationContract  
- did not implement optimizer/simulator or budget allocation math  
- did not reopen MMM runtime/control-plane plumbing  
