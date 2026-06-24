"""Tests for public mip.workflows.orchestrator exports."""


def test_public_imports() -> None:
    from mip.workflows.orchestrator import (
        WorkflowRunStatus,
        WorkflowRunSummary,
        run_local_workflow,
    )

    assert WorkflowRunStatus.COMPLETED.value == "completed"
    assert callable(run_local_workflow)
    assert WorkflowRunSummary is not None
