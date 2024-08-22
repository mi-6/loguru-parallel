from multiprocessing import Manager
from queue import Queue
from loguru import logger

_queue = None


def get_global_log_queue() -> Queue:
    global _queue
    if _queue is None:
        m = Manager()
        _queue = m.Queue()
    return _queue


def enqueue_logger() -> None:
    queue = get_global_log_queue()
    logger.remove()
    logger.add(lambda record: queue.put(record))
