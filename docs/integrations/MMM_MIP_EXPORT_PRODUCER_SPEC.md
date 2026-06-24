# MMM → MIP Export Producer Specification

## Scope

This document specifies how the **mmm** sibling repository should write static JSON exports for MIP consumption.

See also: [MIP_SIBLING_EXPORT_PRODUCER_SPEC.md](MIP_SIBLING_EXPORT_PRODUCER_SPEC.md)

## Export directory

```text
mmm/integrations/mip/exports/
```

Write one or more `.json` files per export batch. MIP discovers files read-only via Phase 8C hooks.

## Required field mapping

| Field | Value |
|-------|-------|
| `source_repo` | `mmm` |
| `engine_kind` | `mmm` |
| `artifact_kind` | `mmm_adapter_output` |
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

`payload` may contain structural placeholders only, for example:

```json
{
  "placeholder": true,
  "producer_spec_example_only": true
}
```

Do not include ROI, lift, response curves, channel contributions, causal impact, budget recommendations, production readiness claims, or model metrics.

## Minimal valid example

Reference file in MIP:

`tests/fixtures/sibling_exports/producer_spec_mmm_minimal_valid.json`

## Producer responsibilities

1. Write JSON only; no Python import path from MIP into `mmm`.
2. Include `source_commit_marker` for lineage (string marker, not live git integration from MIP).
3. Set `validation_status` to `validated_fixture` only when the export structurally passes producer validation.
4. Use `blocked_fixture` or `invalid_fixture` with `blocking_reasons` when the export cannot be consumed.

## MIP consumption path

```text
mmm/integrations/mip/exports/*.json
  → SiblingFixtureExport validation (8B)
  → directory discovery (8C)
  → compatibility registry (8D)
  → local path wiring (8E)
  → AdapterOutputBundle → governance artifact → TrustReport
```

No live MMM execution is triggered by MIP through this contract.

## Hard boundaries

MIP must not import `mmm`, use subprocess, trigger training or estimation, or execute sibling code through this file handoff.
