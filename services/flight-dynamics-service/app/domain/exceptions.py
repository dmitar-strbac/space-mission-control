from typing import Any
from uuid import UUID


class SimulationError(Exception):
    code = "SIMULATION_ERROR"

    def __init__(
        self,
        message: str,
        *,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class SimulationNotFoundError(SimulationError):
    code = "SIMULATION_NOT_FOUND"

    def __init__(self, mission_id: UUID) -> None:
        super().__init__(
            f"Simulation for mission '{mission_id}' was not found.",
            details={"mission_id": str(mission_id)},
        )


class SimulationConflictError(SimulationError):
    code = "SIMULATION_CONFLICT"


class InvalidSimulationTransitionError(SimulationError):
    code = "INVALID_SIMULATION_TRANSITION"

    def __init__(
        self,
        mission_id: UUID,
        current_status: str,
        target_status: str,
    ) -> None:
        super().__init__(
            (
                f"Simulation for mission '{mission_id}' cannot transition "
                f"from '{current_status}' to '{target_status}'."
            ),
            details={
                "mission_id": str(mission_id),
                "current_status": current_status,
                "target_status": target_status,
            },
        )


class SimulationAlreadyExistsError(SimulationError):
    code = "SIMULATION_ALREADY_EXISTS"

    def __init__(self, mission_id: UUID) -> None:
        super().__init__(
            f"Simulation for mission '{mission_id}' already exists.",
            details={"mission_id": str(mission_id)},
        )


class SimulationExecutionError(SimulationError):
    code = "SIMULATION_EXECUTION_FAILED"


class SimulationStateUnavailableError(SimulationError):
    code = "SIMULATION_STATE_UNAVAILABLE"
