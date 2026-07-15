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

    @classmethod
    def from_environment(cls) -> "ProviderConfig":
        enabled = os.getenv("MIP_LLM_ENABLED", "").lower() in {"1", "true", "yes"}
        provider = os.getenv("MIP_LLM_PROVIDER", "disabled")
        model = os.getenv("MIP_LLM_MODEL", "")
        credential = os.getenv("MIP_LLM_API_KEY")
        if not enabled or not provider or not model or not credential:
            return cls()
        return cls(enabled=True, provider_id=provider, model_id=model, credential_reference="MIP_LLM_API_KEY", base_url=os.getenv("MIP_LLM_BASE_URL"), configuration_id="environment")
