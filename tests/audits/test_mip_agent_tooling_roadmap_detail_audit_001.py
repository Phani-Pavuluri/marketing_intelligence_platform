"""Lightweight checks for agent tooling roadmap detail audit documentation."""

from __future__ import annotations

import json
from pathlib import Path

_AUDIT = Path("docs/audits/MIP_AGENT_TOOLING_AND_ROADMAP_IMPLEMENTATION_DETAIL_AUDIT_001.md")
_SUMMARY = Path(
    "docs/audits/archives/mip_agent_tooling_roadmap_detail_audit_001_summary.json"
)

_REQUIRED_SECTIONS = (
    "## 2. Executive summary",
    "## 4. Agent/tooling gap matrix",
    "## 5. Roadmap implementation-detail gap matrix",
    "## 6. Report-generation readiness",
    "## 8. Cursor-agent executability checklist",
    "## 10. Stop/go criteria",
)

_REQUIRED_SUMMARY_KEYS = (
    "audit_id",
    "overall_verdict",
    "highest_priority_gaps",
    "recommended_next_step",
)


def test_agent_tooling_audit_doc_exists() -> None:
    assert _AUDIT.is_file()


def test_agent_tooling_audit_contains_required_sections() -> None:
    content = _AUDIT.read_text(encoding="utf-8")
    for section in _REQUIRED_SECTIONS:
        assert section in content, f"missing section: {section}"


def test_agent_tooling_audit_summary_json_exists_and_valid() -> None:
    assert _SUMMARY.is_file()
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    for key in _REQUIRED_SUMMARY_KEYS:
        assert key in summary, key
    assert summary["status"] == "audit_complete"
