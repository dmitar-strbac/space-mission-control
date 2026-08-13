from app.domain.enums import SagaStepType
from app.domain.saga import (
    PREPARE_MISSION_STEP_ORDER,
    get_compensation_order,
    get_next_step,
)


def test_prepare_mission_step_order() -> None:
    assert PREPARE_MISSION_STEP_ORDER == (
        SagaStepType.VEHICLE_RESERVATION,
        SagaStepType.TRAJECTORY_PLANNING,
        SagaStepType.RESOURCE_VALIDATION,
        SagaStepType.COMMUNICATION_PROFILE,
        SagaStepType.SIMULATION_INITIALIZATION,
    )


def test_get_next_step() -> None:
    assert get_next_step(SagaStepType.VEHICLE_RESERVATION) is SagaStepType.TRAJECTORY_PLANNING

    assert get_next_step(SagaStepType.SIMULATION_INITIALIZATION) is None


def test_compensation_order_is_reversed() -> None:
    completed = {
        SagaStepType.VEHICLE_RESERVATION,
        SagaStepType.TRAJECTORY_PLANNING,
        SagaStepType.RESOURCE_VALIDATION,
    }

    assert get_compensation_order(completed) == (
        SagaStepType.RESOURCE_VALIDATION,
        SagaStepType.TRAJECTORY_PLANNING,
        SagaStepType.VEHICLE_RESERVATION,
    )
