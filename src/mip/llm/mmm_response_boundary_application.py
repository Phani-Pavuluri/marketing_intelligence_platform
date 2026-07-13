"""Narrow metadata-only application packaging for MMM LLM response boundary.

Packages deterministic rendered MMM planning response sections into a
JSON-safe application-facing payload for a future LLM/user-facing layer.

Does not call an LLM/provider, assemble prompts, generate user-facing answers,
create DecisionSurface, bypass TrustReport, create RecommendationContract,
or authorize planning/spend/ROI/budget recommendations.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any, Mapping, Sequence

from pydantic import Field, field_validator

from mip.contracts.base import ContractBaseModel

ARTIFACT_ID = "MIP_MMM_LLM_RESPONSE_BOUNDARY_APPLICATION_001"
APPLICATION_MODULE = "mip.llm.mmm_response_boundary_application"
RECOMMENDED_NEXT_ARTIFACT = "MIP_MMM_LLM_RESPONSE_BOUNDARY_APPLICATION_CHECKPOINT_001"

_RECOMMENDATION_LIKE_TOKENS = (
    "recommend",
    "recommendation",
    "reallocate",
    "reallocation",
    "budget",
    "spend movement",
    "optimal mix",
    "roi",
    "roas",
    "lift claim",
    "causal lift",
)

_GATE_TOKENS = (
    "recommendationcontract",
    "recommendation_contract",
    "decisionsurface",
    "decision_surface",
    "trustreport",
    "trust_report",
)

SAFE_RESPONSE_GUIDANCE = (
    "Use only the packaged rendered sections. "
    "Do not infer from raw model internals. "
    "Do not add recommendations not present in deterministic sections. "
    "Preserve unsupported/deferred statuses verbatim. "
    "Do not convert cannot_say into softer advice. "
    "Do not imply DecisionSurface, TrustReport, or RecommendationContract readiness. "
    "Do not make ROI/ROAS/causal/statistical claims unless explicitly authorized "
    "by deterministic artifacts. "
    "cannot_say dominates can_say."
)


class MMMResponseBoundaryApplicationStatus(StrEnum):
    """Application packaging status."""

    READY_FOR_METADATA_PACKAGING = (
        "MMM_LLM_RESPONSE_BOUNDARY_APPLICATION_READY_FOR_METADATA_PACKAGING"
    )
    BLOCKED_MISSING_RENDERED_SECTIONS = (
        "MMM_LLM_RESPONSE_BOUNDARY_APPLICATION_BLOCKED_MISSING_RENDERED_SECTIONS"
    )
    BLOCKED_INVALID_SECTION = (
        "MMM_LLM_RESPONSE_BOUNDARY_APPLICATION_BLOCKED_INVALID_SECTION"
    )
    BLOCKED_BOUNDARY_VIOLATION = (
        "MMM_LLM_RESPONSE_BOUNDARY_APPLICATION_BLOCKED_BOUNDARY_VIOLATION"
    )
    BLOCKED_UNSUPPORTED_RECOMMENDATION = (
        "MMM_LLM_RESPONSE_BOUNDARY_APPLICATION_BLOCKED_UNSUPPORTED_RECOMMENDATION"
    )


class MMMResponseBoundaryApplicationInput(ContractBaseModel):
    """Input for metadata-only MMM LLM response boundary packaging."""

    rendered_sections: Sequence[Mapping[str, Any]] = Field(default_factory=list)
    response_boundary: Mapping[str, Any] | None = None
    request_context: Mapping[str, Any] | None = None
    strict_boundary: bool = True
    lineage: Mapping[str, Any] | None = None


class MMMResponseBoundaryApplicationSection(ContractBaseModel):
    """One packaged application-facing response section."""

    section_id: str
    title: str
    rendered_text: str = ""
    section_type: str = "rendered"
    can_say: tuple[str, ...] = ()
    cannot_say: tuple[str, ...] = ()
    source_artifact_refs: tuple[str, ...] = ()
    unsupported_or_deferred_reasons: tuple[str, ...] = ()
    required_gates: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    @field_validator("section_id", "title")
    @classmethod
    def required_text_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "section_id and title cannot be empty"
            raise ValueError(msg)
        return value


class MMMResponseBoundaryApplicationOutput(ContractBaseModel):
    """JSON-safe application-facing MMM LLM response boundary payload."""

    application_status: str
    sections: tuple[MMMResponseBoundaryApplicationSection, ...] = ()
    can_say: tuple[str, ...] = ()
    cannot_say: tuple[str, ...] = ()
    unsupported_or_deferred_reasons: tuple[str, ...] = ()
    safe_response_guidance: str = SAFE_RESPONSE_GUIDANCE
    required_gates: tuple[str, ...] = ()
    blocked_capabilities: tuple[str, ...] = ()
    provenance: Mapping[str, Any] = Field(default_factory=dict)
    lineage: Mapping[str, Any] = Field(default_factory=dict)
    ready_for_llm_prompt_assembly: bool = False
    ready_for_user_facing_answer: bool = False
    ready_for_full_orchestration: bool = False


def package_mmm_llm_response_boundary(
    application_input: MMMResponseBoundaryApplicationInput,
) -> MMMResponseBoundaryApplicationOutput:
    """Package rendered MMM planning sections into a metadata-only payload.

    Always returns ready_for_llm_prompt_assembly /
    ready_for_user_facing_answer / ready_for_full_orchestration as False.
    """
    lineage = _build_lineage(application_input)
    blocked_capabilities = _default_blocked_capabilities()
    provenance = _build_provenance(application_input)

    raw_sections = list(application_input.rendered_sections or [])
    if not raw_sections:
        return _blocked(
            status=MMMResponseBoundaryApplicationStatus.BLOCKED_MISSING_RENDERED_SECTIONS,
            lineage=lineage,
            provenance=provenance,
            blocked_capabilities=blocked_capabilities,
            unsupported_or_deferred_reasons=("missing_rendered_sections",),
        )

    try:
        normalized_sections: list[MMMResponseBoundaryApplicationSection] = [
            _normalize_section(raw) for raw in raw_sections
        ]
    except (TypeError, ValueError, KeyError) as exc:
        return _blocked(
            status=MMMResponseBoundaryApplicationStatus.BLOCKED_INVALID_SECTION,
            lineage=lineage,
            provenance=provenance,
            blocked_capabilities=blocked_capabilities,
            unsupported_or_deferred_reasons=(f"invalid_section:{exc}",),
        )

    package_can_say = _collect_can_say(
        normalized_sections, application_input.response_boundary
    )
    package_cannot_say = _collect_cannot_say(
        normalized_sections, application_input.response_boundary
    )
    package_can_say = _cannot_say_dominates(package_can_say, package_cannot_say)

    sections: tuple[MMMResponseBoundaryApplicationSection, ...] = tuple(
        section.model_copy(
            update={
                "can_say": _cannot_say_dominates(section.can_say, section.cannot_say),
            }
        )
        for section in normalized_sections
    )

    if application_input.strict_boundary and not _has_boundary_metadata(
        sections=sections,
        package_can_say=package_can_say,
        package_cannot_say=package_cannot_say,
        response_boundary=application_input.response_boundary,
    ):
        return _blocked(
            status=MMMResponseBoundaryApplicationStatus.BLOCKED_BOUNDARY_VIOLATION,
            lineage=lineage,
            provenance=provenance,
            blocked_capabilities=blocked_capabilities,
            sections=sections,
            can_say=package_can_say,
            cannot_say=package_cannot_say,
            unsupported_or_deferred_reasons=("missing_can_say_cannot_say_boundary",),
        )

    required_gates = _collect_required_gates(sections, application_input.response_boundary)
    unsupported = _collect_unsupported_deferred(sections, application_input.response_boundary)

    if _has_recommendation_like_without_gates(sections, required_gates):
        return _blocked(
            status=MMMResponseBoundaryApplicationStatus.BLOCKED_UNSUPPORTED_RECOMMENDATION,
            lineage=lineage,
            provenance=provenance,
            blocked_capabilities=blocked_capabilities,
            sections=sections,
            can_say=package_can_say,
            cannot_say=package_cannot_say,
            unsupported_or_deferred_reasons=(
                *unsupported,
                "recommendation_like_content_without_required_gates",
            ),
            required_gates=required_gates,
        )

    return MMMResponseBoundaryApplicationOutput(
        application_status=(
            MMMResponseBoundaryApplicationStatus.READY_FOR_METADATA_PACKAGING.value
        ),
        sections=sections,
        can_say=package_can_say,
        cannot_say=package_cannot_say,
        unsupported_or_deferred_reasons=unsupported,
        safe_response_guidance=SAFE_RESPONSE_GUIDANCE,
        required_gates=required_gates,
        blocked_capabilities=blocked_capabilities,
        provenance=provenance,
        lineage=lineage,
        ready_for_llm_prompt_assembly=False,
        ready_for_user_facing_answer=False,
        ready_for_full_orchestration=False,
    )


def serialize_mmm_llm_response_boundary_application_output(
    output: MMMResponseBoundaryApplicationOutput,
) -> dict[str, Any]:
    """Serialize application output to a JSON-safe dict."""

    data = output.model_dump(mode="json")
    for key in (
        "can_say",
        "cannot_say",
        "unsupported_or_deferred_reasons",
        "required_gates",
        "blocked_capabilities",
    ):
        value = data.get(key)
        if isinstance(value, tuple):
            data[key] = list(value)
    sections = data.get("sections")
    if isinstance(sections, list):
        normalized_sections: list[dict[str, Any]] = []
        for section in sections:
            if not isinstance(section, dict):
                continue
            for key in (
                "can_say",
                "cannot_say",
                "source_artifact_refs",
                "unsupported_or_deferred_reasons",
                "required_gates",
                "warnings",
            ):
                value = section.get(key)
                if isinstance(value, tuple):
                    section[key] = list(value)
            normalized_sections.append(section)
        data["sections"] = normalized_sections
    return data


def _normalize_section(raw: Mapping[str, Any]) -> MMMResponseBoundaryApplicationSection:
    if not isinstance(raw, Mapping):
        msg = "rendered section must be a mapping"
        raise TypeError(msg)

    section_id = str(raw.get("section_id") or "").strip()
    title = str(raw.get("title") or section_id or "").strip()
    if not section_id or not title:
        msg = "section_id and title are required"
        raise ValueError(msg)

    rendered_text = _rendered_text_from_raw(raw)
    section_type = str(raw.get("section_type") or section_id or "rendered")

    can_say = _as_str_tuple(raw.get("can_say"))
    cannot_say = _as_str_tuple(raw.get("cannot_say"))
    if section_id == "can_say" and not can_say:
        can_say = _items_as_tuple(raw)
    if section_id == "cannot_say" and not cannot_say:
        cannot_say = _items_as_tuple(raw)

    unsupported = _as_str_tuple(
        raw.get("unsupported_or_deferred_reasons")
        or raw.get("unsupported_reasons")
        or raw.get("deferred_reasons")
    )
    if section_id in {"blocked_deferred_reasons", "unsupported"} and not unsupported:
        unsupported = _items_as_tuple(raw)

    required_gates = _as_str_tuple(raw.get("required_gates"))
    if section_id == "required_gates" and not required_gates:
        required_gates = _items_as_tuple(raw)

    source_refs = _as_str_tuple(
        raw.get("source_artifact_refs") or raw.get("evidence_references")
    )
    if section_id == "evidence_references" and not source_refs:
        source_refs = _items_as_tuple(raw)

    warnings = _as_str_tuple(raw.get("warnings") or raw.get("caveats"))
    if section_id == "caveats" and not warnings:
        warnings = _items_as_tuple(raw)

    return MMMResponseBoundaryApplicationSection(
        section_id=section_id,
        title=title,
        rendered_text=rendered_text,
        section_type=section_type,
        can_say=can_say,
        cannot_say=cannot_say,
        source_artifact_refs=source_refs,
        unsupported_or_deferred_reasons=unsupported,
        required_gates=required_gates,
        warnings=warnings,
    )


def _rendered_text_from_raw(raw: Mapping[str, Any]) -> str:
    if "rendered_text" in raw and raw["rendered_text"] is not None:
        return str(raw["rendered_text"])
    items = raw.get("items")
    if isinstance(items, (list, tuple)):
        return "\n".join(str(item) for item in items)
    return ""


def _items_as_tuple(raw: Mapping[str, Any]) -> tuple[str, ...]:
    items = raw.get("items")
    if isinstance(items, (list, tuple)):
        return tuple(str(item) for item in items if str(item).strip())
    return ()


def _as_str_tuple(value: object) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,) if value.strip() else ()
    if isinstance(value, (list, tuple)):
        return tuple(str(item) for item in value if str(item).strip())
    return (str(value),)


def _collect_can_say(
    sections: Sequence[MMMResponseBoundaryApplicationSection],
    response_boundary: Mapping[str, Any] | None,
) -> tuple[str, ...]:
    collected: list[str] = []
    for section in sections:
        collected.extend(section.can_say)
        if section.section_id == "can_say" and section.rendered_text and not section.can_say:
            collected.extend(
                line.strip() for line in section.rendered_text.splitlines() if line.strip()
            )
    if response_boundary:
        collected.extend(_as_str_tuple(response_boundary.get("can_say")))
        collected.extend(_as_str_tuple(response_boundary.get("may_rewrite_sections")))
    return tuple(dict.fromkeys(collected))


def _collect_cannot_say(
    sections: Sequence[MMMResponseBoundaryApplicationSection],
    response_boundary: Mapping[str, Any] | None,
) -> tuple[str, ...]:
    collected: list[str] = []
    for section in sections:
        collected.extend(section.cannot_say)
        if section.section_id == "cannot_say" and section.rendered_text and not section.cannot_say:
            collected.extend(
                line.strip() for line in section.rendered_text.splitlines() if line.strip()
            )
    if response_boundary:
        collected.extend(_as_str_tuple(response_boundary.get("cannot_say")))
        collected.extend(_as_str_tuple(response_boundary.get("must_preserve_sections")))
        forbidden = response_boundary.get("forbidden_additions")
        collected.extend(_as_str_tuple(forbidden))
    return tuple(dict.fromkeys(collected))


def _collect_required_gates(
    sections: Sequence[MMMResponseBoundaryApplicationSection],
    response_boundary: Mapping[str, Any] | None,
) -> tuple[str, ...]:
    collected: list[str] = []
    for section in sections:
        collected.extend(section.required_gates)
    if response_boundary:
        collected.extend(_as_str_tuple(response_boundary.get("required_gates")))
    return tuple(dict.fromkeys(collected))


def _collect_unsupported_deferred(
    sections: Sequence[MMMResponseBoundaryApplicationSection],
    response_boundary: Mapping[str, Any] | None,
) -> tuple[str, ...]:
    collected: list[str] = []
    for section in sections:
        collected.extend(section.unsupported_or_deferred_reasons)
        if section.section_id == "blocked_deferred_reasons" and section.rendered_text:
            collected.extend(
                line.strip() for line in section.rendered_text.splitlines() if line.strip()
            )
    if response_boundary:
        status = response_boundary.get("status")
        if status in {"blocked", "deferred", "BLOCKED", "DEFERRED"}:
            collected.append(f"boundary_status:{status}")
        collected.extend(_as_str_tuple(response_boundary.get("unsupported_or_deferred_reasons")))
    return tuple(dict.fromkeys(collected))


def _cannot_say_dominates(
    can_say: Sequence[str],
    cannot_say: Sequence[str],
) -> tuple[str, ...]:
    blocked = {item.strip().lower() for item in cannot_say if item.strip()}
    return tuple(
        item for item in can_say if item.strip().lower() not in blocked
    )


def _has_boundary_metadata(
    *,
    sections: Sequence[MMMResponseBoundaryApplicationSection],
    package_can_say: Sequence[str],
    package_cannot_say: Sequence[str],
    response_boundary: Mapping[str, Any] | None,
) -> bool:
    if package_can_say or package_cannot_say:
        return True
    if any(section.section_id in {"can_say", "cannot_say"} for section in sections):
        return True
    if any(section.can_say or section.cannot_say for section in sections):
        return True
    if response_boundary and (
        response_boundary.get("section_policies")
        or response_boundary.get("forbidden_additions")
        or response_boundary.get("refusal_policies")
        or response_boundary.get("can_say") is not None
        or response_boundary.get("cannot_say") is not None
    ):
        return True
    # Non-empty rendered content without can_say/cannot_say boundary fails.
    return not any(section.rendered_text.strip() for section in sections)


def _has_recommendation_like_without_gates(
    sections: Sequence[MMMResponseBoundaryApplicationSection],
    required_gates: Sequence[str],
) -> bool:
    gate_blob = " ".join(required_gates).lower().replace("-", "_").replace(" ", "")
    has_gate = any(token in gate_blob for token in _GATE_TOKENS)
    if has_gate:
        return False

    for section in sections:
        # Dedicated can_say/cannot_say/status sections are metadata, not advice.
        if section.section_id in {
            "can_say",
            "cannot_say",
            "status",
            "answer_mode",
            "required_gates",
            "blocked_deferred_reasons",
            "caveats",
            "human_review_required",
            "evidence_references",
        }:
            continue
        text = f"{section.rendered_text} {' '.join(section.can_say)}".lower()
        if any(token in text for token in _RECOMMENDATION_LIKE_TOKENS):
            return True
    return False


def _default_blocked_capabilities() -> tuple[str, ...]:
    return (
        "llm_prompt_assembly",
        "user_facing_answer_generation",
        "full_orchestration",
        "decision_surface",
        "trust_report_bypass",
        "recommendation_contract",
        "planning_recommendation",
        "budget_optimization",
        "spend_movement",
        "roi_roas",
        "claim_authorization",
    )


def _build_lineage(
    application_input: MMMResponseBoundaryApplicationInput,
) -> dict[str, Any]:
    lineage: dict[str, Any] = {
        "artifact_id": ARTIFACT_ID,
        "application_module": APPLICATION_MODULE,
        "application": "package_mmm_llm_response_boundary",
        "metadata_only_packaging": True,
        "llm_provider_called": False,
        "prompt_assembly_implemented": False,
        "user_facing_answer_generation_implemented": False,
        "full_orchestration_implemented": False,
        "ready_for_llm_prompt_assembly": False,
        "ready_for_user_facing_answer": False,
        "ready_for_full_orchestration": False,
    }
    if application_input.lineage:
        lineage["input_lineage"] = dict(application_input.lineage)
    if application_input.request_context:
        lineage["request_context"] = dict(application_input.request_context)
    if application_input.response_boundary:
        lineage["response_boundary_present"] = True
        boundary_status = application_input.response_boundary.get("status")
        if boundary_status is not None:
            lineage["response_boundary_status"] = str(boundary_status)
    return lineage


def _build_provenance(
    application_input: MMMResponseBoundaryApplicationInput,
) -> dict[str, Any]:
    provenance: dict[str, Any] = {
        "source": "deterministic_rendered_mmm_planning_sections",
        "consumes_raw_model_internals": False,
        "strict_boundary": application_input.strict_boundary,
        "section_count": len(list(application_input.rendered_sections or [])),
    }
    if application_input.lineage:
        provenance["lineage_refs"] = dict(application_input.lineage)
    return provenance


def _blocked(
    *,
    status: MMMResponseBoundaryApplicationStatus,
    lineage: Mapping[str, Any],
    provenance: Mapping[str, Any],
    blocked_capabilities: Sequence[str],
    sections: Sequence[MMMResponseBoundaryApplicationSection] = (),
    can_say: Sequence[str] = (),
    cannot_say: Sequence[str] = (),
    unsupported_or_deferred_reasons: Sequence[str] = (),
    required_gates: Sequence[str] = (),
) -> MMMResponseBoundaryApplicationOutput:
    return MMMResponseBoundaryApplicationOutput(
        application_status=status.value,
        sections=tuple(sections),
        can_say=tuple(can_say),
        cannot_say=tuple(cannot_say),
        unsupported_or_deferred_reasons=tuple(unsupported_or_deferred_reasons),
        safe_response_guidance=SAFE_RESPONSE_GUIDANCE,
        required_gates=tuple(required_gates),
        blocked_capabilities=tuple(blocked_capabilities),
        provenance=dict(provenance),
        lineage=dict(lineage),
        ready_for_llm_prompt_assembly=False,
        ready_for_user_facing_answer=False,
        ready_for_full_orchestration=False,
    )


__all__ = [
    "ARTIFACT_ID",
    "APPLICATION_MODULE",
    "RECOMMENDED_NEXT_ARTIFACT",
    "SAFE_RESPONSE_GUIDANCE",
    "MMMResponseBoundaryApplicationInput",
    "MMMResponseBoundaryApplicationOutput",
    "MMMResponseBoundaryApplicationSection",
    "MMMResponseBoundaryApplicationStatus",
    "package_mmm_llm_response_boundary",
    "serialize_mmm_llm_response_boundary_application_output",
]
