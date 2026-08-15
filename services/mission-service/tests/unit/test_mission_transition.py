from app.domain.enums import MissionStatus
from app.domain.transitions import can_transition


def test_draft_can_start_preparation() -> None:
    assert can_transition(MissionStatus.DRAFT, MissionStatus.PREPARING)


def test_draft_cannot_launch() -> None:
    assert not can_transition(MissionStatus.DRAFT, MissionStatus.IN_PROGRESS)


def test_terminal_status_cannot_transition() -> None:
    assert not can_transition(MissionStatus.COMPLETED, MissionStatus.ABORTING)


def test_in_progress_mission_can_enter_aborting_state() -> None:
    assert can_transition(
        MissionStatus.IN_PROGRESS,
        MissionStatus.ABORTING,
    )


def test_aborting_mission_can_complete_as_aborted() -> None:
    assert can_transition(
        MissionStatus.ABORTING,
        MissionStatus.ABORTED,
    )


def test_aborting_mission_can_fail() -> None:
    assert can_transition(
        MissionStatus.ABORTING,
        MissionStatus.FAILED,
    )
