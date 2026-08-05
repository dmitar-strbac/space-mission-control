from app.domain.enums import MissionStatus

ALLOWED_STATUS_TRANSITIONS: dict[MissionStatus, frozenset[MissionStatus]] = {
    MissionStatus.DRAFT: frozenset({MissionStatus.PLANNING, MissionStatus.PREPARING}),
    MissionStatus.PLANNING: frozenset({MissionStatus.PREPARING, MissionStatus.FAILED_PREPARATION}),
    MissionStatus.PREPARING: frozenset({MissionStatus.READY, MissionStatus.FAILED_PREPARATION}),
    MissionStatus.READY: frozenset({MissionStatus.IN_PROGRESS}),
    MissionStatus.IN_PROGRESS: frozenset(
        {MissionStatus.COMPLETED, MissionStatus.ABORTING, MissionStatus.FAILED}
    ),
    MissionStatus.ABORTING: frozenset({MissionStatus.ABORTED, MissionStatus.FAILED}),
    MissionStatus.COMPLETED: frozenset(),
    MissionStatus.ABORTED: frozenset(),
    MissionStatus.FAILED_PREPARATION: frozenset(),
    MissionStatus.FAILED: frozenset(),
}


def can_transition(current: MissionStatus, target: MissionStatus) -> bool:
    return target in ALLOWED_STATUS_TRANSITIONS[current]
