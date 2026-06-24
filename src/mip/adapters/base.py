"""Shared adapter interface contracts and validation."""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING

from pydantic import Field, field_validator, model_validator

from mip.contracts.base import ContractBaseModel

if TYPE_CHECKING:
    from mip.adapters.geox import GeoXAdapterInput, GeoXAdapterOutputPlaceholder
    from mip.adapters.mmm import MMMAdapterInput, MMMAdapterOutputPlaceholder

_FORBIDDEN_CLAIM_PHRASES = (
    "estimated lift",
    "incremental roi",
    "causal impact",
    "budget recommendation",
    "model results",
    "ran mmm",
    "executed geox",
    "model execution was completed",
    "recommended spend",
)

_FORBIDDEN_FIELD_NAMES = frozenset(
    {
        "lift",
        "roi",
        "incremental_roi",
        "causal_impact",
        "budget_recommendation",
        "model_results",
        "channel_roi",
        "response_curve",
    }
)


class AdapterRunStatus(StrEnum):
    """Lifecycle status for adapter input and output bundles."""

    DRAFT = "draft"
    VALIDATED = "validated"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class AdapterRunKind(StrEnum):
    """Adapter engine family."""

    MMM = "mmm"
    GEOX = "geox"


class AdapterValidationReport(ContractBaseModel):
    """Validation summary for adapter output bundles."""

    status: AdapterRunStatus
    passed_checks: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)

    @field_validator("passed_checks", "warnings", "blocking_reasons")
    @classmethod
    def string_lists_not_empty(cls, value: list[str]) -> list[str]:
        if any(not item.strip() for item in value):
            msg = "validation string lists cannot contain empty strings"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def failed_or_blocked_requires_reasons(self) -> AdapterValidationReport:
        if self.status in (AdapterRunStatus.FAILED, AdapterRunStatus.BLOCKED):
            if not self.blocking_reasons:
                msg = "failed or blocked validation requires blocking_reasons"
                raise ValueError(msg)
        return self


class AdapterInputBundle(ContractBaseModel):
    """Adapter-safe input bundle built from a governed config draft."""

    kind: AdapterRunKind
    status: AdapterRunStatus
    source_config_marker: str
    objective_type: str
    warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)
    mmm_input: MMMAdapterInput | None = None
    geox_input: GeoXAdapterInput | None = None

    @field_validator("source_config_marker")
    @classmethod
    def marker_not_empty(cls, value: str) -> str:
        if not value.strip():
            msg = "source_config_marker cannot be empty"
            raise ValueError(msg)
        return value

    @field_validator("warnings", "blocking_reasons")
    @classmethod
    def string_lists_not_empty(cls, value: list[str]) -> list[str]:
        if any(not item.strip() for item in value):
            msg = "warnings and blocking_reasons cannot contain empty strings"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def kind_matches_payload(self) -> AdapterInputBundle:
        if self.kind == AdapterRunKind.MMM and self.mmm_input is None:
            msg = "mmm adapter input requires mmm_input payload"
            raise ValueError(msg)
        if self.kind == AdapterRunKind.GEOX and self.geox_input is None:
            msg = "geox adapter input requires geox_input payload"
            raise ValueError(msg)
        if self.kind == AdapterRunKind.MMM and self.geox_input is not None:
            msg = "mmm adapter input cannot include geox_input payload"
            raise ValueError(msg)
        if self.kind == AdapterRunKind.GEOX and self.mmm_input is not None:
            msg = "geox adapter input cannot include mmm_input payload"
            raise ValueError(msg)
        return self


class AdapterOutputBundle(ContractBaseModel):
    """Adapter-safe output bundle with governed placeholders only."""

    kind: AdapterRunKind
    status: AdapterRunStatus
    source_config_marker: str
    validation: AdapterValidationReport | None = None
    reason: str | None = None
    mmm_output: MMMAdapterOutputPlaceholder | None = None
    geox_output: GeoXAdapterOutputPlaceholder | None = None

    @field_validator("source_config_marker")
    @classmethod
    def marker_not_empty(cls, value: str) -> str:
        if not value.strip():
            msg = "source_config_marker cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def output_consistency(self) -> AdapterOutputBundle:
        if self.status == AdapterRunStatus.COMPLETED and self.validation is None:
            msg = "completed adapter output requires validation report"
            raise ValueError(msg)
        if self.status in (AdapterRunStatus.FAILED, AdapterRunStatus.BLOCKED):
            if not self.reason or not self.reason.strip():
                msg = "failed or blocked adapter output requires reason"
                raise ValueError(msg)
        if self.kind == AdapterRunKind.MMM and self.mmm_output is None:
            if self.status == AdapterRunStatus.COMPLETED:
                msg = "completed mmm adapter output requires mmm_output placeholder"
                raise ValueError(msg)
        if self.kind == AdapterRunKind.GEOX and self.geox_output is None:
            if self.status == AdapterRunStatus.COMPLETED:
                msg = "completed geox adapter output requires geox_output placeholder"
                raise ValueError(msg)
        return self


def validate_adapter_output(output_bundle: AdapterOutputBundle) -> AdapterValidationReport:
    """Validate adapter output structure, consistency, and safety boundaries."""
    _assert_no_forbidden_field_names(output_bundle)
    _assert_no_forbidden_claim_text(output_bundle.model_dump(mode="json"))

    if output_bundle.status == AdapterRunStatus.COMPLETED:
        if output_bundle.validation is None:
            msg = "completed adapter output requires validation report"
            raise ValueError(msg)
        return output_bundle.validation

    if output_bundle.status in (AdapterRunStatus.FAILED, AdapterRunStatus.BLOCKED):
        if not output_bundle.reason or not output_bundle.reason.strip():
            msg = "failed or blocked adapter output requires reason"
            raise ValueError(msg)

    if output_bundle.validation is not None:
        return output_bundle.validation

    msg = "adapter output requires validation report or explicit failed/blocked reason"
    raise ValueError(msg)


def _assert_no_forbidden_field_names(model: ContractBaseModel) -> None:
    for field_name in type(model).model_fields:
        if field_name.lower() in _FORBIDDEN_FIELD_NAMES:
            msg = f"adapter bundle must not include forbidden field: {field_name}"
            raise ValueError(msg)


def _assert_no_forbidden_claim_text(payload: object) -> None:
    for text in _collect_strings(payload):
        lowered = text.lower()
        for phrase in _FORBIDDEN_CLAIM_PHRASES:
            if phrase in lowered:
                msg = f"adapter output must not include forbidden claim phrase: {phrase}"
                raise ValueError(msg)


def _collect_strings(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        collected: list[str] = []
        for nested in value.values():
            collected.extend(_collect_strings(nested))
        return collected
    if isinstance(value, list):
        collected = []
        for nested in value:
            collected.extend(_collect_strings(nested))
        return collected
    return []
