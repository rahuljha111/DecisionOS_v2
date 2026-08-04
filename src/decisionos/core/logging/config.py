import logging

from decisionos.core.config.settings import settings


def configure_logging() -> None:
    """Configure the application's logging."""

    logging.basicConfig(
        level=settings.log_level.upper(),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )