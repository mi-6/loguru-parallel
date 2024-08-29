from joblib import Parallel
from loguru import logger
from sinks import config_stdout_sink

from loguru_parallel import (
    delayed_with_logger,
    loguru_enqueue_and_listen,
)


def worker_func(x):
    logger.info(f"Hello {x}")


if __name__ == "__main__":
    loguru_enqueue_and_listen(config_stdout_sink)

    logger.info("Starting")

    def _test_patcher(record):
        record["message"] = record["message"] + " (from patcher)"

    logger.configure(patcher=_test_patcher)

    funcs = [delayed_with_logger(worker_func, logger)(x) for x in range(10)]
    Parallel(n_jobs=4)(funcs)

    logger.info("Finished")
