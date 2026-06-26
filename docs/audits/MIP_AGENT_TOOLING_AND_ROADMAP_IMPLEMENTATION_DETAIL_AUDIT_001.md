# MIP Agent Tooling and Roadmap Implementation Detail Audit 001

## 1. Title and status

| Field | Value |
|-------|-------|
| **Title** | MIP Agent Tooling and Roadmap Implementation Detail Audit 001 |
| **Status** | Audit complete |
| **Type** | Agent tooling / roadmap executability / implementation-detail gap audit |
| **Base commit** | `1eef281` — Stage A.2 fixture loader helpers merged (PR #34) |
| **Date** | 2026-05-28 |
| **Scope** | Docs + code review only; no runtime or product changes |

**Hard boundaries (unchanged):** No MMM/GeoX execution, no LLM providers, no production ingestion, no new API routes, no mock advanced dashboards, no unsupported causal/ROI claims.

---

## 2. Executive summary

### Are future agents provided with sufficient tools today?

**Verdict: `mostly_ready_with_minor_gaps` for deterministic Cursor implementation; `needs_detail_before_implementation` for LLM/agent runtime.**

MIP already gives future agents a **strong deterministic spine**: typed Pydantic contracts, workflow helpers, FastAPI service with OpenAPI/response tests, Stage A synthetic fixtures, Stage A.2 loader helpers, P12 SDK/API examples, P8b agent handoff contracts, P7b LLM explanation governance contracts, and extensive forbidden-claim tests. A Cursor agent implementing **docs-only work**, **fixture/tests**, or **deterministic workflow wiring** can usually proceed without inventing business logic.

Gaps appear where **report output contracts**, **fixture→workflow adapters**, **service/fixture ID alignment**, **notebook/landing-page binding specs**, and **LLM/agent runtime orchestration** are still underspecified. Without those, agents may hardcode paths, duplicate rendering logic, or blur governance boundaries when building user-facing narratives.

### Where tools are adequate

- Contracts and workflows for advisory, readiness, calibration mapping, intake routing
- Service API surface (`/advisory/cold-start`, `/readiness/assess`, `/calibration/map`, `/intake/overview`) with governance blocks
- Stage A fixtures + `mip.examples.stage_a_fixtures` loaders
- P12 usage patterns; deterministic usage modes doc
- Agent role / failure / validation contracts (P8b) and recovery helpers
- LLM explanation **request/plan** governance (P7b), disabled by default
- No-mock-final-dashboard rule and Stage B deferral

### Where tools are missing or incomplete

- Unified **report generation** helpers and stable human-readable export contracts
- **Stage A fixture → contract** adapters (business profile, readiness summary → workbench)
- Service API still keyed on `app.demo_fixtures` sample keys, not Stage A `fixture_id`s
- Notebook file plan lacks per-notebook acceptance criteria and golden outputs
- Landing-page guided demo lacks fixture/journey binding table with expected artifacts
- `LLMExplanationResponse`, `AgentInputPacket`, `ReportGenerationRequest/Result` not defined
- Agent manifests not integrated with FastAPI service or public demo
- Golden harness / agent safety tests for end-to-end agent prompts not yet present

### Are roadmap items detailed enough for Cursor?

| Area | Detail level |
|------|----------------|
| P10–P12, Stage A, Stage A.2 | **Ready** — clear files, tests, boundaries |
| Deterministic notebooks | **Needs detail** — listed in strategy/P12 but no plan doc with AC |
| Landing-page guided demos | **Needs detail** — product plan defines journeys, not implementation AC |
| LLM explanation runtime | **Blocked until tooling** — contracts exist; provider/BYOK/auth deferred |
| LangGraph / P17 agents | **Blocked until tooling** — P8b contracts exist; runtime deferred |
| Stage B MMM/GeoX visuals | **Blocked until certified engines** — correctly deferred |
| Production ingestion / auth | **Too vague** — intentionally deferred; must not be guessed |

### What must be fixed before LLM/agent implementation?

1. Deterministic **report output contract plan** (human + machine views)
2. **Fixture→workflow adapter** plan for Stage A (beyond raw JSON load)
3. **Cursor prompt template** adoption (checklist in §8) across roadmap items
4. **Notebook plan** with per-notebook inputs, outputs, forbidden claims, tests
5. **LLMExplanationResponse** and governed payload assembly spec (8G alignment)
6. **Agent tool registry** mapping roles → allowed deterministic functions
7. Golden scenarios / agent eval harness before live provider wiring

---

## 3. Current adequate foundations

| Foundation | Evidence | Agent value |
|------------|----------|-------------|
| Typed contracts | `src/mip/contracts/*` | Agents call stable schemas; validators encode governance |
| Deterministic workflows | `src/mip/workflows/intake/*`, `readiness/*` | Business logic not invented in UI/API layer |
| FastAPI service | `src/mip/service/*`, `tests/service/*` | HTTP examples with contract tests |
| OpenAPI / response tests | `test_openapi_contract.py`, `test_response_contracts.py` | Prevents route/schema drift |
| Stage A fixtures | `examples/fixtures/stage_a/**`, manifest | Canonical synthetic inputs |
| Stage A.2 loaders | `mip.examples.stage_a_fixtures` | CWD-independent discovery/load |
| P12 examples | `docs/examples/P12_SDK_API_USAGE_EXAMPLES_001.md` | Copy-paste safe patterns |
| Governance boundaries | Contract validators, `blocked_claims`, service `governance` fields | Reduces unsafe agent output |
| Public demo boundaries | P9b record, Streamlit deterministic mode | Clear non-production scope |
| No-mock-final-dashboard rule | Synthetic dataset strategy §7 | Prevents fake ROI/optimizer visuals |
| Agent contracts (P8b) | `AgentRunManifest`, `AgentFailurePacket`, `AgentValidationReport` | Typed handoffs for future runtime |
| LLM explanation governance (P7b) | `LLMExplanationRequest`, `LLMExplanationPlan` | Provider mode gating |
| Agent recovery helpers | `mip.workflows.intake.agentic_recovery` | Failure/retry patterns without execution |

---

## 4. Agent/tooling gap matrix

| Capability | Needed by future agent? | Current artifact/tool | Gap | Risk if not fixed | Recommended next action | Priority |
|------------|-------------------------|----------------------|-----|-------------------|-------------------------|----------|
| Fixture discovery/loading | Yes | `mip.examples.stage_a_fixtures`, manifest | None for load; no workflow adapters | Agents duplicate mapping logic | Stage A.3 fixture→contract adapters plan | P1 |
| Cold-start advisory report generation | Yes | `build_cold_start_advisory_plan`, `ColdStartAdvisoryPlan`, service route | No stable markdown/HTML export; Stage A profiles not wired to plan builder | Inconsistent demo reports | Report output contract plan + thin renderer helper | P1 |
| Readiness report generation | Yes | `build_workflow_readiness_reports`, service route | Stage A readiness summaries ≠ workbench input | Agents cannot use Stage A readiness fixtures end-to-end | Adapter from summary → workbench or documented gap | P1 |
| Calibration mapping report generation | Yes | `map_evidence_to_calibration_signal`, Stage A calibration fixtures | Works via loader + contracts | Low if P12 pattern followed | Document canonical fixture IDs in agent checklist | P2 |
| Intake/routing report generation | Yes | `recommend_intake_path`, `IntakePathRecommendation` | Stage A intake fixtures are narrative, not `MeasurementIntakeSession` | Agents invent session shapes | Intake fixture→session adapter or explicit “routing-only” label | P1 |
| Trust/governance summary generation | Yes | `TrustReport` assembly, gates, `AgentValidationReport` | No single “governance summary” helper for demos | Fragmented explanations | `build_governance_summary` plan (docs first) | P2 |
| Unsupported-claim detection | Yes | Contract validators, governance fixtures, LLM blocked topics | Not exposed as one callable tool | Agents miss edge phrasing | Expose `validate_forbidden_claims` tool wrapper (docs plan) | P2 |
| Missing-data checklist generation | Yes | Advisory `tracking_checklist`, readiness `blocking_reasons` | No unified checklist contract across workflows | Incomplete user guidance | Missing-data checklist contract in report plan | P2 |
| API/service usage examples | Yes | P12 doc, `tests/service/*` | Service uses demo `sample_key`, not Stage A ids | Two parallel fixture namespaces | Align or document mapping table | P2 |
| Notebook usage examples | Yes | P12 §10 future list only | No notebooks, no AC | Agents invent notebook structure | Deterministic notebook plan doc | P1 |
| Landing-page guided demo data binding | Yes | Product entrypoint plan journeys | No fixture_id / artifact binding table | Wrong demo data wired | Guided demo binding spec (docs) | P1 |
| LLM explanation input packet | Yes | `LLMExplanationRequest`, governed input refs | No single builder from workflow outputs | Incomplete payloads | `build_llm_explanation_request` from artifacts (spec) | P2 |
| LLM explanation output contract | Yes | `LLMExplanationPlan`, provider interfaces | No `LLMExplanationResponse` with claim guards | Ungoverned narrative | Define response contract in 8G plan | P2 |
| Agent run manifest | Yes | `AgentRunManifest` contract + builders in `agentic_recovery` | Not used in service/demo paths | Orphan contract | Wire manifest into future agent runtime plan only | P3 |
| Agent failure packet | Yes | `AgentFailurePacket` + builders | Same | Same | Document when to emit in agent checklist | P3 |
| Agent validation report | Yes | `AgentValidationReport` + builders | Same | Same | Require before user-facing LLM answers (already in P8b) | P2 |
| Safe retry policy | Yes | `AgentRetryPolicy`, recovery helpers | Not integrated with service | Unsafe retries | Keep deferred; document allowed retries in checklist | P3 |
| Artifact registry | Partial | `EvidenceRegistry`, adapter governance | Not a general demo artifact registry | Agents lose lineage | Use existing registry patterns; document | P3 |
| Report export format | Yes | JSON via Pydantic; Streamlit renderers in `app/ui_renderers.py` | No stable Markdown/PDF contract | Inconsistent exports | Report export contract plan | P1 |
| Benchmark/reference schema mapping | Partial | Synthetic strategy §5 references | No adapter map file | Schema guesswork | Reference mapping doc (Robyn/Meridian/GeoLift as refs only) | P3 |
| Future MMM engine handoff | Later | Adapters 6A–6C, sibling fixtures 8B | Live execution blocked | Fake engine outputs | Keep blocked per repo strategy | — |
| Future GeoX engine handoff | Later | GeoX adapter placeholders | Same | Same | Keep blocked | — |

---

## 5. Roadmap implementation-detail gap matrix

| Roadmap item | Current detail level | Can Cursor implement safely? | Missing specifics | Required acceptance criteria | Recommended fix |
|--------------|---------------------|------------------------------|-------------------|------------------------------|-----------------|
| Stage A.2 fixture loader helpers | **Implemented** (`mip.examples.stage_a_fixtures`) | Yes | Service/demo still use `sample_key` | Load all manifest entries; CWD-independent | Document dual-key mapping; optional service alias |
| Stage A.3 fixture→workflow adapters | Not planned as named phase | **No** — would guess | Adapter functions per workflow area | Each adapter has tests; no engine execution | Add plan doc before implementation |
| Deterministic notebook planning | Listed in P12/strategy | **Partial** | Per-notebook IO, tests, forbidden claims | Notebook runs in CI; outputs match contracts | `DETERMINISTIC_NOTEBOOK_PLAN_001.md` |
| Deterministic notebook implementation | Future | **No** until plan | File paths, kernel, poetry env | Same as plan | After plan merged |
| Landing-page guided demos | Product plan §4–8 | **Partial** | Fixture binding, Streamlit layout AC | Journey → fixture_id → artifact type table | Guided demo implementation plan |
| LLM explanation layer | P7b contracts; runtime deferred | **No** for providers | Response contract, payload builder, eval | No provider calls in public demo | 8G explanation payload plan |
| BYOK/provider plan | Documented deferral | **No** | Auth, cost, rate limits | P11 hosted hardening first | Keep blocked |
| Agent run manifests / failure / validation | P8b implemented contracts | **Partial** for wiring | Runtime integration, LangGraph boundaries | Manifest on every agent step | P17 plan references P8b only |
| Report/artifact generation | Workflow outputs only | **Partial** | Export contract, inventory helper | Stable JSON schema for reports | Report output contract plan |
| MMM/GeoX handoff adapters | 8A–8F fixture bridge | **No** for live | Golden scenarios, 8G–8N | No live subprocess | Keep blocked |
| Stage B engine-backed outputs | Strategy §6 | **No** | Certified engine path | Real artifacts + TrustReport | Keep blocked |
| Dashboard visuals | Entrypoint plan | **No** | Engine outputs required | No mock charts | Keep blocked |
| Scenario planner / optimizer / DecisionSurface | ADR + gates | **No** | Governed DecisionSurface | Gate tests pass | Keep blocked |
| Production data ingestion | I11 deferred | **No** | Security, persistence | No raw upload in public path | Keep blocked |
| Auth/security / deployment hardening | P11 partial | **Partial** | Hosted API auth | Contract tests for errors | P11 hosted phase plan |

---

## 6. Report-generation readiness

| Report type | Classification | Notes |
|-------------|----------------|-------|
| Human-readable advisory report | **Possible but no helper** | `ColdStartAdvisoryPlan` exists; Streamlit renders ad hoc |
| Readiness report | **Already possible** | `BaseWorkflowReadinessReport` list from workbench |
| Calibration report | **Already possible** | `CalibrationMappingReport` from mapping helper |
| Intake routing report | **Already possible** | `IntakePathRecommendation` |
| Governance/blocked claim report | **Possible but no stable output contract** | Scattered across contracts/tests; governance fixture is educational JSON |
| Developer/API usage report | **Already possible** | OpenAPI + P12 patterns + service tests |
| Fixture inventory report | **Already possible** | `load_stage_a_manifest()` + manifest fields |

**Deferred for governance reasons:** ROI, optimizer, response-curve, scenario, DecisionSurface, causal lift, matched-market, power/MDE reports.

---

## 7. Future LLM/agent tool contract needs

Audit recommendation — **define in plans, do not implement in this audit:**

| Contract | Should receive | Should return | Notes |
|----------|--------------|---------------|-------|
| `AgentRunManifest` | workflow id, step, input refs, package version | status, warnings, blocking reasons | Exists; wire at runtime later |
| `AgentInputPacket` | user question, maturity, available data refs, fixture ids | normalized routing context | **Missing** — recommend add to P17 plan |
| `AgentAllowedAction` / `AgentBlockedAction` | role, workflow area, evidence tier | enumerated actions + rationale | Partially in `AgentPermissionBoundary` |
| `AgentFailurePacket` | exception, validation errors, context refs | safe retry hints | Exists |
| `AgentValidationReport` | candidate narrative + artifact refs | approve/block + forbidden claims | Exists |
| `AgentArtifactReference` | artifact id, type, evidence tier | URI/path contract | Partial via registry |
| `LLMExplanationRequest` | governed payload refs, provider config | readiness status | Exists |
| `LLMExplanationResponse` | model text (future) | claim-labeled sections, preserved warnings | **Missing** |
| `ReportGenerationRequest` | artifact type, format, audience | — | **Missing** |
| `ReportGenerationResult` | — | body, format, evidence labels, blocked sections | **Missing** |

Agents must **never** receive raw production rows by default (`AgentFailurePacket` / P8b rules already steer this).

---

## 8. Cursor-agent executability checklist

Every future Cursor implementation prompt for MIP should include:

### Prerequisite checks
- [ ] `git switch main && git pull --ff-only origin main`
- [ ] Verify named milestone on main (commit, doc path, or test path)
- [ ] Run targeted pytest + ruff + mypy before starting

### Allowed scope
- [ ] Explicit file allow-list (e.g. `src/mip/examples/*`, `docs/*`, `tests/examples/*`)
- [ ] Branch name pattern (`feature/*`, `data/*`, `docs/*`, `audit/*`)

### Forbidden scope
- [ ] No new FastAPI routes unless explicitly authorized
- [ ] No Streamlit behavior change unless explicitly authorized
- [ ] No LLM providers, BYOK, auth, secrets, persistence, external connectors
- [ ] No MMM fitting, GeoX inference, ROI/optimizer/response-curve/scenario outputs
- [ ] No mock final dashboards
- [ ] No production readiness claims

### Input docs
- [ ] Link strategy/plan docs (e.g. synthetic dataset strategy, P12, product entrypoint)
- [ ] Link audit or ADR when touching agents/governance

### Expected outputs
- [ ] Files to create/modify listed by path
- [ ] Tests to add with behavior described
- [ ] Doc updates enumerated

### Governance boundaries
- [ ] `synthetic: true` for demo fixtures
- [ ] `requires_mmm_or_geox_engine: false` for Stage A
- [ ] Preserve “MIP is control plane, not statistical engine”

### Acceptance criteria
- [ ] Test commands and expected pass counts
- [ ] Boundary checks (forbidden claims, no engine execution)

### Git workflow
- [ ] Commit message format
- [ ] Push branch name
- [ ] PR target `main`; no auto-merge unless reviewed

### Post-merge cleanup
- [ ] Delete local feature branch after merge
- [ ] Completion report template

---

## 9. Recommendations (prioritized)

| # | Action | Type | Rationale |
|---|--------|------|-----------|
| 1 | **Stage A.3 fixture→workflow adapter plan** | Docs | Closes biggest deterministic gap after loaders |
| 2 | **Deterministic report output contract plan** | Docs | Stabilizes human-readable outputs for agents/notebooks |
| 3 | **Report generator helper implementation** | Code (small) | Thin wrappers over existing plans/reports |
| 4 | **Deterministic notebook plan** (`01`–`04` from P12) | Docs | Prevents notebook guesswork |
| 5 | **Notebook implementation** | Examples | After plan AC merged |
| 6 | **Landing-page guided demo binding spec** | Docs | Links journeys → fixture_id → artifact |
| 7 | **LLM explanation response contract plan (8G alignment)** | Docs | Before any provider wiring |
| 8 | **Agent runtime / LangGraph plan (P17)** using P8b contracts | Docs | Before agent execution |
| 9 | BYOK/provider implementation | Engineering | Only after auth + eval harness |
| 10 | Stage B MMM/GeoX engine-backed outputs | Engineering | Only after certified engines |

---

## 10. Stop/go criteria

### Safe to implement next (GO)

- Docs-only plans (report contract, notebook plan, guided demo binding, Stage A.3 adapters)
- Thin deterministic helpers that **wrap existing** `mip.workflows.*` without new claims
- Tests and examples using Stage A loaders + P12 patterns
- Service/doc alignment (sample_key ↔ fixture_id mapping table)

### Requires more detail first (SLOW)

- Deterministic notebooks (need plan + golden outputs)
- Landing-page UI changes (need binding spec + AC)
- LLM explanation runtime (need response contract + eval)
- LangGraph agent orchestration (need tool registry + manifest wiring spec)
- Production ingestion, auth, hosted API hardening

### Blocked until deterministic tools exist (STOP)

- Live LLM providers in public demo
- Autonomous multi-step agents without `AgentValidationReport`
- User-facing narratives without governed payload assembly

### Blocked until MMM/GeoX certified outputs exist (STOP)

- Channel ROI, response curves, optimizer, scenario planner, DecisionSurface visuals
- Stage B synthetic/engine-backed dashboard demos
- Causal lift, matched markets, power/MDE product claims

---

## Related documents

- [Roadmap execution sequence](../roadmap/ROADMAP_EXECUTION_SEQUENCE.md)
- [Roadmap execution audit 001](ROADMAP_EXECUTION_AUDIT_001.md)
- [Repo integration strategy](../architecture/REPO_INTEGRATION_STRATEGY.md)
- [Product entrypoint plan](../product/PRODUCT_ENTRYPOINT_AND_DEMO_EXPERIENCE_PLAN_001.md)
- [Synthetic demo dataset strategy](../product/SYNTHETIC_DEMO_DATASET_STRATEGY_PLAN_001.md)
- [P12 SDK/API usage examples](../examples/P12_SDK_API_USAGE_EXAMPLES_001.md)
- [P11 API hardening plan](../service/P11_API_HARDENING_AND_SERVICE_PACKAGING_PLAN_001.md)
- [Stage A fixture README](../../examples/fixtures/stage_a/README.md)
