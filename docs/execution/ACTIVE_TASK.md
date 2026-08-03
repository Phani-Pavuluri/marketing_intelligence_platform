# Active Task

**Status:** ready_for_review
**Owner:** MIP program governance

## Identity

- **Task ID:** `MIP_INVOCATION_ONLY_CODEX_PROMPT_STANDARD_001`
- **Feature branch:** `docs/mip-invocation-only-codex-prompt-standard-001`
- **Authorization head:** `39abc3d66a80054b2b293a73f2dbeb690eb2304b`
- **Implementation:** `9376284a35f6dda7d1b9a535e5cf23c565f759ad`
- **Risk tier:** Tier 1 documentation/governance plus focused test

## Completed outcome

Codex prompts are invocation-only. The canonical execution or correction
invocation is `Synchronize from Git and execute the active task.` A merge
invocation carries only the exact externally approved remote head SHA. Main
provides authorization provenance; a verified declared feature branch provides
the latest resumed lifecycle state. Safe fail-closed outcomes are Git-durable.

## Validation and authority

The frozen review tree passed JSON parsing, current-state consistency, boundary
and six-path scope checks, `git diff --check`, and the focused governance test.
Docker, Ruff, mypy, and the full suite are not required for this Tier 1 task.
MMM and GeoX are unchanged; adoption remains separately unauthorized. Merge,
PR creation, and capability authority remain false. Review this exact head only.
