"""Tests for the simulated LLM service."""

import pytest

from app.services.llm import (
    estimate_request_cost,
    estimate_token_count,
)


def test_estimate_token_count_counts_words() -> None:
    token_count = estimate_token_count(
        "OpenTelemetry traces are useful"
    )

    assert token_count == 4


def test_estimate_token_count_returns_at_least_one() -> None:
    token_count = estimate_token_count("")

    assert token_count == 1


def test_estimate_request_cost() -> None:
    estimated_cost = estimate_request_cost(
        input_tokens=1_000,
        output_tokens=1_000,
    )

    assert estimated_cost == pytest.approx(0.003)


def test_estimate_request_cost_for_partial_thousand() -> None:
    estimated_cost = estimate_request_cost(
        input_tokens=500,
        output_tokens=250,
    )

    assert estimated_cost == pytest.approx(0.001)

# Calculation:
# 500 input tokens:
# 500 / 1000 × 0.001 = 0.0005

# 250 output tokens:
# 250 / 1000 × 0.002 = 0.0005

# Total:
# 0.001 USD    