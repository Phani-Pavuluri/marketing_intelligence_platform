"""Fail-closed, provider-neutral configuration."""
# ruff: noqa
# mypy: ignore-errors
from __future__ import annotations
import os
from pydantic import BaseModel, Field

class ProviderConfig(BaseModel):
    enabled: bool = False
    provider_id: str = "disabled"
    model_id: str = ""
    credential_reference: str | None = None
    base_url: str | None = None
    timeout_seconds: float = Field(default=10.0, gt=0, le=60)
    max_output_chars: int = Field(default=4000, gt=0, le=20000)
    prompt_template_id: str = "mip_read_only_front_door"
    prompt_version: str = "1"
    configuration_id: str = "default"
    max_retries: int = Field(default=0, ge=0, le=1)
    max_output_tokens: int = Field(default=1200, ge=256, le=4096)
    project: str | None = None

    @classmethod
    def from_secret_mapping(cls, secrets: dict) -> "ProviderConfig":
        """Resolve the same explicit settings from an injected Streamlit mapping."""
        enabled = str(secrets.get("MIP_LLM_ENABLED", "")).lower() in {"1", "true", "yes"}
        provider = str(secrets.get("MIP_LLM_PROVIDER", "disabled"))
        model = str(secrets.get("MIP_LLM_MODEL", ""))
        key = secrets.get("OPENAI_API_KEY")
        if not enabled or provider != "openai" or not model or not key:
            return cls()
        return cls(enabled=True, provider_id="openai", model_id=model, credential_reference="OPENAI_API_KEY", configuration_id="streamlit_secrets", max_retries=int(secrets.get("MIP_LLM_MAX_RETRIES", 0)), max_output_tokens=int(secrets.get("MIP_LLM_MAX_OUTPUT_TOKENS", 1200)), timeout_seconds=float(secrets.get("MIP_LLM_TIMEOUT_SECONDS", 20)))

    @classmethod
    def from_environment(cls) -> "ProviderConfig":
        enabled = os.getenv("MIP_LLM_ENABLED", "").lower() in {"1", "true", "yes"}
        provider = os.getenv("MIP_LLM_PROVIDER", "disabled")
        model = os.getenv("MIP_LLM_MODEL", "")
        credential = os.getenv("MIP_LLM_API_KEY")
        if not enabled or not provider or not model or not credential:
            return cls()
        return cls(enabled=True, provider_id=provider, model_id=model, credential_reference="OPENAI_API_KEY", configuration_id="environment", max_retries=int(os.getenv("MIP_LLM_MAX_RETRIES", "0")), max_output_tokens=int(os.getenv("MIP_LLM_MAX_OUTPUT_TOKENS", "1200")), timeout_seconds=float(os.getenv("MIP_LLM_TIMEOUT_SECONDS", "20")), project=os.getenv("OPENAI_PROJECT"))
