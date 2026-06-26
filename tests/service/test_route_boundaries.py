"""Governance and boundary tests for P10b service routes."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from mip.service.app import create_app
from mip.service.contracts import FORBIDDEN_API_OUTPUT_PHRASES

_FORBIDDEN_PHRASES = FORBIDDEN_API_OUTPUT_PHRASES


def _collect_response_text(client: TestClient) -> str:
    payloads = [
        client.get("/health").json(),
        client.get("/version").json(),
        client.post("/advisory/cold-start", json={"sample_key": "dtc_skincare_ecommerce"}).json(),
        client.post(
            "/readiness/assess",
            json={"sample_key": "national_mmm_ready_geox_blocked"},
        ).json(),
        client.post("/calibration/map", json={"sample_key": "valid_governed_evidence"}).json(),
        client.post("/intake/overview", json={"example_key": "national_mmm_diagnostic"}).json(),
    ]
    return json.dumps(payloads).lower()


def test_no_forbidden_measurement_claims_in_route_outputs() -> None:
    client = TestClient(create_app())
    combined = _collect_response_text(client)
    for phrase in _FORBIDDEN_PHRASES:
        assert phrase not in combined


def test_health_and_version_remain_deterministic() -> None:
    client = TestClient(create_app())
    health = client.get("/health").json()
    version = client.get("/version").json()
    assert health["llm_enabled"] is False
    assert health["external_services_enabled"] is False
    assert health["persistence_enabled"] is False
    assert version["api_phase"] == "P10b.1"
    assert version["llm_enabled"] is False


def test_workflow_responses_do_not_enable_llm_or_persistence() -> None:
    client = TestClient(create_app())
    advisory = client.post(
        "/advisory/cold-start",
        json={"sample_key": "local_fitness_studio"},
    ).json()
    readiness = client.post(
        "/readiness/assess",
        json={"sample_key": "dma_week_structurally_ready"},
    ).json()
    for payload in (advisory, readiness):
        governance = payload["governance"]
        assert governance["llm_enabled"] is False
        assert governance["external_services_enabled"] is False
        assert governance["persistence_enabled"] is False
        assert governance["production_connector_enabled"] is False
        assert governance["measurement_engine_execution"] is False


def test_advisory_route_is_advisory_only() -> None:
    client = TestClient(create_app())
    payload = client.post(
        "/advisory/cold-start",
        json={"sample_key": "traffic_informed_advisory"},
    ).json()
    assert payload["governance"]["advisory_only"] is True
    assert payload["governance"]["roi_claims_allowed"] is False
    assert "hypothesis" in json.dumps(payload["claim_types"]).lower()


def test_intake_route_returns_requirements_not_measurement_conclusions() -> None:
    client = TestClient(create_app())
    payload = client.post(
        "/intake/overview",
        json={"example_key": "geox_experiment_design"},
    ).json()
    combined = json.dumps(payload).lower()
    assert payload["recommended_path"]
    assert "lift" not in combined or "blocked" in combined
    assert payload["governance"]["causal_decision_support"] is False


def test_no_dockerfile_exists() -> None:
    assert not Path("Dockerfile").exists()
