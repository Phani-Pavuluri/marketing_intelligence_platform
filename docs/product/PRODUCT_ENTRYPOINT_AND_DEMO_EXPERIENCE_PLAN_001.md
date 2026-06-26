# Product Entrypoint and Demo Experience Plan 001

## 1. Title and status

| Field | Value |
|-------|-------|
| **Title** | Product Entrypoint and Demo Experience Plan 001 |
| **Status** | Accepted product direction |
| **Type** | Product UX / demo experience roadmap |
| **Baseline** | Current public demo is deterministic and Streamlit-based at `app/streamlit_app.py`. Future product direction is chat-first and LLM-assisted, but governed by deterministic MIP contracts and workflows. |
| **Hosted public demo** | https://marketingintelligenceplatform.streamlit.app/ |
| **Related docs** | [Deterministic usage modes](../service/DETERMINISTIC_USAGE_MODES.md) (when present), [Roadmap execution sequence](../roadmap/ROADMAP_EXECUTION_SEQUENCE.md), [Repo integration strategy](../architecture/REPO_INTEGRATION_STRATEGY.md) |

This document records **intended user experience** for MIP. It does **not** authorize implementation in this phase. Runtime behavior of the current public demo is unchanged.

## 2. Core decision

MIP should move toward a **single-page landing experience with chat-first interaction**.

The homepage should **not** primarily expose internal workflow tabs such as cold-start advisory, readiness, calibration mapping, and intake overview. Those are governed artifacts and workflows. The primary entrypoint should help users understand what MIP can do for their **business decisions** and let them ask questions naturally.

The page should use **anchor sections** rather than many top-level tabs:

| Anchor section | Purpose |
|----------------|---------|
| **Home / hero** | What MIP is and who it serves |
| **Ask MIP** | Primary future interface (chat/search) |
| **What MIP can help decide** | Business-value outcomes, not internal workflow names |
| **Guided demo journeys** | Sample user paths with clear evidence labels |
| **Output previews** | Illustrative previews of future business-valuable results |
| **How it works** | Control-plane flow from question to governed artifact |
| **Data needed by decision** | What data unlocks which decisions |
| **Developer / API / package usage** | SDK, FastAPI, notebooks, future CLI |
| **Governance boundaries** | What MIP blocks, allows, and never claims |

**Principle:** MIP is the **control plane**, not the statistical engine. The product surface should teach that distinction clearly.

## 3. Target user segments

MIP should serve users across marketing maturity levels.

### Beginner / small business user

**Example questions:**

- “I want to increase sales through marketing.”
- “I need help planning how to spend on marketing.”

**Expected behavior:**

- LLM may provide clearly labeled **general-knowledge advisory** guidance when enabled.
- MIP steers toward starter tracking, data collection, and a learning agenda.
- **No** measured ROI or causal claims.
- Evidence mode: `general_knowledge_only` or `business_profile_only`.

### Intermediate user

**Example question:**

- “I have weekly spend and sales by channel. Can I understand what is working?”

**Expected behavior:**

- LLM extracts available data structure when enabled.
- MIP runs **deterministic** readiness and routing checks.
- Output explains which workflows are supported or blocked.
- User receives a missing-data checklist and next steps.

### Sophisticated user

**Example question:**

- “I have DMA-week media/outcome data and experiment readouts. Can I check MMM/GeoX readiness and calibration?”

**Expected behavior:**

- MIP behaves as a **deterministic control plane**.
- Validates contracts, readiness, calibration mapping, and governance boundaries.
- Routes to certified MMM/GeoX engines only when appropriate and gated.
- LLM explains governed results but **does not invent** measurement conclusions.

## 4. Landing page structure

### Hero

**Purpose:** Quickly explain what MIP is.

**Suggested copy:**

> Marketing Intelligence Platform helps users move from broad marketing questions to governed measurement-backed decisions — from starter planning and tracking setup to MMM calibration, experiment evidence, scenario planning, and safer budget decisions.

### Ask MIP search / chat bar

**Purpose:** Primary future interface.

**Example placeholder:**

> Ask MIP how to plan, measure, or improve your marketing…

**Example prompt chips:**

- “I want to increase sales. Where should I start?”
- “What data do I need to measure marketing ROI?”
- “Can my data support MMM?”
- “Can this experiment readout calibrate MMM?”
- “Can I run a geo experiment?”
- “How should I reallocate budget next quarter?”

**Current deterministic demo behavior:**

- If LLM is disabled (default today), show Ask MIP as **planned / future** or route users to **guided deterministic demos**.
- **Do not** fake LLM responses with canned or template explanations.

### What MIP can help decide

Use **business-value language**, not internal tab names:

- where to start with marketing
- what to track first
- whether data is ready for MMM or GeoX
- whether experiment evidence is admissible for calibration
- which channels appear promising **once evidence exists**
- how channel ROI/contribution **may be summarized when certified models exist**
- where response curves / saturation **may matter**
- how scenarios and budget allocations **can be evaluated when a governed DecisionSurface exists**

**Caveat (required on page):**

Advanced outputs require appropriate data, **certified model outputs**, and governance checks. The public demo does not currently produce ROI, lift, power/MDE, matched markets, treatment assignment, budget optimization, or response curves unless clearly labeled as **illustrative synthetic preview**.

## 5. Guided demo journeys

Guided demos should show **sample user journeys and business outcomes**, not internal workflow names.

### Demo 1: Small business starting from zero

| Field | Value |
|-------|-------|
| **Question** | “I want more sales. Where should I start?” |
| **Shows** | Starter channel hypotheses; tracking checklist; learning agenda; what data to collect next |
| **Output type** | Advisory-only plan — **not** causal proof |
| **Maps to today** | Cold-start advisory (deterministic fixture) |

### Demo 2: Marketer with weekly spend/sales data

| Field | Value |
|-------|-------|
| **Question** | “I have weekly spend and sales by channel. Can I measure what is working?” |
| **Shows** | Readiness assessment; MMM vs GeoX routing; missing data requirements; blocked workflow explanations |
| **Output type** | Workflow readiness report |
| **Maps to today** | Readiness assess (deterministic fixture) |

### Demo 3: Experiment readout review

| Field | Value |
|-------|-------|
| **Question** | “Can this lift study calibrate MMM?” |
| **Shows** | CalibrationSignal mapping; missing standard error block; metric/estimand mismatch block; valid diagnostic signal when admissible |
| **Output type** | Mapped diagnostic signal or blocked evidence report |
| **Maps to today** | Calibration mapping (deterministic fixture) |

### Demo 4: Mature marketing team / budget planning preview

| Field | Value |
|-------|-------|
| **Question** | “How should I reallocate budget next quarter?” |
| **Shows (illustrative)** | Channel ROI/contribution summary preview; response curve/saturation preview; scenario planner preview; budget optimizer guardrails; uncertainty/risk flags |
| **Output type** | **Illustrative synthetic preview** unless backed by certified data and model evidence |
| **Maps to today** | Not implemented — preview placeholders only in future landing page |

## 6. Output previews

The product should show what **business-valuable results can eventually look like** when the right data and certified models exist.

| Preview category | Notes |
|------------------|-------|
| Channel ROI / contribution snapshot | Requires certified MMM outputs |
| Budget optimizer recommendation preview | Illustrative unless governed DecisionSurface + certification |
| Scenario planner preview | Illustrative unless governed DecisionSurface exists |
| Response curve and saturation preview | Model output — not produced by current public demo |
| Readiness report | Available today via deterministic demo |
| Calibration mapping report | Available today via deterministic demo |
| Trust / governance summary | Future assembled view over TrustReport and gates |
| Decision risk and uncertainty flags | Future — tied to certified evidence tiers |

**Labeling rules for previews:**

| Label | Meaning |
|-------|---------|
| **Illustrative synthetic preview** | Sample UI only; not from user data or live models |
| **Requires certified MMM/GeoX/model evidence** | Real output only after engine certification path |
| **Not produced by current public demo** | Unless explicitly implemented later |
| **Not a causal or budget recommendation** | Without governed evidence and TrustReport authorization |

## 7. Data needed by decision

MIP should teach users **what data unlocks which decisions**.

| User has | MIP can help with | Example decision | Evidence level |
|----------|-------------------|------------------|----------------|
| Business description only | Starter advisory plan | Where to start | `general_knowledge_only` / `business_profile_only` |
| Website traffic / source summary | Traffic-informed advisory | Which channels to test first | `data_informed_advisory` |
| Weekly channel spend + outcome | MMM readiness | Whether MMM may be structurally possible | Readiness only — not fitted MMM |
| Geo-week spend / outcome | GeoX / geo-MMM readiness | Whether geo experiment or geo model path is structurally possible | Readiness only — not design/inference |
| Experiment lift + standard error | Calibration mapping | Whether evidence can calibrate MMM | Diagnostic / calibration evidence |
| Certified MMM outputs | Contribution, ROI, response curves | Which channels appear productive | Measured diagnostic / model output |
| Governed DecisionSurface | Scenario planning / budget allocation | Safer budget movement | Causal decision support **only if certified** |

**Emphasis:** Readiness and advisory outputs **do not** authorize ROI, lift, optimal mix, or budget moves. Calibration mapping produces **diagnostic-tier** signals until TrustReport and engine certification allow more.

## 8. How the system works

```text
User asks a question
  → MIP identifies user maturity and intent
  → LLM extracts structured business profile, data summary, or evidence fields (when enabled)
  → Deterministic contracts/workflows validate inputs
  → MIP routes to advisory, readiness, calibration, MMM/GeoX handoff, or decision review
  → Certified engines provide measurement outputs when available
  → MIP returns plain-English answer plus governed artifact and blocked claims
```

**Clarification:** The LLM is a **conversational interface and translator**. It is **not** the measurement authority. Deterministic MIP contracts, readiness reports, calibration mapping reports, and TrustReports remain authoritative.

## 9. Interface roles

### LLM workbench (primary future user interface)

- Free-form questions
- Structured extraction from user text
- Follow-up questions for missing fields
- Explains governed outputs in plain language
- Routes to deterministic tools
- **Cannot** invent causal, ROI, power/MDE, matched-market, treatment-assignment, or budget-optimization claims

### Streamlit public demo (current)

- Public demo and **deterministic governance console**
- Shows safe sample workflows and what MIP blocks/allows
- Should **evolve** toward landing page + guided demo journeys (this plan)
- **Not** the final product UX

### FastAPI service (`mip.service`)

- Application and automation interface
- Exposes deterministic workflows for future UI, agents, and LLM workbench
- Calls shared `mip.workflows.*` helpers
- Must not duplicate business logic or depend on UI rendering code

### Python SDK / package

- Developer and notebook usage
- Advanced users call contracts and workflows directly
- Future sample notebooks should show readiness, calibration, and decision-surface workflows

### Future CLI

- Local operator interface without requiring LLM
- Example commands: readiness assess, calibration map, advisory cold-start, intake overview

## 10. What current tabs become

Today’s Streamlit tabs (cold-start advisory, readiness reports, calibration mapping, intake overview) are **governed artifact views**, not the intended primary homepage navigation.

**Preferred future layout:**

```text
Single-page landing + anchor links + chat-first interaction
  → guided demo journey (user question framing)
  → deterministic workflow execution
  → artifact view with evidence/claim labels
```

**Avoid:**

- Making internal workflow tabs the **first** experience
- Over-polishing current tab UI as if it were final product
- Hiding governance details, blocked claims, or evidence labels entirely

## 11. Recommended future implementation sequence

| Step | Scope | Type |
|------|-------|------|
| 1 | Finish **P10b.1** service workflow boundary cleanup | Engineering |
| 2 | Finish **P10c** Docker / local container smoke test | Engineering |
| 3 | Add product entrypoint roadmap references (this document) | Docs ✓ |
| 4 | Minimal Streamlit landing page update: hero, Ask MIP placeholder, guided demo links, output preview placeholders, data-needed-by-decision section, governance boundaries | Product UI |
| 5 | Sample SDK / API docs | Docs |
| 6 | Sample notebooks | Docs / examples |
| 7 | Plan LLM workbench mode: disabled default, governed extraction, tool routing, explanation validation, no free-form measurement claims | Design + engineering |
| 8 | Actual LLM implementation after privacy, cost, auth, and provider boundaries | Engineering (gated) |

Steps 4–8 are **future work**. This plan does not authorize them in the current phase.

## 12. Acceptance criteria

This product direction is documented when:

- [x] Single-page landing + chat-first direction is explicit
- [x] Guided demo journeys are defined
- [x] Output preview categories are defined
- [x] Data-needed-by-decision matrix is documented
- [x] Deterministic / LLM / API / SDK / Streamlit / CLI roles are documented
- [x] Current tabs are reframed as demo/artifact views
- [x] Advanced outputs are clearly caveated as requiring certified evidence
- [x] No runtime behavior is changed in this phase

## Related documents

- [Roadmap execution sequence](../roadmap/ROADMAP_EXECUTION_SEQUENCE.md)
- [Repo integration strategy](../architecture/REPO_INTEGRATION_STRATEGY.md)
- [P10 FastAPI/Docker wrapper plan](../service/P10_FASTAPI_DOCKER_WRAPPER_PLAN.md)
- [Public demo deployment record (P9b)](../demo/PUBLIC_DEMO_DEPLOYMENT_RECORD_P9B.md)
- [LLM Decision Layer vision](../architecture/LLM_DECISION_LAYER_VISION.md)
