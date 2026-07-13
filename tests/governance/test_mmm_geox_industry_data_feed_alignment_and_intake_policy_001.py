"""Governance checks for MMM/GeoX industry data-feed alignment intake policy."""

from __future__ import annotations

import json
from pathlib import Path

_DOC = Path(
    "docs/intake/MIP_MMM_GEOX_INDUSTRY_DATA_FEED_ALIGNMENT_AND_INTAKE_POLICY_001.md"
)
_SUMMARY = Path(
    "docs/intake/archives/"
    "MIP_MMM_GEOX_INDUSTRY_DATA_FEED_ALIGNMENT_AND_INTAKE_POLICY_001_summary.json"
)

_ARTIFACT_ID = "MIP_MMM_GEOX_INDUSTRY_DATA_FEED_ALIGNMENT_AND_INTAKE_POLICY_001"

_TRUE_FLAGS = (
    "industry_data_feed_alignment_completed",
    "canonical_mmm_ready_intake_defined",
    "canonical_geox_ready_intake_defined",
    "raw_source_inspection_layer_defined",
    "normalized_engine_ready_layer_defined",
    "grain_comparability_policy_defined",
    "same_grain_join_policy_defined",
    "partial_overlap_warning_policy_defined",
    "mapping_required_for_different_grains",
    "roll_up_only_policy_defined",
    "roll_down_blocked",
    "user_confirmation_required_for_unclear_grain",
    "user_provided_crosswalk_required",
    "global_crosswalk_fetching_rejected",
    "user_facing_data_requirement_messages_defined",
)

_FALSE_FLAGS = (
    "dataset_generation_implemented",
    "raw_source_normalization_runtime_implemented",
    "automatic_global_geo_dictionary_fetching_implemented",
    "fuzzy_geo_resolution_as_source_of_truth_implemented",
    "roll_down_allocation_implemented",
    "production_connector_implemented",
    "mmm_fitting_implemented",
    "geox_estimator_logic_implemented",
    "calibration_signal_runtime_changed",
    "decision_surface_generation_implemented",
    "trust_report_generation_implemented",
    "recommendation_contract_generation_implemented",
    "optimizer_simulator_implemented",
    "roi_roas_lift_incrementality_computation_implemented",
    "llm_provider_execution_implemented",
    "prompt_execution_implemented",
    "ui_demo_implemented",
    "production_code_changed",
)

_GRAIN_STATUSES = (
    "MATCHED_GRAIN",
    "SAME_GRAIN_PARTIAL_OVERLAP",
    "DIFFERENT_GRAIN_MAPPING_REQUIRED",
    "DIFFERENT_GRAIN_MAPPING_AVAILABLE",
    "UNKNOWN_GEO_COMPARABILITY",
    "BLOCKED_NO_MAPPING",
    "BLOCKED_UNSAFE_DISAGGREGATION",
    "USER_CONFIRMATION_REQUIRED",
)

_NON_GOALS = (
    "automatic global geo dictionary fetching",
    "fuzzy geo resolution as source of truth",
    "roll-down allocation",
    "dataset generation",
    "production connector",
    "mmm fitting",
    "geox estimator logic",
    "calibrationsignal runtime change",
    "decisionsurface",
    "trustreport",
    "recommendationcontract",
    "optimizer",
    "simulator",
    "roi",
    "roas",
    "lift",
    "incrementality",
    "llm provider",
    "prompt execution",
    "ui implementation",
)


def test_policy_doc_exists() -> None:
    assert _DOC.is_file()


def test_summary_json_exists() -> None:
    assert _SUMMARY.is_file()


def test_artifact_id_present() -> None:
    content = _DOC.read_text(encoding="utf-8")
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert _ARTIFACT_ID in content
    assert summary["artifact_id"] == _ARTIFACT_ID


def test_summary_flags_truthful() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    for key in _TRUE_FLAGS:
        assert summary[key] is True, key
    for key in _FALSE_FLAGS:
        assert summary[key] is False, key
    assert summary["recommended_next_artifact"] == "MIP_DEMO_DOMAIN_DATASETS_001"


def test_industry_alignment_finding_present() -> None:
    content = _DOC.read_text(encoding="utf-8").lower()
    assert "industry alignment finding" in content
    assert "no single universal industry schema" in content
    assert "messy raw sources for inspection" in content
    assert "normalized canonical panels" in content


def test_canonical_mmm_and_geox_intake_defined() -> None:
    content = _DOC.read_text(encoding="utf-8").lower()
    assert "canonical mmm-ready intake" in content
    assert "canonical geox-ready intake" in content
    assert "time × geo" in content or "time x geo" in content
    assert "once per time-geo" in content
    assert "search_spend" in content
    assert "meta_spend" in content
    assert "eligible" in content


def test_raw_source_inspection_layer_defined() -> None:
    content = _DOC.read_text(encoding="utf-8").lower()
    assert "raw source inspection" in content
    assert "not directly model-ready unless normalized" in content
    assert "mapping / crosswalk" in content or "mapping/crosswalk" in content


def test_grain_comparability_statuses_present() -> None:
    content = _DOC.read_text(encoding="utf-8")
    for status in _GRAIN_STATUSES:
        assert status in content, status


def test_mapping_and_roll_up_roll_down_policy() -> None:
    content = _DOC.read_text(encoding="utf-8").lower()
    assert "user-provided mapping" in content or "user-provided crosswalk" in content
    assert "mapping/crosswalk must exist" in content or "mapping must exist" in content
    assert "roll-up only" in content or "roll up only" in content
    assert "roll-down" in content
    assert "blocked" in content
    assert "high confidence alone is not enough" in content


def test_user_confirmation_and_no_global_crosswalk() -> None:
    content = _DOC.read_text(encoding="utf-8").lower()
    assert "user confirmation" in content
    assert "must not infer global mappings" in content or (
        "global crosswalk fetching" in content and "rejected" in content
    )


def test_user_facing_intake_explanation() -> None:
    content = _DOC.read_text(encoding="utf-8").lower()
    assert "what i found" in content
    assert "what is missing or ambiguous" in content
    assert "what i can safely do next" in content
    assert "what is blocked" in content
    assert "what to upload next" in content
    assert "market-to-state mapping" in content or "mapping table" in content


def test_non_goals_present() -> None:
    content = _DOC.read_text(encoding="utf-8").lower()
    for phrase in _NON_GOALS:
        assert phrase in content, phrase


def test_recommended_next_artifact() -> None:
    content = _DOC.read_text(encoding="utf-8")
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert "MIP_DEMO_DOMAIN_DATASETS_001" in content
    assert summary["recommended_next_artifact"] == "MIP_DEMO_DOMAIN_DATASETS_001"
    assert (
        summary["deferred_normalization_artifact"]
        == "MIP_SOURCE_NORMALIZATION_FROM_RAW_MARKETING_DATA_001"
    )


def test_no_production_code_changed() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["production_code_changed"] is False
    assert summary["dataset_generation_implemented"] is False
    assert summary["raw_source_normalization_runtime_implemented"] is False
