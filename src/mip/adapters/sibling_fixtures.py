"""Pinned sibling-repo fixture export imports for adapter governance paths."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any

from pydantic import Field, field_validator, model_validator

from mip.adapters.base import (
    AdapterOutputBundle,
    AdapterRunKind,
    AdapterRunStatus,
    AdapterValidationReport,
)
from mip.adapters.geox import GeoXAdapterOutputPlaceholder
from mip.adapters.governance import (
    AdapterRegistrationResult,
    register_adapter_output,
    trust_report_for_adapter_output,
)
from mip.adapters.mmm import MMMAdapterOutputPlaceholder
from mip.contracts import DecisionSurface, ExperimentEvidence, TrustReport
from mip.contracts.base import ContractBaseModel
from mip.evidence.registry import EvidenceRegistry

_REQUIRED_LABELS = (
    "pinned_sibling_repo_fixture_only",
    "not_live_engine_execution",
)

_FORBIDDEN_CLAIM_PHRASES = (
    "actual roi",
    "true roi",
    "incremental lift",
    "causal impact",
    "model result",
    "budget recommendation",
    "production-ready",
)

_DISCLAIMER = (
    "Pinned sibling-repo fixture import only. No live engine execution. "
    "Structural metadata placeholder; not a real model result and not decision-ready."
)

_REPO_ROOT = Path(__file__).resolve().parents[3]
_DEFAULT_MMM_FIXTURE_PATH = (
    _REPO_ROOT / "tests/fixtures/sibling_exports/mmm_adapter_export_fixture.json"
)
_DEFAULT_GEOX_FIXTURE_PATH = (
    _REPO_ROOT / "tests/fixtures/sibling_exports/geox_adapter_export_fixture.json"
)


class SiblingFixtureSource(StrEnum):
    """Sibling repository that produced a pinned fixture export."""

    MMM = "mmm"
    PANEL_EXP = "panel_exp"


class SiblingFixtureArtifactKind(StrEnum):
    """Artifact kind encoded in a sibling fixture export."""

    MMM_ADAPTER_OUTPUT = "mmm_adapter_output"
    GEOX_ADAPTER_OUTPUT = "geox_adapter_output"


class SiblingFixtureValidationStatus(StrEnum):
    """Validation status for a sibling fixture export."""

    VALIDATED_FIXTURE = "validated_fixture"
    BLOCKED_FIXTURE = "blocked_fixture"
    INVALID_FIXTURE = "invalid_fixture"


class SiblingFixtureExport(ContractBaseModel):
    """Pinned sibling-repo fixture export contract."""

    fixture_id: str
    source_repo: SiblingFixtureSource
    source_commit_marker: str
    export_schema_version: str
    artifact_kind: SiblingFixtureArtifactKind
    engine_kind: AdapterRunKind
    config_marker: str
    validation_status: SiblingFixtureValidationStatus
    labels: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)
    disclaimer: str = _DISCLAIMER
    payload: dict[str, Any] = Field(default_factory=dict)

    @field_validator(
        "fixture_id",
        "source_commit_marker",
        "export_schema_version",
        "config_marker",
        "disclaimer",
    )
    @classmethod
    def non_empty(cls, value: str) -> str:
        if not value.strip():
            msg = "sibling fixture export string fields cannot be empty"
            raise ValueError(msg)
        return value

    @field_validator("labels", "warnings", "blocking_reasons")
    @classmethod
    def string_lists_not_empty(cls, value: list[str]) -> list[str]:
        if any(not item.strip() for item in value):
            msg = "labels, warnings, and blocking_reasons cannot contain empty strings"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def export_consistency(self) -> SiblingFixtureExport:
        for label in _REQUIRED_LABELS:
            if label not in self.labels:
                msg = f"sibling fixture labels must include {label}"
                raise ValueError(msg)

        if self.source_repo == SiblingFixtureSource.MMM:
            if self.engine_kind != AdapterRunKind.MMM:
                msg = "mmm source repo requires engine_kind mmm"
                raise ValueError(msg)
            if self.artifact_kind != SiblingFixtureArtifactKind.MMM_ADAPTER_OUTPUT:
                msg = "mmm source repo requires mmm_adapter_output artifact kind"
                raise ValueError(msg)
        elif self.source_repo == SiblingFixtureSource.PANEL_EXP:
            if self.engine_kind != AdapterRunKind.GEOX:
                msg = "panel_exp source repo requires engine_kind geox"
                raise ValueError(msg)
            if self.artifact_kind != SiblingFixtureArtifactKind.GEOX_ADAPTER_OUTPUT:
                msg = "panel_exp source repo requires geox_adapter_output artifact kind"
                raise ValueError(msg)

        if self.validation_status == SiblingFixtureValidationStatus.VALIDATED_FIXTURE:
            if not self.payload:
                msg = "validated fixture requires payload"
                raise ValueError(msg)
        elif not self.blocking_reasons:
            msg = "blocked or invalid fixture requires blocking_reasons"
            raise ValueError(msg)

        return self


@dataclass(frozen=True)
class SiblingFixtureRegistrationResult:
    """Result of importing a sibling fixture export through governance paths."""

    fixture_id: str
    source_repo: SiblingFixtureSource
    source_commit_marker: str
    engine_kind: AdapterRunKind
    validation_status: SiblingFixtureValidationStatus
    adapter_output: AdapterOutputBundle | None
    registration: AdapterRegistrationResult
    labels: list[str]
    warnings: list[str]
    blocking_reasons: list[str]
    disclaimer: str


def default_mmm_sibling_fixture_path() -> Path:
    """Return the path to the pinned MMM sibling fixture export."""
    return _DEFAULT_MMM_FIXTURE_PATH


def default_geox_sibling_fixture_path() -> Path:
    """Return the path to the pinned GeoX sibling fixture export."""
    return _DEFAULT_GEOX_FIXTURE_PATH


def load_sibling_fixture_export(path: Path | str) -> SiblingFixtureExport:
    """Load and parse a pinned sibling fixture export JSON file."""
    fixture_path = Path(path)
    raw = json.loads(fixture_path.read_text(encoding="utf-8"))
    export = SiblingFixtureExport.model_validate(raw)
    assert_safe_sibling_fixture_export(export)
    return export


def validate_sibling_fixture_export(export: SiblingFixtureExport) -> list[str]:
    """Return blocking reasons when a sibling fixture export fails validation."""
    issues: list[str] = []
    for label in _REQUIRED_LABELS:
        if label not in export.labels:
            issues.append(f"missing required label: {label}")

    if not export.source_commit_marker.strip():
        issues.append("missing source_commit_marker")

    if not export.export_schema_version.strip():
        issues.append("missing export_schema_version")

    if export.source_repo == SiblingFixtureSource.MMM:
        if export.engine_kind != AdapterRunKind.MMM:
            issues.append("mmm source repo requires engine_kind mmm")
        if export.artifact_kind != SiblingFixtureArtifactKind.MMM_ADAPTER_OUTPUT:
            issues.append("mmm source repo requires mmm_adapter_output artifact kind")
    elif export.source_repo == SiblingFixtureSource.PANEL_EXP:
        if export.engine_kind != AdapterRunKind.GEOX:
            issues.append("panel_exp source repo requires engine_kind geox")
        if export.artifact_kind != SiblingFixtureArtifactKind.GEOX_ADAPTER_OUTPUT:
            issues.append("panel_exp source repo requires geox_adapter_output artifact kind")

    if export.validation_status == SiblingFixtureValidationStatus.VALIDATED_FIXTURE:
        if not export.payload:
            issues.append("validated fixture requires payload")
    elif not export.blocking_reasons:
        issues.append("blocked or invalid fixture requires blocking_reasons")

    return issues


def assert_safe_sibling_fixture_export(export: SiblingFixtureExport) -> None:
    """Raise if a sibling fixture export includes forbidden claims or labels."""
    issues = validate_sibling_fixture_export(export)
    if issues:
        msg = f"sibling fixture export validation failed: {', '.join(issues)}"
        raise ValueError(msg)

    combined = _claim_scan_text(export)
    for phrase in _FORBIDDEN_CLAIM_PHRASES:
        if phrase in combined:
            msg = f"sibling fixture export must not include forbidden phrase: {phrase}"
            raise ValueError(msg)
    if _contains_false_production_ready_claim(combined):
        msg = "sibling fixture export must not claim production-ready status"
        raise ValueError(msg)


def _claim_scan_text(export: SiblingFixtureExport) -> str:
    """Collect export text scanned for forbidden inferential claims."""
    payload_text = [str(value) for value in export.payload.values()]
    return "\n".join([*export.warnings, *export.blocking_reasons, *payload_text]).lower()


def sibling_fixture_to_adapter_output(export: SiblingFixtureExport) -> AdapterOutputBundle:
    """Convert a sibling fixture export into an AdapterOutputBundle."""
    assert_safe_sibling_fixture_export(export)
    marker = export.config_marker
    workflow_notes = str(
        export.payload.get(
            "workflow_notes",
            "Pinned sibling-repo fixture placeholder only; no model execution.",
        )
    )

    if export.validation_status == SiblingFixtureValidationStatus.BLOCKED_FIXTURE:
        return AdapterOutputBundle(
            kind=export.engine_kind,
            status=AdapterRunStatus.BLOCKED,
            source_config_marker=marker,
            reason=export.blocking_reasons[0],
            validation=AdapterValidationReport(
                status=AdapterRunStatus.BLOCKED,
                blocking_reasons=list(export.blocking_reasons),
            ),
        )

    if export.validation_status == SiblingFixtureValidationStatus.INVALID_FIXTURE:
        return AdapterOutputBundle(
            kind=export.engine_kind,
            status=AdapterRunStatus.FAILED,
            source_config_marker=marker,
            reason=export.blocking_reasons[0],
            validation=AdapterValidationReport(
                status=AdapterRunStatus.FAILED,
                blocking_reasons=list(export.blocking_reasons),
            ),
        )

    passed_checks = [
        "pinned_sibling_fixture_export",
        "placeholder_only_output",
        f"source_repo={_enum_value(export.source_repo)}",
        f"source_commit_marker={export.source_commit_marker}",
    ]
    validation = AdapterValidationReport(
        status=AdapterRunStatus.COMPLETED,
        passed_checks=passed_checks,
        warnings=list(export.warnings),
    )

    if export.engine_kind == AdapterRunKind.MMM:
        return AdapterOutputBundle(
            kind=AdapterRunKind.MMM,
            status=AdapterRunStatus.COMPLETED,
            source_config_marker=marker,
            validation=validation,
            mmm_output=MMMAdapterOutputPlaceholder(
                config_marker=marker,
                workflow_notes=workflow_notes,
            ),
        )

    return AdapterOutputBundle(
        kind=AdapterRunKind.GEOX,
        status=AdapterRunStatus.COMPLETED,
        source_config_marker=marker,
        validation=validation,
        geox_output=GeoXAdapterOutputPlaceholder(
            config_marker=marker,
            workflow_notes=workflow_notes,
        ),
    )


def trust_report_for_sibling_fixture(export: SiblingFixtureExport) -> TrustReport:
    """Build a TrustReport for a sibling fixture export via adapter governance."""
    output_bundle = sibling_fixture_to_adapter_output(export)
    return trust_report_for_adapter_output(output_bundle)


def register_sibling_fixture_export(
    registry: EvidenceRegistry,
    export: SiblingFixtureExport,
) -> SiblingFixtureRegistrationResult:
    """Import a sibling fixture export through adapter governance and registry paths."""
    output_bundle = sibling_fixture_to_adapter_output(export)
    registration = register_adapter_output(registry, output_bundle)
    return SiblingFixtureRegistrationResult(
        fixture_id=export.fixture_id,
        source_repo=export.source_repo,
        source_commit_marker=export.source_commit_marker,
        engine_kind=export.engine_kind,
        validation_status=export.validation_status,
        adapter_output=output_bundle,
        registration=registration,
        labels=list(export.labels),
        warnings=list(export.warnings),
        blocking_reasons=list(export.blocking_reasons),
        disclaimer=export.disclaimer,
    )


def sibling_fixture_import_sections(
    export: SiblingFixtureExport,
    result: SiblingFixtureRegistrationResult,
) -> dict[str, object]:
    """Format a sibling fixture import result for display-only UI sections."""
    assert_safe_sibling_fixture_export(export)
    registration = result.registration
    artifact = registration.artifact
    governance_artifact_ref: dict[str, object] | None = None
    if isinstance(artifact, DecisionSurface):
        governance_artifact_ref = {
            "artifact_type": "decision_surface_fixture",
            "artifact_id": artifact.surface_id,
        }
    elif isinstance(artifact, ExperimentEvidence):
        governance_artifact_ref = {
            "artifact_type": "experiment_evidence_fixture",
            "artifact_id": artifact.evidence_id,
        }

    trust_report = registration.trust_report
    return {
        "fixture_id": export.fixture_id,
        "source_repo": _enum_value(export.source_repo),
        "source_commit_marker": export.source_commit_marker,
        "engine_kind": _enum_value(export.engine_kind),
        "validation_status": _enum_value(export.validation_status),
        "labels": list(export.labels),
        "warnings": list(export.warnings),
        "blocking_reasons": list(export.blocking_reasons),
        "adapter_output_ref": {
            "artifact_type": "adapter_output_bundle",
            "artifact_id": registration.adapter_output_id,
        },
        "governance_artifact_ref": governance_artifact_ref,
        "trust_report_verdict": _enum_value(trust_report.confidence_tier),
        "trust_report_id": trust_report.trust_report_id,
        "registered_in_registry": registration.registered_in_registry,
        "disclaimer": export.disclaimer,
        "safety_note": (
            "Pinned sibling-repo fixture import only. No live engine execution "
            "or real model results."
        ),
    }


def build_default_sibling_fixture_import_sections() -> list[dict[str, object]]:
    """Load pinned test fixtures and format display sections for each."""
    sections: list[dict[str, object]] = []
    for path in (default_mmm_sibling_fixture_path(), default_geox_sibling_fixture_path()):
        if not path.exists():
            continue
        export = load_sibling_fixture_export(path)
        result = register_sibling_fixture_export(EvidenceRegistry(), export)
        sections.append(sibling_fixture_import_sections(export, result))
    return sections


def _contains_false_production_ready_claim(text: str) -> bool:
    for match in re.finditer(r"production[- ]ready", text):
        start = match.start()
        prefix = text[max(0, start - 4) : start]
        if not prefix.endswith("not "):
            return True
    return False


def _enum_value(value: object) -> str:
    if isinstance(value, str):
        return value
    return str(getattr(value, "value", value))


__all__ = [
    "SiblingFixtureArtifactKind",
    "SiblingFixtureExport",
    "SiblingFixtureRegistrationResult",
    "SiblingFixtureSource",
    "SiblingFixtureValidationStatus",
    "assert_safe_sibling_fixture_export",
    "build_default_sibling_fixture_import_sections",
    "default_geox_sibling_fixture_path",
    "default_mmm_sibling_fixture_path",
    "load_sibling_fixture_export",
    "register_sibling_fixture_export",
    "sibling_fixture_import_sections",
    "sibling_fixture_to_adapter_output",
    "trust_report_for_sibling_fixture",
    "validate_sibling_fixture_export",
]
