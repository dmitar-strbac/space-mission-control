from app.domain.enums import CommandStatus

_ALLOWED_TRANSITIONS: dict[CommandStatus, set[CommandStatus]] = {
    CommandStatus.CREATED: {
        CommandStatus.QUEUED,
        CommandStatus.REJECTED,
    },
    CommandStatus.QUEUED: {
        CommandStatus.IN_TRANSIT,
        CommandStatus.EXPIRED,
        CommandStatus.LOST,
        CommandStatus.REJECTED,
    },
    CommandStatus.IN_TRANSIT: {
        CommandStatus.DELIVERED,
        CommandStatus.EXPIRED,
        CommandStatus.LOST,
    },
    CommandStatus.DELIVERED: {
        CommandStatus.EXECUTED,
        CommandStatus.REJECTED,
    },
    CommandStatus.EXECUTED: set(),
    CommandStatus.REJECTED: set(),
    CommandStatus.EXPIRED: set(),
    CommandStatus.LOST: set(),
}


def can_transition(
    current_status: CommandStatus,
    target_status: CommandStatus,
) -> bool:
    return target_status in _ALLOWED_TRANSITIONS[current_status]


def is_terminal_status(status: CommandStatus) -> bool:
    return status in {
        CommandStatus.EXECUTED,
        CommandStatus.REJECTED,
        CommandStatus.EXPIRED,
        CommandStatus.LOST,
    }
