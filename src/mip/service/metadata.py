"""Service metadata contracts for P10a health/version routes."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

from mip.contracts.base import ContractBaseModel

SERVICE_NAME = "mip-api"
PROJECT_NAME = "Marketing Intelligence Platform"
API_PHASE = "P10b.1"
SERVICE_BASELINE_COMMIT = "841cca0"
PUBLIC_DEMO_URL = "https://marketingintelligenceplatform.streamlit.app/"
STREAMLIT_ENTRYPOINT = "app/streamlit_app.py"
SERVICE_MODE = "deterministic"


class HealthResponse(ContractBaseModel):
    """Deterministic service health metadata."""

    status: str
    service: str
    mode: str
    llm_enabled: bool
    external_services_enabled: bool
    persistence_enabled: bool
    production_connector_enabled: bool
    measurement_engine_execution_enabled: bool


class VersionResponse(ContractBaseModel):
    """Deterministic service version and governance metadata."""

    service: str
    project: str
    package_version: str
    api_phase: str
    baseline_commit: str
    public_demo_url: str
    streamlit_entrypoint: str
    mode: str
    llm_enabled: bool
    external_services_enabled: bool
    persistence_enabled: bool
    production_connector_enabled: bool
    measurement_engine_execution_enabled: bool


def _package_version() -> str:
    try:
        return version("mip")
    except PackageNotFoundError:
        return "0.0.0"


def build_health_response() -> HealthResponse:
    """Build the canonical /health payload for deterministic P10a service mode."""
    return HealthResponse(
        status="ok",
        service=SERVICE_NAME,
        mode=SERVICE_MODE,
        llm_enabled=False,
        external_services_enabled=False,
        persistence_enabled=False,
        production_connector_enabled=False,
        measurement_engine_execution_enabled=False,
    )


def build_version_response() -> VersionResponse:
    """Build the canonical /version payload for deterministic P10a service mode."""
    return VersionResponse(
        service=SERVICE_NAME,
        project=PROJECT_NAME,
        package_version=_package_version(),
        api_phase=API_PHASE,
        baseline_commit=SERVICE_BASELINE_COMMIT,
        public_demo_url=PUBLIC_DEMO_URL,
        streamlit_entrypoint=STREAMLIT_ENTRYPOINT,
        mode=SERVICE_MODE,
        llm_enabled=False,
        external_services_enabled=False,
        persistence_enabled=False,
        production_connector_enabled=False,
        measurement_engine_execution_enabled=False,
    )
