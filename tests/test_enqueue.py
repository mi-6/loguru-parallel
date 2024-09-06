import importlib
import multiprocessing as mp

import pytest
from joblib import Parallel, delayed

from loguru_parallel.enqueue import (
    enqueue_logger,
    get_global_log_queue,
    create_log_queue,
    logger_is_enqueued,
)


def worker_func(queue, x):
    queue.put(x)
    x = queue.get()


@pytest.mark.parametrize("backend", ["loky", "threading", "multiprocessing"])
def test_joblib_backends(backend):
    _queue = get_global_log_queue()
    funcs = [delayed(worker_func)(_queue, x) for x in range(4)]
    Parallel(n_jobs=4, backend=backend)(funcs)


def test_mp_process():
    queue = get_global_log_queue()
    p = mp.Process(target=worker_func, args=(queue, 1))
    p.start()
    p.join()


def test_mp_pool():
    queue = get_global_log_queue()
    with mp.Pool(2) as pool:
        pool.starmap(worker_func, [(queue, x) for x in range(4)])


@pytest.fixture
def logger():
    import loguru

    importlib.reload(loguru)
    from loguru import logger

    yield logger
    del logger


def test_is_enqueued_true(logger):
    queue = create_log_queue()
    enqueue_logger(logger, queue)
    assert logger_is_enqueued(logger)


def test_enqueue_without_sink(logger):
    logger.remove()
    queue = create_log_queue()
    enqueue_logger(logger, queue)
    assert logger_is_enqueued(logger)


def test_is_enqueued_false(logger):
    assert not logger_is_enqueued(logger)
