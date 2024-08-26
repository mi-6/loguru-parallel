from multiprocessing import Manager
from queue import Queue

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


def enqueue_logger(logger) -> None:
    _queue = get_global_log_queue()
    logger.remove()
    handler_id = logger.add(lambda record: _queue.put(record))
    logger._core.handlers[handler_id]._enqueued = True


def logger_is_enqueued(logger) -> bool:
    handlers = logger._core.handlers
    if not handlers:
        return False

    for handler in handlers.values():
        if not getattr(handler, "_enqueued", False):
            return False
    return True
