import pytest

from app.domain.enums import SimulationStatus
from app.domain.simulation import (
    can_transition,
    validate_simulation_speed,
)


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (
            SimulationStatus.INITIALIZED,
            SimulationStatus.RUNNING,
        ),
        (
            SimulationStatus.RUNNING,
            SimulationStatus.PAUSED,
        ),
        (
            SimulationStatus.RUNNING,
            SimulationStatus.COMPLETED,
        ),
        (
            SimulationStatus.PAUSED,
            SimulationStatus.RUNNING,
        ),
    ],
)
def test_allowed_simulation_transitions(
    current: SimulationStatus,
    target: SimulationStatus,
) -> None:
    assert can_transition(current, target) is True


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (
            SimulationStatus.INITIALIZED,
            SimulationStatus.PAUSED,
        ),
        (
            SimulationStatus.COMPLETED,
            SimulationStatus.RUNNING,
        ),
        (
            SimulationStatus.FAILED,
            SimulationStatus.RUNNING,
        ),
    ],
)
def test_disallowed_simulation_transitions(
    current: SimulationStatus,
    target: SimulationStatus,
) -> None:
    assert can_transition(current, target) is False


@pytest.mark.parametrize(
    "speed",
    [1, 10, 60, 300],
)
def test_supported_simulation_speeds(
    speed: int,
) -> None:
    validate_simulation_speed(speed)


@pytest.mark.parametrize(
    "speed",
    [0, 2, 5, 100, 301],
)
def test_unsupported_simulation_speeds(
    speed: int,
) -> None:
    with pytest.raises(
        ValueError,
        match="Simulation speed must be one of",
    ):
        validate_simulation_speed(speed)
