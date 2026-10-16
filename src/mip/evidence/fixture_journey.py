"""Fixture-only resolver for the MIP planning-evidence journey (synthetic).

Pure, deterministic, zero-dependency evaluation over producer-shaped
fixture inputs. Producer analytical values stay opaque; only shape,
provenance, and declared producer decisions are evaluated. Identity-first:
every simultaneous issue is retained, the headline selects status and next
evidence only, and permitted claims respect every matched restriction.
Existing live consumers are untouched; nothing here executes packages,
touches real data, or grants analytical authority.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

SCHEMA_VERSION = "mip_fixture_journey_input_v1"

READOUT_STATUSES = frozenset(
    {"success", "warning", "stale", "incompatible", "blocked", "failed"}
)
HANDOFF_STATUSES = frozenset(
    {
        "eligible_for_compatibility_evaluation",
        "ineligible_for_calibration_handoff",
        "blocked_for_handoff",
    }
)
FRESHNESS_STATUSES = frozenset({"fresh", "stale", "unknown"})
METHOD_STATUSES = frozenset({"governed", "research_only", "diagnostic_only", "blocked"})
COMPAT_STATES = frozenset(
    {"compatible", "compatible_with_warning", "stale", "incompatible", "blocked"}
)
SIM_STATUSES = frozenset({"SUCCEEDED", "SUCCEEDED_WITH_LIMITATIONS", "BLOCKED", "FAILED"})
SIM_UNCERTAINTY = frozenset({"AVAILABLE", "UNAVAILABLE", "RESEARCH_ONLY"})
RANGE_RELATIONS = frozenset(
    {
        "WITHIN_OBSERVED_RANGE",
        "WITHIN_SUPPORTED_RANGE",
        "AT_LOWER_BOUNDARY",
        "AT_UPPER_BOUNDARY",
        "OUTSIDE_OBSERVED_BUT_SUPPORTED",
        "OUTSIDE_SUPPORTED_RANGE",
        "UNKNOWN",
    }
)
EXTRAPOLATIONS = frozenset(
    {
        "NONE",
        "INTERPOLATION",
        "BOUNDARY",
        "LIMITED_EXTRAPOLATION",
        "UNSUPPORTED_EXTRAPOLATION",
        "UNKNOWN",
    }
)
REASON_CODES = frozenset(
    {
        "handoff_not_eligible",
        "method_status_not_governed",
        "kpi_mismatch",
        "unit_mismatch",
        "estimand_mismatch",
        "effect_scale_mismatch",
        "channel_mismatch",
        "geography_mismatch",
        "grain_mismatch",
        "time_window_no_overlap",
        "time_window_partial_overlap",
        "evidence_stale",
        "uncertainty_unavailable",
        "uncertainty_mismatch",
    }
)
CONSUMPTION_STATUSES = frozenset(
    {"diagnostic_context_only", "answerability_context_only", "blocked"}
)
STATIC_LABELS = frozenset(
    {
        "static_export_file_only",
        "not_live_engine_execution",
        "not_real_model_result",
        "diagnostic_only",
        "not_decision_ready",
        "research_only",
    }
)
FAILURE_CODES = frozenset(
    {
        "unknown_version",
        "missing_fields",
        "unmapped_literal",
        "unsupported_consumption",
        "invalid_invariants",
        "no_explainable_journey",
    }
)

ROW_IDS = (
    "r01_success",
    "r02_success_with_warning",
    "r03_stale",
    "r04_incompatible",
    "r05_blocked_handoff",
    "r06_blocked_simulation",
    "r07_producer_failure",
    "r08_diagnostic_only",
    "r09_research_only",
    "r10_unavailable_uncertainty",
    "r11_range_restriction",
    "r12_conflict_superseded",
)

REPORT_STATUSES = (
    "evidence_ready_human_review_required",
    "evidence_ready_with_warning_human_review_required",
    "stale_evidence",
    "incompatible_evidence",
    "blocked_evidence",
    "blocked_evidence",
    "producer_failure",
    "diagnostic_only",
    "research_only",
    "evidence_with_unavailable_uncertainty",
    "evidence_with_range_restriction",
    "conflicting_or_superseded_evidence",
)

PRECEDENCE = (
    "r12_conflict_superseded",
    "r07_producer_failure",
    "r05_blocked_handoff",
    "r06_blocked_simulation",
    "r04_incompatible",
    "r03_stale",
    "r08_diagnostic_only",
    "r09_research_only",
    "r10_unavailable_uncertainty",
    "r11_range_restriction",
    "r02_success_with_warning",
    "r01_success",
)

_MAY_DELTA = "may:delta_mu_with_uncertainty_in_scope"
_MAY_BOUNDED = "may:bounded_comparison_with_warning"
_MAY_STATE = "may:state_typed_evidence_state_and_next_evidence"
_NO_CERTAINTY = "mustnot:causal_certainty"
_NO_APPROVAL = "mustnot:approval_or_execution"

_ROW_STATUS = dict(zip(ROW_IDS, REPORT_STATUSES, strict=True))
_ROW_MAY: dict[str, tuple[str, ...]] = {
    "r01_success": (_MAY_DELTA,),
    "r02_success_with_warning": (_MAY_BOUNDED,),
    "r03_stale": (_MAY_STATE,),
    "r04_incompatible": (_MAY_STATE,),
    "r05_blocked_handoff": (_MAY_STATE,),
    "r06_blocked_simulation": (_MAY_STATE,),
    "r07_producer_failure": (_MAY_STATE,),
    "r08_diagnostic_only": (_MAY_STATE,),
    "r09_research_only": (_MAY_STATE,),
    "r10_unavailable_uncertainty": (_MAY_BOUNDED,),
    "r11_range_restriction": (_MAY_BOUNDED,),
    "r12_conflict_superseded": (_MAY_STATE,),
}
_ROW_MUSTNOT: dict[str, tuple[str, ...]] = {
    "r01_success": (_NO_CERTAINTY, _NO_APPROVAL),
    "r02_success_with_warning": (_NO_CERTAINTY, _NO_APPROVAL, "mustnot:warning_immaterial"),
    "r03_stale": (_NO_CERTAINTY, _NO_APPROVAL, "mustnot:stale_as_current"),
    "r04_incompatible": (_NO_CERTAINTY, _NO_APPROVAL, "mustnot:replacement_compatibility"),
    "r05_blocked_handoff": (_NO_CERTAINTY, _NO_APPROVAL, "mustnot:simulation_can_proceed"),
    "r06_blocked_simulation": (_NO_CERTAINTY, _NO_APPROVAL, "mustnot:simulation_can_proceed"),
    "r07_producer_failure": (_NO_CERTAINTY, _NO_APPROVAL, "mustnot:result_from_failure"),
    "r08_diagnostic_only": (_NO_CERTAINTY, _NO_APPROVAL, "mustnot:planning_conclusion"),
    "r09_research_only": (_NO_CERTAINTY, _NO_APPROVAL, "mustnot:decision_authority"),
    "r10_unavailable_uncertainty": (
        _NO_CERTAINTY,
        _NO_APPROVAL,
        "mustnot:uncertainty_interval",
    ),
    "r11_range_restriction": (_NO_CERTAINTY, _NO_APPROVAL, "mustnot:beyond_range"),
    "r12_conflict_superseded": (_NO_CERTAINTY, _NO_APPROVAL, "mustnot:preferred_result"),
}
_ROW_HEADLINE: dict[str, tuple[str, str]] = {
    "r01_success": ("comparison:success", "required human review"),
    "r02_success_with_warning": (
        "comparison:warning",
        "required human review with listed warnings",
    ),
    "r03_stale": ("freshness:stale", "fresh producer evidence"),
    "r04_incompatible": ("compat:incompatible", "compatible model context or experiment evidence"),
    "r05_blocked_handoff": ("handoff:blocked", "unblock handoff; no model comparison available"),
    "r06_blocked_simulation": ("sim:blocked", "producer-stated unblock reason"),
    "r07_producer_failure": ("producer:failed", "successful producer re-run"),
    "r08_diagnostic_only": ("mark:diagnostic_only", "decision-ready evidence"),
    "r09_research_only": ("mark:research_only", "governed decision-ready evidence"),
    "r10_unavailable_uncertainty": (
        "uncertainty:unavailable",
        "uncertainty evidence with reference",
    ),
    "r11_range_restriction": ("range:restricted", "in-range evidence or expanded support"),
    "r12_conflict_superseded": ("identity:conflict", "identity resolution or supersession record"),
}

_TOP_LEVEL_KEYS = frozenset({"schema_version", "geox_readout", "mmm_compat", "mmm_sim", "context"})
_COMPAT_OK_STATES = frozenset({"compatible", "compatible_with_warning"})
_SIM_OK_STATUSES = frozenset({"SUCCEEDED", "SUCCEEDED_WITH_LIMITATIONS"})
_ELIGIBLE_HANDOFF = "eligible_for_compatibility_evaluation"
_MARK_METHODS = frozenset({"diagnostic_only", "research_only"})

_READOUT_REQUIRED = (
    "readout_id",
    "readout_version",
    "artifact_version",
    "experiment_id",
    "fixture_id",
    "dataset_version",
    "truth_version",
    "kpi",
    "estimand",
    "effect_scale",
    "freshness_status",
    "uncertainty_available",
    "method_status",
    "readout_status",
    "handoff_eligibility_status",
    "warnings",
    "blocked_reasons",
    "failure_reasons",
    "lineage",
    "provenance",
    "replay_metadata",
    "authorization_flags",
)


@dataclass(frozen=True)
class FixtureJourneyFailure:
    """Typed admission failure; no row is explainable."""

    code: str
    detail: str


@dataclass(frozen=True)
class FixtureJourneyHeadline:
    """Deterministic headline: status selector and next evidence only."""

    row_id: str
    issue: str
    next_evidence: str


@dataclass(frozen=True)
class FixtureJourneyResult:
    """Resolved fixture journey with every simultaneous issue retained."""

    matched_rows: tuple[str, ...]
    report_status: str
    headline: FixtureJourneyHeadline
    issues: tuple[str, ...]
    warnings: tuple[str, ...]
    limitations: tuple[str, ...]
    permitted_claims: tuple[str, ...]
    prohibited_claims: tuple[str, ...]
    human_review_required: bool
    versions: dict[str, str] = field(default_factory=dict)
    lineage: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class _Readout:
    status: str
    handoff: str
    freshness: str
    method_status: str
    warnings: tuple[str, ...]
    blocked: tuple[str, ...]
    failures: tuple[str, ...]
    experiment_id: str
    commit: str
    uncertainty_available: bool


@dataclass(frozen=True)
class _Compat:
    state: str
    method_status: str
    handoff_eligible: bool
    reason_codes: tuple[str, ...]
    warnings_count: int
    blockers_count: int
    freshness: str
    uncertainty: str
    commit: str | None
    evidence_id: str
    warning_texts: tuple[str, ...]


@dataclass(frozen=True)
class _Sim:
    status: str
    uncertainty: str
    uncertainty_ref: str | None
    blocked_eval: bool
    restrictive_eval: bool
    restriction_desc: tuple[str, ...]
    limitation_refs: tuple[str, ...]
    blocking_refs: tuple[str, ...]
    failure_code: str | None
    failure_commit: str | None
    run_id: str
    artifact_id: str
    warning_texts: tuple[str, ...]


@dataclass(frozen=True)
class _Context:
    consumption: str | None
    static_labels: tuple[str, ...]
    supersedes_id: str | None
    supersedes_commit: str | None


@dataclass(frozen=True)
class _Bundle:
    readout: _Readout | None
    compat: _Compat | None
    sim: _Sim | None
    context: _Context


class _AdmissionFailure(Exception):
    """Internal admission signal; always converted to FixtureJourneyFailure."""

    def __init__(self, code: str, detail: str) -> None:
        super().__init__(detail)
        self.code = code
        self.detail = detail


def _fail(code: str, detail: str) -> _AdmissionFailure:
    if code not in FAILURE_CODES:
        code = "unmapped_literal"
    return _AdmissionFailure(code, detail)


def _get_str(data: Mapping[str, object], key: str, where: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value:
        raise _fail("missing_fields", f"{where}.{key} must be a non-empty string")
    return value


def _get_opt_str(data: Mapping[str, object], key: str) -> str | None:
    value = data.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise _fail("unmapped_literal", f"{key} must be a string")
    return value


def _get_bool(data: Mapping[str, object], key: str, where: str) -> bool:
    value = data.get(key)
    if not isinstance(value, bool):
        raise _fail("missing_fields", f"{where}.{key} must be a boolean")
    return value


def _get_str_list(data: Mapping[str, object], key: str, where: str) -> tuple[str, ...]:
    value = data.get(key)
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise _fail("missing_fields", f"{where}.{key} must be a list of strings")
    return tuple(value)


def _get_mapping(data: Mapping[str, object], key: str, where: str) -> Mapping[str, object]:
    value = data.get(key)
    if not isinstance(value, Mapping):
        raise _fail("missing_fields", f"{where}.{key} must be a mapping")
    return value


def _check_literal(value: str, allowed: frozenset[str], where: str) -> str:
    if value not in allowed:
        raise _fail("unmapped_literal", f"{where} value {value!r} is not a known literal")
    return value


def _admit_readout(data: Mapping[str, object]) -> _Readout:
    for key in _READOUT_REQUIRED:
        if key not in data:
            raise _fail("missing_fields", f"geox_readout.{key} is required")
    status = _check_literal(
        _get_str(data, "readout_status", "geox_readout"), READOUT_STATUSES, "readout_status"
    )
    handoff = _check_literal(
        _get_str(data, "handoff_eligibility_status", "geox_readout"), HANDOFF_STATUSES, "handoff"
    )
    freshness = _check_literal(
        _get_str(data, "freshness_status", "geox_readout"), FRESHNESS_STATUSES, "freshness_status"
    )
    method_status = _check_literal(
        _get_str(data, "method_status", "geox_readout"), METHOD_STATUSES, "method_status"
    )
    for key in (
        "readout_id",
        "readout_version",
        "artifact_version",
        "experiment_id",
        "fixture_id",
        "dataset_version",
        "truth_version",
        "kpi",
        "estimand",
        "effect_scale",
    ):
        _get_str(data, key, "geox_readout")
    uncertainty_available = _get_bool(data, "uncertainty_available", "geox_readout")
    warnings = _get_str_list(data, "warnings", "geox_readout")
    blocked = _get_str_list(data, "blocked_reasons", "geox_readout")
    failures = _get_str_list(data, "failure_reasons", "geox_readout")
    if status in {"blocked", "failed"} and not (blocked or failures):
        raise _fail(
            "invalid_invariants", "blocked/failed readout requires reasons"
        )
    lineage = _get_mapping(data, "lineage", "geox_readout")
    for key in ("fixture_id", "dataset_version", "truth_version"):
        if key not in lineage:
            raise _fail("missing_fields", f"geox_readout.lineage.{key} is required")
    provenance = _get_mapping(data, "provenance", "geox_readout")
    for key in ("source_repo", "source_commit", "producer_package_version", "created_by"):
        if key not in provenance:
            raise _fail("missing_fields", f"geox_readout.provenance.{key} is required")
    replay = _get_mapping(data, "replay_metadata", "geox_readout")
    for key in ("assignment_seed", "replay_version"):
        if key not in replay:
            raise _fail("missing_fields", f"geox_readout.replay_metadata.{key} is required")
    flags = _get_mapping(data, "authorization_flags", "geox_readout")
    if any(value is True for value in flags.values()):
        raise _fail("unmapped_literal", "true production authorization flags are never admitted")
    commit_value = provenance.get("source_commit")
    commit = commit_value if isinstance(commit_value, str) else ""
    experiment_value = data.get("experiment_id")
    experiment_id = experiment_value if isinstance(experiment_value, str) else ""
    return _Readout(
        status=status,
        handoff=handoff,
        freshness=freshness,
        method_status=method_status,
        warnings=warnings,
        blocked=blocked,
        failures=failures,
        experiment_id=experiment_id,
        commit=commit,
        uncertainty_available=uncertainty_available,
    )


def _admit_compat_issue(item: object, where: str) -> str:
    if not isinstance(item, Mapping):
        raise _fail("missing_fields", f"{where} entries must be mappings")
    code_value = item.get("reason_code")
    if not isinstance(code_value, str) or code_value not in REASON_CODES:
        raise _fail("unmapped_literal", f"{where} reason_code is not a known code")
    rationale = item.get("rationale")
    if not isinstance(rationale, str) or not rationale:
        raise _fail("missing_fields", f"{where} rationale is required")
    return code_value


def _admit_compat(data: Mapping[str, object]) -> _Compat:
    for key in ("source", "model_context", "lineage", "compatibility_state", "reason_codes"):
        if key not in data:
            raise _fail("missing_fields", f"mmm_compat.{key} is required")
    source = _get_mapping(data, "source", "mmm_compat")
    for key in (
        "source_readout_id",
        "source_readout_version",
        "handoff_eligible",
        "kpi_id",
        "unit",
        "estimand_id",
        "effect_scale",
        "channel_id",
        "geography",
        "grain",
        "evidence_window_start",
        "evidence_window_end",
        "observed_at",
        "fresh_through",
        "uncertainty_status",
        "method_family",
        "instrument_identity",
        "method_status",
    ):
        if key not in source:
            raise _fail("missing_fields", f"mmm_compat.source.{key} is required")
    if not isinstance(source.get("handoff_eligible"), bool):
        raise _fail("missing_fields", "mmm_compat.source.handoff_eligible must be a boolean")
    handoff_eligible = source["handoff_eligible"]
    assert isinstance(handoff_eligible, bool)
    source_uncertainty = source.get("uncertainty_status")
    if source_uncertainty not in {"available", "unavailable"}:
        raise _fail("unmapped_literal", "mmm_compat.source.uncertainty_status is not known")
    source_method = source.get("method_status")
    if source_method not in METHOD_STATUSES:
        raise _fail("unmapped_literal", "mmm_compat.source.method_status is not known")
    assert isinstance(source_method, str)
    model = _get_mapping(data, "model_context", "mmm_compat")
    for key in (
        "model_id",
        "run_id",
        "model_family",
        "kpi_id",
        "unit",
        "estimand_id",
        "effect_scale",
        "channel_id",
        "geography",
        "grain",
        "model_window_start",
        "model_window_end",
        "evaluated_at",
        "uncertainty_status",
    ):
        if key not in model:
            raise _fail("missing_fields", f"mmm_compat.model_context.{key} is required")
    lineage = _get_mapping(data, "lineage", "mmm_compat")
    for key in (
        "evidence_artifact_id",
        "model_artifact_id",
        "configuration_hash",
        "panel_id",
        "evaluation_id",
    ):
        if key not in lineage:
            raise _fail("missing_fields", f"mmm_compat.lineage.{key} is required")
    state_value = data.get("compatibility_state")
    if not isinstance(state_value, str) or state_value not in COMPAT_STATES:
        raise _fail("unmapped_literal", "mmm_compat.compatibility_state is not known")
    codes_value = data.get("reason_codes")
    if not isinstance(codes_value, list) or any(
        not isinstance(code, str) or code not in REASON_CODES for code in codes_value
    ):
        raise _fail("unmapped_literal", "mmm_compat.reason_codes holds an unknown code")
    if len(set(codes_value)) != len(codes_value):
        raise _fail("invalid_invariants", "mmm_compat.reason_codes must be unique")
    codes = tuple(codes_value)
    warnings_value = data.get("warnings", [])
    blockers_value = data.get("blockers", [])
    if not isinstance(warnings_value, list) or not isinstance(blockers_value, list):
        raise _fail("missing_fields", "mmm_compat.warnings/blockers must be lists")
    warning_codes = tuple(
        _admit_compat_issue(item, "mmm_compat.warnings") for item in warnings_value
    )
    blocker_codes = tuple(
        _admit_compat_issue(item, "mmm_compat.blockers") for item in blockers_value
    )
    if state_value == "compatible" and (codes or warning_codes or blocker_codes):
        raise _fail("invalid_invariants", "compatible results cannot contain warnings or blockers")
    if state_value == "compatible_with_warning" and (not warning_codes or blocker_codes):
        raise _fail("invalid_invariants", "warning results require warnings without blockers")
    if state_value == "stale" and ("evidence_stale" not in codes or blocker_codes):
        raise _fail("invalid_invariants", "stale results require stale evidence without blockers")
    if state_value == "incompatible" and (not codes or blocker_codes):
        raise _fail("invalid_invariants", "incompatible results require reasons without blockers")
    if state_value == "blocked" and not blocker_codes:
        raise _fail("invalid_invariants", "blocked results require typed blockers")
    freshness_value = data.get("freshness_decision", "fresh")
    if freshness_value not in {"fresh", "stale"}:
        raise _fail("unmapped_literal", "mmm_compat.freshness_decision is not known")
    assert isinstance(freshness_value, str)
    uncertainty_value = data.get("uncertainty_decision", "compatible")
    if uncertainty_value not in {"compatible", "unavailable", "mismatch"}:
        raise _fail("unmapped_literal", "mmm_compat.uncertainty_decision is not known")
    assert isinstance(uncertainty_value, str)
    commit_value = source.get("source_producer_commit")
    commit = commit_value if isinstance(commit_value, str) and commit_value else None
    evidence_value = lineage.get("evidence_artifact_id")
    evidence_id = evidence_value if isinstance(evidence_value, str) else ""
    warning_texts: list[str] = []
    for item in warnings_value:
        if isinstance(item, Mapping):
            rationale = item.get("rationale")
            if isinstance(rationale, str):
                warning_texts.append(rationale)
    return _Compat(
        state=state_value,
        method_status=source_method,
        handoff_eligible=handoff_eligible,
        reason_codes=codes,
        warnings_count=len(warning_codes),
        blockers_count=len(blocker_codes),
        freshness=freshness_value,
        uncertainty=uncertainty_value,
        commit=commit,
        evidence_id=evidence_id,
        warning_texts=tuple(warning_texts),
    )


def _admit_sim_uncertainty(data: Mapping[str, object], where: str) -> tuple[str, str | None]:
    status_value = data.get("status", "UNAVAILABLE")
    if not isinstance(status_value, str) or status_value not in SIM_UNCERTAINTY:
        raise _fail("unmapped_literal", f"{where}.status is not known")
    ref_value = data.get("artifact_reference")
    ref = ref_value if isinstance(ref_value, str) and ref_value else None
    if status_value == "AVAILABLE" and ref is None:
        raise _fail("invalid_invariants", f"{where} available uncertainty needs a reference")
    return status_value, ref


def _admit_sim(data: Mapping[str, object]) -> _Sim:
    for key in (
        "schema_version",
        "export_id",
        "run_id",
        "created_at",
        "baseline_plan",
        "candidate_plan",
        "comparison",
        "supported_range_evidence_id",
        "status",
    ):
        if key not in data:
            raise _fail("missing_fields", f"mmm_sim.{key} is required")
    if data.get("schema_version") != "mmm_public_simulation_export_v1":
        raise _fail("unknown_version", "mmm_sim.schema_version is not supported")
    status_value = data.get("status")
    if not isinstance(status_value, str) or status_value not in SIM_STATUSES:
        raise _fail("unmapped_literal", "mmm_sim.status is not known")
    run_value = data.get("run_id")
    if not isinstance(run_value, str) or not run_value:
        raise _fail("missing_fields", "mmm_sim.run_id is required")
    for plan_key in ("baseline_plan", "candidate_plan"):
        plan = _get_mapping(data, plan_key, "mmm_sim")
        if plan.get("schema_version") != "mmm_simulation_plan_v1":
            raise _fail("unknown_version", f"mmm_sim.{plan_key}.schema_version is not supported")
        for key in (
            "plan_id",
            "role",
            "spend_unit",
            "evaluation_time_window",
            "items",
            "total_spend",
        ):
            if key not in plan:
                raise _fail("missing_fields", f"mmm_sim.{plan_key}.{key} is required")
        role = plan.get("role")
        if role not in {"BASELINE", "CANDIDATE"}:
            raise _fail("unmapped_literal", f"mmm_sim.{plan_key}.role is not known")
        items = plan.get("items")
        if not isinstance(items, list) or not items:
            raise _fail("missing_fields", f"mmm_sim.{plan_key}.items must be non-empty")
        total = plan.get("total_spend")
        if not isinstance(total, int | float):
            raise _fail("missing_fields", f"mmm_sim.{plan_key}.total_spend must be numeric")
        running = 0.0
        for item in items:
            if not isinstance(item, Mapping):
                raise _fail("missing_fields", f"mmm_sim.{plan_key}.items entries must be mappings")
            for key in ("channel_id", "spend", "spend_unit"):
                if key not in item:
                    raise _fail("missing_fields", f"mmm_sim.{plan_key}.items.{key} is required")
            spend = item.get("spend")
            if not isinstance(spend, int | float) or spend < 0:
                raise _fail(
                    "invalid_invariants", f"mmm_sim.{plan_key}.items.spend must be non-negative"
                )
            running += float(spend)
        if abs(running - float(total)) > 1e-9:
            raise _fail(
                "invalid_invariants", f"mmm_sim.{plan_key}.total_spend must equal item spends"
            )
    comparison_raw = data.get("comparison")
    metrics: list[Mapping[str, object]] = []
    range_evals: list[Mapping[str, object]] = []
    uncertainty = "UNAVAILABLE"
    uncertainty_ref: str | None = None
    if comparison_raw is not None:
        if not isinstance(comparison_raw, Mapping):
            raise _fail("missing_fields", "mmm_sim.comparison must be a mapping")
        for key in (
            "comparison_id",
            "run_id",
            "baseline_plan_id",
            "candidate_plan_id",
            "status",
            "technical_summary",
        ):
            if key not in comparison_raw:
                raise _fail("missing_fields", f"mmm_sim.comparison.{key} is required")
        comp_status = comparison_raw.get("status")
        if comp_status not in SIM_STATUSES:
            raise _fail("unmapped_literal", "mmm_sim.comparison.status is not known")
        raw_metrics = comparison_raw.get("metrics", [])
        if not isinstance(raw_metrics, list):
            raise _fail("missing_fields", "mmm_sim.comparison.metrics must be a list")
        for metric in raw_metrics:
            if not isinstance(metric, Mapping):
                raise _fail("missing_fields", "mmm_sim.comparison.metrics entries must be mappings")
            for key in (
                "metric_id",
                "estimand",
                "aggregation_scope",
                "baseline_mu",
                "candidate_mu",
                "delta_mu",
                "unit",
            ):
                if key not in metric:
                    raise _fail("missing_fields", f"mmm_sim.comparison.metrics.{key} is required")
            base = metric.get("baseline_mu")
            cand = metric.get("candidate_mu")
            delta = metric.get("delta_mu")
            if (
                not isinstance(base, int | float)
                or not isinstance(cand, int | float)
                or not isinstance(delta, int | float)
                or abs(float(delta) - (float(cand) - float(base))) > 1e-9
            ):
                raise _fail(
                    "invalid_invariants", "delta_mu must equal candidate_mu minus baseline_mu"
                )
            metrics.append(metric)
            unc_raw = metric.get("uncertainty", {})
            if not isinstance(unc_raw, Mapping):
                raise _fail("missing_fields", "metric.uncertainty must be a mapping")
            unc_status, unc_ref = _admit_sim_uncertainty(
                unc_raw, "mmm_sim.comparison.metrics.uncertainty"
            )
            if unc_status != "AVAILABLE":
                uncertainty = unc_status
            elif uncertainty == "UNAVAILABLE":
                uncertainty = "AVAILABLE"
                uncertainty_ref = unc_ref
        raw_ranges = comparison_raw.get("range_evaluations", [])
        if not isinstance(raw_ranges, list):
            raise _fail("missing_fields", "mmm_sim.comparison.range_evaluations must be a list")
        for entry in raw_ranges:
            if not isinstance(entry, Mapping):
                raise _fail("missing_fields", "range_evaluations entries must be mappings")
            for key in (
                "range_record_id",
                "channel_id",
                "baseline_relation",
                "candidate_relation",
                "extrapolation",
            ):
                if key not in entry:
                    raise _fail("missing_fields", f"range_evaluations.{key} is required")
            candidate_relation = entry.get("candidate_relation")
            extrapolation = entry.get("extrapolation")
            if candidate_relation not in RANGE_RELATIONS or extrapolation not in EXTRAPOLATIONS:
                raise _fail("unmapped_literal", "range_evaluations holds an unknown literal")
            range_evals.append(entry)
    blocked_eval = any(entry.get("blocked") is True for entry in range_evals)
    restrictive_eval = any(
        entry.get("candidate_relation") != "WITHIN_SUPPORTED_RANGE"
        or entry.get("extrapolation") not in {"NONE", "INTERPOLATION"}
        for entry in range_evals
    )
    restriction_desc = tuple(
        f"range:{entry.get('range_record_id')}:{entry.get('candidate_relation')}"
        f"+{entry.get('extrapolation')}"
        for entry in range_evals
        if entry.get("candidate_relation") != "WITHIN_SUPPORTED_RANGE"
        or entry.get("extrapolation") not in {"NONE", "INTERPOLATION"}
    )
    limitation_refs = (
        _get_str_list(data, "limitation_references", "mmm_sim")
        if "limitation_references" in data
        else ()
    )
    blocking_refs = (
        _get_str_list(data, "blocking_references", "mmm_sim")
        if "blocking_references" in data
        else ()
    )
    failure_code: str | None = None
    failure_commit: str | None = None
    packet_raw = data.get("failure_packet")
    if packet_raw is not None:
        if not isinstance(packet_raw, Mapping):
            raise _fail("missing_fields", "mmm_sim.failure_packet must be a mapping")
        if packet_raw.get("schema_version") != "mmm_mip_failure_v1":
            raise _fail("unknown_version", "mmm_sim.failure_packet.schema_version is not supported")
        code_value = packet_raw.get("code")
        if not isinstance(code_value, str) or not code_value:
            raise _fail("missing_fields", "mmm_sim.failure_packet.code is required")
        failure_code = code_value
        packet_run = packet_raw.get("run_id")
        if packet_run is not None and packet_run != run_value:
            raise _fail("invalid_invariants", "failure_packet.run_id must match export run_id")
        packet_commit = packet_raw.get("producer_git_commit")
        if isinstance(packet_commit, str) and packet_commit:
            failure_commit = packet_commit
    if status_value in {"BLOCKED", "FAILED"} and packet_raw is None:
        raise _fail("invalid_invariants", "blocked/failed exports require a failure_packet")
    manifest_raw = data.get("run_manifest")
    if manifest_raw is not None:
        if not isinstance(manifest_raw, Mapping):
            raise _fail("missing_fields", "mmm_sim.run_manifest must be a mapping")
        if manifest_raw.get("run_id") != run_value:
            raise _fail("invalid_invariants", "run_manifest.run_id must match export run_id")
        if manifest_raw.get("status") != status_value:
            raise _fail("invalid_invariants", "run_manifest.status must equal export status")
    artifact_value = data.get("artifact_id")
    if isinstance(artifact_value, str) and artifact_value:
        artifact_id = artifact_value
    else:
        artifact_id = f"mmm_public_simulation:{run_value}"
    if run_value not in artifact_id:
        raise _fail("invalid_invariants", "artifact_id must include run_id")
    warning_texts = tuple(f"limitation:{ref}" for ref in limitation_refs)
    return _Sim(
        status=status_value,
        uncertainty=uncertainty,
        uncertainty_ref=uncertainty_ref,
        blocked_eval=blocked_eval,
        restrictive_eval=restrictive_eval,
        restriction_desc=restriction_desc,
        limitation_refs=limitation_refs,
        blocking_refs=blocking_refs,
        failure_code=failure_code,
        failure_commit=failure_commit,
        run_id=run_value,
        artifact_id=artifact_id,
        warning_texts=warning_texts,
    )


def _admit_context(data: Mapping[str, object] | None) -> _Context:
    if data is None:
        return _Context(
            consumption=None, static_labels=(), supersedes_id=None, supersedes_commit=None
        )
    if not isinstance(data, Mapping):
        raise _fail("missing_fields", "context must be a mapping")
    for key in data:
        if key not in {"consumption", "static_labels", "supersedes"}:
            raise _fail("unmapped_literal", f"context.{key} is not a known key")
    consumption_value = data.get("consumption")
    consumption: str | None = None
    if consumption_value is not None:
        if not isinstance(consumption_value, str) or consumption_value not in CONSUMPTION_STATUSES:
            raise _fail("unsupported_consumption", "context.consumption is not an admitted status")
        consumption = consumption_value
    labels_value = data.get("static_labels", [])
    if not isinstance(labels_value, list) or any(
        not isinstance(label, str) or label not in STATIC_LABELS for label in labels_value
    ):
        raise _fail("unmapped_literal", "context.static_labels holds an unknown label")
    supersedes_id: str | None = None
    supersedes_commit: str | None = None
    supersedes_raw = data.get("supersedes")
    if supersedes_raw is not None:
        if not isinstance(supersedes_raw, Mapping):
            raise _fail("missing_fields", "context.supersedes must be a mapping")
        artifact_value = supersedes_raw.get("artifact_id")
        commit_value = supersedes_raw.get("source_commit")
        if not isinstance(artifact_value, str) or not artifact_value:
            raise _fail("missing_fields", "context.supersedes.artifact_id is required")
        if not isinstance(commit_value, str) or not commit_value:
            raise _fail("missing_fields", "context.supersedes.source_commit is required")
        supersedes_id = artifact_value
        supersedes_commit = commit_value
    return _Context(
        consumption=consumption,
        static_labels=tuple(labels_value),
        supersedes_id=supersedes_id,
        supersedes_commit=supersedes_commit,
    )


def _admit(inputs: Mapping[str, object]) -> _Bundle:
    if not isinstance(inputs, Mapping):
        raise _fail("missing_fields", "inputs must be a mapping")
    version = inputs.get("schema_version")
    if version != SCHEMA_VERSION:
        raise _fail("unknown_version", "schema_version must be mip_fixture_journey_input_v1")
    for key in inputs:
        if key not in _TOP_LEVEL_KEYS:
            raise _fail("unmapped_literal", f"top-level key {key!r} is not known")
    readout_raw = inputs.get("geox_readout")
    compat_raw = inputs.get("mmm_compat")
    sim_raw = inputs.get("mmm_sim")
    if readout_raw is None and compat_raw is None and sim_raw is None:
        raise _fail("missing_fields", "at least one producer view is required")
    readout: _Readout | None = None
    compat: _Compat | None = None
    sim: _Sim | None = None
    if readout_raw is not None:
        if not isinstance(readout_raw, Mapping):
            raise _fail("missing_fields", "geox_readout must be a mapping")
        readout = _admit_readout(readout_raw)
    if compat_raw is not None:
        if not isinstance(compat_raw, Mapping):
            raise _fail("missing_fields", "mmm_compat must be a mapping")
        compat = _admit_compat(compat_raw)
    if sim_raw is not None:
        if not isinstance(sim_raw, Mapping):
            raise _fail("missing_fields", "mmm_sim must be a mapping")
        sim = _admit_sim(sim_raw)
    context_raw = inputs.get("context")
    if context_raw is not None and not isinstance(context_raw, Mapping):
        raise _fail("missing_fields", "context must be a mapping")
    context = _admit_context(context_raw if isinstance(context_raw, Mapping) else None)
    return _Bundle(readout=readout, compat=compat, sim=sim, context=context)


def _artifact_ids(bundle: _Bundle) -> tuple[str, ...]:
    ids: list[str] = []
    if bundle.readout is not None:
        ids.append(f"readout:{bundle.readout.experiment_id}")
    if bundle.compat is not None:
        ids.append(f"compat:{bundle.compat.evidence_id}")
    if bundle.sim is not None:
        ids.append(f"sim:{bundle.sim.artifact_id}")
        ids.append(f"sim:{bundle.sim.run_id}")
    return tuple(ids)


def _is_conflict(bundle: _Bundle) -> bool:
    context = bundle.context
    if context.supersedes_id is not None and context.supersedes_id in _artifact_ids(bundle):
        return True
    commits: set[str] = set()
    if bundle.readout is not None and bundle.readout.commit:
        commits.add(bundle.readout.commit)
    if bundle.compat is not None and bundle.compat.commit:
        commits.add(bundle.compat.commit)
    if bundle.sim is not None and bundle.sim.failure_commit:
        commits.add(bundle.sim.failure_commit)
    views_present = sum(
        1 for view in (bundle.readout, bundle.compat, bundle.sim) if view is not None
    )
    if views_present >= 2 and len(commits) > 1:
        return True
    compat_ok = bundle.compat is not None and bundle.compat.state in _COMPAT_OK_STATES
    sim_failed = bundle.sim is not None and bundle.sim.status == "FAILED"
    readout_failed = bundle.readout is not None and bundle.readout.status == "failed"
    sim_ok = bundle.sim is not None and bundle.sim.status in _SIM_OK_STATUSES
    if (compat_ok and sim_failed) or (readout_failed and sim_ok):
        return True
    if bundle.compat is not None and bundle.compat.state == "incompatible" and sim_ok:
        return True
    return False


def _comparison_present(bundle: _Bundle) -> bool:
    if bundle.sim is None or bundle.sim.status not in _SIM_OK_STATUSES:
        return False
    if bundle.compat is not None and bundle.compat.state not in _COMPAT_OK_STATES:
        return False
    if bundle.readout is not None and bundle.readout.handoff != _ELIGIBLE_HANDOFF:
        return False
    return True


def _is_fresh(bundle: _Bundle) -> bool:
    if bundle.readout is not None and bundle.readout.freshness != "fresh":
        return False
    return bundle.compat is None or bundle.compat.freshness == "fresh"


def _has_marks(bundle: _Bundle) -> bool:
    labels = bundle.context.static_labels
    if "diagnostic_only" in labels or "research_only" in labels:
        return True
    if bundle.context.consumption == "diagnostic_context_only":
        return True
    return bundle.compat is not None and bundle.compat.method_status in _MARK_METHODS


def _has_warnings_or_limits(bundle: _Bundle) -> bool:
    if bundle.compat is not None and (
        bundle.compat.warnings_count > 0 or bundle.compat.warning_texts
    ):
        return True
    if bundle.sim is not None and (bundle.sim.limitation_refs or bundle.sim.warning_texts):
        return True
    if bundle.readout is not None and (
        bundle.readout.warnings or bundle.readout.status == "warning"
    ):
        return True
    return False


def _uncertainty_available(bundle: _Bundle) -> bool:
    sim_ok = bundle.sim is None or bundle.sim.uncertainty == "AVAILABLE"
    compat_ok = bundle.compat is None or bundle.compat.uncertainty != "unavailable"
    return sim_ok and compat_ok


def _match_rows(bundle: _Bundle) -> list[str]:
    matched: list[str] = []
    if _is_conflict(bundle):
        matched.append("r12_conflict_superseded")
    sim_failed = bundle.sim is not None and bundle.sim.status == "FAILED"
    readout_failed = bundle.readout is not None and bundle.readout.status == "failed"
    if sim_failed or readout_failed:
        matched.append("r07_producer_failure")
    readout_blocked = bundle.readout is not None and bundle.readout.handoff == "blocked_for_handoff"
    compat_blocked = bundle.compat is not None and bundle.compat.state == "blocked"
    if readout_blocked or compat_blocked:
        matched.append("r05_blocked_handoff")
    if bundle.sim is not None and bundle.sim.status == "BLOCKED":
        matched.append("r06_blocked_simulation")
    if bundle.compat is not None and bundle.compat.state == "incompatible":
        matched.append("r04_incompatible")
    compat_stale = bundle.compat is not None and (
        bundle.compat.state == "stale" or bundle.compat.freshness == "stale"
    )
    readout_stale = bundle.readout is not None and bundle.readout.freshness in {"stale", "unknown"}
    if compat_stale or readout_stale:
        matched.append("r03_stale")
    labels = bundle.context.static_labels
    compat_diagnostic = (
        bundle.compat is not None and bundle.compat.method_status == "diagnostic_only"
    )
    compat_research = bundle.compat is not None and bundle.compat.method_status == "research_only"
    diagnostic_mark = (
        "diagnostic_only" in labels
        or bundle.context.consumption == "diagnostic_context_only"
        or compat_diagnostic
    )
    research_mark = "research_only" in labels or compat_research
    if diagnostic_mark:
        matched.append("r08_diagnostic_only")
    if research_mark:
        matched.append("r09_research_only")
    comparison = _comparison_present(bundle)
    if comparison and not _uncertainty_available(bundle):
        matched.append("r10_unavailable_uncertainty")
    if comparison and bundle.sim is not None and bundle.sim.restrictive_eval:
        matched.append("r11_range_restriction")
    if (
        comparison
        and _is_fresh(bundle)
        and _uncertainty_available(bundle)
        and (bundle.sim is None or not bundle.sim.restrictive_eval)
        and not _has_marks(bundle)
        and _has_warnings_or_limits(bundle)
    ):
        matched.append("r02_success_with_warning")
    if (
        comparison
        and _is_fresh(bundle)
        and _uncertainty_available(bundle)
        and (bundle.sim is None or not bundle.sim.restrictive_eval)
        and not _has_marks(bundle)
        and not _has_warnings_or_limits(bundle)
        and (bundle.compat is None or bundle.compat.state == "compatible")
        and (bundle.readout is None or bundle.readout.status == "success")
    ):
        matched.append("r01_success")
    return sorted(matched, key=ROW_IDS.index)


def _collect_issue_ids(bundle: _Bundle, matched: list[str]) -> list[str]:
    ids: list[str] = [f"row:{row}" for row in matched]
    if bundle.compat is not None:
        ids.extend(f"compat:{code}" for code in bundle.compat.reason_codes)
    if bundle.sim is not None:
        if bundle.sim.failure_code is not None:
            ids.append(f"sim:{bundle.sim.failure_code}")
        ids.extend(f"limitation:{ref}" for ref in bundle.sim.limitation_refs)
        ids.extend(f"blocking:{ref}" for ref in bundle.sim.blocking_refs)
        ids.extend(bundle.sim.restriction_desc)
    if bundle.readout is not None:
        ids.append(f"readout:{bundle.readout.status}")
        if bundle.readout.freshness != "fresh":
            ids.append(f"freshness:{bundle.readout.freshness}")
    for row in matched:
        if row == "r08_diagnostic_only":
            ids.append("mark:diagnostic_only")
        elif row == "r09_research_only":
            ids.append("mark:research_only")
        elif row == "r10_unavailable_uncertainty":
            ids.append("uncertainty:unavailable")
        elif row == "r11_range_restriction":
            ids.append("range:restricted")
        elif row == "r12_conflict_superseded":
            ids.append("identity:conflict")
        elif row == "r05_blocked_handoff":
            ids.append("handoff:blocked")
        elif row == "r06_blocked_simulation":
            ids.append("sim:blocked")
        elif row == "r07_producer_failure":
            ids.append("producer:failed")
        elif row == "r03_stale":
            ids.append("freshness:stale")
        elif row == "r04_incompatible":
            ids.append("compat:incompatible")
        elif row == "r02_success_with_warning":
            ids.append("comparison:warning")
        elif row == "r01_success":
            ids.append("comparison:success")
    return sorted(set(ids))


def _collect_warnings(bundle: _Bundle) -> tuple[str, ...]:
    texts: list[str] = []
    if bundle.readout is not None:
        texts.extend(bundle.readout.warnings)
    if bundle.compat is not None:
        texts.extend(bundle.compat.warning_texts)
    if bundle.sim is not None:
        texts.extend(bundle.sim.warning_texts)
    return tuple(sorted(set(texts)))


def _collect_limitations(bundle: _Bundle) -> tuple[str, ...]:
    items: list[str] = []
    if bundle.sim is not None:
        items.extend(f"limitation:{ref}" for ref in bundle.sim.limitation_refs)
        items.extend(bundle.sim.restriction_desc)
    return tuple(sorted(set(items)))


def resolve_fixture_journey(
    inputs: Mapping[str, object],
) -> FixtureJourneyResult | FixtureJourneyFailure:
    """Resolve one fixture journey from producer-shaped inputs.

    Never raises on producer data: admission problems return a typed
    FixtureJourneyFailure, contradictory known evidence returns the
    conflict row, and every matched row keeps its issues and restrictions.
    """
    try:
        bundle = _admit(inputs)
    except _AdmissionFailure as exc:
        return FixtureJourneyFailure(code=exc.code, detail=exc.detail)
    matched = _match_rows(bundle)
    if not matched:
        return FixtureJourneyFailure(
            code="no_explainable_journey",
            detail="inputs admit no explainable fixture journey row",
        )
    headline_id = min(matched, key=PRECEDENCE.index)
    issue, next_evidence = _ROW_HEADLINE[headline_id]
    other_mustnot: set[str] = set()
    for row in matched:
        if row != headline_id:
            other_mustnot.update(_ROW_MUSTNOT[row])
    permitted = tuple(claim for claim in _ROW_MAY[headline_id] if claim not in other_mustnot)
    prohibited = tuple(sorted(set().union(*(_ROW_MUSTNOT[row] for row in matched))))
    versions: dict[str, str] = {"fixture_schema": SCHEMA_VERSION}
    lineage: dict[str, str] = {}
    if bundle.readout is not None:
        versions["readout_version"] = "1.0"
        versions["artifact_version"] = "1.0"
        lineage["experiment_id"] = bundle.readout.experiment_id
        lineage["source_commit"] = bundle.readout.commit
    if bundle.compat is not None:
        versions["mmm_compat_schema"] = "mmm_calibration_compatibility_result_v1"
        lineage["compat_evidence_id"] = bundle.compat.evidence_id
        if bundle.compat.commit:
            lineage["compat_source_commit"] = bundle.compat.commit
    if bundle.sim is not None:
        versions["mmm_sim_schema"] = "mmm_public_simulation_export_v1"
        versions["mmm_sim_plan_schema"] = "mmm_simulation_plan_v1"
        lineage["sim_run_id"] = bundle.sim.run_id
        lineage["sim_artifact_id"] = bundle.sim.artifact_id
    return FixtureJourneyResult(
        matched_rows=tuple(matched),
        report_status=_ROW_STATUS[headline_id],
        headline=FixtureJourneyHeadline(
            row_id=headline_id, issue=issue, next_evidence=next_evidence
        ),
        issues=tuple(_collect_issue_ids(bundle, matched)),
        warnings=_collect_warnings(bundle),
        limitations=_collect_limitations(bundle),
        permitted_claims=permitted,
        prohibited_claims=prohibited,
        human_review_required=True,
        versions=versions,
        lineage=lineage,
    )


__all__ = [
    "CONSUMPTION_STATUSES",
    "FAILURE_CODES",
    "PRECEDENCE",
    "REPORT_STATUSES",
    "ROW_IDS",
    "SCHEMA_VERSION",
    "STATIC_LABELS",
    "FixtureJourneyFailure",
    "FixtureJourneyHeadline",
    "FixtureJourneyResult",
    "resolve_fixture_journey",
]
