"""OpenAPI contract inspection tests for P11 service hardening."""

from __future__ import annotations

import json
from typing import Any, cast

from mip.service.app import WORKFLOW_ROUTE_PATHS, create_app

_EXPECTED_PATHS: dict[str, set[str]] = {
    "/health": {"get"},
    "/version": {"get"},
    "/advisory/cold-start": {"post"},
    "/readiness/assess": {"post"},
    "/calibration/map": {"post"},
    "/intake/overview": {"post"},
}

_POST_ROUTES = tuple(WORKFLOW_ROUTE_PATHS)

_FORBIDDEN_PATH_FRAGMENTS = (
    "/llm",
    "/auth",
    "/upload",
    "/ingest",
    "/openai",
    "/anthropic",
    "/ollama",
    "/persist",
    "/connector",
)


def _openapi() -> dict[str, object]:
    schema = create_app().openapi()
    assert isinstance(schema, dict)
    return schema


def _paths(schema: dict[str, object]) -> dict[str, Any]:
    paths = schema.get("paths")
    assert isinstance(paths, dict)
    return cast(dict[str, Any], paths)


def test_openapi_includes_expected_service_paths_and_methods() -> None:
    paths = _paths(_openapi())
    for path, methods in _EXPECTED_PATHS.items():
        assert path in paths, f"missing OpenAPI path: {path}"
        operation_methods = {method.lower() for method in paths[path]}
        assert methods <= operation_methods, f"{path} missing methods {methods - operation_methods}"


def test_openapi_has_no_unexpected_capability_routes() -> None:
    paths = _paths(_openapi())
    assert set(paths.keys()) == set(_EXPECTED_PATHS.keys())
    combined = json.dumps(paths).lower()
    for fragment in _FORBIDDEN_PATH_FRAGMENTS:
        assert fragment not in combined


def test_openapi_post_routes_have_request_and_response_schemas() -> None:
    paths = _paths(_openapi())
    for route in _POST_ROUTES:
        post = paths[route]["post"]
        assert isinstance(post, dict)
        request_body = post.get("requestBody")
        assert isinstance(request_body, dict)
        json_content = request_body["content"]["application/json"]
        assert "schema" in json_content
        responses = post.get("responses")
        assert isinstance(responses, dict)
        success = responses.get("200") or responses.get("201")
        assert isinstance(success, dict)
        response_json = success["content"]["application/json"]
        assert "schema" in response_json


def test_openapi_get_routes_have_response_schemas() -> None:
    paths = _paths(_openapi())
    for path in ("/health", "/version"):
        get_op = paths[path]["get"]
        assert isinstance(get_op, dict)
        responses = get_op.get("responses")
        assert isinstance(responses, dict)
        success = responses["200"]
        assert "schema" in success["content"]["application/json"]


def test_openapi_route_summaries_are_present() -> None:
    paths = _paths(_openapi())
    for path, methods in _EXPECTED_PATHS.items():
        for method in methods:
            operation = paths[path][method]
            assert isinstance(operation, dict)
            summary = operation.get("summary")
            assert isinstance(summary, str)
            assert summary.strip()
