from loguru import logger



def _sub_func():
    logger.info("Hi from subfunc")


def worker_func(x):
    def _test_patcher(record):
        record["message"] = record["message"] + " (from worker patcher)"

    # logger.configure(patcher=_test_patcher)
    # logger.info(f"Processing {x}")
    logger.patch(_test_patcher).info(f"Processing {x}")
    _sub_func()
