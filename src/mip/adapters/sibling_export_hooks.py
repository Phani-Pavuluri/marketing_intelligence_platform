"""Read-only discovery and import hooks for sibling export JSON directories."""

from __future__ import annotations

import json
import re
from enum import StrEnum
from pathlib import Path

from pydantic import Field, ValidationError, field_validator, model_validator

from mip.adapters.base import AdapterRunKind
from mip.adapters.sibling_fixtures import (
    SiblingFixtureExport,
    SiblingFixtureSource,
    SiblingFixtureValidationStatus,
    assert_safe_sibling_fixture_export,
    register_sibling_fixture_export,
    validate_sibling_fixture_export,
)
from mip.contracts import DecisionSurface, ExperimentEvidence
from mip.contracts.base import ContractBaseModel
from mip.evidence.registry import EvidenceRegistry

_REQUIRED_LABELS = (
    "readonly_sibling_export_hook_only",
    "static_export_file_only",
    "not_live_engine_execution",
    "not_real_model_result",
    "diagnostic_only",
    "not_decision_ready",
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
    "Read-only sibling export hook only. Static JSON files are imported; "
    "no live sibling repo execution, model training, or inferential claims."
)

_REPO_ROOT = Path(__file__).resolve().parents[3]
_DEFAULT_SAMPLE_EXPORT_DIRECTORY = _REPO_ROOT / "tests/fixtures/sibling_exports"


class SiblingExportHookStatus(StrEnum):
    """Status for sibling export directory discovery and registration."""

    NOT_CONFIGURED = "not_configured"
    DISCOVERED = "discovered"
    VALIDATED = "validated"
    BLOCKED = "blocked"
    INVALID = "invalid"


class SiblingExportDirectoryRef(ContractBaseModel):
    """Reference to a sibling export directory for read-only discovery."""

    directory_path: str
    expected_source_repo: SiblingFixtureSource | None = None
    expected_engine_kind: AdapterRunKind | None = None
    recursive: bool = False
    allowed_filename_suffix: str = ".json"
    follow_symlinks: bool = False

    @field_validator("directory_path", "allowed_filename_suffix")
    @classmethod
    def non_empty(cls, value: str) -> str:
        if not value.strip():
            msg = "directory ref string fields cannot be empty"
            raise ValueError(msg)
        return value


class SiblingExportDiscoveryResult(ContractBaseModel):
    """Result of discovering and loading sibling export JSON files."""

    directory_ref: SiblingExportDirectoryRef
    status: SiblingExportHookStatus
    discovered_file_paths: list[str] = Field(default_factory=list)
    loaded_exports: list[SiblingFixtureExport] = Field(default_factory=list)
    validation_warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)
    labels: list[str] = Field(default_factory=list)
    disclaimer: str = _DISCLAIMER

    @field_validator("discovered_file_paths", "validation_warnings", "blocking_reasons", "labels")
    @classmethod
    def string_lists_not_empty(cls, value: list[str]) -> list[str]:
        if any(not item.strip() for item in value):
            msg = "discovery result string lists cannot contain empty strings"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def labels_present(self) -> SiblingExportDiscoveryResult:
        for label in _REQUIRED_LABELS:
            if label not in self.labels:
                msg = f"sibling export hook labels must include {label}"
                raise ValueError(msg)
        return self


class SiblingExportRegistrationResult(ContractBaseModel):
    """Per-file registration result for a sibling export hook import."""

    source_path: str
    export_fixture_id: str
    adapter_output_marker: str
    governance_artifact_marker: str | None = None
    trust_report_marker: str | None = None
    registered_in_registry: bool = False
    status: SiblingExportHookStatus
    warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)

    @field_validator(
        "source_path",
        "export_fixture_id",
        "adapter_output_marker",
        "governance_artifact_marker",
        "trust_report_marker",
    )
    @classmethod
    def optional_non_empty(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            msg = "registration marker fields cannot be empty strings"
            raise ValueError(msg)
        return value

    @field_validator("warnings", "blocking_reasons")
    @classmethod
    def string_lists_not_empty(cls, value: list[str]) -> list[str]:
        if any(not item.strip() for item in value):
            msg = "warnings and blocking_reasons cannot contain empty strings"
            raise ValueError(msg)
        return value


def default_sample_export_directory() -> Path:
    """Return the default sample sibling export directory used in demos."""
    return _DEFAULT_SAMPLE_EXPORT_DIRECTORY


def default_sample_export_directory_ref() -> SiblingExportDirectoryRef:
    """Return a directory ref for the committed sample sibling export fixtures."""
    return SiblingExportDirectoryRef(directory_path=str(default_sample_export_directory()))


def discover_sibling_export_files(
    directory_ref: SiblingExportDirectoryRef,
) -> SiblingExportDiscoveryResult:
    """Discover JSON export files in an explicit sibling export directory."""
    directory = Path(directory_ref.directory_path)
    if not directory_ref.directory_path.strip():
        return _blocked_discovery(
            directory_ref,
            SiblingExportHookStatus.NOT_CONFIGURED,
            ["directory path is not configured"],
        )
    if not directory.exists():
        return _blocked_discovery(
            directory_ref,
            SiblingExportHookStatus.NOT_CONFIGURED,
            [f"directory does not exist: {directory}"],
        )
    if not directory.is_dir():
        return _blocked_discovery(
            directory_ref,
            SiblingExportHookStatus.BLOCKED,
            [f"path is not a directory: {directory}"],
        )

    discovered = _discover_json_files(directory_ref)
    if not discovered:
        return _blocked_discovery(
            directory_ref,
            SiblingExportHookStatus.BLOCKED,
            [f"no {directory_ref.allowed_filename_suffix} files discovered"],
        )

    return SiblingExportDiscoveryResult(
        directory_ref=directory_ref,
        status=SiblingExportHookStatus.DISCOVERED,
        discovered_file_paths=[str(path) for path in discovered],
        labels=list(_REQUIRED_LABELS),
    )


def load_sibling_exports_from_directory(
    directory_ref: SiblingExportDirectoryRef,
) -> SiblingExportDiscoveryResult:
    """Discover and load sibling export JSON files without raising on malformed input."""
    discovery = discover_sibling_export_files(directory_ref)
    if discovery.status in (
        SiblingExportHookStatus.NOT_CONFIGURED,
        SiblingExportHookStatus.BLOCKED,
    ):
        return discovery

    loaded_exports: list[SiblingFixtureExport] = []
    warnings: list[str] = list(discovery.validation_warnings)
    blockers: list[str] = list(discovery.blocking_reasons)

    for file_path in discovery.discovered_file_paths:
        export, file_warnings, file_blockers = _load_export_file(
            Path(file_path),
            directory_ref,
        )
        warnings.extend(file_warnings)
        blockers.extend(file_blockers)
        if export is not None:
            loaded_exports.append(export)

    status = _status_after_load(
        discovered_count=len(discovery.discovered_file_paths),
        loaded_count=len(loaded_exports),
        blockers=blockers,
    )
    return SiblingExportDiscoveryResult(
        directory_ref=directory_ref,
        status=status,
        discovered_file_paths=list(discovery.discovered_file_paths),
        loaded_exports=loaded_exports,
        validation_warnings=warnings,
        blocking_reasons=blockers,
        labels=list(_REQUIRED_LABELS),
    )


def validate_sibling_export_directory(
    result: SiblingExportDiscoveryResult,
) -> SiblingExportDiscoveryResult:
    """Validate a discovery result and refresh hook status from export checks."""
    if result.status in (
        SiblingExportHookStatus.NOT_CONFIGURED,
        SiblingExportHookStatus.BLOCKED,
    ):
        return result

    warnings = list(result.validation_warnings)
    blockers = list(result.blocking_reasons)
    validated_exports: list[SiblingFixtureExport] = []

    for export in result.loaded_exports:
        issues = validate_sibling_fixture_export(export)
        if issues:
            blockers.append(
                f"{export.fixture_id}: export validation failed: {', '.join(issues)}"
            )
            continue
        try:
            assert_safe_sibling_fixture_export(export)
        except ValueError as exc:
            blockers.append(f"{export.fixture_id}: {exc}")
            continue
        validated_exports.append(export)

    status = _status_after_load(
        discovered_count=len(result.discovered_file_paths),
        loaded_count=len(validated_exports),
        blockers=blockers,
    )

    updated = result.model_copy(
        update={
            "status": status,
            "loaded_exports": validated_exports,
            "validation_warnings": warnings,
            "blocking_reasons": blockers,
        }
    )
    assert_safe_sibling_export_hook_result(updated)
    return updated


def register_sibling_exports_from_directory(
    registry: EvidenceRegistry,
    directory_ref: SiblingExportDirectoryRef,
) -> tuple[SiblingExportDiscoveryResult, list[SiblingExportRegistrationResult]]:
    """Load, validate, and register sibling exports from a directory."""
    discovery = validate_sibling_export_directory(
        load_sibling_exports_from_directory(directory_ref)
    )
    registrations: list[SiblingExportRegistrationResult] = []

    for file_path in discovery.discovered_file_paths:
        path = Path(file_path)
        export, _, _ = _load_export_file(path, discovery.directory_ref)
        if export is None:
            registrations.append(
                SiblingExportRegistrationResult(
                    source_path=str(path),
                    export_fixture_id="unknown",
                    adapter_output_marker="not_registered",
                    status=SiblingExportHookStatus.INVALID,
                    blocking_reasons=_blockers_for_path(discovery, path),
                )
            )
            continue
        registrations.append(_register_loaded_export(registry, path, export))

    assert_safe_sibling_export_hook_result(discovery)
    for item in registrations:
        assert_safe_sibling_export_hook_result(item)
    return discovery, registrations


def sibling_export_discovery_sections(
    result: SiblingExportDiscoveryResult,
    registrations: list[SiblingExportRegistrationResult] | None = None,
) -> dict[str, object]:
    """Format a sibling export discovery result for display-only UI sections."""
    assert_safe_sibling_export_hook_result(result)
    registration_rows: list[dict[str, object]] = []
    for item in registrations or []:
        assert_safe_sibling_export_hook_result(item)
        registration_rows.append(
            {
                "source_path": item.source_path,
                "export_fixture_id": item.export_fixture_id,
                "adapter_output_marker": item.adapter_output_marker,
                "governance_artifact_marker": item.governance_artifact_marker,
                "trust_report_marker": item.trust_report_marker,
                "registered_in_registry": item.registered_in_registry,
                "status": _enum_value(item.status),
                "warnings": list(item.warnings),
                "blocking_reasons": list(item.blocking_reasons),
            }
        )

    export_summaries = [
        {
            "fixture_id": export.fixture_id,
            "source_repo": _enum_value(export.source_repo),
            "engine_kind": _enum_value(export.engine_kind),
            "validation_status": _enum_value(export.validation_status),
        }
        for export in result.loaded_exports
    ]

    return {
        "directory_path": result.directory_ref.directory_path,
        "status": _enum_value(result.status),
        "discovered_file_paths": list(result.discovered_file_paths),
        "loaded_export_count": len(result.loaded_exports),
        "export_summaries": export_summaries,
        "registration_results": registration_rows,
        "labels": list(result.labels),
        "validation_warnings": list(result.validation_warnings),
        "blocking_reasons": list(result.blocking_reasons),
        "disclaimer": result.disclaimer,
        "safety_note": (
            "Static export file import only. No live sibling repo execution "
            "or real model results."
        ),
    }


def build_default_sibling_export_hook_sections() -> dict[str, object]:
    """Build display sections for the default sample sibling export directory."""
    directory_ref = default_sample_export_directory_ref()
    discovery, registrations = register_sibling_exports_from_directory(
        EvidenceRegistry(),
        directory_ref,
    )
    return sibling_export_discovery_sections(discovery, registrations)


def assert_safe_sibling_export_hook_result(
    obj: SiblingExportDiscoveryResult | SiblingExportRegistrationResult,
) -> None:
    """Raise if a sibling export hook result includes forbidden claims."""
    combined = _claim_scan_text(obj)
    for phrase in _FORBIDDEN_CLAIM_PHRASES:
        if phrase in combined:
            msg = f"sibling export hook result must not include forbidden phrase: {phrase}"
            raise ValueError(msg)
    if _contains_false_production_ready_claim(combined):
        msg = "sibling export hook result must not claim production-ready status"
        raise ValueError(msg)


def _blockers_for_path(discovery: SiblingExportDiscoveryResult, path: Path) -> list[str]:
    matched = [
        reason
        for reason in discovery.blocking_reasons
        if path.name in reason or str(path) in reason
    ]
    return matched or ["export failed validation and was not registered"]


def _register_loaded_export(
    registry: EvidenceRegistry,
    source_path: Path,
    export: SiblingFixtureExport,
) -> SiblingExportRegistrationResult:
    if export.validation_status != SiblingFixtureValidationStatus.VALIDATED_FIXTURE:
        return SiblingExportRegistrationResult(
            source_path=str(source_path),
            export_fixture_id=export.fixture_id,
            adapter_output_marker="not_registered",
            status=SiblingExportHookStatus.BLOCKED,
            blocking_reasons=list(export.blocking_reasons)
            or ["export is blocked and cannot register usable evidence"],
        )

    registration = register_sibling_fixture_export(registry, export)
    artifact_marker: str | None = None
    artifact = registration.registration.artifact
    if isinstance(artifact, DecisionSurface):
        artifact_marker = artifact.surface_id
    elif isinstance(artifact, ExperimentEvidence):
        artifact_marker = artifact.evidence_id

    return SiblingExportRegistrationResult(
        source_path=str(source_path),
        export_fixture_id=export.fixture_id,
        adapter_output_marker=registration.registration.adapter_output_id,
        governance_artifact_marker=artifact_marker,
        trust_report_marker=registration.registration.trust_report.trust_report_id,
        registered_in_registry=registration.registration.registered_in_registry,
        status=SiblingExportHookStatus.VALIDATED,
        warnings=list(export.warnings),
        blocking_reasons=list(export.blocking_reasons),
    )


def _load_export_file(
    path: Path,
    directory_ref: SiblingExportDirectoryRef,
) -> tuple[SiblingFixtureExport | None, list[str], list[str]]:
    warnings: list[str] = []
    blockers: list[str] = []

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        blockers.append(f"{path.name}: malformed_json")
        return None, warnings, blockers

    try:
        export = SiblingFixtureExport.model_validate(raw)
    except ValidationError as exc:
        blockers.append(f"{path.name}: invalid_export_schema")
        warnings.append(f"{path.name}: schema validation detail suppressed for safety")
        _ = exc
        return None, warnings, blockers

    mismatch_blockers = _directory_expectation_blockers(directory_ref, export, path.name)
    if mismatch_blockers:
        blockers.extend(mismatch_blockers)
        return None, warnings, blockers

    try:
        assert_safe_sibling_fixture_export(export)
    except ValueError as exc:
        blockers.append(f"{path.name}: {exc}")
        return None, warnings, blockers

    return export, warnings, blockers


def _directory_expectation_blockers(
    directory_ref: SiblingExportDirectoryRef,
    export: SiblingFixtureExport,
    file_name: str,
) -> list[str]:
    blockers: list[str] = []
    if (
        directory_ref.expected_source_repo is not None
        and export.source_repo != directory_ref.expected_source_repo
    ):
        blockers.append(
            f"{file_name}: source_repo_mismatch expected "
            f"{_enum_value(directory_ref.expected_source_repo)} "
            f"got {_enum_value(export.source_repo)}"
        )
    if (
        directory_ref.expected_engine_kind is not None
        and export.engine_kind != directory_ref.expected_engine_kind
    ):
        blockers.append(
            f"{file_name}: engine_kind_mismatch expected "
            f"{_enum_value(directory_ref.expected_engine_kind)} "
            f"got {_enum_value(export.engine_kind)}"
        )
    return blockers


def _discover_json_files(directory_ref: SiblingExportDirectoryRef) -> list[Path]:
    directory = Path(directory_ref.directory_path)
    suffix = directory_ref.allowed_filename_suffix
    paths: list[Path] = []
    if directory_ref.recursive:
        iterator = directory.rglob(f"*{suffix}")
    else:
        iterator = directory.glob(f"*{suffix}")
    for path in sorted(iterator):
        if not path.is_file():
            continue
        if not directory_ref.follow_symlinks and path.is_symlink():
            continue
        paths.append(path)
    return paths


def _status_after_load(
    *,
    discovered_count: int,
    loaded_count: int,
    blockers: list[str],
) -> SiblingExportHookStatus:
    if discovered_count == 0:
        return SiblingExportHookStatus.BLOCKED
    if loaded_count == 0:
        return SiblingExportHookStatus.INVALID
    if loaded_count < discovered_count or blockers:
        return SiblingExportHookStatus.INVALID
    return SiblingExportHookStatus.VALIDATED


def _blocked_discovery(
    directory_ref: SiblingExportDirectoryRef,
    status: SiblingExportHookStatus,
    blockers: list[str],
) -> SiblingExportDiscoveryResult:
    return SiblingExportDiscoveryResult(
        directory_ref=directory_ref,
        status=status,
        blocking_reasons=blockers,
        labels=list(_REQUIRED_LABELS),
    )


def _claim_scan_text(
    obj: SiblingExportDiscoveryResult | SiblingExportRegistrationResult,
) -> str:
    if isinstance(obj, SiblingExportDiscoveryResult):
        parts = [*obj.validation_warnings, *obj.blocking_reasons]
        for export in obj.loaded_exports:
            parts.extend(export.warnings)
            parts.extend(export.blocking_reasons)
            parts.extend(str(value) for value in export.payload.values())
    else:
        parts = [*obj.warnings, *obj.blocking_reasons]
    return "\n".join(parts).lower()


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
    "SiblingExportDirectoryRef",
    "SiblingExportDiscoveryResult",
    "SiblingExportHookStatus",
    "SiblingExportRegistrationResult",
    "assert_safe_sibling_export_hook_result",
    "build_default_sibling_export_hook_sections",
    "default_sample_export_directory",
    "default_sample_export_directory_ref",
    "discover_sibling_export_files",
    "load_sibling_exports_from_directory",
    "register_sibling_exports_from_directory",
    "sibling_export_discovery_sections",
    "validate_sibling_export_directory",
]
