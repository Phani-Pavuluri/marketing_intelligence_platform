"""Deterministic, metadata-only capability registry."""
# ruff: noqa: E501, UP035, F401
from __future__ import annotations

import hashlib
import json
import re
from types import MappingProxyType
from typing import Iterable

from pydantic import Field

from mip.contracts.base import ContractBaseModel
from mip.contracts.conversation import (
    CapabilityDescriptor,
    CapabilityStatus,
    EventType,
    ExecutionMode,
)

CAPABILITY_REGISTRY_VERSION = "capability_registry_v1"
_ID_PATTERN = re.compile(r"^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$")
_EXTERNAL_PREFIX = "external:"


class UnknownCapabilityError(LookupError):
    """Raised instead of silently returning no capability."""


class RegistryValidationIssue(ContractBaseModel):
    """A fail-closed registry validation finding."""

    code: str
    capability_id: str | None = None
    message: str


def _descriptor(
    capability_id: str,
    *,
    domain: str,
    status: CapabilityStatus,
    intents: Iterable[str],
    events: Iterable[EventType],
    required_inputs: Iterable[str] = (),
    conditional_inputs: Iterable[str] = (),
    required_artifacts: Iterable[str] = (),
    produced_artifacts: Iterable[str] = (),
    allowed_claims: Iterable[str] = (),
    blocked_claims: Iterable[str] = (),
    modes: Iterable[ExecutionMode] = (ExecutionMode.FIXTURE,),
    next_capabilities: Iterable[str] = (),
    workflow_nodes: Iterable[str] = (),
    release_gate: str | None = None,
    owner: str = "mip.control_plane",
) -> CapabilityDescriptor:
    return CapabilityDescriptor(
        capability_id=capability_id,
        capability_version="1",
        owner=owner,
        domain=domain,
        status=status,
        supported_intents=list(intents),
        supported_event_types=list(events),
        required_inputs=list(required_inputs),
        conditional_inputs=list(conditional_inputs),
        required_artifact_types=list(required_artifacts),
        produced_artifact_types=list(produced_artifacts),
        allowed_claims=list(allowed_claims),
        blocked_claims=list(blocked_claims),
        execution_modes=list(modes),
        next_capability_ids=list(next_capabilities),
        workflow_node_ids=list(workflow_nodes),
        documentation_retrieval_filters={
            "domain": domain,
            "capability_id": capability_id,
            "status": status.value,
            "version": "1",
        },
        release_gate=release_gate,
    )


_ALL_EVENTS = tuple(EventType)
_CHAT_EVENTS = (EventType.USER_MESSAGE, EventType.STARTER_PROMPT_SELECTED)
_UPLOAD_EVENTS = (
    EventType.FILE_UPLOADED,
    EventType.COLUMN_MAPPING_CONFIRMED,
    EventType.ANALYZE_MY_DATA_SELECTED,
)
_MMM_INPUTS = ("business_goal", "primary_kpi", "date", "time_frequency", "channel", "spend", "history_start", "history_end")
_MMM_CONDITIONAL = ("geography", "segment", "controls", "promotions", "calendar", "pricing_changes", "experiment_evidence", "planning_horizon")
_MMM_NODES = ("build_validate_mmm", "understand_channel_results")
_PLANNING_NODES = ("plan_next_quarter",)
_GEOX_NODES = ("design_geox", "review_geox_evidence")


def _build_catalog() -> tuple[CapabilityDescriptor, ...]:
    """Build the one canonical catalog; this function has no execution side effects."""
    fixture = CapabilityStatus.FIXTURE_BACKED
    readiness = CapabilityStatus.READINESS_ONLY
    blocked = CapabilityStatus.BLOCKED
    available = CapabilityStatus.AVAILABLE
    return (
        _descriptor("platform.onboarding", domain="platform", status=available, intents=("platform.onboarding",), events=_CHAT_EVENTS, allowed_claims=("onboarding guidance", "next action"), blocked_claims=("engine execution",), modes=(ExecutionMode.FIXTURE,), workflow_nodes=("define_decision",), release_gate="phase_a_contracts"),
        _descriptor("data.requirements.explain", domain="data", status=available, intents=("data.requirements.explain",), events=_CHAT_EVENTS, allowed_claims=("required fields", "missing inputs", "next action"), blocked_claims=("ROI", "causal lift", "budget recommendation"), modes=(ExecutionMode.FIXTURE,)),
        _descriptor("sample.use_case.activate", domain="sample", status=fixture, intents=("sample.use_case.activate",), events=(EventType.SAMPLE_USE_CASE_SELECTED,), produced_artifacts=("sample_use_case",), allowed_claims=("sample activation",), blocked_claims=("production evidence",), modes=(ExecutionMode.FIXTURE,), next_capabilities=("mmm.intake.requirements",)),
        _descriptor("uploaded_data.intake", domain="uploaded_data", status=readiness, intents=("uploaded_data.intake",), events=_UPLOAD_EVENTS, required_inputs=("file",), produced_artifacts=("uploaded_session",), allowed_claims=("file inventory", "privacy disclosure"), blocked_claims=("model fit", "ROI"), modes=(ExecutionMode.UPLOADED_SESSION,)),
        _descriptor("uploaded_data.profile", domain="uploaded_data", status=readiness, intents=("uploaded_data.profile",), events=(EventType.FILE_UPLOADED,), required_inputs=("uploaded_session",), produced_artifacts=("profile_report",), allowed_claims=("detected fields", "structural profile"), blocked_claims=("production readiness",), modes=(ExecutionMode.UPLOADED_SESSION,)),
        _descriptor("uploaded_data.map_columns", domain="uploaded_data", status=readiness, intents=("uploaded_data.map_columns",), events=(EventType.COLUMN_MAPPING_CONFIRMED,), required_inputs=("profile_report",), produced_artifacts=("column_mapping",), allowed_claims=("confirmed mapping",), blocked_claims=("causal interpretation",), modes=(ExecutionMode.UPLOADED_SESSION,)),
        _descriptor("uploaded_data.assess_compatibility", domain="uploaded_data", status=readiness, intents=("uploaded_data.assess_compatibility",), events=(EventType.COLUMN_MAPPING_CONFIRMED,), required_inputs=("column_mapping",), conditional_inputs=("geography", "controls"), produced_artifacts=("readiness_report",), allowed_claims=("grain compatibility", "structural readiness", "next action"), blocked_claims=("ROI", "live fitting"), modes=(ExecutionMode.UPLOADED_SESSION,)),
        _descriptor("mmm.intake.requirements", domain="mmm", status=available, intents=("mmm.intake.requirements",), events=_CHAT_EVENTS, required_inputs=_MMM_INPUTS, conditional_inputs=_MMM_CONDITIONAL, allowed_claims=("required fields", "missing inputs", "clarification"), blocked_claims=("ROI", "contribution", "budget recommendation"), modes=(ExecutionMode.FIXTURE,), workflow_nodes=("bring_data", "inspect_validate", "build_validate_mmm")),
        _descriptor("mmm.intake.readiness", domain="mmm", status=readiness, intents=("mmm.intake.readiness",), events=(EventType.BUSINESS_GOAL_CONFIRMED, EventType.COLUMN_MAPPING_CONFIRMED), required_inputs=_MMM_INPUTS, conditional_inputs=_MMM_CONDITIONAL, required_artifacts=("readiness_report",), allowed_claims=("structural readiness", "missing inputs"), blocked_claims=("model fit", "ROI"), modes=(ExecutionMode.UPLOADED_SESSION,), workflow_nodes=("inspect_validate",)),
        _descriptor("mmm.run.request", domain="mmm", status=blocked, intents=("mmm.run.request",), events=(EventType.CAPABILITY_EXECUTION_REQUESTED,), required_inputs=_MMM_INPUTS, required_artifacts=("readiness_report",), allowed_claims=("execution request blocked"), blocked_claims=("live fitting", "ROI"), modes=(ExecutionMode.FUTURE_ENGINE,), workflow_nodes=("build_validate_mmm",), release_gate="future_engine_release"),
        _descriptor("mmm.result.explain", domain="mmm", status=fixture, intents=("mmm.result.explain",), events=_CHAT_EVENTS, required_artifacts=("mmm_result_fixture",), produced_artifacts=("explanation",), allowed_claims=("sample result explanation", "sample uncertainty", "sample diagnostics"), blocked_claims=("production evidence", "budget movement", "optimization"), modes=(ExecutionMode.FIXTURE,), workflow_nodes=("understand_channel_results",)),
        _descriptor("mmm.channel_uncertainty.explain", domain="mmm", status=fixture, intents=("mmm.channel_uncertainty.explain",), events=_CHAT_EVENTS, required_artifacts=("mmm_result_fixture",), allowed_claims=("sample uncertainty explanation",), blocked_claims=("production certainty",), modes=(ExecutionMode.FIXTURE,), workflow_nodes=("understand_channel_results", "identify_evidence_gap")),
        _descriptor("planning.readiness", domain="planning", status=readiness, intents=("planning.readiness",), events=_CHAT_EVENTS, required_artifacts=("mmm_result",), allowed_claims=("planning prerequisites", "blocked reason"), blocked_claims=("optimized spend", "recommendation"), modes=(ExecutionMode.FIXTURE,), workflow_nodes=_PLANNING_NODES),
        _descriptor("planning.simulation.request", domain="planning", status=blocked, intents=("planning.simulation.request",), events=(EventType.CAPABILITY_EXECUTION_REQUESTED,), required_artifacts=("valid_mmm_result", "DecisionSurface", "baseline_plan", "trust_evidence"), allowed_claims=("simulation request blocked",), blocked_claims=("optimized spend", "expected incremental KPI"), modes=(ExecutionMode.FUTURE_ENGINE,), workflow_nodes=_PLANNING_NODES, release_gate="simulation_release"),
        _descriptor("planning.recommendation.explain_blocked", domain="planning", status=available, intents=("planning.recommendation.explain_blocked",), events=_CHAT_EVENTS, allowed_claims=("blocked recommendation explanation", "planning prerequisites"), blocked_claims=("budget recommendation", "budget movement"), modes=(ExecutionMode.FIXTURE,), workflow_nodes=_PLANNING_NODES),
        _descriptor("geox.intake.requirements", domain="geox", status=available, intents=("geox.intake.requirements",), events=_CHAT_EVENTS, required_inputs=("experiment_question", "primary_kpi", "candidate_channel", "treatment_unit", "candidate_markets", "pre_period", "proposed_test_window", "spend_intervention"), conditional_inputs=("excluded_markets", "assignment_constraints", "precision_or_mde_goal", "earliest_start_date", "latest_end_date"), allowed_claims=("required inputs", "feasibility ownership"), blocked_claims=("market assignment", "predicted lift"), modes=(ExecutionMode.FIXTURE,), workflow_nodes=_GEOX_NODES),
        _descriptor("geox.design_request.create", domain="geox", status=fixture, intents=("geox.design_request.create",), events=(EventType.WORKFLOW_ACTION_SELECTED,), required_inputs=("experiment_question", "primary_kpi", "candidate_channel"), produced_artifacts=("geox_design_request",), allowed_claims=("governed request artifact", "required inputs"), blocked_claims=("automatic assignment", "guaranteed feasibility"), modes=(ExecutionMode.FIXTURE,), workflow_nodes=("design_geox",)),
        _descriptor("geox.feasibility.explain", domain="geox", status=fixture, intents=("geox.feasibility.explain",), events=_CHAT_EVENTS, required_artifacts=("geox_design_request",), allowed_claims=("feasibility explanation", "ownership"), blocked_claims=("guaranteed feasibility", "predicted lift"), modes=(ExecutionMode.FIXTURE,), workflow_nodes=_GEOX_NODES),
        _descriptor("geox.readout.explain", domain="geox", status=fixture, intents=("geox.readout.explain",), events=_CHAT_EVENTS, required_artifacts=("geox_readout_fixture",), allowed_claims=("fixture readout explanation",), blocked_claims=("production readout", "causal guarantee"), modes=(ExecutionMode.FIXTURE,), workflow_nodes=("review_geox_evidence",)),
        _descriptor("calibration.compatibility.validate", domain="calibration", status=readiness, intents=("calibration.compatibility.validate",), events=(EventType.CAPABILITY_EXECUTION_REQUESTED,), required_artifacts=("CalibrationSignal",), allowed_claims=("compatibility status",), blocked_claims=("calibration execution",), modes=(ExecutionMode.UPLOADED_SESSION,)),
        _descriptor("calibration.signal.explain", domain="calibration", status=fixture, intents=("calibration.signal.explain",), events=_CHAT_EVENTS, required_artifacts=("CalibrationSignal",), allowed_claims=("signal explanation",), blocked_claims=("causal guarantee",), modes=(ExecutionMode.FIXTURE,)),
        _descriptor("mmm.refresh.compare", domain="mmm", status=blocked, intents=("mmm.refresh.compare",), events=(EventType.CAPABILITY_EXECUTION_REQUESTED,), required_artifacts=("mmm_result",), allowed_claims=("refresh comparison blocked"), blocked_claims=("live refresh", "budget movement"), modes=(ExecutionMode.FUTURE_ENGINE,), release_gate="refresh_release"),
        _descriptor("decision_package.build", domain="decision_package", status=blocked, intents=("decision_package.build",), events=(EventType.CAPABILITY_EXECUTION_REQUESTED,), required_artifacts=("validated_evidence",), produced_artifacts=("decision_package",), allowed_claims=("package request blocked"), blocked_claims=("recommendation authorization",), modes=(ExecutionMode.FUTURE_ENGINE,), workflow_nodes=("decision_package",), release_gate="decision_package_release"),
        _descriptor("artifact.open", domain="artifact", status=available, intents=("artifact.open",), events=(EventType.ARTIFACT_OPENED,), required_inputs=("artifact_id",), allowed_claims=("artifact metadata",), blocked_claims=("unverified claims",), modes=(ExecutionMode.FIXTURE, ExecutionMode.UPLOADED_SESSION)),
        _descriptor("report.open", domain="report", status=available, intents=("report.open",), events=(EventType.REPORT_OPENED,), required_inputs=("report_id",), allowed_claims=("report navigation",), blocked_claims=("new claims",), modes=(ExecutionMode.FIXTURE,)),
        _descriptor("dashboard.context.update", domain="dashboard", status=available, intents=("dashboard.context.update",), events=(EventType.DASHBOARD_FILTER_CHANGED,), required_inputs=("active_view",), allowed_claims=("context update",), blocked_claims=("model execution",), modes=(ExecutionMode.FIXTURE, ExecutionMode.UPLOADED_SESSION)),
        _descriptor("knowledge.explain", domain="knowledge", status=CapabilityStatus.FUTURE_INTEGRATION, intents=("knowledge.explain",), events=_CHAT_EVENTS, allowed_claims=("general explanation",), blocked_claims=("user-data claims", "artifact numbers", "execution success", "recommendations"), modes=(ExecutionMode.FIXTURE,)),
        _descriptor("knowledge.compare", domain="knowledge", status=CapabilityStatus.FUTURE_INTEGRATION, intents=("knowledge.compare",), events=_CHAT_EVENTS, allowed_claims=("concept comparison",), blocked_claims=("user-data claims", "artifact numbers", "execution success", "recommendations"), modes=(ExecutionMode.FIXTURE,)),
        _descriptor("platform.guide", domain="platform", status=CapabilityStatus.FUTURE_INTEGRATION, intents=("platform.guide",), events=_CHAT_EVENTS, allowed_claims=("platform guidance",), blocked_claims=("current status without structured truth", "execution success", "recommendations"), modes=(ExecutionMode.FIXTURE,)),
        _descriptor("workflow.guide", domain="workflow", status=CapabilityStatus.FUTURE_INTEGRATION, intents=("workflow.guide",), events=_CHAT_EVENTS, allowed_claims=("workflow guidance",), blocked_claims=("workflow authorization", "execution success", "recommendations"), modes=(ExecutionMode.FIXTURE,)),
        _descriptor("artifact.explain", domain="artifact", status=CapabilityStatus.BLOCKED, intents=("artifact.explain",), events=_CHAT_EVENTS, required_artifacts=("resolved_artifact",), allowed_claims=("verified artifact explanation",), blocked_claims=("unprovenance numerical claims", "execution success", "recommendations"), modes=(ExecutionMode.FIXTURE,), release_gate="artifact_resolution_release"),
    )


class CapabilityRegistry:
    """Immutable metadata catalog with deterministic, side-effect-free discovery."""

    def __init__(self, descriptors: Iterable[CapabilityDescriptor], *, registry_version: str = CAPABILITY_REGISTRY_VERSION) -> None:
        self.registry_version = registry_version
        ordered = tuple(sorted((descriptor.model_copy(deep=True) for descriptor in descriptors), key=lambda item: item.capability_id))
        self._descriptors = ordered
        self._by_id = MappingProxyType({item.capability_id: item for item in ordered})
        issues = self.validate()
        if issues:
            raise ValueError("; ".join(issue.message for issue in issues))

    def get(self, capability_id: str) -> CapabilityDescriptor:
        try:
            return self._by_id[capability_id].model_copy(deep=True)
        except KeyError as exc:
            raise UnknownCapabilityError(f"Unknown capability: {capability_id}") from exc

    def list_all(self) -> tuple[CapabilityDescriptor, ...]:
        return tuple(item.model_copy(deep=True) for item in self._descriptors)

    def find(self, *, domain: str | None = None, status: CapabilityStatus | None = None, supported_intent: str | None = None, supported_event_type: EventType | None = None, execution_mode: ExecutionMode | None = None, workflow_node_id: str | None = None) -> tuple[CapabilityDescriptor, ...]:
        return tuple(item for item in self.list_all() if (domain is None or item.domain == domain) and (status is None or item.status == status) and (supported_intent is None or supported_intent in item.supported_intents) and (supported_event_type is None or supported_event_type in item.supported_event_types) and (execution_mode is None or execution_mode in item.execution_modes) and (workflow_node_id is None or workflow_node_id in item.workflow_node_ids))

    def validate(self) -> tuple[RegistryValidationIssue, ...]:
        issues: list[RegistryValidationIssue] = []
        if self.registry_version != CAPABILITY_REGISTRY_VERSION:
            issues.append(RegistryValidationIssue(code="registry_version", message="unsupported registry version"))
        ids = [item.capability_id for item in self._descriptors]
        if not ids:
            issues.append(RegistryValidationIssue(code="empty_registry", message="registry must not be empty"))
        if len(ids) != len(set(ids)):
            issues.append(RegistryValidationIssue(code="duplicate_id", message="capability IDs must be unique"))
        for item in self._descriptors:
            if not _ID_PATTERN.fullmatch(item.capability_id):
                issues.append(RegistryValidationIssue(code="invalid_id", capability_id=item.capability_id, message="invalid capability ID"))
            if set(item.allowed_claims) & set(item.blocked_claims):
                issues.append(RegistryValidationIssue(code="claim_overlap", capability_id=item.capability_id, message=f"{item.capability_id}: allowed and blocked claims overlap"))
            if set(item.required_inputs) & set(item.conditional_inputs):
                issues.append(RegistryValidationIssue(code="input_overlap", capability_id=item.capability_id, message="required and conditional inputs overlap"))
            if item.status in {CapabilityStatus.BLOCKED, CapabilityStatus.FUTURE_INTEGRATION} and ExecutionMode.EXTERNAL in item.execution_modes:
                issues.append(RegistryValidationIssue(code="blocked_execution", capability_id=item.capability_id, message="blocked/future capability cannot advertise external execution"))
            if item.capability_id == "planning.simulation.request" and item.status != CapabilityStatus.BLOCKED:
                issues.append(RegistryValidationIssue(code="planning_unblocked", capability_id=item.capability_id, message="planning simulation must remain blocked"))
            for target in item.next_capability_ids:
                if not target.startswith(_EXTERNAL_PREFIX) and target not in self._by_id:
                    issues.append(RegistryValidationIssue(code="unknown_next_capability", capability_id=item.capability_id, message=f"unknown next capability {target}"))
            for node_id in item.workflow_node_ids:
                if not _ID_PATTERN.fullmatch(node_id):
                    issues.append(RegistryValidationIssue(code="invalid_workflow_node", capability_id=item.capability_id, message="invalid workflow node ID"))
            required_filters = {"domain", "capability_id", "status", "version"}
            if not required_filters <= item.documentation_retrieval_filters.keys():
                issues.append(RegistryValidationIssue(code="retrieval_filter", capability_id=item.capability_id, message="retrieval filters lack identity metadata"))
        return tuple(issues)

    def fingerprint(self) -> str:
        payload = [item.model_dump(mode="json") for item in self._descriptors]
        canonical = json.dumps({"registry_version": self.registry_version, "capabilities": payload}, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode()).hexdigest()


DEFAULT_CAPABILITY_REGISTRY = CapabilityRegistry(_build_catalog())
