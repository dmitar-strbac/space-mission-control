from uuid import UUID

from app.domain.faults import ActiveFault, FaultType
from app.services.runtime_store import runtime_store


class FaultInjectionError(ValueError):
    pass


class FaultService:
    def inject(
        self,
        *,
        mission_id: UUID,
        fault_type: FaultType,
        magnitude: float,
    ) -> ActiveFault:
        runtime = runtime_store.get(mission_id)

        if runtime is None:
            raise FaultInjectionError(
                f"Simulation runtime for mission {mission_id} is not available."
            )

        self._validate_magnitude(
            fault_type=fault_type,
            magnitude=magnitude,
        )

        fault = ActiveFault(
            fault_type=fault_type,
            magnitude=magnitude,
        )

        runtime.active_faults[fault_type] = fault

        return fault

    def clear(
        self,
        *,
        mission_id: UUID,
        fault_type: FaultType,
    ) -> None:
        runtime = runtime_store.get(mission_id)

        if runtime is None:
            raise FaultInjectionError(
                f"Simulation runtime for mission {mission_id} is not available."
            )

        runtime.active_faults.pop(
            fault_type,
            None,
        )

    @staticmethod
    def _validate_magnitude(
        *,
        fault_type: FaultType,
        magnitude: float,
    ) -> None:
        if magnitude < 0.0:
            raise FaultInjectionError("Fault magnitude cannot be negative.")

        if fault_type is FaultType.ENGINE_FAILURE and magnitude > 1.0:
            raise FaultInjectionError("Engine failure magnitude must be between 0.0 and 1.0.")

        if fault_type is FaultType.TARGETING_ERROR and magnitude > 180.0:
            raise FaultInjectionError("Targeting error cannot exceed 180 degrees.")
