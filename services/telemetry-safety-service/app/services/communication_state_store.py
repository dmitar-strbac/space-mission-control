from uuid import UUID

from app.schemas.communication import (
    CommunicationStatusEventPayload,
)


class CommunicationStateStore:
    def __init__(self) -> None:
        self._states: dict[
            UUID,
            CommunicationStatusEventPayload,
        ] = {}

    def set(
        self,
        state: CommunicationStatusEventPayload,
    ) -> None:
        self._states[state.mission_id] = state

    def get(
        self,
        mission_id: UUID,
    ) -> CommunicationStatusEventPayload | None:
        return self._states.get(mission_id)

    def remove(
        self,
        mission_id: UUID,
    ) -> None:
        self._states.pop(
            mission_id,
            None,
        )

    def clear(self) -> None:
        self._states.clear()


communication_state_store = CommunicationStateStore()
