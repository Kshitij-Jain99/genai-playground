"""Deterministic demonstration scenarios and simulated timings."""

from dataclasses import dataclass
from enum import StrEnum
from time import sleep

from app.core.config import get_settings

settings = get_settings()


class Scenario(StrEnum):
    """Supported deterministic application scenarios."""

    NORMAL = "normal"
    SLOW = "slow"
    FAILURE = "failure"
    HIGH_TOKEN = "high-token"
    TOOL_FAILURE = "tool-failure"
    RETRIEVAL_EMPTY = "retrieval-empty"


@dataclass(frozen=True)
class ScenarioTimings:
    """Artificial operation delays in seconds."""

    prompt_seconds: float
    retrieval_seconds: float
    tool_seconds: float
    llm_seconds: float
    validation_seconds: float


NORMAL_TIMINGS = ScenarioTimings(
    prompt_seconds=0.010,
    retrieval_seconds=0.100,
    tool_seconds=0.150,
    llm_seconds=0.500,
    validation_seconds=0.020,
)

SLOW_TIMINGS = ScenarioTimings(
    prompt_seconds=0.050,
    retrieval_seconds=1.500,
    tool_seconds=2.000,
    llm_seconds=6.000,
    validation_seconds=0.200,
)


def get_scenario_timings(
    scenario: Scenario,
) -> ScenarioTimings:
    """Return deterministic delays for a scenario."""

    if scenario == Scenario.SLOW:
        return SLOW_TIMINGS

    return NORMAL_TIMINGS


def simulate_delay(seconds: float) -> None:
    """Apply an artificial delay when scenario delays are enabled."""

    if seconds < 0:
        raise ValueError("Delay must not be negative.")

    if settings.simulate_operation_delays:
        sleep(seconds)