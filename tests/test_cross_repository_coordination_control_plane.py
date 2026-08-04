import json
from pathlib import Path
from typing import TypeAlias, cast

JsonValue: TypeAlias = (
    str | int | float | bool | None | list["JsonValue"] | dict[str, "JsonValue"]
)
JsonObject: TypeAlias = dict[str, JsonValue]

ROOT = Path(__file__).parents[1]
PROGRAM = ROOT / "docs" / "program"
STATE_PATH = PROGRAM / "CROSS_REPOSITORY_COORDINATION_STATE.json"


def _state() -> JsonObject:
    raw: object = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    assert isinstance(raw, dict)
    return cast(JsonObject, raw)


def _object(value: JsonValue) -> JsonObject:
    assert isinstance(value, dict)
    return value


def _list(value: JsonValue) -> list[JsonValue]:
    assert isinstance(value, list)
    return value


def _by_id(entries: list[JsonValue]) -> dict[str, JsonObject]:
    result: dict[str, JsonObject] = {}
    for entry in entries:
        item = _object(entry)
        identifier = item["id"]
        assert isinstance(identifier, str)
        result[identifier] = item
    return result


def test_live_repository_pins_and_protocol_adoption_states_are_coherent() -> None:
    state = _state()
    repositories = _by_id(_list(state["repositories"]))
    assert (
        repositories["mip"]["observed_remote_main_sha"]
        == "976d3a1daeae9c52c8772e5112574f698951a57c"
    )
    assert repositories["mmm"]["active_task_id"] == "MMM_REPOSITORY_EXECUTION_PROTOCOL_ADOPTION_001"
    assert (
        repositories["mmm"]["absorbed_task_id"]
        == "MMM_CROSS_REPOSITORY_COORDINATION_PROTOCOL_ADOPTION_001"
    )
    geox = repositories["geox"]
    assert geox["observed_remote_main_sha"] == "b6c714ced8a9c6e9c1fcb0f6b4f7f79a542c5a7f"
    assert geox["active_task_id"] == "GEOX_EXECUTION_BRANCH_BINDING_001"
    assert geox["active_task_status"] == "superseded"
    assert geox["active_task_authorization_head_sha"] == "dc68853e87a65a494c942b3fe2794e321a22b036"
    workstreams = _by_id(_list(state["workstreams"]))
    assert workstreams["WS-GEOX-EXECUTION-BRANCH-BINDING-001"]["task_id"] == geox["active_task_id"]
    assert (
        workstreams["WS-GEOX-EXECUTION-BRANCH-BINDING-001"]["status"]
        == geox["active_task_status"]
    )
    assert workstreams["WS-GEOX-LEAN-DELIVERY-ADOPTION-001"]["status"] == "superseded"
    assert workstreams["WS-GEOX-EXECUTION-BRANCH-BINDING-REAUTHORING-001"]["status"] == "proposed"
    branch_source = _object(state["feature_branch_review_source"])
    assert branch_source["snapshot_scope"] == "repository_main_observations_only"


def test_geox_builder_supersession_and_successor_sequence_are_fail_closed() -> None:
    state = _state()
    workstreams = _by_id(_list(state["workstreams"]))
    old_builder = workstreams["WS-GEOX-READOUT-BUILDER-001"]
    successors = workstreams["WS-GEOX-PRODUCER-SUCCESSOR-SEQUENCE-001"]
    assert old_builder["status"] == "superseded"
    assert "without merge" in _string(old_builder["live_resolution_condition"])
    assert successors["status"] == "proposed"
    assert successors["task_id"] is None
    assert len(_list(successors["successor_outcomes"])) == 4
    assert successors["dependencies"] == ["WS-GEOX-EXECUTION-BRANCH-BINDING-REAUTHORING-001"]
    blockers = _by_id(_list(state["blockers"]))
    assert blockers["P2-GEOX-TEMPORAL-VERSION-SEMANTICS"]["state"] == "open"
    assert blockers["P2-GEOX-READOUT-BUILDER-ENTRYPOINT"]["state"] == "open"


def test_mmm_normalization_and_mip_p2_dependencies_require_consumer_verification() -> None:
    state = _state()
    workstreams = _by_id(_list(state["workstreams"]))
    assert workstreams["WS-MMM-NORMALIZATION-FIXTURES-001"]["status"] == "proposed"
    assert workstreams["WS-MIP-P2-JOURNEY-001"]["status"] == "proposed"
    for blocker in _list(state["blockers"]):
        assert _object(blocker)["consumer_verification_required"] is True
    journey = workstreams["WS-MIP-P2-JOURNEY-001"]
    conditions = _object(journey["live_resolution_conditions"])
    producer_condition = _string(conditions["WS-GEOX-PRODUCER-SUCCESSOR-SEQUENCE-001"])
    assert "exact merged GeoX producer evidence" in producer_condition


def test_roadmap_execution_sequence_preserves_p0_p8_and_removes_stale_current_state() -> None:
    roadmap = (ROOT / "docs" / "roadmap" / "ROADMAP.md").read_text(encoding="utf-8")
    sequence_path = ROOT / "docs" / "roadmap" / "ROADMAP_EXECUTION_SEQUENCE.md"
    sequence = sequence_path.read_text(encoding="utf-8")
    assert "P0–P8" in roadmap
    assert "R0–R6" in sequence
    assert "Current main: `000273a`" not in sequence
    assert "Immediate next phase: MIP tool registry" not in sequence
    assert "single authorized governed-readout builder" not in sequence


def test_stale_mip_resolver_is_superseded_without_merge_authority() -> None:
    mip = _by_id(_list(_state()["repositories"]))["mip"]
    assert mip["superseded_task_id"] == "MIP_ACTIVE_TASK_CONTEXT_RESOLVER_001"
    assert mip["superseded_task_status"] == "superseded_without_merge"
    assert mip["superseded_task_branch_head_sha"] == "b96dfc4365d5aadf9425d31aa576664f58270fa5"
    history = (PROGRAM / "CROSS_REPOSITORY_COORDINATION_HISTORY.md").read_text(
        encoding="utf-8"
    )
    assert "MIP_ACTIVE_TASK_CONTEXT_RESOLVER_001" in history
    assert "superseded without merge" in history


def test_coordination_authority_freezes_remain_false() -> None:
    authority = _object(_state()["authority"])
    assert authority["capability_authorizations_changed"] is False
    for key in (
        "runtime_integration",
        "real_data",
        "persistence",
        "recommendations",
        "optimization",
        "pilot",
        "production",
        "package_side_agents",
    ):
        assert authority[key] == "blocked"


def test_coordination_test_is_current_state_semantic_not_task_identity_coupled() -> None:
    state_text = STATE_PATH.read_text(encoding="utf-8")
    assert "MIP_COORDINATION_POST_MERGE_CLOSURE_RECONCILIATION_001" not in state_text
    old_active_builder = (
        '"GEOX_GOVERNED_READOUT_BUILDER_PACKAGE_ENTRYPOINT_001",\n'
        '      "status": "authorized"'
    )
    assert old_active_builder not in state_text


def _string(value: JsonValue) -> str:
    assert isinstance(value, str)
    return value
