from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums import (
    CheckpointReason,
    ManeuverExecutionStatus,
    SimulationStatus,
)
from app.domain.exceptions import (
    InvalidSimulationTransitionError,
    SimulationAlreadyExistsError,
    SimulationExecutionError,
)
from app.domain.faults import ActiveFault, FaultType
from app.schemas.simulation import SimulationInitializeRequest
from app.services.runtime_store import runtime_store
from app.services.simulation_service import SimulationService


def _request(
    *,
    simulation_speed: int = 1,
    checkpoint_interval_s: float = 60.0,
) -> SimulationInitializeRequest:
    return SimulationInitializeRequest(
        mission_id=uuid4(),
        trajectory_plan_id=uuid4(),
        vehicle_id=uuid4(),
        initial_state_vector={
            "position": {
                "x": 6_771_000.0,
                "y": 0.0,
            },
            "velocity": {
                "x": 0.0,
                "y": 7_672.0,
            },
            "total_mass_kg": 10_000.0,
            "propellant_mass_kg": 2_000.0,
            "elapsed_time_s": 0.0,
        },
        planned_maneuvers=[],
        engine_thrust_n=100_000.0,
        engine_specific_impulse_s=450.0,
        oxygen_kg=5.0,
        oxygen_consumption_rate_kg_s=0.001,
        battery_kwh=10.0,
        power_consumption_kw=1.0,
        simulation_speed=simulation_speed,
        integration_step_s=1.0,
        checkpoint_interval_s=checkpoint_interval_s,
    )


@pytest.mark.asyncio
async def test_initialize_creates_simulation_and_checkpoint(
    session: AsyncSession,
) -> None:
    service = SimulationService(session)
    request = _request()

    simulation = await service.initialize(request)

    assert simulation.status is SimulationStatus.INITIALIZED
    assert simulation.mission_id == request.mission_id

    checkpoints = await service.get_checkpoints(request.mission_id)

    assert len(checkpoints) == 1
    assert checkpoints[0].reason is CheckpointReason.INITIALIZED
    assert checkpoints[0].simulated_time_s == pytest.approx(0.0)


@pytest.mark.asyncio
async def test_duplicate_initialization_is_rejected(
    session: AsyncSession,
) -> None:
    service = SimulationService(session)
    request = _request()

    await service.initialize(request)

    with pytest.raises(SimulationAlreadyExistsError):
        await service.initialize(request)


@pytest.mark.asyncio
async def test_start_pause_and_resume_simulation(
    session: AsyncSession,
) -> None:
    service = SimulationService(session)
    request = _request()

    await service.initialize(request)

    simulation = await service.start(request.mission_id)

    assert simulation.status is SimulationStatus.RUNNING
    assert simulation.started_at is not None

    simulation = await service.pause(request.mission_id)

    assert simulation.status is SimulationStatus.PAUSED
    assert simulation.paused_at is not None

    simulation = await service.resume(request.mission_id)

    assert simulation.status is SimulationStatus.RUNNING
    assert simulation.paused_at is None


@pytest.mark.asyncio
async def test_invalid_transition_is_rejected(
    session: AsyncSession,
) -> None:
    service = SimulationService(session)
    request = _request()

    await service.initialize(request)

    with pytest.raises(InvalidSimulationTransitionError):
        await service.pause(request.mission_id)


@pytest.mark.asyncio
async def test_simulation_speed_controls_simulated_time(
    session: AsyncSession,
) -> None:
    service = SimulationService(session)
    request = _request(simulation_speed=10)

    await service.initialize(request)
    await service.start(request.mission_id)

    runtime = await service.advance(
        request.mission_id,
        real_duration_s=1.0,
    )

    assert runtime.state.elapsed_time_s == pytest.approx(10.0)


@pytest.mark.asyncio
async def test_periodic_checkpoint_is_created(
    session: AsyncSession,
) -> None:
    service = SimulationService(session)

    request = _request(checkpoint_interval_s=5.0)

    await service.initialize(request)
    await service.start(request.mission_id)

    await service.advance(
        request.mission_id,
        real_duration_s=6.0,
    )

    checkpoints = await service.get_checkpoints(request.mission_id)

    assert len(checkpoints) == 2

    assert checkpoints[0].reason is CheckpointReason.INITIALIZED
    assert checkpoints[1].reason is CheckpointReason.PERIODIC

    assert checkpoints[1].simulated_time_s == pytest.approx(6.0)


@pytest.mark.asyncio
async def test_pause_creates_checkpoint(
    session: AsyncSession,
) -> None:
    service = SimulationService(session)
    request = _request()

    await service.initialize(request)
    await service.start(request.mission_id)

    await service.advance(
        request.mission_id,
        real_duration_s=2.0,
    )

    await service.pause(request.mission_id)

    checkpoints = await service.get_checkpoints(request.mission_id)

    assert checkpoints[-1].reason is CheckpointReason.PAUSED
    assert checkpoints[-1].simulated_time_s == pytest.approx(2.0)


@pytest.mark.asyncio
async def test_begin_abort_cancels_pending_and_active_maneuvers(
    session: AsyncSession,
) -> None:
    service = SimulationService(session)

    request = _request()

    request_with_maneuvers = SimulationInitializeRequest.model_validate(
        {
            **request.model_dump(),
            "planned_maneuvers": [
                {
                    "id": str(uuid4()),
                    "sequence": 1,
                    "maneuver_type": "ORBIT_RAISE",
                    "delta_v_m_s": 100.0,
                    "planned_offset_s": 0.0,
                },
                {
                    "id": str(uuid4()),
                    "sequence": 2,
                    "maneuver_type": "DEORBIT_BURN",
                    "delta_v_m_s": 50.0,
                    "planned_offset_s": 120.0,
                },
            ],
        }
    )

    await service.initialize(request_with_maneuvers)

    _, runtime = await service.begin_abort(request_with_maneuvers.mission_id)

    assert len(runtime.maneuvers) == 2

    assert all(
        maneuver.status is ManeuverExecutionStatus.CANCELLED for maneuver in runtime.maneuvers
    )

    assert all(maneuver.remaining_burn_s is None for maneuver in runtime.maneuvers)


@pytest.mark.asyncio
async def test_abort_maneuver_is_rejected_when_engine_is_unavailable(
    session: AsyncSession,
) -> None:
    service = SimulationService(session)

    request = _request()

    await service.initialize(request)

    runtime = runtime_store.get(request.mission_id)

    assert runtime is not None

    runtime.active_faults[FaultType.ENGINE_FAILURE] = ActiveFault(
        fault_type=FaultType.ENGINE_FAILURE,
        magnitude=1.0,
    )

    with pytest.raises(
        SimulationExecutionError,
        match="engine thrust is unavailable",
    ):
        await service.execute_abort_maneuver(
            request.mission_id,
            maneuver_id=uuid4(),
            delta_v_m_s=100.0,
        )
