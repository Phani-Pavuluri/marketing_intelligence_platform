"""Tests for MMM runtime adapter workflow."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from mip.contracts.mmm_existing_model_availability import (
    MMMExistingModelAvailabilityResult,
    MMMExistingModelAvailabilityStatus,
    MMMModelArtifact,
    MMMModelDiagnosticStatus,
    MMMModelPromotionStatus,
)
from mip.contracts.mmm_runtime_adapter import (
    DEFAULT_ADAPTER_PLACEHOLDER_REFERENCE,
    DEFAULT_GOVERNANCE_ADAPTER_REFERENCE,
    MMMRuntimeArtifactHandoff,
    MMMRuntimeCallDecision,
    MMMRuntimeCallIssueCode,
    MMMRuntimeCallRequest,
    MMMRuntimeCallResult,
    MMMRuntimeCallStatus,
    MMMRuntimeEngineKind,
    MMMRuntimeFailurePacket,
    MMMRuntimeReference,
)
from mip.contracts.planning_mmm_readiness_report_adapter import (
    PlanningMMMReadinessReportAdapterEnvelope,
    PlanningMMMReadinessReportAdapterResult,
    PlanningMMMReadinessReportAdapterStatus,
    PlanningMMMReadinessReportCompatibility,
    PlanningMMMReadinessReportCompatibilityMode,
)
from mip.contracts.planning_mmm_trusted_input_model_run_eligibility import (
    PlanningMMMModelRunEligibilityDecision,
    PlanningMMMModelRunEligibilityRequest,
    PlanningMMMModelRunEligibilityResult,
    PlanningMMMModelRunEligibilityStatus,
    PlanningMMMTrustedInputStatus,
)
from mip.workflows.mmm_runtime_adapter import prepare_mmm_runtime_call, summarize_mmm_runtime_call
from mip.workflows.planning_mmm_trusted_input_model_run_eligibility import (
    evaluate_planning_mmm_trusted_input_and_model_run_eligibility,
)

_WORKFLOW_SOURCE = Path("src/mip/workflows/mmm_runtime_adapter.py")
_CONTRACT_SOURCE = Path("src/mip/contracts/mmm_runtime_adapter.py")


def _compatibility() -> PlanningMMMReadinessReportCompatibility:
    return PlanningMMMReadinessReportCompatibility(
        mode=PlanningMMMReadinessReportCompatibilityMode.METADATA_COMPATIBLE,
        metadata_compatible=True,
    )


def _data_readiness() -> PlanningMMMReadinessReportAdapterResult:
    return PlanningMMMReadinessReportAdapterResult(
        request_id="data-readiness-1",
        status=PlanningMMMReadinessReportAdapterStatus.REPORT_ADAPTED,
        envelope=PlanningMMMReadinessReportAdapterEnvelope(
            envelope_id="env-data",
            source_workflow_readiness_status="ready_for_mmm_workflow_readiness",
            source_workflow_readiness_tier="ready_for_gated_workflow",
            readiness_report_status="ready",
            compatibility=_compatibility(),
            readiness_metadata={
                "has_historical_spend": True,
                "has_historical_outcome": True,
                "has_channel_taxonomy": True,
                "has_budget_constraints": False,
            },
            lineage={"data_stage": "adapter"},
        ),
    )


def _existing_model(
    *,
    status: MMMExistingModelAvailabilityStatus,
    requires_new_model_run: bool = False,
    requires_model_refresh: bool = False,
) -> MMMExistingModelAvailabilityResult:
    selected = None
    if status in {
        MMMExistingModelAvailabilityStatus.USABLE_EXISTING_MODEL,
        MMMExistingModelAvailabilityStatus.USABLE_EXISTING_MODEL_WITH_WARNINGS,
        MMMExistingModelAvailabilityStatus.REQUIRES_MODEL_REFRESH,
    }:
        selected = MMMModelArtifact(
            model_id="mmm-existing-1",
            artifact_fingerprint="fp-1",
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
            diagnostic_status=MMMModelDiagnosticStatus.PASSED,
            promotion_status=MMMModelPromotionStatus.PROMOTED_FOR_PLANNING,
        )
    return MMMExistingModelAvailabilityResult(
        request_id="existing-avail-1",
        status=status,
        selected_model=selected,
        requires_new_model_run=requires_new_model_run,
        requires_model_refresh=requires_model_refresh,
    )


def _eligibility(
    *,
    existing: MMMExistingModelAvailabilityResult | None = None,
    model_config_present: bool = False,
    model_config_id: str | None = None,
    allow_existing_model_reuse: bool = True,
) -> PlanningMMMModelRunEligibilityResult:
    return evaluate_planning_mmm_trusted_input_and_model_run_eligibility(
        PlanningMMMModelRunEligibilityRequest(
            request_id="eligibility-1",
            data_readiness_result=_data_readiness(),
            existing_model_availability_result=existing,
            model_config_present=model_config_present,
            model_config_id=model_config_id,
            allow_existing_model_reuse=allow_existing_model_reuse,
        )
    )


def _prepare(
    *,
    eligibility: PlanningMMMModelRunEligibilityResult | None = None,
    model_config_id: str | None = None,
    runtime_reference: MMMRuntimeReference | None = None,
    external_run_id: str | None = None,
    supplied_artifact_handoff: MMMRuntimeArtifactHandoff | None = None,
    supplied_failure_packet: MMMRuntimeFailurePacket | None = None,
) -> MMMRuntimeCallResult:
    return prepare_mmm_runtime_call(
        MMMRuntimeCallRequest(
            request_id="runtime-req-1",
            eligibility_result=eligibility,
            model_config_id=model_config_id,
            runtime_reference=runtime_reference,
            external_run_id=external_run_id,
            supplied_artifact_handoff=supplied_artifact_handoff,
            supplied_failure_packet=supplied_failure_packet,
            lineage={"upstream": "eligibility"},
        )
    )


def test_missing_eligibility_blocks() -> None:
    result = _prepare(eligibility=None)
    assert result.status == MMMRuntimeCallStatus.BLOCKED_BY_ELIGIBILITY
    assert result.decision == MMMRuntimeCallDecision.BLOCK_RUNTIME_CALL
    assert result.failure_packet is not None


def test_use_existing_model_creates_no_runtime_call() -> None:
    eligibility = _eligibility(
        existing=_existing_model(status=MMMExistingModelAvailabilityStatus.USABLE_EXISTING_MODEL)
    )
    result = _prepare(eligibility=eligibility)
    assert result.status == MMMRuntimeCallStatus.NOT_CALLED_EXISTING_MODEL_SELECTED
    assert result.decision == MMMRuntimeCallDecision.USE_EXISTING_MODEL_NO_RUNTIME_CALL
    assert result.runtime_called is False


def test_request_new_model_run_prepares_external_runtime_call() -> None:
    eligibility = _eligibility(
        existing=_existing_model(
            status=MMMExistingModelAvailabilityStatus.REQUIRES_NEW_MODEL_RUN,
            requires_new_model_run=True,
        ),
        model_config_present=True,
        model_config_id="cfg-new",
    )
    result = _prepare(eligibility=eligibility, model_config_id="cfg-new")
    assert result.status == MMMRuntimeCallStatus.READY_TO_CALL_EXTERNAL_RUNTIME
    assert result.decision == MMMRuntimeCallDecision.PREPARE_EXTERNAL_NEW_MODEL_RUN
    assert result.runtime_called is False
    assert result.metadata.get("requested_run_type") == "new_model_run"


def test_request_model_refresh_prepares_external_refresh_call() -> None:
    eligibility = _eligibility(
        existing=_existing_model(
            status=MMMExistingModelAvailabilityStatus.REQUIRES_MODEL_REFRESH,
            requires_model_refresh=True,
        ),
        model_config_present=True,
        model_config_id="cfg-refresh",
    )
    result = _prepare(eligibility=eligibility, model_config_id="cfg-refresh")
    assert result.status == MMMRuntimeCallStatus.READY_TO_CALL_EXTERNAL_RUNTIME
    assert result.decision == MMMRuntimeCallDecision.PREPARE_EXTERNAL_MODEL_REFRESH
    assert result.metadata.get("requested_run_type") == "model_refresh"


def test_blocked_eligibility_blocks_runtime_call() -> None:
    eligibility = _eligibility(model_config_present=False)
    eligibility = evaluate_planning_mmm_trusted_input_and_model_run_eligibility(
        PlanningMMMModelRunEligibilityRequest(
            request_id="eligibility-blocked",
            data_readiness_result=None,
        )
    )
    result = _prepare(eligibility=eligibility)
    assert result.status == MMMRuntimeCallStatus.BLOCKED_BY_ELIGIBILITY
    assert result.decision == MMMRuntimeCallDecision.BLOCK_RUNTIME_CALL


def test_deferred_eligibility_defers_runtime_call() -> None:
    from mip.contracts.planning_mmm_trusted_input_model_run_eligibility import (
        PlanningMMMModelRunEligibilityResult,
    )

    eligibility = PlanningMMMModelRunEligibilityResult(
        request_id="eligibility-deferred",
        trusted_input_status=PlanningMMMTrustedInputStatus.TRUSTED_INPUT_DEFERRED,
        eligibility_status=PlanningMMMModelRunEligibilityStatus.DEFERRED,
        decision=PlanningMMMModelRunEligibilityDecision.DEFER,
    )
    result = _prepare(eligibility=eligibility)
    assert result.status == MMMRuntimeCallStatus.DEFERRED
    assert result.decision == MMMRuntimeCallDecision.DEFER_RUNTIME_CALL


def test_missing_trusted_input_package_blocks_new_run() -> None:
    from mip.contracts.planning_mmm_trusted_input_model_run_eligibility import (
        PlanningMMMModelRunEligibilityResult,
    )

    eligibility = PlanningMMMModelRunEligibilityResult(
        request_id="eligibility-no-package",
        trusted_input_status=PlanningMMMTrustedInputStatus.TRUSTED_INPUT_READY,
        eligibility_status=PlanningMMMModelRunEligibilityStatus.REQUIRES_NEW_MODEL_RUN,
        decision=PlanningMMMModelRunEligibilityDecision.REQUEST_NEW_MODEL_RUN,
        requires_new_model_run=True,
        eligible_to_request_model_run=True,
        trusted_input_package=None,
    )
    result = _prepare(eligibility=eligibility, model_config_id="cfg-new")
    assert result.status == MMMRuntimeCallStatus.BLOCKED_MISSING_TRUSTED_INPUT_PACKAGE


def test_missing_model_config_blocks_new_run() -> None:
    from mip.contracts.planning_mmm_trusted_input_model_run_eligibility import (
        PlanningMMMModelRunEligibilityResult,
        PlanningMMMTrustedInputPackage,
    )

    eligibility = PlanningMMMModelRunEligibilityResult(
        request_id="eligibility-no-config",
        trusted_input_status=PlanningMMMTrustedInputStatus.TRUSTED_INPUT_READY,
        eligibility_status=PlanningMMMModelRunEligibilityStatus.REQUIRES_NEW_MODEL_RUN,
        decision=PlanningMMMModelRunEligibilityDecision.REQUEST_NEW_MODEL_RUN,
        requires_new_model_run=True,
        eligible_to_request_model_run=True,
        trusted_input_package=PlanningMMMTrustedInputPackage(
            package_id="trusted-input:pkg-1",
            request_id="eligibility-no-config",
            model_config_present=False,
        ),
    )
    result = _prepare(eligibility=eligibility)
    assert result.status == MMMRuntimeCallStatus.BLOCKED_MISSING_MODEL_CONFIG


def test_runtime_reference_preserved() -> None:
    reference = MMMRuntimeReference(
        runtime_id="custom-runtime-1",
        runtime_kind=MMMRuntimeEngineKind.EXTERNAL_SANDBOX_MMM_ENGINE,
        runtime_name="sandbox_mmm",
    )
    eligibility = _eligibility(
        existing=_existing_model(status=MMMExistingModelAvailabilityStatus.USABLE_EXISTING_MODEL)
    )
    result = _prepare(eligibility=eligibility, runtime_reference=reference)
    assert result.runtime_reference is not None
    assert result.runtime_reference.runtime_id == "custom-runtime-1"


def test_adapter_placeholder_reference_preserved() -> None:
    eligibility = _eligibility(
        existing=_existing_model(
            status=MMMExistingModelAvailabilityStatus.REQUIRES_NEW_MODEL_RUN,
            requires_new_model_run=True,
        ),
        model_config_present=True,
        model_config_id="cfg-new",
    )
    result = _prepare(eligibility=eligibility, model_config_id="cfg-new")
    assert result.metadata.get("adapter_placeholder_reference") == (
        DEFAULT_ADAPTER_PLACEHOLDER_REFERENCE
    )


def test_governance_adapter_reference_preserved() -> None:
    eligibility = _eligibility(
        existing=_existing_model(
            status=MMMExistingModelAvailabilityStatus.REQUIRES_NEW_MODEL_RUN,
            requires_new_model_run=True,
        ),
        model_config_present=True,
        model_config_id="cfg-new",
    )
    result = _prepare(eligibility=eligibility, model_config_id="cfg-new")
    assert result.metadata.get("governance_adapter_reference") == (
        DEFAULT_GOVERNANCE_ADAPTER_REFERENCE
    )


def test_lineage_preserved() -> None:
    eligibility = _eligibility(
        existing=_existing_model(status=MMMExistingModelAvailabilityStatus.USABLE_EXISTING_MODEL)
    )
    result = _prepare(eligibility=eligibility)
    assert result.lineage.get("upstream") == "eligibility"
    assert result.lineage.get("runtime_adapter_stage") == "mmm_runtime_adapter"


def test_failure_packet_created_for_blocked_state() -> None:
    result = _prepare(eligibility=None)
    assert result.failure_packet is not None
    assert MMMRuntimeCallIssueCode.FAILURE_PACKET_CREATED in result.issues


def test_external_artifact_handoff_accepted_as_uri_metadata_only() -> None:
    handoff = MMMRuntimeArtifactHandoff(
        handoff_id="handoff-1",
        request_id="runtime-req-1",
        external_run_id="ext-run-99",
        artifact_uris=["s3://bucket/model.json"],
        model_artifact_uri="s3://bucket/model.bin",
    )
    eligibility = _eligibility(
        existing=_existing_model(
            status=MMMExistingModelAvailabilityStatus.REQUIRES_NEW_MODEL_RUN,
            requires_new_model_run=True,
        ),
        model_config_present=True,
        model_config_id="cfg-new",
    )
    result = _prepare(
        eligibility=eligibility,
        model_config_id="cfg-new",
        external_run_id="ext-run-99",
        supplied_artifact_handoff=handoff,
    )
    assert result.status == MMMRuntimeCallStatus.EXTERNAL_RUNTIME_CALL_RECORDED
    assert result.runtime_called is True
    assert result.artifact_handoff is handoff
    assert result.artifact_handoff.artifact_uris == ["s3://bucket/model.json"]


def test_no_model_execution_in_sources() -> None:
    forbidden = (
        "import requests",
        "import httpx",
        "import urllib",
        "import socket",
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
    for path in (_WORKFLOW_SOURCE, _CONTRACT_SOURCE):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("#"):
                continue
            for token in forbidden:
                assert token not in line, f"{token} in {path}: {line}"


def test_boundary_issue_codes_present() -> None:
    eligibility = _eligibility(
        existing=_existing_model(status=MMMExistingModelAvailabilityStatus.USABLE_EXISTING_MODEL)
    )
    result = _prepare(eligibility=eligibility)
    assert MMMRuntimeCallIssueCode.NO_MODEL_EXECUTION in result.issues
    assert MMMRuntimeCallIssueCode.NO_POSTERIOR_CALCULATION in result.issues
    assert MMMRuntimeCallIssueCode.NO_TRUST_REPORT_CONSTRUCTION in result.issues
    assert MMMRuntimeCallIssueCode.NO_CLAIM_AUTHORIZATION in result.issues


def test_summarize_returns_metadata_only() -> None:
    eligibility = _eligibility(
        existing=_existing_model(status=MMMExistingModelAvailabilityStatus.USABLE_EXISTING_MODEL)
    )
    result = _prepare(eligibility=eligibility)
    summary = summarize_mmm_runtime_call(result)
    assert summary["runtime_called"] is False
    assert "recommendation" not in summary
