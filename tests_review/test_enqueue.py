import multiprocessing as mp

import pytest
from joblib import Parallel, delayed
from loguru import logger

from loguru_parallel.enqueue import (
    create_log_queue,
    enqueue_logger,
    logger_is_enqueued,
)


def worker_func(queue, x):
    queue.put(x)
    x = queue.get()


@pytest.mark.parametrize(
    "backend", ["loky", "threading", "multiprocessing", "sequential"]
)
def test_joblib_backends(backend):
    _queue = create_log_queue()
    funcs = [delayed(worker_func)(_queue, x) for x in range(4)]
    Parallel(n_jobs=4, backend=backend)(funcs)


def test_mp_process():
    queue = create_log_queue()
    p = mp.Process(target=worker_func, args=(queue, 1))
    p.start()
    p.join()


def test_mp_pool():
    queue = create_log_queue()
    with mp.Pool(2) as pool:
        pool.starmap(worker_func, [(queue, x) for x in range(4)])


def test_is_enqueued_true():
    queue = create_log_queue()
    enqueue_logger(queue)
    assert logger_is_enqueued(logger)


def test_enqueue_without_sink():
    logger.remove()
    queue = create_log_queue()
    enqueue_logger(queue)
    assert logger_is_enqueued(logger)


def test_is_enqueued_false():
    logger.remove()
    assert not logger_is_enqueued(logger)
