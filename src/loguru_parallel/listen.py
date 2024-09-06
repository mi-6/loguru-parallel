import atexit
from logging.handlers import QueueListener
from multiprocessing import Process
from queue import Queue
from typing import Callable

from loguru import logger

from loguru_parallel.enqueue import create_log_queue, enqueue_logger


class LoguruQueueListener(QueueListener):
    def __init__(self, queue: Queue, configure_sink: Callable[[], None]):
        self.queue = queue
        self._process = None
        self._configure_sink = configure_sink

    def handle(self, record):
        """Logs a record from the queue."""
        record = record.record
        level, message = record["level"].name, record["message"]
        logger.patch(lambda r: r.update(record)).log(level, message)

    def start(self) -> None:
        """Start the listener.

        This starts up a background process to monitor the queue for records to process.
        """
        self._process = p = Process(target=self._monitor)
        p.daemon = True
        p.start()

    def stop(self) -> None:
        """Stop the listener.

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
        """Monitor the queue for records, and ask the handler to deal with them."""
        self._configure_sink()
        super()._monitor()
        logger.complete()
        print("Loguru Listener stopped.")


def loguru_enqueue_and_listen(
    logger,
    configure_sink: Callable[[], None],
) -> LoguruQueueListener:
    queue = create_log_queue()
    enqueue_logger(logger, queue)
    listener = LoguruQueueListener(queue, configure_sink)
    listener.start()
    atexit.register(listener.stop)
    return listener
