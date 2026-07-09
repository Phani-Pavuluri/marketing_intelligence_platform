# GeoX readout materialization fixtures

Synthetic CSV fixtures for **controlled local materialization** in the MIP GeoX readout handoff lane.

## Purpose

Support `MIP_GEOX_READOUT_FIXTURE_MATERIALIZATION_ADAPTER_001` and Stage 3B runtime-call tests without production upload ingestion, warehouse queries, or live API calls.

## Optional `panel_exp` runtime dependency (Stage 3B)

Stage 3B (`call_geox_post_test_spend_runtime_for_fixture`) lazy-imports the sibling **panel_exp** package to call `build_post_test_spend_evidence` and `build_trusted_readout_spend_handoff`. **`panel_exp` is not a required MIP dependency** — it is not in `pyproject.toml`. Workflow tests use `pytest.importorskip("panel_exp")` and skip when the package is absent. For local full-path validation, install the sibling GeoX repo editable into the MIP virtualenv.

## Files

| File | Role | Columns |
|------|------|---------|
| `spend_panel.csv` | SPEND | date, dma, spend, currency, cell, channel, campaign |
| `assignment_table.csv` | ASSIGNMENT | dma, cell, treatment |

All data is synthetic. No real customer or Adobe data.

## Usage

Reference via `DatasetReference` with `REGISTERED_ARTIFACT` or `UPLOADED_CSV` and a path under this directory. Materialization is enforced by `GeoXFixtureMaterializationPolicy.allowed_fixture_roots`.

See `manifest.json` for dataset ref IDs and required columns.
