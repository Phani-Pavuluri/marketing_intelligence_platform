"""Workflow route tests for P10b deterministic API endpoints."""

from __future__ import annotations

import json

from fastapi.testclient import TestClient

from mip.service.app import WORKFLOW_ROUTE_PATHS, create_app

_WORKFLOW_ROUTES = WORKFLOW_ROUTE_PATHS


def _client() -> TestClient:
    return TestClient(create_app())


def _route_paths(application: object) -> set[str]:
    openapi = getattr(application, "openapi", None)
    if callable(openapi):
        return set(openapi()["paths"].keys())
    paths: set[str] = set()
    routes = getattr(application, "routes", [])
    for route in routes:
        if hasattr(route, "path") and route.path:
            paths.add(route.path)
    return paths


def test_workflow_routes_exist() -> None:
    paths = _route_paths(create_app())
    for route in _WORKFLOW_ROUTES:
        assert route in paths


def test_advisory_cold_start_returns_200() -> None:
    response = _client().post("/advisory/cold-start", json={"sample_key": "dtc_skincare_ecommerce"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["governance"]["advisory_only"] is True
    assert payload["governance"]["causal_decision_support"] is False
    assert payload["evidence_mode"]
    assert payload["channel_hypotheses"]


def test_advisory_unknown_sample_returns_400() -> None:
    response = _client().post("/advisory/cold-start", json={"sample_key": "unknown"})
    assert response.status_code == 400


def test_advisory_invalid_body_returns_422() -> None:
    response = _client().post("/advisory/cold-start", json={"sample_key": 123})
    assert response.status_code == 422


def test_readiness_assess_national_blocked_returns_200() -> None:
    response = _client().post(
        "/readiness/assess",
        json={"sample_key": "national_mmm_ready_geox_blocked"},
    )
    assert response.status_code == 200
    payload = response.json()
    report_types = {report["report_type"] for report in payload["reports"]}
    assert "geox_design_readiness" in report_types
    geox = next(
        report for report in payload["reports"] if report["report_type"] == "geox_design_readiness"
    )
    assert geox["status"] in {"blocked", "needs_more_data", "not_applicable"}
    assert geox["blocking_reasons"] or geox["blocked_next_steps"]


def test_calibration_map_valid_returns_200() -> None:
    response = _client().post(
        "/calibration/map",
        json={"sample_key": "valid_governed_evidence"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "mapped"
    assert payload["mapped_signal_id"]


def test_calibration_map_missing_uncertainty_blocks_mapping() -> None:
    response = _client().post(
        "/calibration/map",
        json={"sample_key": "missing_uncertainty"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["mapped_signal_id"] is None
    assert payload["status"] in {"blocked", "needs_more_data", "incompatible"}
    combined = json.dumps(payload).lower()
    assert "missing_uncertainty" in combined or "standard_error" in combined


def test_calibration_map_metric_mismatch_blocks_mapping() -> None:
    response = _client().post(
        "/calibration/map",
        json={"sample_key": "metric_mismatch"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["mapped_signal_id"] is None
    assert payload["status"] in {"blocked", "incompatible", "needs_more_data"}
    combined = json.dumps(payload).lower()
    assert "incompatible" in combined or "metric" in combined


def test_intake_overview_returns_routing_summary() -> None:
    response = _client().post(
        "/intake/overview",
        json={"example_key": "national_mmm_diagnostic"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["recommended_path"]
    assert payload["why_this_path"]
    assert payload["governance"]["causal_decision_support"] is False


def test_intake_overview_unknown_example_returns_400() -> None:
    response = _client().post("/intake/overview", json={"example_key": "unknown"})
    assert response.status_code == 400
