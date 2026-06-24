# MIP Sibling Export Producer Specification

## Purpose

This document defines the **producer-side contract** for sibling repositories (`mmm`, `panel_exp`) that write static JSON exports for MIP to consume.

MIP phases **8B–8E** implement the read-only consumer bridge:

| Phase | Capability |
|-------|------------|
| 8B | `SiblingFixtureExport` schema and governance import |
| 8C | Read-only export directory discovery |
| 8D | Sibling compatibility registry |
| 8E | Local sibling export path wiring |

Phase **8F** documents what sibling repos must emit. MIP does **not** modify sibling repos in this phase.

## Export directory contract

Sibling repos must write static JSON files to:

```text
mmm/integrations/mip/exports/
panel_exp/integrations/mip/exports/
```

Paths are relative to each sibling repository root. MIP resolves them through `SiblingRepoExportConfig` and local path defaults (`integrations/mip/exports`).

## File format

Every export file must be **static JSON** conforming to the MIP `SiblingFixtureExport` schema:

| Field | Required | Notes |
|-------|----------|-------|
| `fixture_id` | yes | Stable export identifier |
| `source_repo` | yes | `mmm` or `panel_exp` |
| `source_commit_marker` | yes | Lineage marker string (not a live git call from MIP) |
| `export_schema_version` | yes | `1.0.0` for current contract |
| `artifact_kind` | yes | `mmm_adapter_output` or `geox_adapter_output` |
| `engine_kind` | yes | `mmm` or `geox` |
| `config_marker` | yes | Source config lineage marker |
| `validation_status` | yes | `validated_fixture`, `blocked_fixture`, or `invalid_fixture` |
| `labels` | yes | See required labels below |
| `warnings` | optional | Non-inferential warnings only |
| `blocking_reasons` | required when blocked/invalid | |
| `disclaimer` | yes | Must not claim inferential results |
| `payload` | required when validated | Structural placeholders only |

## Required schema version

```text
1.0.0
```

## Required labels (all producer exports)

```text
static_export_file_only
not_live_engine_execution
not_real_model_result
diagnostic_only
not_decision_ready
```

MIP consumer validation also accepts `pinned_sibling_repo_fixture_only` as an alternate source-marker label for committed test fixtures.

## Allowed content

Producer exports may contain:

- Structural placeholder output
- Source config markers
- Validation status
- Warnings and blockers
- Lineage metadata
- Schema version
- Source commit marker

## Forbidden claims

Producer exports must **not** claim:

- Real ROI or iROAS
- Lift or incremental lift
- Causal impact
- Incrementality results
- Production readiness
- Budget recommendations
- Decision recommendations
- Model execution success (unless separately governed outside this contract)
- Experiment readout certification (unless separately governed)

## Handoff model

The sibling repo may run its own workflow independently, but **MIP must only consume the static export artifact**.

MIP must **not**:

- Call sibling repo code
- Import sibling repo modules (`import mmm`, `import panel_exp`)
- Trigger sibling repo execution through this contract
- Use subprocess or command execution in sibling repos
- Perform file watching, scheduling, training, or estimation through this path

This remains a **file-based handoff**, not a Python dependency or execution path.

## Minimal valid examples

Committed in MIP for validation and sibling-repo reference:

- `tests/fixtures/sibling_exports/producer_spec_mmm_minimal_valid.json`
- `tests/fixtures/sibling_exports/producer_spec_panel_exp_minimal_valid.json`

## Next sibling-repo work

Implement producer writers in `mmm` and `panel_exp` that emit JSON matching this contract into `integrations/mip/exports/`. Live engine execution remains blocked on the MIP side until a later explicitly governed phase.
