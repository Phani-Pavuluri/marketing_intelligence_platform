"""Tests for estimand contracts."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from mip.contracts import CausalQuantity, Estimand, TimeWindow


def test_valid_time_window() -> None:
    tw = TimeWindow(
        start=datetime(2025, 1, 1, tzinfo=UTC),
        end=datetime(2025, 2, 1, tzinfo=UTC),
    )
    assert tw.end > tw.start


def test_invalid_time_window_end_before_start() -> None:
    with pytest.raises(ValidationError, match="end must be after start"):
        TimeWindow(
            start=datetime(2025, 6, 1, tzinfo=UTC),
            end=datetime(2025, 1, 1, tzinfo=UTC),
        )


def test_valid_estimand(delta_mu_estimand: Estimand) -> None:
    assert delta_mu_estimand.causal_quantity == CausalQuantity.DELTA_MU
    assert delta_mu_estimand.allowed_claims == []


def test_estimand_empty_target_metric_rejected(time_window: TimeWindow) -> None:
    with pytest.raises(ValidationError):
        Estimand(
            target_metric="  ",
            causal_quantity=CausalQuantity.LIFT,
            unit="USD",
            time_window=time_window,
            treatment_definition="holdout",
            aggregation_level="geo",
        )


def test_estimand_empty_treatment_definition_rejected(time_window: TimeWindow) -> None:
    with pytest.raises(ValidationError):
        Estimand(
            target_metric="conversions",
            causal_quantity=CausalQuantity.LIFT,
            unit="count",
            time_window=time_window,
            treatment_definition="",
            aggregation_level="geo",
        )
