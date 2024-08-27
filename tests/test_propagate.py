import queue

import pytest
from joblib import Parallel, delayed
from loguru import logger

from loguru_parallel.log_queue import enqueue_logger, get_global_log_queue
from loguru_parallel.propagate import propagate_logger


def worker_func(x):
    logger.info(f"Hello {x}")


@pytest.mark.parametrize("backend", ["loky", "threading"])
def test_propagate_logger_joblib(backend):
    enqueue_logger(logger)
    _queue = get_global_log_queue()
    n = 3
    funcs = [delayed(propagate_logger(worker_func))(x) for x in range(n)]
    Parallel(n_jobs=2, backend=backend)(funcs)

    logs = ""
    while True:
        try:
            log = _queue.get(timeout=0.01)
            logs += log
        except queue.Empty:
            break

    print("logs", logs)
    assert all(f"Hello {x}" in logs for x in range(n))


def propagated_worker_func():
    enqueue_logger(logger)
    return propagate_logger(worker_func)
