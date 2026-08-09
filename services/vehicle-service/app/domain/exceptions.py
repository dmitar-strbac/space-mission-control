from uuid import UUID

from app.domain.enums import SpacecraftStatus


class VehicleServiceError(Exception):
    """Base exception for Vehicle Service errors."""


class SpacecraftNotFoundError(VehicleServiceError):
    def __init__(self, spacecraft_id: UUID) -> None:
        self.spacecraft_id = spacecraft_id
        super().__init__(f"Spacecraft '{spacecraft_id}' was not found.")


class SpacecraftNameConflictError(VehicleServiceError):
    def __init__(self, name: str) -> None:
        self.name = name
        super().__init__(f"Spacecraft with name '{name}' already exists.")


class SpacecraftDeletionConflictError(VehicleServiceError):
    def __init__(
        self,
        spacecraft_id: UUID,
        status: SpacecraftStatus,
    ) -> None:
        self.spacecraft_id = spacecraft_id
        self.status = status
        super().__init__(
            f"Spacecraft '{spacecraft_id}' cannot be deleted while its status is '{status.value}'."
        )


class SpacecraftModificationConflictError(VehicleServiceError):
    def __init__(
        self,
        spacecraft_id: UUID,
        status: SpacecraftStatus,
    ) -> None:
        self.spacecraft_id = spacecraft_id
        self.status = status
        super().__init__(
            f"Spacecraft '{spacecraft_id}' cannot be modified while its status is '{status.value}'."
        )


class InvalidManualStatusError(VehicleServiceError):
    def __init__(self, status: SpacecraftStatus) -> None:
        self.status = status
        super().__init__(
            f"Spacecraft status '{status.value}' cannot be assigned through the configuration API."
        )
