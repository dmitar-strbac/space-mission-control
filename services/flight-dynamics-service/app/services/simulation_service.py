from collections.abc import Sequence
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.engine import (
    SimulationConfiguration,
    advance_runtime,
)
from app.domain.enums import (
    CheckpointReason,
    ManeuverExecutionStatus,
    SimulationStatus,
)
from app.domain.exceptions import (
    InvalidSimulationTransitionError,
    SimulationAlreadyExistsError,
    SimulationExecutionError,
    SimulationNotFoundError,
    SimulationStateUnavailableError,
)
from app.domain.runtime import (
    RuntimeManeuver,
    SimulationRuntime,
)
from app.domain.simulation import (
    can_transition,
    validate_simulation_speed,
)
from app.models.simulation_checkpoint import (
    SimulationCheckpoint,
)
from app.models.simulation_session import (
    SimulationSession,
)
from app.repositories.simulation_repository import (
    SimulationRepository,
)
from app.schemas.simulation import (
    SimulationInitializeRequest,
)
from app.services.runtime_store import runtime_store
from orbital_mechanics.models import (
    EngineParameters,
    StateVector,
    Vector2D,
)


class SimulationService:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session
        self._repository = SimulationRepository(session)

    async def initialize(
        self,
        request: SimulationInitializeRequest,
    ) -> SimulationSession:
        existing = await self._repository.get_by_mission_id(request.mission_id)

        if existing is not None:
            raise SimulationAlreadyExistsError(request.mission_id)

        validate_simulation_speed(request.simulation_speed)

        simulation = SimulationSession(
            mission_id=request.mission_id,
            trajectory_plan_id=request.trajectory_plan_id,
            vehicle_id=request.vehicle_id,
            status=SimulationStatus.INITIALIZED,
            simulation_speed=request.simulation_speed,
            integration_step_s=request.integration_step_s,
            checkpoint_interval_s=(request.checkpoint_interval_s),
            initial_state_vector=(request.initial_state_vector.model_dump()),
            planned_maneuvers=[
                maneuver.model_dump(mode="json") for maneuver in request.planned_maneuvers
            ],
            engine_thrust_n=request.engine_thrust_n,
            engine_specific_impulse_s=(request.engine_specific_impulse_s),
            oxygen_kg=request.oxygen_kg,
            oxygen_consumption_rate_kg_s=(request.oxygen_consumption_rate_kg_s),
            battery_kwh=request.battery_kwh,
            power_consumption_kw=(request.power_consumption_kw),
        )

        self._repository.add_session(simulation)

        await self._session.flush()

        runtime = _create_runtime(request)

        runtime_store.set(
            request.mission_id,
            runtime,
        )

        self._add_checkpoint(
            simulation=simulation,
            runtime=runtime,
            reason=CheckpointReason.INITIALIZED,
        )

        await self._session.commit()
        await self._session.refresh(simulation)

        return simulation

    async def get(
        self,
        mission_id: UUID,
    ) -> SimulationSession:
        simulation = await self._repository.get_by_mission_id(mission_id)

        if simulation is None:
            raise SimulationNotFoundError(mission_id)

        return simulation

    async def start(
        self,
        mission_id: UUID,
    ) -> SimulationSession:
        return await self._transition(
            mission_id=mission_id,
            target=SimulationStatus.RUNNING,
            started=True,
        )

    async def pause(
        self,
        mission_id: UUID,
    ) -> SimulationSession:
        simulation = await self._transition(
            mission_id=mission_id,
            target=SimulationStatus.PAUSED,
            paused=True,
        )

        runtime = self._get_runtime(mission_id)

        self._add_checkpoint(
            simulation=simulation,
            runtime=runtime,
            reason=CheckpointReason.PAUSED,
        )

        await self._session.commit()

        return simulation

    async def resume(
        self,
        mission_id: UUID,
    ) -> SimulationSession:
        return await self._transition(
            mission_id=mission_id,
            target=SimulationStatus.RUNNING,
        )

    async def advance(
        self,
        mission_id: UUID,
        *,
        real_duration_s: float,
    ) -> SimulationRuntime:
        simulation = await self.get(mission_id)

        if simulation.status is not SimulationStatus.RUNNING:
            raise InvalidSimulationTransitionError(
                mission_id=mission_id,
                current_status=simulation.status.value,
                target_status=SimulationStatus.RUNNING.value,
            )

        runtime = self._get_runtime(mission_id)

        simulated_duration_s = real_duration_s * simulation.simulation_speed

        configuration = SimulationConfiguration(
            engine=EngineParameters(
                thrust_n=simulation.engine_thrust_n,
                specific_impulse_s=(simulation.engine_specific_impulse_s),
            ),
            integration_step_s=(simulation.integration_step_s),
            oxygen_consumption_rate_kg_s=(simulation.oxygen_consumption_rate_kg_s),
            power_consumption_kw=(simulation.power_consumption_kw),
        )

        previous_completed = {
            maneuver.id
            for maneuver in runtime.maneuvers
            if maneuver.status is ManeuverExecutionStatus.COMPLETED
        }

        try:
            advance_runtime(
                runtime=runtime,
                configuration=configuration,
                simulated_duration_s=(simulated_duration_s),
            )
        except ValueError as error:
            simulation.status = SimulationStatus.FAILED
            simulation.failure_reason = str(error)

            await self._session.commit()

            raise SimulationExecutionError(
                str(error),
                details={"mission_id": str(mission_id)},
            ) from error

        newly_completed = [
            maneuver
            for maneuver in runtime.maneuvers
            if (
                maneuver.status is ManeuverExecutionStatus.COMPLETED
                and maneuver.id not in previous_completed
            )
        ]

        for _ in newly_completed:
            self._add_checkpoint(
                simulation=simulation,
                runtime=runtime,
                reason=(CheckpointReason.MANEUVER_COMPLETED),
            )

        if (
            runtime.state.elapsed_time_s - runtime.last_checkpoint_time_s
            >= simulation.checkpoint_interval_s
        ):
            self._add_checkpoint(
                simulation=simulation,
                runtime=runtime,
                reason=CheckpointReason.PERIODIC,
            )

            runtime.last_checkpoint_time_s = runtime.state.elapsed_time_s

        await self._session.commit()

        return runtime

    async def get_state(
        self,
        mission_id: UUID,
    ) -> SimulationRuntime:
        await self.get(mission_id)

        return self._get_runtime(mission_id)

    async def get_checkpoints(
        self,
        mission_id: UUID,
    ) -> Sequence[SimulationCheckpoint]:
        simulation = await self.get(mission_id)

        return await self._repository.get_checkpoints(simulation.id)

    async def _transition(
        self,
        *,
        mission_id: UUID,
        target: SimulationStatus,
        started: bool = False,
        paused: bool = False,
    ) -> SimulationSession:
        simulation = await self._repository.get_by_mission_id(
            mission_id,
            for_update=True,
        )

        if simulation is None:
            raise SimulationNotFoundError(mission_id)

        if not can_transition(
            simulation.status,
            target,
        ):
            raise InvalidSimulationTransitionError(
                mission_id=mission_id,
                current_status=simulation.status.value,
                target_status=target.value,
            )

        simulation.status = target

        now = datetime.now(UTC)

        if started and simulation.started_at is None:
            simulation.started_at = now

        if paused:
            simulation.paused_at = now
        elif target is SimulationStatus.RUNNING:
            simulation.paused_at = None

        await self._session.commit()
        await self._session.refresh(simulation)

        return simulation

    def _get_runtime(
        self,
        mission_id: UUID,
    ) -> SimulationRuntime:
        runtime = runtime_store.get(mission_id)

        if runtime is None:
            raise SimulationStateUnavailableError(
                (f"Active simulation state for mission '{mission_id}' is not available in memory."),
                details={"mission_id": str(mission_id)},
            )

        return runtime

    def _add_checkpoint(
        self,
        *,
        simulation: SimulationSession,
        runtime: SimulationRuntime,
        reason: CheckpointReason,
    ) -> None:
        checkpoint = SimulationCheckpoint(
            simulation_session_id=simulation.id,
            simulated_time_s=(runtime.state.elapsed_time_s),
            state_vector=_serialize_state_vector(runtime.state),
            oxygen_kg=runtime.oxygen_kg,
            battery_kwh=runtime.battery_kwh,
            maneuver_states=[
                _serialize_runtime_maneuver(maneuver) for maneuver in runtime.maneuvers
            ],
            reason=reason,
        )

        self._repository.add_checkpoint(checkpoint)


def _create_runtime(
    request: SimulationInitializeRequest,
) -> SimulationRuntime:
    source = request.initial_state_vector

    return SimulationRuntime(
        state=StateVector(
            position=Vector2D(
                x=source.position.x,
                y=source.position.y,
            ),
            velocity=Vector2D(
                x=source.velocity.x,
                y=source.velocity.y,
            ),
            total_mass_kg=source.total_mass_kg,
            propellant_mass_kg=(source.propellant_mass_kg),
            elapsed_time_s=source.elapsed_time_s,
        ),
        oxygen_kg=request.oxygen_kg,
        battery_kwh=request.battery_kwh,
        maneuvers=[
            RuntimeManeuver(
                id=maneuver.id,
                sequence=maneuver.sequence,
                maneuver_type=maneuver.maneuver_type,
                delta_v_m_s=maneuver.delta_v_m_s,
                planned_offset_s=(maneuver.planned_offset_s),
                direction=(
                    Vector2D(
                        x=maneuver.direction.x,
                        y=maneuver.direction.y,
                    )
                    if maneuver.direction is not None
                    else None
                ),
            )
            for maneuver in request.planned_maneuvers
        ],
        last_checkpoint_time_s=(source.elapsed_time_s),
    )


def _serialize_state_vector(
    state: StateVector,
) -> dict[str, object]:
    return {
        "position": {
            "x": state.position.x,
            "y": state.position.y,
        },
        "velocity": {
            "x": state.velocity.x,
            "y": state.velocity.y,
        },
        "total_mass_kg": state.total_mass_kg,
        "propellant_mass_kg": (state.propellant_mass_kg),
        "elapsed_time_s": state.elapsed_time_s,
    }


def _serialize_runtime_maneuver(
    maneuver: RuntimeManeuver,
) -> dict[str, object]:
    return {
        "id": str(maneuver.id),
        "sequence": maneuver.sequence,
        "maneuver_type": maneuver.maneuver_type.value,
        "delta_v_m_s": maneuver.delta_v_m_s,
        "planned_offset_s": (maneuver.planned_offset_s),
        "status": maneuver.status.value,
        "remaining_burn_s": (maneuver.remaining_burn_s),
    }
