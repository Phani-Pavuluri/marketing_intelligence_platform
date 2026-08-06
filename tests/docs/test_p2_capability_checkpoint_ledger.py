import json
import re
from collections.abc import Iterable
from pathlib import Path
from typing import cast

ROOT = Path(__file__).parents[2]
LEDGER_PATH = ROOT / "docs/program/P2_CAPABILITY_CHECKPOINT_LEDGER.json"
PROGRAM_STATE_PATH = ROOT / "docs/program/PROGRAM_CURRENT_STATE.md"
CHECKPOINTS_PATH = ROOT / "docs/program/REPOSITORY_CHECKPOINTS.md"
SEQUENCE_PATH = ROOT / "docs/program/NEXT_EXECUTION_SEQUENCE.md"
CONTEXT_INDEX_PATH = ROOT / "docs/execution/REPOSITORY_CONTEXT_INDEX.md"

EXPECTED_REPOSITORY_PINS = {
    "mip": "c3897ed0b1ca096d186a9cabda36e1b926c4e71f",
    "mmm": "fe8e784923994406a2e4907d28debd872d61fd73",
    "geox": "b11646bab1f461964644a6526ef4967a8f04624d",
}
EXPECTED_CAPABILITIES = {
    "geox_calibration_source_manifest_generator",
    "geox_calibration_source_manifest_validator",
    "geox_calibration_source_manifest_producer",
    "mmm_provenance_linked_compatibility_fixtures",
    "mip_geox_mmm_compatibility_bridge",
    "p2_d6_release_compatibility_evidence",
    "mip_fixture_only_planning_evidence_journey",
}
EXPECTED_SEQUENCE = [
    "GEOX_MAIN_TEST_ISOLATION_AND_CHECKPOINT_CONTEXT_RECOVERY_001",
    "GEOX_CALIBRATION_SOURCE_MANIFEST_CERTIFICATION_RECOVERY_001",
    "P2_MMM_PROVENANCE_LINKED_COMPATIBILITY_FIXTURES",
    "P2_MIP_GEOX_MMM_COMPATIBILITY_BRIDGE",
    "P2_D6_RELEASE_COMPATIBILITY_EVIDENCE",
    "P2_MIP_PLANNING_EVIDENCE_JOURNEY",
]
STALE_PINS = {
    "18ab0d0c798dfcedd3f07034f4561320929477ea",
    "1b75d1d3c9f49d40f2b7ab71f524fbd2dc6d1421",
    "ee9673c13e69082367c1727568946ac4c1a01015",
}


def _load_ledger() -> dict[str, object]:
    return cast(dict[str, object], json.loads(LEDGER_PATH.read_text()))


def _walk_dependencies(
    capability_id: str,
    capabilities: dict[str, dict[str, object]],
    active: set[str],
    visited: set[str],
) -> None:
    assert capability_id not in active, f"dependency cycle at {capability_id}"
    if capability_id in visited:
        return
    active.add(capability_id)
    dependencies = capabilities[capability_id]["dependencies"]
    assert isinstance(dependencies, list)
    for dependency in dependencies:
        assert isinstance(dependency, str)
        assert dependency in capabilities
        _walk_dependencies(dependency, capabilities, active, visited)
    active.remove(capability_id)
    visited.add(capability_id)


def _document_text(paths: Iterable[Path]) -> str:
    return "\n".join(path.read_text() for path in paths)


def _historical_or_current_paragraphs(document: str) -> list[str]:
    return [paragraph for paragraph in re.split(r"\n\s*\n", document) if paragraph]


def _assert_stale_pins_are_historical_only(document: str) -> None:
    historical_markers = (
        "historical",
        "prior",
        "superseded",
        "archived",
        "coordination provenance",
    )
    current_markers = (
        "current verified",
        "active repository observation",
        "current checkpoint",
        "active task prerequisite",
        "current execution sequence",
    )

    for paragraph in _historical_or_current_paragraphs(document):
        normalized_paragraph = paragraph.lower()
        for stale_sha in STALE_PINS:
            if stale_sha not in paragraph:
                continue
            assert any(marker in normalized_paragraph for marker in historical_markers)
            for marker in current_markers:
                assert not re.search(
                    rf"(?<!not ){re.escape(marker)}[^\n]*{stale_sha}|"
                    rf"{stale_sha}[^\n]*(?<!not ){re.escape(marker)}",
                    normalized_paragraph,
                )


def test_ledger_schema_pins_and_exact_capability_set() -> None:
    ledger = _load_ledger()
    assert ledger["schema_version"] == "mip_p2_capability_checkpoint_ledger_v1"
    assert ledger["program"] == "causal_marketing_intelligence_platform"
    assert ledger["phase"] == "P2"
    assert ledger["last_verified"] == "2026-08-05"
    assert ledger["missing_checkpoint"] == (
        "P2_GEOX_CALIBRATION_SOURCE_PRODUCER_CHECKPOINT"
    )

    observations = ledger["repository_observations"]
    assert isinstance(observations, dict)
    assert set(observations) == {"mip", "mmm", "geox"}
    for repository_id, expected_sha in EXPECTED_REPOSITORY_PINS.items():
        observation = observations[repository_id]
        assert isinstance(observation, dict)
        assert observation["main_sha"] == expected_sha
        assert re.fullmatch(r"[0-9a-f]{40}", expected_sha)

    capabilities = ledger["capabilities"]
    assert isinstance(capabilities, dict)
    assert set(capabilities) == EXPECTED_CAPABILITIES


def test_capability_vocabularies_dependencies_and_authority() -> None:
    ledger = _load_ledger()
    capabilities = ledger["capabilities"]
    vocabularies = ledger["state_vocabularies"]
    assert isinstance(capabilities, dict)
    assert isinstance(vocabularies, dict)

    for record in capabilities.values():
        assert isinstance(record, dict)
        for field in (
            "implementation_state",
            "validation_state",
            "certification_state",
            "consumer_verification_state",
            "downstream_eligibility",
        ):
            vocabulary = vocabularies[field]
            assert isinstance(vocabulary, list)
            assert record[field] in vocabulary

    visited: set[str] = set()
    for capability_id in capabilities:
        _walk_dependencies(capability_id, capabilities, set(), visited)
    assert visited == EXPECTED_CAPABILITIES

    authority = ledger["authority"]
    assert isinstance(authority, dict)
    assert authority
    assert all(value is False for value in authority.values())


def test_required_capability_classifications_and_parked_bridge() -> None:
    ledger = _load_ledger()
    capabilities = ledger["capabilities"]
    assert isinstance(capabilities, dict)

    generator = capabilities["geox_calibration_source_manifest_generator"]
    assert generator["implementation_state"] == "merged_on_main"
    assert generator["validation_state"] == "component_validated"
    assert generator["certification_state"] == "uncertified"

    validator = capabilities["geox_calibration_source_manifest_validator"]
    assert validator["implementation_state"] == "present_on_main"
    assert validator["validation_state"] == "incomplete"
    assert validator["certification_state"] == "uncertified"
    assert validator["downstream_eligibility"] == "blocked"

    producer = capabilities["geox_calibration_source_manifest_producer"]
    assert producer["implementation_state"] == "present_on_main"
    assert producer["certification_state"] == "uncertified"
    assert producer["downstream_eligibility"] == "blocked"

    mmm_fixtures = capabilities["mmm_provenance_linked_compatibility_fixtures"]
    assert mmm_fixtures["implementation_state"] == "not_started"
    assert mmm_fixtures["downstream_eligibility"] == "blocked"

    bridge = capabilities["mip_geox_mmm_compatibility_bridge"]
    evidence = bridge["evidence"]
    assert isinstance(evidence, dict)
    assert evidence["parked_branch_head_sha"] == (
        "480b32040ce185b8ff091435121c4bea6fc6c453"
    )
    assert evidence["resume_authorized"] is False
    assert bridge["downstream_eligibility"] == "blocked"

    for capability_id in (
        "p2_d6_release_compatibility_evidence",
        "mip_fixture_only_planning_evidence_journey",
    ):
        capability = capabilities[capability_id]
        assert capability["implementation_state"] == "not_started"
        assert capability["downstream_eligibility"] == "blocked"


def test_sequence_is_exact_unauthorized_and_has_one_next_eligible_item() -> None:
    ledger = _load_ledger()
    sequence = ledger["ordered_execution_sequence"]
    assert isinstance(sequence, list)
    assert [item["order"] for item in sequence] == list(range(1, 7))
    assert [item["task_id"] for item in sequence] == EXPECTED_SEQUENCE
    assert all(item["authorized"] is False for item in sequence)
    eligible = [item["task_id"] for item in sequence if item["next_eligible"]]
    assert eligible == ["GEOX_MAIN_TEST_ISOLATION_AND_CHECKPOINT_CONTEXT_RECOVERY_001"]


def test_program_documents_align_and_reject_stale_pins() -> None:
    paths = (
        PROGRAM_STATE_PATH,
        CHECKPOINTS_PATH,
        SEQUENCE_PATH,
        CONTEXT_INDEX_PATH,
    )
    text = _document_text(paths)
    for sha in EXPECTED_REPOSITORY_PINS.values():
        assert sha in text
    for path in paths:
        _assert_stale_pins_are_historical_only(path.read_text())
    for task_id in EXPECTED_SEQUENCE:
        assert task_id in SEQUENCE_PATH.read_text()
    for path in paths:
        assert "P2_CAPABILITY_CHECKPOINT_LEDGER.json" in path.read_text()
