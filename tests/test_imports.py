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
