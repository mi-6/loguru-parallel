from loguru import logger
from joblib import Parallel, delayed
from loguru_parallel.listener import start_log_listener
from loguru_parallel.log_queue import enqueue_logger
from loguru_parallel.worker import worker_func
from loguru_parallel.utils import inherit_logger
import sys


def _configure_sink_logger() -> None:
    logger.remove()
    logger.add(sys.stdout)


if __name__ == "__main__":
    enqueue_logger()

    logger.info("Starting")

    def _test_patcher(record):
        record["message"] = record["message"] + " (from patcher)"

    logger.configure(patcher=_test_patcher)

    start_log_listener(_configure_sink_logger)

    funcs = [delayed(inherit_logger(worker_func))(x) for x in range(10)]
    Parallel(n_jobs=4)(funcs)

    logger.info("Finished")
