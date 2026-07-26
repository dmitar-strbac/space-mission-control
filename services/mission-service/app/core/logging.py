import logging
import sys


def configure_logging(log_level: str) -> None:
    normalized_level = log_level.upper()

    logging.basicConfig(
        level=normalized_level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        stream=sys.stdout,
        force=True,
    )
