import sys

from joblib import Parallel
from loguru import logger
from worker_func import worker_func

from loguru_parallel import (
    delayed_with_logger,
    loguru_enqueue_and_listen,
)


def config_sink() -> None:
    logger.remove()
    logger.add(sys.stderr)


if __name__ == "__main__":
    loguru_enqueue_and_listen(logger, config_sink)

    logger.info("Starting")

    def _test_patcher(record):
        record["message"] = record["message"] + " (with patcher)"

    logger.configure(patcher=_test_patcher)

    funcs = [delayed_with_logger(worker_func, logger)(x) for x in range(3)]

    logger.info("Loky")
    Parallel(n_jobs=4, backend="loky")(funcs)

    logger.info("Multiprocessing")
    Parallel(n_jobs=4, backend="multiprocessing")(funcs)

    logger.info("Threading")
    Parallel(n_jobs=4, backend="threading")(funcs)

    logger.info("Sequential")
    Parallel(n_jobs=1, backend="sequential")(funcs)

    logger.info("Finished")
