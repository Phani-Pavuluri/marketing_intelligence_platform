"""Local path wiring for read-only sibling repo static export directories."""

from __future__ import annotations

import re
from enum import StrEnum
from pathlib import Path

from pydantic import Field, field_validator, model_validator

from mip.adapters.base import AdapterRunKind
from mip.adapters.sibling_compatibility import (
    SiblingRepoCompatibilityRegistry,
    SiblingRepoCompatibilityReport,
    SiblingRepoCompatibilityStatus,
    SiblingRepoExportConfig,
    SiblingRepoName,
    assert_safe_sibling_compatibility,
    build_sibling_repo_compatibility_registry,
    check_sibling_repo_compatibility,
    register_exports_for_compatible_repo,
)
from mip.adapters.sibling_export_hooks import SiblingExportRegistrationResult
from mip.adapters.sibling_fixtures import SiblingFixtureSource
from mip.contracts.base import ContractBaseModel
from mip.evidence.registry import EvidenceRegistry

_LOCAL_REQUIRED_LABELS = (
    "local_sibling_export_path_wiring_only",
    "readonly_export_contract_only",
    "static_export_file_only",
    "not_live_engine_execution",
    "not_real_model_result",
    "diagnostic_only",
    "not_decision_ready",
)

_COMPATIBILITY_LABELS = (
    "sibling_repo_compatibility_check_only",
)

_CONFIG_LABELS = _LOCAL_REQUIRED_LABELS + _COMPATIBILITY_LABELS + (
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
    "Local sibling export path wiring only. Reads static JSON export files from "
    "configured sibling directories; no live engine execution or inferential claims."
)

_DEFAULT_MMM_REPO_PATH = "/Users/phani/Desktop/mmm"
_DEFAULT_PANEL_EXP_REPO_PATH = "/Users/phani/Desktop/panel_exp"
_DEFAULT_EXPORT_RELATIVE_PATH = "integrations/mip/exports"
_DEFAULT_SCHEMA_VERSION = "1.0.0"


class LocalSiblingPathStatus(StrEnum):
    """Status for local sibling export path wiring."""

    CONFIGURED = "configured"
    NOT_FOUND = "not_found"
    COMPATIBLE = "compatible"
    COMPATIBLE_WITH_WARNINGS = "compatible_with_warnings"
    BLOCKED = "blocked"
    INVALID = "invalid"


class LocalSiblingRepoPathDefaults(ContractBaseModel):
    """Default local sibling repo path settings for read-only export wiring."""

    mmm_repo_path: str = _DEFAULT_MMM_REPO_PATH
    panel_exp_repo_path: str = _DEFAULT_PANEL_EXP_REPO_PATH
    export_directory_relative_path: str = _DEFAULT_EXPORT_RELATIVE_PATH
    expected_schema_version: str = _DEFAULT_SCHEMA_VERSION
    read_only: bool = True
    labels: list[str] = Field(default_factory=lambda: list(_LOCAL_REQUIRED_LABELS))
    disclaimer: str = _DISCLAIMER

    @field_validator(
        "mmm_repo_path",
        "panel_exp_repo_path",
        "export_directory_relative_path",
        "expected_schema_version",
        "disclaimer",
    )
    @classmethod
    def non_empty(cls, value: str) -> str:
        if not value.strip():
            msg = "local sibling path defaults string fields cannot be empty"
            raise ValueError(msg)
        return value

    @field_validator("labels")
    @classmethod
    def string_lists_not_empty(cls, value: list[str]) -> list[str]:
        if any(not item.strip() for item in value):
            msg = "local sibling path labels cannot contain empty strings"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def defaults_consistency(self) -> LocalSiblingRepoPathDefaults:
        if not self.read_only:
            msg = "local sibling path defaults must be read_only"
            raise ValueError(msg)
        for label in _LOCAL_REQUIRED_LABELS:
            if label not in self.labels:
                msg = f"local sibling path labels must include {label}"
                raise ValueError(msg)
        if ".." in Path(self.export_directory_relative_path).parts:
            msg = "export directory relative path cannot escape repo root via .."
            raise ValueError(msg)
        for repo_path in (self.mmm_repo_path, self.panel_exp_repo_path):
            if not Path(repo_path).is_absolute():
                msg = f"repo path must be an explicit absolute path: {repo_path}"
                raise ValueError(msg)
        return self


class LocalSiblingPathRegistryResult(ContractBaseModel):
    """Aggregate result for local sibling export path wiring."""

    defaults: LocalSiblingRepoPathDefaults
    compatibility_registry: SiblingRepoCompatibilityRegistry
    mmm_report: SiblingRepoCompatibilityReport | None = None
    panel_exp_report: SiblingRepoCompatibilityReport | None = None
    aggregate_status: LocalSiblingPathStatus
    warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)
    labels: list[str] = Field(default_factory=list)
    disclaimer: str = _DISCLAIMER

    @field_validator("warnings", "blocking_reasons", "labels")
    @classmethod
    def string_lists_not_empty(cls, value: list[str]) -> list[str]:
        if any(not item.strip() for item in value):
            msg = "local path registry string lists cannot contain empty strings"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def labels_present(self) -> LocalSiblingPathRegistryResult:
        for label in _LOCAL_REQUIRED_LABELS:
            if label not in self.labels:
                msg = f"local path registry labels must include {label}"
                raise ValueError(msg)
        return self


def default_local_sibling_path_config() -> LocalSiblingRepoPathDefaults:
    """Return default local sibling repo path settings."""
    return LocalSiblingRepoPathDefaults()


def build_local_mmm_export_config(
    defaults: LocalSiblingRepoPathDefaults | None = None,
) -> SiblingRepoExportConfig:
    """Build a governed MMM sibling export config from local path defaults."""
    settings = defaults or default_local_sibling_path_config()
    assert_safe_local_sibling_path_result(settings)
    return SiblingRepoExportConfig(
        repo_name=SiblingRepoName.MMM,
        repo_path=settings.mmm_repo_path,
        export_directory_relative_path=settings.export_directory_relative_path,
        expected_source_repo=SiblingFixtureSource.MMM,
        expected_engine_kind=AdapterRunKind.MMM,
        expected_schema_version=settings.expected_schema_version,
        read_only=settings.read_only,
        labels=_config_labels(settings),
        notes="Local MMM sibling export path wiring; read-only JSON import only.",
    )


def build_local_panel_exp_export_config(
    defaults: LocalSiblingRepoPathDefaults | None = None,
) -> SiblingRepoExportConfig:
    """Build a governed panel_exp sibling export config from local path defaults."""
    settings = defaults or default_local_sibling_path_config()
    assert_safe_local_sibling_path_result(settings)
    return SiblingRepoExportConfig(
        repo_name=SiblingRepoName.PANEL_EXP,
        repo_path=settings.panel_exp_repo_path,
        export_directory_relative_path=settings.export_directory_relative_path,
        expected_source_repo=SiblingFixtureSource.PANEL_EXP,
        expected_engine_kind=AdapterRunKind.GEOX,
        expected_schema_version=settings.expected_schema_version,
        read_only=settings.read_only,
        labels=_config_labels(settings),
        notes="Local panel_exp sibling export path wiring; read-only JSON import only.",
    )


def build_local_sibling_compatibility_registry(
    defaults: LocalSiblingRepoPathDefaults | None = None,
) -> LocalSiblingPathRegistryResult:
    """Build a local sibling path compatibility registry from defaults."""
    settings = defaults or default_local_sibling_path_config()
    assert_safe_local_sibling_path_result(settings)

    mmm_config = build_local_mmm_export_config(settings)
    panel_config = build_local_panel_exp_export_config(settings)
    mmm_report = _local_compatibility_report(mmm_config, settings)
    panel_report = _local_compatibility_report(panel_config, settings)

    compatibility_registry = build_sibling_repo_compatibility_registry(
        [mmm_config, panel_config]
    )
    warnings = list(compatibility_registry.warnings)
    blockers = list(compatibility_registry.blocking_reasons)

    aggregate_status = _aggregate_local_status(
        mmm_report.status if mmm_report is not None else None,
        panel_report.status if panel_report is not None else None,
        compatibility_registry.aggregate_status,
    )

    result = LocalSiblingPathRegistryResult(
        defaults=settings,
        compatibility_registry=compatibility_registry,
        mmm_report=mmm_report,
        panel_exp_report=panel_report,
        aggregate_status=aggregate_status,
        warnings=warnings,
        blocking_reasons=blockers,
        labels=list(_LOCAL_REQUIRED_LABELS),
    )
    assert_safe_local_sibling_path_result(result)
    return result


def register_compatible_local_sibling_exports(
    registry: EvidenceRegistry,
    defaults: LocalSiblingRepoPathDefaults | None = None,
) -> tuple[LocalSiblingPathRegistryResult, list[SiblingExportRegistrationResult]]:
    """Register exports only for locally compatible sibling repo reports."""
    result = build_local_sibling_compatibility_registry(defaults)
    registrations: list[SiblingExportRegistrationResult] = []

    for report in (result.mmm_report, result.panel_exp_report):
        if report is None:
            continue
        if report.status not in (
            SiblingRepoCompatibilityStatus.COMPATIBLE,
            SiblingRepoCompatibilityStatus.COMPATIBLE_WITH_WARNINGS,
        ):
            continue
        _, repo_registrations = register_exports_for_compatible_repo(registry, report)
        registrations.extend(repo_registrations)

    assert_safe_local_sibling_path_result(result)
    return result, registrations


def local_sibling_path_sections(
    result: LocalSiblingPathRegistryResult,
) -> dict[str, object]:
    """Format a local sibling path registry result for display-only UI sections."""
    assert_safe_local_sibling_path_result(result)
    defaults = result.defaults
    return {
        "mmm_repo_path": defaults.mmm_repo_path,
        "panel_exp_repo_path": defaults.panel_exp_repo_path,
        "export_directory_relative_path": defaults.export_directory_relative_path,
        "expected_schema_version": defaults.expected_schema_version,
        "aggregate_status": _enum_value(result.aggregate_status),
        "mmm_status": _report_status(result.mmm_report),
        "panel_exp_status": _report_status(result.panel_exp_report),
        "mmm_discovered_export_count": _report_count(result.mmm_report, "discovered"),
        "mmm_compatible_export_count": _report_count(result.mmm_report, "compatible"),
        "panel_exp_discovered_export_count": _report_count(result.panel_exp_report, "discovered"),
        "panel_exp_compatible_export_count": _report_count(result.panel_exp_report, "compatible"),
        "labels": list(result.labels),
        "warnings": list(result.warnings),
        "blocking_reasons": list(result.blocking_reasons),
        "disclaimer": result.disclaimer,
        "safety_note": (
            "Reads static export JSON only from configured sibling directories. "
            "No live engine execution."
        ),
    }


def build_default_local_sibling_path_sections() -> dict[str, object]:
    """Build display sections for default local sibling export path wiring."""
    result = build_local_sibling_compatibility_registry()
    return local_sibling_path_sections(result)


def assert_safe_local_sibling_path_result(
    obj: LocalSiblingRepoPathDefaults | LocalSiblingPathRegistryResult,
) -> None:
    """Raise if local sibling path artifacts include forbidden inferential claims."""
    combined = _claim_scan_text(obj)
    for phrase in _FORBIDDEN_CLAIM_PHRASES:
        if phrase in combined:
            msg = f"local sibling path artifact must not include forbidden phrase: {phrase}"
            raise ValueError(msg)
    if _contains_false_production_ready_claim(combined):
        msg = "local sibling path artifact must not claim production-ready status"
        raise ValueError(msg)


def _local_compatibility_report(
    config: SiblingRepoExportConfig,
    settings: LocalSiblingRepoPathDefaults,
) -> SiblingRepoCompatibilityReport:
    repo_root = Path(config.repo_path)
    labels = _config_labels(settings)
    if not repo_root.exists():
        return _not_found_report(
            config,
            labels,
            [f"sibling repo path not found: {repo_root}"],
        )
    return check_sibling_repo_compatibility(config)


def _not_found_report(
    config: SiblingRepoExportConfig,
    labels: list[str],
    blockers: list[str],
) -> SiblingRepoCompatibilityReport:
    report = SiblingRepoCompatibilityReport(
        config=config,
        resolved_export_directory="not_resolved",
        status=SiblingRepoCompatibilityStatus.NOT_CONFIGURED,
        blocking_reasons=blockers,
        labels=labels,
    )
    assert_safe_sibling_compatibility(report)
    return report


def _config_labels(settings: LocalSiblingRepoPathDefaults) -> list[str]:
    merged = list(dict.fromkeys([*_CONFIG_LABELS, *settings.labels]))
    return merged


def _aggregate_local_status(
    mmm_status: SiblingRepoCompatibilityStatus | None,
    panel_status: SiblingRepoCompatibilityStatus | None,
    registry_status: SiblingRepoCompatibilityStatus,
) -> LocalSiblingPathStatus:
    local_statuses = [
        _map_compat_status_to_local(status)
        for status in (mmm_status, panel_status)
        if status is not None
    ]
    if not local_statuses:
        return _map_compat_status_to_local(registry_status)
    if any(status == LocalSiblingPathStatus.INVALID for status in local_statuses):
        return LocalSiblingPathStatus.INVALID
    if any(status == LocalSiblingPathStatus.BLOCKED for status in local_statuses):
        return LocalSiblingPathStatus.BLOCKED
    if all(status == LocalSiblingPathStatus.NOT_FOUND for status in local_statuses):
        return LocalSiblingPathStatus.NOT_FOUND
    if any(status == LocalSiblingPathStatus.NOT_FOUND for status in local_statuses):
        if any(
            status
            in (LocalSiblingPathStatus.COMPATIBLE, LocalSiblingPathStatus.COMPATIBLE_WITH_WARNINGS)
            for status in local_statuses
        ):
            return LocalSiblingPathStatus.COMPATIBLE_WITH_WARNINGS
        return LocalSiblingPathStatus.NOT_FOUND
    if any(status == LocalSiblingPathStatus.COMPATIBLE_WITH_WARNINGS for status in local_statuses):
        return LocalSiblingPathStatus.COMPATIBLE_WITH_WARNINGS
    if all(status == LocalSiblingPathStatus.COMPATIBLE for status in local_statuses):
        return LocalSiblingPathStatus.COMPATIBLE
    if any(status == LocalSiblingPathStatus.CONFIGURED for status in local_statuses):
        return LocalSiblingPathStatus.CONFIGURED
    return _map_compat_status_to_local(registry_status)


def _map_compat_status_to_local(
    status: SiblingRepoCompatibilityStatus,
) -> LocalSiblingPathStatus:
    if status == SiblingRepoCompatibilityStatus.COMPATIBLE:
        return LocalSiblingPathStatus.COMPATIBLE
    if status == SiblingRepoCompatibilityStatus.COMPATIBLE_WITH_WARNINGS:
        return LocalSiblingPathStatus.COMPATIBLE_WITH_WARNINGS
    if status == SiblingRepoCompatibilityStatus.NOT_CONFIGURED:
        return LocalSiblingPathStatus.NOT_FOUND
    if status == SiblingRepoCompatibilityStatus.BLOCKED:
        return LocalSiblingPathStatus.BLOCKED
    if status == SiblingRepoCompatibilityStatus.INVALID:
        return LocalSiblingPathStatus.INVALID
    return LocalSiblingPathStatus.CONFIGURED


def _report_status(report: SiblingRepoCompatibilityReport | None) -> str | None:
    if report is None:
        return None
    mapped = _map_compat_status_to_local(report.status)
    return _enum_value(mapped)


def _report_count(
    report: SiblingRepoCompatibilityReport | None,
    kind: str,
) -> int | None:
    if report is None:
        return None
    if kind == "discovered":
        return report.discovered_export_count
    return report.compatible_export_count


def _claim_scan_text(
    obj: LocalSiblingRepoPathDefaults | LocalSiblingPathRegistryResult,
) -> str:
    if isinstance(obj, LocalSiblingRepoPathDefaults):
        return (obj.disclaimer or "").lower()
    return "\n".join(obj.warnings).lower()


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
    "LocalSiblingPathRegistryResult",
    "LocalSiblingPathStatus",
    "LocalSiblingRepoPathDefaults",
    "assert_safe_local_sibling_path_result",
    "build_default_local_sibling_path_sections",
    "build_local_mmm_export_config",
    "build_local_panel_exp_export_config",
    "build_local_sibling_compatibility_registry",
    "default_local_sibling_path_config",
    "local_sibling_path_sections",
    "register_compatible_local_sibling_exports",
]
