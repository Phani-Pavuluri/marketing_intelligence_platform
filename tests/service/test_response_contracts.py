"""Response shape contract tests for P11 service hardening."""

from __future__ import annotations

import json

from fastapi.testclient import TestClient

from mip.service.app import WORKFLOW_ROUTE_PATHS, create_app

_GOVERNANCE_FIELDS = {
    "mode",
    "advisory_only",
    "causal_decision_support",
    "roi_claims_allowed",
    "optimized_budget_claims_allowed",
    "measurement_engine_execution",
    "llm_enabled",
    "external_services_enabled",
    "persistence_enabled",
    "production_connector_enabled",
}

_WORKFLOW_CASES = [
    (
        "/advisory/cold-start",
        {"sample_key": "dtc_skincare_ecommerce"},
        {
            "status",
            "evidence_mode",
            "claim_types",
            "channel_hypotheses",
            "warnings",
            "blocking_reasons",
            "allowed_next_steps",
            "blocked_next_steps",
            "governance",
        },
    ),
    (
        "/readiness/assess",
        {"sample_key": "national_mmm_ready_geox_blocked"},
        {"sample_key", "reports", "warnings", "blocking_reasons", "governance"},
    ),
    (
        "/calibration/map",
        {"sample_key": "valid_governed_evidence"},
        {
            "status",
            "blocking_reasons",
            "missing_fields",
            "incompatible_fields",
            "warnings",
            "lineage",
            "allowed_next_steps",
            "blocked_next_steps",
            "governance",
        },
    ),
    (
        "/intake/overview",
        {"example_key": "national_mmm_diagnostic"},
        {
            "label",
            "business_question",
            "workflow_kind",
            "recommended_path",
            "status",
            "why_this_path",
            "why_other_paths_blocked",
            "required_next_inputs",
            "warnings",
            "blocking_reasons",
            "allowed_next_steps",
            "blocked_next_steps",
            "governance",
        },
    ),
]


def _client() -> TestClient:
    return TestClient(create_app())


def test_health_response_contract() -> None:
    payload = _client().get("/health").json()
    for field in (
        "status",
        "service",
        "mode",
        "llm_enabled",
        "external_services_enabled",
        "persistence_enabled",
        "production_connector_enabled",
        "measurement_engine_execution_enabled",
    ):
        assert field in payload
    assert payload["status"] == "ok"
    assert payload["mode"] == "deterministic"
    assert payload["llm_enabled"] is False


def test_version_response_contract() -> None:
    payload = _client().get("/version").json()
    for field in (
        "service",
        "project",
        "package_version",
        "api_phase",
        "baseline_commit",
        "public_demo_url",
        "streamlit_entrypoint",
        "mode",
        "llm_enabled",
        "external_services_enabled",
        "persistence_enabled",
        "production_connector_enabled",
        "measurement_engine_execution_enabled",
    ):
        assert field in payload
    assert payload["api_phase"] == "P10b.1"
    assert payload["mode"] == "deterministic"


def test_workflow_responses_include_expected_top_level_fields() -> None:
    client = _client()
    for route, body, expected_fields in _WORKFLOW_CASES:
        payload = client.post(route, json=body).json()
        assert expected_fields <= set(payload.keys()), f"{route} missing fields"


def test_workflow_governance_block_is_complete() -> None:
    client = _client()
    for route in WORKFLOW_ROUTE_PATHS:
        payload = client.post(route, json=_body_for_route(route)).json()
        governance = payload["governance"]
        assert _GOVERNANCE_FIELDS <= set(governance.keys())
        assert governance["llm_enabled"] is False
        assert governance["measurement_engine_execution"] is False


def test_workflow_responses_do_not_include_raw_row_fields() -> None:
    client = _client()
    forbidden_keys = {"rows", "raw_rows", "dataframe", "records"}
    for route in WORKFLOW_ROUTE_PATHS:
        payload = client.post(route, json=_body_for_route(route)).json()
        assert forbidden_keys.isdisjoint(payload.keys())
        combined = json.dumps(payload).lower()
        assert "raw row" not in combined


def test_deterministic_sample_requests_remain_stable() -> None:
    client = _client()
    advisory_a = client.post(
        "/advisory/cold-start",
        json={"sample_key": "dtc_skincare_ecommerce"},
    ).json()
    advisory_b = client.post(
        "/advisory/cold-start",
        json={"sample_key": "dtc_skincare_ecommerce"},
    ).json()
    assert advisory_a["status"] == advisory_b["status"]
    assert advisory_a["evidence_mode"] == advisory_b["evidence_mode"]
    assert len(advisory_a["channel_hypotheses"]) == len(advisory_b["channel_hypotheses"])


def _body_for_route(route: str) -> dict[str, str]:
    mapping = {
        "/advisory/cold-start": {"sample_key": "dtc_skincare_ecommerce"},
        "/readiness/assess": {"sample_key": "national_mmm_ready_geox_blocked"},
        "/calibration/map": {"sample_key": "valid_governed_evidence"},
        "/intake/overview": {"example_key": "national_mmm_diagnostic"},
    }
    return mapping[route]
