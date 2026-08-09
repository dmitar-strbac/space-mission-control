from app.domain.enums import SimulationStatus

_ALLOWED_TRANSITIONS: dict[
    SimulationStatus,
    frozenset[SimulationStatus],
] = {
    SimulationStatus.INITIALIZED: frozenset(
        {
            SimulationStatus.RUNNING,
            SimulationStatus.FAILED,
        }
    ),
    SimulationStatus.RUNNING: frozenset(
        {
            SimulationStatus.PAUSED,
            SimulationStatus.COMPLETED,
            SimulationStatus.FAILED,
        }
    ),
    SimulationStatus.PAUSED: frozenset(
        {
            SimulationStatus.RUNNING,
            SimulationStatus.FAILED,
        }
    ),
    SimulationStatus.COMPLETED: frozenset(),
    SimulationStatus.FAILED: frozenset(),
}


SUPPORTED_SIMULATION_SPEEDS = frozenset({1, 10, 60, 300})


def can_transition(
    current: SimulationStatus,
    target: SimulationStatus,
) -> bool:
    return target in _ALLOWED_TRANSITIONS[current]


def validate_simulation_speed(speed: int) -> None:
    if speed not in SUPPORTED_SIMULATION_SPEEDS:
        supported = ", ".join(str(value) for value in sorted(SUPPORTED_SIMULATION_SPEEDS))
        raise ValueError(f"Simulation speed must be one of: {supported}.")
