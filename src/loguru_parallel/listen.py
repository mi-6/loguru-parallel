import atexit
from copy import deepcopy
from logging.handlers import QueueListener
from queue import Queue
from typing import Any

from loguru import logger
from loguru._logger import Core

from loguru_parallel.enqueue import create_log_queue, enqueue_logger


def get_unconfigured_logger_instance():
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

    def _monitor(self) -> None:
        """Monitor the queue for records, and ask the handler to deal with them."""
        super()._monitor()
        self._sink_logger.complete()
        print("Loguru Listener stopped.")


def loguru_enqueue_and_listen(handlers: list[dict[str, Any]]) -> LoguruQueueListener:
    queue = create_log_queue()
    listener = LoguruQueueListener(handlers, queue)
    enqueue_logger(queue)
    listener.start()
    atexit.register(listener.stop)
    return listener
