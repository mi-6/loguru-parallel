import sys

from loguru import logger


def _configure_sink_logger() -> None:
    logger.remove()
    logger.add(sys.stdout)
