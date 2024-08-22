from loguru import logger
import sys


def _configure_sink_logger() -> None:
    logger.remove()
    logger.add(sys.stdout)
