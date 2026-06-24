"""Data readiness report assembly."""

from collections.abc import Mapping, Sequence
from enum import StrEnum

from pydantic import Field, field_validator, model_validator

from mip.contracts.base import ContractBaseModel
from mip.workflows.intake.feasibility import (
    FeasibilityStatus,
    ObjectiveFeasibilityReport,
    evaluate_objective_feasibility,
)
from mip.workflows.intake.objectives import BusinessObjective
from mip.workflows.readiness.checks import (
    ReadinessCheckCode,
    ReadinessCheckResult,
    ReadinessSeverity,
    run_readiness_checks,
)
from mip.workflows.readiness.profile import (
    DatasetProfile,
    profile_from_records,
    profile_to_availability,
)


class DataReadinessStatus(StrEnum):
    """Overall readiness verdict for a dataset."""

    READY = "ready"
    READY_WITH_WARNINGS = "ready_with_warnings"
    DIAGNOSTIC_ONLY = "diagnostic_only"
    BLOCKED = "blocked"


_SUMMARY_BY_STATUS: dict[DataReadinessStatus, str] = {
    DataReadinessStatus.BLOCKED: "Dataset is blocked for the requested workflow.",
    DataReadinessStatus.DIAGNOSTIC_ONLY: "Dataset is suitable for diagnostic use only.",
    DataReadinessStatus.READY_WITH_WARNINGS: "Dataset is ready with warnings.",
    DataReadinessStatus.READY: "Dataset is ready for the requested workflow.",
}


class DataReadinessReport(ContractBaseModel):
    """Governed readiness report for a dataset profile."""

    profile: DatasetProfile
    status: DataReadinessStatus
    checks: list[ReadinessCheckResult]
    summary: str
    blocking_reasons: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    recommended_fixes: list[str] = Field(default_factory=list)

    @field_validator("summary")
    @classmethod
    def summary_not_empty(cls, value: str) -> str:
        if not value.strip():
            msg = "summary cannot be empty"
            raise ValueError(msg)
        return value

    @field_validator("blocking_reasons", "warnings", "recommended_fixes")
    @classmethod
    def string_lists_not_empty(cls, value: list[str]) -> list[str]:
        if any(not item.strip() for item in value):
            msg = "blocking_reasons, warnings, and recommended_fixes cannot contain empty strings"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def report_consistency(self) -> "DataReadinessReport":
        if not self.checks:
            msg = "checks cannot be empty"
            raise ValueError(msg)
        if self.status == DataReadinessStatus.BLOCKED and not self.blocking_reasons:
            msg = "blocked status requires blocking_reasons"
            raise ValueError(msg)
        return self


def build_data_readiness_report(
    profile: DatasetProfile,
    feasibility: ObjectiveFeasibilityReport | None = None,
) -> DataReadinessReport:
    """Build a readiness report from profile checks and optional feasibility."""
    checks = run_readiness_checks(profile, feasibility)
    blockers = [check for check in checks if check.severity == ReadinessSeverity.BLOCKER]
    warnings = [check for check in checks if check.severity == ReadinessSeverity.WARNING]

    if blockers:
        status = DataReadinessStatus.BLOCKED
    elif feasibility is not None and feasibility.status == FeasibilityStatus.DIAGNOSTIC_ONLY:
        status = DataReadinessStatus.DIAGNOSTIC_ONLY
    elif warnings:
        status = DataReadinessStatus.READY_WITH_WARNINGS
    else:
        status = DataReadinessStatus.READY

    return DataReadinessReport(
        profile=profile,
        status=status,
        checks=checks,
        summary=_SUMMARY_BY_STATUS[status],
        blocking_reasons=[check.message for check in blockers],
        warnings=[check.message for check in warnings],
        recommended_fixes=_recommended_fixes(checks),
    )


def build_readiness_from_records(
    records: Sequence[Mapping[str, object]],
    objective: BusinessObjective | None = None,
) -> DataReadinessReport:
    """Profile records and optionally evaluate readiness for a business objective."""
    profile = profile_from_records(records)
    if objective is None:
        return build_data_readiness_report(profile)

    availability = profile_to_availability(profile)
    feasibility = evaluate_objective_feasibility(objective, availability)
    return build_data_readiness_report(profile, feasibility)


def _recommended_fixes(checks: list[ReadinessCheckResult]) -> list[str]:
    fixes: list[str] = []
    seen: set[str] = set()

    for check in checks:
        fix = _fix_for_check(check)
        if fix and fix not in seen:
            seen.add(fix)
            fixes.append(fix)

    return fixes


def _fix_for_check(check: ReadinessCheckResult) -> str | None:
    if check.code == ReadinessCheckCode.MISSING_DATE_FIELD:
        return "Provide a date/week/month field."
    if check.code == ReadinessCheckCode.TOO_FEW_ROWS:
        return "Provide more observations before running MMM or experiment workflows."
    if check.code == ReadinessCheckCode.TOO_SHORT_HISTORY:
        return "Provide at least 52 weeks of history for more stable MMM workflows."
    if check.code == ReadinessCheckCode.MISSING_REQUIRED_FIELD and check.field_name:
        return f"Provide required field: {check.field_name}."
    if check.code == ReadinessCheckCode.MISSING_RECOMMENDED_FIELD and check.field_name:
        return f"Consider providing recommended field: {check.field_name}."
    if check.code == ReadinessCheckCode.MISSING_VALUES and check.field_name:
        return f"Fill or investigate missing values in {check.field_name}."
    if check.code == ReadinessCheckCode.UNKNOWN_TIME_GRAIN:
        return "Use a consistent daily, weekly, or monthly time grain."
    if check.code == ReadinessCheckCode.IRREGULAR_TIME_GRAIN:
        return "Regularize the dataset to a consistent time grain."
    return None
