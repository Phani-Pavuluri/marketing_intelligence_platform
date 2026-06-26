"""Request validation and error behavior tests for P11 service hardening."""

from __future__ import annotations

from fastapi.testclient import TestClient

from mip.service.app import WORKFLOW_ROUTE_PATHS, create_app

_POST_ROUTES = [
    ("/advisory/cold-start", "sample_key", {"sample_key": "dtc_skincare_ecommerce"}),
    ("/readiness/assess", "sample_key", {"sample_key": "national_mmm_ready_geox_blocked"}),
    ("/calibration/map", "sample_key", {"sample_key": "valid_governed_evidence"}),
    ("/intake/overview", "example_key", {"example_key": "national_mmm_diagnostic"}),
]


def _client() -> TestClient:
    return TestClient(create_app())


def test_missing_json_body_returns_422() -> None:
    client = _client()
    for route, _, _ in _POST_ROUTES:
        response = client.post(route, content=b"", headers={"Content-Type": "application/json"})
        assert response.status_code == 422, route


def test_invalid_field_type_returns_422() -> None:
    client = _client()
    for route, field, _ in _POST_ROUTES:
        response = client.post(route, json={field: 123})
        assert response.status_code == 422, route


def test_unknown_request_fields_return_422() -> None:
    client = _client()
    for route, field, valid_body in _POST_ROUTES:
        body = {**valid_body, "unexpected_field": "not_allowed"}
        response = client.post(route, json=body)
        assert response.status_code == 422, route


def test_unknown_fixture_key_returns_400_not_500() -> None:
    client = _client()
    cases = [
        ("/advisory/cold-start", {"sample_key": "unknown"}),
        ("/readiness/assess", {"sample_key": "unknown"}),
        ("/calibration/map", {"sample_key": "unknown"}),
        ("/intake/overview", {"example_key": "unknown"}),
    ]
    for route, body in cases:
        response = client.post(route, json=body)
        assert response.status_code == 400, route
        assert response.json()["detail"]


def test_calibration_incompatible_evidence_returns_governed_payload() -> None:
    response = _client().post(
        "/calibration/map",
        json={"sample_key": "metric_mismatch"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["mapped_signal_id"] is None
    assert payload["status"] in {"blocked", "incompatible", "needs_more_data"}
    assert payload["governance"]["measurement_engine_execution"] is False


def test_all_workflow_routes_handle_validation_without_server_error() -> None:
    client = _client()
    for route in WORKFLOW_ROUTE_PATHS:
        response = client.post(route, json={})
        assert response.status_code in {200, 422}, route
