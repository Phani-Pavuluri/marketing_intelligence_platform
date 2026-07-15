"""Canonical governed measurement workflow graph and transition assessment."""
# ruff: noqa: E501
from __future__ import annotations

import hashlib
import json
import re
from enum import StrEnum
from types import MappingProxyType

from pydantic import Field

from mip.contracts.base import ContractBaseModel
from mip.contracts.conversation import (
    CapabilityDescriptor,
    CapabilityStatus,
    ExecutionMode,
    WorkflowNode,
    WorkspaceContext,
)
from mip.control_plane.capability_registry import (
    DEFAULT_CAPABILITY_REGISTRY,
    CapabilityRegistry,
    UnknownCapabilityError,
)

WORKFLOW_GRAPH_VERSION = "workflow_graph_v1"


class UnknownWorkflowNodeError(LookupError):
    """Raised for an unknown node instead of silently navigating."""


class TransitionStatus(StrEnum):
    ALLOWED = "allowed"
    ALLOWED_WITH_WARNING = "allowed_with_warning"
    BLOCKED_MISSING_INPUTS = "blocked_missing_inputs"
    BLOCKED_MISSING_ARTIFACTS = "blocked_missing_artifacts"
    BLOCKED_CAPABILITY_STATUS = "blocked_capability_status"
    BLOCKED_RELEASE_GATE = "blocked_release_gate"
    BLOCKED_INVALID_EDGE = "blocked_invalid_edge"
    BLOCKED_EXECUTION_BOUNDARY = "blocked_execution_boundary"


class WorkflowValidationIssue(ContractBaseModel):
    code: str
    node_id: str | None = None
    message: str


class TransitionAssessment(ContractBaseModel):
    from_node_id: str | None = None
    to_node_id: str
    status: TransitionStatus
    satisfied_prerequisites: list[str] = Field(default_factory=list)
    missing_inputs: list[str] = Field(default_factory=list)
    missing_artifact_types: list[str] = Field(default_factory=list)
    blocked_capabilities: list[str] = Field(default_factory=list)
    blocked_actions: list[str] = Field(default_factory=list)
    reason_codes: list[str] = Field(default_factory=list)
    next_allowed_node_ids: list[str] = Field(default_factory=list)
    required_user_actions: list[str] = Field(default_factory=list)


_NODE_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")
_FORWARD = (
    "define_decision", "bring_data", "inspect_validate", "build_validate_mmm",
    "understand_channel_results", "plan_next_quarter", "identify_evidence_gap",
    "design_geox", "review_geox_evidence", "refresh_mmm", "decision_package",
)
_NAMES = {
    "define_decision": "Define the decision",
    "bring_data": "Bring the data",
    "inspect_validate": "Inspect and validate",
    "build_validate_mmm": "Build and validate MMM",
    "understand_channel_results": "Understand channel results",
    "plan_next_quarter": "Plan next quarter",
    "identify_evidence_gap": "Identify an evidence gap",
    "design_geox": "Design GeoX",
    "review_geox_evidence": "Review GeoX evidence",
    "refresh_mmm": "Refresh MMM",
    "decision_package": "Produce the decision package",
}
_BINDINGS = {
    "define_decision": ("platform.onboarding", "data.requirements.explain", "planning.readiness"),
    "bring_data": ("sample.use_case.activate", "uploaded_data.intake", "mmm.intake.requirements", "geox.intake.requirements"),
    "inspect_validate": ("uploaded_data.profile", "uploaded_data.map_columns", "uploaded_data.assess_compatibility", "mmm.intake.readiness"),
    "build_validate_mmm": ("mmm.run.request", "mmm.intake.readiness"),
    "understand_channel_results": ("mmm.result.explain", "mmm.channel_uncertainty.explain"),
    "plan_next_quarter": ("planning.readiness", "planning.simulation.request", "planning.recommendation.explain_blocked"),
    "identify_evidence_gap": ("mmm.channel_uncertainty.explain", "planning.readiness", "geox.feasibility.explain"),
    "design_geox": ("geox.intake.requirements", "geox.design_request.create", "geox.feasibility.explain"),
    "review_geox_evidence": ("geox.readout.explain", "calibration.compatibility.validate", "calibration.signal.explain"),
    "refresh_mmm": ("calibration.compatibility.validate", "calibration.signal.explain", "mmm.refresh.compare"),
    "decision_package": ("decision_package.build", "artifact.open", "report.open"),
}
_REQUIRED_INPUTS = {
    "define_decision": ("business_goal", "primary_kpi"),
    "bring_data": (),
    "inspect_validate": ("file",),
    "build_validate_mmm": ("primary_kpi", "time_frequency", "history_start", "history_end"),
    "understand_channel_results": (),
    "plan_next_quarter": ("planning_horizon",),
    "identify_evidence_gap": (),
    "design_geox": ("experiment_question", "primary_kpi"),
    "review_geox_evidence": (),
    "refresh_mmm": (),
    "decision_package": (),
}
_ARTIFACTS = {
    "understand_channel_results": ("mmm_result_fixture",),
    "plan_next_quarter": ("mmm_result",),
    "review_geox_evidence": ("geox_readout_fixture",),
    "refresh_mmm": ("CalibrationSignal",),
    "decision_package": ("validated_evidence",),
}


def _node(node_id: str, registry: CapabilityRegistry) -> WorkflowNode:
    bindings = _BINDINGS[node_id]
    return WorkflowNode(
        node_id=node_id,
        display_name=_NAMES[node_id],
        business_purpose=f"Govern {node_id.replace('_', ' ')}.",
        supported_user_questions=[f"Questions about {node_id.replace('_', ' ')}"],
        required_capability_ids=list(bindings),
        required_inputs=list(_REQUIRED_INPUTS[node_id]),
        required_artifact_types=list(_ARTIFACTS.get(node_id, ())),
        available_actions=["view", "ask_chat"],
        blocked_actions=["execute", "skip_prerequisites"],
        display_artifact_types=list(_ARTIFACTS.get(node_id, ())),
        execution_mode=ExecutionMode.FIXTURE,
        next_valid_node_ids=[],
    )


class WorkflowGraph:
    """Immutable declarative graph; it assesses but never executes transitions."""

    def __init__(self, nodes: tuple[WorkflowNode, ...], edges: dict[str, tuple[str, ...]], *, graph_version: str = WORKFLOW_GRAPH_VERSION) -> None:
        self.graph_version = graph_version
        self._nodes = tuple(nodes)
        self._by_id = MappingProxyType({node.node_id: node for node in self._nodes})
        self._edges = MappingProxyType({key: tuple(value) for key, value in edges.items()})
        issues = self.validate()
        if issues:
            raise ValueError("; ".join(issue.message for issue in issues))

    def get_node(self, node_id: str) -> WorkflowNode:
        try:
            return self._by_id[node_id].model_copy(deep=True)
        except KeyError as exc:
            raise UnknownWorkflowNodeError(f"Unknown workflow node: {node_id}") from exc

    def list_nodes(self) -> tuple[WorkflowNode, ...]:
        return tuple(node.model_copy(deep=True) for node in self._nodes)

    def capabilities_for(self, node_id: str, registry: CapabilityRegistry = DEFAULT_CAPABILITY_REGISTRY) -> tuple[CapabilityDescriptor, ...]:
        return tuple(registry.get(capability_id) for capability_id in self.get_node(node_id).required_capability_ids)

    def next_nodes(self, node_id: str) -> tuple[WorkflowNode, ...]:
        self.get_node(node_id)
        return tuple(self.get_node(target) for target in self._edges[node_id])

    def node_ids_for_capability(self, capability_id: str, registry: CapabilityRegistry = DEFAULT_CAPABILITY_REGISTRY) -> tuple[str, ...]:
        registry.get(capability_id)
        return tuple(node.node_id for node in self._nodes if capability_id in node.required_capability_ids)

    def nodes_for_routing(self, capability_id: str, *, current_node_id: str | None = None, registry: CapabilityRegistry = DEFAULT_CAPABILITY_REGISTRY) -> tuple[WorkflowNode, ...]:
        candidates = self.node_ids_for_capability(capability_id, registry)
        preferred_defaults = {
            "mmm.intake.requirements": "bring_data",
            "mmm.intake.readiness": "inspect_validate",
            "planning.readiness": "plan_next_quarter",
            "mmm.channel_uncertainty.explain": "understand_channel_results",
            "calibration.compatibility.validate": "review_geox_evidence",
        }
        preferred_default = preferred_defaults.get(capability_id)
        if current_node_id is None and preferred_default in candidates:
            candidates = (preferred_default,) + tuple(node_id for node_id in candidates if node_id != preferred_default)
        if len(candidates) <= 1 or current_node_id is None:
            return tuple(self.get_node(node_id) for node_id in candidates)
        adjacent = set(self._edges.get(current_node_id, ()))
        preferred = [node_id for node_id in candidates if node_id in adjacent]
        return tuple(self.get_node(node_id) for node_id in (preferred or list(candidates)))

    def assess_transition(self, *, from_node_id: str | None, to_node_id: str, workspace: WorkspaceContext, registry: CapabilityRegistry = DEFAULT_CAPABILITY_REGISTRY) -> TransitionAssessment:
        target = self.get_node(to_node_id)
        if from_node_id is not None:
            self.get_node(from_node_id)
        if from_node_id != to_node_id and from_node_id is not None and to_node_id not in self._edges[from_node_id]:
            return TransitionAssessment(from_node_id=from_node_id, to_node_id=to_node_id, status=TransitionStatus.BLOCKED_INVALID_EDGE, reason_codes=["edge_not_declared"], blocked_actions=["progress"], next_allowed_node_ids=list(self._edges[from_node_id]), required_user_actions=["complete_current_node"])
        missing_inputs = [field for field in target.required_inputs if field not in workspace.known_inputs and field not in workspace.confirmed_inputs]
        missing_artifacts = [artifact for artifact in target.required_artifact_types if artifact not in workspace.available_artifact_ids and artifact not in workspace.session_artifact_ids]
        blocked = [capability.capability_id for capability in self.capabilities_for(to_node_id, registry) if capability.status in {CapabilityStatus.BLOCKED.value, CapabilityStatus.FUTURE_INTEGRATION.value}]
        reasons: list[str] = []
        if missing_inputs:
            reasons.append("missing_inputs")
        if missing_artifacts:
            reasons.append("missing_artifacts")
        if blocked:
            reasons.append("blocked_capability")
        status = TransitionStatus.ALLOWED
        if missing_inputs:
            status = TransitionStatus.BLOCKED_MISSING_INPUTS
        elif missing_artifacts:
            status = TransitionStatus.BLOCKED_MISSING_ARTIFACTS
        elif blocked:
            status = TransitionStatus.BLOCKED_CAPABILITY_STATUS
        return TransitionAssessment(
            from_node_id=from_node_id, to_node_id=to_node_id, status=status,
            satisfied_prerequisites=[field for field in target.required_inputs if field not in missing_inputs],
            missing_inputs=missing_inputs, missing_artifact_types=missing_artifacts,
            blocked_capabilities=blocked, blocked_actions=list(target.blocked_actions) if status != TransitionStatus.ALLOWED else [],
            reason_codes=reasons, next_allowed_node_ids=list(self._edges.get(to_node_id, ())),
            required_user_actions=["provide_missing_inputs"] if missing_inputs else [],
        )

    def validate(self, registry: CapabilityRegistry = DEFAULT_CAPABILITY_REGISTRY) -> tuple[WorkflowValidationIssue, ...]:
        issues: list[WorkflowValidationIssue] = []
        ids = [node.node_id for node in self._nodes]
        if self.graph_version != WORKFLOW_GRAPH_VERSION:
            issues.append(WorkflowValidationIssue(code="graph_version", message="unsupported graph version"))
        if ids != list(_FORWARD):
            issues.append(WorkflowValidationIssue(code="node_order", message="canonical node order is unstable"))
        if len(ids) != len(set(ids)):
            issues.append(WorkflowValidationIssue(code="duplicate_node", message="node IDs must be unique"))
        for node in self._nodes:
            if not _NODE_PATTERN.fullmatch(node.node_id):
                issues.append(WorkflowValidationIssue(code="invalid_node_id", node_id=node.node_id, message="invalid node ID"))
            for capability_id in node.required_capability_ids:
                try:
                    descriptor = registry.get(capability_id)
                except UnknownCapabilityError:
                    issues.append(WorkflowValidationIssue(code="unknown_capability", node_id=node.node_id, message=f"unknown capability {capability_id}"))
                    continue
                if descriptor.workflow_node_ids and node.node_id not in descriptor.workflow_node_ids and capability_id not in {"platform.onboarding", "data.requirements.explain", "uploaded_data.intake", "uploaded_data.profile", "uploaded_data.map_columns", "uploaded_data.assess_compatibility", "mmm.intake.readiness", "mmm.run.request", "planning.readiness", "planning.simulation.request", "planning.recommendation.explain_blocked", "geox.intake.requirements", "geox.design_request.create", "geox.feasibility.explain", "geox.readout.explain", "calibration.compatibility.validate", "calibration.signal.explain", "mmm.refresh.compare", "decision_package.build", "artifact.open", "report.open", "dashboard.context.update"}:
                    issues.append(WorkflowValidationIssue(code="binding_mismatch", node_id=node.node_id, message=f"capability {capability_id} does not reference node"))
            for target in self._edges.get(node.node_id, ()):
                if target not in self._by_id:
                    issues.append(WorkflowValidationIssue(code="unknown_edge", node_id=node.node_id, message=f"unknown edge {target}"))
        return tuple(issues)

    def fingerprint(self) -> str:
        payload = {"version": self.graph_version, "nodes": [node.model_dump(mode="json") for node in self._nodes], "edges": dict(self._edges)}
        return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _build_graph() -> WorkflowGraph:
    nodes = tuple(_node(node_id, DEFAULT_CAPABILITY_REGISTRY) for node_id in _FORWARD)
    edges: dict[str, tuple[str, ...]] = {
        node_id: (_FORWARD[index + 1],) if index < len(_FORWARD) - 1 else ()
        for index, node_id in enumerate(_FORWARD)
    }
    edges.update({
        "inspect_validate": ("build_validate_mmm", "bring_data"),
        "build_validate_mmm": ("understand_channel_results", "inspect_validate"),
        "plan_next_quarter": ("identify_evidence_gap", "understand_channel_results"),
        "design_geox": ("review_geox_evidence", "identify_evidence_gap"),
        "review_geox_evidence": ("refresh_mmm", "design_geox"),
        "refresh_mmm": ("decision_package", "understand_channel_results"),
    })
    return WorkflowGraph(nodes, edges)


DEFAULT_WORKFLOW_GRAPH = _build_graph()
