"""Deterministic data readiness checks."""

from enum import StrEnum

from pydantic import field_validator

from mip.contracts.base import ContractBaseModel
from mip.workflows.intake.feasibility import FeasibilityStatus, ObjectiveFeasibilityReport
from mip.workflows.readiness.profile import DatasetProfile, DetectedTimeGrain


def _grain_is_unknown(grain: DetectedTimeGrain | str) -> bool:
    return grain == DetectedTimeGrain.UNKNOWN or grain == DetectedTimeGrain.UNKNOWN.value


def _grain_is_irregular(grain: DetectedTimeGrain | str) -> bool:
    return grain == DetectedTimeGrain.IRREGULAR or grain == DetectedTimeGrain.IRREGULAR.value


class ReadinessSeverity(StrEnum):
    """Severity of a readiness check finding."""

    INFO = "info"
    WARNING = "warning"
    BLOCKER = "blocker"


class ReadinessCheckCode(StrEnum):
    """Machine-readable readiness check identifier."""

    MISSING_REQUIRED_FIELD = "missing_required_field"
    MISSING_RECOMMENDED_FIELD = "missing_recommended_field"
    MISSING_DATE_FIELD = "missing_date_field"
    TOO_FEW_ROWS = "too_few_rows"
    TOO_SHORT_HISTORY = "too_short_history"
    MISSING_VALUES = "missing_values"
    INSUFFICIENT_GEO_BREAKDOWN = "insufficient_geo_breakdown"
    MISSING_CHANNEL_BREAKDOWN = "missing_channel_breakdown"
    UNKNOWN_TIME_GRAIN = "unknown_time_grain"
    IRREGULAR_TIME_GRAIN = "irregular_time_grain"
    OBJECTIVE_NOT_FEASIBLE = "objective_not_feasible"
    DIAGNOSTIC_ONLY = "diagnostic_only"
    READY = "ready"


class ReadinessCheckResult(ContractBaseModel):
    """Single readiness check outcome."""

    code: ReadinessCheckCode
    severity: ReadinessSeverity
    message: str
    field_name: str | None = None

    @field_validator("message")
    @classmethod
    def message_not_empty(cls, value: str) -> str:
        if not value.strip():
            msg = "message cannot be empty"
            raise ValueError(msg)
        return value

    @field_validator("field_name")
    @classmethod
    def field_name_not_blank(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            msg = "field_name cannot be empty when provided"
            raise ValueError(msg)
        return value


def run_readiness_checks(
    profile: DatasetProfile,
    feasibility: ObjectiveFeasibilityReport | None = None,
) -> list[ReadinessCheckResult]:
    """Run deterministic readiness checks against a dataset profile."""
    results: list[ReadinessCheckResult] = []

    if profile.row_count < 10:
        results.append(
            ReadinessCheckResult(
                code=ReadinessCheckCode.TOO_FEW_ROWS,
                severity=ReadinessSeverity.BLOCKER,
                message=f"Dataset has only {profile.row_count} rows; at least 10 are required.",
            )
        )

    if profile.date_field is None:
        results.append(
            ReadinessCheckResult(
                code=ReadinessCheckCode.MISSING_DATE_FIELD,
                severity=ReadinessSeverity.BLOCKER,
                message="No date-like field detected in the dataset.",
            )
        )

    if _grain_is_unknown(profile.time_grain):
        results.append(
            ReadinessCheckResult(
                code=ReadinessCheckCode.UNKNOWN_TIME_GRAIN,
                severity=ReadinessSeverity.WARNING,
                message="Time grain could not be inferred from date values.",
            )
        )
    elif _grain_is_irregular(profile.time_grain):
        results.append(
            ReadinessCheckResult(
                code=ReadinessCheckCode.IRREGULAR_TIME_GRAIN,
                severity=ReadinessSeverity.WARNING,
                message="Date values follow an irregular time cadence.",
            )
        )

    if profile.history_weeks is not None and profile.history_weeks < 52:
        results.append(
            ReadinessCheckResult(
                code=ReadinessCheckCode.TOO_SHORT_HISTORY,
                severity=ReadinessSeverity.WARNING,
                message=(
                    f"History spans approximately {profile.history_weeks} weeks; "
                    "52 weeks is recommended for MMM."
                ),
            )
        )

    for field_name, missingness in profile.missingness_by_field.items():
        if missingness > 0.2:
            results.append(
                ReadinessCheckResult(
                    code=ReadinessCheckCode.MISSING_VALUES,
                    severity=ReadinessSeverity.WARNING,
                    message=f"Field '{field_name}' has {missingness:.0%} missing values.",
                    field_name=field_name,
                )
            )

    if feasibility is not None:
        for field_name in feasibility.missing_required_fields:
            results.append(
                ReadinessCheckResult(
                    code=ReadinessCheckCode.MISSING_REQUIRED_FIELD,
                    severity=ReadinessSeverity.BLOCKER,
                    message=f"Required field '{field_name}' is missing for the objective.",
                    field_name=field_name,
                )
            )

        for field_name in feasibility.missing_recommended_fields:
            results.append(
                ReadinessCheckResult(
                    code=ReadinessCheckCode.MISSING_RECOMMENDED_FIELD,
                    severity=ReadinessSeverity.WARNING,
                    message=f"Recommended field '{field_name}' is missing for the objective.",
                    field_name=field_name,
                )
            )

        if feasibility.status == FeasibilityStatus.BLOCKED:
            reason = (
                feasibility.blocking_reasons[0]
                if feasibility.blocking_reasons
                else "Objective is not feasible with available data."
            )
            results.append(
                ReadinessCheckResult(
                    code=ReadinessCheckCode.OBJECTIVE_NOT_FEASIBLE,
                    severity=ReadinessSeverity.BLOCKER,
                    message=reason,
                )
            )
        elif feasibility.status == FeasibilityStatus.DIAGNOSTIC_ONLY:
            results.append(
                ReadinessCheckResult(
                    code=ReadinessCheckCode.DIAGNOSTIC_ONLY,
                    severity=ReadinessSeverity.WARNING,
                    message="Objective is feasible for diagnostic analysis only.",
                )
            )

    has_blockers = any(result.severity == ReadinessSeverity.BLOCKER for result in results)
    has_warnings = any(result.severity == ReadinessSeverity.WARNING for result in results)
    if not has_blockers and not has_warnings:
        results.append(
            ReadinessCheckResult(
                code=ReadinessCheckCode.READY,
                severity=ReadinessSeverity.INFO,
                message="Dataset passes structural readiness checks.",
            )
        )

    return results
