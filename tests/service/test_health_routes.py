"""Route tests for P10a health/version metadata endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient

from mip.service.app import WORKFLOW_ROUTE_PATHS, create_app
from mip.service.metadata import PUBLIC_DEMO_URL

_WORKFLOW_ROUTES = WORKFLOW_ROUTE_PATHS


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
    assert payload["api_phase"] == "P10b"
    assert payload["baseline_commit"] == "3af1d45"
    assert payload["public_demo_url"] == PUBLIC_DEMO_URL
    assert payload["streamlit_entrypoint"] == "app/streamlit_app.py"
    assert payload["mode"] == "deterministic"
    assert payload["llm_enabled"] is False
    assert payload["external_services_enabled"] is False
    assert payload["persistence_enabled"] is False
    assert payload["production_connector_enabled"] is False
    assert payload["measurement_engine_execution_enabled"] is False


def test_workflow_routes_are_registered() -> None:
    application = create_app()
    paths = _route_paths(application)
    for route in _WORKFLOW_ROUTES:
        assert route in paths
    assert "/health" in paths
    assert "/version" in paths
