"""Smoke tests: package and subpackages import cleanly."""

import importlib
import pkgutil

import mip


def test_mip_version() -> None:
    assert mip.__version__ == "0.1.0"


def test_subpackages_import() -> None:
    subpackages = [
        "mip.contracts",
        "mip.evidence",
        "mip.experimentation",
        "mip.mmm",
        "mip.optimization",
        "mip.orchestration",
        "mip.trust",
        "mip.evaluation",
        "mip.llm",
        "mip.workflows",
    ]
    for name in subpackages:
        mod = importlib.import_module(name)
        assert mod.__doc__ is not None


def test_discoverable_subpackages() -> None:
    names = {m.name for m in pkgutil.iter_modules(mip.__path__, mip.__name__ + ".")}
    expected = {
        "mip.contracts",
        "mip.evidence",
        "mip.experimentation",
        "mip.mmm",
        "mip.optimization",
        "mip.orchestration",
        "mip.trust",
        "mip.evaluation",
        "mip.llm",
        "mip.workflows",
    }
    assert expected.issubset(names)


def test_workflows_intake_imports() -> None:
    import mip.workflows.intake as intake

    assert intake.__doc__ is not None


def test_workflows_readiness_imports() -> None:
    import mip.workflows.readiness as readiness

    assert readiness.__doc__ is not None


def test_workflows_configs_imports() -> None:
    import mip.workflows.configs as configs

    assert configs.__doc__ is not None


def test_workflows_orchestrator_imports() -> None:
    import mip.workflows.orchestrator as orchestrator

    assert orchestrator.__doc__ is not None


def test_cli_imports() -> None:
    import mip.cli as cli

    assert cli.__doc__ is not None


def test_adapters_imports() -> None:
    import mip.adapters as adapters
    from mip.adapters import (
        check_sibling_repo_compatibility,
        discover_sibling_export_files,
        load_sibling_exports_from_directory,
        register_sibling_exports_from_directory,
        register_sibling_fixture_export,
    )

    assert adapters.__doc__ is not None
    assert callable(register_sibling_fixture_export)
    assert callable(check_sibling_repo_compatibility)
    assert callable(discover_sibling_export_files)
    assert callable(load_sibling_exports_from_directory)
    assert callable(register_sibling_exports_from_directory)


def test_reports_imports() -> None:
    import mip.reports as reports

    assert reports.__doc__ is not None


def test_orchestration_imports() -> None:
    from mip.orchestration import (
        ApprovalRequest,
        PlannerRoute,
        WorkflowRunManifest,
        build_governed_planner_route,
        build_manifest_from_workflow_summary,
        build_plan_from_workflow_summary,
        create_approval_request,
        planner_route_from_summary,
        route_next_actions,
    )

    assert WorkflowRunManifest is not None
    assert PlannerRoute is not None
    assert ApprovalRequest is not None
    assert callable(build_plan_from_workflow_summary)
    assert callable(build_manifest_from_workflow_summary)
    assert callable(route_next_actions)
    assert callable(planner_route_from_summary)
    assert callable(build_governed_planner_route)
    assert callable(create_approval_request)
    from mip.orchestration import orchestrate_mmm_fixture_engine

    assert callable(orchestrate_mmm_fixture_engine)


def test_app_imports() -> None:
    import mip.app as app

    assert app.__doc__ is not None
