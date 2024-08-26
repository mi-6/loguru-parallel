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


# class QueueSink:
#     def __init__(self):
#         self._queue = get_global_log_queue()

#     def __call__(self, record):
#         self._queue.put(record)


def enqueue_logger() -> None:
    _queue = get_global_log_queue()
    logger.remove()
    logger.add(lambda record: _queue.put(record))
    logger._enqueued = True


def logger_is_enqueued() -> bool:
    handlers = logger._core.handlers
    if len(handlers) == 0 or len(handlers) > 1:
        return False

    return getattr(logger, "_enqueued", False)
