# GeoX readout materialization fixtures

Synthetic CSV fixtures for **controlled local materialization** in the MIP GeoX readout handoff lane.

## Purpose

Support `MIP_GEOX_READOUT_FIXTURE_MATERIALIZATION_ADAPTER_001` and future Stage 3B runtime-call tests without production upload ingestion, warehouse queries, or live API calls.

## Files

| File | Role | Columns |
|------|------|---------|
| `spend_panel.csv` | SPEND | date, dma, spend, currency, cell, channel, campaign |
| `assignment_table.csv` | ASSIGNMENT | dma, cell, treatment |

All data is synthetic. No real customer or Adobe data.

## Usage

Reference via `DatasetReference` with `REGISTERED_ARTIFACT` or `UPLOADED_CSV` and a path under this directory. Materialization is enforced by `GeoXFixtureMaterializationPolicy.allowed_fixture_roots`.

See `manifest.json` for dataset ref IDs and required columns.
