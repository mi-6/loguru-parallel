import multiprocessing as mp
import sys

from loguru import logger
from worker_func import worker_func

from loguru_parallel import (
    loguru_enqueue_and_listen,
    propagate_logger,
)

if __name__ == "__main__":
    loguru_enqueue_and_listen(handlers=[dict(sink=sys.stderr, serialize=True)])

    logger.info("Starting")

    def _test_patcher(record):
        record["message"] = record["message"] + " (with patcher)"

    logger.configure(patcher=_test_patcher, extra={"test": "extra"})

    with mp.Pool(4) as pool:
        pool.map(propagate_logger(worker_func, logger), range(3))

    logger.info("Finished")
