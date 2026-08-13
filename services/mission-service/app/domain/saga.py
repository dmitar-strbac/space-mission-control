from app.domain.enums import (
    SagaStepStatus,
    SagaStepType,
)

PREPARE_MISSION_STEP_ORDER: tuple[
    SagaStepType,
    ...,
] = (
    SagaStepType.VEHICLE_RESERVATION,
    SagaStepType.TRAJECTORY_PLANNING,
    SagaStepType.RESOURCE_VALIDATION,
    SagaStepType.COMMUNICATION_PROFILE,
    SagaStepType.SIMULATION_INITIALIZATION,
)


def get_next_step(
    current_step: SagaStepType,
) -> SagaStepType | None:
    try:
        index = PREPARE_MISSION_STEP_ORDER.index(current_step)
    except ValueError:
        return None

    next_index = index + 1

    if next_index >= len(PREPARE_MISSION_STEP_ORDER):
        return None

    return PREPARE_MISSION_STEP_ORDER[next_index]


def get_compensation_order(
    completed_steps: set[SagaStepType],
) -> tuple[SagaStepType, ...]:
    return tuple(step for step in reversed(PREPARE_MISSION_STEP_ORDER) if step in completed_steps)


def is_terminal_step_status(
    status: SagaStepStatus,
) -> bool:
    return status in {
        SagaStepStatus.COMPLETED,
        SagaStepStatus.FAILED,
        SagaStepStatus.COMPENSATED,
    }
