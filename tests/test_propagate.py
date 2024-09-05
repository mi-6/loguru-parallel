import multiprocessing as mp
import queue
import sys

import pytest
from joblib import Parallel
from loguru import logger

from loguru_parallel import delayed_with_logger, propagate_logger
from loguru_parallel.enqueue import enqueue_logger, get_global_log_queue


def worker_func(x):
    logger.info(f"Hello {x}")


def _read_queued_logs() -> list[str]:
    _queue = get_global_log_queue()
    logs = []
    while True:
        try:
            log = _queue.get(timeout=0.01)
            logs.append(log)
        except queue.Empty:
            break
    return logs


@pytest.mark.parametrize("backend", ["loky", "threading", "multiprocessing"])
def test_propagate_logger_joblib(backend):
    enqueue_logger(logger)
    n = 3
    funcs = [delayed_with_logger(worker_func, logger)(x) for x in range(n)]
    Parallel(n_jobs=2, backend=backend)(funcs)

    logs = _read_queued_logs()
    assert len(logs) == n
    for x in range(n):
        assert any(f"Hello {x}" in log for log in logs)


def test_propagate_mp_pool():
    enqueue_logger(logger)
    n = 3
    with mp.Pool(2) as pool:
        pool.starmap(propagate_logger(worker_func, logger), [(x,) for x in range(n)])

    logs = _read_queued_logs()
    assert len(logs) == n
    for x in range(n):
        assert any(f"Hello {x}" in log for log in logs)


def test_propagate_mp_process():
    enqueue_logger(logger)
    p = mp.Process(target=propagate_logger(worker_func, logger), args=(0,))
    p.start()
    p.join()

    logs = _read_queued_logs()
    assert len(logs) == 1
    assert "Hello 0" in logs[0]


@pytest.mark.parametrize("backend", ["threading", "multiprocessing"])
def test_propagate_logger_not_enqueued(backend):
    logger.add(sys.stderr)
    n = 3
    funcs = [delayed_with_logger(worker_func, logger)(x) for x in range(n)]
    Parallel(n_jobs=2, backend=backend)(funcs)

    logs = _read_queued_logs()
    assert any("Skipping propagation" in log for log in logs)
