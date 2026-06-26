"""Docker packaging checks for P10c deterministic FastAPI service."""

from __future__ import annotations

from pathlib import Path

_DOCKERFILE = Path("Dockerfile")
_DOCKERIGNORE = Path(".dockerignore")


def test_dockerfile_exists_for_p10c_service() -> None:
    assert _DOCKERFILE.is_file()


def test_dockerfile_runs_fastapi_service_only() -> None:
    content = _DOCKERFILE.read_text(encoding="utf-8")
    assert "uvicorn" in content
    assert "mip.service.app:app" in content
    assert "streamlit run" not in content.lower()
    assert "0.0.0.0" in content
    assert "8000" in content


def test_dockerignore_excludes_local_cache_and_git() -> None:
    assert _DOCKERIGNORE.is_file()
    content = _DOCKERIGNORE.read_text(encoding="utf-8")
    for pattern in (".git", ".venv", "__pycache__", ".pytest_cache", ".mypy_cache"):
        assert pattern in content
