# Conversational Control Plane Workflow Graph and Binding 001

Phase E adds the canonical declarative graph at `src/mip/control_plane/workflow_graph.py`, version `workflow_graph_v1`. It exposes `DEFAULT_WORKFLOW_GRAPH`, immutable node access, capability bindings, deterministic node/capability lookup, explicit forward and return edges, transition assessment, validation, and a stable fingerprint.

The graph contains exactly eleven nodes in canonical order: define_decision, bring_data, inspect_validate, build_validate_mmm, understand_channel_results, plan_next_quarter, identify_evidence_gap, design_geox, review_geox_evidence, refresh_mmm, and decision_package. The forward journey is explicit; only governed return edges are included. Unknown nodes and invalid edges fail closed. Transition assessments distinguish allowed, missing inputs, missing artifacts, blocked capability status, and invalid edges, with reason codes and required actions. Assessment never executes a capability, loads an artifact, traverses a workflow automatically, or imports optional engines.

Bindings use registered capability IDs and graph metadata. Router capability suggestions map to preferred nodes without mutating workspace state. Workspace typed workflow actions assess before mutation and update active/completed/available/blocked node fields; neutral state starts at define_decision, sample and upload modes start at bring_data, and reset restores the neutral node. Existing fixture stage aliases remain compatibility-only; the polished eleven-node vertical UI remains deferred until artifact resolution and grounded responses.

Sample, upload, and future live modes share this graph. Sample activation remains fixture-scoped and cannot jump to planning; upload mode has no result or planning access; simulation/recommendation, live MMM/GeoX, assignment, and decision-package production remain blocked by metadata and release gates. Conversation identity and the empty-transcript fix are preserved.

Browser review was unavailable in this agent environment. AppTest, automated, Docker, and public deployment checks passed; visual verification remains pending user verification.

Next artifact: `MIP_CONVERSATIONAL_CONTROL_PLANE_ARTIFACT_AND_REQUIREMENT_RESOLVER_001`.
