"""Base model for all platform contracts."""

from pydantic import BaseModel, ConfigDict


class ContractBaseModel(BaseModel):
    """Strict base for cross-engine data contracts.

    Contracts are the shared interface between experimentation, MMM, calibration,
    recommendations, trust, and orchestration. Forbidding extra fields and validating
    assignment prevents silent schema drift and keeps LLM orchestration bound to
    certified, typed engine outputs rather than informal structures.
    """

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        use_enum_values=True,
        str_strip_whitespace=True,
    )
