"""Public import tests for the MIP FastAPI service shell."""

from __future__ import annotations

import importlib
from pathlib import Path

from mip.service import app as service_app
from mip.service.app import create_app


def test_service_package_imports() -> None:
    service = importlib.import_module("mip.service")
    assert callable(service.create_app)
    assert service.API_PHASE == "P10b.1"


def test_create_app_returns_fastapi_instance() -> None:
    application = create_app()
    assert application is not None
    assert application.title == "MIP API"


def test_module_level_app_is_created() -> None:
    assert service_app is not None
    assert service_app.title == "MIP API"


def test_dockerfile_exists_for_p10c() -> None:
    assert Path("Dockerfile").is_file()


def test_streamlit_app_import_still_works() -> None:
    streamlit_app = importlib.import_module("app.streamlit_app")
    assert callable(streamlit_app.main)
