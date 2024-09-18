import sys
import time

from joblib import Parallel, delayed
from loguru import logger
from worker_func import worker_func

from loguru_parallel import (
    loguru_enqueue_and_listen,
    propagate_logger,
)

if __name__ == "__main__":
    listener = loguru_enqueue_and_listen(handlers=[dict(sink=sys.stderr)])
    logger.info("Starting")

    worker_func = propagate_logger(worker_func, logger)
    funcs = [delayed(worker_func)(x) for x in range(3)]

    logger.configure(
        patcher=lambda record: record.update(
            {"message": record["message"] + " (from Loky)"}
        )
    )
    Parallel(n_jobs=4, backend="loky")(funcs)

    logger.configure(
        patcher=lambda record: record.update(
            {"message": record["message"] + " (from Multiprocessing)"}
        )
    )
    Parallel(n_jobs=4, backend="multiprocessing")(funcs)

    logger.configure(
        patcher=lambda record: record.update(
            {"message": record["message"] + " (from Threading)"}
        )
    )
    Parallel(n_jobs=4, backend="threading")(funcs)

    # Change logging configuration
    time.sleep(0.5)
    listener.sink_logger.remove()
    listener.sink_logger.add(sys.stdout, serialize=True)
    logger.configure(extra={"extra_key": "extra_value"})

    logger.configure(
        patcher=lambda record: record.update(
            {"message": record["message"] + " (from Sequential)"}
        )
    )
    Parallel(n_jobs=4, backend="sequential")(funcs)

    logger.configure(patcher=lambda record: record)
    logger.info("Finished")
