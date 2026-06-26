"""Deterministic helpers for Stage A synthetic fixture discovery and loading."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[3]
_STAGE_A_ROOT = _REPO_ROOT / "examples" / "fixtures" / "stage_a"
_MANIFEST_PATH = _STAGE_A_ROOT / "manifest.json"


class StageAFixtureError(Exception):
    """Raised when Stage A fixture discovery or loading fails."""


def _read_manifest_document() -> dict[str, Any]:
    if not _MANIFEST_PATH.is_file():
        msg = f"Stage A manifest not found: {_MANIFEST_PATH}"
        raise StageAFixtureError(msg)
    try:
        document = json.loads(_MANIFEST_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        msg = f"Stage A manifest is not valid JSON: {_MANIFEST_PATH}"
        raise StageAFixtureError(msg) from exc
    if not isinstance(document, dict):
        msg = f"Stage A manifest must be a JSON object: {_MANIFEST_PATH}"
        raise StageAFixtureError(msg)
    return document


def _manifest_entries() -> list[dict[str, Any]]:
    document = _read_manifest_document()
    fixtures = document.get("fixtures")
    if not isinstance(fixtures, list):
        msg = "Stage A manifest is missing a fixtures list"
        raise StageAFixtureError(msg)
    return [entry for entry in fixtures if isinstance(entry, dict)]


def _entry_for_fixture_id(fixture_id: str) -> dict[str, Any]:
    if not fixture_id.strip():
        msg = "fixture_id cannot be empty"
        raise StageAFixtureError(msg)
    for entry in _manifest_entries():
        if entry.get("fixture_id") == fixture_id:
            return entry
    msg = f"Stage A fixture id not found in manifest: {fixture_id}"
    raise StageAFixtureError(msg)


def _validate_manifest_entry(entry: dict[str, Any]) -> None:
    if entry.get("requires_mmm_or_geox_engine") is True:
        fixture_id = entry.get("fixture_id", "<unknown>")
        msg = (
            f"Stage A fixture {fixture_id!r} requires MMM/GeoX engine execution "
            "and cannot be loaded through Stage A helpers"
        )
        raise StageAFixtureError(msg)


def _resolve_fixture_path(relative_path: str) -> Path:
    if not relative_path.strip():
        msg = "fixture path cannot be empty"
        raise StageAFixtureError(msg)
    resolved = (_REPO_ROOT / relative_path).resolve()
    stage_a_resolved = _STAGE_A_ROOT.resolve()
    if stage_a_resolved not in resolved.parents:
        msg = f"fixture path escapes Stage A root: {relative_path}"
        raise StageAFixtureError(msg)
    return resolved


def _read_fixture_file(path: Path) -> dict[str, Any]:
    if not path.is_file():
        msg = f"Stage A fixture file not found: {path}"
        raise StageAFixtureError(msg)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        msg = f"Stage A fixture is not valid JSON: {path}"
        raise StageAFixtureError(msg) from exc
    if not isinstance(payload, dict):
        msg = f"Stage A fixture must be a JSON object: {path}"
        raise StageAFixtureError(msg)
    if payload.get("synthetic") is not True:
        msg = f"Stage A fixture must set synthetic=true: {path}"
        raise StageAFixtureError(msg)
    return payload


def load_stage_a_manifest() -> list[dict[str, Any]]:
    """Return manifest entries for all Stage A fixtures."""
    entries = _manifest_entries()
    for entry in entries:
        _validate_manifest_entry(entry)
    return [dict(entry) for entry in entries]


def list_stage_a_fixtures(
    workflow_area: str | None = None,
) -> list[dict[str, Any]]:
    """List Stage A manifest entries, optionally filtered by workflow area."""
    entries = load_stage_a_manifest()
    if workflow_area is None:
        return entries
    return [entry for entry in entries if entry.get("workflow_area") == workflow_area]


def stage_a_fixture_path(fixture_id: str) -> Path:
    """Resolve the on-disk path for a Stage A fixture id."""
    entry = _entry_for_fixture_id(fixture_id)
    _validate_manifest_entry(entry)
    relative_path = entry.get("path")
    if not isinstance(relative_path, str):
        msg = f"Stage A fixture {fixture_id!r} is missing a path"
        raise StageAFixtureError(msg)
    return _resolve_fixture_path(relative_path)


def load_stage_a_fixture(fixture_id: str) -> dict[str, Any]:
    """Load a Stage A fixture payload by manifest fixture id."""
    entry = _entry_for_fixture_id(fixture_id)
    _validate_manifest_entry(entry)
    path = stage_a_fixture_path(fixture_id)
    payload = _read_fixture_file(path)
    if payload.get("fixture_id") != fixture_id:
        msg = (
            f"Stage A fixture {fixture_id!r} file fixture_id "
            f"does not match manifest entry"
        )
        raise StageAFixtureError(msg)
    return payload


def load_stage_a_fixtures_by_workflow_area(workflow_area: str) -> list[dict[str, Any]]:
    """Load all Stage A fixture payloads for a workflow area."""
    if not workflow_area.strip():
        msg = "workflow_area cannot be empty"
        raise StageAFixtureError(msg)
    return [
        load_stage_a_fixture(str(entry["fixture_id"]))
        for entry in list_stage_a_fixtures(workflow_area=workflow_area)
    ]
