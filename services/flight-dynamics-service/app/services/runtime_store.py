from uuid import UUID

from app.domain.runtime import SimulationRuntime


class SimulationRuntimeStore:
    def __init__(self) -> None:
        self._runtimes: dict[UUID, SimulationRuntime] = {}

    def set(
        self,
        mission_id: UUID,
        runtime: SimulationRuntime,
    ) -> None:
        self._runtimes[mission_id] = runtime

    def get(
        self,
        mission_id: UUID,
    ) -> SimulationRuntime | None:
        return self._runtimes.get(mission_id)

    def remove(
        self,
        mission_id: UUID,
    ) -> None:
        self._runtimes.pop(mission_id, None)

    def clear(self) -> None:
        self._runtimes.clear()


runtime_store = SimulationRuntimeStore()
