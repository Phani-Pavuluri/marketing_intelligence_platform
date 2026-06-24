"""Engine adapter interfaces for MMM and GeoX integration."""

from mip.adapters.base import (
    AdapterInputBundle,
    AdapterOutputBundle,
    AdapterRunKind,
    AdapterRunStatus,
    AdapterValidationReport,
    validate_adapter_output,
)
from mip.adapters.geox import (
    GeoXAdapterInput,
    GeoXAdapterOutputPlaceholder,
    build_geox_adapter_input,
    build_geox_adapter_output_placeholder,
)
from mip.adapters.governance import (
    AdapterRegistrationResult,
    adapter_output_id,
    adapter_output_to_decision_surface,
    adapter_output_to_experiment_evidence,
    gate_outcomes_for_adapter_output,
    register_adapter_output,
    trust_report_for_adapter_output,
)
from mip.adapters.mmm import (
    MMMAdapterInput,
    MMMAdapterOutputPlaceholder,
    build_mmm_adapter_input,
    build_mmm_adapter_output_placeholder,
)

AdapterInputBundle.model_rebuild(
    _types_namespace={
        "MMMAdapterInput": MMMAdapterInput,
        "GeoXAdapterInput": GeoXAdapterInput,
    }
)
AdapterOutputBundle.model_rebuild(
    _types_namespace={
        "MMMAdapterOutputPlaceholder": MMMAdapterOutputPlaceholder,
        "GeoXAdapterOutputPlaceholder": GeoXAdapterOutputPlaceholder,
    }
)

__all__ = [
    "AdapterInputBundle",
    "AdapterOutputBundle",
    "AdapterRegistrationResult",
    "AdapterRunKind",
    "AdapterRunStatus",
    "AdapterValidationReport",
    "GeoXAdapterInput",
    "GeoXAdapterOutputPlaceholder",
    "MMMAdapterInput",
    "MMMAdapterOutputPlaceholder",
    "adapter_output_id",
    "adapter_output_to_decision_surface",
    "adapter_output_to_experiment_evidence",
    "build_geox_adapter_input",
    "build_geox_adapter_output_placeholder",
    "build_mmm_adapter_input",
    "build_mmm_adapter_output_placeholder",
    "gate_outcomes_for_adapter_output",
    "register_adapter_output",
    "trust_report_for_adapter_output",
    "validate_adapter_output",
]
