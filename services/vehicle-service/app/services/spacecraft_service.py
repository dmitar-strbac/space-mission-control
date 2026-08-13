from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums import MissionType, SpacecraftStatus
from app.domain.exceptions import (
    InvalidManualStatusError,
    SpacecraftDeletionConflictError,
    SpacecraftModificationConflictError,
    SpacecraftNameConflictError,
    SpacecraftNotFoundError,
    VehicleReservationConflictError,
    VehicleValidationRejectedError,
)
from app.domain.validation import (
    FinalResourceValidationResult,
    PreliminaryValidationResult,
    validate_final_resources,
    validate_preliminary_configuration,
)
from app.models.resource_reservation import ResourceReservation
from app.models.spacecraft import Spacecraft
from app.repositories.resource_reservation_repository import ResourceReservationRepository
from app.repositories.spacecraft_repository import SpacecraftRepository
from app.schemas.saga import FinalResourceValidationRequest, VehicleReservationRequest
from app.schemas.spacecraft import (
    SpacecraftCreate,
    SpacecraftListResponse,
    SpacecraftResponse,
    SpacecraftUpdate,
)
from app.schemas.validation import (
    SpacecraftValidationRequest,
    SpacecraftValidationResponse,
    ValidationViolation,
)


class SpacecraftService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repository = SpacecraftRepository(session)
        self._reservations = ResourceReservationRepository(session)

    async def create(
        self,
        request: SpacecraftCreate,
    ) -> Spacecraft:
        existing = await self._repository.get_by_name(request.name)

        if existing is not None:
            raise SpacecraftNameConflictError(request.name)

        spacecraft = Spacecraft(
            name=request.name,
            vehicle_type=request.vehicle_type,
            supported_mission_types=[
                mission_type.value for mission_type in request.supported_mission_types
            ],
            dry_mass_kg=request.dry_mass_kg,
            max_payload_kg=request.max_payload_kg,
            crew_capacity=request.crew_capacity,
            engine_thrust_n=request.engine_thrust_n,
            engine_specific_impulse_s=request.engine_specific_impulse_s,
            propellant_capacity_kg=request.propellant_capacity_kg,
            oxygen_capacity_kg=request.oxygen_capacity_kg,
            battery_capacity_kwh=request.battery_capacity_kwh,
            max_mission_duration_h=request.max_mission_duration_h,
            max_acceleration_g=request.max_acceleration_g,
            status=SpacecraftStatus.AVAILABLE,
        )

        self._repository.add(spacecraft)

        try:
            await self._session.commit()
        except IntegrityError as error:
            await self._session.rollback()
            raise SpacecraftNameConflictError(request.name) from error

        await self._session.refresh(spacecraft)

        return spacecraft

    async def get(self, spacecraft_id: UUID) -> Spacecraft:
        spacecraft = await self._repository.get_by_id(spacecraft_id)

        if spacecraft is None:
            raise SpacecraftNotFoundError(spacecraft_id)

        return spacecraft

    async def list(
        self,
        *,
        offset: int,
        limit: int,
    ) -> SpacecraftListResponse:
        spacecraft = await self._repository.list(
            offset=offset,
            limit=limit,
        )
        total = await self._repository.count()

        return SpacecraftListResponse(
            items=[SpacecraftResponse.model_validate(item) for item in spacecraft],
            total=total,
            offset=offset,
            limit=limit,
        )

    async def update(
        self,
        spacecraft_id: UUID,
        request: SpacecraftUpdate,
    ) -> Spacecraft:
        spacecraft = await self.get(spacecraft_id)

        if spacecraft.status is SpacecraftStatus.RESERVED:
            raise SpacecraftModificationConflictError(
                spacecraft_id=spacecraft.id,
                status=spacecraft.status,
            )

        if request.status is SpacecraftStatus.RESERVED:
            raise InvalidManualStatusError(request.status)

        existing = await self._repository.get_by_name(request.name)

        if existing is not None and existing.id != spacecraft.id:
            raise SpacecraftNameConflictError(request.name)

        spacecraft.name = request.name
        spacecraft.vehicle_type = request.vehicle_type
        spacecraft.supported_mission_types = [
            mission_type.value for mission_type in request.supported_mission_types
        ]
        spacecraft.dry_mass_kg = request.dry_mass_kg
        spacecraft.max_payload_kg = request.max_payload_kg
        spacecraft.crew_capacity = request.crew_capacity
        spacecraft.engine_thrust_n = request.engine_thrust_n
        spacecraft.engine_specific_impulse_s = request.engine_specific_impulse_s
        spacecraft.propellant_capacity_kg = request.propellant_capacity_kg
        spacecraft.oxygen_capacity_kg = request.oxygen_capacity_kg
        spacecraft.battery_capacity_kwh = request.battery_capacity_kwh
        spacecraft.max_mission_duration_h = request.max_mission_duration_h
        spacecraft.max_acceleration_g = request.max_acceleration_g
        spacecraft.status = request.status

        try:
            await self._session.commit()
        except IntegrityError as error:
            await self._session.rollback()
            raise SpacecraftNameConflictError(request.name) from error

        await self._session.refresh(spacecraft)

        return spacecraft

    async def delete(self, spacecraft_id: UUID) -> None:
        spacecraft = await self.get(spacecraft_id)

        if spacecraft.status is SpacecraftStatus.RESERVED:
            raise SpacecraftDeletionConflictError(
                spacecraft_id=spacecraft.id,
                status=spacecraft.status,
            )

        await self._repository.delete(spacecraft)
        await self._session.commit()

    async def validate(
        self,
        spacecraft_id: UUID,
        request: SpacecraftValidationRequest,
    ) -> SpacecraftValidationResponse:
        spacecraft = await self.get(spacecraft_id)

        supported_mission_types = frozenset(
            MissionType(value) for value in spacecraft.supported_mission_types
        )

        result = validate_preliminary_configuration(
            status=spacecraft.status,
            supported_mission_types=supported_mission_types,
            requested_mission_type=request.mission_type,
            crew_capacity=spacecraft.crew_capacity,
            requested_crew_count=request.crew_count,
            max_payload_kg=spacecraft.max_payload_kg,
            requested_payload_mass_kg=request.payload_mass_kg,
            max_mission_duration_h=spacecraft.max_mission_duration_h,
            requested_duration_h=request.estimated_duration_h,
            dry_mass_kg=spacecraft.dry_mass_kg,
            propellant_capacity_kg=spacecraft.propellant_capacity_kg,
            engine_specific_impulse_s=(spacecraft.engine_specific_impulse_s),
        )

        return SpacecraftValidationResponse(
            spacecraft_id=spacecraft.id,
            valid=result.valid,
            initial_mass_kg=result.initial_mass_kg,
            available_delta_v_m_s=result.available_delta_v_m_s,
            violations=[
                ValidationViolation(
                    code=violation.code,
                    message=violation.message,
                )
                for violation in result.violations
            ],
        )

    async def reserve_for_mission(
        self,
        request: VehicleReservationRequest,
    ) -> tuple[
        Spacecraft,
        PreliminaryValidationResult,
    ]:
        existing = await self._reservations.get_by_mission_id(request.mission_id)

        if existing is not None:
            if existing.spacecraft_id != request.vehicle_id:
                raise VehicleReservationConflictError(request.vehicle_id)

            reserved_spacecraft = await self.get(existing.spacecraft_id)

            result = self._validate_for_reservation(
                reserved_spacecraft,
                request,
            )

            return reserved_spacecraft, result

        spacecraft = await self._repository.get_by_id(
            request.vehicle_id,
            for_update=True,
        )

        if spacecraft is None:
            raise SpacecraftNotFoundError(request.vehicle_id)

        occupied = await self._reservations.get_by_spacecraft_id(spacecraft.id)

        if occupied is not None:
            raise VehicleReservationConflictError(spacecraft.id)

        result = self._validate_for_reservation(
            spacecraft,
            request,
        )

        if not result.valid:
            messages = "; ".join(violation.message for violation in result.violations)

            raise VehicleValidationRejectedError(messages)

        spacecraft.status = SpacecraftStatus.RESERVED

        self._reservations.add(
            ResourceReservation(
                mission_id=request.mission_id,
                spacecraft_id=spacecraft.id,
            )
        )

        await self._session.commit()
        await self._session.refresh(spacecraft)

        return spacecraft, result

    async def validate_final_resources_for_mission(
        self,
        request: FinalResourceValidationRequest,
    ) -> FinalResourceValidationResult:
        reservation = await self._reservations.get_by_mission_id(request.mission_id)

        if reservation is None or reservation.spacecraft_id != request.vehicle_id:
            raise VehicleValidationRejectedError(
                "Mission does not own the requested spacecraft reservation."
            )

        spacecraft = await self.get(request.vehicle_id)

        result = validate_final_resources(
            total_mass_kg=request.total_mass_kg,
            required_propellant_kg=(request.required_propellant_kg),
            propellant_capacity_kg=(spacecraft.propellant_capacity_kg),
            minimum_propellant_reserve_percent=(request.minimum_propellant_reserve_percent),
            mission_duration_s=(request.mission_duration_s),
            oxygen_capacity_kg=(spacecraft.oxygen_capacity_kg),
            oxygen_consumption_rate_kg_s=(request.oxygen_consumption_rate_kg_s),
            battery_capacity_kwh=(spacecraft.battery_capacity_kwh),
            power_consumption_kw=(request.power_consumption_kw),
            engine_thrust_n=(spacecraft.engine_thrust_n),
            max_acceleration_g=(spacecraft.max_acceleration_g),
        )

        if not result.valid:
            messages = "; ".join(violation.message for violation in result.violations)

            raise VehicleValidationRejectedError(messages)

        return result

    def _validate_for_reservation(
        self,
        spacecraft: Spacecraft,
        request: VehicleReservationRequest,
    ) -> PreliminaryValidationResult:
        supported_mission_types = frozenset(
            MissionType(value) for value in spacecraft.supported_mission_types
        )

        return validate_preliminary_configuration(
            status=spacecraft.status,
            supported_mission_types=(supported_mission_types),
            requested_mission_type=(request.mission_type),
            crew_capacity=(spacecraft.crew_capacity),
            requested_crew_count=(request.crew_count),
            max_payload_kg=(spacecraft.max_payload_kg),
            requested_payload_mass_kg=(request.payload_mass_kg),
            max_mission_duration_h=(spacecraft.max_mission_duration_h),
            requested_duration_h=0.0,
            dry_mass_kg=spacecraft.dry_mass_kg,
            propellant_capacity_kg=(spacecraft.propellant_capacity_kg),
            engine_specific_impulse_s=(spacecraft.engine_specific_impulse_s),
        )

    async def release_for_mission(
        self,
        mission_id: UUID,
    ) -> Spacecraft | None:
        reservation = await self._reservations.get_by_mission_id(mission_id)

        if reservation is None:
            return None

        spacecraft = await self._repository.get_by_id(
            reservation.spacecraft_id,
            for_update=True,
        )

        await self._reservations.delete(reservation)

        if spacecraft is not None:
            spacecraft.status = SpacecraftStatus.AVAILABLE

        await self._session.commit()

        if spacecraft is not None:
            await self._session.refresh(spacecraft)

        return spacecraft
