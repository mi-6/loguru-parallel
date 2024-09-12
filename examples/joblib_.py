import sys

from joblib import Parallel, delayed
from loguru import logger
from worker_func import worker_func

from loguru_parallel import (
    loguru_enqueue_and_listen,
    propagate_logger,
)

if __name__ == "__main__":
    loguru_enqueue_and_listen(handlers=[dict(sink=sys.stderr)])
    logger.info("Starting")

    def _test_patcher(record):
        record["message"] = record["message"] + " (with patcher)"

    logger.configure(patcher=_test_patcher)

    worker_func = propagate_logger(worker_func, logger)
    funcs = [delayed(worker_func)(x) for x in range(3)]

    logger.info("Loky")
    Parallel(n_jobs=4, backend="loky")(funcs)

    logger.info("Multiprocessing")
    Parallel(n_jobs=4, backend="multiprocessing")(funcs)

    logger.info("Threading")
    Parallel(n_jobs=4, backend="threading")(funcs)

    logger.info("Sequential")
    Parallel(n_jobs=1, backend="sequential")(funcs)

    logger.info("Finished")
