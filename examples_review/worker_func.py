from loguru import logger


def worker_func(x):
    logger.info(f"Hello {x}")
