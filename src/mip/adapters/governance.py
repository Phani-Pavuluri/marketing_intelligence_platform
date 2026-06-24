"""Wire adapter placeholder outputs into MIP governance artifacts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from mip.adapters.base import (
    AdapterOutputBundle,
    AdapterRunKind,
    AdapterRunStatus,
    validate_adapter_output,
)
from mip.contracts import (
    ArtifactStatus,
    ConfidenceTier,
    DecisionSurface,
    DecisionSurfaceType,
    DiagnosticSummary,
    Estimand,
    EvidenceRole,
    ExperimentEvidence,
    ExperimentType,
    TimeWindow,
    TrustReport,
)
from mip.contracts.enums import CausalQuantity
from mip.evaluation.gates import GateDecision, GateOutcome, GatePurpose
from mip.evidence.registry import EvidenceRegistry
from mip.trust.assembly import build_trust_report_from_gates
from mip.trust.router import build_trust_report_for_artifact, gate_outcomes_for_artifact

_PLACEHOLDER_UNSUPPORTED_CLAIMS = (
    "adapter_fixture_placeholder_only",
    "no_engine_execution",
    "no_numeric_effect_claims",
)


@dataclass(frozen=True)
class AdapterRegistrationResult:
    """Result of attempting to register an adapter output in governance paths."""

    adapter_output_id: str
    kind: AdapterRunKind
    source_config_marker: str
    artifact: ExperimentEvidence | DecisionSurface | None
    trust_report: TrustReport
    registered_in_registry: bool


def adapter_output_id(output_bundle: AdapterOutputBundle) -> str:
    """Return a stable adapter output identifier preserving lineage."""
    return f"adapter:{_enum_value(output_bundle.kind)}:{output_bundle.source_config_marker}"


def adapter_lineage_assumptions(output_bundle: AdapterOutputBundle) -> list[str]:
    """Return lineage assumptions attached to governance artifacts."""
    assumptions = [
        f"adapter_kind={_enum_value(output_bundle.kind)}",
        f"source_config_marker={output_bundle.source_config_marker}",
        f"adapter_output_id={adapter_output_id(output_bundle)}",
        f"adapter_status={_enum_value(output_bundle.status)}",
    ]
    if output_bundle.validation is not None:
        assumptions.append(
            f"adapter_validation_status={_enum_value(output_bundle.validation.status)}"
        )
    return assumptions


def adapter_output_to_experiment_evidence(
    output_bundle: AdapterOutputBundle,
) -> ExperimentEvidence:
    """Map a completed GeoX adapter output placeholder to ExperimentEvidence."""
    _require_completed_kind(output_bundle, AdapterRunKind.GEOX)
    validate_adapter_output(output_bundle)
    marker = output_bundle.source_config_marker
    placeholder = output_bundle.geox_output
    if placeholder is None:
        msg = "geox adapter output placeholder is required"
        raise ValueError(msg)

    diagnostics = DiagnosticSummary(
        passed=True,
        metrics={"adapter_fixture": True, "placeholder_only": True},
    )
    time_window = _placeholder_time_window()
    return ExperimentEvidence(
        evidence_id=adapter_output_id(output_bundle),
        experiment_type=ExperimentType.GEOX,
        evidence_role=EvidenceRole.DIAGNOSTIC_CONTEXT,
        estimand=Estimand(
            target_metric="outcome",
            causal_quantity=CausalQuantity.INCREMENTAL_IMPACT,
            unit="placeholder",
            time_window=time_window,
            treatment_definition="adapter_fixture_placeholder",
            aggregation_level="geo",
            unsupported_claims=list(_PLACEHOLDER_UNSUPPORTED_CLAIMS),
        ),
        estimate=0.0,
        design_diagnostics=diagnostics,
        execution_diagnostics=diagnostics,
        inference_diagnostics=diagnostics,
        quality_score=0.5,
        freshness_score=0.5,
        confidence_tier=ConfidenceTier.DIAGNOSTIC_ONLY,
        status=ArtifactStatus.DRAFT,
        created_at=datetime.now(tz=UTC),
        artifact_uri=f"adapter://geox/{marker}",
    )


def adapter_output_to_decision_surface(
    output_bundle: AdapterOutputBundle,
) -> DecisionSurface:
    """Map a completed MMM adapter output placeholder to DecisionSurface."""
    _require_completed_kind(output_bundle, AdapterRunKind.MMM)
    validate_adapter_output(output_bundle)
    marker = output_bundle.source_config_marker
    placeholder = output_bundle.mmm_output
    if placeholder is None:
        msg = "mmm adapter output placeholder is required"
        raise ValueError(msg)

    return DecisionSurface(
        surface_id=adapter_output_id(output_bundle),
        model_id=f"adapter-mmm:{marker}",
        surface_type=DecisionSurfaceType.DIAGNOSTIC_CURVE,
        decision_estimand=Estimand(
            target_metric="outcome",
            causal_quantity=CausalQuantity.CONTRIBUTION,
            unit="placeholder",
            time_window=_placeholder_time_window(),
            treatment_definition="adapter_fixture_placeholder",
            aggregation_level="full_panel",
            unsupported_claims=list(_PLACEHOLDER_UNSUPPORTED_CLAIMS),
        ),
        certification_status=ArtifactStatus.DRAFT,
        artifact_fingerprint=f"adapter-mmm-placeholder:{marker}",
        created_at=datetime.now(tz=UTC),
        warnings=["adapter_fixture_placeholder_only"],
        unsupported_claims=list(_PLACEHOLDER_UNSUPPORTED_CLAIMS),
    )


def trust_report_for_adapter_output(output_bundle: AdapterOutputBundle) -> TrustReport:
    """Build a TrustReport for an adapter output via existing gate paths."""
    validate_adapter_output(output_bundle)
    if output_bundle.status in (AdapterRunStatus.FAILED, AdapterRunStatus.BLOCKED):
        return _blocked_adapter_trust_report(output_bundle)

    if output_bundle.status != AdapterRunStatus.COMPLETED:
        msg = f"unsupported adapter status for trust reporting: {_enum_value(output_bundle.status)}"
        raise ValueError(msg)

    artifact = _artifact_for_completed_output(output_bundle)
    return build_trust_report_for_artifact(
        artifact,
        assumptions=adapter_lineage_assumptions(output_bundle),
        unsupported_claims=list(_PLACEHOLDER_UNSUPPORTED_CLAIMS),
    )


def register_adapter_output(
    registry: EvidenceRegistry,
    output_bundle: AdapterOutputBundle,
) -> AdapterRegistrationResult:
    """Register adapter output artifacts and build governed trust reports."""
    validate_adapter_output(output_bundle)
    output_id = adapter_output_id(output_bundle)

    if output_bundle.status in (AdapterRunStatus.FAILED, AdapterRunStatus.BLOCKED):
        return AdapterRegistrationResult(
            adapter_output_id=output_id,
            kind=output_bundle.kind,
            source_config_marker=output_bundle.source_config_marker,
            artifact=None,
            trust_report=_blocked_adapter_trust_report(output_bundle),
            registered_in_registry=False,
        )

    if output_bundle.kind == AdapterRunKind.GEOX:
        evidence = adapter_output_to_experiment_evidence(output_bundle)
        registry.add_evidence(evidence)
        trust_report = build_trust_report_for_artifact(
            evidence,
            assumptions=adapter_lineage_assumptions(output_bundle),
            unsupported_claims=list(_PLACEHOLDER_UNSUPPORTED_CLAIMS),
        )
        return AdapterRegistrationResult(
            adapter_output_id=output_id,
            kind=output_bundle.kind,
            source_config_marker=output_bundle.source_config_marker,
            artifact=evidence,
            trust_report=trust_report,
            registered_in_registry=True,
        )

    if output_bundle.kind == AdapterRunKind.MMM:
        surface = adapter_output_to_decision_surface(output_bundle)
        trust_report = build_trust_report_for_artifact(
            surface,
            assumptions=adapter_lineage_assumptions(output_bundle),
            unsupported_claims=list(_PLACEHOLDER_UNSUPPORTED_CLAIMS),
        )
        return AdapterRegistrationResult(
            adapter_output_id=output_id,
            kind=output_bundle.kind,
            source_config_marker=output_bundle.source_config_marker,
            artifact=surface,
            trust_report=trust_report,
            registered_in_registry=False,
        )

    msg = f"unsupported adapter kind for registration: {_enum_value(output_bundle.kind)}"
    raise ValueError(msg)


def gate_outcomes_for_adapter_output(output_bundle: AdapterOutputBundle) -> list[GateOutcome]:
    """Expose gate evaluation for a completed adapter output mapping."""
    if output_bundle.status in (AdapterRunStatus.FAILED, AdapterRunStatus.BLOCKED):
        msg = "failed or blocked adapter outputs do not map to gate-checked artifacts"
        raise ValueError(msg)
    artifact = _artifact_for_completed_output(output_bundle)
    return gate_outcomes_for_artifact(artifact)


def _artifact_for_completed_output(
    output_bundle: AdapterOutputBundle,
) -> ExperimentEvidence | DecisionSurface:
    if output_bundle.kind == AdapterRunKind.GEOX:
        return adapter_output_to_experiment_evidence(output_bundle)
    if output_bundle.kind == AdapterRunKind.MMM:
        return adapter_output_to_decision_surface(output_bundle)
    msg = f"unsupported adapter kind for artifact mapping: {_enum_value(output_bundle.kind)}"
    raise ValueError(msg)


def _require_completed_kind(
    output_bundle: AdapterOutputBundle,
    expected_kind: AdapterRunKind,
) -> None:
    if output_bundle.kind != expected_kind:
        msg = (
            f"{_enum_value(expected_kind)} mapping requires {_enum_value(expected_kind)} "
            f"adapter output, got {_enum_value(output_bundle.kind)}"
        )
        raise ValueError(msg)
    if output_bundle.status != AdapterRunStatus.COMPLETED:
        msg = f"completed adapter output required, got {_enum_value(output_bundle.status)}"
        raise ValueError(msg)


def _blocked_adapter_trust_report(output_bundle: AdapterOutputBundle) -> TrustReport:
    output_id = adapter_output_id(output_bundle)
    reason = output_bundle.reason or "adapter_output_blocked"
    gate_outcome = GateOutcome(
        artifact_id=output_id,
        artifact_type=f"adapter_{_enum_value(output_bundle.kind)}_output",
        purpose=GatePurpose.TRUST_REPORTING,
        decision=GateDecision.BLOCK,
        max_confidence_tier=ConfidenceTier.BLOCKED,
        reason_codes=[reason],
    )
    return build_trust_report_from_gates(
        trust_report_id=f"trust_report:adapter_output:{output_id}",
        output_id=output_id,
        output_type=f"adapter_{_enum_value(output_bundle.kind)}_output",
        gate_outcomes=[gate_outcome],
        assumptions=adapter_lineage_assumptions(output_bundle),
        unsupported_claims=list(_PLACEHOLDER_UNSUPPORTED_CLAIMS),
    )


def _placeholder_time_window() -> TimeWindow:
    return TimeWindow(
        start=datetime(2025, 1, 1, tzinfo=UTC),
        end=datetime(2025, 6, 1, tzinfo=UTC),
    )


def _enum_value(value: object) -> str:
    if isinstance(value, str):
        return value
    return str(getattr(value, "value", value))
