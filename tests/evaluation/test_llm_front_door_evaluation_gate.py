# ruff: noqa
# mypy: ignore-errors
import json
from pathlib import Path

from mip.conversation import ConversationalFrontDoor, ProviderConfig
from mip.control_plane.workspace import InMemoryWorkspace


def test_evaluation_corpus_contains_mandatory_regression_and_boundaries():
    path = Path("tests/fixtures/conversation/llm_front_door_evaluation_v1.json")
    data = json.loads(path.read_text())
    ids = {case["case_id"] for case in data["cases"]}
    assert {"observed_transcript", "governed_actions", "artifact_boundary", "provider_failure", "typed_actions"} <= ids
    turns = next(case["conversation_turns"] for case in data["cases"] if case["case_id"] == "observed_transcript")
    assert turns == ["test", "whats MMM", "whats GeoX", "what data is needed", "how can you help", "measurement"]


def test_gate_records_provider_missing_without_calling_on_import():
    front_door = ConversationalFrontDoor(config=ProviderConfig())
    assert front_door.provider is None
    result = front_door.handle("whats MMM", workspace=InMemoryWorkspace(session_id="s", conversation_id="c", workspace_id="w"))
    assert result.provider_disclosure.invocation_status in {"not_invoked", "fallback_used"}
    assert "MMM" in result.answer or "mix" in result.answer.lower()
