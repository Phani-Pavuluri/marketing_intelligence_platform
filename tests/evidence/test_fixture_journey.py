"""Focused acceptance tests for the fixture-only journey resolver."""

from collections.abc import Mapping
from typing import Any

from mip.evidence.fixture_journey import (
    FixtureJourneyFailure,
    FixtureJourneyResult,
    resolve_fixture_journey,
)


def as_list(value: object) -> list[object]:
    """Narrow an object to a list for fixture builders."""
    assert isinstance(value, list)
    return value


COMMIT = "fixture-commit-r01"


def as_dict(value: object) -> dict[str, Any]:
    """Narrow an object to a string-keyed mapping for fixture builders."""
    assert isinstance(value, Mapping)
    return dict(value)


def base_readout(**overrides: object) -> dict[str, object]:
    readout: dict[str, object] = {
        "readout_id": "readout-r01",
        "readout_version": "1.0",
        "artifact_version": "1.0",
        "producer_package_version": "1.0",
        "producer_commit": COMMIT,
        "experiment_id": "experiment-1",
        "fixture_id": "fixture-1",
        "dataset_version": "dataset-1",
        "truth_version": "truth-1",
        "kpi": "revenue",
        "kpi_units": "currency",
        "estimand": "ATT",
        "effect_scale": "absolute",
        "channel": "channel",
        "tactic": "tactic",
        "geography_scope": "fixture_geos",
        "geo_grain": "geo",
        "time_window": "pre-post",
        "pre_period": "pre",
        "post_period": "post",
        "freshness_status": "fresh",
        "uncertainty_available": True,
        "method_family": "SCM",
        "instrument_id": "instrument",
        "design_type": "geo_experiment",
        "feasibility_status": "feasible",
        "method_status": "governed",
        "readout_status": "success",
        "handoff_eligibility_status": "eligible_for_compatibility_evaluation",
        "warnings": [],
        "blocked_reasons": [],
        "failure_reasons": [],
        "lineage": {
            "fixture_id": "fixture-1",
            "dataset_version": "dataset-1",
            "truth_version": "truth-1",
        },
        "provenance": {
            "source_repo": "panel_exp",
            "source_commit": COMMIT,
            "producer_package_version": "1.0",
            "created_by": "contract",
        },
        "replay_metadata": {"assignment_seed": 1, "replay_version": "1.0"},
        "authorization_flags": {
            "production_inference": False,
            "assignment": False,
            "causal_readout": False,
            "calibration_signal_export": False,
            "experiment_evidence_export": False,
            "trust_report": False,
            "decision_surface": False,
            "recommendation_contract": False,
            "llm_decisioning": False,
            "budget_optimization": False,
        },
    }
    readout.update(overrides)
    return readout


def base_compat(**overrides: object) -> dict[str, object]:
    compat: dict[str, object] = {
        "source": {
            "source_readout_id": "readout-r01",
            "source_readout_version": "1.0",
            "handoff_eligible": True,
            "kpi_id": "revenue",
            "unit": "currency",
            "estimand_id": "ATT",
            "effect_scale": "absolute",
            "channel_id": "channel",
            "geography": "fixture_geos",
            "grain": "geo",
            "evidence_window_start": "2026-01-01T00:00:00+00:00",
            "evidence_window_end": "2026-02-01T00:00:00+00:00",
            "observed_at": "2026-02-02T00:00:00+00:00",
            "fresh_through": "2026-03-01T00:00:00+00:00",
            "uncertainty_status": "available",
            "method_family": "SCM",
            "instrument_identity": "instrument",
            "method_status": "governed",
        },
        "model_context": {
            "model_id": "model-1",
            "run_id": "run-1",
            "model_family": "ridge",
            "kpi_id": "revenue",
            "unit": "currency",
            "estimand_id": "ATT",
            "effect_scale": "absolute",
            "channel_id": "channel",
            "geography": "fixture_geos",
            "grain": "geo",
            "model_window_start": "2026-01-01T00:00:00+00:00",
            "model_window_end": "2026-02-01T00:00:00+00:00",
            "evaluated_at": "2026-02-15T00:00:00+00:00",
            "uncertainty_status": "available",
        },
        "lineage": {
            "evidence_artifact_id": "evidence-1",
            "model_artifact_id": "model-1",
            "configuration_hash": "config-1",
            "panel_id": "panel-1",
            "evaluation_id": "eval-1",
        },
        "compatibility_state": "compatible",
        "reason_codes": [],
        "warnings": [],
        "blockers": [],
        "freshness_decision": "fresh",
        "uncertainty_decision": "compatible",
        "time_overlap_decision": "exact",
    }
    compat.update(overrides)
    return compat


def base_plan(role: str) -> dict[str, object]:
    return {
        "schema_version": "mmm_simulation_plan_v1",
        "plan_id": f"plan-{role.lower()}",
        "role": role,
        "spend_unit": "currency",
        "evaluation_time_window": "pre-post",
        "items": [{"channel_id": "channel", "spend": 10.0, "spend_unit": "currency"}],
        "total_spend": 10.0,
    }


def base_sim(**overrides: object) -> dict[str, object]:
    sim: dict[str, object] = {
        "schema_version": "mmm_public_simulation_export_v1",
        "export_id": "export-1",
        "run_id": "run-1",
        "created_at": "2026-02-16T00:00:00+00:00",
        "baseline_plan": base_plan("BASELINE"),
        "candidate_plan": base_plan("CANDIDATE"),
        "comparison": {
            "comparison_id": "cmp-1",
            "run_id": "run-1",
            "baseline_plan_id": "plan-baseline",
            "candidate_plan_id": "plan-candidate",
            "status": "SUCCEEDED",
            "technical_summary": "ok",
            "metrics": [
                {
                    "metric_id": "m1",
                    "estimand": "ATT",
                    "aggregation_scope": "full-panel",
                    "baseline_mu": 10.0,
                    "candidate_mu": 12.0,
                    "delta_mu": 2.0,
                    "unit": "currency",
                    "uncertainty": {"status": "AVAILABLE", "artifact_reference": "unc-1"},
                }
            ],
            "range_evaluations": [
                {
                    "range_record_id": "rg-1",
                    "channel_id": "channel",
                    "baseline_relation": "WITHIN_SUPPORTED_RANGE",
                    "candidate_relation": "WITHIN_SUPPORTED_RANGE",
                    "extrapolation": "NONE",
                    "blocked": False,
                }
            ],
        },
        "supported_range_evidence_id": "sr-1",
        "status": "SUCCEEDED",
        "producer_package_name": "mmm",
        "artifact_kind": "MMMPublicSimulationExport",
        "artifact_schema_version": "mmm_public_simulation_export_v1",
        "artifact_id": "mmm_public_simulation:run-1",
        "run_manifest": {"run_id": "run-1", "status": "SUCCEEDED"},
    }
    sim.update(overrides)
    return sim


def base_inputs(**overrides: object) -> dict[str, object]:
    inputs: dict[str, object] = {
        "schema_version": "mip_fixture_journey_input_v1",
        "geox_readout": base_readout(),
        "mmm_compat": base_compat(),
        "mmm_sim": base_sim(),
    }
    inputs.update(overrides)
    return inputs


def resolve(inputs: Mapping[str, object]) -> FixtureJourneyResult:
    result = resolve_fixture_journey(inputs)
    assert isinstance(result, FixtureJourneyResult), f"expected result, got failure: {result}"
    return result


def test_f01_success_single_row() -> None:
    result = resolve(base_inputs())
    assert result.matched_rows == ("r01_success",)
    assert result.report_status == "evidence_ready_human_review_required"
    assert result.headline.row_id == "r01_success"
    assert result.permitted_claims == ("may:delta_mu_with_uncertainty_in_scope",)
    assert "mustnot:causal_certainty" in result.prohibited_claims
    assert "mustnot:approval_or_execution" in result.prohibited_claims
    assert result.human_review_required is True


def test_f02_success_with_warning() -> None:
    compat = base_compat(
        compatibility_state="compatible_with_warning",
        reason_codes=["uncertainty_unavailable"],
        warnings=[{"reason_code": "uncertainty_unavailable", "rationale": "uncertainty thin"}],
    )
    sim = base_sim()
    comparison = as_dict(sim["comparison"])
    sim = {**sim, "comparison": comparison, "status": "SUCCEEDED_WITH_LIMITATIONS",
           "limitation_references": ["limit-1"],
           "run_manifest": {"run_id": "run-1", "status": "SUCCEEDED_WITH_LIMITATIONS"}}
    result = resolve(base_inputs(mmm_compat=compat, mmm_sim=sim))
    assert result.matched_rows == ("r02_success_with_warning",)
    assert result.report_status == "evidence_ready_with_warning_human_review_required"
    assert "mustnot:warning_immaterial" in result.prohibited_claims
    assert result.warnings == ("limitation:limit-1", "uncertainty thin")


def test_f03_stale_compat() -> None:
    compat = base_compat(
        compatibility_state="stale",
        reason_codes=["evidence_stale"],
        freshness_decision="stale",
    )
    result = resolve(base_inputs(mmm_compat=compat))
    assert result.matched_rows == ("r03_stale",)
    assert result.report_status == "stale_evidence"
    assert "mustnot:stale_as_current" in result.prohibited_claims


def test_f03b_readout_stale_standalone() -> None:
    readout = base_readout(readout_status="stale", freshness_status="stale")
    result = resolve(
        {"schema_version": "mip_fixture_journey_input_v1", "geox_readout": readout}
    )
    assert result.matched_rows == ("r03_stale",)
    assert result.report_status == "stale_evidence"


def test_f04_incompatible() -> None:
    compat = base_compat(
        compatibility_state="incompatible",
        reason_codes=["kpi_mismatch"],
    )
    result = resolve(base_inputs(mmm_compat=compat, mmm_sim=None))
    assert result.matched_rows == ("r04_incompatible",)
    assert result.report_status == "incompatible_evidence"
    assert "mustnot:replacement_compatibility" in result.prohibited_claims
    assert "compat:kpi_mismatch" in result.issues


def test_f05_blocked_handoff_readout() -> None:
    readout = base_readout(
        readout_status="blocked",
        handoff_eligibility_status="blocked_for_handoff",
        blocked_reasons=["governed_blocker"],
    )
    result = resolve(
        {"schema_version": "mip_fixture_journey_input_v1", "geox_readout": readout}
    )
    assert result.matched_rows == ("r05_blocked_handoff",)
    assert result.report_status == "blocked_evidence"
    assert "mustnot:simulation_can_proceed" in result.prohibited_claims


def test_f05b_compat_handoff_not_eligible_blocked() -> None:
    source = as_dict(base_compat()["source"])
    source["handoff_eligible"] = False
    compat = base_compat(
        source=source,
        compatibility_state="blocked",
        reason_codes=["handoff_not_eligible"],
        blockers=[{"reason_code": "handoff_not_eligible", "rationale": "not eligible"}],
    )
    result = resolve(base_inputs(mmm_compat=compat))
    assert result.matched_rows == ("r05_blocked_handoff",)
    assert result.report_status == "blocked_evidence"


def test_f06_blocked_simulation() -> None:
    sim = base_sim(
        status="BLOCKED",
        comparison={**as_dict(base_sim()["comparison"]), "status": "BLOCKED"},
        failure_packet={
            "schema_version": "mmm_mip_failure_v1",
            "failure_id": "f-1",
            "created_at": "2026-02-16T00:00:00+00:00",
            "code": "UNSUPPORTED_EXTRAPOLATION",
            "run_id": "run-1",
        },
        blocking_references=["block-1"],
        run_manifest={"run_id": "run-1", "status": "BLOCKED"},
    )
    result = resolve(base_inputs(mmm_sim=sim))
    assert result.matched_rows == ("r06_blocked_simulation",)
    assert result.report_status == "blocked_evidence"
    assert "sim:UNSUPPORTED_EXTRAPOLATION" in result.issues


def test_f07_failed_producer() -> None:
    sim = base_sim(
        status="FAILED",
        comparison={**as_dict(base_sim()["comparison"]), "status": "FAILED"},
        failure_packet={
            "schema_version": "mmm_mip_failure_v1",
            "failure_id": "f-1",
            "created_at": "2026-02-16T00:00:00+00:00",
            "code": "MODEL_INSTABILITY",
            "run_id": "run-1",
        },
        run_manifest={"run_id": "run-1", "status": "FAILED"},
    )
    result = resolve(base_inputs(mmm_compat=None, mmm_sim=sim))
    assert "r07_producer_failure" in result.matched_rows
    assert result.headline.row_id == "r07_producer_failure"
    assert result.report_status == "producer_failure"
    assert "mustnot:result_from_failure" in result.prohibited_claims


def test_f08_diagnostic_only_static_path() -> None:
    inputs = base_inputs(
        context={
            "static_labels": ["static_export_file_only", "diagnostic_only", "not_decision_ready"]
        }
    )
    result = resolve({**inputs, "mmm_compat": None, "mmm_sim": None})
    assert result.matched_rows == ("r08_diagnostic_only",)
    assert result.report_status == "diagnostic_only"
    assert "mustnot:planning_conclusion" in result.prohibited_claims


def test_f09_research_only_static_path() -> None:
    inputs = base_inputs(context={"static_labels": ["static_export_file_only", "research_only"]})
    result = resolve({**inputs, "mmm_compat": None, "mmm_sim": None})
    assert result.matched_rows == ("r09_research_only",)
    assert result.report_status == "research_only"
    assert "mustnot:decision_authority" in result.prohibited_claims


def test_f08b_compat_mark_cofires_blocked() -> None:
    source = as_dict(base_compat()["source"])
    source["method_status"] = "diagnostic_only"
    compat = base_compat(
        source=source,
        compatibility_state="blocked",
        reason_codes=["method_status_not_governed"],
        blockers=[{"reason_code": "method_status_not_governed", "rationale": "not governed"}],
    )
    result = resolve(base_inputs(mmm_compat=compat))
    assert set(result.matched_rows) == {"r05_blocked_handoff", "r08_diagnostic_only"}
    assert result.headline.row_id == "r05_blocked_handoff"
    assert result.report_status == "blocked_evidence"
    assert "mark:diagnostic_only" in result.issues
    assert "mustnot:planning_conclusion" in result.prohibited_claims


def test_f10_unavailable_uncertainty() -> None:
    sim = base_sim()
    comparison = as_dict(sim["comparison"])
    metric = as_dict(as_list(comparison["metrics"])[0])
    metric["uncertainty"] = {"status": "UNAVAILABLE"}
    comparison["metrics"] = [metric]
    sim = {**sim, "comparison": comparison}
    result = resolve(base_inputs(mmm_sim=sim))
    assert result.matched_rows == ("r10_unavailable_uncertainty",)
    assert result.report_status == "evidence_with_unavailable_uncertainty"
    assert "mustnot:uncertainty_interval" in result.prohibited_claims


def test_f11_range_restriction() -> None:
    sim = base_sim()
    comparison = as_dict(sim["comparison"])
    evaluation = as_dict(as_list(comparison["range_evaluations"])[0])
    evaluation["candidate_relation"] = "OUTSIDE_OBSERVED_BUT_SUPPORTED"
    evaluation["extrapolation"] = "LIMITED_EXTRAPOLATION"
    comparison["range_evaluations"] = [evaluation]
    sim = {**sim, "comparison": comparison, "limitation_references": ["range-limit-1"],
           "status": "SUCCEEDED_WITH_LIMITATIONS",
           "run_manifest": {"run_id": "run-1", "status": "SUCCEEDED_WITH_LIMITATIONS"}}
    result = resolve(base_inputs(mmm_sim=sim))
    assert result.matched_rows == ("r11_range_restriction",)
    assert result.report_status == "evidence_with_range_restriction"
    assert "mustnot:beyond_range" in result.prohibited_claims


def test_f12_supersession_names_present_artifact() -> None:
    inputs = base_inputs(
        context={"supersedes": {"artifact_id": "sim:run-1", "source_commit": "new-commit"}}
    )
    result = resolve(inputs)
    assert "r12_conflict_superseded" in result.matched_rows
    assert result.headline.row_id == "r12_conflict_superseded"
    assert result.report_status == "conflicting_or_superseded_evidence"
    assert "mustnot:preferred_result" in result.prohibited_claims


def test_f12b_lineage_conflict_differing_commits() -> None:
    provenance = as_dict(base_readout()["provenance"])
    provenance["source_commit"] = "other-commit"
    readout = base_readout(provenance=provenance, producer_commit="other-commit")
    source = as_dict(base_compat()["source"])
    source["source_producer_commit"] = "third-commit"
    compat = base_compat(source=source)
    result = resolve(base_inputs(geox_readout=readout, mmm_compat=compat))
    assert "r12_conflict_superseded" in result.matched_rows
    assert result.headline.row_id == "r12_conflict_superseded"


def test_f12c_contradictory_terminals_return_conflict_not_failure() -> None:
    sim = base_sim(
        status="FAILED",
        comparison={**as_dict(base_sim()["comparison"]), "status": "FAILED"},
        failure_packet={
            "schema_version": "mmm_mip_failure_v1",
            "failure_id": "f-1",
            "created_at": "2026-02-16T00:00:00+00:00",
            "code": "MODEL_INSTABILITY",
            "run_id": "run-1",
        },
        run_manifest={"run_id": "run-1", "status": "FAILED"},
    )
    result = resolve(base_inputs(mmm_sim=sim))
    assert isinstance(result, FixtureJourneyResult)
    assert set(result.matched_rows) == {"r07_producer_failure", "r12_conflict_superseded"}
    assert result.headline.row_id == "r12_conflict_superseded"


def test_safety_unknown_version() -> None:
    result = resolve_fixture_journey({**base_inputs(), "schema_version": "v9"})
    assert isinstance(result, FixtureJourneyFailure)
    assert result.code == "unknown_version"


def test_safety_missing_field() -> None:
    readout = base_readout()
    del readout["readout_status"]
    result = resolve_fixture_journey(base_inputs(geox_readout=readout))
    assert isinstance(result, FixtureJourneyFailure)
    assert result.code == "missing_fields"
    assert "readout_status" in result.detail


def test_safety_unmapped_literal() -> None:
    result = resolve_fixture_journey(base_inputs(geox_readout=base_readout(readout_status="bogus")))
    assert isinstance(result, FixtureJourneyFailure)
    assert result.code == "unmapped_literal"


def test_safety_unsupported_consumption() -> None:
    inputs = base_inputs(context={"consumption": "experiment_evidence_candidate"})
    result = resolve_fixture_journey(inputs)
    assert isinstance(result, FixtureJourneyFailure)
    assert result.code == "unsupported_consumption"


def test_safety_invalid_invariants_compatible_with_warnings() -> None:
    compat = base_compat(
        reason_codes=["uncertainty_unavailable"],
        warnings=[{"reason_code": "uncertainty_unavailable", "rationale": "thin"}],
    )
    result = resolve_fixture_journey(base_inputs(mmm_compat=compat))
    assert isinstance(result, FixtureJourneyFailure)
    assert result.code == "invalid_invariants"


def test_safety_ineligible_only_handoff_not_explainable() -> None:
    readout = base_readout(handoff_eligibility_status="ineligible_for_calibration_handoff")
    result = resolve_fixture_journey(
        {"schema_version": "mip_fixture_journey_input_v1", "geox_readout": readout}
    )
    assert isinstance(result, FixtureJourneyFailure)
    assert result.code == "no_explainable_journey"


def test_collision_failure_plus_lineage_conflict() -> None:
    provenance = as_dict(base_readout()["provenance"])
    provenance["source_commit"] = "other-commit"
    readout = base_readout(provenance=provenance, producer_commit="other-commit")
    sim = base_sim(
        status="FAILED",
        comparison={**as_dict(base_sim()["comparison"]), "status": "FAILED"},
        failure_packet={
            "schema_version": "mmm_mip_failure_v1",
            "failure_id": "f-1",
            "created_at": "2026-02-16T00:00:00+00:00",
            "code": "MODEL_INSTABILITY",
            "run_id": "run-1",
        },
        run_manifest={"run_id": "run-1", "status": "FAILED"},
    )
    result = resolve(base_inputs(geox_readout=readout, mmm_sim=sim))
    assert result.headline.row_id == "r12_conflict_superseded"
    assert "r07_producer_failure" in result.matched_rows
    assert "identity:conflict" in result.issues
    assert "sim:MODEL_INSTABILITY" in result.issues


def test_collision_stale_plus_warning_headlines_stale() -> None:
    readout = base_readout(
        readout_status="stale", freshness_status="stale", warnings=["late-data"]
    )
    compat = base_compat(
        compatibility_state="stale",
        reason_codes=["evidence_stale"],
        freshness_decision="stale",
    )
    result = resolve(base_inputs(geox_readout=readout, mmm_compat=compat))
    assert result.headline.row_id == "r03_stale"
    assert result.warnings == ("late-data",)


def test_collision_warned_plus_unavailable_headlines_uncertainty() -> None:
    compat = base_compat(
        compatibility_state="compatible_with_warning",
        reason_codes=["uncertainty_unavailable"],
        warnings=[{"reason_code": "uncertainty_unavailable", "rationale": "thin"}],
    )
    sim = base_sim()
    comparison = as_dict(sim["comparison"])
    metric = as_dict(as_list(comparison["metrics"])[0])
    metric["uncertainty"] = {"status": "UNAVAILABLE"}
    comparison["metrics"] = [metric]
    sim = {**sim, "comparison": comparison}
    result = resolve(base_inputs(mmm_compat=compat, mmm_sim=sim))
    assert result.headline.row_id == "r10_unavailable_uncertainty"
    assert "thin" in result.warnings


def test_collision_research_only_plus_warning_zero_comparison_claims() -> None:
    inputs = base_inputs(
        context={"static_labels": ["static_export_file_only", "research_only"]}
    )
    compat = base_compat(
        compatibility_state="compatible_with_warning",
        reason_codes=["uncertainty_unavailable"],
        warnings=[{"reason_code": "uncertainty_unavailable", "rationale": "thin"}],
    )
    result = resolve({**inputs, "mmm_compat": compat})
    assert result.headline.row_id == "r09_research_only"
    assert "may:delta_mu_with_uncertainty_in_scope" not in result.permitted_claims
    assert "may:bounded_comparison_with_warning" not in result.permitted_claims
    assert "thin" in result.warnings


def test_resolver_is_pure_and_never_raises_on_producer_data() -> None:
    first = resolve_fixture_journey(base_inputs())
    second = resolve_fixture_journey(base_inputs())
    assert first == second
    garbage: dict[str, object] = {"schema_version": "mip_fixture_journey_input_v1",
                                   "geox_readout": {"readout_status": 42}}
    result = resolve_fixture_journey(garbage)
    assert isinstance(result, FixtureJourneyFailure)


def test_no_default_success_without_explainable_row() -> None:
    readout = base_readout(handoff_eligibility_status="ineligible_for_calibration_handoff")
    compat = base_compat(
        compatibility_state="incompatible",
        reason_codes=["kpi_mismatch"],
    )
    result = resolve(base_inputs(geox_readout=readout, mmm_compat=compat, mmm_sim=None))
    assert "r01_success" not in result.matched_rows
    assert "r02_success_with_warning" not in result.matched_rows


def test_result_types() -> None:
    assert isinstance(resolve(base_inputs()), FixtureJourneyResult)
    assert isinstance(
        resolve_fixture_journey({"schema_version": "wrong"}), FixtureJourneyFailure
    )


def test_fjr001_unknown_geox_version_rejected() -> None:
    result = resolve_fixture_journey(base_inputs(geox_readout=base_readout(readout_version="2.0")))
    assert isinstance(result, FixtureJourneyFailure)
    assert result.code == "unknown_version"


def test_fjr001_wrong_sim_package_kind_rejected() -> None:
    sim = base_sim(producer_package_name="other", artifact_kind="OtherExport")
    result = resolve_fixture_journey(base_inputs(mmm_sim=sim))
    assert isinstance(result, FixtureJourneyFailure)
    assert result.code == "unmapped_literal"


def test_fjr001_missing_authorization_flags_rejected() -> None:
    readout = base_readout(authorization_flags={"production_inference": False})
    result = resolve_fixture_journey(base_inputs(geox_readout=readout))
    assert isinstance(result, FixtureJourneyFailure)
    assert result.code == "missing_fields"


def test_fjr001_non_boolean_authorization_flag_rejected() -> None:
    flags = dict(as_dict(base_readout()["authorization_flags"]))
    flags["assignment"] = "no"
    result = resolve_fixture_journey(
        base_inputs(geox_readout=base_readout(authorization_flags=flags))
    )
    assert isinstance(result, FixtureJourneyFailure)
    assert result.code == "invalid_invariants"


def test_fjr001_true_authorization_flag_rejected() -> None:
    flags = dict(as_dict(base_readout()["authorization_flags"]))
    flags["causal_readout"] = True
    result = resolve_fixture_journey(
        base_inputs(geox_readout=base_readout(authorization_flags=flags))
    )
    assert isinstance(result, FixtureJourneyFailure)
    assert result.code == "invalid_invariants"


def test_fjr002_null_comparison_rejected() -> None:
    result = resolve_fixture_journey(base_inputs(mmm_sim=base_sim(comparison=None)))
    assert isinstance(result, FixtureJourneyFailure)
    assert result.code == "invalid_invariants"


def test_fjr002_missing_comparison_rejected() -> None:
    sim = base_sim()
    del sim["comparison"]
    result = resolve_fixture_journey(base_inputs(mmm_sim=sim))
    assert isinstance(result, FixtureJourneyFailure)
    assert result.code == "missing_fields"


def test_fjr002_missing_run_manifest_rejected() -> None:
    sim = base_sim()
    del sim["run_manifest"]
    result = resolve_fixture_journey(base_inputs(mmm_sim=sim))
    assert isinstance(result, FixtureJourneyFailure)
    assert result.code == "missing_fields"


def test_fjr002_mismatched_run_manifest_rejected() -> None:
    sim = base_sim(run_manifest={"run_id": "run-1", "status": "FAILED"})
    result = resolve_fixture_journey(base_inputs(mmm_sim=sim))
    assert isinstance(result, FixtureJourneyFailure)
    assert result.code == "invalid_invariants"


def test_fjr002_missing_artifact_id_rejected() -> None:
    sim = base_sim()
    del sim["artifact_id"]
    result = resolve_fixture_journey(base_inputs(mmm_sim=sim))
    assert isinstance(result, FixtureJourneyFailure)
    assert result.code == "missing_fields"


def test_fjr002_mismatched_artifact_id_rejected() -> None:
    result = resolve_fixture_journey(
        base_inputs(mmm_sim=base_sim(artifact_id="mmm_public_simulation:other"))
    )
    assert isinstance(result, FixtureJourneyFailure)
    assert result.code == "invalid_invariants"


def test_fjr003_nan_spend_rejected() -> None:
    import math as _math

    bad_plan = base_plan("BASELINE")
    bad_plan["items"] = [{"channel_id": "channel", "spend": _math.nan, "spend_unit": "currency"}]
    bad_plan["total_spend"] = _math.nan
    result = resolve_fixture_journey(base_inputs(mmm_sim=base_sim(baseline_plan=bad_plan)))
    assert isinstance(result, FixtureJourneyFailure)
    assert result.code == "invalid_invariants"


def test_fjr003_infinite_delta_rejected() -> None:
    import math as _math2

    sim = base_sim()
    comparison = as_dict(sim["comparison"])
    metric = as_dict(as_list(comparison["metrics"])[0])
    metric["baseline_mu"] = 10.0
    metric["candidate_mu"] = _math2.inf
    metric["delta_mu"] = _math2.inf
    comparison["metrics"] = [metric]
    sim = {**sim, "comparison": comparison}
    result = resolve_fixture_journey(base_inputs(mmm_sim=sim))
    assert isinstance(result, FixtureJourneyFailure)
    assert result.code == "invalid_invariants"


def test_fjr003_nan_delta_trio_rejected() -> None:
    import math as _math3

    sim = base_sim()
    comparison = as_dict(sim["comparison"])
    metric = as_dict(as_list(comparison["metrics"])[0])
    metric["baseline_mu"] = _math3.nan
    metric["candidate_mu"] = _math3.nan
    metric["delta_mu"] = _math3.nan
    comparison["metrics"] = [metric]
    sim = {**sim, "comparison": comparison}
    result = resolve_fixture_journey(base_inputs(mmm_sim=sim))
    assert isinstance(result, FixtureJourneyFailure)
    assert result.code == "invalid_invariants"


def test_fjr003_invalid_baseline_relation_rejected() -> None:
    sim = base_sim()
    comparison = as_dict(sim["comparison"])
    evaluation = as_dict(as_list(comparison["range_evaluations"])[0])
    evaluation["baseline_relation"] = "EVERYWHERE"
    comparison["range_evaluations"] = [evaluation]
    sim = {**sim, "comparison": comparison}
    result = resolve_fixture_journey(base_inputs(mmm_sim=sim))
    assert isinstance(result, FixtureJourneyFailure)
    assert result.code == "unmapped_literal"


def test_fjr003_non_boolean_blocked_rejected() -> None:
    sim = base_sim()
    comparison = as_dict(sim["comparison"])
    evaluation = as_dict(as_list(comparison["range_evaluations"])[0])
    evaluation["blocked"] = "yes"
    comparison["range_evaluations"] = [evaluation]
    sim = {**sim, "comparison": comparison}
    result = resolve_fixture_journey(base_inputs(mmm_sim=sim))
    assert isinstance(result, FixtureJourneyFailure)
    assert result.code == "invalid_invariants"


def test_fjr003_swapped_plan_roles_rejected() -> None:
    sim = base_sim(baseline_plan=base_plan("CANDIDATE"), candidate_plan=base_plan("BASELINE"))
    result = resolve_fixture_journey(base_inputs(mmm_sim=sim))
    assert isinstance(result, FixtureJourneyFailure)
    assert result.code == "invalid_invariants"


def test_fjr003_mismatched_comparison_plan_ids_rejected() -> None:
    sim = base_sim()
    comparison = as_dict(sim["comparison"])
    comparison["baseline_plan_id"] = "plan-elsewhere"
    sim = {**sim, "comparison": comparison}
    result = resolve_fixture_journey(base_inputs(mmm_sim=sim))
    assert isinstance(result, FixtureJourneyFailure)
    assert result.code == "invalid_invariants"


def test_fjr003_mismatched_comparison_run_id_rejected() -> None:
    sim = base_sim()
    comparison = as_dict(sim["comparison"])
    comparison["run_id"] = "run-elsewhere"
    sim = {**sim, "comparison": comparison}
    result = resolve_fixture_journey(base_inputs(mmm_sim=sim))
    assert isinstance(result, FixtureJourneyFailure)
    assert result.code == "invalid_invariants"
