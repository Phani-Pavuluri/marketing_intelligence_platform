"""MIP FastAPI service wrapper (P10a+)."""

from mip.service.app import app, create_app
from mip.service.metadata import (
    API_PHASE,
    PUBLIC_DEMO_URL,
    SERVICE_BASELINE_COMMIT,
    STREAMLIT_ENTRYPOINT,
    HealthResponse,
    VersionResponse,
    build_health_response,
    build_version_response,
)

__all__ = [
    "API_PHASE",
    "PUBLIC_DEMO_URL",
    "SERVICE_BASELINE_COMMIT",
    "STREAMLIT_ENTRYPOINT",
    "HealthResponse",
    "VersionResponse",
    "app",
    "build_health_response",
    "build_version_response",
    "create_app",
]
