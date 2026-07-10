"""Tests for MMM existing model availability gate workflow."""

from __future__ import annotations

from datetime import UTC, date, datetime
from pathlib import Path

from mip.contracts.mmm_existing_model_availability import (
    MMMExistingModelAvailabilityIssueCode,
    MMMExistingModelAvailabilityRequest,
    MMMExistingModelAvailabilityResult,
    MMMExistingModelAvailabilityStatus,
    MMMModelAllowedUse,
    MMMModelArtifact,
    MMMModelArtifactQuery,
    MMMModelDiagnosticStatus,
    MMMModelPromotionStatus,
)
from mip.workflows.mmm_existing_model_availability import (
    evaluate_mmm_existing_model_availability,
    summarize_mmm_existing_model_availability,
)

_CONTRACT_SOURCE = Path("src/mip/contracts/mmm_existing_model_availability.py")
_WORKFLOW_SOURCE = Path("src/mip/workflows/mmm_existing_model_availability.py")
_REFERENCE_DATE = date(2026, 6, 1)


def _artifact(
    *,
    model_id: str,
    geo_scope: list[str] | None = None,
    business_unit: str | None = "bu-retail",
    product_scope: list[str] | None = None,
    channels: list[str] | None = None,
    metrics: list[str] | None = None,
    freshness_date: date | None = None,
    diagnostic_status: MMMModelDiagnosticStatus = MMMModelDiagnosticStatus.PASSED,
    promotion_status: MMMModelPromotionStatus = MMMModelPromotionStatus.PROMOTED_FOR_PLANNING,
    allowed_uses: list[MMMModelAllowedUse] | None = None,
    trust_report_id: str | None = None,
    decision_surface_id: str | None = None,
    model_calibration_readiness_id: str | None = None,
) -> MMMModelArtifact:
    return MMMModelArtifact(
        model_id=model_id,
        artifact_fingerprint=f"fp-{model_id}",
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
        training_start_date=date(2025, 1, 1),
        training_end_date=date(2025, 12, 31),
        data_freshness_date=freshness_date or date(2026, 5, 1),
        geo_scope=geo_scope or ["US"],
        business_unit=business_unit,
        product_scope=product_scope or ["product-a"],
        channels=channels or ["search", "social", "tv"],
        metrics=metrics or ["revenue"],
        diagnostic_status=diagnostic_status,
        promotion_status=promotion_status,
        allowed_uses=allowed_uses
        or [
            MMMModelAllowedUse.BUDGET_PLANNING,
            MMMModelAllowedUse.SCENARIO_SIMULATION,
            MMMModelAllowedUse.READ_ONLY_SUMMARY,
        ],
        trust_report_id=trust_report_id,
        decision_surface_id=decision_surface_id,
        model_calibration_readiness_id=model_calibration_readiness_id,
    )


def _query(
    *,
    intended_use: MMMModelAllowedUse = MMMModelAllowedUse.BUDGET_PLANNING,
    geo_scope: str | None = "US",
    business_unit: str | None = "bu-retail",
    product_scope: str | None = "product-a",
    channels: list[str] | None = None,
    metric: str | None = "revenue",
    max_model_age_days: int = 180,
    require_promoted: bool = True,
    require_diagnostics_passed: bool = True,
    require_trust_metadata: bool = False,
) -> MMMModelArtifactQuery:
    return MMMModelArtifactQuery(
        request_id="query-1",
        intended_use=intended_use,
        geo_scope=geo_scope,
        business_unit=business_unit,
        product_scope=product_scope,
        channels=channels or ["search", "social"],
        metric=metric,
        planning_end_date=_REFERENCE_DATE,
        max_model_age_days=max_model_age_days,
        require_promoted=require_promoted,
        require_diagnostics_passed=require_diagnostics_passed,
        require_trust_metadata=require_trust_metadata,
    )


def _evaluate(
    *,
    candidates: list[MMMModelArtifact],
    query: MMMModelArtifactQuery | None = None,
) -> MMMExistingModelAvailabilityResult:
    return evaluate_mmm_existing_model_availability(
        MMMExistingModelAvailabilityRequest(
            request_id="avail-1",
            query=query or _query(),
            candidate_models=candidates,
        )
    )


def test_usable_existing_model() -> None:
    result = _evaluate(candidates=[_artifact(model_id="mmm-usable")])
    assert result.status == MMMExistingModelAvailabilityStatus.USABLE_EXISTING_MODEL
    assert result.selected_model is not None
    assert result.selected_model.model_id == "mmm-usable"
    assert result.requires_new_model_run is False
    assert MMMExistingModelAvailabilityIssueCode.MODEL_SELECTED in result.issues


def test_usable_existing_model_with_warnings() -> None:
    result = _evaluate(
        candidates=[
            _artifact(
                model_id="mmm-warn",
                diagnostic_status=MMMModelDiagnosticStatus.PASSED_WITH_WARNINGS,
            )
        ]
    )
    assert result.status == MMMExistingModelAvailabilityStatus.USABLE_EXISTING_MODEL_WITH_WARNINGS
    assert result.warnings


def test_no_candidate_requires_new_run() -> None:
    result = _evaluate(candidates=[])
    assert result.status == MMMExistingModelAvailabilityStatus.BLOCKED_NO_CANDIDATE_MODEL
    assert result.requires_new_model_run is True
    assert MMMExistingModelAvailabilityIssueCode.NO_CANDIDATE_MODEL in result.issues


def test_scope_mismatch() -> None:
    result = _evaluate(
        candidates=[_artifact(model_id="mmm-scope", geo_scope=["EU"])],
        query=_query(geo_scope="US"),
    )
    assert result.status == MMMExistingModelAvailabilityStatus.BLOCKED_SCOPE_MISMATCH
    assert result.requires_new_model_run is True


def test_metric_mismatch() -> None:
    result = _evaluate(
        candidates=[_artifact(model_id="mmm-metric", metrics=["orders"])],
        query=_query(metric="revenue"),
    )
    assert result.status == MMMExistingModelAvailabilityStatus.BLOCKED_METRIC_MISMATCH
    assert result.requires_new_model_run is True


def test_channel_mismatch() -> None:
    result = _evaluate(
        candidates=[_artifact(model_id="mmm-channel", channels=["search"])],
        query=_query(channels=["search", "tv"]),
    )
    assert result.status == MMMExistingModelAvailabilityStatus.BLOCKED_CHANNEL_MISMATCH
    assert result.requires_new_model_run is True


def test_stale_model_requires_refresh() -> None:
    result = _evaluate(
        candidates=[
            _artifact(
                model_id="mmm-stale",
                freshness_date=date(2025, 1, 1),
            )
        ],
        query=_query(max_model_age_days=90),
    )
    assert result.status == MMMExistingModelAvailabilityStatus.REQUIRES_MODEL_REFRESH
    assert result.requires_model_refresh is True
    assert MMMExistingModelAvailabilityIssueCode.MODEL_STALE in result.issues


def test_diagnostics_failed() -> None:
    result = _evaluate(
        candidates=[
            _artifact(
                model_id="mmm-diag",
                diagnostic_status=MMMModelDiagnosticStatus.FAILED,
            )
        ]
    )
    assert result.status == MMMExistingModelAvailabilityStatus.BLOCKED_DIAGNOSTICS_FAILED
    assert result.requires_new_model_run is True


def test_not_promoted() -> None:
    result = _evaluate(
        candidates=[
            _artifact(
                model_id="mmm-nopromo",
                promotion_status=MMMModelPromotionStatus.NOT_PROMOTED,
            )
        ]
    )
    assert result.status == MMMExistingModelAvailabilityStatus.BLOCKED_NOT_PROMOTED
    assert result.requires_new_model_run is True


def test_diagnostic_only_blocked_for_budget_planning() -> None:
    result = _evaluate(
        candidates=[
            _artifact(
                model_id="mmm-diag-only",
                promotion_status=MMMModelPromotionStatus.PROMOTED_FOR_DIAGNOSTIC_ONLY,
            )
        ],
        query=_query(intended_use=MMMModelAllowedUse.BUDGET_PLANNING),
    )
    assert result.status == MMMExistingModelAvailabilityStatus.DIAGNOSTIC_ONLY
    assert result.requires_new_model_run is True


def test_intended_use_not_allowed() -> None:
    result = _evaluate(
        candidates=[
            _artifact(
                model_id="mmm-use",
                allowed_uses=[MMMModelAllowedUse.READ_ONLY_SUMMARY],
            )
        ],
        query=_query(intended_use=MMMModelAllowedUse.BUDGET_OPTIMIZATION),
    )
    assert result.status == MMMExistingModelAvailabilityStatus.BLOCKED_USE_NOT_ALLOWED
    assert result.requires_new_model_run is True


def test_missing_trust_metadata_when_required() -> None:
    result = _evaluate(
        candidates=[_artifact(model_id="mmm-notrust")],
        query=_query(require_trust_metadata=True),
    )
    assert result.status == MMMExistingModelAvailabilityStatus.BLOCKED_MISSING_TRUST_METADATA
    assert result.requires_new_model_run is True


def test_deterministic_best_candidate_selection() -> None:
    older = _artifact(
        model_id="mmm-older",
        freshness_date=date(2026, 3, 1),
    )
    newer = _artifact(
        model_id="mmm-newer",
        freshness_date=date(2026, 5, 15),
    )
    result = _evaluate(candidates=[older, newer])
    assert result.status == MMMExistingModelAvailabilityStatus.USABLE_EXISTING_MODEL
    assert result.selected_model is not None
    assert result.selected_model.model_id == "mmm-newer"


def test_no_model_execution_or_artifact_loading_in_sources() -> None:
    forbidden_import_lines = (
        "import pickle",
        "import joblib",
        "mlflow.pyfunc.load_model",
        "load_model(",
        ".fit(",
        ".predict(",
        ".sample(",
        "DecisionSurface(",
        "RecommendationContract(",
        "TrustReport(",
    )
    for path in (_CONTRACT_SOURCE, _WORKFLOW_SOURCE):
        content = path.read_text(encoding="utf-8")
        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            for token in forbidden_import_lines:
                assert token not in line, f"{token} found in {path}: {line}"


def test_decision_surface_and_trust_report_references_metadata_only() -> None:
    result = _evaluate(
        candidates=[
            _artifact(
                model_id="mmm-meta",
                trust_report_id="trust-meta-1",
                decision_surface_id="surface-meta-1",
                model_calibration_readiness_id="readiness-meta-1",
            )
        ]
    )
    assert result.selected_model is not None
    assert result.selected_model.decision_surface_id == "surface-meta-1"
    assert result.selected_model.trust_report_id == "trust-meta-1"
    assert (
        MMMExistingModelAvailabilityIssueCode.DECISION_SURFACE_REFERENCE_PRESENT in result.issues
    )
    assert (
        MMMExistingModelAvailabilityIssueCode.MODEL_CALIBRATION_READINESS_REFERENCE_PRESENT
        in result.issues
    )
    assert MMMExistingModelAvailabilityIssueCode.NO_DECISION_SURFACE_EXECUTION in result.issues
    assert MMMExistingModelAvailabilityIssueCode.NO_CLAIM_AUTHORIZATION in result.issues


def test_summarize_returns_metadata_only() -> None:
    result = _evaluate(candidates=[_artifact(model_id="mmm-summary")])
    summary = summarize_mmm_existing_model_availability(result)
    assert summary["status"] == MMMExistingModelAvailabilityStatus.USABLE_EXISTING_MODEL.value
    assert summary["selected_model_id"] == "mmm-summary"
    assert "recommendation" not in summary
    assert "budget_recommendation" not in summary
