import multiprocessing as mp
import queue
import sys

import pytest
from joblib import Parallel
from loguru import logger

from loguru_parallel import delayed_with_logger, propagate_logger
from loguru_parallel.enqueue import create_log_queue, enqueue_logger


def worker_func(x):
    logger.info(f"Hello {x}")


def _read_queued_logs(_queue: queue.Queue) -> list[str]:
    logs = []
    while True:
        try:
            log = _queue.get(timeout=0.01)
            logs.append(log)
        except queue.Empty:
            break
    return logs


@pytest.mark.parametrize(
    "backend", ["loky", "threading", "multiprocessing", "sequential"]
)
def test_propagate_logger_joblib(backend):
    _queue = create_log_queue()
    enqueue_logger(_queue)
    n = 3
    funcs = [delayed_with_logger(worker_func, logger)(x) for x in range(n)]
    Parallel(n_jobs=2, backend=backend)(funcs)

    logs = _read_queued_logs(_queue)
    assert len(logs) == n
    for x in range(n):
        assert any(f"Hello {x}" in log for log in logs)


def test_propagate_mp_pool():
    _queue = create_log_queue()
    enqueue_logger(_queue)
    n = 3
    with mp.Pool(2) as pool:
        pool.starmap(propagate_logger(worker_func, logger), [(x,) for x in range(n)])

    logs = _read_queued_logs(_queue)
    assert len(logs) == n
    for x in range(n):
        assert any(f"Hello {x}" in log for log in logs)


def test_propagate_mp_process():
    _queue = create_log_queue()
    enqueue_logger(_queue)
    p = mp.Process(target=propagate_logger(worker_func, logger), args=(0,))
    p.start()
    p.join()

    logs = _read_queued_logs(_queue)
    assert len(logs) == 1
    assert "Hello 0" in logs[0]


@pytest.mark.parametrize(
    "backend", ["threading", "multiprocessing", "loky", "sequential"]
)
def test_propagate_logger_not_enqueued(backend, capfd):
    logger.remove()
    logger.add(sys.stderr)
    n = 3
    funcs = [delayed_with_logger(worker_func, logger)(x) for x in range(n)]
    Parallel(n_jobs=2, backend=backend)(funcs)

    captured = capfd.readouterr()
    assert "Skipping propagation" in captured.err
