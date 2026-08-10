import pytest

from app.domain.command import (
    can_transition,
    is_terminal_status,
)
from app.domain.enums import CommandStatus


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (
            CommandStatus.CREATED,
            CommandStatus.QUEUED,
        ),
        (
            CommandStatus.CREATED,
            CommandStatus.REJECTED,
        ),
        (
            CommandStatus.QUEUED,
            CommandStatus.IN_TRANSIT,
        ),
        (
            CommandStatus.QUEUED,
            CommandStatus.EXPIRED,
        ),
        (
            CommandStatus.QUEUED,
            CommandStatus.LOST,
        ),
        (
            CommandStatus.IN_TRANSIT,
            CommandStatus.DELIVERED,
        ),
        (
            CommandStatus.IN_TRANSIT,
            CommandStatus.EXPIRED,
        ),
        (
            CommandStatus.IN_TRANSIT,
            CommandStatus.LOST,
        ),
        (
            CommandStatus.DELIVERED,
            CommandStatus.EXECUTED,
        ),
        (
            CommandStatus.DELIVERED,
            CommandStatus.REJECTED,
        ),
    ],
)
def test_valid_command_transitions(
    current: CommandStatus,
    target: CommandStatus,
) -> None:
    assert can_transition(
        current,
        target,
    )


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (
            CommandStatus.CREATED,
            CommandStatus.EXECUTED,
        ),
        (
            CommandStatus.QUEUED,
            CommandStatus.DELIVERED,
        ),
        (
            CommandStatus.IN_TRANSIT,
            CommandStatus.EXECUTED,
        ),
        (
            CommandStatus.EXECUTED,
            CommandStatus.QUEUED,
        ),
        (
            CommandStatus.LOST,
            CommandStatus.DELIVERED,
        ),
        (
            CommandStatus.REJECTED,
            CommandStatus.EXECUTED,
        ),
    ],
)
def test_invalid_command_transitions(
    current: CommandStatus,
    target: CommandStatus,
) -> None:
    assert not can_transition(
        current,
        target,
    )


@pytest.mark.parametrize(
    "status",
    [
        CommandStatus.EXECUTED,
        CommandStatus.REJECTED,
        CommandStatus.EXPIRED,
        CommandStatus.LOST,
    ],
)
def test_terminal_command_statuses(
    status: CommandStatus,
) -> None:
    assert is_terminal_status(status)


@pytest.mark.parametrize(
    "status",
    [
        CommandStatus.CREATED,
        CommandStatus.QUEUED,
        CommandStatus.IN_TRANSIT,
        CommandStatus.DELIVERED,
    ],
)
def test_non_terminal_command_statuses(
    status: CommandStatus,
) -> None:
    assert not is_terminal_status(status)
