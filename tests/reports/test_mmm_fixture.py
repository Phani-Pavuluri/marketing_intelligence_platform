"""Tests for MMM fixture governance reports."""

from datetime import date, timedelta

import pytest

from mip.reports.mmm_fixture import (
    MMMFixtureReport,
    assert_safe_mmm_fixture_report,
    build_mmm_fixture_report,
    format_mmm_fixture_disclaimer,
    mmm_fixture_report_sections,
)
from mip.workflows.intake import BusinessObjective, BusinessObjectiveType
from mip.workflows.orchestrator import WorkflowRunSummary, run_local_workflow


def _weekly_rows(count: int = 12) -> list[dict[str, object]]:
    return [
        {
            "date": (date(2025, 1, 1) + timedelta(days=7 * index)).isoformat(),
            "channel": "search",
            "spend": 100 + index,
            "conversions": 10 + index,
        }
        for index in range(count)
    ]


def _long_history_rows() -> list[dict[str, object]]:
    return [
        {
            "date": (date(2024, 1, 1) + timedelta(days=7 * index)).isoformat(),
            "spend": 100,
            "conversions": 10,
            "channel": "search" if index % 2 == 0 else "social",
            "geo": "us" if index % 2 == 0 else "uk",
        }
        for index in range(60)
    ]


def _run_summary(objective_type: str, records: list[dict[str, object]]) -> WorkflowRunSummary:
    return run_local_workflow(
        BusinessObjective(objective_type=BusinessObjectiveType(objective_type)),
        records,
    )


def test_mmm_fixture_report_builds_from_conversion_roi_summary() -> None:
    summary = _run_summary("conversion_roi", _long_history_rows())
    report = build_mmm_fixture_report(summary)
    assert report is not None
    assert report.objective_type == "conversion_roi"
    assert report.adapter_output_id.startswith("adapter:mmm:")


def test_report_includes_config_adapter_surface_and_trust_sections() -> None:
    summary = _run_summary("conversion_roi", _long_history_rows())
    report = build_mmm_fixture_report(summary)
    assert report is not None
    sections = mmm_fixture_report_sections(report)
    assert sections["config_draft_status"]
    assert sections["adapter_input_status"]
    assert sections["adapter_output_status"]
    assert sections["decision_surface_id"]
    assert sections["trust_report_confidence_tier"]


def test_report_is_diagnostic_placeholder_only() -> None:
    summary = _run_summary("conversion_roi", _long_history_rows())
    report = build_mmm_fixture_report(summary)
    assert report is not None
    assert "adapter_fixture_placeholder_only" in report.placeholder_labels
    assert "not_model_execution" in report.placeholder_labels
    assert "not_decision_ready" in report.placeholder_labels
    assert report.decision_surface_type == "diagnostic_curve"


def test_report_does_not_include_forbidden_claims() -> None:
    summary = _run_summary("conversion_roi", _long_history_rows())
    report = build_mmm_fixture_report(summary)
    assert report is not None
    combined = "\n".join(
        [
            report.placeholder_explanation,
            report.disclaimer,
            *report.placeholder_labels,
            *report.missing_production_requirements,
        ]
    ).lower()
    assert "actual roi" not in combined
    assert "incremental lift" not in combined
    assert "budget recommendation" not in combined
    assert "not decision-ready" in combined or "not decision ready" in combined


def test_blocked_or_non_mmm_workflows_return_no_report() -> None:
    awareness_summary = _run_summary("awareness", _weekly_rows(12))
    assert build_mmm_fixture_report(awareness_summary) is None

    experiment_summary = _run_summary(
        "experiment_design",
        [
            {
                "date": (date(2024, 1, 1) + timedelta(days=7 * index)).isoformat(),
                "geo": "dma_a" if index % 2 == 0 else "dma_b",
                "outcome": 100 + index,
                "spend": 50,
            }
            for index in range(60)
        ],
    )
    assert build_mmm_fixture_report(experiment_summary) is None


def test_assert_safe_rejects_production_ready_claim() -> None:
    report = MMMFixtureReport(
        objective_type="conversion_roi",
        config_draft_status="draftable",
        production_eligible=False,
        adapter_input_status="validated",
        adapter_output_status="completed",
        source_config_marker="marker",
        adapter_output_id="adapter:mmm:marker",
        decision_surface_id="adapter:mmm:marker",
        decision_surface_type="diagnostic_curve",
        decision_surface_certification_status="draft",
        trust_report_confidence_tier="blocked",
        trust_report_warnings=[],
        trust_report_unsupported_claims=[],
        trust_report_assumptions=[],
        placeholder_labels=["not_decision_ready"],
        missing_production_requirements=["example"],
        placeholder_explanation="This output is production-ready",
        disclaimer=format_mmm_fixture_disclaimer(),
    )
    with pytest.raises(ValueError, match="production-ready"):
        assert_safe_mmm_fixture_report(report)


def test_public_imports() -> None:
    from mip.reports import (
        MMMFixtureReport,
        build_mmm_fixture_report,
        format_mmm_fixture_disclaimer,
        mmm_fixture_report_sections,
    )

    assert callable(build_mmm_fixture_report)
    assert callable(mmm_fixture_report_sections)
    assert callable(format_mmm_fixture_disclaimer)
    assert MMMFixtureReport is not None
