"""Deterministic loaders for agent capability eval fixtures."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import Field, field_validator

from mip.contracts.agent_answerability import (
    AgentCapabilityEvalCase,
)
from mip.contracts.base import ContractBaseModel

_REPO_ROOT = Path(__file__).resolve().parents[3]
_EVAL_ROOT = _REPO_ROOT / "examples" / "fixtures" / "agent_capability_eval"
_MANIFEST_PATH = _EVAL_ROOT / "manifest.json"
_CASES_DIR = _EVAL_ROOT / "cases"


class AgentCapabilityEvalFixtureError(Exception):
    """Raised when agent capability eval fixture loading fails."""


class AgentCapabilityEvalFixtureRecord(ContractBaseModel):
    """File-backed eval fixture with manifest metadata and validated eval case."""

    case_id: str
    description: str
    user_question: str
    tags: list[str] = Field(default_factory=list)
    forbidden_answerable_states: list[str] = Field(default_factory=list)
    allowed_expected_states: list[str] = Field(default_factory=list)
    requires_fallback_message: bool = False
    requires_report: bool = False
    requires_tool: bool = False
    requires_missing_inputs: bool = False
    eval_case: AgentCapabilityEvalCase

    @field_validator("case_id", "description", "user_question")
    @classmethod
    def fixture_text_fields_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "fixture text fields cannot be empty"
            raise ValueError(msg)
        return value


def _read_json_object(path: Path, *, label: str) -> dict[str, Any]:
    if not path.is_file():
        msg = f"{label} not found: {path}"
        raise AgentCapabilityEvalFixtureError(msg)
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        msg = f"{label} is not valid JSON: {path}"
        raise AgentCapabilityEvalFixtureError(msg) from exc
    if not isinstance(document, dict):
        msg = f"{label} must be a JSON object: {path}"
        raise AgentCapabilityEvalFixtureError(msg)
    return document


def _resolve_case_path(relative_path: str) -> Path:
    if not relative_path.strip():
        msg = "case_file path cannot be empty"
        raise AgentCapabilityEvalFixtureError(msg)
    resolved = (_EVAL_ROOT / relative_path).resolve()
    cases_resolved = _CASES_DIR.resolve()
    if cases_resolved not in resolved.parents and resolved != cases_resolved:
        msg = f"case_file escapes eval cases directory: {relative_path}"
        raise AgentCapabilityEvalFixtureError(msg)
    return resolved


def _parse_eval_case(document: dict[str, Any]) -> AgentCapabilityEvalCase:
    request_payload = document.get("request")
    if not isinstance(request_payload, dict):
        msg = "eval case is missing request object"
        raise AgentCapabilityEvalFixtureError(msg)
    return AgentCapabilityEvalCase.model_validate(
        {
            "case_id": document["case_id"],
            "user_question": document["user_question"],
            "request": request_payload,
            "expected_state": document["expected_state"],
            "expected_answer_mode": document.get("expected_answer_mode"),
            "expected_evidence_level": document.get("expected_evidence_level"),
            "expected_blocked_claims": document.get("expected_blocked_claims", []),
            "forbidden_phrases": document.get("forbidden_phrases", []),
            "expected_safe_fallback": document.get("expected_safe_fallback"),
        }
    )


def _parse_fixture_record(document: dict[str, Any]) -> AgentCapabilityEvalFixtureRecord:
    eval_case = _parse_eval_case(document)
    if eval_case.case_id != document.get("case_id"):
        msg = "case_id mismatch between root and eval case payload"
        raise AgentCapabilityEvalFixtureError(msg)
    return AgentCapabilityEvalFixtureRecord(
        case_id=eval_case.case_id,
        description=str(document["description"]),
        user_question=eval_case.user_question,
        tags=list(document.get("tags", [])),
        forbidden_answerable_states=list(document.get("forbidden_answerable_states", [])),
        allowed_expected_states=list(document.get("allowed_expected_states", [])),
        requires_fallback_message=bool(document.get("requires_fallback_message", False)),
        requires_report=bool(document.get("requires_report", False)),
        requires_tool=bool(document.get("requires_tool", False)),
        requires_missing_inputs=bool(document.get("requires_missing_inputs", False)),
        eval_case=eval_case,
    )


def _manifest_case_entries() -> list[dict[str, Any]]:
    document = _read_json_object(_MANIFEST_PATH, label="agent capability eval manifest")
    cases = document.get("cases")
    if not isinstance(cases, list):
        msg = "agent capability eval manifest is missing a cases list"
        raise AgentCapabilityEvalFixtureError(msg)
    entries = [entry for entry in cases if isinstance(entry, dict)]
    case_ids = [str(entry.get("case_id", "")) for entry in entries]
    if len(case_ids) != len(set(case_ids)):
        msg = "duplicate case_id values in agent capability eval manifest"
        raise AgentCapabilityEvalFixtureError(msg)
    if any(not case_id.strip() for case_id in case_ids):
        msg = "manifest case_id cannot be empty"
        raise AgentCapabilityEvalFixtureError(msg)
    return entries


def load_agent_capability_eval_manifest() -> dict[str, Any]:
    """Load the agent capability eval manifest document."""
    return _read_json_object(_MANIFEST_PATH, label="agent capability eval manifest")


def list_agent_capability_eval_cases() -> list[AgentCapabilityEvalCase]:
    """Load and validate every eval case declared in the manifest."""
    return [
        load_agent_capability_eval_fixture(case_id).eval_case
        for case_id in _manifest_case_ids()
    ]


def list_agent_capability_eval_fixtures() -> list[AgentCapabilityEvalFixtureRecord]:
    """Load every eval fixture record declared in the manifest."""
    return [load_agent_capability_eval_fixture(case_id) for case_id in _manifest_case_ids()]


def load_agent_capability_eval_case(case_id: str) -> AgentCapabilityEvalCase:
    """Load a single validated eval case by ID."""
    return load_agent_capability_eval_fixture(case_id).eval_case


def load_agent_capability_eval_fixture(case_id: str) -> AgentCapabilityEvalFixtureRecord:
    """Load a single eval fixture record by ID."""
    if not case_id.strip():
        msg = "case_id cannot be empty"
        raise AgentCapabilityEvalFixtureError(msg)
    for entry in _manifest_case_entries():
        if entry.get("case_id") == case_id:
            case_file = entry.get("case_file")
            if not isinstance(case_file, str):
                msg = f"manifest entry for {case_id!r} is missing case_file"
                raise AgentCapabilityEvalFixtureError(msg)
            path = _resolve_case_path(case_file)
            record = _parse_fixture_record(_read_json_object(path, label=f"eval case {case_id}"))
            if record.case_id != case_id:
                msg = f"case file {path} case_id does not match manifest entry {case_id!r}"
                raise AgentCapabilityEvalFixtureError(msg)
            return record
    msg = f"agent capability eval case_id not found in manifest: {case_id}"
    raise AgentCapabilityEvalFixtureError(msg)


def _manifest_case_ids() -> list[str]:
    return [str(entry["case_id"]) for entry in _manifest_case_entries()]


__all__ = [
    "AgentCapabilityEvalFixtureError",
    "AgentCapabilityEvalFixtureRecord",
    "list_agent_capability_eval_cases",
    "list_agent_capability_eval_fixtures",
    "load_agent_capability_eval_case",
    "load_agent_capability_eval_fixture",
    "load_agent_capability_eval_manifest",
]
