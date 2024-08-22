from logging.handlers import QueueListener
from loguru import logger
from multiprocessing import Process
from typing import Callable
from loguru_parallel.log_queue import get_global_log_queue, enqueue_logger
import atexit


class _LoguruQueueListener(QueueListener):
    def __init__(self, queue, configure_logger: Callable[[], None]):
        self.queue = queue
        self._process = None
        self._configure_logger = configure_logger

    def handle(self, record):
        record = record.record
        level, message = record["level"].name, record["message"]
        record["message"] = message + " (from LoguruQueueListener)"
        logger.patch(lambda r: r.update(record)).log(level, message)

    def start(self) -> None:
        """
        Start the listener.

        This starts up a background thread to monitor the queue for
        LogRecords to process.
        """
        self._process = p = Process(target=self._monitor)
        p.daemon = True
        p.start()

    def stop(self) -> None:
        """
        Stop the listener.

        This asks the thread to terminate, and then waits for it to do so.
        Note that if you don't call this before your application exits, there
        may be some records still left on the queue, which won't be processed.
        """
        if self._process is None:
            return
        self.enqueue_sentinel()
        self._process.join()
        self._process = None

    def _monitor(self) -> None:
        self._configure_logger()
        super()._monitor()
        logger.complete()
        print("Listener stopped")


def start_log_listener(configure_logger: Callable[[], None]) -> _LoguruQueueListener:
    queue = get_global_log_queue()
    listener = _LoguruQueueListener(queue, configure_logger)
    listener.start()
    atexit.register(listener.stop)
    enqueue_logger()
    return listener
