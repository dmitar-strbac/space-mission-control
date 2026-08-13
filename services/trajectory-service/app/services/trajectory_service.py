from datetime import timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums import (
    ManeuverStatus,
    ReferenceFrame,
    TrajectoryStatus,
)
from app.domain.exceptions import TrajectoryPlanNotFoundError
from app.domain.planning import calculate_leo_trajectory
from app.models.maneuver import Maneuver
from app.models.trajectory_plan import TrajectoryPlan
from app.repositories.trajectory_repository import TrajectoryRepository
from app.schemas.trajectory import TrajectoryPlanRequest
from orbital_mechanics.models import StateVector
from orbital_mechanics.orbits import create_circular_orbit_state


class TrajectoryService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repository = TrajectoryRepository(session)

    async def plan(
        self,
        request: TrajectoryPlanRequest,
    ) -> TrajectoryPlan:
        result = calculate_leo_trajectory(
            initial_altitude_m=request.initial_altitude_m,
            target_altitude_m=request.target_altitude_m,
            total_mass_kg=request.total_mass_kg,
            available_propellant_kg=request.available_propellant_kg,
            engine_specific_impulse_s=request.engine_specific_impulse_s,
            minimum_propellant_reserve_percent=(request.minimum_propellant_reserve_percent),
        )

        initial_state = create_circular_orbit_state(
            altitude_m=request.initial_altitude_m,
            total_mass_kg=request.total_mass_kg,
            propellant_mass_kg=request.available_propellant_kg,
        )

        target_total_mass_kg = request.total_mass_kg - result.estimated_propellant_kg
        target_propellant_kg = max(
            request.available_propellant_kg - result.estimated_propellant_kg,
            0.0,
        )

        target_state = create_circular_orbit_state(
            altitude_m=request.target_altitude_m,
            total_mass_kg=target_total_mass_kg,
            propellant_mass_kg=target_propellant_kg,
        )

        trajectory_plan = TrajectoryPlan(
            mission_id=request.mission_id,
            reference_frame=ReferenceFrame.EARTH_CENTERED_INERTIAL,
            departure_time=request.departure_time,
            arrival_time=(request.departure_time + timedelta(seconds=result.estimated_duration_s)),
            initial_state_vector=_serialize_state_vector(initial_state),
            target_state_vector=_serialize_state_vector(target_state),
            required_delta_v_m_s=result.required_delta_v_m_s,
            estimated_propellant_kg=result.estimated_propellant_kg,
            propellant_reserve_percent=result.propellant_reserve_percent,
            safety_margin_percent=result.safety_margin_percent,
            window_score=result.window_score,
            status=(TrajectoryStatus.PLANNED if result.feasible else TrajectoryStatus.INFEASIBLE),
        )

        trajectory_plan.maneuvers = [
            Maneuver(
                sequence=maneuver.sequence,
                maneuver_type=maneuver.maneuver_type,
                delta_v_m_s=maneuver.delta_v_m_s,
                planned_offset_s=maneuver.planned_offset_s,
                status=ManeuverStatus.PLANNED,
            )
            for maneuver in result.maneuvers
        ]

        self._repository.add(trajectory_plan)

        await self._session.commit()
        await self._session.refresh(trajectory_plan)

        return await self.get(request.mission_id)

    async def get(
        self,
        mission_id: UUID,
    ) -> TrajectoryPlan:
        trajectory_plan = await self._repository.get_by_mission_id(mission_id)

        if trajectory_plan is None:
            raise TrajectoryPlanNotFoundError(mission_id)

        return trajectory_plan

    async def get_maneuvers(
        self,
        mission_id: UUID,
    ) -> list[Maneuver]:
        trajectory_plan = await self.get(mission_id)
        return list(trajectory_plan.maneuvers)

    async def cancel(
        self,
        mission_id: UUID,
    ) -> TrajectoryPlan | None:
        trajectory = await self._repository.get_by_mission_id(mission_id)

        if trajectory is None:
            return None

        if trajectory.status is not TrajectoryStatus.SUPERSEDED:
            trajectory.status = TrajectoryStatus.SUPERSEDED

            for maneuver in trajectory.maneuvers:
                maneuver.status = ManeuverStatus.CANCELLED

            await self._session.commit()
            await self._session.refresh(trajectory)

        return trajectory


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
        "propellant_mass_kg": state.propellant_mass_kg,
        "elapsed_time_s": state.elapsed_time_s,
    }
