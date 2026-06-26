# MIP Report, Adapter, and Agent Contract Plan 001

## 1. Title and status

| Field | Value |
|-------|-------|
| **Title** | MIP Report, Adapter, and Agent Contract Plan 001 |
| **Status** | Accepted contract planning direction |
| **Type** | Report contracts / fixture adapters / agent tooling / LLM boundary plan |
| **Base commit** | `f094986` — Agent tooling audit merged (PR #35) |
| **Date** | 2026-05-28 |
| **Scope** | Docs/contract planning only — no runtime implementation in this phase |

**Hard boundaries (unchanged):** No MMM/GeoX execution, no LLM providers, no production ingestion, no mock advanced dashboards, no unsupported causal/ROI claims. MIP is the **control plane**, not the statistical engine.

---

## 2. Why this plan exists

[MIP Agent Tooling and Roadmap Implementation Detail Audit 001](../audits/MIP_AGENT_TOOLING_AND_ROADMAP_IMPLEMENTATION_DETAIL_AUDIT_001.md) found MIP is **mostly ready for deterministic Cursor work** but **not ready for LLM/agent runtime**.

The critical missing layer is **not** more UI, notebooks, or provider wiring. It is **stable contracts** between:

```text
Stage A fixtures
  → workflow inputs (adapters)
  → deterministic workflow outputs
  → report envelopes (exportable artifacts)
  → artifact references (provenance)
  → future agent packets / LLM explanations (read-only, governed)
```

Without these contracts, Cursor agents, notebooks, and guided demos will **invent** adapter shapes, report formats, provenance fields, and explanation boundaries. This plan converts audit warnings into **enforceable architecture** before any new runtime helpers ship.

---

## 3. Source audit findings

**Source:** [MIP_AGENT_TOOLING_AND_ROADMAP_IMPLEMENTATION_DETAIL_AUDIT_001.md](../audits/MIP_AGENT_TOOLING_AND_ROADMAP_IMPLEMENTATION_DETAIL_AUDIT_001.md)

### Three highest-priority gaps (from audit)

| # | Gap | This plan section |
|---|-----|-------------------|
| 1 | Stage A fixture→workflow adapters | §4 Stage A.3 |
| 2 | Deterministic report output contract plan | §5 |
| 3 | Deterministic notebook plan with acceptance criteria | §10 (prerequisites; notebook plan deferred until gates pass) |

### Five critical gates (must exist before notebooks / LLM / agent runtime)

| # | Gate | This plan section |
|---|------|-------------------|
| 1 | Stable report artifact contracts | §5 |
| 2 | Agent input/output packet contracts | §7 |
| 3 | LLM explanation-layer boundary | §8 |
| 4 | Artifact registry / provenance | §6 |
| 5 | Golden-path deterministic acceptance tests | §9 |

---

## 4. Stage A.3 fixture→workflow adapter plan

### Purpose

Map Stage A `fixture_id` values into **current deterministic workflow inputs** using Stage A.2 loaders (`mip.examples.stage_a_fixtures`). Adapters must not require docs, notebooks, UI, or agents to understand raw fixture JSON schemas.

### Future module (not implemented in this plan)

Recommended location: `src/mip/examples/stage_a_adapters.py` (or `src/mip/workflows/intake/stage_a_adapters.py` after review — **do not create until implementation phase**).

### Required adapter capabilities

| Function | Purpose |
|----------|---------|
| `list_supported_fixture_workflow_mappings()` | Return governed `(fixture_id, workflow_area, adapter_id, status)` tuples |
| `build_cold_start_input_from_fixture(fixture_id)` | → `ColdStartBusinessProfile` (+ optional traffic profile) or governed error |
| `build_readiness_input_from_fixture(fixture_id)` | → `CommonIntakeWorkbench` or governed error |
| `build_calibration_input_from_fixture(fixture_id)` | → `(CalibrationEvidenceInput, CalibrationMappingRequirement)` |
| `build_intake_input_from_fixture(fixture_id)` | → `MeasurementIntakeSession` or routing-only context dict |
| `validate_fixture_workflow_compatibility(fixture_id, workflow_area)` | Fail closed before workflow execution |
| `explain_fixture_mapping(fixture_id)` | Human/agent-readable mapping rationale from manifest metadata |

### Required behavior

- **Use** `load_stage_a_fixture`, `list_stage_a_fixtures`, manifest metadata from Stage A.2
- **Never** run MMM/GeoX engines or claim engine-backed outputs
- Return **typed workflow input objects** (Pydantic contracts) or explicit `StageAAdapterError`
- **Fail closed** for unsupported fixture/workflow combinations
- Preserve `synthetic: true` and `requires_mmm_or_geox_engine: false` in adapter metadata
- Attach `source_fixture_id`, `workflow_area`, `demo_journey`, `evidence_level` to adapter result metadata

### Namespace mismatch (do not collapse without review)

| Namespace | Used by | Example keys |
|-----------|---------|--------------|
| `sample_key` | `app.demo_fixtures`, FastAPI service routes | `valid_governed_evidence`, `national_mmm_ready_geox_blocked` |
| `fixture_id` | Stage A manifest, `mip.examples.stage_a_fixtures` | `experiment_readout_valid`, `national_weekly_channel_summary` |

**Rule:** Stage A.3 adapters bridge `fixture_id` → workflow inputs. A separate **optional** `sample_key ↔ fixture_id` mapping table may be added later for service API alignment. Do **not** silently alias the two namespaces in adapters.

### Implementation sequencing (explicit)

| Order | Item | Rationale |
|-------|------|-----------|
| **1a** | Freeze report envelope fields for calibration path (§5) | Golden path #3–#5 need stable report IDs |
| **1b** | Implement **calibration adapter first** | Cleanest today: fixture already has `evidence` + `requirement` |
| **2** | Readiness adapter | Only where summary → workbench mapping is contract-clear |
| **3** | Advisory adapter | Map business profile JSON → `ColdStartBusinessProfile` |
| **4** | Intake adapter | May remain **routing-only** until `MeasurementIntakeSession` builder is specified |

Readiness and intake fixtures are **summaries/narratives**, not direct workbench/session payloads. Adapters for those paths must either build minimal governed workbenches from declared fields or return `StageAAdapterError` with `unsupported_mapping` — **never guess row-level data**.

### Acceptance criteria (Stage A.3 implementation)

- [ ] Calibration adapter for `experiment_readout_valid`, `experiment_readout_missing_se`, `experiment_readout_metric_mismatch`
- [ ] `list_supported_fixture_workflow_mappings()` documents supported vs deferred mappings
- [ ] Unsupported mappings raise `StageAAdapterError` (or equivalent) with deterministic message
- [ ] Tests prove adapters never emit ROI, optimizer, response-curve, matched-market, power/MDE, or causal-lift fields
- [ ] Tests prove every adapter output preserves `synthetic` and `requires_mmm_or_geox_engine: false`
- [ ] No adapter calls MMM/GeoX engines or `run_local_workflow` engine paths

---

## 5. Deterministic report output contract plan

### Purpose

Define **stable report envelopes** that wrap existing workflow outputs for exporters, notebooks, UI, agents, and future LLM explanations. Reports are **deterministic summaries** of governed workflow artifacts — not new measurement results.

### Relationship to existing contracts

| Existing workflow output | Report envelope | Notes |
|--------------------------|-----------------|-------|
| `ColdStartAdvisoryPlan` | `ColdStartAdvisoryReport` | New envelope; embeds plan fields |
| `BaseWorkflowReadinessReport` (list) | `ReadinessAssessmentReport` | Aggregates one or more readiness reports |
| `CalibrationMappingReport` (+ optional `CalibrationSignal`) | `CalibrationMappingReportEnvelope` | Wraps existing `CalibrationMappingReport`; avoid name collision in implementation |
| `IntakePathRecommendation` | `IntakeRoutingReport` | Wraps recommendation + session refs |
| Governance fixture / validation output | `GovernanceBlockedClaimReport` | Educational + validator findings |
| Manifest + loader metadata | `FixtureInventoryReport` | Inventory for docs/agents |

> **Naming note:** `CalibrationMappingReport` already exists in `mip.contracts.calibration_intake`. Implementation should use a distinct envelope name (e.g. `DeterministicCalibrationReport`) or namespace to avoid shadowing.

### Common report envelope fields (all report types)

Every deterministic report **must** include:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `report_id` | `str` | yes | Stable unique ID for this report instance |
| `report_type` | `str` | yes | e.g. `cold_start_advisory`, `readiness_assessment` |
| `schema_version` | `str` | yes | e.g. `deterministic_report_v1` |
| `source_workflow` | `str` | yes | Workflow helper or route name |
| `source_input_ref` | `ArtifactReference` | yes | Fixture or input provenance |
| `generated_at` | `datetime` | yes | UTC timestamp |
| `evidence_mode` | `str` | yes | e.g. `business_profile_only`, `diagnostic_candidate` |
| `governance_status` | `str` | yes | e.g. `hypothesis`, `blocked`, `needs_more_data`, `mapped` |
| `summary` | `str` | yes | Short deterministic summary |
| `findings` | `list[str]` | yes | Key findings (may be empty) |
| `recommended_next_steps` | `list[str]` | yes | Safe next steps from contracts |
| `missing_data` | `list[str]` | yes | Missing fields/assets (may be empty) |
| `blocked_claims` | `list[str]` | yes | Claims that must not be made |
| `allowed_downstream_uses` | `list[str]` | yes | e.g. `education`, `diagnostic_review` |
| `forbidden_downstream_uses` | `list[str]` | yes | e.g. `decision_recommendation`, `budget_optimization` |
| `artifact_refs` | `list[ArtifactReference]` | yes | Linked artifacts (workflow output, fixture, etc.) |
| `workflow_payload` | `dict` or typed embed | yes | Governed embed of existing contract JSON |

Reports **must not** add causal estimates, ROI, optimizer output, response curves, matched markets, power/MDE, or treatment assignment unless produced by a **certified engine path** (Stage B — blocked today).

### Per-report specifics

#### `ColdStartAdvisoryReport`

- `governance_status`: `hypothesis` / `blocked` (if inputs invalid)
- `workflow_payload`: serialized `ColdStartAdvisoryPlan`
- `blocked_claims`: must include causal lift, ROI proof, budget optimization when `evidence_mode=business_profile_only`

#### `ReadinessAssessmentReport`

- `governance_status`: mirrors readiness `status` aggregate (blocked if any blocking)
- `workflow_payload`: list of `BaseWorkflowReadinessReport`
- `missing_data`: union of `blocking_reasons` and checklist items

#### `CalibrationMappingReportEnvelope`

- `governance_status`: maps from `CalibrationIntakeStatus` (`mapped`, `needs_more_data`, `incompatible`, `blocked`)
- `workflow_payload`: `CalibrationMappingReport` + optional `CalibrationSignal` reference only (not full signal if blocked)

#### `IntakeRoutingReport`

- `governance_status`: `route_recommended` / `needs_more_inputs`
- `workflow_payload`: `IntakePathRecommendation` + optional session summary

#### `GovernanceBlockedClaimReport`

- `governance_status`: `educational_only`
- `workflow_payload`: unsupported-claim examples or validator output
- Must not change runtime behavior — report-only

#### `FixtureInventoryReport`

- `workflow_payload`: manifest entries + synthetic markers
- Used by agents/docs; no workflow execution

### Acceptance criteria (report contract implementation)

- [ ] Pydantic models (or JSON schema) defined in `src/mip/contracts/` before any report generator helpers
- [ ] Reports preserve `blocked` / `needs_more_data` / `incompatible` status — never upgrade silently
- [ ] `blocked_claims` and `forbidden_downstream_uses` populated from existing contract fields
- [ ] Golden-path tests (§9) can assert on report envelope fields
- [ ] Reports suitable for later Markdown/HTML export without re-deriving governance fields

### Sequencing vs adapters

**Report envelope schemas must be defined before report generator helpers.**

**Calibration adapter (Stage A.3) may proceed in parallel** once `CalibrationMappingReportEnvelope` field list is frozen, because the workflow output contract already exists. Do **not** implement generators until envelope models are merged.

---

## 6. Artifact registry / provenance plan

### Purpose

Every report must cite **where its inputs came from** and what downstream uses are allowed. Prevents silent promotion of advisory/diagnostic evidence to decision evidence.

### Candidate contract: `ArtifactReference`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `artifact_id` | `str` | yes | Stable ID |
| `artifact_type` | `str` | yes | e.g. `stage_a_fixture`, `calibration_mapping_report`, `cold_start_advisory_plan` |
| `source_workflow` | `str` | yes | Producing workflow or loader |
| `source_fixture_id_or_payload_ref` | `str` | yes | `fixture_id` or hashed payload ref |
| `source_commit_or_version` | `str` | yes | Package version + optional git commit |
| `created_at` | `datetime` | yes | UTC |
| `governance_status` | `str` | yes | Current governance tier |
| `evidence_mode` | `str` | yes | Evidence mode label |
| `allowed_downstream_uses` | `list[str]` | yes | Explicit allow list |
| `forbidden_downstream_uses` | `list[str]` | yes | Explicit deny list |
| `content_hash_optional` | `str` | no | SHA-256 of canonical JSON for drift detection |
| `path_or_uri_optional` | `str` | no | File path only (local); no cloud URIs in Stage A |

### Near-term implementation constraints

- **Local / in-memory / file-path only** — reuse patterns from `EvidenceRegistry` where appropriate
- **No** database, queue, object storage, or external registry
- **No** raw row storage in artifact references

### Acceptance criteria

- [ ] Every report envelope `source_input_ref` is a valid `ArtifactReference`
- [ ] Every artifact has non-empty `forbidden_downstream_uses` for decision paths when `evidence_mode` is advisory/diagnostic
- [ ] No artifact metadata may set `governance_status=decision_ready` without TrustReport / certified engine path (blocked today)
- [ ] Provenance chain: `fixture_id` → adapter metadata → workflow output → report envelope

---

## 7. Future agent packet contract plan

**Do not implement in this phase.** Define requirements for P17 / LangGraph and Cursor agent tasks.

### Existing contracts (P8b — implemented)

Already in `src/mip/contracts/agentic_workflow.py`:

- `AgentRunManifest`
- `AgentFailurePacket`
- `AgentResolutionPlan`
- `AgentValidationReport`
- `AgentRetryPolicy`
- `AgentRole`, `AgentPermissionBoundary`, etc.

### Missing / to define at implementation

| Contract | Purpose | Key fields (high level) |
|----------|---------|-------------------------|
| `AgentInputPacket` | Normalize user question + fixture/report refs for a task | `packet_id`, `role`, `workflow_area`, `user_question`, `fixture_ids`, `report_ids`, `allowed_actions`, `blocked_actions`, `evidence_mode` |
| `AgentArtifactReference` | Lightweight ref for handoffs | `artifact_id`, `artifact_type`, `governance_status`, `evidence_mode` |
| `AgentAllowedAction` | Enumerated safe action | `action_id`, `description`, `requires_human_approval` |
| `AgentBlockedAction` | Enumerated forbidden action | `action_id`, `reason`, `safe_alternative` |

### Agent rules (non-negotiable)

Agents **may**:

- Call deterministic loaders, adapters, workflows, report exporters
- Summarize existing reports in governed language
- Propose next **safe** actions from `recommended_next_steps`
- Emit `AgentRunManifest`, `AgentFailurePacket`, `AgentValidationReport`

Agents **may not**:

- Estimate lift, ROI, power/MDE
- Choose matched markets or treatment/control assignment
- Approve or override `TrustReport` / blocked status
- Promote diagnostic/advisory evidence to decision evidence
- Run MMM/GeoX engines without certified gated paths
- Store raw production rows in manifests

### Acceptance criteria (future agent runtime)

- [ ] Every agent task declares `allowed_actions` and `blocked_actions`
- [ ] Every run produces `AgentRunManifest`
- [ ] Every failure produces `AgentFailurePacket` or governed deterministic error
- [ ] Every user-facing output passes `AgentValidationReport` before display (when LLM involved)

---

## 8. LLM explanation boundary contract plan

**Do not implement providers in this phase.**

### Existing (P7b)

- `LLMExplanationRequest`
- `LLMExplanationPlan`
- `LLMExplanationStatus`, `LLMExplanationBlockingReason`
- `build_llm_explanation_plan()` in `mip.workflows.intake.llm_explanation`

### Missing: `LLMExplanationResponse`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `explanation_id` | `str` | yes | Unique ID |
| `source_report_id` | `str` | yes | **Required** — no orphan explanations |
| `schema_version` | `str` | yes | e.g. `llm_explanation_response_v1` |
| `summary` | `str` | yes | Short explanation |
| `plain_language_explanation` | `str` | yes | Business-language narrative |
| `allowed_interpretations` | `list[str]` | yes | What reader may conclude |
| `blocked_interpretations` | `list[str]` | yes | What reader must not conclude |
| `recommended_next_steps` | `list[str]` | yes | From source report only |
| `citations_to_report_sections` | `list[str]` | yes | Section refs in source report |
| `governance_status_preserved` | `bool` | yes | Must be `true`; validator fails if false |
| `claim_labels_preserved` | `list[str]` | yes | Copied from source |
| `warnings` | `list[str]` | yes | Including "LLM does not create measurement authority" |

### Allowed LLM behavior

- Explain deterministic report contents
- Translate technical findings into business language
- Explain why a claim is blocked
- List missing data from report `missing_data`
- Suggest safe next steps from report `recommended_next_steps`

### Blocked LLM behavior

- Create causal estimates, ROI, budget recommendations
- Generate response curves, optimizer outputs, scenario plans
- Infer matched markets; calculate power/MDE
- Override `governance_status`, `blocked_claims`, or evidence labels
- Convert advisory/diagnostic evidence into decision evidence
- Invent missing uncertainty or fill null SE fields

### Acceptance criteria (future LLM implementation)

- [ ] `LLMExplanationResponse` requires non-empty `source_report_id`
- [ ] Validator asserts `governance_status_preserved is True`
- [ ] No response field contains forbidden claim fragments (reuse contract validators)
- [ ] Public demo remains `LLMProviderMode.DISABLED` until auth/eval harness exists

---

## 9. Golden-path deterministic acceptance test plan

Five golden paths **must** pass before notebooks, landing-page guided demos, or LLM layers depend on these workflows.

### Golden path 1 — Beginner cold-start advisory

| Item | Value |
|------|-------|
| **Source fixture** | `local_fitness_studio` |
| **Adapter** | `build_cold_start_input_from_fixture` (Stage A.3) |
| **Workflow** | `build_cold_start_advisory_plan` |
| **Report** | `ColdStartAdvisoryReport` |
| **Expected governance** | `hypothesis`; `evidence_mode=business_profile_only` |
| **Blocked claims** | causal lift, ROI proof, budget optimization |
| **Assertions** | Plan has `claim_type=hypothesis_to_test`; report `forbidden_downstream_uses` includes decision paths |
| **Forbidden outputs** | ROI, lift, optimizer, response curves |

### Golden path 2 — Partial weekly media readiness

| Item | Value |
|------|-------|
| **Source fixture** | `national_weekly_channel_summary` |
| **Adapter** | `build_readiness_input_from_fixture` (or deferred with explicit error until workbench mapping exists) |
| **Workflow** | `build_workflow_readiness_reports` |
| **Report** | `ReadinessAssessmentReport` |
| **Expected governance** | national MMM structurally plausible; GeoX blocked |
| **Missing data** | dma-level geo for GeoX |
| **Assertions** | `blocked_claims` include matched markets, treatment assignment |
| **Forbidden outputs** | fitted MMM, channel ROI |

### Golden path 3 — Valid calibration mapping

| Item | Value |
|------|-------|
| **Source fixture** | `experiment_readout_valid` |
| **Adapter** | `build_calibration_input_from_fixture` |
| **Workflow** | `map_evidence_to_calibration_signal` |
| **Report** | `CalibrationMappingReportEnvelope` |
| **Expected governance** | `mapped`; diagnostic candidate only |
| **Assertions** | `mapped_signal_id` present; `forbidden_downstream_uses` includes `decision_recommendation` |
| **Forbidden outputs** | MMM calibration executed, causal certification |

### Golden path 4 — Missing SE calibration

| Item | Value |
|------|-------|
| **Source fixture** | `experiment_readout_missing_se` |
| **Adapter** | `build_calibration_input_from_fixture` |
| **Workflow** | `map_evidence_to_calibration_signal` |
| **Report** | `CalibrationMappingReportEnvelope` |
| **Expected governance** | `needs_more_data` |
| **Assertions** | `signal is None`; blocking includes missing uncertainty |
| **Forbidden outputs** | calibration candidate promotion without SE |

### Golden path 5 — Metric mismatch calibration

| Item | Value |
|------|-------|
| **Source fixture** | `experiment_readout_metric_mismatch` |
| **Adapter** | `build_calibration_input_from_fixture` |
| **Workflow** | `map_evidence_to_calibration_signal` |
| **Report** | `CalibrationMappingReportEnvelope` |
| **Expected governance** | `incompatible` |
| **Assertions** | `incompatible_metric` blocking; no mapped signal |
| **Forbidden outputs** | forced mapping, decision evidence |

### Golden-path acceptance criteria

- [ ] Each path runs deterministically in CI
- [ ] Each path has dedicated test module under `tests/golden/` or `tests/examples/golden_paths/`
- [ ] Each path asserts absence of forbidden output tokens
- [ ] Each path asserts `governance_status` unchanged through report envelope
- [ ] Paths #3–#5 may ship **before** paths #1–#2 if advisory/readiness adapters are deferred

---

## 10. Notebook and guided-demo prerequisites

**Do not implement** deterministic notebooks or landing-page guided demos until:

| Prerequisite | Status |
|--------------|--------|
| Stage A.3 adapters (minimum: calibration) | Not implemented |
| Report envelope contracts | Not implemented |
| `ArtifactReference` provenance | Not implemented |
| Golden-path tests (#3–#5 minimum) | Not implemented |

**Notebook plan** (`DETERMINISTIC_NOTEBOOK_PLAN_001`) — create **after** this plan merges and calibration golden paths pass.

**Landing-page guided demo binding spec** — docs-only binding table (`demo_journey` → `fixture_id` → `report_type`) may be drafted in parallel **after** report contracts are frozen; **UI implementation** waits for golden paths.

---

## 11. Roadmap sequencing recommendation

| Step | Milestone | Type |
|------|-----------|------|
| 1 | **MIP_REPORT_ADAPTER_AGENT_CONTRACT_PLAN_001** (this document) | Docs ✓ |
| 2 | Report envelope Pydantic models (`deterministic_report_v1`) | Contracts |
| 3 | Stage A.3 calibration adapter | Code |
| 4 | Golden-path tests #3–#5 | Tests |
| 5 | Stage A.3 advisory/readiness adapters (where mapping clear) | Code |
| 6 | Golden-path tests #1–#2 | Tests |
| 7 | Deterministic report generator helpers (envelope builders only) | Code |
| 8 | `ArtifactReference` helper + in-memory registry slice | Code |
| 9 | Deterministic notebook plan | Docs |
| 10 | Deterministic notebook implementation | Examples |
| 11 | Landing-page guided demo binding plan + UI | Product |
| 12 | `LLMExplanationResponse` contract + validator | Contracts |
| 13 | `AgentInputPacket` + agent tool registry plan | Contracts/docs |
| 14 | BYOK/provider integration | Engineering (gated) |
| 15 | Stage B MMM/GeoX engine-backed visuals | Engineering (certified outputs only) |

**Parallelism allowed:** Step 2 (report schemas) and step 3 (calibration adapter) may run in parallel once calibration envelope fields are frozen.

**Explicit block:** Report **generators** (step 7) must not precede report **contracts** (step 2).

---

## 12. Cursor-agent instruction checklist

Reuse for every implementation prompt after this plan:

### Prerequisite checks
- [ ] `git switch main && git pull --ff-only origin main`
- [ ] Verify milestone on main (commit, doc, or test path)
- [ ] Read [contract plan](MIP_REPORT_ADAPTER_AGENT_CONTRACT_PLAN_001.md) and [audit 001](../audits/MIP_AGENT_TOOLING_AND_ROADMAP_IMPLEMENTATION_DETAIL_AUDIT_001.md)

### Branch and mode
- [ ] Branch pattern: `feature/*`, `docs/*`, `data/*`
- [ ] State: implementation vs docs-only

### Allowed files
- [ ] Explicit allow-list per task

### Forbidden
- [ ] No FastAPI/Streamlit changes unless authorized
- [ ] No LLM providers, auth, persistence, connectors
- [ ] No MMM/GeoX execution, ROI/optimizer/response-curve/scenario outputs
- [ ] No mock final dashboards

### Inputs
- [ ] Fixture IDs from Stage A manifest
- [ ] Source docs linked

### Expected outputs
- [ ] Files, tests, doc updates listed

### Governance
- [ ] Preserve `synthetic`, `requires_mmm_or_geox_engine: false`
- [ ] Preserve blocked/needs_more_data status in reports

### Acceptance criteria
- [ ] pytest + ruff + mypy commands and expected pass

### Git
- [ ] Commit message, push branch, PR to `main`, no auto-merge

### Post-merge
- [ ] Delete local branch, completion report

---

## 13. Stop/go criteria

### Safe now (GO)

- This contract plan and follow-on docs (notebook plan, guided demo binding)
- Report envelope Pydantic models after plan merge
- Stage A.3 calibration adapter after envelope fields frozen
- Golden-path tests after adapters + envelopes exist

### Needs more detail (SLOW)

- Deterministic notebooks
- Landing-page guided demo UI
- LLM explanation runtime
- Agent tool registry / LangGraph (P17)
- `sample_key` ↔ `fixture_id` service alignment

### Blocked (STOP)

- ROI / response-curve / optimizer / scenario-planner visuals
- MMM/GeoX engine-backed outputs (Stage B)
- Production data ingestion, auth, BYOK in public demo
- LLM providers without `LLMExplanationResponse` validator and eval harness
- Report generators before report contracts
- Agent runtime without `AgentValidationReport` gate

---

## Related documents

- [Agent tooling audit 001](../audits/MIP_AGENT_TOOLING_AND_ROADMAP_IMPLEMENTATION_DETAIL_AUDIT_001.md)
- [Roadmap execution sequence](../roadmap/ROADMAP_EXECUTION_SEQUENCE.md)
- [Repo integration strategy](REPO_INTEGRATION_STRATEGY.md)
- [Synthetic demo dataset strategy](../product/SYNTHETIC_DEMO_DATASET_STRATEGY_PLAN_001.md)
- [P12 SDK/API usage examples](../examples/P12_SDK_API_USAGE_EXAMPLES_001.md)
- [Stage A fixture README](../../examples/fixtures/stage_a/README.md)
- [Deterministic usage modes](../service/DETERMINISTIC_USAGE_MODES.md)
