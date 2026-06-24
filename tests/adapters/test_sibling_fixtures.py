"""Tests for pinned sibling-repo fixture adapter imports."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from mip.adapters.base import AdapterRunKind, AdapterRunStatus, validate_adapter_output
from mip.adapters.governance import (
    adapter_output_to_decision_surface,
    adapter_output_to_experiment_evidence,
)
from mip.adapters.sibling_fixtures import (
    SiblingFixtureArtifactKind,
    SiblingFixtureExport,
    SiblingFixtureSource,
    SiblingFixtureValidationStatus,
    assert_safe_sibling_fixture_export,
    default_geox_sibling_fixture_path,
    default_mmm_sibling_fixture_path,
    load_sibling_fixture_export,
    register_sibling_fixture_export,
    sibling_fixture_to_adapter_output,
    trust_report_for_sibling_fixture,
    validate_sibling_fixture_export,
)
from mip.contracts import DecisionSurface, ExperimentEvidence
from mip.contracts.enums import ConfidenceTier
from mip.evidence.registry import EvidenceRegistry

_REPO_ROOT = Path(__file__).resolve().parents[2]
_MMM_FIXTURE_PATH = _REPO_ROOT / "tests/fixtures/sibling_exports/mmm_adapter_export_fixture.json"
_GEOX_FIXTURE_PATH = _REPO_ROOT / "tests/fixtures/sibling_exports/geox_adapter_export_fixture.json"


def test_default_fixture_paths_point_to_committed_files() -> None:
    assert default_mmm_sibling_fixture_path() == _MMM_FIXTURE_PATH
    assert default_geox_sibling_fixture_path() == _GEOX_FIXTURE_PATH
    assert _MMM_FIXTURE_PATH.exists()
    assert _GEOX_FIXTURE_PATH.exists()


def test_mmm_fixture_json_loads_and_validates() -> None:
    export = load_sibling_fixture_export(_MMM_FIXTURE_PATH)
    assert export.source_repo == SiblingFixtureSource.MMM
    assert export.engine_kind == AdapterRunKind.MMM
    assert export.validation_status == SiblingFixtureValidationStatus.VALIDATED_FIXTURE
    assert validate_sibling_fixture_export(export) == []


def test_geox_fixture_json_loads_and_validates() -> None:
    export = load_sibling_fixture_export(_GEOX_FIXTURE_PATH)
    assert export.source_repo == SiblingFixtureSource.PANEL_EXP
    assert export.engine_kind == AdapterRunKind.GEOX
    assert export.validation_status == SiblingFixtureValidationStatus.VALIDATED_FIXTURE
    assert validate_sibling_fixture_export(export) == []


def test_mmm_fixture_converts_to_adapter_output_bundle() -> None:
    export = load_sibling_fixture_export(_MMM_FIXTURE_PATH)
    bundle = sibling_fixture_to_adapter_output(export)
    assert bundle.kind == AdapterRunKind.MMM
    assert bundle.status == AdapterRunStatus.COMPLETED
    assert bundle.mmm_output is not None
    validate_adapter_output(bundle)


def test_geox_fixture_converts_to_adapter_output_bundle() -> None:
    export = load_sibling_fixture_export(_GEOX_FIXTURE_PATH)
    bundle = sibling_fixture_to_adapter_output(export)
    assert bundle.kind == AdapterRunKind.GEOX
    assert bundle.status == AdapterRunStatus.COMPLETED
    assert bundle.geox_output is not None
    validate_adapter_output(bundle)


def test_mmm_fixture_maps_to_decision_surface_trust_report() -> None:
    export = load_sibling_fixture_export(_MMM_FIXTURE_PATH)
    bundle = sibling_fixture_to_adapter_output(export)
    surface = adapter_output_to_decision_surface(bundle)
    assert isinstance(surface, DecisionSurface)
    trust_report = trust_report_for_sibling_fixture(export)
    assert trust_report.output_type == "decision_surface"
    assert trust_report.output_id == surface.surface_id


def test_geox_fixture_maps_to_experiment_evidence_registry_path() -> None:
    export = load_sibling_fixture_export(_GEOX_FIXTURE_PATH)
    registry = EvidenceRegistry()
    result = register_sibling_fixture_export(registry, export)
    assert result.registration.registered_in_registry is True
    assert isinstance(result.registration.artifact, ExperimentEvidence)
    bundle = sibling_fixture_to_adapter_output(export)
    evidence = adapter_output_to_experiment_evidence(bundle)
    assert evidence.evidence_id == result.registration.adapter_output_id
    assert registry.list_evidence()
    trust_report = trust_report_for_sibling_fixture(export)
    assert trust_report.confidence_tier != ConfidenceTier.BLOCKED


def test_blocked_fixture_produces_blocked_trust_report() -> None:
    export = load_sibling_fixture_export(_GEOX_FIXTURE_PATH)
    blocked = export.model_copy(
        update={
            "validation_status": SiblingFixtureValidationStatus.BLOCKED_FIXTURE,
            "blocking_reasons": ["fixture_export_blocked_for_demo"],
            "payload": {},
        }
    )
    registry = EvidenceRegistry()
    result = register_sibling_fixture_export(registry, blocked)
    assert result.registration.registered_in_registry is False
    assert result.registration.artifact is None
    trust_report = result.registration.trust_report
    assert trust_report.confidence_tier == ConfidenceTier.BLOCKED


def test_mismatched_source_repo_and_engine_kind_is_rejected() -> None:
    payload = json.loads(_MMM_FIXTURE_PATH.read_text(encoding="utf-8"))
    payload["engine_kind"] = "geox"
    with pytest.raises(ValueError, match="mmm source repo requires engine_kind mmm"):
        SiblingFixtureExport.model_validate(payload)


def test_missing_source_commit_marker_is_rejected() -> None:
    payload = json.loads(_MMM_FIXTURE_PATH.read_text(encoding="utf-8"))
    payload["source_commit_marker"] = "   "
    with pytest.raises(ValueError, match="cannot be empty"):
        SiblingFixtureExport.model_validate(payload)


@pytest.mark.parametrize(
    "forbidden_phrase",
    [
        "actual ROI",
        "true ROI",
        "incremental lift",
        "causal impact",
        "model result",
        "budget recommendation",
        "production-ready",
    ],
)
def test_forbidden_claims_are_rejected(forbidden_phrase: str) -> None:
    payload = json.loads(_MMM_FIXTURE_PATH.read_text(encoding="utf-8"))
    payload["warnings"] = [forbidden_phrase]
    export = SiblingFixtureExport.model_validate(payload)
    with pytest.raises(ValueError, match="forbidden phrase"):
        assert_safe_sibling_fixture_export(export)


def test_public_imports() -> None:
    from mip.adapters import (
        SiblingFixtureExport,
        SiblingFixtureSource,
        assert_safe_sibling_fixture_export,
        load_sibling_fixture_export,
        register_sibling_fixture_export,
        sibling_fixture_to_adapter_output,
        trust_report_for_sibling_fixture,
        validate_sibling_fixture_export,
    )

    assert SiblingFixtureSource.MMM.value == "mmm"
    assert callable(load_sibling_fixture_export)
    assert callable(sibling_fixture_to_adapter_output)
    assert callable(validate_sibling_fixture_export)
    assert callable(trust_report_for_sibling_fixture)
    assert callable(register_sibling_fixture_export)
    assert callable(assert_safe_sibling_fixture_export)
    assert SiblingFixtureExport is not None


def _blocked_export_from_mmm() -> SiblingFixtureExport:
    export = load_sibling_fixture_export(_MMM_FIXTURE_PATH)
    return export.model_copy(
        update={
            "fixture_id": "mmm-export-fixture-blocked",
            "validation_status": SiblingFixtureValidationStatus.BLOCKED_FIXTURE,
            "blocking_reasons": ["pinned_fixture_blocked"],
            "payload": {},
        }
    )


def test_invalid_fixture_requires_blocking_reasons_at_model_level() -> None:
    export = load_sibling_fixture_export(_MMM_FIXTURE_PATH)
    data = export.model_dump()
    data["validation_status"] = SiblingFixtureValidationStatus.INVALID_FIXTURE
    data["blocking_reasons"] = []
    data["payload"] = {}
    with pytest.raises(ValueError, match="blocked or invalid fixture requires blocking_reasons"):
        SiblingFixtureExport.model_validate(data)


def test_mismatched_artifact_kind_is_rejected() -> None:
    export = load_sibling_fixture_export(_MMM_FIXTURE_PATH)
    data = deepcopy(export.model_dump())
    data["artifact_kind"] = SiblingFixtureArtifactKind.GEOX_ADAPTER_OUTPUT
    with pytest.raises(ValueError, match="mmm source repo requires mmm_adapter_output"):
        SiblingFixtureExport.model_validate(data)
