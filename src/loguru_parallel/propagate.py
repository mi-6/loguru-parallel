import functools

from joblib import delayed, wrap_non_picklable_objects

from loguru_parallel.enqueue import logger_is_enqueued


def propagate_logger(func, parent_logger):
    """Wrapper for multiprocesssing target functions to propagate the parent logger.

    Propagation is achieved by setting the child process logger's core to the parent logger's core.
    Usecase: when a logger is enqueued, the child process logger should also be enqueued. Propagation
    is skipped if the parent logger is not enqueued.
    """

    if not logger_is_enqueued(parent_logger):
        parent_logger.debug("Logger not enqueued. Skipping propagation.")
        return func

    @wrap_non_picklable_objects
    def wrapped_func(*args, **kwargs):
        from loguru import logger as child_logger

        child_logger._core = parent_logger._core
        return func(*args, **kwargs)

    try:
        wrapped_func = functools.wraps(func)(wrapped_func)
    except AttributeError:
        " functools.wraps fails on some callable objects "
    return wrapped_func


def delayed_with_logger(func, parent_logger):
    """Extension of joblib's `delayed` wrapper, to propagate the logger to the child process."""
    return delayed(propagate_logger(func, parent_logger))
