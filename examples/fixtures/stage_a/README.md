# Stage A synthetic deterministic fixtures

Canonical **MIP-owned synthetic fixtures** for deterministic product and demo workflows. These files are **artificial, non-production, and non-sensitive** — they exist to power docs, API examples, tests, and future guided demos without impersonating certified measurement outputs.

## What Stage A includes

| Category | Purpose |
|----------|---------|
| `business_profiles/` | Cold-start advisory examples (beginner/intermediate business context) |
| `readiness/` | Governed data **summaries** for MMM and GeoX structural readiness checks |
| `calibration/` | Synthetic experiment readouts for calibration mapping pass/fail cases |
| `intake/` | Structured intake/routing request examples |
| `governance/` | Educational unsupported-claim examples |

See `manifest.json` for the full fixture index with `fixture_id`, `workflow_area`, `demo_journey`, `evidence_level`, and `expected_status`.

## What Stage A does **not** include

- Raw production rows or user-level data
- MMM fitting or GeoX design/inference execution
- Channel ROI, optimizer output, response curves, or scenario-planner artifacts
- Matched markets, power/MDE, treatment assignment, or causal lift claims
- Notebooks (planned separately)
- New API routes or runtime behavior changes

All fixtures set `"synthetic": true` and `"requires_mmm_or_geox_engine": false`.

## Usage

Fixtures are **schema-aligned examples** for deterministic MIP workflows. They align with patterns in `app/demo_fixtures.py` and [P12 SDK/API usage examples](../../../docs/examples/P12_SDK_API_USAGE_EXAMPLES_001.md).

**Stage A.2 loader helpers** (`mip.examples.stage_a_fixtures`) discover and load fixtures without hardcoding paths:

```python
from mip.examples.stage_a_fixtures import (
    list_stage_a_fixtures,
    load_stage_a_fixture,
    load_stage_a_manifest,
)

manifest_entries = load_stage_a_manifest()
calibration_entries = list_stage_a_fixtures(workflow_area="calibration_mapping")
readout = load_stage_a_fixture("experiment_readout_valid")
```

Helpers are deterministic and local — they read JSON only, validate `synthetic=true`, and do not run MMM/GeoX engines or imply production data ingestion.

**Calibration fixtures** wrap `evidence` and `requirement` objects compatible with `CalibrationEvidenceInput` and `CalibrationMappingRequirement`:

```python
from mip.contracts.calibration_intake import (
    CalibrationEvidenceInput,
    CalibrationMappingRequirement,
)
from mip.examples.stage_a_fixtures import load_stage_a_fixture
from mip.workflows.intake.calibration_mapping import map_evidence_to_calibration_signal

payload = load_stage_a_fixture("experiment_readout_valid")
evidence = CalibrationEvidenceInput(**payload["evidence"])
requirement = CalibrationMappingRequirement(**payload["requirement"])
signal, report = map_evidence_to_calibration_signal(evidence, requirement)
```

**Readiness fixtures** are governed summaries (`summary_type`, `structural_support`, `missing_for_*`) — not raw CSV uploads.

**Business profile fixtures** supply structured fields for cold-start advisory demos (`domain`, `objective`, `tracking_state`, `evidence_mode`, etc.).

Stage A.2 loader helpers are implemented in `mip.examples.stage_a_fixtures`. **Stage A.3** calibration adapter (`mip.examples.stage_a_adapters`) and `deterministic_report_v1` envelopes are implemented for calibration golden paths only. Advisory/readiness/intake adapters remain future.

## Related docs

- [Synthetic demo dataset strategy](../../../docs/product/SYNTHETIC_DEMO_DATASET_STRATEGY_PLAN_001.md)
- [Product entrypoint and demo experience plan](../../../docs/product/PRODUCT_ENTRYPOINT_AND_DEMO_EXPERIENCE_PLAN_001.md)
- [P12 SDK/API usage examples](../../../docs/examples/P12_SDK_API_USAGE_EXAMPLES_001.md)
- [Deterministic usage modes](../../../docs/service/DETERMINISTIC_USAGE_MODES.md)

## Stage B (deferred)

Engine-backed MMM/GeoX visuals, ROI charts, response curves, and optimizer outputs remain **Stage B** — only after certified engine paths produce governed artifacts. MIP is the control plane, not the statistical engine.
