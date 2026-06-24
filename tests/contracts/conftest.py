"""Shared fixtures for contract tests."""

from datetime import UTC, datetime

import pytest

from mip.contracts import CausalQuantity, DiagnosticSummary, Estimand, TimeWindow


@pytest.fixture
def time_window() -> TimeWindow:
    return TimeWindow(
        start=datetime(2025, 1, 1, tzinfo=UTC),
        end=datetime(2025, 6, 1, tzinfo=UTC),
    )


@pytest.fixture
def delta_mu_estimand(time_window: TimeWindow) -> Estimand:
    return Estimand(
        target_metric="revenue",
        causal_quantity=CausalQuantity.DELTA_MU,
        unit="USD",
        time_window=time_window,
        treatment_definition="+10% spend all channels",
        aggregation_level="full_panel",
    )


@pytest.fixture
def passing_diagnostics() -> DiagnosticSummary:
    return DiagnosticSummary(passed=True)


@pytest.fixture
def failed_diagnostics() -> DiagnosticSummary:
    return DiagnosticSummary(passed=False, failures=["power below threshold"])
