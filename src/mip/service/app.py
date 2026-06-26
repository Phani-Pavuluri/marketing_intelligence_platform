"""Minimal FastAPI application factory for the MIP service wrapper (P10a)."""

from __future__ import annotations

from fastapi import FastAPI

from mip.service.metadata import (
    HealthResponse,
    VersionResponse,
    build_health_response,
    build_version_response,
)

_DEFERRED_WORKFLOW_ROUTE_PREFIXES = (
    "/advisory/",
    "/readiness/",
    "/calibration/",
    "/intake/",
)


def create_app() -> FastAPI:
    """Create the P10a FastAPI shell with health/version metadata routes only."""
    application = FastAPI(
        title="MIP API",
        description=(
            "Deterministic MIP service wrapper. P10a exposes health/version metadata only. "
            "Workflow routes are deferred to P10b."
        ),
        version="0.1.0",
    )

    @application.get("/health", response_model=HealthResponse, tags=["service"])
    def health() -> HealthResponse:
        return build_health_response()

    @application.get("/version", response_model=VersionResponse, tags=["service"])
    def version() -> VersionResponse:
        return build_version_response()

    return application


app = create_app()

__all__ = ["app", "create_app", "_DEFERRED_WORKFLOW_ROUTE_PREFIXES"]
