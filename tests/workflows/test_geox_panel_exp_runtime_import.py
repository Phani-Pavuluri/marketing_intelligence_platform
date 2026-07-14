"""Tests for the optional panel_exp import boundary."""

from __future__ import annotations

from types import ModuleType

import pytest

from mip.workflows import geox_panel_exp_runtime_call as runtime_call


def test_optional_runtime_import_loads_documented_callables(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = ModuleType("panel_exp.validation.post_test_spend_readiness_adapter_runtime_001")

    class PostTestSpendInput:
        def __init__(self, **kwargs: object) -> None:
            self.kwargs = kwargs

    def build_post_test_spend_evidence(spend_input: object) -> object:
        return spend_input

    def build_trusted_readout_spend_handoff(evidence: object) -> dict[str, object]:
        return {"evidence": evidence}

    setattr(module, "PostTestSpendInput", PostTestSpendInput)
    setattr(module, "build_post_test_spend_evidence", build_post_test_spend_evidence)
    setattr(module, "build_trusted_readout_spend_handoff", build_trusted_readout_spend_handoff)
    monkeypatch.setattr(runtime_call, "import_module", lambda _: module)

    runtime = runtime_call._import_panel_exp_runtime()

    spend_input = runtime["PostTestSpendInput"](experiment_id="exp-1")
    evidence = runtime["build_post_test_spend_evidence"](spend_input)
    assert evidence is spend_input
    assert runtime["build_trusted_readout_spend_handoff"](evidence) == {"evidence": evidence}


def test_optional_runtime_import_preserves_missing_package_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def missing_module(_: str) -> ModuleType:
        raise ModuleNotFoundError("No module named 'panel_exp'")

    monkeypatch.setattr(runtime_call, "import_module", missing_module)

    with pytest.raises(ModuleNotFoundError, match="No module named 'panel_exp'"):
        runtime_call._import_panel_exp_runtime()
