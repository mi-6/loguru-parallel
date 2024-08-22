from loguru import logger
from joblib import Parallel, delayed
from loguru_parallel.listener import start_log_listener
from loguru_parallel.worker import worker_func
from loguru_parallel.propagate import propagate_logger
import sys


def _configure_sink_logger() -> None:
    logger.remove()
    logger.add(sys.stdout)


def test_main():
    logger.info("Starting")

    def _test_patcher(record):
        record["message"] = record["message"] + " (from patcher)"

    logger.configure(patcher=_test_patcher)

    start_log_listener(_configure_sink_logger)

    # funcs = [delayed(enq_logs(worker_func))(x) for x in range(10)]
    # funcs = [delayed(worker_func_w_logger)(x, logger) for x in range(10)]
    # funcs = [delayed(pass_logger(worker_func, logger))(x) for x in range(10)]
    funcs = [delayed(propagate_logger(worker_func))(x) for x in range(10)]
    # funcs = [delayed(pass_logger(worker_func))(x, logger=logger) for x in range(10)]
    # funcs = [delayed(nonlocal_kwargs(worker_func, logger=logger))(x) for x in range(10)]
    Parallel(n_jobs=4)(funcs)

    # listener.stop()
    logger.info("Finished")
