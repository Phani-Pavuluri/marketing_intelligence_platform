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
        SiblingFixtureExport,
        SiblingFixtureSource,
        assert_safe_sibling_fixture_export,
        build_geox_adapter_input,
        build_mmm_adapter_input,
        load_sibling_fixture_export,
        register_adapter_output,
        register_sibling_fixture_export,
        sibling_fixture_to_adapter_output,
        trust_report_for_adapter_output,
        trust_report_for_sibling_fixture,
        validate_adapter_output,
        validate_sibling_fixture_export,
    )

    assert AdapterRunKind.MMM.value == "mmm"
    assert AdapterRunStatus.VALIDATED.value == "validated"
    assert callable(build_mmm_adapter_input)
    assert callable(build_geox_adapter_input)
    assert callable(validate_adapter_output)
    assert callable(register_adapter_output)
    assert callable(trust_report_for_adapter_output)
    assert callable(validate_sibling_fixture_export)
    assert callable(trust_report_for_sibling_fixture)
    assert callable(register_sibling_fixture_export)
    assert callable(assert_safe_sibling_fixture_export)
    assert callable(load_sibling_fixture_export)
    assert callable(sibling_fixture_to_adapter_output)
    assert AdapterInputBundle is not None
    assert AdapterOutputBundle is not None
    assert AdapterValidationReport is not None
    assert MMMAdapterInput is not None
    assert GeoXAdapterInput is not None
    assert SiblingFixtureExport is not None
    assert SiblingFixtureSource is not None
