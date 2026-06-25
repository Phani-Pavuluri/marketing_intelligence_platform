# Roadmap Execution Sequence

Condensed implementation sequence derived from [ROADMAP_EXECUTION_AUDIT_001.md](../audits/ROADMAP_EXECUTION_AUDIT_001.md).

**Current main:** `d89bc6d`  
**Immediate next phase:** **P7** — Streamlit/local workflow shell

## What is already implemented

| Layer | Status |
|-------|--------|
| P1 intake session + path recommendation (I1–I2) | ✓ |
| P2 required data assets + sample schemas (I3) | ✓ |
| P3 DataSourceRef + intake manifest (I5) | ✓ |
| P4 column mapping + semantic confirmation (I6) | ✓ |
| P4b experiment design objective + data requirements (I6b) | ✓ |
| P4c common intake workbench + preliminary profiling (I6c) | ✓ |
| P5 workflow-specific readiness reports (I7–I8) | ✓ |
| P5b general advisory / cold-start planning (I8b) | ✓ |
| P6 CalibrationSignal intake mapping (I9) | ✓ |
| Contracts, gates, TrustReport, evidence registry | ✓ |
| LLM Phase 1–5D (safety, intake, readiness, configs, orchestrator, CLI, MockLLM, Streamlit shell) | ✓ |
| Adapters 6A–6C, orchestration 7A–7C, static sibling bridge 8A–8F | ✓ |
| Roadmap docs: 8G–8N, P1–P13, S1–S12, G1–G20, I1–I15 | ✓ documented |

## Platform principles

**Common intake first, workflow-specific readiness second.**

MIP uses **one Common Data Intake Workbench** for MMM, GeoX/experiment design, CalibrationSignal intake, and decision-review workflows. Data is uploaded, connected, or declared **once**; MIP profiles, maps, snapshots, and routes it into workflow-specific readiness checks.

The user should **not** need separate MMM and GeoX upload flows. The LLM is the **conversational interface** over common intake and workflow-specific readiness—not the owner of raw data analysis or causal design decisions.

**Explicitly rejected:**

- Separate MMM upload flow · separate GeoX upload flow
- Duplicated column mapping logic · duplicated profiling logic
- LLM answers from raw files

The LLM must answer data-grounded questions only from governed profile summaries, readiness reports, diagnostic reports, and `TrustReport`s. LangGraph may route workflow state but must not expose raw dataframes to the LLM.

## Execution themes → roadmap tracks

| Theme | Tracks | Phase |
|-------|--------|-------|
| T1 Core semantics | S1–S12 | P4+ |
| T2 LLM-guided intake | I1–I3 | **P1–P2** |
| T3 Manifests | I4–I5, P8 | P3 |
| T4 Experiment design intake | I6b, MMM→GeoX bridge | **P4b** |
| T5 Common intake workbench | I6c, workflow support assessment | **P4c** |
| T6 Workflow-specific readiness | I7–I8 | **P5** |
| T6b General advisory / cold-start | I8b | **P5b** |
| T7 CalibrationSignal | I9 | P6 |
| T8 Product UI | I10, I15 | P7 |
| T9 Demo profiling impl | I4, I7 | P8 |
| T10 LangGraph orchestration | Agentic governance | **P17** |
| T11 Lifecycle / current-state | P1, G11, G16 | P11 |
| T12 LLM answer governance | 8G–8N, G12–G20 | P12 |
| T13 Refresh governance | I12, P1 | P10 |
| T14 Golden scenarios | G1–G3, 8N | P13 |
| T15 Production hardening | I11, I13–I14 | P9 (table-ref design) |
| T16 Live execution / optimizer | Phase 8+, P14–P15 | P15–P16 deferred |

## Dependency chain (summary)

```text
P1 session/path
  → P2 required assets/sample schemas
  → P3 data source refs/manifests
  → P4 column mapping/semantic confirmation
  → P4b experiment design objective/KPI/data requirement contracts
  → P4c Common Data Intake Workbench + preliminary profiling contracts
  → P5 workflow-specific readiness reports (MMM / GeoX / CalibrationSignal / decision-review)
  → P5b general advisory and cold-start planning contracts
  → P6 CalibrationSignal intake mapping
  → P7 Streamlit/local workflow shell
  → P8 local/demo profiling implementation
  → P17 LangGraph/stateful orchestration skeleton (after contracts stabilize)
  → later panel_exp/MMM diagnostic execution / export handoff (gated)
```

## Implementation phases (P0–P17)

| Phase | Goal | Runtime allowed |
|-------|------|-----------------|
| **P0** | Roadmap audit ✓ | None |
| **P1** | I1–I2 intake session + path recommendation | Contracts/fixtures only | ✓ implemented |
| **P2** | I3 required data assets | Contracts/fixtures only | ✓ implemented |
| **P3** | I5 DataSourceRef + manifest | In-memory records | ✓ implemented |
| **P4** | I6 column mapping + semantic confirmation | Contracts/fixtures only | ✓ implemented |
| **P4b** | Experiment design objective + KPI/data requirement contracts | Contracts/fixtures only | ✓ implemented |
| **P4c** | **Common Data Intake Workbench** + preliminary profiling contracts | Summary records only; shared by MMM and GeoX | ✓ implemented |
| **P5** | **Workflow-specific** readiness report contracts (I7–I8) | Builds on P4c workbench | ✓ implemented |
| **P5b** | **General advisory** and cold-start planning contracts (I8b) | Routes users not ready for formal measurement | ✓ implemented |
| **P6** | I9 CalibrationSignal mapping | Fixture validation | ✓ implemented |
| **P7** | I10 Streamlit/local workflow shell | Display only |
| **P8** | I4 demo upload + profiling implementation | Sandbox CSV only |
| **P9** | I11 production table-ref design | Design only |
| **P10** | I12 refresh governance | No model execution |
| **P11** | P1/G11/G16 lifecycle selection | Registry metadata |
| **P12** | 8G–8H LLM answer governance | MockLLM only |
| **P13** | G1–G3 golden harness | Fixture tests |
| **P14** | S6/G9 decision packet | Assembly only |
| **P15** | P6–P7 optimizer governance | **No optimizer execution** |
| **P16** | Live execution gate review | **Deferred** |
| **P17** | LangGraph / stateful workflow orchestration skeleton | Governed tool routing only |

> **Note:** Integer **P9** remains production table-reference design. LangGraph orchestration is **P17**.

## Common Data Intake Workbench (P4c)

**Purpose:** One shared intake layer before workflow-specific readiness branches.

**Shared responsibilities (future):**

Source registration · upload/connect/declaration modes · data source refs · intake manifests · column mapping · semantic confirmation · snapshot metadata · basic profiling summaries · time/geo coverage · metric/media/control availability · missingness summaries · grain/scope detection · LLM-safe data summary reports · **WorkflowSupportAssessment**

**Supports readiness for:** MMM · GeoX/experiment design · CalibrationSignal intake · decision-review

**Future contracts:**

`CommonIntakeWorkbench` · `CommonDataIntakeSession` · `DataSnapshot` · `SourceIngestionRecord` · `IngestionMode` · `IngestedAssetRecord` · `CommonDataProfileSummary` · `MetricAvailabilitySummary` · `GeoCoverageSummary` · `TimeCoverageSummary` · `MediaCoverageSummary` · `ControlCoverageSummary` · `WorkflowSupportAssessment` · `WorkflowReadinessRoute` · `LLMAnswerGroundingContext` · `PreliminaryAnalysisReport`

**WorkflowSupportAssessment** answers: which workflows can this data support? which are blocked? what grain/KPI/source is missing? what diagnostic should run next?

Example statuses: `supports_national_mmm` · `supports_geo_level_mmm` · `supports_geox_design_diagnostics` · `supports_calibration_signal_intake` · `blocked_needs_geo_level_outcome` · `blocked_needs_geo_level_media` · `blocked_needs_calibration_uncertainty` · `blocked_needs_metric_mapping`

**Important distinction:** Common profiling assesses **structural suitability** for the next step. It must **not** claim experiment design is valid, powered, or feasible. **panel_exp/GeoX** owns power, MDE, matchability, and design feasibility. **MMM** owns MMM model and calibration diagnostics.

### Same data, different workflow support (examples)

**National weekly data** (`week, country, product, channel, spend, impressions, conversions`):

> May support national MMM intake. Does **not** support DMA-level GeoX design—DMA/geo-level outcome and media are missing.

**DMA-week data** (`week, dma, product, platform, campaign, spend, impressions, visits, conversions`):

> May support GeoX design diagnostics for a DMA-level test. May support geo-level MMM if enough history and media variation exist. For awareness objectives, visits may be usable but BSV/branded search is not present. For conversion objectives, conversions are present but sparsity must be profiled.

**Experiment readout data** (`experiment_id, metric_id, estimand_id, channel, geo_scope, effect_estimate, standard_error, time_window`):

> May support CalibrationSignal intake if metric, estimand, scope, effect, and uncertainty are valid. **Not** sufficient alone for MMM modeling or new GeoX design.

## P5 — Workflow-specific readiness branching

**Status:** ✓ implemented — structural readiness reports only (`MMMDataReadinessReport`, `GeoXDesignReadinessReport`, `CalibrationSignalReadinessReport`, `DecisionReviewReadinessReport`, `build_workflow_readiness_reports`). Engine diagnostics, CalibrationSignal transformation, TrustReport approval, and decision recommendations remain deferred.

After common intake/profiling (P4c), readiness **branches by workflow**:

| Branch | Decides |
|--------|---------|
| **MMM readiness** | Time grain; historical coverage; media channels over time; outcome/media scope alignment; controls/promos/seasonality; calibration evidence; national vs geo-level vs calibrated vs refresh vs decision-surface candidate |
| **GeoX / experiment-design readiness** | Geo/DMA/market grain; outcome at geo-time level; media at geo-time level; pre-period data for design diagnostics; geo coverage; KPI vs objective alignment; whether panel_exp should run design diagnostics |
| **CalibrationSignal readiness** | Effect estimate + uncertainty; metric/estimand/channel/geo/time mapping; structured enough for `CalibrationSignal`; governed vs stale vs blocked |
| **Decision-review readiness** | `TrustReport` present; evidence alignment; metric/estimand/scope/freshness; human approval; blocked vs diagnostic vs decision-supporting |

**Why P5b follows P5:** P5 workflow-specific readiness reports determine whether the user is structurally ready for MMM, GeoX, CalibrationSignal, or decision-review workflows. If the user is **not** ready for formal measurement but still needs guidance, MIP should route them to **advisory/cold-start planning** rather than forcing an MMM or GeoX workflow.

## P5b — General advisory and cold-start planning

**Status:** ✓ implemented — advisory contracts and deterministic helpers (`build_cold_start_advisory_plan`, `build_cold_start_business_profile`, `infer_advisory_evidence_mode`, `build_traffic_source_signals`, `suggest_channel_candidates`, `build_channel_hypotheses`, `build_tracking_readiness_checklist`, `build_starter_measurement_plan`, `build_learning_agenda`). Outputs are labeled by evidence mode and claim type; ROI, causal lift, optimal mix, and decision authorization remain blocked.

**Purpose:** Broader advisory lane for users who are not yet measurement-ready. Covers SMB paid media, no-data channel planning, business-profile-driven hypotheses, website traffic/source-informed advisory, tracking setup, and learning agendas—not only formal MMM/GeoX paths.

### Architecture statement

The platform supports **advisory reasoning before formal measurement exists**. LLM general knowledge may be used to ask better questions and produce clearly labeled advisory hypotheses. When governed customer data summaries exist, data analysis modules may make the answer data-informed. MMM, GeoX, CalibrationSignal, and `TrustReport` remain required for measured, causal, or decision-supporting claims.

**Evidence hierarchy:**

```text
General knowledge
  → business profile
  → customer data summaries
  → measured diagnostics
  → TrustReport-authorized decision support
```

Referral traffic, organic search, direct traffic, email traffic, CRM data, and sales summaries may inform cold-start hypotheses, but they do **not** authorize causal or ROI claims. Advisory outputs must be labeled as **hypotheses to test** unless supported by measured diagnostics and `TrustReport` governance.

The LLM is allowed to use general marketing knowledge when no customer data exists, but the answer must say that it is **advisory-only** and should identify what data or tracking would increase confidence.

### Advisory evidence modes

`AdvisoryEvidenceMode`:

| Mode | Definition |
|------|------------|
| `general_knowledge_only` | LLM uses broad marketing knowledge and customer-provided business details. No customer data is available. |
| `business_profile_only` | LLM uses structured business profile details such as product, audience, geography, budget, margin, sales cycle, and objective. |
| `data_informed_advisory` | LLM uses governed customer data summaries such as website traffic source profile, CRM summary, sales summary, or common intake profile. Still not causal. |
| `measured_diagnostic` | LLM explains governed MMM, GeoX, calibration, or readiness diagnostic outputs. |
| `causal_decision_support` | LLM explains `TrustReport`-authorized decision-supporting outputs only. |

### Claim types

`AdvisoryClaimType`:

| Claim type | Allowed when |
|------------|--------------|
| `general_marketing_guidance` | General advisory |
| `hypothesis_to_test` | General advisory |
| `data_informed_hypothesis` | Data-informed advisory |
| `measured_observation` | Measured diagnostic |
| `diagnostic_explanation` | Measured diagnostic |
| `causal_claim` | `TrustReport`-authorized workflows only |
| `decision_recommendation` | `TrustReport`-authorized workflows only |

### Evidence levels

`EvidenceLevel`:

`no_customer_data` · `business_profile_signal` · `organic_interest_signal` · `organic_conversion_signal` · `search_intent_signal` · `referral_interest_signal` · `crm_signal` · `sales_signal` · `paid_test_signal` · `experiment_signal` · `mmm_signal` · `trust_report_authorized`

**Rules:**

- Recommendations based on business details alone → `no_customer_data` or `business_profile_signal`.
- Recommendations based on website traffic → `organic_interest_signal`, `organic_conversion_signal`, `search_intent_signal`, or `referral_interest_signal`.
- Recommendations based on paid test data → `paid_test_signal`.
- Only experiment/MMM/`TrustReport` outputs → measurement-backed or decision-supporting labels.

### Cold-start readiness statuses

`ColdStartAdvisoryStatus`:

`needs_business_details` · `needs_tracking_setup` · `advisory_plan_ready` · `ready_for_basic_tracking` · `ready_for_starter_test` · `not_ready_for_mmm` · `not_ready_for_geox` · `ready_for_data_collection` · `ready_for_reassessment`

### Readiness-to-measure ladder

```text
Advisory
  → tracking setup
  → starter test
  → paid readout
  → experiment / MMM later
```

### Future contracts

**Business profile and objectives:**

- `ColdStartBusinessProfile` — `business_type`, `product_or_service`, `B2B_or_B2C`, `average_order_value`, `gross_margin`, `sales_cycle_length`, `geography`, `target_audience`, `monthly_budget`, `primary_objective`, `secondary_objectives`, `existing_website`, `existing_tracking`, `creative_assets_available`, `customer_list_available`, `organic_channels_available`, `seasonality_context`, `constraints`
- `ColdStartMediaObjective` — awareness · traffic · lead_generation · sales · app_installs · store_visits · retention · repeat_purchase · market_launch · product_launch

**Channel suitability:**

- `ChannelCandidate` · `ChannelSuitabilityAssessment` · `ColdStartChannelHypothesis` · `StarterMediaMixHypothesis`

Channel candidates include: Google Search · Google Performance Max · Meta/Instagram · TikTok · YouTube · LinkedIn · Pinterest · Reddit · Display · CTV · Email/CRM · SEO/content · Creators/influencers · Affiliate/partnerships · Retargeting · Local listings/maps · Marketplaces

**Rules:** Channel hypotheses are advisory only unless backed by measured diagnostics. The platform may say a channel is a reasonable test candidate. The platform must **not** say a channel is ROI-optimal without measured evidence.

**Website traffic source advisory** (Organic Demand Signal Assessment):

- `WebsiteTrafficSourceProfile` · `TrafficSourceSignal` · `OrganicDemandSignal` · `ReferralInterestSignal` · `SearchIntentSignal` · `TrafficConversionSignal`

Allowed inputs (later): source/medium · default channel group · landing page · geography · device · new vs returning · sessions · engaged sessions · conversion events · leads · purchases · revenue · conversion rate · organic search queries · referral domains · social referrals · email traffic · direct traffic · UTM coverage

**Guardrail:** Website referral/social/organic traffic can suggest where to test first, but it cannot prove paid channel ROI or optimal media mix.

**Allowed example:** *Instagram referral traffic shows organic audience interest, so Meta/Instagram may be a reasonable small paid test candidate. Paid performance is unproven and should be validated with tracking and a limited test.*

**Disallowed example:** *Instagram referral traffic proves Meta is your best paid channel.*

**Tracking and learning agenda:**

- `TrackingReadinessChecklist` · `StarterMeasurementPlan` · `LearningAgenda` · `ReassessmentPlan`

Covers: UTM setup · pixel/tag setup · conversion events · lead capture · CRM/customer list · landing-page readiness · budget/timebox for initial test · primary KPI · secondary KPI · guardrail metrics · weekly reporting cadence · criteria for scaling/stopping · when to reassess · when to route to GeoX/MMM later

### Budget maturity handling

$500/month and $50K/month need different advice. Budget maturity should influence channel mix hypotheses, test scope, and learning agenda—not ROI claims.

### Example flows

**Example 1 — No data, business profile only**

User: *I sell handmade skincare online. I have $2,000/month. What channels should I start with?*

Allowed: Ask for target audience, margin, AOV, geography, creative assets, tracking, and objective. Produce advisory-only channel hypotheses (Meta/Instagram, TikTok, Google Search, SEO/content, email capture). Label: `business_profile_signal`, `hypothesis_to_test`, not ROI-proven.

**Example 2 — Website traffic exists, no paid media history**

Traffic summaries: organic search converts well · Instagram referral has traffic but weak conversion · email traffic converts well · direct traffic is high but attribution unclear.

Allowed: Search may be a strong first test candidate (organic intent). Meta/Instagram may be a small awareness or retargeting test, but paid social is unproven. Improve UTM tracking and list capture before scaling. Label: `data_informed_hypothesis`, not causal, requires paid test.

**Example 3 — No measurement readiness**

User: *Can I run MMM or GeoX?*

Allowed: Use P5 readiness reports. If not ready, route to cold-start advisory or tracking setup. Do not force MMM/GeoX.

**Example 4 — Broad non-channel advisory**

User: *What KPI should I use for this campaign?*

Allowed: Use general knowledge + objective ontology. Ask for business objective and funnel stage. If data exists, use metric availability summaries. Label KPI recommendation as advisory unless confirmed by semantic/readiness reports.

### LLM behavior (P5b)

**May:** ask for specific business details · ask for data that would improve the answer · use general marketing knowledge when no data exists · use governed data-analysis summaries when available · recommend channels as hypotheses to test · suggest starter tracking setup · suggest a learning agenda · explain what would be needed before MMM or GeoX

**Must not:** claim optimal media mix · claim channel ROI · claim causal effect · claim expected lift · claim final budget allocation · claim MMM/GeoX readiness without readiness reports · claim design feasibility without panel_exp diagnostics · claim decision authorization without `TrustReport`

### Future acceptance criteria (P5b)

- Can answer advisory marketing questions when no customer data exists
- Can ask for business details needed to improve channel recommendations
- Can ask for data that would make the answer more grounded
- Can label advisory answers by evidence mode and claim type
- Can use website traffic/source summaries to produce data-informed hypotheses
- Can distinguish organic/referral/social traffic signals from paid ROI evidence
- Can produce starter channel hypotheses without claiming optimality
- Can produce tracking setup checklist and learning agenda
- Can route users to MMM/GeoX only when readiness reports indicate eligibility
- Can block causal, ROI, lift, optimized budget, and decision-supporting claims without governed measurement evidence

### Hard boundaries (P5b)

No web search integration · no file parsing · no data profiling computation · no MMM/GeoX execution · no budget optimizer · no channel ROI model · no causal effect estimation · no automatic recommendation approval

## P6 — CalibrationSignal intake mapping

**Status:** ✓ implemented — `CalibrationEvidenceInput`, `CalibrationMappingRequirement`, `CalibrationMappingReport`, `validate_calibration_evidence_input`, `map_evidence_to_calibration_signal`. Maps governed experiment evidence into existing `CalibrationSignal` contracts with fixture validation. MMM calibration execution, effect estimation, causal certification, and decision approval remain deferred.

**Purpose:** Bridge governed experiment/readout evidence to MMM-consumable calibration signals after P5 readiness and P5b advisory lanes.

**Key behaviors:**

- Validates effect estimate, uncertainty (`standard_error`; CI alone does not auto-derive SE), metric/estimand, scope, and time window alignment
- Preserves lineage via `source_artifact_id`, `source_readout_id`, `source_experiment_id`, `source_trust_report_id`
- Blocks stale/non-causal evidence when requirements disallow them
- Maps valid evidence to `CalibrationSignal` with `DIAGNOSTIC_ONLY` tier and blocked decision/refresh usage

## P4b — Experiment design objective and data requirement contracts

**Entry paths:** MMM-driven (uncertainty, calibration gap, evidence conflict) · standalone GeoX design.

**Future contracts:** `ExperimentDesignObjective` · `ExperimentDesignIntake` · `MMMToGeoXDesignBridge` · `StandaloneGeoXDesignRequest` · `ExperimentDiagnosticRequest` · (see [CONVERSATIONAL_INTAKE_AND_DATA_HANDOFF_ROADMAP.md](./CONVERSATIONAL_INTAKE_AND_DATA_HANDOFF_ROADMAP.md) I6b)

**Objective-to-KPI families (deterministic, future):** awareness · demand creation · conversion · retention/usage · MMM calibration (must match MMM metric/estimand/scope).

## Diagnostic ownership split

| Owner | Responsibility |
|-------|----------------|
| **Common MIP intake/profiling** | Upload/connect/declaration; source registration; snapshots; mapping; semantic confirmation; structural profiling; workflow support assessment; LLM-safe summaries |
| **MMM** | MMM data sufficiency; media time-series; channel coverage; calibration use; model refresh; decision surface diagnostics |
| **GeoX / panel_exp** | Design feasibility; pre-period sufficiency; power/MDE; matchability; treatment/control; duration sensitivity; readout |
| **LLM** | Clarify intent; explain required data; explain insufficiency; summarize governed reports—**no** diagnostic computation or certification |

## LLM role in common intake (allowed vs disallowed)

**May say:**

> You asked for DMA-level GeoX design, but your uploaded data is national-week only. GeoX design needs geo/DMA-level outcome and media data.

> You asked for an awareness test. Your data includes visits and conversions but not BSV or branded search. Visits may be a proxy, but the platform should confirm whether traffic is acceptable as the primary KPI.

**Must not say:** this test is powered · use 8 weeks · these are the matched markets · the design is valid · move budget to this channel

## Future acceptance criteria

### Common intake workbench (P4c)

- User provides data **once** through common intake
- Same data evaluated for MMM, GeoX, CalibrationSignal, and decision-review support
- Platform reports grain (national, geo, DMA, weekly, daily, monthly)
- Platform explains when more granular data is needed for GeoX
- Platform explains when longer history is needed (without claiming final feasibility)
- Platform explains KPI gaps for awareness/demand/conversion goals
- LLM explains workflow-specific gaps from governed reports only
- Common layer cannot produce lift, MDE, power, matched markets, or budget recommendations

### Experiment design intake (P4b)

- MMM-driven and standalone GeoX requests; objective→KPI mapping; `ExperimentDiagnosticRequest` without executing panel_exp

### LangGraph (P17)

- Route intent to governed nodes; typed graph state; approved tools only; human approval for decision-support transitions; audit trail; no bypass of readiness/`TrustReport`/engine boundaries

## Capability blockers (quick reference)

| Capability | Blocked until |
|------------|---------------|
| Workflow-specific readiness | P4c workbench + P5 contracts |
| General advisory / cold-start | P5b contracts + evidence/claim labeling |
| CalibrationSignal intake mapping | P6 contracts + fixture validation |
| Experiment design diagnostics | P4b + P4c + P5 + panel_exp gated handoff |
| LLM current-performance answers | P11 + P12 + S1–S3 + TrustReport + G11–G20 |
| LangGraph runtime | P4b, P4c, P5, P5b, P8 contracts stable |
| Live engine execution | P13, P12, 8G–8N, G3, explicit signoff |

## Do not build yet

Model execution, optimizer execution, sibling imports, actual file upload/parsing, production connectors, power/MDE/matching, LangGraph runtime (until P17 prerequisites), raw-file LLM grounding, lift/budget/design-validity claims from common intake alone.

## Canonical ownership (overlaps)

| Concept | Owner doc |
|---------|-----------|
| Common intake workbench | This doc P4c; Conversational intake I6c |
| Workflow-specific readiness | Conversational intake I7–I8; P5 |
| General advisory / cold-start | Conversational intake I8b; P5b |
| Experiment design intake | Conversational intake I6b; P4b |
| LangGraph orchestration | Agentic workflow governance P17 |

## Related documents

- [CONVERSATIONAL_INTAKE_AND_DATA_HANDOFF_ROADMAP.md](./CONVERSATIONAL_INTAKE_AND_DATA_HANDOFF_ROADMAP.md)
- [LLM_REASONING_AND_MODEL_GUIDANCE_ROADMAP.md](./LLM_REASONING_AND_MODEL_GUIDANCE_ROADMAP.md)
- [PLATFORM_SEMANTIC_AND_DECISION_READINESS_ROADMAP.md](./PLATFORM_SEMANTIC_AND_DECISION_READINESS_ROADMAP.md)
- [AGENTIC_WORKFLOW_GOVERNANCE_ROADMAP.md](../architecture/AGENTIC_WORKFLOW_GOVERNANCE_ROADMAP.md)
- [REPO_INTEGRATION_STRATEGY.md](../architecture/REPO_INTEGRATION_STRATEGY.md)
- [ROADMAP_EXECUTION_AUDIT_001.md](../audits/ROADMAP_EXECUTION_AUDIT_001.md)
