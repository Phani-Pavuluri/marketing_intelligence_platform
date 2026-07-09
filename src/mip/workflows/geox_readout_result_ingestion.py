"""GeoX readout result ingestion and explanation workflow.

Consumes Stage 3B MIP-wrapped package artifacts only. No panel_exp import or metric
recomputation.
"""

from __future__ import annotations

from mip.contracts.geox_panel_exp_runtime_call import (
    CLAIM_AUTHORIZATION_OWNER,
    GeoXPostTestSpendEvidenceArtifact,
    GeoXTrustedReadoutSpendHandoffArtifact,
)
from mip.contracts.geox_readout_result_ingestion import (
    GeoXReadoutClaimReadiness,
    GeoXReadoutExplanationAudience,
    GeoXReadoutResultEnvelope,
    GeoXReadoutResultExplanation,
    GeoXReadoutResultIngestionRequest,
    GeoXReadoutResultIngestionResult,
    GeoXReadoutResultIssueCode,
    GeoXReadoutResultStatus,
)

_READY_STATUSES = frozenset({"READY", "ready"})
_DIAGNOSTIC_STATUSES = frozenset({"PARTIAL_DIAGNOSTIC_ONLY", "partial_diagnostic_only"})


def ingest_geox_readout_result_for_explanation(
    request: GeoXReadoutResultIngestionRequest,
) -> GeoXReadoutResultIngestionResult:
    """Ingest Stage 3B package artifacts and produce a MIP-facing explanation envelope."""
    lineage = {
        **request.lineage,
        "ingestion_stage": "result_ingestion_and_explanation",
        "explanation_audience": str(request.audience),
    }
    warnings = list(dict.fromkeys(request.warnings))
    issues: list[GeoXReadoutResultIssueCode] = [
        GeoXReadoutResultIssueCode.ROI_ROAS_NOT_COMPUTED_IN_MIP,
        GeoXReadoutResultIssueCode.LIFT_NOT_COMPUTED_IN_MIP,
        GeoXReadoutResultIssueCode.CLAIM_AUTHORIZATION_DELEGATED,
        GeoXReadoutResultIssueCode.TRUST_REPORT_REQUIRED_FOR_CLAIMS,
        GeoXReadoutResultIssueCode.RECOMMENDATION_REQUIRES_DECISION_SURFACE,
    ]

    if request.evidence_artifact is None:
        return _blocked(
            request.request_id,
            GeoXReadoutResultStatus.BLOCKED_MISSING_EVIDENCE_ARTIFACT,
            issues + [GeoXReadoutResultIssueCode.MISSING_EVIDENCE_ARTIFACT],
            warnings,
            lineage,
        )

    if request.trusted_handoff_artifact is None:
        return _blocked(
            request.request_id,
            GeoXReadoutResultStatus.BLOCKED_MISSING_TRUSTED_HANDOFF_ARTIFACT,
            issues + [GeoXReadoutResultIssueCode.MISSING_TRUSTED_HANDOFF_ARTIFACT],
            warnings,
            lineage,
        )

    evidence = request.evidence_artifact
    handoff = request.trusted_handoff_artifact

    validation_error = _validate_package_artifacts(evidence, handoff)
    if validation_error is not None:
        return _blocked(
            request.request_id,
            GeoXReadoutResultStatus.BLOCKED_MALFORMED_PACKAGE_ARTIFACT,
            issues + [GeoXReadoutResultIssueCode.MALFORMED_PACKAGE_ARTIFACT],
            warnings + [validation_error],
            lineage,
        )

    readiness_status = evidence.readiness_status.strip()
    result_status, readiness_issues = _classify_package_readiness(readiness_status)
    if result_status == GeoXReadoutResultStatus.BLOCKED_MALFORMED_PACKAGE_ARTIFACT:
        return _blocked(
            request.request_id,
            result_status,
            issues + readiness_issues,
            warnings + [f"Unrecognized package readiness status: {readiness_status}"],
            lineage,
        )
    issues.extend(readiness_issues)

    package_warnings = _merge_warnings(evidence, handoff)
    if package_warnings:
        issues.append(GeoXReadoutResultIssueCode.PACKAGE_WARNINGS_PRESENT)
        warnings.extend(package_warnings)

    if "package_computed_spend_delta" in evidence.package_output_summary:
        issues.append(GeoXReadoutResultIssueCode.SPEND_DELTA_PACKAGE_COMPUTED)

    claim_readiness, claim_issues, claim_status = _resolve_claim_readiness(
        evidence, handoff, readiness_status
    )
    issues.extend(claim_issues)

    if claim_status is not None:
        return _blocked(
            request.request_id,
            claim_status,
            issues,
            warnings,
            lineage,
        )

    package_output_summary = (
        dict(evidence.package_output_summary)
        if request.include_package_output_summary
        else {}
    )
    trusted_handoff_summary = _trusted_handoff_summary(handoff)
    explanation = _build_explanation(
        evidence=evidence,
        handoff=handoff,
        audience=request.audience,
        result_status=result_status,
        claim_readiness=claim_readiness,
        package_warnings=package_warnings,
    )

    envelope = GeoXReadoutResultEnvelope(
        result_id=f"geox-readout-result:{evidence.experiment_id}:{request.request_id}",
        experiment_id=evidence.experiment_id,
        status=result_status,
        package_readiness_status=readiness_status,
        package_blocking_reasons=list(evidence.blocking_reasons),
        package_warnings=package_warnings,
        package_output_summary=package_output_summary,
        trusted_handoff_summary=trusted_handoff_summary,
        claim_readiness=claim_readiness,
        claim_authorization_owner=evidence.claim_authorization_owner,
        explanation=explanation,
        issues=_dedupe_issues(issues),
        warnings=list(dict.fromkeys(warnings)),
        lineage={
            **lineage,
            **evidence.source_lineage,
            "evidence_artifact_id": evidence.artifact_id,
            "trusted_handoff_artifact_id": handoff.artifact_id,
        },
    )

    return GeoXReadoutResultIngestionResult(
        request_id=request.request_id,
        status=result_status,
        result_envelope=envelope,
        registered_artifact_ref_optional=None,
        issues=_dedupe_issues(issues),
        warnings=list(dict.fromkeys(warnings)),
        lineage=lineage,
    )


def _validate_package_artifacts(
    evidence: GeoXPostTestSpendEvidenceArtifact,
    handoff: GeoXTrustedReadoutSpendHandoffArtifact,
) -> str | None:
    if not evidence.experiment_id.strip():
        return "evidence artifact missing experiment_id"
    if not evidence.readiness_status.strip():
        return "evidence artifact missing readiness_status"
    if not evidence.claim_authorization_owner.strip():
        return "evidence artifact missing claim_authorization_owner"
    if not handoff.experiment_id.strip():
        return "trusted handoff artifact missing experiment_id"
    if not handoff.claim_authorization_owner.strip():
        return "trusted handoff artifact missing claim_authorization_owner"
    if evidence.experiment_id != handoff.experiment_id:
        return "evidence and trusted handoff experiment_id mismatch"
    if not evidence.package_output_summary and not handoff.spend_readiness_summary:
        return "package artifact missing output summaries"
    return None


def _classify_package_readiness(
    readiness_status: str,
) -> tuple[GeoXReadoutResultStatus, list[GeoXReadoutResultIssueCode]]:
    normalized = readiness_status.strip()
    upper = normalized.upper()
    if upper in _READY_STATUSES:
        return GeoXReadoutResultStatus.EXPLAINED_READY_PACKAGE_RESULT, []
    if upper in _DIAGNOSTIC_STATUSES:
        return (
            GeoXReadoutResultStatus.EXPLAINED_DIAGNOSTIC_ONLY_PACKAGE_RESULT,
            [GeoXReadoutResultIssueCode.PACKAGE_READINESS_DIAGNOSTIC_ONLY],
        )
    if upper.startswith("BLOCKED_") or upper.startswith("blocked_"):
        return (
            GeoXReadoutResultStatus.EXPLAINED_BLOCKED_PACKAGE_RESULT,
            [GeoXReadoutResultIssueCode.PACKAGE_READINESS_BLOCKED],
        )
    return GeoXReadoutResultStatus.BLOCKED_MALFORMED_PACKAGE_ARTIFACT, [
        GeoXReadoutResultIssueCode.MALFORMED_PACKAGE_ARTIFACT
    ]


def _resolve_claim_readiness(
    evidence: GeoXPostTestSpendEvidenceArtifact,
    handoff: GeoXTrustedReadoutSpendHandoffArtifact,
    readiness_status: str,
) -> tuple[
    GeoXReadoutClaimReadiness,
    list[GeoXReadoutResultIssueCode],
    GeoXReadoutResultStatus | None,
]:
    issues: list[GeoXReadoutResultIssueCode] = []
    roi_status = handoff.package_handoff_summary.get("roi_claim_authorization_status", "")
    owner = evidence.claim_authorization_owner

    if roi_status == "NOT_EVALUATED":
        issues.append(GeoXReadoutResultIssueCode.CLAIM_AUTHORIZATION_NOT_EVALUATED)

    if owner != CLAIM_AUTHORIZATION_OWNER:
        if roi_status == "NOT_EVALUATED" or not owner.strip():
            return (
                GeoXReadoutClaimReadiness.NOT_EVALUATED,
                issues,
                GeoXReadoutResultStatus.BLOCKED_CLAIM_AUTHORIZATION_NOT_EVALUATED,
            )
        return GeoXReadoutClaimReadiness.NOT_AUTHORIZED, issues, None

    if readiness_status.upper() in _READY_STATUSES:
        return GeoXReadoutClaimReadiness.READY_FOR_TRUST_REPORT_REVIEW, issues, None
    return (
        GeoXReadoutClaimReadiness.DELEGATED_TO_CLAIM_AUTHORIZATION_RUNTIME,
        issues,
        None,
    )


def _merge_warnings(
    evidence: GeoXPostTestSpendEvidenceArtifact,
    handoff: GeoXTrustedReadoutSpendHandoffArtifact,
) -> list[str]:
    merged = list(evidence.warnings) + list(handoff.spend_warnings)
    return list(dict.fromkeys(item for item in merged if item))


def _trusted_handoff_summary(
    handoff: GeoXTrustedReadoutSpendHandoffArtifact,
) -> dict[str, str | bool]:
    summary: dict[str, str | bool] = {}
    for key, value in handoff.spend_readiness_summary.items():
        summary[str(key)] = value if isinstance(value, bool) else str(value)
    for key, value in handoff.package_handoff_summary.items():
        summary[str(key)] = str(value)
    if handoff.blocked_efficiency_metrics:
        summary["blocked_efficiency_metrics"] = ", ".join(handoff.blocked_efficiency_metrics)
    return summary


def _build_explanation(
    *,
    evidence: GeoXPostTestSpendEvidenceArtifact,
    handoff: GeoXTrustedReadoutSpendHandoffArtifact,
    audience: GeoXReadoutExplanationAudience,
    result_status: GeoXReadoutResultStatus,
    claim_readiness: GeoXReadoutClaimReadiness,
    package_warnings: list[str],
) -> GeoXReadoutResultExplanation:
    readiness = evidence.readiness_status
    blockers = evidence.blocking_reasons
    blocker_text = (
        "No package blockers reported."
        if not blockers
        else "Package blockers: " + "; ".join(blockers)
    )
    warning_text = (
        "No package warnings reported."
        if not package_warnings
        else "Package warnings: " + "; ".join(package_warnings)
    )

    if result_status == GeoXReadoutResultStatus.EXPLAINED_READY_PACKAGE_RESULT:
        readiness_explanation = (
            f"Package post-test spend readiness is {readiness}. "
            "MIP preserved package evidence without recomputing metrics."
        )
        next_action = (
            "Spend readiness artifact is available for downstream TrustReport and "
            "DecisionSurface review. This is not a business recommendation."
        )
        summary = "Package spend readiness is ready; MIP explanation only."
        business_safe = (
            "Spend readiness checks passed at the package layer. "
            "No business claim is authorized by MIP."
        )
    elif result_status == GeoXReadoutResultStatus.EXPLAINED_BLOCKED_PACKAGE_RESULT:
        readiness_explanation = (
            f"Package post-test spend readiness is blocked ({readiness}). "
            "MIP surfaced package blockers without recomputing spend or efficiency metrics."
        )
        next_action = _blocked_next_action(blockers, readiness)
        summary = "Package spend readiness is blocked; review missing inputs."
        business_safe = (
            "Spend readiness is not ready. Correct the listed input gaps before "
            "requesting claim review."
        )
    else:
        readiness_explanation = (
            f"Package post-test spend readiness is diagnostic-only ({readiness}). "
            "Use for diagnostics only, not production claim authorization."
        )
        next_action = (
            "Treat this as diagnostic package output only. "
            "Do not use for production claim authorization."
        )
        summary = "Package spend readiness is diagnostic-only."
        business_safe = "Diagnostic spend readiness only — not for production claims."

    claim_boundary = (
        f"Claim authorization owner: {evidence.claim_authorization_owner}. "
        f"MIP claim readiness: {claim_readiness.value}. "
        "MIP does not authorize ROI, ROAS, lift, or spend_delta claims. "
        "Efficiency metrics remain package-governed."
    )

    governance_notes = [
        "TrustReport is required before any claim authorization.",
        "DecisionSurface is required before business recommendations.",
        "RecommendationContract must not be bypassed.",
        "MIP ingests and explains package artifacts only.",
    ]

    technical_details = [
        f"evidence_artifact_id={evidence.artifact_id}",
        f"trusted_handoff_artifact_id={handoff.artifact_id}",
        f"package_readiness_status={readiness}",
        f"blocked_efficiency_metrics={handoff.blocked_efficiency_metrics}",
    ]
    if "package_computed_spend_delta" in evidence.package_output_summary:
        technical_details.append(
            "package_computed_spend_delta preserved in package_output_summary only"
        )

    if audience == GeoXReadoutExplanationAudience.BUSINESS:
        summary = business_safe
    elif audience == GeoXReadoutExplanationAudience.GOVERNANCE:
        summary = summary + " Governance boundaries apply before claim review."

    return GeoXReadoutResultExplanation(
        summary=summary,
        readiness_explanation=readiness_explanation,
        blocker_explanation=blocker_text,
        warning_explanation=warning_text,
        claim_boundary_explanation=claim_boundary,
        next_action=next_action,
        technical_details=technical_details,
        business_safe_summary=business_safe,
        governance_notes=governance_notes,
    )


def _blocked_next_action(blockers: list[str], readiness: str) -> str:
    if blockers:
        return (
            "Resolve package blockers before downstream review: "
            + "; ".join(blockers)
        )
    if "BASELINE" in readiness.upper() or "COUNTERFACTUAL" in readiness.upper():
        return (
            "Provide missing baseline or counterfactual spend definition "
            "required by the package runtime."
        )
    return "Correct missing or mismatched package inputs before retrying readout."


def _blocked(
    request_id: str,
    status: GeoXReadoutResultStatus,
    issues: list[GeoXReadoutResultIssueCode],
    warnings: list[str],
    lineage: dict[str, str],
) -> GeoXReadoutResultIngestionResult:
    return GeoXReadoutResultIngestionResult(
        request_id=request_id,
        status=status,
        result_envelope=None,
        registered_artifact_ref_optional=None,
        issues=_dedupe_issues(issues),
        warnings=list(dict.fromkeys(warnings)),
        lineage=lineage,
    )


def _dedupe_issues(
    issues: list[GeoXReadoutResultIssueCode],
) -> list[GeoXReadoutResultIssueCode]:
    seen: set[GeoXReadoutResultIssueCode] = set()
    ordered: list[GeoXReadoutResultIssueCode] = []
    for issue in issues:
        if issue not in seen:
            seen.add(issue)
            ordered.append(issue)
    return ordered
