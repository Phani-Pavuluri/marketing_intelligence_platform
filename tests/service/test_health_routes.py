"""Route tests for P10a health/version metadata endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient

from mip.service.app import create_app
from mip.service.metadata import PUBLIC_DEMO_URL

_DEFERRED_WORKFLOW_ROUTES = (
    "/advisory/cold-start",
    "/readiness/assess",
    "/calibration/map",
    "/intake/overview",
)


def _route_paths(application: object) -> set[str]:
    routes = getattr(application, "routes", [])
    return {route.path for route in routes if hasattr(route, "path")}


def test_health_returns_200_with_deterministic_flags() -> None:
    client = TestClient(create_app())
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["service"] == "mip-api"
    assert payload["mode"] == "deterministic"
    assert payload["llm_enabled"] is False
    assert payload["external_services_enabled"] is False
    assert payload["persistence_enabled"] is False
    assert payload["production_connector_enabled"] is False
    assert payload["measurement_engine_execution_enabled"] is False


def test_version_returns_200_with_p10a_metadata() -> None:
    client = TestClient(create_app())
    response = client.get("/version")
    assert response.status_code == 200
    payload = response.json()
    assert payload["service"] == "mip-api"
    assert payload["project"] == "Marketing Intelligence Platform"
    assert payload["api_phase"] == "P10a"
    assert payload["baseline_commit"] == "b54d2d0"
    assert payload["public_demo_url"] == PUBLIC_DEMO_URL
    assert payload["streamlit_entrypoint"] == "app/streamlit_app.py"
    assert payload["mode"] == "deterministic"
    assert payload["llm_enabled"] is False
    assert payload["external_services_enabled"] is False
    assert payload["persistence_enabled"] is False
    assert payload["production_connector_enabled"] is False
    assert payload["measurement_engine_execution_enabled"] is False


def test_deferred_workflow_routes_are_absent() -> None:
    application = create_app()
    paths = _route_paths(application)
    for route in _DEFERRED_WORKFLOW_ROUTES:
        assert route not in paths
    assert "/health" in paths
    assert "/version" in paths
