"""Serialization and export helpers for deterministic report envelopes."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from mip.contracts.deterministic_report import (
    DETERMINISTIC_REPORT_SCHEMA_VERSION,
    DeterministicReportEnvelope,
)

_UNSUPPORTED_ADVANCED_OUTPUT_PATTERN = re.compile(
    r"\b("
    r"channel_roi|"
    r"response_curve|"
    r"optimizer_output|"
    r"matched_markets|"
    r"treatment_assignment|"
    r"causal_lift|"
    r"power_mde|"
    r"mmm_fitted|"
    r"budget_optimization_result"
    r")\b",
    re.IGNORECASE,
)


class DeterministicReportExportError(Exception):
    """Raised when deterministic report export or validation fails."""


def report_to_dict(report: DeterministicReportEnvelope) -> dict[str, Any]:
    """Serialize a deterministic report envelope to a JSON-compatible dict."""
    validate_report_has_no_unsupported_advanced_outputs(report)
    return report.model_dump(mode="json")


def report_to_json(
    report: DeterministicReportEnvelope,
    *,
    indent: int = 2,
) -> str:
    """Serialize a deterministic report envelope to a JSON string."""
    return json.dumps(report_to_dict(report), indent=indent, sort_keys=True)


def write_report_json(
    report: DeterministicReportEnvelope,
    output_path: Path | str,
    *,
    overwrite: bool = False,
) -> Path:
    """Write a deterministic report envelope to a local UTF-8 JSON file."""
    path = Path(output_path)
    if path.exists() and not overwrite:
        msg = f"report output already exists: {path}"
        raise DeterministicReportExportError(msg)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report_to_json(report), encoding="utf-8")
    return path


def _text_fields_for_advanced_output_scan(report: DeterministicReportEnvelope) -> str:
    parts = [
        report.summary,
        " ".join(report.recommended_next_steps),
        " ".join(report.allowed_downstream_uses),
        " ".join(report.forbidden_downstream_uses),
        " ".join(finding.message for finding in report.findings),
        json.dumps(report.workflow_payload, sort_keys=True),
    ]
    return " ".join(parts).lower()


def validate_report_has_no_unsupported_advanced_outputs(
    report: DeterministicReportEnvelope,
) -> None:
    """Fail closed if report text fields contain unsupported advanced-output claims."""
    if report.schema_version != DETERMINISTIC_REPORT_SCHEMA_VERSION:
        msg = f"unsupported schema_version: {report.schema_version}"
        raise DeterministicReportExportError(msg)
    text = _text_fields_for_advanced_output_scan(report)
    match = _UNSUPPORTED_ADVANCED_OUTPUT_PATTERN.search(text)
    if match is not None:
        msg = f"report contains unsupported advanced output claim: {match.group(0)}"
        raise DeterministicReportExportError(msg)
