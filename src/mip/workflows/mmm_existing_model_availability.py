"""MMM existing model availability gate workflow (metadata only)."""

from __future__ import annotations

from datetime import UTC, date, datetime

from mip.contracts.mmm_existing_model_availability import (
    DEFAULT_MAX_MODEL_AGE_DAYS,
    MMMExistingModelAvailabilityIssueCode,
    MMMExistingModelAvailabilityRequest,
    MMMExistingModelAvailabilityResult,
    MMMExistingModelAvailabilityStatus,
    MMMModelAllowedUse,
    MMMModelArtifact,
    MMMModelArtifactMatch,
    MMMModelArtifactQuery,
    MMMModelDiagnosticStatus,
    MMMModelPromotionStatus,
)

_PLANNING_INTENDED_USES = frozenset(
    {
        MMMModelAllowedUse.BUDGET_PLANNING,
        MMMModelAllowedUse.BUDGET_OPTIMIZATION,
        MMMModelAllowedUse.SCENARIO_SIMULATION,
    }
)

_BOUNDARY_ISSUES = (
    MMMExistingModelAvailabilityIssueCode.NO_MODEL_EXECUTION,
    MMMExistingModelAvailabilityIssueCode.NO_OPTIMIZER_EXECUTION,
    MMMExistingModelAvailabilityIssueCode.NO_SIMULATOR_EXECUTION,
    MMMExistingModelAvailabilityIssueCode.NO_RECOMMENDATION_GENERATED,
    MMMExistingModelAvailabilityIssueCode.NO_DECISION_SURFACE_EXECUTION,
    MMMExistingModelAvailabilityIssueCode.NO_CLAIM_AUTHORIZATION,
    MMMExistingModelAvailabilityIssueCode.MODEL_ARTIFACT_METADATA_PRESERVED,
)


def evaluate_mmm_existing_model_availability(
    request: MMMExistingModelAvailabilityRequest,
) -> MMMExistingModelAvailabilityResult:
    """Determine whether an existing MMM model artifact can be used for a planning request."""
    query = request.query
    lineage = {
        **request.lineage,
        "gate_stage": "mmm_existing_model_availability",
        "query_request_id": query.request_id,
    }
    warnings = list(dict.fromkeys(request.warnings))
    issues: list[MMMExistingModelAvailabilityIssueCode] = list(_BOUNDARY_ISSUES)

    if not request.candidate_models:
        return _result(
            request_id=request.request_id,
            status=MMMExistingModelAvailabilityStatus.BLOCKED_NO_CANDIDATE_MODEL,
            requires_new_model_run=True,
            blocked_reasons=["no candidate MMM model artifacts provided"],
            warnings=warnings,
            issues=issues
            + [
                MMMExistingModelAvailabilityIssueCode.NO_CANDIDATE_MODEL,
                MMMExistingModelAvailabilityIssueCode.REQUIRES_NEW_MODEL_RUN,
            ],
            lineage=lineage,
        )

    issues.append(MMMExistingModelAvailabilityIssueCode.CANDIDATE_MODEL_FOUND)
    reference_date = _reference_date(query)
    matches = [
        _evaluate_candidate(query, candidate, reference_date=reference_date)
        for candidate in request.candidate_models
    ]

    if not any(match.scope_match for match in matches):
        return _blocked_result(
            request_id=request.request_id,
            status=MMMExistingModelAvailabilityStatus.BLOCKED_SCOPE_MISMATCH,
            matches=matches,
            blocked_reasons=["no candidate model matches requested scope"],
            issue=MMMExistingModelAvailabilityIssueCode.SCOPE_MISMATCH,
            warnings=warnings,
            issues=issues,
            lineage=lineage,
            requires_new_model_run=True,
        )

    scope_matches = [match for match in matches if match.scope_match]
    if not any(match.metric_match for match in scope_matches):
        return _blocked_result(
            request_id=request.request_id,
            status=MMMExistingModelAvailabilityStatus.BLOCKED_METRIC_MISMATCH,
            matches=matches,
            blocked_reasons=["no candidate model models requested metric"],
            issue=MMMExistingModelAvailabilityIssueCode.METRIC_MISMATCH,
            warnings=warnings,
            issues=issues,
            lineage=lineage,
            requires_new_model_run=True,
        )

    metric_matches = [match for match in scope_matches if match.metric_match]
    if not any(match.channel_match for match in metric_matches):
        return _blocked_result(
            request_id=request.request_id,
            status=MMMExistingModelAvailabilityStatus.BLOCKED_CHANNEL_MISMATCH,
            matches=matches,
            blocked_reasons=["no candidate model includes requested channels"],
            issue=MMMExistingModelAvailabilityIssueCode.CHANNEL_MISMATCH,
            warnings=warnings,
            issues=issues,
            lineage=lineage,
            requires_new_model_run=True,
        )

    channel_matches = [match for match in metric_matches if match.channel_match]

    diagnostic_only_blocked = [
        match
        for match in channel_matches
        if match.model_artifact.promotion_status
        == MMMModelPromotionStatus.PROMOTED_FOR_DIAGNOSTIC_ONLY
        and query.intended_use in _PLANNING_INTENDED_USES
    ]
    if diagnostic_only_blocked and not any(
        match.model_artifact.promotion_status == MMMModelPromotionStatus.PROMOTED_FOR_PLANNING
        for match in channel_matches
    ):
        return _blocked_result(
            request_id=request.request_id,
            status=MMMExistingModelAvailabilityStatus.DIAGNOSTIC_ONLY,
            matches=matches,
            blocked_reasons=[
                "candidate model promoted for diagnostic use only; planning use blocked"
            ],
            issue=MMMExistingModelAvailabilityIssueCode.USE_NOT_ALLOWED,
            warnings=warnings,
            issues=issues,
            lineage=lineage,
            requires_new_model_run=True,
        )

    if query.require_diagnostics_passed and not any(
        match.diagnostics_match for match in channel_matches
    ):
        return _blocked_result(
            request_id=request.request_id,
            status=MMMExistingModelAvailabilityStatus.BLOCKED_DIAGNOSTICS_FAILED,
            matches=matches,
            blocked_reasons=["required diagnostics not passed for any candidate model"],
            issue=MMMExistingModelAvailabilityIssueCode.DIAGNOSTICS_FAILED,
            warnings=warnings,
            issues=issues,
            lineage=lineage,
            requires_new_model_run=True,
        )

    diag_matches = (
        channel_matches
        if not query.require_diagnostics_passed
        else [match for match in channel_matches if match.diagnostics_match]
    )

    if query.require_promoted and not any(match.promotion_match for match in diag_matches):
        return _blocked_result(
            request_id=request.request_id,
            status=MMMExistingModelAvailabilityStatus.BLOCKED_NOT_PROMOTED,
            matches=matches,
            blocked_reasons=["no candidate model is promoted for planning"],
            issue=MMMExistingModelAvailabilityIssueCode.MODEL_NOT_PROMOTED,
            warnings=warnings,
            issues=issues,
            lineage=lineage,
            requires_new_model_run=True,
        )

    promo_matches = (
        diag_matches
        if not query.require_promoted
        else [match for match in diag_matches if match.promotion_match]
    )

    if not any(match.allowed_use_match for match in promo_matches):
        return _blocked_result(
            request_id=request.request_id,
            status=MMMExistingModelAvailabilityStatus.BLOCKED_USE_NOT_ALLOWED,
            matches=matches,
            blocked_reasons=["intended use not allowed for any candidate model"],
            issue=MMMExistingModelAvailabilityIssueCode.USE_NOT_ALLOWED,
            warnings=warnings,
            issues=issues,
            lineage=lineage,
            requires_new_model_run=True,
        )

    use_matches = [match for match in promo_matches if match.allowed_use_match]

    if query.require_trust_metadata and not any(
        match.trust_metadata_match for match in use_matches
    ):
        return _blocked_result(
            request_id=request.request_id,
            status=MMMExistingModelAvailabilityStatus.BLOCKED_MISSING_TRUST_METADATA,
            matches=matches,
            blocked_reasons=["required trust metadata missing for all candidate models"],
            issue=MMMExistingModelAvailabilityIssueCode.TRUST_METADATA_MISSING,
            warnings=warnings,
            issues=issues,
            lineage=lineage,
            requires_new_model_run=True,
        )

    trust_matches = (
        use_matches
        if not query.require_trust_metadata
        else [match for match in use_matches if match.trust_metadata_match]
    )

    fresh_matches = [match for match in trust_matches if match.freshness_match]
    stale_matches = [match for match in trust_matches if not match.freshness_match]

    if not fresh_matches and stale_matches:
        best_stale = _select_best_candidate(stale_matches)
        return _result(
            request_id=request.request_id,
            status=MMMExistingModelAvailabilityStatus.REQUIRES_MODEL_REFRESH,
            selected_model=best_stale.model_artifact,
            candidate_matches=matches,
            requires_model_refresh=True,
            requires_new_model_run=False,
            blocked_reasons=["best matching candidate model is stale"],
            warnings=warnings + list(best_stale.warnings),
            issues=issues
            + [
                MMMExistingModelAvailabilityIssueCode.MODEL_STALE,
                MMMExistingModelAvailabilityIssueCode.REQUIRES_MODEL_REFRESH,
                MMMExistingModelAvailabilityIssueCode.MODEL_SELECTED,
            ],
            allowed_uses=list(best_stale.model_artifact.allowed_uses),
            lineage=lineage,
        )

    if not fresh_matches:
        return _result(
            request_id=request.request_id,
            status=MMMExistingModelAvailabilityStatus.REQUIRES_NEW_MODEL_RUN,
            candidate_matches=matches,
            requires_new_model_run=True,
            blocked_reasons=["no usable existing model artifact after eligibility checks"],
            warnings=warnings,
            issues=issues + [MMMExistingModelAvailabilityIssueCode.REQUIRES_NEW_MODEL_RUN],
            lineage=lineage,
        )

    best = _select_best_candidate(fresh_matches)
    has_warnings = bool(best.warnings) or any(
        best.model_artifact.diagnostic_status == MMMModelDiagnosticStatus.PASSED_WITH_WARNINGS
        for _ in [0]
    )
    status = (
        MMMExistingModelAvailabilityStatus.USABLE_EXISTING_MODEL_WITH_WARNINGS
        if has_warnings
        else MMMExistingModelAvailabilityStatus.USABLE_EXISTING_MODEL
    )
    selected_issues = [
        MMMExistingModelAvailabilityIssueCode.MODEL_SELECTED,
        MMMExistingModelAvailabilityIssueCode.ALLOWED_USE_MATCHED,
    ]
    if best.model_artifact.decision_surface_id:
        selected_issues.append(
            MMMExistingModelAvailabilityIssueCode.DECISION_SURFACE_REFERENCE_PRESENT
        )
    if best.model_artifact.model_calibration_readiness_id:
        selected_issues.append(
            MMMExistingModelAvailabilityIssueCode.MODEL_CALIBRATION_READINESS_REFERENCE_PRESENT
        )

    return _result(
        request_id=request.request_id,
        status=status,
        selected_model=best.model_artifact,
        candidate_matches=matches,
        warnings=warnings + list(best.warnings),
        issues=issues + selected_issues,
        allowed_uses=list(best.model_artifact.allowed_uses),
        lineage=lineage,
    )


def summarize_mmm_existing_model_availability(
    result: MMMExistingModelAvailabilityResult,
) -> dict[str, str | int | float | bool | list[str] | None]:
    """Return metadata-only summary of an availability evaluation."""
    if isinstance(result.status, MMMExistingModelAvailabilityStatus):
        status = result.status.value
    else:
        status = str(result.status)
    return {
        "request_id": result.request_id,
        "status": status,
        "selected_model_id": (
            result.selected_model.model_id if result.selected_model is not None else None
        ),
        "requires_new_model_run": result.requires_new_model_run,
        "requires_model_refresh": result.requires_model_refresh,
        "blocked_reasons": list(result.blocked_reasons),
        "candidate_count": len(result.candidate_matches),
        "warnings": list(result.warnings),
        "allowed_uses": [
            use.value if isinstance(use, MMMModelAllowedUse) else str(use)
            for use in result.allowed_uses
        ],
    }


def _evaluate_candidate(
    query: MMMModelArtifactQuery,
    candidate: MMMModelArtifact,
    *,
    reference_date: date,
) -> MMMModelArtifactMatch:
    warnings: list[str] = []
    issues: list[MMMExistingModelAvailabilityIssueCode] = []

    scope_match = _scope_match(query, candidate)
    if not scope_match:
        issues.append(MMMExistingModelAvailabilityIssueCode.SCOPE_MISMATCH)

    metric_match = _metric_match(query, candidate)
    if not metric_match:
        issues.append(MMMExistingModelAvailabilityIssueCode.METRIC_MISMATCH)

    channel_match = _channel_match(query, candidate)
    if not channel_match:
        issues.append(MMMExistingModelAvailabilityIssueCode.CHANNEL_MISMATCH)

    freshness_match, freshness_warning = _freshness_match(
        query, candidate, reference_date=reference_date
    )
    if freshness_warning:
        warnings.append(freshness_warning)
    if not freshness_match:
        issues.append(MMMExistingModelAvailabilityIssueCode.MODEL_STALE)

    diagnostics_match = _diagnostics_match(query, candidate, warnings=warnings)
    if not diagnostics_match:
        issues.append(MMMExistingModelAvailabilityIssueCode.DIAGNOSTICS_FAILED)

    promotion_match = _promotion_match(query, candidate, warnings=warnings)
    if not promotion_match:
        issues.append(MMMExistingModelAvailabilityIssueCode.MODEL_NOT_PROMOTED)

    allowed_use_match = query.intended_use in candidate.allowed_uses
    if allowed_use_match:
        issues.append(MMMExistingModelAvailabilityIssueCode.ALLOWED_USE_MATCHED)
    else:
        issues.append(MMMExistingModelAvailabilityIssueCode.USE_NOT_ALLOWED)

    trust_metadata_match = _trust_metadata_match(query, candidate)
    if trust_metadata_match:
        if candidate.decision_surface_id:
            issues.append(
                MMMExistingModelAvailabilityIssueCode.DECISION_SURFACE_REFERENCE_PRESENT
            )
        if candidate.model_calibration_readiness_id:
            issues.append(
                MMMExistingModelAvailabilityIssueCode.MODEL_CALIBRATION_READINESS_REFERENCE_PRESENT
            )
    elif query.require_trust_metadata:
        issues.append(MMMExistingModelAvailabilityIssueCode.TRUST_METADATA_MISSING)

    match_score = _compute_match_score(
        scope_match=scope_match,
        metric_match=metric_match,
        channel_match=channel_match,
        freshness_match=freshness_match,
        promotion_match=promotion_match,
        diagnostics_match=diagnostics_match,
        allowed_use_match=allowed_use_match,
        trust_metadata_match=trust_metadata_match,
        candidate=candidate,
        reference_date=reference_date,
    )

    return MMMModelArtifactMatch(
        model_artifact=candidate,
        scope_match=scope_match,
        metric_match=metric_match,
        channel_match=channel_match,
        freshness_match=freshness_match,
        promotion_match=promotion_match,
        diagnostics_match=diagnostics_match,
        allowed_use_match=allowed_use_match,
        trust_metadata_match=trust_metadata_match,
        match_score=match_score,
        warnings=warnings,
        issues=list(dict.fromkeys(issues)),
    )


def _scope_match(query: MMMModelArtifactQuery, candidate: MMMModelArtifact) -> bool:
    if query.geo_scope and candidate.geo_scope and query.geo_scope not in candidate.geo_scope:
        return False
    if query.business_unit and candidate.business_unit and (
        query.business_unit != candidate.business_unit
    ):
        return False
    if query.product_scope and candidate.product_scope and (
        query.product_scope not in candidate.product_scope
    ):
        return False
    return True


def _metric_match(query: MMMModelArtifactQuery, candidate: MMMModelArtifact) -> bool:
    if not query.metric:
        return True
    if not candidate.metrics:
        return False
    return query.metric in candidate.metrics


def _channel_match(query: MMMModelArtifactQuery, candidate: MMMModelArtifact) -> bool:
    if not query.channels:
        return True
    if not candidate.channels:
        return False
    requested = {channel.strip().lower() for channel in query.channels if channel.strip()}
    available = {channel.strip().lower() for channel in candidate.channels if channel.strip()}
    return requested.issubset(available)


def _freshness_match(
    query: MMMModelArtifactQuery,
    candidate: MMMModelArtifact,
    *,
    reference_date: date,
) -> tuple[bool, str | None]:
    fresh_date = candidate.data_freshness_date or candidate.training_end_date
    if fresh_date is None:
        return False, "model freshness date unavailable"
    age_days = (reference_date - fresh_date).days
    max_age = query.max_model_age_days or DEFAULT_MAX_MODEL_AGE_DAYS
    if age_days > max_age:
        return False, f"model data is {age_days} days old; max allowed is {max_age}"
    if age_days > max_age * 0.75:
        return True, f"model data is {age_days} days old; approaching max age {max_age}"
    return True, None


def _diagnostics_match(
    query: MMMModelArtifactQuery,
    candidate: MMMModelArtifact,
    *,
    warnings: list[str],
) -> bool:
    if not query.require_diagnostics_passed:
        return True
    if candidate.diagnostic_status == MMMModelDiagnosticStatus.PASSED:
        return True
    if candidate.diagnostic_status == MMMModelDiagnosticStatus.PASSED_WITH_WARNINGS:
        warnings.append("model diagnostics passed with warnings")
        return True
    return False


def _promotion_match(
    query: MMMModelArtifactQuery,
    candidate: MMMModelArtifact,
    *,
    warnings: list[str],
) -> bool:
    if not query.require_promoted:
        return True
    if candidate.promotion_status == MMMModelPromotionStatus.PROMOTED_FOR_PLANNING:
        return True
    if candidate.promotion_status == MMMModelPromotionStatus.PROMOTED_FOR_DIAGNOSTIC_ONLY:
        if query.intended_use in _PLANNING_INTENDED_USES:
            return False
        warnings.append("model promoted for diagnostic use only")
        return True
    return False


def _trust_metadata_match(query: MMMModelArtifactQuery, candidate: MMMModelArtifact) -> bool:
    has_reference = bool(
        candidate.trust_report_id
        or candidate.decision_surface_id
        or candidate.model_calibration_readiness_id
    )
    if not query.require_trust_metadata:
        return True
    return has_reference


def _compute_match_score(
    *,
    scope_match: bool,
    metric_match: bool,
    channel_match: bool,
    freshness_match: bool,
    promotion_match: bool,
    diagnostics_match: bool,
    allowed_use_match: bool,
    trust_metadata_match: bool,
    candidate: MMMModelArtifact,
    reference_date: date,
) -> int:
    score = 0
    if scope_match:
        score += 100
    if metric_match:
        score += 100
    if channel_match:
        score += 100
    if allowed_use_match:
        score += 80
    if promotion_match:
        score += 60
        if candidate.promotion_status == MMMModelPromotionStatus.PROMOTED_FOR_PLANNING:
            score += 20
    if diagnostics_match:
        score += 50
        if candidate.diagnostic_status == MMMModelDiagnosticStatus.PASSED:
            score += 10
    if trust_metadata_match:
        score += 20
    if freshness_match:
        score += 40
        fresh_date = candidate.data_freshness_date or candidate.training_end_date
        if fresh_date is not None:
            age_days = (reference_date - fresh_date).days
            score += max(0, 30 - age_days // 7)
    return score


def _reference_date(query: MMMModelArtifactQuery) -> date:
    if query.planning_end_date is not None:
        return query.planning_end_date
    return datetime.now(tz=UTC).date()


def _select_best_candidate(matches: list[MMMModelArtifactMatch]) -> MMMModelArtifactMatch:
    return max(
        matches,
        key=lambda match: (
            match.match_score,
            match.model_artifact.data_freshness_date
            or match.model_artifact.training_end_date
            or date.min,
            match.model_artifact.model_id,
        ),
    )


def _blocked_result(
    *,
    request_id: str,
    status: MMMExistingModelAvailabilityStatus,
    matches: list[MMMModelArtifactMatch],
    blocked_reasons: list[str],
    issue: MMMExistingModelAvailabilityIssueCode,
    warnings: list[str],
    issues: list[MMMExistingModelAvailabilityIssueCode],
    lineage: dict[str, str],
    requires_new_model_run: bool,
) -> MMMExistingModelAvailabilityResult:
    return _result(
        request_id=request_id,
        status=status,
        candidate_matches=matches,
        requires_new_model_run=requires_new_model_run,
        blocked_reasons=blocked_reasons,
        warnings=warnings,
        issues=issues + [issue, MMMExistingModelAvailabilityIssueCode.REQUIRES_NEW_MODEL_RUN],
        lineage=lineage,
    )


def _result(
    *,
    request_id: str,
    status: MMMExistingModelAvailabilityStatus,
    selected_model: MMMModelArtifact | None = None,
    candidate_matches: list[MMMModelArtifactMatch] | None = None,
    requires_new_model_run: bool = False,
    requires_model_refresh: bool = False,
    blocked_reasons: list[str] | None = None,
    warnings: list[str] | None = None,
    issues: list[MMMExistingModelAvailabilityIssueCode] | None = None,
    allowed_uses: list[MMMModelAllowedUse] | None = None,
    lineage: dict[str, str] | None = None,
) -> MMMExistingModelAvailabilityResult:
    return MMMExistingModelAvailabilityResult(
        request_id=request_id,
        status=status,
        selected_model=selected_model,
        candidate_matches=candidate_matches or [],
        requires_new_model_run=requires_new_model_run,
        requires_model_refresh=requires_model_refresh,
        blocked_reasons=blocked_reasons or [],
        allowed_uses=allowed_uses or [],
        warnings=warnings or [],
        issues=issues or [],
        lineage=lineage or {},
    )
