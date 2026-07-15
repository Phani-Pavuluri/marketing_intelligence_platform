# Conversational Control Plane Capability Registry 001

Phase B adds the canonical metadata-only registry at `src/mip/control_plane/capability_registry.py`. It is the sole source of truth: an immutable, deterministically sorted tuple of Phase A `CapabilityDescriptor` values. There is no parallel JSON catalog.

The public interface exports `DEFAULT_CAPABILITY_REGISTRY`, `CAPABILITY_REGISTRY_VERSION`, `CapabilityRegistry`, `RegistryValidationIssue`, and `UnknownCapabilityError`. Lookup returns defensive copies; unknown IDs raise; filters are deterministic; the SHA-256 fingerprint covers canonical JSON and registry version.

All required platform, data/upload, MMM, planning, GeoX, calibration, artifact, report, dashboard, and decision-package identities are registered. Statuses are evidence-based: sample capabilities are fixture-backed, upload/readiness capabilities are readiness-only, live execution and simulation are blocked/future-engine, and explanatory/navigation capabilities are available or fixture-backed. Required and conditional inputs, artifact types, allowed/blocked claims, execution modes, release gates, workflow-node references, and retrieval identity filters are explicit.

Validation rejects duplicate/invalid IDs, unknown next-capability references, claim/input overlap, invalid workflow IDs, missing retrieval identity metadata, and incompatible blocked execution modes. It confirms planning simulation remains blocked. Descriptors contain metadata only: no executor, callable, provider, Streamlit, retrieval, or engine dependency is registered. Phase E retains ownership of graph traversal validation.

Next artifact: `MIP_CONVERSATIONAL_CONTROL_PLANE_PERSISTENT_WORKSPACE_AND_EVENTS_001`.
