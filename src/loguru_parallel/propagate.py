import functools

from loguru import logger

from loguru_parallel.log_queue import logger_is_enqueued


def propagate_logger(func):
    """Wrapper for multiprocesssing target functions to propagate the parent logger.

    Propagation is achieved by setting the child process logger's core to the parent logger's core.
    Usecase: when a logger is enqueued, the child process logger should also be enqueued. Propagation
    is skipped if the parent logger is not enqueued.
    """
    if not logger_is_enqueued(logger):
        logger.debug("Logger not enqueued. Skipping propagation.")
        return func

    def wrapped_func(*args, **kwargs):
        from loguru import logger as child_logger

        child_logger._core = logger._core
        return func(*args, **kwargs)

    try:
        wrapped_func = functools.wraps(func)(wrapped_func)
    except AttributeError:
        " functools.wraps fails on some callable objects "
    return wrapped_func
