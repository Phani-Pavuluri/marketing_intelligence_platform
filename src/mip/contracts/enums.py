"""Platform-wide enumerations for contracts and trust tiering."""

from enum import StrEnum


class ConfidenceTier(StrEnum):
    """Explicit confidence tier for analytical outputs and recommendations."""

    DECISION_READY = "decision_ready"
    DIRECTIONAL = "directional"
    DIAGNOSTIC_ONLY = "diagnostic_only"
    RESEARCH_ONLY = "research_only"
    BLOCKED = "blocked"


class ArtifactStatus(StrEnum):
    """Lifecycle status for evidence, models, and decision surfaces."""

    DRAFT = "draft"
    VALIDATED = "validated"
    CERTIFIED = "certified"
    DEPRECATED = "deprecated"
    BLOCKED = "blocked"


class ExperimentType(StrEnum):
    """Supported experiment design families."""

    GEOX = "geox"
    PANEL = "panel"
    AB_TEST = "ab_test"
    CONVERSION_LIFT = "conversion_lift"
    PLATFORM_LIFT = "platform_lift"
    SYNTHETIC_CONTROL = "synthetic_control"
    CALIBRATION_EXPERIMENT = "calibration_experiment"


class CausalQuantity(StrEnum):
    """Causal estimand quantity types."""

    LIFT = "lift"
    INCREMENTAL_IMPACT = "incremental_impact"
    DELTA_MU = "delta_mu"
    CONTRIBUTION = "contribution"
    ELASTICITY = "elasticity"
    ROI = "roi"
    IROAS = "iroas"


class EvidenceRole(StrEnum):
    """Role of evidence in the measurement stack."""

    CAUSAL_ANCHOR = "causal_anchor"
    CALIBRATION_SIGNAL = "calibration_signal"
    VALIDATION_SIGNAL = "validation_signal"
    DIAGNOSTIC_CONTEXT = "diagnostic_context"


class CompatibilityStatus(StrEnum):
    """Experiment-to-model compatibility verdict."""

    COMPATIBLE = "compatible"
    PARTIALLY_COMPATIBLE = "partially_compatible"
    INCOMPATIBLE = "incompatible"
    UNKNOWN = "unknown"


class RecommendationType(StrEnum):
    """Recommendation action categories."""

    BUDGET_SHIFT = "budget_shift"
    RUN_EXPERIMENT = "run_experiment"
    HOLD_BUDGET = "hold_budget"
    RECALIBRATE_MODEL = "recalibrate_model"
    INVESTIGATE = "investigate"
    MONITOR = "monitor"
    BLOCK_ACTION = "block_action"


class DecisionSurfaceType(StrEnum):
    """MMM and planning output surface types.

    Only ``full_panel_delta_mu`` is production decision-grade for budget planning.
    """

    FULL_PANEL_DELTA_MU = "full_panel_delta_mu"
    DIAGNOSTIC_CURVE = "diagnostic_curve"
    DECOMPOSITION = "decomposition"
    FORECAST = "forecast"
    RESEARCH_SURFACE = "research_surface"
