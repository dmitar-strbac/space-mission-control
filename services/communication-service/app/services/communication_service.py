from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.communication import (
    validate_packet_loss_percent,
)
from app.domain.exceptions import (
    CommunicationProfileAlreadyExistsError,
    CommunicationProfileNotFoundError,
)
from app.models.communication_profile import CommunicationProfile
from app.repositories.communication_profile_repository import CommunicationProfileRepository
from app.schemas.communication_profile import (
    CommunicationProfileCreateRequest,
    CommunicationProfileUpdateRequest,
)


class CommunicationService:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session
        self._repository = CommunicationProfileRepository(session)

    async def create_profile(
        self,
        request: CommunicationProfileCreateRequest,
    ) -> CommunicationProfile:
        existing = await self._repository.get_by_mission_id(request.mission_id)

        if existing is not None:
            raise CommunicationProfileAlreadyExistsError(request.mission_id)

        validate_packet_loss_percent(request.packet_loss_percent)

        profile = CommunicationProfile(
            mission_id=request.mission_id,
            distance_m=request.distance_m,
            additional_latency_ms=request.additional_latency_ms,
            packet_loss_percent=request.packet_loss_percent,
            signal_status=request.signal_status,
        )

        self._repository.add(profile)

        await self._session.commit()
        await self._session.refresh(profile)

        return profile

    async def get_profile(
        self,
        mission_id: UUID,
    ) -> CommunicationProfile:
        profile = await self._repository.get_by_mission_id(mission_id)

        if profile is None:
            raise CommunicationProfileNotFoundError(mission_id)

        return profile

    async def update_profile(
        self,
        mission_id: UUID,
        request: CommunicationProfileUpdateRequest,
    ) -> CommunicationProfile:
        profile = await self._repository.get_by_mission_id(
            mission_id,
            for_update=True,
        )

        if profile is None:
            raise CommunicationProfileNotFoundError(mission_id)

        if request.distance_m is not None:
            profile.distance_m = request.distance_m

        if request.additional_latency_ms is not None:
            profile.additional_latency_ms = request.additional_latency_ms

        if request.packet_loss_percent is not None:
            validate_packet_loss_percent(request.packet_loss_percent)

            profile.packet_loss_percent = request.packet_loss_percent

        if request.signal_status is not None:
            profile.signal_status = request.signal_status

        await self._session.commit()
        await self._session.refresh(profile)

        return profile

    async def remove_profile(
        self,
        mission_id: UUID,
    ) -> None:
        profile = await self._repository.get_by_mission_id(
            mission_id,
            for_update=True,
        )

        if profile is None:
            return

        await self._repository.delete(profile)

        await self._session.commit()
