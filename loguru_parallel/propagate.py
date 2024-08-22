from loguru import logger
from loguru_parallel.log_queue import logger_is_enqueued
import functools


def propagate_logger(func):
    if not logger_is_enqueued():
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
