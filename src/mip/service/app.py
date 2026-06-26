"""Minimal FastAPI application factory for the MIP service wrapper."""

from __future__ import annotations

from fastapi import FastAPI

from mip.service.metadata import (
    HealthResponse,
    VersionResponse,
    build_health_response,
    build_version_response,
)
from mip.service.routes import workflow_router

WORKFLOW_ROUTE_PATHS = (
    "/advisory/cold-start",
    "/readiness/assess",
    "/calibration/map",
    "/intake/overview",
)


def create_app() -> FastAPI:
    """Create the MIP FastAPI shell with health/version and P10b workflow routes."""
    application = FastAPI(
        title="MIP API",
        description=(
            "Deterministic MIP service wrapper. P10a health/version metadata plus "
            "P10b deterministic workflow routes over governed helpers."
        ),
        version="0.1.0",
    )

    @application.get(
        "/health",
        response_model=HealthResponse,
        tags=["service"],
        summary="Deterministic service health check",
        description=(
            "Returns deterministic service health metadata. No LLM, persistence, "
            "external services, or measurement engine execution."
        ),
    )
    def health() -> HealthResponse:
        return build_health_response()

    @application.get(
        "/version",
        response_model=VersionResponse,
        tags=["service"],
        summary="Service version and phase metadata",
        description=(
            "Returns package version, internal API phase, and governance flags for "
            "the deterministic MIP service wrapper."
        ),
    )
    def version() -> VersionResponse:
        return build_version_response()

    application.include_router(workflow_router)
    return application


app = create_app()

__all__ = ["app", "create_app", "WORKFLOW_ROUTE_PATHS"]
