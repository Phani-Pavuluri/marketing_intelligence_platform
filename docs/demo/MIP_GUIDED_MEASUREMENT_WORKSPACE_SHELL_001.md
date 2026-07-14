# MIP Guided Measurement Workspace Shell 001

## Outcome

P1 replaces the generic chat-first landing with a business-facing guided workspace shell. It does not implement the vertical journey, upload runtime, full answer layer, live engines, or providers.

## Previous limitations

The previous landing led with a generic measurement copilot description, six uneven onboarding prompts, no explicit entry-mode state, and an internal stage-menu mental model. It could not clearly distinguish the SaaS sample path from the future user-data readiness path.

## New shell

The page headline is **Turn marketing data into trustworthy spend decisions**. Supporting copy explains channel performance, future-budget preparation, incrementality testing, and using experiment evidence to improve MMM. The compact Measure / Plan / Experiment / Learn frame remains secondary to the hero.

The initial assistant welcome explains decision clarification, data requirements, MMM versus GeoX choice, readiness/evidence, uncertainty, planning support, and next actions. It explicitly distinguishes the SaaS sample from the planned readiness workflow without making dataset-specific claims before selection. The composer is available immediately.

Exactly four primary prompts have distinct deterministic answers:

1. platform capabilities and governed evidence;
2. practical data requirements;
3. MMM versus GeoX ownership and evidence gaps; and
4. next-quarter planning prerequisites and the blocked optimization boundary.

Each answer contains a direct answer, useful detail, limitation, next action, and relevant follow-ups.

## Entry modes and context

**Explore a sample use case** enters sample mode without activating data, then requires a separate SaaS activation. It describes the committed SaaS growth-planning fixture: paid conversions, weekly × DMA grain, Search/Meta/YouTube, four controls, 14 weeks, and deterministic precomputed mode.

**Analyze my data** is an enabled informational action. It describes the future CSV inventory, profiling, mapping, grain checks, and MMM/GeoX readiness workflow, while explicitly stating that it does not implement upload, fitting, ROI, optimization, or experiment execution. It makes no persistence statement.

The shell state adds `entry_mode` and `active_use_case_id`; reset clears both, the dataset, and conversation state. Active context renders only after SaaS activation: sample mode, SaaS growth planning, and SaaS subscriptions.

## Transitional flow and safety

The default landing no longer exposes the internal stage menu or incomplete sample-selection wording. After activation, existing fixture-backed stage controls remain under **Current sample walkthrough** as a documented P2 transition. Advanced tools remain available in the secondary sidebar surface.

No LLM/provider execution, MMM fitting/export ingestion, GeoX execution, calibration, simulation, optimization, recommendation authorization, upload widget, parsing, persistence, or fixture-data change was introduced.

## Validation and verification

Focused state, answer, and Streamlit AppTest coverage verifies the hero, entry modes, active context, truthful upload information, activation, reset, and absence of duplicate keys. Automated and Docker validation passed. The interactive local browser surface was unavailable in the implementation environment, so local visual review is pending user verification; hosted visual review is pending redeployment and user verification. No manual browser acceptance is claimed.

## Next artifact

`MIP_GUIDED_MEASUREMENT_WORKSPACE_VERTICAL_JOURNEY_001`
