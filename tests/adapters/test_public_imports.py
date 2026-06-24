"""Tests for public mip.adapters exports."""


def test_public_imports() -> None:
    from mip.adapters import (
        AdapterInputBundle,
        AdapterOutputBundle,
        AdapterRunKind,
        AdapterRunStatus,
        AdapterValidationReport,
        GeoXAdapterInput,
        MMMAdapterInput,
        build_geox_adapter_input,
        build_mmm_adapter_input,
        validate_adapter_output,
    )

    assert AdapterRunKind.MMM.value == "mmm"
    assert AdapterRunStatus.VALIDATED.value == "validated"
    assert callable(build_mmm_adapter_input)
    assert callable(build_geox_adapter_input)
    assert callable(validate_adapter_output)
    assert AdapterInputBundle is not None
    assert AdapterOutputBundle is not None
    assert AdapterValidationReport is not None
    assert MMMAdapterInput is not None
    assert GeoXAdapterInput is not None
