from app.domain.enums import MissionStatus
from app.domain.transitions import can_transition


def test_draft_can_start_preparation() -> None:
    assert can_transition(MissionStatus.DRAFT, MissionStatus.PREPARING)


def test_draft_cannot_launch() -> None:
    assert not can_transition(MissionStatus.DRAFT, MissionStatus.IN_PROGRESS)


def test_terminal_status_cannot_transition() -> None:
    assert not can_transition(MissionStatus.COMPLETED, MissionStatus.ABORTING)
