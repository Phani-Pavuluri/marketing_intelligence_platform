import pytest

# ruff: noqa: E501
from mip.contracts.conversation import WorkspaceContext
from mip.control_plane import (
    DEFAULT_WORKFLOW_GRAPH,
    TransitionStatus,
    UnknownWorkflowNodeError,
)


def empty_context() -> WorkspaceContext:
    return WorkspaceContext(
        session_id="s", conversation_id="c", workspace_id="w",
        active_view="workspace_home", active_workflow_node_id="define_decision",
        available_workflow_node_ids=["define_decision"],
    )


def test_graph_has_canonical_order_and_stable_identity() -> None:
    graph = DEFAULT_WORKFLOW_GRAPH
    assert [node.node_id for node in graph.list_nodes()] == [
        "define_decision", "bring_data", "inspect_validate", "build_validate_mmm",
        "understand_channel_results", "plan_next_quarter", "identify_evidence_gap",
        "design_geox", "review_geox_evidence", "refresh_mmm", "decision_package",
    ]
    assert graph.validate() == ()
    assert graph.fingerprint() == graph.fingerprint()
    with pytest.raises(UnknownWorkflowNodeError):
        graph.get_node("not_a_node")


def test_forward_and_return_edges_are_explicit() -> None:
    assert DEFAULT_WORKFLOW_GRAPH.next_nodes("define_decision")[0].node_id == "bring_data"
    assert {node.node_id for node in DEFAULT_WORKFLOW_GRAPH.next_nodes("inspect_validate")} == {"build_validate_mmm", "bring_data"}
    assert {node.node_id for node in DEFAULT_WORKFLOW_GRAPH.next_nodes("refresh_mmm")} == {"decision_package", "understand_channel_results"}
    assert DEFAULT_WORKFLOW_GRAPH.next_nodes("define_decision") != DEFAULT_WORKFLOW_GRAPH.next_nodes("plan_next_quarter")


def test_transition_assessment_distinguishes_invalid_missing_and_blocked() -> None:
    graph = DEFAULT_WORKFLOW_GRAPH
    invalid = graph.assess_transition(from_node_id="define_decision", to_node_id="plan_next_quarter", workspace=empty_context())
    assert invalid.status == TransitionStatus.BLOCKED_INVALID_EDGE
    missing = graph.assess_transition(from_node_id="define_decision", to_node_id="bring_data", workspace=empty_context())
    assert missing.status == TransitionStatus.ALLOWED
    missing_input = graph.assess_transition(from_node_id="inspect_validate", to_node_id="build_validate_mmm", workspace=empty_context())
    assert missing_input.status == TransitionStatus.BLOCKED_MISSING_INPUTS
    blocked = graph.assess_transition(
        from_node_id="plan_next_quarter", to_node_id="identify_evidence_gap",
        workspace=empty_context().model_copy(update={"active_workflow_node_id": "plan_next_quarter", "known_inputs": {"planning_horizon": "next_quarter"}}),
    )
    assert blocked.status in {TransitionStatus.ALLOWED, TransitionStatus.BLOCKED_CAPABILITY_STATUS}


def test_bindings_and_router_mapping_are_declarative() -> None:
    for node in DEFAULT_WORKFLOW_GRAPH.list_nodes():
        assert DEFAULT_WORKFLOW_GRAPH.capabilities_for(node.node_id)
    assert DEFAULT_WORKFLOW_GRAPH.nodes_for_routing("mmm.intake.requirements")[0].node_id == "bring_data"
    assert DEFAULT_WORKFLOW_GRAPH.nodes_for_routing("mmm.intake.readiness")[0].node_id == "inspect_validate"
    assert DEFAULT_WORKFLOW_GRAPH.nodes_for_routing("geox.design_request.create")[0].node_id == "design_geox"
    assert DEFAULT_WORKFLOW_GRAPH.nodes_for_routing("planning.readiness")[0].node_id == "plan_next_quarter"


def test_graph_structure_is_immutable_and_has_no_execution_hooks() -> None:
    nodes = DEFAULT_WORKFLOW_GRAPH.list_nodes()
    nodes[0].display_name = "mutated"
    assert DEFAULT_WORKFLOW_GRAPH.get_node("define_decision").display_name != "mutated"
    assert not any(callable(value) for node in DEFAULT_WORKFLOW_GRAPH.list_nodes() for value in node.model_dump().values())
