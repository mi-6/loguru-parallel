from loguru import logger as parent_logger
import functools


def inherit_logger(func):
    def wrapped_func(*args, **kwargs):
        from loguru import logger as child_logger

        child_logger._core = parent_logger._core
        return func(*args, **kwargs)

    try:
        wrapped_func = functools.wraps(func)(wrapped_func)
    except AttributeError:
        " functools.wraps fails on some callable objects "
    return wrapped_func
