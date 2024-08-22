from loguru import logger
from joblib import Parallel, delayed
from loguru_parallel.listener import start_log_listener

from loguru_parallel.worker import worker_func
from loguru_parallel.propagate import propagate_logger
import sys


def _configure_sink_logger() -> None:
    logger.remove()
    logger.add(sys.stdout)


if __name__ == "__main__":
    start_log_listener(_configure_sink_logger)

    logger.info("Starting")

    def _test_patcher(record):
        record["message"] = record["message"] + " (from patcher)"

    logger.configure(patcher=_test_patcher)

    funcs = [delayed(propagate_logger(worker_func))(x) for x in range(10)]
    Parallel(n_jobs=4)(funcs)

    logger.info("Finished")
