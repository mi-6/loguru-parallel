from loguru_parallel.log_queue import get_global_log_queue
from joblib import Parallel, delayed
import pytest
import multiprocessing as mp


def worker_func(queue, x):
    queue.put(x)
    x = queue.get()


@pytest.mark.parametrize(
    "backend", ["loky", "threading"]
)  # NOTE pickling fails for multiprocessing backend
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
    with mp.Pool(4) as pool:
        pool.starmap(worker_func, [(queue, x) for x in range(4)])
