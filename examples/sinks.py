import sys

from loguru import logger


def config_stdout_sink() -> None:
    logger.remove()
    logger.add(sys.stdout)
