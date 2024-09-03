from multiprocessing import Manager
from queue import Queue

from loguru._simple_sinks import CallableSink

_queue = None


def get_global_log_queue() -> Queue:
    global _queue
    if _queue is None:
        m = Manager()
        _queue = m.Queue()
    return _queue


def enqueue_logger(logger) -> None:
    """Configure the current process's logger to enqueue records.

    This means that all handlers will be removed and replaced with a single handler that
    enqueues records to the global log queue.
    """
    _queue = get_global_log_queue()
    handlers = logger._core.handlers
    for id, handler in handlers.items():
        state = handler.__getstate__()
        sink = CallableSink(lambda record: _queue.put(record))
        sink._enqueued = True
        state["_sink"] = sink
        state["_name"] = getattr(sink, "__name__", None) or repr(sink)
        handler.__setstate__(state)


def logger_is_enqueued(logger) -> bool:
    handlers = logger._core.handlers
    if not handlers:
        return False

    for handler in handlers.values():
        state = handler.__getstate__()
        if not getattr(state["_sink"], "_enqueued", False):
            return False
    return True
