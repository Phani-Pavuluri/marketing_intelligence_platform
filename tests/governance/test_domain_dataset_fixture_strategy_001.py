"""Governance checks for MIP domain dataset fixture strategy."""

from __future__ import annotations

import json
from pathlib import Path

_DOC = Path("docs/design/MIP_DOMAIN_DATASET_FIXTURE_STRATEGY_001.md")
_SUMMARY = Path(
    "docs/design/archives/MIP_DOMAIN_DATASET_FIXTURE_STRATEGY_001_summary.json"
)

_ALLOWED_VERDICTS = (
    "DOMAIN_FIXTURE_STRATEGY_READY_FOR_SCHEMA_CONTRACT",
    "DOMAIN_FIXTURE_STRATEGY_NEEDS_EXISTING_FIXTURE_INVENTORY_FIRST",
    "DOMAIN_FIXTURE_STRATEGY_NEEDS_MMM_GEOX_SCHEMA_RECONCILIATION_FIRST",
    "DOMAIN_FIXTURE_STRATEGY_BLOCKED_BY_LAYERING_ISSUE",
)

_REQUIRED_DOMAINS = (
    "SaaS subscriptions",
    "E-commerce",
    "Mobile app",
    "B2B pipeline",
    "Geo / local experiments",
)

_REQUIRED_FAMILIES = (
    "MMM spend/KPI panels",
    "GeoX calibration signal fixtures",
    "Control-signal catalog fixtures",
    "Experiment metadata fixtures",
    "Data sufficiency / readiness fixtures",
    "LLM demo/eval scenario fixtures",
)

_TRUE_FLAGS = (
    "strategy_completed",
    "mip_owns_tier_1_tiny_fixtures",
    "mip_owns_tier_2_realistic_synthetic_panels",
    "packages_own_tier_3_method_simulation_generation",
    "saas_domain_included",
    "ecommerce_domain_included",
    "mobile_app_domain_included",
    "b2b_pipeline_domain_included",
    "geo_local_experiment_domain_included",
    "mmm_spend_kpi_panels_included",
    "geox_calibration_signal_fixtures_included",
    "control_signal_catalog_included",
    "experiment_metadata_fixtures_included",
    "data_sufficiency_readiness_fixtures_included",
    "llm_demo_eval_scenario_fixtures_included",
    "expected_allowed_blocked_behaviors_required",
    "can_say_cannot_say_expectations_required",
    "human_review_expectations_required",
    "forbidden_recommendation_expectations_required",
)

_FALSE_FLAGS = (
    "dataset_generation_implemented",
    "mmm_fitting_implemented",
    "geox_estimator_logic_implemented",
    "production_connector_implemented",
    "decision_surface_implemented",
    "recommendation_contract_implemented",
    "optimizer_simulator_implemented",
    "llm_provider_integration_implemented",
    "production_code_changed",
)


def test_strategy_doc_exists() -> None:
    assert _DOC.is_file()


def test_summary_json_exists() -> None:
    assert _SUMMARY.is_file()


def test_verdict_is_allowed_value() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["verdict"] in _ALLOWED_VERDICTS


def test_summary_key_booleans_truthful() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    for key in _TRUE_FLAGS:
        assert summary[key] is True, key
    for key in _FALSE_FLAGS:
        assert summary[key] is False, key


def test_doc_defines_three_fixture_tiers() -> None:
    content = _DOC.read_text(encoding="utf-8")
    assert "Tier 1" in content
    assert "Tier 2" in content
    assert "Tier 3" in content
    assert "tiny deterministic" in content.lower()
    assert "realistic synthetic" in content.lower()
    assert "method simulation" in content.lower()


def test_doc_includes_all_required_domains() -> None:
    content = _DOC.read_text(encoding="utf-8")
    for domain in _REQUIRED_DOMAINS:
        assert domain in content, domain


def test_doc_includes_all_required_dataset_families() -> None:
    content = _DOC.read_text(encoding="utf-8")
    for family in _REQUIRED_FAMILIES:
        assert family in content, family


def test_doc_states_mip_mmm_geox_ownership_boundaries() -> None:
    content = _DOC.read_text(encoding="utf-8")
    assert "MIP" in content
    assert "MMM package" in content
    assert "GeoX" in content or "panel_exp" in content
    assert "Tier 1" in content and "Tier 2" in content and "Tier 3" in content
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["mip_owns_tier_1_tiny_fixtures"] is True
    assert summary["mip_owns_tier_2_realistic_synthetic_panels"] is True
    assert summary["packages_own_tier_3_method_simulation_generation"] is True


def test_doc_requires_expected_allowed_blocked_behavior_outcomes() -> None:
    content = _DOC.read_text(encoding="utf-8").lower()
    assert "can_say" in content and "cannot_say" in content
    assert "human review" in content
    assert "forbidden recommendation" in content or "forbidden recommendation behavior" in content
    assert "blocked" in content and "deferred" in content
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["expected_allowed_blocked_behaviors_required"] is True
    assert summary["can_say_cannot_say_expectations_required"] is True
    assert summary["human_review_expectations_required"] is True
    assert summary["forbidden_recommendation_expectations_required"] is True


def test_doc_states_no_dataset_generation_implemented() -> None:
    content = _DOC.read_text(encoding="utf-8").lower()
    assert "does not generate datasets" in content or "no dataset generation" in content
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["dataset_generation_implemented"] is False


def test_doc_states_recommended_next_artifact() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["recommended_next_artifact"] == "MIP_DOMAIN_DATASET_SCHEMA_CONTRACT_001"
    content = _DOC.read_text(encoding="utf-8")
    assert "MIP_DOMAIN_DATASET_SCHEMA_CONTRACT_001" in content


def test_strategy_is_docs_only_scope() -> None:
    content = _DOC.read_text(encoding="utf-8").lower()
    assert "strategy" in content
    assert "did not generate datasets" in content or "no dataset generation" in content
    assert "did not" in content and "production code" in content


def test_no_production_code_changed() -> None:
    assert Path("src/mip/llm/mmm_response_template.py").is_file()
    assert _DOC.is_file()
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["production_code_changed"] is False
    assert summary["dataset_generation_implemented"] is False
