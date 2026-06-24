"""In-memory registry for experiment evidence and calibration signals."""

from mip.contracts import (
    ArtifactStatus,
    CalibrationSignal,
    CausalQuantity,
    CompatibilityStatus,
    ConfidenceTier,
    ExperimentEvidence,
    ExperimentType,
    TrustReport,
)
from mip.trust.router import build_trust_report_for_artifact


class EvidenceRegistryError(Exception):
    """Base exception for evidence registry errors."""


class DuplicateEvidenceError(EvidenceRegistryError):
    """Raised when evidence_id already exists in the registry."""


class DuplicateCalibrationSignalError(EvidenceRegistryError):
    """Raised when calibration_id already exists in the registry."""


class MissingEvidenceError(EvidenceRegistryError):
    """Raised when evidence_id is not found in the registry."""


class MissingCalibrationSignalError(EvidenceRegistryError):
    """Raised when calibration_id is not found in the registry."""


class EvidenceRegistry:
    """Typed in-memory store for experiment evidence and calibration signals."""

    def __init__(self) -> None:
        self._evidence: dict[str, ExperimentEvidence] = {}
        self._calibration_signals: dict[str, CalibrationSignal] = {}

    def add_evidence(self, evidence: ExperimentEvidence) -> None:
        """Register experiment evidence by evidence_id."""
        if evidence.evidence_id in self._evidence:
            msg = f"evidence_id already exists: {evidence.evidence_id}"
            raise DuplicateEvidenceError(msg)
        self._evidence[evidence.evidence_id] = evidence

    def add_calibration_signal(self, signal: CalibrationSignal) -> None:
        """Register a calibration signal by calibration_id."""
        if signal.calibration_id in self._calibration_signals:
            msg = f"calibration_id already exists: {signal.calibration_id}"
            raise DuplicateCalibrationSignalError(msg)
        self._calibration_signals[signal.calibration_id] = signal

    def get_evidence(self, evidence_id: str) -> ExperimentEvidence:
        """Retrieve experiment evidence by ID."""
        if not evidence_id.strip():
            raise MissingEvidenceError("evidence_id cannot be empty")
        try:
            return self._evidence[evidence_id]
        except KeyError as exc:
            msg = f"evidence not found: {evidence_id}"
            raise MissingEvidenceError(msg) from exc

    def get_calibration_signal(self, calibration_id: str) -> CalibrationSignal:
        """Retrieve a calibration signal by ID."""
        if not calibration_id.strip():
            raise MissingCalibrationSignalError("calibration_id cannot be empty")
        try:
            return self._calibration_signals[calibration_id]
        except KeyError as exc:
            msg = f"calibration signal not found: {calibration_id}"
            raise MissingCalibrationSignalError(msg) from exc

    def list_evidence(self) -> list[ExperimentEvidence]:
        """List all evidence sorted by created_at, then evidence_id."""
        return sorted(
            self._evidence.values(),
            key=lambda item: (item.created_at, item.evidence_id),
        )

    def list_calibration_signals(self) -> list[CalibrationSignal]:
        """List all calibration signals sorted by calibration_id."""
        return sorted(self._calibration_signals.values(), key=lambda item: item.calibration_id)

    def find_evidence(
        self,
        *,
        experiment_type: ExperimentType | None = None,
        target_metric: str | None = None,
        causal_quantity: CausalQuantity | None = None,
        confidence_tier: ConfidenceTier | None = None,
        status: ArtifactStatus | None = None,
        min_quality_score: float | None = None,
        min_freshness_score: float | None = None,
        scope_contains: dict[str, str] | None = None,
    ) -> list[ExperimentEvidence]:
        """Find evidence matching all provided filters (AND semantics)."""
        _validate_unit_interval(min_quality_score, "min_quality_score")
        _validate_unit_interval(min_freshness_score, "min_freshness_score")

        metric_filter = target_metric.strip() if target_metric is not None else None

        results: list[ExperimentEvidence] = []
        for evidence in self._evidence.values():
            if experiment_type is not None and evidence.experiment_type != experiment_type:
                continue
            if metric_filter is not None:
                evidence_metric = evidence.estimand.target_metric.strip()
                if evidence_metric != metric_filter:
                    continue
            if causal_quantity is not None and evidence.estimand.causal_quantity != causal_quantity:
                continue
            if confidence_tier is not None and evidence.confidence_tier != confidence_tier:
                continue
            if status is not None and evidence.status != status:
                continue
            if min_quality_score is not None and evidence.quality_score < min_quality_score:
                continue
            if min_freshness_score is not None and evidence.freshness_score < min_freshness_score:
                continue
            if scope_contains is not None and not _scope_matches(
                evidence.estimand.scope, scope_contains
            ):
                continue
            results.append(evidence)

        return sorted(results, key=lambda item: (item.created_at, item.evidence_id))

    def find_calibration_signals(
        self,
        *,
        source_evidence_id: str | None = None,
        target_model_id: str | None = None,
        compatibility_status: CompatibilityStatus | None = None,
        min_weight: float | None = None,
        min_freshness_decay: float | None = None,
        confidence_tier: ConfidenceTier | None = None,
    ) -> list[CalibrationSignal]:
        """Find calibration signals matching all provided filters (AND semantics)."""
        _validate_unit_interval(min_weight, "min_weight")
        _validate_unit_interval(min_freshness_decay, "min_freshness_decay")

        results: list[CalibrationSignal] = []
        for signal in self._calibration_signals.values():
            if source_evidence_id is not None and signal.source_evidence_id != source_evidence_id:
                continue
            if target_model_id is not None and signal.target_model_id != target_model_id:
                continue
            if (
                compatibility_status is not None
                and signal.compatibility_status != compatibility_status
            ):
                continue
            if min_weight is not None and signal.weight < min_weight:
                continue
            if min_freshness_decay is not None and signal.freshness_decay < min_freshness_decay:
                continue
            if confidence_tier is not None and signal.confidence_tier != confidence_tier:
                continue
            results.append(signal)

        return sorted(results, key=lambda item: item.calibration_id)

    def trust_report_for_evidence(self, evidence_id: str) -> TrustReport:
        """Build a trust report for registered experiment evidence."""
        return build_trust_report_for_artifact(self.get_evidence(evidence_id))

    def trust_report_for_calibration_signal(self, calibration_id: str) -> TrustReport:
        """Build a trust report for a registered calibration signal."""
        return build_trust_report_for_artifact(self.get_calibration_signal(calibration_id))

    def __len__(self) -> int:
        """Return total number of evidence and calibration signal records."""
        return len(self._evidence) + len(self._calibration_signals)


def _validate_unit_interval(value: float | None, field_name: str) -> None:
    if value is None:
        return
    if not 0.0 <= value <= 1.0:
        msg = f"{field_name} must be between 0 and 1"
        raise ValueError(msg)


def _scope_matches(
    scope: dict[str, str | list[str]],
    scope_contains: dict[str, str],
) -> bool:
    for key, requested in scope_contains.items():
        if key not in scope:
            return False
        actual = scope[key]
        if isinstance(actual, str):
            if actual != requested:
                return False
        elif requested not in actual:
            return False
    return True
