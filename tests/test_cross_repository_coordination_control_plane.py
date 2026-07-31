import json
from pathlib import Path

ROOT = Path(__file__).parents[1]
PROGRAM = ROOT / "docs" / "program"
STATE_PATH = PROGRAM / "CROSS_REPOSITORY_COORDINATION_STATE.json"
PROTOCOL_PATH = PROGRAM / "CROSS_REPOSITORY_COORDINATION_PROTOCOL.md"
CURRENT_STATE_PATH = PROGRAM / "PROGRAM_CURRENT_STATE.md"
CHECKPOINTS_PATH = PROGRAM / "REPOSITORY_CHECKPOINTS.md"
SEQUENCE_PATH = PROGRAM / "NEXT_EXECUTION_SEQUENCE.md"


def test_cross_repository_coordination_control_plane() -> None:
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    assert state["schema_version"] == "mip_cross_repository_coordination_v1"
    assert state["coordinator_repository"] == "Phani-Pavuluri/marketing_intelligence_platform"
    expected_pins = {
        "mip": "631763cfb75fc42f8b1bf7025c5bce34c39097b5",
        "mmm": "1b75d1d3c9f49d40f2b7ab71f524fbd2dc6d1421",
        "geox": "e0cef94c063b03b29e1e1760fb1c2320ce497b56",
    }
    repositories = {entry["id"]: entry for entry in state["repositories"]}
    assert set(repositories) == set(expected_pins)
    for repository_id, sha in expected_pins.items():
        entry = repositories[repository_id]
        assert entry["observed_remote_main_sha"] == sha
        assert entry["evidence_paths"]
    workstreams = state["workstreams"]
    workstream_ids = {entry["id"] for entry in workstreams}
    assert len(workstream_ids) == len(workstreams)
    owners = {(entry["owner_repository"], entry["capability_area"]) for entry in workstreams}
    assert len(owners) == len(workstreams)
    blockers = state["blockers"]
    blocker_ids = {entry["id"] for entry in blockers}
    assert len(blocker_ids) == len(blockers)
    task_ids = {entry["task_id"] for entry in workstreams}
    for workstream in workstreams:
        assert set(workstream["dependencies"]) <= workstream_ids
        assert set(workstream["blocked_by"]) <= blocker_ids
    for blocker in blockers:
        assert blocker["state"] in {
            "open",
            "in_progress",
            "producer_completed_pending_consumer_verification",
            "resolved",
            "superseded",
        }
        assert blocker["evidence"]
        assert isinstance(blocker["consumer_verification_required"], bool)
        assert set(blocker["unblocks"]) <= task_ids | blocker_ids
        if blocker["state"] == "resolved":
            assert blocker["consumer_verification_required"] is True
    for blocker_id in (
        "P2-GEOX-TEMPORAL-VERSION-SEMANTICS",
        "P2-GEOX-READOUT-BUILDER-ENTRYPOINT",
        "P2-MMM-GEOX-NORMALIZATION",
        "P2-MMM-CROSS-REPOSITORY-FIXTURES",
        "P2-D6-RELEASE-COMPATIBILITY-EVIDENCE",
    ):
        assert blocker_id in blocker_ids
    sequence = state["ordered_program_sequence"]
    assert sequence[:3] == [
        "MIP_CROSS_REPOSITORY_COORDINATION_CONTROL_PLANE_001",
        "GEOX_CROSS_REPOSITORY_COORDINATION_PROTOCOL_ADOPTION_001",
        "MMM_CROSS_REPOSITORY_COORDINATION_PROTOCOL_ADOPTION_001",
    ]
    assert "MIP_P2_FIXTURE_ONLY_PLANNING_EVIDENCE_JOURNEY_001" in sequence
    assert state["authority"]["runtime_integration"] == "blocked"
    assert state["authority"]["recommendations"] == "blocked"
    assert state["authority"]["optimization"] == "blocked"
    assert state["authority"]["production"] == "blocked"
    assert state["authority"]["package_side_agents"] == "blocked"
    protocol = PROTOCOL_PATH.read_text(encoding="utf-8")
    assert "stale" in protocol
    assert "duplicate ownership" in protocol
    for path in (CURRENT_STATE_PATH, CHECKPOINTS_PATH, SEQUENCE_PATH):
        text = path.read_text(encoding="utf-8")
        for sha in expected_pins.values():
            assert sha in text or sha[:7] in text
    assert "implemented" not in state["authority"].values()
    assert state["authority"]["capability_authorizations_changed"] is False
