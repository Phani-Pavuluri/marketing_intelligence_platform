"""Deterministic, metadata-only platform truth assembled from canonical sources."""
# ruff: noqa
from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from enum import StrEnum
from typing import Iterable

from pydantic import Field, model_validator
from mip.contracts.base import ContractBaseModel
from mip.contracts.conversation import CapabilityStatus, ExecutionMode
from mip.control_plane.capability_registry import CapabilityRegistry, DEFAULT_CAPABILITY_REGISTRY, UnknownCapabilityError
from mip.control_plane.workflow_graph import DEFAULT_WORKFLOW_GRAPH, WORKFLOW_GRAPH_VERSION, WorkflowGraph, UnknownWorkflowNodeError

PLATFORM_TRUTH_SCHEMA_VERSION = "platform_truth_v1"

class RuntimeFeatureStatus(StrEnum):
    AVAILABLE = "available"
    FIXTURE_BACKED = "fixture_backed"
    READINESS_ONLY = "readiness_only"
    IMPLEMENTED_NOT_USER_ENABLED = "implemented_not_user_enabled"
    EXTERNAL_EXECUTION = "external_execution"
    BLOCKED = "blocked"
    NOT_IMPLEMENTED = "not_implemented"
    FUTURE_INTEGRATION = "future_integration"

class RuntimeFeatureTruthRecord(ContractBaseModel):
    feature_id: str
    status: RuntimeFeatureStatus
    description: str
    available_modes: list[str] = Field(default_factory=list)
    blocked_modes: list[str] = Field(default_factory=list)
    authoritative_source: str
    source_reference: str

class CapabilityTruthRecord(ContractBaseModel):
    capability_id: str
    capability_version: str
    domain: str
    status: CapabilityStatus
    owner: str
    supported_intents: list[str]
    supported_event_types: list[str]
    required_inputs: list[str]
    conditional_inputs: list[str]
    required_artifact_types: list[str]
    produced_artifact_types: list[str]
    execution_modes: list[ExecutionMode]
    allowed_claims: list[str]
    blocked_claims: list[str]
    workflow_node_ids: list[str]
    next_capability_ids: list[str]
    release_gate: str | None
    currently_executable: bool
    execution_boundary: str
    source_reference: str

    @model_validator(mode="after")
    def safe_execution(self) -> "CapabilityTruthRecord":
        if self.status in {CapabilityStatus.BLOCKED, CapabilityStatus.FUTURE_INTEGRATION} and self.currently_executable:
            raise ValueError("blocked or future capabilities cannot be executable")
        if set(self.allowed_claims) & set(self.blocked_claims):
            raise ValueError("allowed and blocked claims overlap")
        return self

class WorkflowTruthRecord(ContractBaseModel):
    node_id: str
    display_name: str
    business_purpose: str
    required_capability_ids: list[str]
    required_inputs: list[str]
    required_artifact_types: list[str]
    available_actions: list[str]
    blocked_actions: list[str]
    next_valid_node_ids: list[str]
    execution_mode: ExecutionMode
    source_reference: str

class RuntimeStatusCatalog(ContractBaseModel):
    features: tuple[RuntimeFeatureTruthRecord, ...]

class PlatformTruthSnapshot(ContractBaseModel):
    schema_version: str = PLATFORM_TRUTH_SCHEMA_VERSION
    snapshot_version: str
    generated_at: datetime
    registry_version: str
    registry_fingerprint: str
    workflow_graph_version: str
    workflow_graph_fingerprint: str
    capabilities: tuple[CapabilityTruthRecord, ...]
    workflow_nodes: tuple[WorkflowTruthRecord, ...]
    runtime_features: tuple[RuntimeFeatureTruthRecord, ...]
    global_allowed_claims: tuple[str, ...]
    global_blocked_claims: tuple[str, ...]
    global_release_boundaries: tuple[str, ...]
    source_references: tuple[str, ...]
    snapshot_fingerprint: str

    @model_validator(mode="after")
    def validate_snapshot(self) -> "PlatformTruthSnapshot":
        if self.generated_at.tzinfo is None:
            raise ValueError("generated_at must be timezone-aware")
        if set(self.global_allowed_claims) & set(self.global_blocked_claims):
            raise ValueError("global claim boundaries overlap")
        return self

    def get_capability_truth(self, capability_id: str) -> CapabilityTruthRecord:
        for record in self.capabilities:
            if record.capability_id == capability_id:
                return record.model_copy(deep=True)
        raise UnknownCapabilityError(f"Unknown capability: {capability_id}")

    def get_workflow_truth(self, node_id: str) -> WorkflowTruthRecord:
        for record in self.workflow_nodes:
            if record.node_id == node_id:
                return record.model_copy(deep=True)
        raise UnknownWorkflowNodeError(f"Unknown workflow node: {node_id}")

    def get_runtime_feature_truth(self, feature_id: str) -> RuntimeFeatureTruthRecord:
        for record in self.runtime_features:
            if record.feature_id == feature_id:
                return record.model_copy(deep=True)
        raise KeyError(f"Unknown runtime feature: {feature_id}")

def _runtime_catalog() -> RuntimeStatusCatalog:
    blocked = RuntimeFeatureStatus.BLOCKED
    return RuntimeStatusCatalog(features=tuple(RuntimeFeatureTruthRecord(feature_id=f, status=s, description=d, available_modes=m, blocked_modes=b, authoritative_source="repository runtime evidence", source_reference=ref) for f, s, d, m, b, ref in [
        ("persistent_conversation", RuntimeFeatureStatus.AVAILABLE, "Persistent workspace conversation state.", ["local_session"], ["multi_user"], "control_plane.workspace"),
        ("typed_interaction_events", RuntimeFeatureStatus.AVAILABLE, "Typed append-only interaction events.", ["typed_ui"], [], "conversation contracts"),
        ("capability_registry", RuntimeFeatureStatus.AVAILABLE, "Metadata-only capability registry.", ["discovery"], ["execution"], "control_plane.capability_registry"),
        ("deterministic_router_fallback", RuntimeFeatureStatus.AVAILABLE, "Provider-free routing fallback.", ["fallback"], ["llm_primary"], "control_plane.dialogue_router"),
        ("workflow_graph", RuntimeFeatureStatus.AVAILABLE, "Governed workflow nodes and edges.", ["assessment"], ["implicit_execution"], "control_plane.workflow_graph"),
        ("structured_platform_truth", RuntimeFeatureStatus.AVAILABLE, "Typed snapshot of current platform facts.", ["read_only"], ["prose_authority"], "mip.knowledge.platform_truth"),
        ("approved_knowledge_corpus", RuntimeFeatureStatus.AVAILABLE, "Reviewed explanatory documents.", ["read_only"], ["status_authority"], "mip.knowledge.corpus"),
        ("read_only_retrieval", RuntimeFeatureStatus.NOT_IMPLEMENTED, "Future exact or semantic retrieval boundary.", [], ["retrieval"], "CF3 gate"),
        ("llm_conversational_front_door", RuntimeFeatureStatus.NOT_IMPLEMENTED, "Future constrained LLM front door.", [], ["provider_calls"], "CF4 gate"),
        ("artifact_resolver", blocked, "Artifact resolution is not implemented.", [], ["artifact_interpretation"], "Phase F gate"),
        ("artifact_grounded_interpretation", blocked, "Artifact interpretation requires resolver and evidence.", [], ["artifact_claims"], "Phase F/H gate"),
        ("uploaded_data_readiness", RuntimeFeatureStatus.READINESS_ONLY, "Readiness-only uploaded data flow.", ["readiness"], ["fitting"], "workflow graph and readiness contracts"),
        ("live_mmm_fitting", blocked, "Live MMM fitting is unavailable.", [], ["execution"], "capability registry mmm.run.request"),
        ("live_geox_design_execution", blocked, "Live GeoX design execution is unavailable.", [], ["execution"], "capability registry geox"),
        ("live_geox_assignment", blocked, "Treatment assignment remains unauthorized.", [], ["assignment"], "capability registry geox"),
        ("calibration_application", RuntimeFeatureStatus.READINESS_ONLY, "Calibration compatibility is readiness-only.", ["validation"], ["application"], "capability registry calibration"),
        ("planning_simulation", blocked, "Planning simulation remains blocked.", [], ["simulation"], "capability registry planning.simulation.request"),
        ("budget_optimization", blocked, "Budget optimization is unavailable.", [], ["optimization"], "capability registry"),
        ("recommendation_generation", blocked, "Recommendations are unauthorized.", [], ["recommendations"], "claim policy and registry"),
        ("multi_view_conversation", RuntimeFeatureStatus.FUTURE_INTEGRATION, "Multi-view continuity is future work.", [], ["multi_view"], "Phase K gate"),
    ]))

DEFAULT_RUNTIME_STATUS_CATALOG = _runtime_catalog()

def build_platform_truth_snapshot(*, registry: CapabilityRegistry = DEFAULT_CAPABILITY_REGISTRY, workflow: WorkflowGraph = DEFAULT_WORKFLOW_GRAPH, runtime_status_catalog: RuntimeStatusCatalog = DEFAULT_RUNTIME_STATUS_CATALOG, generated_at: datetime | None = None) -> PlatformTruthSnapshot:
    timestamp = generated_at or datetime.now(UTC)
    if timestamp.tzinfo is None:
        raise ValueError("generated_at must be timezone-aware")
    capabilities = tuple(CapabilityTruthRecord(capability_id=d.capability_id, capability_version=d.capability_version, domain=d.domain, status=d.status, owner=d.owner, supported_intents=list(d.supported_intents), supported_event_types=[str(e) for e in d.supported_event_types], required_inputs=list(d.required_inputs), conditional_inputs=list(d.conditional_inputs), required_artifact_types=list(d.required_artifact_types), produced_artifact_types=list(d.produced_artifact_types), execution_modes=list(d.execution_modes), allowed_claims=list(d.allowed_claims), blocked_claims=list(d.blocked_claims), workflow_node_ids=list(d.workflow_node_ids), next_capability_ids=list(d.next_capability_ids), release_gate=d.release_gate, currently_executable=d.status in {CapabilityStatus.AVAILABLE, CapabilityStatus.FIXTURE_BACKED}, execution_boundary="metadata/readiness only; no executor exposed", source_reference=f"capability_registry:{d.capability_id}") for d in registry.list_all())
    nodes = tuple(WorkflowTruthRecord(node_id=n.node_id, display_name=n.display_name, business_purpose=n.business_purpose, required_capability_ids=list(n.required_capability_ids), required_inputs=list(n.required_inputs), required_artifact_types=list(n.required_artifact_types), available_actions=list(n.available_actions), blocked_actions=list(n.blocked_actions), next_valid_node_ids=[x.node_id for x in workflow.next_nodes(n.node_id)], execution_mode=n.execution_mode, source_reference=f"workflow_graph:{n.node_id}") for n in workflow.list_nodes())
    payload = {"registry": registry.fingerprint(), "workflow": workflow.fingerprint(), "capabilities": [c.model_dump(mode="json") for c in capabilities], "nodes": [n.model_dump(mode="json") for n in nodes], "features": [f.model_dump(mode="json") for f in runtime_status_catalog.features]}
    fingerprint = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return PlatformTruthSnapshot(snapshot_version="1", generated_at=timestamp, registry_version=registry.registry_version, registry_fingerprint=registry.fingerprint(), workflow_graph_version=workflow.graph_version, workflow_graph_fingerprint=workflow.fingerprint(), capabilities=capabilities, workflow_nodes=nodes, runtime_features=runtime_status_catalog.features, global_allowed_claims=("documented capability metadata", "readiness status",), global_blocked_claims=("execution success", "user data", "artifact numbers", "recommendations",), global_release_boundaries=("artifact_resolution_release", "future_engine_release", "simulation_release"), source_references=("capability_registry", "workflow_graph", "runtime_status_catalog"), snapshot_fingerprint=fingerprint)
