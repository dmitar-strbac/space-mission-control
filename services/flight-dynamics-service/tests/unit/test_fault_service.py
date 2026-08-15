from uuid import uuid4

import pytest

from app.domain.faults import FaultType
from app.domain.runtime import SimulationRuntime
from app.services.fault_service import (
    FaultInjectionError,
    FaultService,
)
from app.services.runtime_store import runtime_store
from orbital_mechanics.models import (
    StateVector,
    Vector2D,
)


def _runtime() -> SimulationRuntime:
    return SimulationRuntime(
        state=StateVector(
            position=Vector2D(
                x=6_771_000.0,
                y=0.0,
            ),
            velocity=Vector2D(
                x=0.0,
                y=7_670.0,
            ),
            total_mass_kg=10_000.0,
            propellant_mass_kg=2_000.0,
        ),
        oxygen_kg=100.0,
        battery_kwh=100.0,
    )


def test_inject_fault_adds_fault_to_runtime() -> None:
    mission_id = uuid4()
    runtime_store.set(mission_id, _runtime())

    service = FaultService()

    fault = service.inject(
        mission_id=mission_id,
        fault_type=FaultType.PROPELLANT_LEAK,
        magnitude=0.5,
    )

    assert fault.fault_type is FaultType.PROPELLANT_LEAK

    assert runtime_store.get(mission_id) is not None

    runtime_store.clear()


def test_clear_fault_removes_active_fault() -> None:
    mission_id = uuid4()
    runtime_store.set(mission_id, _runtime())

    service = FaultService()

    service.inject(
        mission_id=mission_id,
        fault_type=FaultType.OXYGEN_LEAK,
        magnitude=0.01,
    )

    service.clear(
        mission_id=mission_id,
        fault_type=FaultType.OXYGEN_LEAK,
    )

    runtime = runtime_store.get(mission_id)

    assert runtime is not None
    assert FaultType.OXYGEN_LEAK not in runtime.active_faults

    runtime_store.clear()


def test_engine_failure_fraction_above_one_is_rejected() -> None:
    mission_id = uuid4()
    runtime_store.set(mission_id, _runtime())

    service = FaultService()

    with pytest.raises(FaultInjectionError):
        service.inject(
            mission_id=mission_id,
            fault_type=FaultType.ENGINE_FAILURE,
            magnitude=1.1,
        )

    runtime_store.clear()


def test_fault_requires_active_runtime() -> None:
    service = FaultService()

    with pytest.raises(FaultInjectionError):
        service.inject(
            mission_id=uuid4(),
            fault_type=FaultType.ENGINE_FAILURE,
            magnitude=1.0,
        )
