from multiprocessing import Manager
# from queue import Queue
# from loguru import logger

_queue = None


def get_global_log_queue():
    global _queue
    if _queue is None:
        m = Manager()
        _queue = m.Queue()
    return _queue


def enqueue_logger() -> None:
    from loguru import logger

    queue = get_global_log_queue()
    logger.remove()
    logger.add(lambda record: queue.put(record))
