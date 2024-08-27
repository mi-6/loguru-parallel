import sys

from joblib import Parallel, delayed
from loguru import logger

from loguru_parallel import loguru_enqueue_and_listen, propagate_logger


def worker_func(x):
    logger.info(f"Hello {x}")


def _configure_sink_logger() -> None:
    logger.remove()
    logger.add(sys.stdout)


if __name__ == "__main__":
    loguru_enqueue_and_listen(_configure_sink_logger)

    logger.info("Starting")

    def _test_patcher(record):
        record["message"] = record["message"] + " (from patcher)"

    logger.configure(patcher=_test_patcher)

    funcs = [delayed(propagate_logger(worker_func))(x) for x in range(10)]
    Parallel(n_jobs=4)(funcs)

    logger.info("Finished")
