"""P10b deterministic workflow API routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from mip.service.contracts import (
    CalibrationMapRequest,
    CalibrationMapResponse,
    ColdStartAdvisoryRequest,
    ColdStartAdvisoryResponse,
    IntakeOverviewRequest,
    IntakeOverviewResponse,
    ReadinessAssessRequest,
    ReadinessAssessResponse,
)
from mip.service.workflows import (
    run_calibration_map,
    run_cold_start_advisory,
    run_intake_overview,
    run_readiness_assess,
)

workflow_router = APIRouter(prefix="", tags=["workflows"])


@workflow_router.post(
    "/advisory/cold-start",
    response_model=ColdStartAdvisoryResponse,
    summary="Deterministic cold-start advisory workflow",
    description=(
        "Build a cold-start advisory plan from a deterministic demo fixture key. "
        "Advisory-only — not causal proof or ROI."
    ),
)
def advisory_cold_start(request: ColdStartAdvisoryRequest) -> ColdStartAdvisoryResponse:
    try:
        return run_cold_start_advisory(request.sample_key)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@workflow_router.post(
    "/readiness/assess",
    response_model=ReadinessAssessResponse,
    summary="Deterministic readiness assessment workflow",
    description=(
        "Assess workflow readiness from a deterministic demo fixture key. "
        "Structural readiness only — no MMM/GeoX execution."
    ),
)
def readiness_assess(request: ReadinessAssessRequest) -> ReadinessAssessResponse:
    try:
        return run_readiness_assess(request.sample_key)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@workflow_router.post(
    "/calibration/map",
    response_model=CalibrationMapResponse,
    summary="Deterministic calibration mapping workflow",
    description=(
        "Map governed experiment evidence to a calibration signal using a demo "
        "fixture key. Diagnostic-tier output only."
    ),
)
def calibration_map(request: CalibrationMapRequest) -> CalibrationMapResponse:
    try:
        return run_calibration_map(request.sample_key)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@workflow_router.post(
    "/intake/overview",
    response_model=IntakeOverviewResponse,
    summary="Deterministic intake routing overview workflow",
    description=(
        "Return intake path recommendation summary from a deterministic demo "
        "example key. Routing guidance only — not measurement conclusions."
    ),
)
def intake_overview(request: IntakeOverviewRequest) -> IntakeOverviewResponse:
    try:
        return run_intake_overview(request.example_key)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
