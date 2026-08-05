from typing import Any
from uuid import UUID

from app.domain.enums import MissionStatus


class MissionError(Exception):
    code = "MISSION_ERROR"

    def __init__(self, message: str, *, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class MissionNotFoundError(MissionError):
    code = "MISSION_NOT_FOUND"

    def __init__(self, mission_id: UUID) -> None:
        super().__init__(
            f"Mission '{mission_id}' was not found.",
            details={"mission_id": str(mission_id)},
        )


class InvalidMissionTransitionError(MissionError):
    code = "INVALID_MISSION_TRANSITION"

    def __init__(
        self,
        mission_id: UUID,
        current_status: MissionStatus,
        requested_status: MissionStatus,
    ) -> None:
        super().__init__(
            f"Mission cannot transition from {current_status} to {requested_status}.",
            details={
                "mission_id": str(mission_id),
                "current_status": current_status,
                "requested_status": requested_status,
            },
        )
