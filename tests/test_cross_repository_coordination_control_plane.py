import json
from pathlib import Path

ROOT = Path(__file__).parents[1]
PROGRAM = ROOT / "docs" / "program"
STATE_PATH = PROGRAM / "CROSS_REPOSITORY_COORDINATION_STATE.json"
PROTOCOL_PATH = PROGRAM / "CROSS_REPOSITORY_COORDINATION_PROTOCOL.md"
CURRENT_STATE_PATH = PROGRAM / "PROGRAM_CURRENT_STATE.md"
CHECKPOINTS_PATH = PROGRAM / "REPOSITORY_CHECKPOINTS.md"
SEQUENCE_PATH = PROGRAM / "NEXT_EXECUTION_SEQUENCE.md"
HISTORY_PATH = PROGRAM / "CROSS_REPOSITORY_COORDINATION_HISTORY.md"
REPORT_PATH = ROOT / "docs" / "execution" / "LATEST_COMPLETION_REPORT.md"
EXECUTION_STATE_PATH = ROOT / "docs" / "execution" / "EXECUTION_STATE.json"


def test_cross_repository_coordination_control_plane() -> None:
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    assert state["schema_version"] == "mip_cross_repository_coordination_v1"
    assert state["coordinator_repository"] == "Phani-Pavuluri/marketing_intelligence_platform"
    historical_snapshot_pins = {
        "mip": "3520176126d129e9288a9ce37591299ec856650a",
        "mmm": "1b75d1d3c9f49d40f2b7ab71f524fbd2dc6d1421",
        "geox": "ee9673c13e69082367c1727568946ac4c1a01015",
    }
    current_mip_main_at_review = "18ab0d0c798dfcedd3f07034f4561320929477ea"
    repositories = {entry["id"]: entry for entry in state["repositories"]}
    assert set(repositories) == set(historical_snapshot_pins)
    for repository_id, sha in historical_snapshot_pins.items():
        entry = repositories[repository_id]
        assert entry["observed_remote_main_sha"] == sha
        assert entry["evidence_paths"]
    assert repositories["mip"]["active_task_status"] == "merged"
    assert repositories["mip"]["latest_completed_task"] == (
        "MIP_CROSS_REPOSITORY_COORDINATION_CONTROL_PLANE_001"
    )
    assert repositories["mip"]["latest_closure_sha"] == historical_snapshot_pins["mip"]
    assert repositories["mip"]["remote_feature_branch_cleanup"] == (
        "observed_deleted_from_origin"
    )
    assert (
        repositories["geox"]["active_task_id"]
        == "GEOX_GOVERNED_READOUT_BUILDER_PACKAGE_ENTRYPOINT_001"
    )
    assert repositories["geox"]["active_task_status"] == "authorized"
    assert (
        repositories["geox"]["active_task_base_sha"]
        == "e0cef94c063b03b29e1e1760fb1c2320ce497b56"
    )
    assert (
        repositories["geox"]["active_task_authorization_head_sha"]
        == "c4c9059a6a6e882a10a356350376d8a64fb14057"
    )
    assert (
        repositories["geox"]["active_task_feature_branch"]
        == "feat/geox-governed-readout-builder-package-entrypoint-001"
    )
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
        if workstream["dependencies"]:
            assert workstream.get("live_resolution_conditions")
    mip_coordination = next(
        entry for entry in workstreams if entry["id"] == "WS-MIP-COORDINATION-001"
    )
    assert mip_coordination["status"] == "merged"
    assert mip_coordination["verified_sha"] == historical_snapshot_pins["mip"]
    assert "live MIP origin/main execution state" in mip_coordination[
        "live_resolution_condition"
    ]
    assert "never satisfies this condition" in mip_coordination[
        "live_resolution_condition"
    ]
    assert "feature_branch_review_state" not in mip_coordination
    assert state["feature_branch_review_source"]["snapshot_scope"] == (
        "repository_main_observations_only"
    )
    assert state["feature_branch_review_source"]["exact_remote_branch_evidence_paths"] == [
        "docs/execution/EXECUTION_STATE.json",
        "docs/execution/ACTIVE_TASK.md",
        "docs/execution/LATEST_COMPLETION_REPORT.md",
    ]
    assert "never satisfies a merged workstream dependency" in state[
        "feature_branch_review_source"
    ]["rule"]
    assert state["live_overlay_rules"]["merged_dependency_condition"]
    assert "cannot permanently block" in state["live_overlay_rules"]["stale_snapshot_behavior"]
    geox_builder = next(
        entry for entry in workstreams if entry["id"] == "WS-GEOX-READOUT-BUILDER-001"
    )
    assert geox_builder["dependencies"] == []
    assert set(geox_builder["advances_blockers"]) == {
        "P2-GEOX-TEMPORAL-VERSION-SEMANTICS",
        "P2-GEOX-READOUT-BUILDER-ENTRYPOINT",
    }
    assert (
        "MIP coordination metadata neither adds dependencies nor authorizes it."
        in geox_builder["owner_authority"]
    )
    assert (
        "GEOX_GOVERNED_READOUT_TEMPORAL_VERSION_AND_ENVELOPE_SEMANTICS_001"
        not in state["ordered_program_sequence"]
    )
    assert "GEOX_GOVERNED_READOUT_BUILDER_ENTRYPOINT_001" not in state["ordered_program_sequence"]
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
    assert sequence[:2] == [
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
    assert "live overlay" in protocol
    assert "cannot retroactively add" in protocol
    assert "must not be cached in the shared snapshot" in protocol
    for path in (CURRENT_STATE_PATH, CHECKPOINTS_PATH, SEQUENCE_PATH):
        text = path.read_text(encoding="utf-8")
        for sha in (
            current_mip_main_at_review,
            historical_snapshot_pins["mmm"],
            historical_snapshot_pins["geox"],
        ):
            assert sha in text or sha[:7] in text
    sequence_text = SEQUENCE_PATH.read_text(encoding="utf-8")
    assert "steps 5–7" not in sequence_text
    assert "No step 7 exists." in sequence_text
    assert (
        "Step 3 depends on live merged GeoX producer evidence at\n"
        "an exact pin and required consumer verification."
    ) in sequence_text
    assert (
        "Step 4 depends on both that\n"
        "live merged GeoX producer evidence and merged MMM normalization/certified-fixture\n"
        "evidence, with the declared consumer verification."
    ) in sequence_text
    assert "Steps 5–6 depend on the\npreceding producer and consumer evidence." in sequence_text
    assert "implemented" not in state["authority"].values()
    assert state["authority"]["capability_authorizations_changed"] is False
    history = HISTORY_PATH.read_text(encoding="utf-8")
    assert "GeoX `e0cef94c063b03b29e1e1760fb1c2320ce497b56`" in history
    assert (
        "GeoX `ee9673c13e69082367c1727568946ac4c1a01015`; authorization "
        "`c4c9059a6a6e882a10a356350376d8a64fb14057`"
        in history
    )
    assert "First coordination review changes requested" in history
    assert "MIP `b0a9a9c1812b1ae1740d85fbb29827d60d338ebe`" in history
    assert "Review decision only" in history
    assert "First coordination correction implementation published" in history
    assert "MIP `067aeca571f2702b88aee92f8647ededee1df0f1`" in history
    assert "Second coordination review changes requested" in history
    assert "MIP `96815daf3cfa3d8d5c658016219784e8e94947b8`" in history
    assert "Second coordination correction implementation published" in history
    assert "MIP `4c93a7c300b3471ffee2a11ff449094e82a1f11d`" in history
    assert "Coordination implementation approved and fast-forward merged" in history
    assert "Approved/merged MIP head `cc1904db8e18b5ba461cca2da738026acadfb43c`" in history
    assert "Coordination post-merge closure recorded" in history
    assert "MIP `3520176126d129e9288a9ce37591299ec856650a`" in history
    report = REPORT_PATH.read_text(encoding="utf-8")
    assert "Before `ready_for_review`, replace this section" not in report
    active_task = (ROOT / "docs" / "execution" / "ACTIVE_TASK.md").read_text(
        encoding="utf-8"
    )
    assert "Resume the existing branch" not in active_task
    execution_state = json.loads(EXECUTION_STATE_PATH.read_text(encoding="utf-8"))
    assert execution_state["repository"] == (
        "Phani-Pavuluri/marketing_intelligence_platform"
    )
    current_task_id = execution_state["task_id"]
    current_status = execution_state["status"]
    assert isinstance(current_task_id, str) and current_task_id
    assert isinstance(current_status, str) and current_status
    assert current_task_id in active_task
    assert current_task_id in report
    assert f"**Status:** {current_status}" in active_task
    assert f"**Current decision:** `{current_status}`" in report
    assert execution_state["merge_authorized"] is False
    assert execution_state["pr_creation_authorized"] is False
    assert execution_state["capability_authorizations_changed"] is False
    assert repositories["mip"]["active_task_status"] == "merged"
