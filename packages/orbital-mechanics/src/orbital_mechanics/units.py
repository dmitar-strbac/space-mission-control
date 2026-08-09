METRES_PER_KILOMETRE: float = 1_000.0
SECONDS_PER_MINUTE: float = 60.0


def kilometres_to_metres(value_km: float) -> float:
    return value_km * METRES_PER_KILOMETRE


def metres_to_kilometres(value_m: float) -> float:
    return value_m / METRES_PER_KILOMETRE


def kilometres_per_second_to_metres_per_second(value_km_s: float) -> float:
    return value_km_s * METRES_PER_KILOMETRE


def metres_per_second_to_kilometres_per_second(value_m_s: float) -> float:
    return value_m_s / METRES_PER_KILOMETRE


def minutes_to_seconds(value_min: float) -> float:
    return value_min * SECONDS_PER_MINUTE


def seconds_to_minutes(value_s: float) -> float:
    return value_s / SECONDS_PER_MINUTE
