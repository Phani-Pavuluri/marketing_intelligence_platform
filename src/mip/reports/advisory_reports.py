"""Cold-start advisory deterministic report builder and export helpers."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from mip.contracts.deterministic_report import DeterministicReportEnvelope
from mip.examples.stage_a_adapters import (
    StageAAdapterError,
    list_supported_advisory_fixture_ids,
    run_cold_start_advisory_for_stage_a_fixture,
)
from mip.reports.deterministic_reports import (
    DeterministicReportExportError,
    write_report_json,
)


def build_cold_start_advisory_report_from_stage_a_fixture(
    fixture_id: str,
    *,
    report_id: str | None = None,
    generated_at: datetime | None = None,
) -> DeterministicReportEnvelope:
    """Build a cold-start advisory deterministic report from a Stage A fixture id."""
    try:
        return run_cold_start_advisory_for_stage_a_fixture(
            fixture_id,
            generated_at=generated_at,
            report_id=report_id,
        )
    except StageAAdapterError as exc:
        msg = f"advisory report build failed for fixture {fixture_id!r}: {exc}"
        raise DeterministicReportExportError(msg) from exc


def export_cold_start_advisory_report_from_stage_a_fixture(
    fixture_id: str,
    output_path: Path | str,
    *,
    report_id: str | None = None,
    generated_at: datetime | None = None,
    overwrite: bool = False,
) -> Path:
    """Build and export a cold-start advisory deterministic report to local JSON."""
    report = build_cold_start_advisory_report_from_stage_a_fixture(
        fixture_id,
        report_id=report_id,
        generated_at=generated_at,
    )
    return write_report_json(report, output_path, overwrite=overwrite)


__all__ = [
    "build_cold_start_advisory_report_from_stage_a_fixture",
    "export_cold_start_advisory_report_from_stage_a_fixture",
    "list_supported_advisory_fixture_ids",
]
