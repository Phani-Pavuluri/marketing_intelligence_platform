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
from mip.adapters.sibling_export_hooks import (
    SiblingExportDirectoryRef,
    SiblingExportDiscoveryResult,
    SiblingExportHookStatus,
    SiblingExportRegistrationResult,
    assert_safe_sibling_export_hook_result,
    build_default_sibling_export_hook_sections,
    default_sample_export_directory,
    default_sample_export_directory_ref,
    discover_sibling_export_files,
    load_sibling_exports_from_directory,
    register_sibling_exports_from_directory,
    sibling_export_discovery_sections,
    validate_sibling_export_directory,
)
from mip.adapters.sibling_fixtures import (
    SiblingFixtureArtifactKind,
    SiblingFixtureExport,
    SiblingFixtureRegistrationResult,
    SiblingFixtureSource,
    SiblingFixtureValidationStatus,
    assert_safe_sibling_fixture_export,
    build_default_sibling_fixture_import_sections,
    default_geox_sibling_fixture_path,
    default_mmm_sibling_fixture_path,
    load_sibling_fixture_export,
    register_sibling_fixture_export,
    sibling_fixture_import_sections,
    sibling_fixture_to_adapter_output,
    trust_report_for_sibling_fixture,
    validate_sibling_fixture_export,
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
    "SiblingFixtureArtifactKind",
    "SiblingFixtureExport",
    "SiblingFixtureRegistrationResult",
    "SiblingFixtureSource",
    "SiblingFixtureValidationStatus",
    "assert_safe_sibling_fixture_export",
    "build_default_sibling_fixture_import_sections",
    "default_geox_sibling_fixture_path",
    "default_mmm_sibling_fixture_path",
    "load_sibling_fixture_export",
    "register_sibling_fixture_export",
    "sibling_fixture_import_sections",
    "sibling_fixture_to_adapter_output",
    "trust_report_for_sibling_fixture",
    "validate_sibling_fixture_export",
    "SiblingExportDirectoryRef",
    "SiblingExportDiscoveryResult",
    "SiblingExportHookStatus",
    "SiblingExportRegistrationResult",
    "assert_safe_sibling_export_hook_result",
    "build_default_sibling_export_hook_sections",
    "default_sample_export_directory",
    "default_sample_export_directory_ref",
    "discover_sibling_export_files",
    "load_sibling_exports_from_directory",
    "register_sibling_exports_from_directory",
    "sibling_export_discovery_sections",
    "validate_sibling_export_directory",
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
