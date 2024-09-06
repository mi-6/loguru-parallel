import multiprocessing as mp
import sys

from loguru import logger
from worker_func import worker_func

from loguru_parallel import (
    loguru_enqueue_and_listen,
    propagate_logger,
)


def config_sink() -> None:
    logger.remove()
    logger.add(sys.stderr, serialize=True)


if __name__ == "__main__":
    loguru_enqueue_and_listen(config_sink)

    logger.info("Starting")

    def _test_patcher(record):
        record["message"] = record["message"] + " (with patcher)"

    logger.configure(patcher=_test_patcher, extra={"test": "extra"})

    with mp.Pool(4) as pool:
        pool.map(propagate_logger(worker_func, logger), range(3))

    logger.info("Finished")
