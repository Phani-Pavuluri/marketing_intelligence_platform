# MIP Chat-First Demo Sample Journey Fixtures 001

This artifact adds one deterministic, demo-only SaaS subscriptions journey at
`data/demo/domain_fixtures/saas_subscriptions/v1/journey/`. It reuses the
committed dataset manifest, raw data, canonical MMM/GeoX readiness panels, and
context-only calibration fixture rather than duplicating them.

The journey ID is `saas_subscriptions_measurement_journey_v1`. Its ordered
chain is dataset selection, upload explanation, MMM readiness, a precomputed
sample MMM run/result, a Meta identifiability evidence gap, a MIP-routed GeoX
request/response/readout example, a downweighted compatible CalibrationSignal,
a refreshed-MMM comparison, and blocked planning readiness.

Every authored result declares `demo_only: true`, `live_execution: false`,
`production_evidence: false`, and
`result_origin: authored_deterministic_demo_fixture`. The GeoX request preserves
the ownership boundary: MIP routes; panel_exp/GeoX owns feasibility and market
assignment; external execution supplies any real experiment. The fixture does
not fit MMM, execute GeoX, ingest production exports, run calibration, optimize
budget, or authorize recommendations.

The fixture-only loader validates identities, references, stage order, execution
labels, intervals, contribution reconciliation, comparison widths, and planning
blockers. Prompt eligibility is contextual and suppresses GeoX, calibration, or
planning prompts until their prerequisite artifacts are available.

Planning remains blocked for simulation and recommendations, and production
authorization remains false. The next artifact is
`MIP_CHAT_FIRST_DEMO_PRODUCT_FLOW_IMPLEMENTATION_001`.
