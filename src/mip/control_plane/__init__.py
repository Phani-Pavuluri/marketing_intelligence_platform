"""Metadata-only conversational control-plane services."""

from mip.control_plane.capability_registry import (
    CAPABILITY_REGISTRY_VERSION,
    DEFAULT_CAPABILITY_REGISTRY,
    CapabilityRegistry,
    RegistryValidationIssue,
    UnknownCapabilityError,
)

__all__ = [
    "CAPABILITY_REGISTRY_VERSION",
    "DEFAULT_CAPABILITY_REGISTRY",
    "CapabilityRegistry",
    "RegistryValidationIssue",
    "UnknownCapabilityError",
]
