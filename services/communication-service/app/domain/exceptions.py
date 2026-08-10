from typing import Any
from uuid import UUID


class CommunicationError(Exception):
    code = "COMMUNICATION_ERROR"

    def __init__(
        self,
        message: str,
        *,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class InvalidCommunicationProfileError(CommunicationError):
    code = "INVALID_COMMUNICATION_PROFILE"


class CommunicationProfileNotFoundError(CommunicationError):
    code = "COMMUNICATION_PROFILE_NOT_FOUND"

    def __init__(self, mission_id: UUID) -> None:
        super().__init__(
            f"Communication profile for mission '{mission_id}' was not found.",
            details={"mission_id": str(mission_id)},
        )


class CommunicationProfileAlreadyExistsError(CommunicationError):
    code = "COMMUNICATION_PROFILE_ALREADY_EXISTS"

    def __init__(self, mission_id: UUID) -> None:
        super().__init__(
            f"Communication profile for mission '{mission_id}' already exists.",
            details={"mission_id": str(mission_id)},
        )


class CommandNotFoundError(CommunicationError):
    code = "COMMAND_NOT_FOUND"

    def __init__(self, command_id: UUID) -> None:
        super().__init__(
            f"Command '{command_id}' was not found.",
            details={"command_id": str(command_id)},
        )


class InvalidCommandTransitionError(CommunicationError):
    code = "INVALID_COMMAND_TRANSITION"


class CommandDeliveryError(CommunicationError):
    code = "COMMAND_DELIVERY_ERROR"
