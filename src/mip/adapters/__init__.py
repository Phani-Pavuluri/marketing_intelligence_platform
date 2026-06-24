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
    "AdapterRunKind",
    "AdapterRunStatus",
    "AdapterValidationReport",
    "GeoXAdapterInput",
    "GeoXAdapterOutputPlaceholder",
    "MMMAdapterInput",
    "MMMAdapterOutputPlaceholder",
    "build_geox_adapter_input",
    "build_geox_adapter_output_placeholder",
    "build_mmm_adapter_input",
    "build_mmm_adapter_output_placeholder",
    "validate_adapter_output",
]
