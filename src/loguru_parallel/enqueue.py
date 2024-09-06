from multiprocessing import Manager
from queue import Queue

from loguru._simple_sinks import CallableSink

_manager = None


def create_log_queue() -> Queue:
    global _manager
    if not _manager:
        _manager = Manager()
    return _manager.Queue()


def enqueue_logger(logger, queue: Queue) -> None:
    """Configure the current process's logger to enqueue records.

    This means that all handlers will be removed and replaced with a single handler that
    enqueues records to the global log queue.

    Args:
        logger: The loguru logger instance to enqueue
    """
    _queue = queue
    if not logger._core.handlers:
        logger.add(lambda dummy: dummy)
    handlers = logger._core.handlers
    for handler in handlers.values():
        state = handler.__getstate__()
        sink = CallableSink(lambda record: _queue.put(record))
        sink._enqueued = True
        state["_sink"] = sink
        state["_name"] = getattr(sink, "__name__", None) or repr(sink)
        handler.__setstate__(state)


def logger_is_enqueued(logger) -> bool:
    """Check whether all handlers of the logger are enqueued.

    Args:
        logger: The loguru logger instance to check.

    Returns:
        True if all handlers are enqueued, False otherwise.
    """
    handlers = logger._core.handlers
    if not handlers:
        return False

    for handler in handlers.values():
        state = handler.__getstate__()
        if not getattr(state["_sink"], "_enqueued", False):
            return False
    return True
