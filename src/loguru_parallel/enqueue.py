from multiprocessing import Manager
from queue import Queue

from loguru import logger

_manager = None


def create_log_queue() -> Queue:
    global _manager
    if not _manager:
        _manager = Manager()
    return _manager.Queue()


def enqueue_logger(queue: Queue) -> None:
    """Configure the loguru.logger instance to send logs to a queue.

    This means that all handlers are deleted and replaced with a single handler that
    enqueues records log queue passed to this function.
    """
    logger.remove()

    def queue_sink(record):
        queue.put(record)

    logger.add(queue_sink)
    handler = list(logger._core.handlers.values())[0]
    handler._loguru_parallel_enqueued = True


def logger_is_enqueued(logger) -> bool:
    """Check whether all handlers of the logger are enqueued.

    Args:
        logger: The loguru logger instance to check.

    Returns:
        True if all handlers are enqueued, False otherwise.
    """
    handlers = logger._core.handlers
    if len(handlers) != 1:
        return False
    handler = list(handlers.values())[0]
    return getattr(handler, "_loguru_parallel_enqueued", False)
