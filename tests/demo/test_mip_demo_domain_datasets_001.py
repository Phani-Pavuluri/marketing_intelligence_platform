"""Tests for MIP demo domain datasets (SaaS subscriptions v1)."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any, cast

_FIXTURE = Path("data/demo/domain_fixtures/saas_subscriptions/v1")
_DOC = Path("docs/demo/MIP_DEMO_DOMAIN_DATASETS_001.md")
_SUMMARY = Path("docs/demo/archives/MIP_DEMO_DOMAIN_DATASETS_001_summary.json")

_REQUIRED_FILES = (
    "README.md",
    "manifest.json",
    "raw_spend_week_dma_channel.csv",
    "raw_kpi_week_dma.csv",
    "controls_week_dma.csv",
    "geo_metadata_dma.csv",
    "mmm_weekly_dma_panel.csv",
    "geox_design_weekly_dma_panel.csv",
    "calibration_signals.json",
    "sample_questions.json",
    "expected_answer_behavior.json",
    "lifecycle_walkthrough.json",
)

_FORBIDDEN_CLAIMS = (
    "ROI",
    "ROAS",
    "lift",
    "incrementality",
    "channel contribution",
    "budget recommendation",
    "budget reallocation plan",
    "GeoX assignment",
    "GeoX readout",
    "causal claim",
)

_TRUE_FLAGS = (
    "demo_domain_datasets_created",
    "saas_subscriptions_fixture_created",
    "raw_spend_week_dma_channel_created",
    "raw_kpi_week_dma_created",
    "controls_week_dma_created",
    "geo_metadata_dma_created",
    "mmm_weekly_dma_panel_created",
    "geox_design_weekly_dma_panel_created",
    "calibration_signals_created",
    "sample_questions_created",
    "expected_answer_behavior_created",
    "lifecycle_walkthrough_created",
    "canonical_mmm_ready_panel_created",
    "canonical_geox_ready_panel_created",
    "grain_compatibility_represented",
    "readiness_questions_supported",
    "budget_planning_guardrail_questions_supported",
    "geox_readiness_questions_supported",
    "roi_recommendation_claims_blocked",
    "mmm_export_dependency_recorded",
)

_FALSE_FLAGS = (
    "mmm_fitting_implemented",
    "mmm_export_adapter_implemented",
    "channel_roi_computation_implemented",
    "channel_roas_computation_implemented",
    "incremental_contribution_computation_implemented",
    "budget_optimizer_implemented",  # forbidden / not implemented boundary
    "budget_recommendation_generated",
    "geox_assignment_implemented",
    "geox_lift_readout_implemented",
    "calibration_signal_runtime_ingestion_implemented",
    "llm_provider_execution_implemented",
    "prompt_execution_implemented",
    "ui_demo_implemented",
)


def _load_csv(name: str) -> list[dict[str, str]]:
    with (_FIXTURE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _load_json(name: str) -> dict[str, Any]:
    payload = json.loads((_FIXTURE / name).read_text(encoding="utf-8"))
    return cast(dict[str, Any], payload)


def test_all_expected_files_exist() -> None:
    assert _FIXTURE.is_dir()
    for name in _REQUIRED_FILES:
        assert (_FIXTURE / name).is_file(), name
    assert _DOC.is_file()
    assert _SUMMARY.is_file()


def test_manifest_is_valid_json() -> None:
    manifest = _load_json("manifest.json")
    assert manifest["domain"] == "saas_subscriptions"
    assert manifest["fixture_version"] == "v1"
    assert manifest["geo_grain"] == "DMA"
    assert manifest["time_grain"] == "WEEK"
    assert manifest["primary_kpi"] == "paid_conversions"
    assert manifest["secondary_kpi"] == "arr"
    assert manifest["channels"] == ["Search", "Meta", "YouTube"]


def test_sample_questions_json_valid() -> None:
    payload = _load_json("sample_questions.json")
    questions = cast(list[dict[str, Any]], payload["questions"])
    assert len(questions) >= 8
    categories = {item["category"] for item in questions}
    for required in (
        "mmm_readiness",
        "geox_readiness",
        "grain_compatibility",
        "budget_planning_guardrail",
        "calibration_context",
        "data_missingness",
    ):
        assert required in categories


def test_expected_answer_behavior_json_valid() -> None:
    payload = _load_json("expected_answer_behavior.json")
    behaviors = cast(list[dict[str, Any]], payload["behaviors"])
    assert len(behaviors) >= 8
    for item in behaviors:
        assert "question_id" in item
        assert "allowed_answer_summary" in item
        assert "cannot_say" in item
        assert "blocked_claims" in item
        assert "next_required_artifact" in item


def test_lifecycle_walkthrough_json_valid() -> None:
    payload = _load_json("lifecycle_walkthrough.json")
    steps = cast(list[dict[str, Any]], payload["steps"])
    assert len(steps) == 10
    ids = [step["step_id"] for step in steps]
    assert ids[0].startswith("1_")
    assert ids[4].startswith("5_")
    assert ids[5].startswith("6_")
    assert ids[9].startswith("10_")


def test_calibration_signals_json_valid() -> None:
    payload = _load_json("calibration_signals.json")
    signals = cast(list[dict[str, Any]], payload["signals"])
    assert len(signals) >= 1
    signal = signals[0]
    for key in (
        "signal_id",
        "source_type",
        "channel",
        "geo_scope",
        "time_window",
        "metric",
        "effect_estimate",
        "standard_error",
        "freshness_status",
        "compatibility_status",
        "demo_fixture_only",
        "allowed_claims",
        "forbidden_claims",
    ):
        assert key in signal
    assert signal["demo_fixture_only"] is True


def test_raw_spend_has_week_dma_channel_uniqueness() -> None:
    rows = _load_csv("raw_spend_week_dma_channel.csv")
    keys = [(r["week_start"], r["dma_code"], r["channel"]) for r in rows]
    assert len(keys) == len(set(keys))
    assert set(r["channel"] for r in rows) == {"Search", "Meta", "YouTube"}


def test_raw_kpi_has_week_dma_uniqueness() -> None:
    rows = _load_csv("raw_kpi_week_dma.csv")
    keys = [(r["week_start"], r["dma_code"]) for r in rows]
    assert len(keys) == len(set(keys))
    for required in ("paid_conversions", "arr", "dma_name"):
        assert required in rows[0]


def test_mmm_panel_has_week_dma_uniqueness() -> None:
    rows = _load_csv("mmm_weekly_dma_panel.csv")
    keys = [(r["week_start"], r["dma_code"]) for r in rows]
    assert len(keys) == len(set(keys))


def test_geox_panel_has_week_dma_uniqueness() -> None:
    rows = _load_csv("geox_design_weekly_dma_panel.csv")
    keys = [(r["week_start"], r["dma_code"]) for r in rows]
    assert len(keys) == len(set(keys))


def test_kpi_once_per_week_dma_in_mmm_panel() -> None:
    rows = _load_csv("mmm_weekly_dma_panel.csv")
    counts = Counter((r["week_start"], r["dma_code"]) for r in rows)
    assert all(count == 1 for count in counts.values())
    assert all(r["paid_conversions"].isdigit() for r in rows)


def test_mmm_panel_has_wide_channel_spend_columns() -> None:
    rows = _load_csv("mmm_weekly_dma_panel.csv")
    headers = set(rows[0].keys())
    for col in (
        "search_spend",
        "meta_spend",
        "youtube_spend",
        "search_impressions",
        "meta_impressions",
        "youtube_impressions",
        "promo_flag",
        "holiday_flag",
        "launch_flag",
        "competitor_event_flag",
        "region",
        "population",
        "eligible",
    ):
        assert col in headers


def test_geox_panel_required_columns_and_periods() -> None:
    rows = _load_csv("geox_design_weekly_dma_panel.csv")
    headers = set(rows[0].keys())
    for col in (
        "primary_kpi",
        "meta_spend",
        "total_spend",
        "eligible",
        "region",
        "population",
        "period",
    ):
        assert col in headers
    assert set(r["period"] for r in rows) == {"pre", "test_candidate"}


def test_forbidden_claims_present_in_manifest_and_expected_behavior() -> None:
    manifest = _load_json("manifest.json")
    forbidden = set(cast(list[str], manifest["forbidden_claims"]))
    for claim in _FORBIDDEN_CLAIMS:
        assert claim in forbidden
    behaviors = cast(
        list[dict[str, Any]],
        _load_json("expected_answer_behavior.json")["behaviors"],
    )
    joined = " ".join(
        " ".join(cast(list[str], item.get("blocked_claims", []))) for item in behaviors
    ).lower()
    assert "roi" in joined
    assert "budget" in joined


def test_roi_roas_budget_recommendation_blocked() -> None:
    behaviors = cast(
        list[dict[str, Any]],
        _load_json("expected_answer_behavior.json")["behaviors"],
    )
    budget = next(
        item
        for item in behaviors
        if item["question_id"] == "budget_planning_guardrail_1"
    )
    blocked = " ".join(cast(list[str], budget["blocked_claims"])).lower()
    assert "roi" in blocked
    assert "roas" in blocked
    assert "budget shift recommendation" in blocked
    lifecycle = cast(
        list[dict[str, Any]],
        _load_json("lifecycle_walkthrough.json")["steps"],
    )
    step5 = lifecycle[4]
    step6 = lifecycle[5]
    assert step5["blocked"] is True
    assert step6["blocked"] is True


def test_lifecycle_includes_full_story() -> None:
    steps = cast(
        list[dict[str, Any]],
        _load_json("lifecycle_walkthrough.json")["steps"],
    )
    titles = " ".join(str(step["title"]).lower() for step in steps)
    assert "raw" in titles or "grain" in titles
    assert "mmm readiness" in titles
    assert "channel roi" in titles
    assert "budget" in titles
    assert "geox readiness" in titles
    assert steps[0]["available_now"] is True
    assert steps[1]["available_now"] is True
    assert steps[2]["available_now"] is True
    assert steps[3]["available_now"] is True
    assert steps[4]["blocked"] is True
    assert steps[5]["blocked"] is True
    assert steps[6]["available_now"] is True
    assert steps[7]["blocked"] is True
    assert steps[8]["fixture_backed"] is True
    assert steps[9]["available_now"] is True


def test_no_treatment_control_assignment_in_geox_fixture() -> None:
    rows = _load_csv("geox_design_weekly_dma_panel.csv")
    headers = {h.lower() for h in rows[0].keys()}
    for forbidden in ("treatment", "control", "assignment", "lift", "readout"):
        assert forbidden not in headers
        assert all(forbidden not in part for h in headers for part in h.split("_"))


def test_no_lift_readout_in_geox_fixture() -> None:
    text = (_FIXTURE / "geox_design_weekly_dma_panel.csv").read_text(encoding="utf-8")
    header = text.splitlines()[0].lower()
    assert "lift" not in header
    assert "readout" not in header
    assert "treatment" not in header
    assert "control" not in header
    assert "assignment" not in header


def test_summary_json_true_false_flags() -> None:
    summary = cast(dict[str, Any], json.loads(_SUMMARY.read_text(encoding="utf-8")))
    for key in _TRUE_FLAGS:
        assert summary[key] is True, key
    for key in _FALSE_FLAGS:
        assert summary[key] is False, key
    assert summary["recommended_next_artifact"] == (
        "MIP_MMM_LLM_RESPONSE_VERIFIER_AUDIT_001"
    )


def test_docs_mention_mmm_export_dependency_and_blocked_path() -> None:
    content = _DOC.read_text(encoding="utf-8")
    lowered = content.lower()
    assert "MMM-EXPORT-001" in content
    assert "MMM-EXPORT-002" in content
    assert "MMM-EXPORT-003" in content
    assert "export adapter" in lowered
    assert "roi" in lowered
    assert "blocked" in lowered
    assert "recommendation" in lowered
    assert "MIP_MMM_LLM_RESPONSE_VERIFIER_AUDIT_001" in content
