"""Read-only sibling repo export compatibility registry and checks."""

from __future__ import annotations

import re
from collections.abc import Iterable
from enum import StrEnum
from pathlib import Path

from pydantic import Field, field_validator, model_validator

from mip.adapters.base import AdapterRunKind
from mip.adapters.sibling_export_hooks import (
    SiblingExportDirectoryRef,
    SiblingExportDiscoveryResult,
    SiblingExportHookStatus,
    SiblingExportRegistrationResult,
    load_sibling_exports_from_directory,
    register_sibling_exports_from_directory,
)
from mip.adapters.sibling_fixtures import SiblingFixtureSource
from mip.contracts.base import ContractBaseModel
from mip.evidence.registry import EvidenceRegistry

_REQUIRED_LABELS = (
    "sibling_repo_compatibility_check_only",
    "readonly_export_contract_only",
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
    "Sibling repo compatibility check only. Read-only export contract validation; "
    "no live sibling repo execution, model training, or inferential claims."
)

_DEFAULT_EXPORT_RELATIVE_PATH = "integrations/mip/exports"
_REPO_ROOT = Path(__file__).resolve().parents[3]
_DEFAULT_FIXTURE_REPO_ROOT = _REPO_ROOT / "tests/fixtures"
_DEFAULT_FIXTURE_EXPORT_RELATIVE = "sibling_exports"


class SiblingRepoName(StrEnum):
    """Known sibling repository names."""

    MMM = "mmm"
    PANEL_EXP = "panel_exp"


class SiblingRepoCompatibilityStatus(StrEnum):
    """Compatibility status for a sibling repo export configuration."""

    COMPATIBLE = "compatible"
    COMPATIBLE_WITH_WARNINGS = "compatible_with_warnings"
    NOT_CONFIGURED = "not_configured"
    BLOCKED = "blocked"
    INVALID = "invalid"


class SiblingRepoExportConfig(ContractBaseModel):
    """Governed configuration for locating sibling repo static exports."""

    repo_name: SiblingRepoName
    repo_path: str
    export_directory_relative_path: str = _DEFAULT_EXPORT_RELATIVE_PATH
    expected_source_repo: SiblingFixtureSource
    expected_engine_kind: AdapterRunKind
    expected_schema_version: str
    expected_source_commit_marker: str | None = None
    read_only: bool = True
    recursive: bool = False
    follow_symlinks: bool = False
    labels: list[str] = Field(default_factory=list)
    notes: str | None = None

    @field_validator("repo_path", "export_directory_relative_path", "expected_schema_version")
    @classmethod
    def non_empty(cls, value: str) -> str:
        if not value.strip():
            msg = "sibling repo export config string fields cannot be empty"
            raise ValueError(msg)
        return value

    @field_validator("expected_source_commit_marker", "notes")
    @classmethod
    def optional_non_empty(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            msg = "optional config notes cannot be empty strings"
            raise ValueError(msg)
        return value

    @field_validator("labels")
    @classmethod
    def string_lists_not_empty(cls, value: list[str]) -> list[str]:
        if any(not item.strip() for item in value):
            msg = "config labels cannot contain empty strings"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def config_consistency(self) -> SiblingRepoExportConfig:
        if not self.read_only:
            msg = "sibling repo export config must be read_only"
            raise ValueError(msg)

        for label in _REQUIRED_LABELS:
            if label not in self.labels:
                msg = f"sibling repo export config labels must include {label}"
                raise ValueError(msg)

        if self.repo_name == SiblingRepoName.MMM:
            if self.expected_source_repo != SiblingFixtureSource.MMM:
                msg = "mmm repo requires expected_source_repo mmm"
                raise ValueError(msg)
            if self.expected_engine_kind != AdapterRunKind.MMM:
                msg = "mmm repo requires expected_engine_kind mmm"
                raise ValueError(msg)
        elif self.repo_name == SiblingRepoName.PANEL_EXP:
            if self.expected_source_repo != SiblingFixtureSource.PANEL_EXP:
                msg = "panel_exp repo requires expected_source_repo panel_exp"
                raise ValueError(msg)
            if self.expected_engine_kind != AdapterRunKind.GEOX:
                msg = "panel_exp repo requires expected_engine_kind geox"
                raise ValueError(msg)

        if ".." in Path(self.export_directory_relative_path).parts:
            msg = "export directory relative path cannot contain .."
            raise ValueError(msg)

        return self


class SiblingRepoCompatibilityReport(ContractBaseModel):
    """Compatibility report for one sibling repo export configuration."""

    config: SiblingRepoExportConfig
    resolved_export_directory: str
    status: SiblingRepoCompatibilityStatus
    discovered_export_count: int = 0
    compatible_export_count: int = 0
    incompatible_export_count: int = 0
    schema_versions_found: list[str] = Field(default_factory=list)
    source_commit_markers_found: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)
    labels: list[str] = Field(default_factory=list)
    disclaimer: str = _DISCLAIMER

    @field_validator(
        "resolved_export_directory",
        "disclaimer",
    )
    @classmethod
    def non_empty(cls, value: str) -> str:
        if not value.strip():
            msg = "compatibility report string fields cannot be empty"
            raise ValueError(msg)
        return value

    @field_validator(
        "schema_versions_found",
        "source_commit_markers_found",
        "warnings",
        "blocking_reasons",
        "labels",
    )
    @classmethod
    def string_lists_not_empty(cls, value: list[str]) -> list[str]:
        if any(not item.strip() for item in value):
            msg = "compatibility report string lists cannot contain empty strings"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def labels_present(self) -> SiblingRepoCompatibilityReport:
        for label in _REQUIRED_LABELS:
            if label not in self.labels:
                msg = f"compatibility report labels must include {label}"
                raise ValueError(msg)
        return self


class SiblingRepoCompatibilityRegistry(ContractBaseModel):
    """Aggregate compatibility registry over multiple sibling repo configs."""

    known_configs: list[SiblingRepoExportConfig] = Field(default_factory=list)
    reports: list[SiblingRepoCompatibilityReport] = Field(default_factory=list)
    aggregate_status: SiblingRepoCompatibilityStatus
    warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)

    @field_validator("warnings", "blocking_reasons")
    @classmethod
    def string_lists_not_empty(cls, value: list[str]) -> list[str]:
        if any(not item.strip() for item in value):
            msg = "registry warnings and blocking_reasons cannot contain empty strings"
            raise ValueError(msg)
        return value


def default_mmm_repo_export_config() -> SiblingRepoExportConfig:
    """Return a sample MMM repo export config over committed test fixtures."""
    return SiblingRepoExportConfig(
        repo_name=SiblingRepoName.MMM,
        repo_path=str(_DEFAULT_FIXTURE_REPO_ROOT),
        export_directory_relative_path=_DEFAULT_FIXTURE_EXPORT_RELATIVE,
        expected_source_repo=SiblingFixtureSource.MMM,
        expected_engine_kind=AdapterRunKind.MMM,
        expected_schema_version="1.0.0",
        labels=list(_REQUIRED_LABELS),
        notes="Sample MMM compatibility config over committed fixture exports.",
    )


def default_panel_exp_repo_export_config() -> SiblingRepoExportConfig:
    """Return a sample panel_exp repo export config over committed test fixtures."""
    return SiblingRepoExportConfig(
        repo_name=SiblingRepoName.PANEL_EXP,
        repo_path=str(_DEFAULT_FIXTURE_REPO_ROOT),
        export_directory_relative_path=_DEFAULT_FIXTURE_EXPORT_RELATIVE,
        expected_source_repo=SiblingFixtureSource.PANEL_EXP,
        expected_engine_kind=AdapterRunKind.GEOX,
        expected_schema_version="1.0.0",
        labels=list(_REQUIRED_LABELS),
        notes="Sample panel_exp compatibility config over committed fixture exports.",
    )


def default_sample_compatibility_configs() -> list[SiblingRepoExportConfig]:
    """Return default sample configs for demos and tests."""
    return [
        default_mmm_repo_export_config(),
        default_panel_exp_repo_export_config(),
    ]


def resolve_export_directory(config: SiblingRepoExportConfig) -> Path:
    """Resolve and validate the absolute export directory for a repo config."""
    repo_root = Path(config.repo_path).expanduser().resolve()
    relative = Path(config.export_directory_relative_path)
    if ".." in relative.parts:
        msg = "export directory relative path cannot escape repo root via .."
        raise ValueError(msg)
    resolved = (repo_root / relative).resolve()
    if repo_root not in resolved.parents and resolved != repo_root:
        msg = "export directory path cannot escape repo root"
        raise ValueError(msg)
    return resolved


def check_sibling_repo_compatibility(
    config: SiblingRepoExportConfig,
) -> SiblingRepoCompatibilityReport:
    """Check whether a sibling repo export directory is compatible."""
    assert_safe_sibling_compatibility(config)
    labels = list(_REQUIRED_LABELS)

    if not config.repo_path.strip():
        return _blocked_report(
            config,
            "",
            SiblingRepoCompatibilityStatus.NOT_CONFIGURED,
            ["repo path is not configured"],
            labels=labels,
        )

    try:
        resolved = resolve_export_directory(config)
    except ValueError as exc:
        return _blocked_report(
            config,
            "",
            SiblingRepoCompatibilityStatus.INVALID,
            [str(exc)],
            labels=labels,
        )

    if not resolved.exists():
        return _blocked_report(
            config,
            str(resolved),
            SiblingRepoCompatibilityStatus.NOT_CONFIGURED,
            [f"export directory does not exist: {resolved}"],
            labels=labels,
        )
    if not resolved.is_dir():
        return _blocked_report(
            config,
            str(resolved),
            SiblingRepoCompatibilityStatus.BLOCKED,
            [f"resolved export path is not a directory: {resolved}"],
            labels=labels,
        )

    directory_ref = _directory_ref_from_config(config, resolved)
    discovery = load_sibling_exports_from_directory(directory_ref)
    return _report_from_discovery(config, str(resolved), discovery, labels)


def build_sibling_repo_compatibility_registry(
    configs: list[SiblingRepoExportConfig],
) -> SiblingRepoCompatibilityRegistry:
    """Build an aggregate compatibility registry for known sibling repo configs."""
    reports = [check_sibling_repo_compatibility(config) for config in configs]
    warnings: list[str] = []
    blockers: list[str] = []
    for report in reports:
        warnings.extend(
            f"{_enum_value(report.config.repo_name)}: {item}" for item in report.warnings
        )
        blockers.extend(
            f"{_enum_value(report.config.repo_name)}: {item}"
            for item in report.blocking_reasons
        )

    aggregate_status = _aggregate_status(report.status for report in reports)
    registry = SiblingRepoCompatibilityRegistry(
        known_configs=list(configs),
        reports=reports,
        aggregate_status=aggregate_status,
        warnings=warnings,
        blocking_reasons=blockers,
    )
    assert_safe_sibling_compatibility(registry)
    return registry


def compatibility_report_to_directory_ref(
    report: SiblingRepoCompatibilityReport,
) -> SiblingExportDirectoryRef:
    """Convert a compatible report into a Phase 8C export directory ref."""
    if report.status not in (
        SiblingRepoCompatibilityStatus.COMPATIBLE,
        SiblingRepoCompatibilityStatus.COMPATIBLE_WITH_WARNINGS,
    ):
        msg = "incompatible report cannot produce export directory ref"
        raise ValueError(msg)
    if not report.resolved_export_directory.strip():
        msg = "compatible report requires resolved export directory"
        raise ValueError(msg)

    return _directory_ref_from_config(
        report.config,
        Path(report.resolved_export_directory),
    )


def discover_exports_for_compatible_repo(
    report: SiblingRepoCompatibilityReport,
) -> SiblingExportDiscoveryResult:
    """Discover exports for a compatible sibling repo report via Phase 8C hooks."""
    directory_ref = compatibility_report_to_directory_ref(report)
    return load_sibling_exports_from_directory(directory_ref)


def register_exports_for_compatible_repo(
    registry: EvidenceRegistry,
    report: SiblingRepoCompatibilityReport,
) -> tuple[SiblingExportDiscoveryResult, list[SiblingExportRegistrationResult]]:
    """Register exports only when compatibility status allows safe import."""
    if report.status not in (
        SiblingRepoCompatibilityStatus.COMPATIBLE,
        SiblingRepoCompatibilityStatus.COMPATIBLE_WITH_WARNINGS,
    ):
        msg = "incompatible report cannot register usable exports"
        raise ValueError(msg)
    directory_ref = compatibility_report_to_directory_ref(report)
    return register_sibling_exports_from_directory(registry, directory_ref)


def sibling_compatibility_sections(
    obj: SiblingRepoCompatibilityReport | SiblingRepoCompatibilityRegistry,
) -> dict[str, object]:
    """Format compatibility artifacts for display-only UI sections."""
    assert_safe_sibling_compatibility(obj)
    if isinstance(obj, SiblingRepoCompatibilityReport):
        return _report_sections(obj)
    return _registry_sections(obj)


def build_default_sibling_compatibility_sections() -> dict[str, object]:
    """Build display sections for the default sample compatibility registry."""
    registry = build_sibling_repo_compatibility_registry(default_sample_compatibility_configs())
    return sibling_compatibility_sections(registry)


def assert_safe_sibling_compatibility(
    obj: (
        SiblingRepoExportConfig
        | SiblingRepoCompatibilityReport
        | SiblingRepoCompatibilityRegistry
    ),
) -> None:
    """Raise if compatibility artifacts include forbidden inferential claims."""
    combined = _claim_scan_text(obj)
    for phrase in _FORBIDDEN_CLAIM_PHRASES:
        if phrase in combined:
            msg = f"sibling compatibility artifact must not include forbidden phrase: {phrase}"
            raise ValueError(msg)
    if _contains_false_production_ready_claim(combined):
        msg = "sibling compatibility artifact must not claim production-ready status"
        raise ValueError(msg)


def _report_from_discovery(
    config: SiblingRepoExportConfig,
    resolved_path: str,
    discovery: SiblingExportDiscoveryResult,
    labels: list[str],
) -> SiblingRepoCompatibilityReport:
    warnings = list(discovery.validation_warnings)
    blockers = list(discovery.blocking_reasons)
    discovered_count = len(discovery.discovered_file_paths)
    schema_versions: set[str] = set()
    commit_markers: set[str] = set()
    compatible_count = 0
    incompatible_count = 0

    loaded_ids = {export.fixture_id for export in discovery.loaded_exports}
    for export in discovery.loaded_exports:
        schema_versions.add(export.export_schema_version)
        commit_markers.add(export.source_commit_marker)
        export_issues = _export_compatibility_issues(config, export)
        if export_issues:
            incompatible_count += 1
            warnings.extend(f"{export.fixture_id}: {issue}" for issue in export_issues)
        else:
            compatible_count += 1

    incompatible_count += discovered_count - len(loaded_ids)

    if not resolved_path.strip() or (
        discovery.status == SiblingExportHookStatus.NOT_CONFIGURED and compatible_count == 0
    ):
        status = SiblingRepoCompatibilityStatus.NOT_CONFIGURED
    elif discovery.status == SiblingExportHookStatus.BLOCKED and compatible_count == 0:
        status = SiblingRepoCompatibilityStatus.BLOCKED
    elif compatible_count == 0:
        status = SiblingRepoCompatibilityStatus.INVALID
    elif incompatible_count > 0 or warnings or blockers:
        status = SiblingRepoCompatibilityStatus.COMPATIBLE_WITH_WARNINGS
    else:
        status = SiblingRepoCompatibilityStatus.COMPATIBLE

    report = SiblingRepoCompatibilityReport(
        config=config,
        resolved_export_directory=resolved_path,
        status=status,
        discovered_export_count=discovered_count,
        compatible_export_count=compatible_count,
        incompatible_export_count=incompatible_count,
        schema_versions_found=sorted(schema_versions),
        source_commit_markers_found=sorted(commit_markers),
        warnings=warnings,
        blocking_reasons=blockers,
        labels=labels,
    )
    assert_safe_sibling_compatibility(report)
    return report


def _export_compatibility_issues(
    config: SiblingRepoExportConfig,
    export: object,
) -> list[str]:
    from mip.adapters.sibling_fixtures import SiblingFixtureExport

    if not isinstance(export, SiblingFixtureExport):
        return ["invalid_export_type"]
    issues: list[str] = []
    if export.export_schema_version != config.expected_schema_version:
        issues.append(
            f"schema_version_mismatch expected {config.expected_schema_version} "
            f"got {export.export_schema_version}"
        )
    if (
        config.expected_source_commit_marker is not None
        and export.source_commit_marker != config.expected_source_commit_marker
    ):
        issues.append("source_commit_marker_mismatch")
    return issues


def _directory_ref_from_config(
    config: SiblingRepoExportConfig,
    resolved: Path,
) -> SiblingExportDirectoryRef:
    return SiblingExportDirectoryRef(
        directory_path=str(resolved),
        expected_source_repo=config.expected_source_repo,
        expected_engine_kind=config.expected_engine_kind,
        recursive=config.recursive,
        follow_symlinks=config.follow_symlinks,
    )


def _blocked_report(
    config: SiblingRepoExportConfig,
    resolved_path: str,
    status: SiblingRepoCompatibilityStatus,
    blockers: list[str],
    *,
    labels: list[str],
) -> SiblingRepoCompatibilityReport:
    report = SiblingRepoCompatibilityReport(
        config=config,
        resolved_export_directory=resolved_path or "not_resolved",
        status=status,
        blocking_reasons=blockers,
        labels=labels,
    )
    assert_safe_sibling_compatibility(report)
    return report


def _aggregate_status(
    statuses: Iterable[SiblingRepoCompatibilityStatus],
) -> SiblingRepoCompatibilityStatus:
    status_list = list(statuses)
    if not status_list:
        return SiblingRepoCompatibilityStatus.NOT_CONFIGURED
    if any(status == SiblingRepoCompatibilityStatus.INVALID for status in status_list):
        return SiblingRepoCompatibilityStatus.INVALID
    if any(status == SiblingRepoCompatibilityStatus.BLOCKED for status in status_list):
        return SiblingRepoCompatibilityStatus.BLOCKED
    if any(status == SiblingRepoCompatibilityStatus.NOT_CONFIGURED for status in status_list):
        return SiblingRepoCompatibilityStatus.NOT_CONFIGURED
    if any(
        status == SiblingRepoCompatibilityStatus.COMPATIBLE_WITH_WARNINGS for status in status_list
    ):
        return SiblingRepoCompatibilityStatus.COMPATIBLE_WITH_WARNINGS
    if all(status == SiblingRepoCompatibilityStatus.COMPATIBLE for status in status_list):
        return SiblingRepoCompatibilityStatus.COMPATIBLE
    return SiblingRepoCompatibilityStatus.BLOCKED


def _report_sections(report: SiblingRepoCompatibilityReport) -> dict[str, object]:
    return {
        "repo_name": _enum_value(report.config.repo_name),
        "repo_path": report.config.repo_path,
        "resolved_export_directory": report.resolved_export_directory,
        "expected_schema_version": report.config.expected_schema_version,
        "expected_source_commit_marker": report.config.expected_source_commit_marker,
        "status": _enum_value(report.status),
        "discovered_export_count": report.discovered_export_count,
        "compatible_export_count": report.compatible_export_count,
        "incompatible_export_count": report.incompatible_export_count,
        "schema_versions_found": list(report.schema_versions_found),
        "source_commit_markers_found": list(report.source_commit_markers_found),
        "labels": list(report.labels),
        "warnings": list(report.warnings),
        "blocking_reasons": list(report.blocking_reasons),
        "disclaimer": report.disclaimer,
        "safety_note": (
            "Compatibility check only. No live sibling repo execution or real model results."
        ),
    }


def _registry_sections(registry: SiblingRepoCompatibilityRegistry) -> dict[str, object]:
    return {
        "aggregate_status": _enum_value(registry.aggregate_status),
        "known_config_count": len(registry.known_configs),
        "reports": [sibling_compatibility_sections(report) for report in registry.reports],
        "warnings": list(registry.warnings),
        "blocking_reasons": list(registry.blocking_reasons),
        "disclaimer": _DISCLAIMER,
        "safety_note": (
            "Compatibility check only. No live sibling repo execution or real model results."
        ),
    }


def _claim_scan_text(
    obj: (
        SiblingRepoExportConfig
        | SiblingRepoCompatibilityReport
        | SiblingRepoCompatibilityRegistry
    ),
) -> str:
    if isinstance(obj, SiblingRepoExportConfig):
        parts = [obj.notes] if obj.notes else []
    elif isinstance(obj, SiblingRepoCompatibilityReport):
        parts = list(obj.warnings)
    else:
        parts = list(obj.warnings)
        for report in obj.reports:
            parts.extend(report.warnings)
    return "\n".join(part for part in parts if part).lower()


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
    "SiblingRepoCompatibilityRegistry",
    "SiblingRepoCompatibilityReport",
    "SiblingRepoCompatibilityStatus",
    "SiblingRepoExportConfig",
    "SiblingRepoName",
    "assert_safe_sibling_compatibility",
    "build_default_sibling_compatibility_sections",
    "build_sibling_repo_compatibility_registry",
    "check_sibling_repo_compatibility",
    "compatibility_report_to_directory_ref",
    "default_mmm_repo_export_config",
    "default_panel_exp_repo_export_config",
    "default_sample_compatibility_configs",
    "discover_exports_for_compatible_repo",
    "register_exports_for_compatible_repo",
    "resolve_export_directory",
    "sibling_compatibility_sections",
]
