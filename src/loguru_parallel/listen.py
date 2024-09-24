import atexit
from copy import deepcopy
from logging.handlers import QueueListener
from queue import Queue
from typing import Any

from loguru import logger
from loguru._logger import Core

from loguru_parallel.enqueue import create_log_queue, enqueue_logger


def get_unconfigured_logger_instance():
    # Temporarily reset _core, to avoid trying to deepcopy non-picklable objects
    current_core = logger._core
    logger._core = Core()
    new_logger = deepcopy(logger)
    logger._core = current_core
    new_logger.remove()
    atexit.register(new_logger.remove)
    return new_logger


_unconfigured_logger = get_unconfigured_logger_instance()


class LoguruQueueListener(QueueListener):
    def __init__(self, handlers: list[dict[str, Any]], queue: Queue):
        self.queue = queue
        self._thread = None

        sink_logger = deepcopy(_unconfigured_logger)
        sink_logger.configure(handlers=handlers)

        assert sink_logger is not logger
        atexit.register(sink_logger.remove)
        self._sink_logger = sink_logger

    @property
    def sink_logger(self):
        """Public access to the logger instance that logs to the sink."""
        return self._sink_logger

    def handle(self, record):
        """Logs a record from the queue."""
        record = record.record
        level, message = record["level"].name, record["message"]
        self._sink_logger.patch(lambda r: r.update(record)).log(level, message)

    def stop(self) -> None:
        """Stop the listener.

        This asks the thread to terminate, and then waits for it to do so.
        Note that if you don't call this before your application exits, there
        may be some records still left on the queue, which won't be processed.
        """
        if self._thread is None:
            return
        super().stop()
        self._sink_logger.complete()
        print("Loguru Listener stopped.")


def loguru_enqueue_and_listen(handlers: list[dict[str, Any]]) -> LoguruQueueListener:
    """Enqueue the logger and start a listener thread to process the log records.

    The listener emits log records to via the handlers passed to this function.

    Args:
        handlers: List of handlers to process log records. The handlers are passed to
            loguru's `logger.configure` method.

    Returns:
        The listener instance.

    Example:
    >>> loguru_enqueue_and_listen(
    ...     handlers=[
    ...         dict(sink=sys.stderr, format="[{time}] {message}"),
    ...         dict(sink="file.log", enqueue=True, serialize=True),
    ...     ]
    ... )
    """
    queue = create_log_queue()
    listener = LoguruQueueListener(handlers, queue)
    enqueue_logger(queue)
    listener.start()
    atexit.register(listener.stop)
    return listener
