"""Deterministic intake path recommendation (P1 / I2)."""

from datetime import UTC, datetime

from mip.contracts.intake import (
    DataGrain,
    GeoGrain,
    IntakeCandidatePath,
    IntakeIntendedUse,
    IntakePathRecommendation,
    IntakeRecommendationStatus,
    MeasurementIntakeSession,
    MeasurementWorkflowKind,
)

_GEO_LEVEL_GRAINS = frozenset(
    {GeoGrain.GEO, GeoGrain.DMA, GeoGrain.REGION, GeoGrain.MARKET},
)


def _missing_required_session_fields(session: MeasurementIntakeSession) -> list[str]:
    missing: list[str] = []
    if not session.business_question.strip():
        missing.append("business_question")
    if session.intended_use is None:
        missing.append("intended_use")
    if session.workflow_kind is None:
        missing.append("workflow_kind")
    return missing


def _semantic_registry_questions(session: MeasurementIntakeSession) -> list[str]:
    questions: list[str] = []
    if not session.metric_id:
        questions.append("Which canonical metric_id should govern this intake?")
    if not session.estimand_id:
        questions.append("Which estimand_id defines the causal or performance claim?")
    return questions


def _base_recommendation(
    session: MeasurementIntakeSession,
    *,
    status: IntakeRecommendationStatus,
    recommended_path: IntakeCandidatePath,
    why_this_path: str,
    why_other_paths_blocked: list[str] | None = None,
    required_next_questions: list[str] | None = None,
    warnings: list[str] | None = None,
    blocking_reasons: list[str] | None = None,
    allowed_next_steps: list[str] | None = None,
    blocked_next_steps: list[str] | None = None,
) -> IntakePathRecommendation:
    semantic_questions = _semantic_registry_questions(session)
    merged_warnings = list(warnings or [])
    merged_questions = list(required_next_questions or [])
    if semantic_questions:
        merged_warnings.append(
            "metric_id and/or estimand_id not set; semantic registries are a later phase"
        )
        merged_questions.extend(semantic_questions)

    return IntakePathRecommendation(
        recommendation_id=f"{session.session_id}-path-rec",
        session_id=session.session_id,
        status=status,
        recommended_path=recommended_path,
        workflow_kind=session.workflow_kind,
        why_this_path=why_this_path,
        why_other_paths_blocked=why_other_paths_blocked or [],
        required_next_questions=merged_questions,
        warnings=merged_warnings,
        blocking_reasons=blocking_reasons or [],
        allowed_next_steps=allowed_next_steps or [],
        blocked_next_steps=blocked_next_steps or [],
        created_at=datetime.now(tz=UTC),
    )


def recommend_intake_path(session: MeasurementIntakeSession) -> IntakePathRecommendation:
    """Return a provider-free, deterministic path recommendation for a session."""

    missing = _missing_required_session_fields(session)
    if missing:
        questions = [f"Please provide: {field}" for field in missing]
        return _base_recommendation(
            session,
            status=IntakeRecommendationStatus.NEEDS_CLARIFICATION,
            recommended_path=IntakeCandidatePath.BLOCKED_NEEDS_MORE_DATA,
            why_this_path="Required intake fields are incomplete.",
            required_next_questions=questions,
            blocking_reasons=["Intake session missing required fields for recommendation."],
            blocked_next_steps=["Proceed to data intake until session is complete."],
        )

    if session.intended_use == IntakeIntendedUse.OPTIMIZER_CANDIDATE:
        return _base_recommendation(
            session,
            status=IntakeRecommendationStatus.BLOCKED,
            recommended_path=IntakeCandidatePath.BLOCKED_NEEDS_MORE_DATA,
            why_this_path=(
                "Optimizer-backed paths are deferred until certified decision surface, "
                "optimizer governance, uncertainty policy, and approval exist."
            ),
            blocking_reasons=[
                "optimizer_candidate intended_use is not supported in P1",
                "Certified decision surface and optimizer governance are required",
            ],
            blocked_next_steps=[
                "optimizer recommendation",
                "budget recommendation",
                "production decision automation",
            ],
        )

    if session.workflow_kind == MeasurementWorkflowKind.CALIBRATION_INTAKE:
        return _base_recommendation(
            session,
            status=IntakeRecommendationStatus.RECOMMENDED_WITH_WARNINGS,
            recommended_path=IntakeCandidatePath.EXPERIMENT_CALIBRATION_INTAKE,
            why_this_path=(
                "Experiment evidence should enter MMM through governed calibration intake."
            ),
            warnings=[
                "Experiment results must map to CalibrationSignal, not free-text evidence."
            ],
            allowed_next_steps=["collect governed experiment export for calibration mapping"],
            blocked_next_steps=["send raw experiment payloads directly into MMM"],
        )

    if session.workflow_kind == MeasurementWorkflowKind.DECISION_REVIEW:
        return _base_recommendation(
            session,
            status=IntakeRecommendationStatus.RECOMMENDED_WITH_WARNINGS,
            recommended_path=IntakeCandidatePath.DECISION_REVIEW_PACKET,
            why_this_path="Decision review requires a governed stakeholder packet.",
            warnings=[
                "Decision packet requires evidence alignment, TrustReport, uncertainty, "
                "and approval state."
            ],
            allowed_next_steps=["assemble decision review packet prerequisites"],
            blocked_next_steps=["publish production decision packet without approval"],
        )

    if session.workflow_kind == MeasurementWorkflowKind.GEOX:
        if session.intended_use == IntakeIntendedUse.GEO_EXPERIMENT_DESIGN:
            return _base_recommendation(
                session,
                status=IntakeRecommendationStatus.RECOMMENDED,
                recommended_path=IntakeCandidatePath.GEO_EXPERIMENT_DESIGN,
                why_this_path="Geo experiment design workflow matches the declared intended use.",
                allowed_next_steps=["capture design requirements and power assumptions"],
            )
        if session.intended_use == IntakeIntendedUse.GEO_EXPERIMENT_READOUT:
            return _base_recommendation(
                session,
                status=IntakeRecommendationStatus.RECOMMENDED_WITH_WARNINGS,
                recommended_path=IntakeCandidatePath.GEO_EXPERIMENT_READOUT,
                why_this_path="Geo experiment readout workflow matches the declared intended use.",
                warnings=["Readout requires governed experiment export and evidence."],
                allowed_next_steps=["import governed experiment export when available"],
            )

    if session.workflow_kind == MeasurementWorkflowKind.MMM:
        if session.intended_use == IntakeIntendedUse.CALIBRATED_MMM:
            return _base_recommendation(
                session,
                status=IntakeRecommendationStatus.RECOMMENDED_WITH_WARNINGS,
                recommended_path=IntakeCandidatePath.CALIBRATED_MMM,
                why_this_path="Calibrated MMM requires governed calibration evidence.",
                warnings=[
                    "CalibrationSignal-compatible evidence will be required in later phases."
                ],
                allowed_next_steps=["plan calibration evidence intake"],
                blocked_next_steps=["treat diagnostic MMM as calibrated"],
            )

        if session.intended_use == IntakeIntendedUse.DECISION_SURFACE_CANDIDATE:
            return _base_recommendation(
                session,
                status=IntakeRecommendationStatus.RECOMMENDED_WITH_WARNINGS,
                recommended_path=IntakeCandidatePath.DECISION_SURFACE_CERTIFICATION,
                why_this_path=(
                    "Decision surface certification is required before decision-support use."
                ),
                warnings=["Decision surface is not certified in P1."],
                allowed_next_steps=["specify decision surface certification prerequisites"],
                blocked_next_steps=[
                    "optimizer recommendation",
                    "budget recommendation",
                    "production decision automation",
                ],
            )

        if session.geo_grain in _GEO_LEVEL_GRAINS:
            return _base_recommendation(
                session,
                status=IntakeRecommendationStatus.RECOMMENDED_WITH_WARNINGS,
                recommended_path=IntakeCandidatePath.GEO_LEVEL_MMM,
                why_this_path="Geo-level MMM matches the declared geographic grain.",
                warnings=["Geo-level KPI and media data will be required in later phases."],
                allowed_next_steps=["confirm geo-level outcome and media coverage"],
            )

        if (
            session.time_grain == DataGrain.WEEKLY
            and session.geo_grain == GeoGrain.NATIONAL
            and session.intended_use == IntakeIntendedUse.DIAGNOSTIC_ONLY
        ):
            return _base_recommendation(
                session,
                status=IntakeRecommendationStatus.RECOMMENDED,
                recommended_path=IntakeCandidatePath.NATIONAL_DIAGNOSTIC_MMM,
                why_this_path=(
                    "Weekly national diagnostic MMM matches scope, grain, and intended use."
                ),
                allowed_next_steps=["define required data assets in a later phase"],
            )

    return _base_recommendation(
        session,
        status=IntakeRecommendationStatus.NEEDS_CLARIFICATION,
        recommended_path=IntakeCandidatePath.BLOCKED_NEEDS_MORE_DATA,
        why_this_path="Insufficient session detail to select a governed path.",
        required_next_questions=[
            "Clarify workflow_kind, intended_use, time_grain, and geo_grain."
        ],
        blocking_reasons=["Session does not match a known deterministic path rule."],
    )
