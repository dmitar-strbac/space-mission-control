import pytest

from app.domain.enums import (
    MissionType,
    SpacecraftStatus,
    ValidationViolationCode,
)
from app.domain.validation import validate_preliminary_configuration


def validate(
    *,
    status: SpacecraftStatus = SpacecraftStatus.AVAILABLE,
    mission_type: MissionType = MissionType.LEO,
    crew_count: int = 3,
    payload_mass_kg: float = 1_000.0,
    duration_h: float = 24.0,
):
    return validate_preliminary_configuration(
        status=status,
        supported_mission_types=frozenset(
            {
                MissionType.LEO,
                MissionType.LEO_RENDEZVOUS,
            }
        ),
        requested_mission_type=mission_type,
        crew_capacity=4,
        requested_crew_count=crew_count,
        max_payload_kg=2_000.0,
        requested_payload_mass_kg=payload_mass_kg,
        max_mission_duration_h=72.0,
        requested_duration_h=duration_h,
        dry_mass_kg=8_000.0,
        propellant_capacity_kg=4_000.0,
        engine_specific_impulse_s=320.0,
    )


def test_valid_configuration_returns_positive_delta_v() -> None:
    result = validate()

    assert result.valid is True
    assert result.violations == ()
    assert result.initial_mass_kg == pytest.approx(13_000.0)
    assert result.available_delta_v_m_s > 0.0


def test_validation_reports_all_detected_violations() -> None:
    result = validate(
        status=SpacecraftStatus.MAINTENANCE,
        mission_type=MissionType.LUNAR,
        crew_count=6,
        payload_mass_kg=3_000.0,
        duration_h=100.0,
    )

    codes = {violation.code for violation in result.violations}

    assert result.valid is False
    assert codes == {
        ValidationViolationCode.VEHICLE_NOT_AVAILABLE,
        ValidationViolationCode.MISSION_TYPE_NOT_SUPPORTED,
        ValidationViolationCode.CREW_CAPACITY_EXCEEDED,
        ValidationViolationCode.PAYLOAD_CAPACITY_EXCEEDED,
        ValidationViolationCode.MISSION_DURATION_EXCEEDED,
    }


def test_payload_mass_is_included_in_delta_v_calculation() -> None:
    lighter = validate(payload_mass_kg=500.0)
    heavier = validate(payload_mass_kg=1_500.0)

    assert lighter.available_delta_v_m_s > heavier.available_delta_v_m_s
