"""Stage A fixture adapters for deterministic workflow inputs (Stage A.3)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from mip.contracts.advisory import (
    ColdStartAdvisoryPlan,
    ColdStartBusinessProfile,
    ColdStartMediaObjective,
)
from mip.contracts.calibration_intake import (
    CalibrationEvidenceInput,
    CalibrationIntakeStatus,
    CalibrationMappingReport,
    CalibrationMappingRequirement,
)
from mip.contracts.deterministic_report import (
    DETERMINISTIC_REPORT_SCHEMA_VERSION,
    ArtifactReference,
    DeterministicReportEnvelope,
    EvidenceMode,
    FindingSeverity,
    GovernanceStatus,
    ReportFinding,
    ReportType,
    default_package_version_label,
)
from mip.examples.stage_a_fixtures import (
    load_stage_a_fixture,
)
from mip.workflows.intake.advisory import (
    build_cold_start_advisory_plan,
    build_cold_start_business_profile,
)
from mip.workflows.intake.calibration_mapping import map_evidence_to_calibration_signal

_ADVISORY_FIXTURE_IDS = frozenset(
    {
        "local_fitness_studio",
        "dtc_skincare_brand",
        "b2b_saas_hr_platform",
    }
)

_ADVISORY_WORKFLOW = "build_cold_start_advisory_plan"

_ADVISORY_REQUIRED_FIXTURE_FIELDS = (
    "domain",
    "objective",
    "geography",
    "monthly_budget_usd",
)

_ADVISORY_ALLOWED_DOWNSTREAM = (
    "explain_advisory_recommendation",
    "identify_missing_data",
    "suggest_safe_next_measurement_step",
    "advisory_hypothesis",
    "tracking_setup",
    "learning_agenda",
)

_ADVISORY_FORBIDDEN_DOWNSTREAM = (
    "decision_recommendation",
    "budget_optimization",
    "geox_design_approval",
    "mmm_model_output",
    "roi_proof",
    "mmm_calibration_executed",
    "causal_certification",
    "causal_effect_authorization",
    "treatment_unit_assignment",
)

_ADVISORY_BLOCKED_CLAIMS = (
    "causal_lift",
    "roi_proof",
    "budget_optimization",
    "geox_design_approval",
    "mmm_model_output",
    "treatment_assignment",
    "decision_authorization",
    "mmm_calibration_executed",
)

_DOMAIN_TO_BUSINESS_TYPE: dict[str, str] = {
    "local_service": "local service",
    "ecommerce": "ecommerce retail",
    "b2b_saas": "b2b saas",
}

_OBJECTIVE_TO_ENUM: dict[str, ColdStartMediaObjective] = {
    "sales": ColdStartMediaObjective.SALES,
    "lead_generation": ColdStartMediaObjective.LEAD_GENERATION,
    "awareness": ColdStartMediaObjective.AWARENESS,
    "traffic": ColdStartMediaObjective.TRAFFIC,
    "app_installs": ColdStartMediaObjective.APP_INSTALLS,
    "store_visits": ColdStartMediaObjective.STORE_VISITS,
    "retention": ColdStartMediaObjective.RETENTION,
    "repeat_purchase": ColdStartMediaObjective.REPEAT_PURCHASE,
    "market_launch": ColdStartMediaObjective.MARKET_LAUNCH,
    "product_launch": ColdStartMediaObjective.PRODUCT_LAUNCH,
}

_BUSINESS_MODEL_TO_B2B_OR_B2C: dict[str, str] = {
    "b2c_dtc": "b2c",
    "b2c_subscription": "b2c",
    "b2b_subscription": "b2b",
}

_TRACKING_STATE_TO_WEBSITE_AND_TRACKING: dict[str, tuple[bool, bool]] = {
    "website_without_full_paid_tracking": (True, False),
    "website_only_partial_utm": (True, False),
    "crm_and_utm_partial": (True, False),
    "no_website": (False, False),
}

_FIXTURE_PROFILE_DEFAULTS: dict[str, dict[str, str]] = {
    "local_fitness_studio": {
        "business_type": "local service",
        "product_or_service": "local fitness studio memberships",
        "target_audience": "Adults within 10 miles of studio",
        "b2b_or_b2c": "b2c",
    },
    "dtc_skincare_brand": {
        "business_type": "ecommerce retail",
        "product_or_service": "DTC handmade skincare ecommerce",
        "target_audience": "Women 25-45 interested in clean beauty",
        "b2b_or_b2c": "b2c",
    },
    "b2b_saas_hr_platform": {
        "business_type": "b2b saas",
        "product_or_service": "B2B HR platform subscription",
        "target_audience": "HR leaders at mid-market companies",
        "b2b_or_b2c": "b2b",
    },
}

_CALIBRATION_FIXTURE_IDS = frozenset(
    {
        "experiment_readout_valid",
        "experiment_readout_missing_se",
        "experiment_readout_metric_mismatch",
    }
)

_CALIBRATION_WORKFLOW = "map_evidence_to_calibration_signal"

_DEFAULT_FORBIDDEN_DOWNSTREAM = (
    "decision_recommendation",
    "budget_optimization",
    "mmm_calibration_executed",
    "causal_certification",
    "roi_proof",
)

_DEFAULT_BLOCKED_CLAIMS = (
    "causal_lift",
    "roi_proof",
    "budget_optimization",
    "mmm_calibration_executed",
    "decision_authorization",
)

_STATUS_TO_GOVERNANCE: dict[str, GovernanceStatus] = {
    CalibrationIntakeStatus.MAPPED.value: GovernanceStatus.CANDIDATE,
    CalibrationIntakeStatus.NEEDS_MORE_DATA.value: GovernanceStatus.NEEDS_MORE_DATA,
    CalibrationIntakeStatus.INCOMPATIBLE.value: GovernanceStatus.INCOMPATIBLE,
    CalibrationIntakeStatus.BLOCKED.value: GovernanceStatus.BLOCKED,
    CalibrationIntakeStatus.READY_FOR_MAPPING.value: GovernanceStatus.DIAGNOSTIC_ONLY,
    CalibrationIntakeStatus.DRAFT.value: GovernanceStatus.DIAGNOSTIC_ONLY,
}


class StageAAdapterError(Exception):
    """Raised when a Stage A fixture cannot be adapted to a workflow input."""


def list_supported_calibration_fixture_ids() -> list[str]:
    """Return calibration fixture IDs supported by Stage A.3 adapters."""
    return sorted(_CALIBRATION_FIXTURE_IDS)


def list_supported_advisory_fixture_ids() -> list[str]:
    """Return business-profile fixture IDs supported by Stage A.3 advisory adapters."""
    return sorted(_ADVISORY_FIXTURE_IDS)


def _assert_calibration_fixture_id(fixture_id: str) -> None:
    if fixture_id not in _CALIBRATION_FIXTURE_IDS:
        msg = (
            f"fixture_id {fixture_id!r} is not a supported calibration fixture; "
            f"supported: {sorted(_CALIBRATION_FIXTURE_IDS)}"
        )
        raise StageAAdapterError(msg)


def build_calibration_input_from_stage_a_fixture(fixture_id: str) -> dict[str, Any]:
    """Load a Stage A calibration fixture and return evidence/requirement payloads."""
    _assert_calibration_fixture_id(fixture_id)
    payload = load_stage_a_fixture(fixture_id)
    if payload.get("workflow_area") != "calibration_mapping":
        msg = f"fixture {fixture_id!r} is not a calibration_mapping fixture"
        raise StageAAdapterError(msg)
    evidence = payload.get("evidence")
    requirement = payload.get("requirement")
    if not isinstance(evidence, dict) or not isinstance(requirement, dict):
        msg = f"fixture {fixture_id!r} is missing evidence/requirement objects"
        raise StageAAdapterError(msg)
    return {
        "fixture_id": fixture_id,
        "synthetic": payload.get("synthetic") is True,
        "workflow_area": payload.get("workflow_area"),
        "demo_journey": payload.get("demo_journey"),
        "evidence_level": payload.get("evidence_level"),
        "expected_status": payload.get("expected_status"),
        "requires_mmm_or_geox_engine": payload.get("requires_mmm_or_geox_engine") is False,
        "evidence": evidence,
        "requirement": requirement,
    }


def _fixture_artifact_reference(
    fixture_id: str,
    *,
    created_at: datetime,
    governance_status: GovernanceStatus,
) -> ArtifactReference:
    return ArtifactReference(
        artifact_id=f"stage-a-fixture:{fixture_id}",
        artifact_type="stage_a_fixture",
        source_workflow="mip.examples.stage_a_fixtures.load_stage_a_fixture",
        source_fixture_id_or_payload_ref=fixture_id,
        source_commit_or_version=default_package_version_label(),
        created_at=created_at,
        governance_status=governance_status,
        evidence_mode=EvidenceMode.DIAGNOSTIC_CANDIDATE,
        allowed_downstream_uses=["diagnostic_review", "calibration_mapping_candidate"],
        forbidden_downstream_uses=list(_DEFAULT_FORBIDDEN_DOWNSTREAM),
    )


def _governance_status_for_mapping(status: str) -> GovernanceStatus:
    return _STATUS_TO_GOVERNANCE.get(status, GovernanceStatus.UNSUPPORTED)


def _summary_for_mapping_report(
    fixture_id: str,
    mapping_report: CalibrationMappingReport,
) -> str:
    status = str(mapping_report.status)
    if status == CalibrationIntakeStatus.MAPPED.value:
        return (
            f"Stage A calibration fixture {fixture_id} mapped structurally to a "
            "diagnostic calibration candidate. MMM calibration execution remains deferred."
        )
    if status == CalibrationIntakeStatus.NEEDS_MORE_DATA.value:
        return (
            f"Stage A calibration fixture {fixture_id} requires additional governed "
            "fields before calibration mapping can proceed."
        )
    if status == CalibrationIntakeStatus.INCOMPATIBLE.value:
        return (
            f"Stage A calibration fixture {fixture_id} is incompatible with the "
            "stated calibration requirement."
        )
    return f"Stage A calibration fixture {fixture_id} produced status {status}."


def _findings_from_mapping_report(
    mapping_report: CalibrationMappingReport,
) -> list[ReportFinding]:
    findings: list[ReportFinding] = []
    for index, reason in enumerate(mapping_report.blocking_reasons):
        findings.append(
            ReportFinding(
                finding_id=f"blocking-{index}",
                severity=FindingSeverity.BLOCKING,
                message=reason,
            )
        )
    for index, field_name in enumerate(mapping_report.missing_fields):
        findings.append(
            ReportFinding(
                finding_id=f"missing-{index}",
                severity=FindingSeverity.BLOCKING,
                message=f"Missing field: {field_name}",
                field_ref=field_name,
            )
        )
    for index, field_name in enumerate(mapping_report.incompatible_fields):
        findings.append(
            ReportFinding(
                finding_id=f"incompatible-{index}",
                severity=FindingSeverity.BLOCKING,
                message=f"Incompatible field: {field_name}",
                field_ref=field_name,
            )
        )
    for index, warning in enumerate(mapping_report.warnings):
        findings.append(
            ReportFinding(
                finding_id=f"warning-{index}",
                severity=FindingSeverity.WARNING,
                message=warning,
            )
        )
    return findings


def build_calibration_report_envelope(
    fixture_id: str,
    mapping_report: CalibrationMappingReport,
    *,
    generated_at: datetime | None = None,
    report_id: str | None = None,
) -> DeterministicReportEnvelope:
    """Build a deterministic report envelope from a calibration mapping report."""
    _assert_calibration_fixture_id(fixture_id)
    governance_status = _governance_status_for_mapping(str(mapping_report.status))
    created_at = generated_at or mapping_report.created_at
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=UTC)

    source_ref = _fixture_artifact_reference(
        fixture_id,
        created_at=created_at,
        governance_status=governance_status,
    )
    workflow_payload: dict[str, Any] = {
        "calibration_mapping_report": mapping_report.model_dump(mode="json"),
    }
    if mapping_report.mapped_signal is not None:
        workflow_payload["calibration_signal"] = mapping_report.mapped_signal.model_dump(
            mode="json"
        )

    return DeterministicReportEnvelope(
        report_id=report_id or f"det-report-cal-{fixture_id}",
        report_type=ReportType.CALIBRATION_MAPPING,
        schema_version=DETERMINISTIC_REPORT_SCHEMA_VERSION,
        source_workflow=_CALIBRATION_WORKFLOW,
        source_input_ref=source_ref,
        generated_at=created_at,
        evidence_mode=EvidenceMode.DIAGNOSTIC_CANDIDATE,
        governance_status=governance_status,
        summary=_summary_for_mapping_report(fixture_id, mapping_report),
        findings=_findings_from_mapping_report(mapping_report),
        recommended_next_steps=list(mapping_report.allowed_next_steps),
        missing_data=list(mapping_report.missing_fields),
        blocked_claims=list(_DEFAULT_BLOCKED_CLAIMS),
        allowed_downstream_uses=["diagnostic_review", "education"],
        forbidden_downstream_uses=list(
            dict.fromkeys(
                [
                    *mapping_report.blocked_next_steps,
                    *_DEFAULT_FORBIDDEN_DOWNSTREAM,
                ]
            )
        ),
        artifact_refs=[source_ref],
        workflow_payload=workflow_payload,
    )


def run_calibration_mapping_for_stage_a_fixture(
    fixture_id: str,
    *,
    generated_at: datetime | None = None,
    report_id: str | None = None,
) -> DeterministicReportEnvelope:
    """Adapt a Stage A calibration fixture, run mapping, and return a report envelope."""
    adapter_input = build_calibration_input_from_stage_a_fixture(fixture_id)
    evidence = CalibrationEvidenceInput(**adapter_input["evidence"])
    requirement = CalibrationMappingRequirement(**adapter_input["requirement"])
    _signal, mapping_report = map_evidence_to_calibration_signal(evidence, requirement)
    return build_calibration_report_envelope(
        fixture_id,
        mapping_report,
        generated_at=generated_at,
        report_id=report_id,
    )


def _assert_advisory_fixture_id(fixture_id: str) -> None:
    if fixture_id not in _ADVISORY_FIXTURE_IDS:
        msg = (
            f"fixture_id {fixture_id!r} is not a supported advisory fixture; "
            f"supported: {sorted(_ADVISORY_FIXTURE_IDS)}"
        )
        raise StageAAdapterError(msg)


def _map_objective(objective: str) -> ColdStartMediaObjective:
    normalized = objective.strip().lower().replace("-", "_")
    return _OBJECTIVE_TO_ENUM.get(normalized, ColdStartMediaObjective.UNKNOWN)


def _map_tracking_state(tracking_state: str | None) -> tuple[bool | None, bool | None]:
    if tracking_state is None:
        return None, None
    mapped = _TRACKING_STATE_TO_WEBSITE_AND_TRACKING.get(tracking_state.strip())
    if mapped is None:
        return None, None
    return mapped


def _business_profile_from_fixture_payload(
    fixture_id: str,
    payload: dict[str, Any],
    *,
    created_at: datetime | None = None,
) -> ColdStartBusinessProfile:
    defaults = _FIXTURE_PROFILE_DEFAULTS.get(fixture_id, {})
    domain = str(payload["domain"])
    business_type = defaults.get("business_type") or _DOMAIN_TO_BUSINESS_TYPE.get(
        domain,
        domain.replace("_", " "),
    )
    business_model = payload.get("business_model")
    b2b_or_b2c = defaults.get("b2b_or_b2c")
    if isinstance(business_model, str):
        b2b_or_b2c = _BUSINESS_MODEL_TO_B2B_OR_B2C.get(business_model, b2b_or_b2c)

    monthly_budget_usd = payload["monthly_budget_usd"]
    if not isinstance(monthly_budget_usd, int | float):
        msg = f"fixture {fixture_id!r} monthly_budget_usd must be numeric"
        raise StageAAdapterError(msg)

    existing_website, existing_tracking = _map_tracking_state(
        payload.get("tracking_state") if isinstance(payload.get("tracking_state"), str) else None
    )
    constraints = payload.get("known_constraints")
    constraint_list = list(constraints) if isinstance(constraints, list) else []
    channels = payload.get("current_channels")
    organic_channels = [str(channel) for channel in channels] if isinstance(channels, list) else []

    return build_cold_start_business_profile(
        profile_id=f"stage-a-{fixture_id}",
        created_at=created_at,
        business_type=business_type,
        product_or_service=defaults.get("product_or_service"),
        b2b_or_b2c=b2b_or_b2c,
        target_audience=defaults.get("target_audience"),
        monthly_budget=f"${int(monthly_budget_usd)}",
        primary_objective=_map_objective(str(payload["objective"])),
        geography=str(payload["geography"]),
        existing_website=existing_website,
        existing_tracking=existing_tracking,
        organic_channels_available=organic_channels,
        constraints=constraint_list,
    )


def build_cold_start_input_from_stage_a_fixture(fixture_id: str) -> dict[str, Any]:
    """Load a Stage A business-profile fixture and return advisory workflow input metadata."""
    _assert_advisory_fixture_id(fixture_id)
    payload = load_stage_a_fixture(fixture_id)
    if payload.get("workflow_area") != "cold_start_advisory":
        msg = f"fixture {fixture_id!r} is not a cold_start_advisory fixture"
        raise StageAAdapterError(msg)
    for field_name in _ADVISORY_REQUIRED_FIXTURE_FIELDS:
        if field_name not in payload:
            msg = f"fixture {fixture_id!r} is missing required field {field_name!r}"
            raise StageAAdapterError(msg)

    profile = _business_profile_from_fixture_payload(fixture_id, payload)
    return {
        "fixture_id": fixture_id,
        "synthetic": payload.get("synthetic") is True,
        "workflow_area": payload.get("workflow_area"),
        "demo_journey": payload.get("demo_journey"),
        "evidence_mode": payload.get("evidence_mode"),
        "requires_mmm_or_geox_engine": payload.get("requires_mmm_or_geox_engine") is False,
        "business_profile": profile,
    }


def _advisory_fixture_artifact_reference(
    fixture_id: str,
    *,
    created_at: datetime,
) -> ArtifactReference:
    return ArtifactReference(
        artifact_id=f"stage-a-fixture:{fixture_id}",
        artifact_type="stage_a_fixture",
        source_workflow="mip.examples.stage_a_fixtures.load_stage_a_fixture",
        source_fixture_id_or_payload_ref=fixture_id,
        source_commit_or_version=default_package_version_label(),
        created_at=created_at,
        governance_status=GovernanceStatus.ADVISORY_ONLY,
        evidence_mode=EvidenceMode.BUSINESS_PROFILE_ONLY,
        allowed_downstream_uses=list(_ADVISORY_ALLOWED_DOWNSTREAM),
        forbidden_downstream_uses=list(_ADVISORY_FORBIDDEN_DOWNSTREAM),
    )


def _summary_for_advisory_plan(fixture_id: str, status: str) -> str:
    return (
        f"Stage A advisory fixture {fixture_id} produced a cold-start advisory plan "
        f"with status {status}. Guidance is advisory-only and not causal measurement."
    )


def _findings_from_advisory_plan(plan: ColdStartAdvisoryPlan) -> list[ReportFinding]:
    findings: list[ReportFinding] = []
    for index, reason in enumerate(plan.blocking_reasons):
        findings.append(
            ReportFinding(
                finding_id=f"blocking-{index}",
                severity=FindingSeverity.BLOCKING,
                message=reason,
            )
        )
    for index, warning in enumerate(plan.warnings):
        findings.append(
            ReportFinding(
                finding_id=f"warning-{index}",
                severity=FindingSeverity.WARNING,
                message=warning,
            )
        )
    suitability = plan.channel_suitability
    if suitability is not None:
        for index, question in enumerate(suitability.clarification_questions):
            findings.append(
                ReportFinding(
                    finding_id=f"clarify-{index}",
                    severity=FindingSeverity.INFO,
                    message=question,
                )
            )
    return findings


def _missing_data_from_advisory_plan(plan: ColdStartAdvisoryPlan) -> list[str]:
    missing: list[str] = []
    if plan.tracking_checklist is not None:
        missing.extend(plan.tracking_checklist.missing_items)
    suitability = plan.channel_suitability
    if suitability is not None:
        missing.extend(suitability.clarification_questions)
    return list(dict.fromkeys(item for item in missing if item.strip()))


def build_cold_start_advisory_report_envelope(
    fixture_id: str,
    plan: ColdStartAdvisoryPlan,
    *,
    generated_at: datetime | None = None,
    report_id: str | None = None,
) -> DeterministicReportEnvelope:
    """Build a deterministic report envelope from a cold-start advisory plan."""
    _assert_advisory_fixture_id(fixture_id)
    created_at = generated_at or plan.created_at
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=UTC)

    source_ref = _advisory_fixture_artifact_reference(fixture_id, created_at=created_at)
    workflow_payload: dict[str, Any] = {
        "cold_start_advisory_plan": plan.model_dump(mode="json"),
    }

    return DeterministicReportEnvelope(
        report_id=report_id or f"det-report-adv-{fixture_id}",
        report_type=ReportType.COLD_START_ADVISORY,
        schema_version=DETERMINISTIC_REPORT_SCHEMA_VERSION,
        source_workflow=_ADVISORY_WORKFLOW,
        source_input_ref=source_ref,
        generated_at=created_at,
        evidence_mode=EvidenceMode.BUSINESS_PROFILE_ONLY,
        governance_status=GovernanceStatus.ADVISORY_ONLY,
        summary=_summary_for_advisory_plan(fixture_id, str(plan.status)),
        findings=_findings_from_advisory_plan(plan),
        recommended_next_steps=list(plan.allowed_next_steps),
        missing_data=_missing_data_from_advisory_plan(plan),
        blocked_claims=list(_ADVISORY_BLOCKED_CLAIMS),
        allowed_downstream_uses=list(_ADVISORY_ALLOWED_DOWNSTREAM),
        forbidden_downstream_uses=list(
            dict.fromkeys([*plan.blocked_next_steps, *_ADVISORY_FORBIDDEN_DOWNSTREAM])
        ),
        artifact_refs=[source_ref],
        workflow_payload=workflow_payload,
    )


def run_cold_start_advisory_for_stage_a_fixture(
    fixture_id: str,
    *,
    generated_at: datetime | None = None,
    report_id: str | None = None,
) -> DeterministicReportEnvelope:
    """Adapt a Stage A business-profile fixture, run advisory workflow, return envelope."""
    adapter_input = build_cold_start_input_from_stage_a_fixture(fixture_id)
    profile = adapter_input["business_profile"]
    if not isinstance(profile, ColdStartBusinessProfile):
        msg = f"fixture {fixture_id!r} did not produce a ColdStartBusinessProfile"
        raise StageAAdapterError(msg)
    if generated_at is not None:
        profile = profile.model_copy(update={"created_at": generated_at})
    plan = build_cold_start_advisory_plan(profile)
    if generated_at is not None:
        plan = plan.model_copy(update={"created_at": generated_at})
    return build_cold_start_advisory_report_envelope(
        fixture_id,
        plan,
        generated_at=generated_at,
        report_id=report_id,
    )
