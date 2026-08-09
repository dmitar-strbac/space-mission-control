from typing import Any
from uuid import UUID


class TrajectoryError(Exception):
    code = "TRAJECTORY_ERROR"

    def __init__(
        self,
        message: str,
        *,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class TrajectoryPlanNotFoundError(TrajectoryError):
    code = "TRAJECTORY_PLAN_NOT_FOUND"

    def __init__(self, mission_id: UUID) -> None:
        super().__init__(
            f"Trajectory plan for mission '{mission_id}' was not found.",
            details={"mission_id": str(mission_id)},
        )


class InvalidTrajectoryRequestError(TrajectoryError):
    code = "INVALID_TRAJECTORY_REQUEST"


class TrajectoryNotFeasibleError(TrajectoryError):
    code = "TRAJECTORY_NOT_FEASIBLE"
