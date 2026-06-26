"""Deployment readiness checks for the deterministic public Streamlit demo."""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
REQUIREMENTS_PATH = REPO_ROOT / "requirements.txt"
README_PATH = REPO_ROOT / "README.md"
CANONICAL_APP_PATH = REPO_ROOT / "app" / "streamlit_app.py"
STREAMLIT_CONFIG_PATH = REPO_ROOT / ".streamlit" / "config.toml"
SECRETS_PATH = REPO_ROOT / ".streamlit" / "secrets.toml"

DEV_ONLY_PACKAGES = ("pytest", "ruff", "mypy", "black", "pre-commit")
FORBIDDEN_PROVIDER_PATTERNS = (
    "api_key",
    "secret_key",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "GEMINI_API_KEY",
    "HF_TOKEN",
    "HUGGINGFACE_TOKEN",
    "st.secrets",
    "type=\"password\"",
    "file_uploader",
)


def test_requirements_txt_exists() -> None:
    assert REQUIREMENTS_PATH.is_file()


def test_requirements_txt_does_not_include_dev_only_tools() -> None:
    content = REQUIREMENTS_PATH.read_text(encoding="utf-8").lower()
    for package in DEV_ONLY_PACKAGES:
        assert package not in content


def test_requirements_txt_includes_local_package_marker() -> None:
    lines = [
        line.strip()
        for line in REQUIREMENTS_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    assert lines[0] == "."


def test_requirements_txt_includes_streamlit() -> None:
    content = REQUIREMENTS_PATH.read_text(encoding="utf-8").lower()
    assert "streamlit" in content


def test_canonical_app_path_exists() -> None:
    assert CANONICAL_APP_PATH.is_file()


def test_readme_references_canonical_app_path() -> None:
    readme = README_PATH.read_text(encoding="utf-8")
    assert "app/streamlit_app.py" in readme
    assert "poetry run streamlit run app/streamlit_app.py" in readme


def test_readme_includes_deterministic_public_demo_statement() -> None:
    readme = README_PATH.read_text(encoding="utf-8").lower()
    assert "deterministic" in readme
    assert "no secrets" in readme or "no llm" in readme or "no api key" in readme


def test_no_committed_streamlit_secrets_toml() -> None:
    assert not SECRETS_PATH.exists()


def test_streamlit_config_exists_without_secrets() -> None:
    assert STREAMLIT_CONFIG_PATH.is_file()
    content = STREAMLIT_CONFIG_PATH.read_text(encoding="utf-8").lower()
    assert "api_key" not in content
    assert "token" not in content


@pytest.mark.parametrize("pattern", FORBIDDEN_PROVIDER_PATTERNS)
def test_canonical_app_source_does_not_contain_provider_or_upload_patterns(
    pattern: str,
) -> None:
    source = CANONICAL_APP_PATH.read_text(encoding="utf-8")
    assert pattern not in source


def test_canonical_app_source_contains_deterministic_mode_language() -> None:
    source = CANONICAL_APP_PATH.read_text(encoding="utf-8").lower()
    assert "deterministic" in source
    assert "public demo safety" in source
    assert "no llm provider" in source
