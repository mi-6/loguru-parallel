# from loguru import logger as parent_logger
# import functools


# def propagate_logger(func):
#     def wrapped_func(*args, **kwargs):
#         from loguru import logger as child_logger

#         child_logger._core = parent_logger._core
#         return func(*args, **kwargs)

#     try:
#         wrapped_func = functools.wraps(func)(wrapped_func)
#     except AttributeError:
#         " functools.wraps fails on some callable objects "
#     return wrapped_func


from loguru_parallel.propagate import propagate_logger
from loguru_parallel.log_queue import enqueue_logger, get_global_log_queue
from loguru import logger
from joblib import delayed, Parallel
import queue
import pytest


def worker_func(x):
    logger.info(f"Hello {x}")


@pytest.mark.parametrize("backend", ["loky", "threading"])
def test_propagate_logger_joblib(backend):
    enqueue_logger()
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
