import functools
import warnings

from joblib import wrap_non_picklable_objects

from loguru_parallel.enqueue import logger_is_enqueued


def propagate_logger(func, parent_logger):
    """Wrapper for multiprocesssing target functions to propagate the parent logger.

    Propagation is achieved by setting the child process logger's core to the parent logger's core.
    Usecase: when a logger is enqueued, the child process logger should also be enqueued. Propagation
    is skipped if the parent logger is not enqueued.
    """

    if not logger_is_enqueued(parent_logger):
        warnings.warn("Logger not enqueued. Skipping propagation.")
        return func

    def wrapped_func(*args, **kwargs):
        from loguru import logger as child_logger

        child_logger._core = parent_logger._core
        return func(*args, **kwargs)

    wrapped_func = wrap_non_picklable_objects(wrapped_func, keep_wrapper=False)
    try:
        wrapped_func = functools.wraps(func)(wrapped_func)
    except AttributeError:
        " functools.wraps fails on some callable objects "
    return wrapped_func
