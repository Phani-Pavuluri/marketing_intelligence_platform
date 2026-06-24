# panel_exp → MIP Export Producer Specification

## Scope

This document specifies how the **panel_exp** (GeoX) sibling repository should write static JSON exports for MIP consumption.

See also: [MIP_SIBLING_EXPORT_PRODUCER_SPEC.md](MIP_SIBLING_EXPORT_PRODUCER_SPEC.md)

## Export directory

```text
panel_exp/integrations/mip/exports/
```

Write one or more `.json` files per export batch. MIP discovers files read-only via Phase 8C hooks.

## Required field mapping

| Field | Value |
|-------|-------|
| `source_repo` | `panel_exp` |
| `engine_kind` | `geox` |
| `artifact_kind` | `geox_adapter_output` |
| `export_schema_version` | `1.0.0` |

## Required labels

```text
static_export_file_only
not_live_engine_execution
not_real_model_result
diagnostic_only
not_decision_ready
```

## Payload guidance

`payload` may contain structural placeholders only. Do not include lift estimates, ROI, causal impact, budget recommendations, p-values, confidence intervals, or experiment readout metrics.

## Minimal valid example

Reference file in MIP:

`tests/fixtures/sibling_exports/producer_spec_panel_exp_minimal_valid.json`

## Producer responsibilities

1. Write JSON only; no Python import path from MIP into `panel_exp`.
2. Include `source_commit_marker` for lineage.
3. Use `validation_status` and `blocking_reasons` consistently with the shared schema.
4. Do not claim causal impact, incrementality, ROI, lift, budget recommendations, production readiness, or production-ready experiment certification in export text.

## MIP consumption path

```text
panel_exp/integrations/mip/exports/*.json
  → SiblingFixtureExport validation (8B)
  → directory discovery (8C)
  → compatibility registry (8D)
  → local path wiring (8E)
  → AdapterOutputBundle → ExperimentEvidence → TrustReport / registry
```

No live GeoX execution is triggered by MIP through this contract.

## Hard boundaries

MIP must not import `panel_exp`, use subprocess, trigger training or estimation, or execute sibling code through this file handoff.
