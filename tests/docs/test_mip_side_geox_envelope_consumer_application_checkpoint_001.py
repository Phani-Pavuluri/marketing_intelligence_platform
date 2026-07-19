import json
from pathlib import Path

ROOT = Path(__file__).parents[2]
DOC = ROOT / "docs/architecture/MIP_SIDE_GEOX_ENVELOPE_CONSUMER_APPLICATION_CHECKPOINT_001.md"
SUMMARY = ROOT / "docs/architecture/archives/MIP_SIDE_GEOX_ENVELOPE_CONSUMER_APPLICATION_CHECKPOINT_001_summary.json"


def test_checkpoint_artifacts_and_boundaries():
    assert DOC.exists()
    data = json.loads(SUMMARY.read_text())
    forbidden = [k for k in data if k.endswith("_authorized") or k in {"geox_repository_modified", "geox_package_called", "production_adapter_added", "mip_fixture_integration_dry_run_added"}]
    assert all(data[key] is False for key in forbidden)
    assert data["decision"] in {"PROCEED_TO_MIP_GEOX_ENVELOPE_FIXTURE_INTEGRATION_DRY_RUN", "BLOCK_MIP_GEOX_ENVELOPE_FIXTURE_INTEGRATION_PENDING_RUNTIME_VALIDATION", "PROCEED_TO_MIP_GEOX_CONSUMER_RUNTIME_REMEDIATION"}
    assert data["recommended_next_artifact"] in {"MIP_GEOX_ENVELOPE_FIXTURE_INTEGRATION_DRY_RUN_001", "MIP_GEOX_CONSUMER_RUNTIME_VALIDATION_RECOVERY_001", "MIP_GEOX_CONSUMER_RUNTIME_REMEDIATION_001"}
    text = DOC.read_text()
    for keyword in ("can_say", "cannot_say", "blocked reasons", "readiness", "GeoX dependency boundary", "fixture-only"):
        assert keyword in text
