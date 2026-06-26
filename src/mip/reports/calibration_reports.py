"""Calibration-specific deterministic report builder and export helpers."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from mip.contracts.deterministic_report import DeterministicReportEnvelope
from mip.examples.stage_a_adapters import (
    StageAAdapterError,
    list_supported_calibration_fixture_ids,
    run_calibration_mapping_for_stage_a_fixture,
)
from mip.reports.deterministic_reports import (
    DeterministicReportExportError,
    write_report_json,
)


def build_calibration_report_from_stage_a_fixture(
    fixture_id: str,
    *,
    report_id: str | None = None,
    generated_at: datetime | None = None,
) -> DeterministicReportEnvelope:
    """Build a calibration deterministic report from a Stage A fixture id."""
    try:
        return run_calibration_mapping_for_stage_a_fixture(
            fixture_id,
            generated_at=generated_at,
            report_id=report_id,
        )
    except StageAAdapterError as exc:
        msg = f"calibration report build failed for fixture {fixture_id!r}: {exc}"
        raise DeterministicReportExportError(msg) from exc


def export_calibration_report_from_stage_a_fixture(
    fixture_id: str,
    output_path: Path | str,
    *,
    report_id: str | None = None,
    generated_at: datetime | None = None,
    overwrite: bool = False,
) -> Path:
    """Build and export a calibration deterministic report to local JSON."""
    report = build_calibration_report_from_stage_a_fixture(
        fixture_id,
        report_id=report_id,
        generated_at=generated_at,
    )
    return write_report_json(report, output_path, overwrite=overwrite)


__all__ = [
    "build_calibration_report_from_stage_a_fixture",
    "export_calibration_report_from_stage_a_fixture",
    "list_supported_calibration_fixture_ids",
]
