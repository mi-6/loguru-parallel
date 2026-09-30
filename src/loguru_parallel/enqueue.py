import pickle
from multiprocessing import Manager
from queue import Queue

from loguru import logger

_manager = None


class UnpicklableException(Exception):
    """Stands in for an exception whose class pickle cannot look up by name."""


def create_log_queue() -> Queue:
    global _manager
    if not _manager:
        _manager = Manager()
    return _manager.Queue()


def enqueue_logger(queue: Queue) -> None:
    """Configure the loguru.logger instance to send logs to a queue.

    This means that all handlers are removed and replaced with a single handler
    that enqueues records to the queue.
    """
    logger.remove()

    def queue_sink(message):
        _make_exception_picklable(message.record)
        queue.put(message)

    logger.add(queue_sink)
    handler = list(logger._core.handlers.values())[0]
    handler._loguru_parallel_enqueued = True


def _make_exception_picklable(record) -> None:
    # Loguru drops an unpicklable exception value when pickling a record, but
    # still pickles its class, which fails for classes created at runtime
    # (botocore's ClientError subclasses): the whole record is then lost.
    exception = record["exception"]
    if exception is None:
        return
    try:
        pickle.dumps(exception.type)
    except Exception:
        name = f"{exception.type.__module__}.{exception.type.__qualname__}"
        record["exception"] = exception._replace(
            type=UnpicklableException,
            value=UnpicklableException(f"{name}: {exception.value}"),
        )


def logger_is_enqueued(logger) -> bool:
    """Check whether the logger is enqueued.

    Args:
        logger: The loguru logger instance to check.

    Returns:
        True if the logger has a single enqueued handler, False otherwise.
    """
    handlers = logger._core.handlers
    if len(handlers) != 1:
        return False
    handler = list(handlers.values())[0]
    return getattr(handler, "_loguru_parallel_enqueued", False)
