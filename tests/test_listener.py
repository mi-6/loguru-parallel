import sys
import tempfile
from pathlib import Path

import pytest
from loguru import logger

from loguru_parallel.listener import loguru_enqueue_and_listen
from loguru_parallel.log_queue import logger_is_enqueued


def _configure_no_sink() -> None:
    from loguru import logger

    logger.remove()


def test_no_sink(capfd):
    listener = loguru_enqueue_and_listen(_configure_no_sink)
    assert logger_is_enqueued(logger)
    logger.info("Hello, world")
    captured = capfd.readouterr()
    assert "Hello, world" not in captured.out
    assert "Hello, world" not in captured.err
    listener.stop()


def _configure_stdout_sink() -> None:
    from loguru import logger

    logger.remove()
    logger.add(sys.stdout)


def test_stdout_sink(capfd):
    listener = loguru_enqueue_and_listen(_configure_stdout_sink)
    assert logger_is_enqueued(logger)
    logger.info("Hello, world")
    listener.stop()
    captured = capfd.readouterr()
    assert "Hello, world" in captured.out


def _configure_stderr_sink() -> None:
    from loguru import logger

    logger.remove()
    logger.add(sys.stderr)


def test_stderr_sink(capfd):
    listener = loguru_enqueue_and_listen(_configure_stderr_sink)
    assert logger_is_enqueued(logger)
    logger.info("Hello, world")
    listener.stop()
    captured = capfd.readouterr()
    assert "Hello, world" in captured.err


_tmp_log_file = Path(tempfile.NamedTemporaryFile().name).parent / "tmp.log"
_tmp_log_file_two_sinks = (
    Path(tempfile.NamedTemporaryFile().name).parent / "tmp_two_sinks.log"
)


@pytest.fixture()
def tmp_log_file():
    _tmp_log_file.touch()
    yield _tmp_log_file
    _tmp_log_file.unlink()


@pytest.fixture()
def tmp_log_file_two_sinks():
    _tmp_log_file_two_sinks.touch()
    yield _tmp_log_file_two_sinks
    _tmp_log_file_two_sinks.unlink()


def _configure_file_sink() -> None:
    from loguru import logger

    logger.remove()
    logger.add(str(_tmp_log_file))


def test_file_sink(tmp_log_file):
    listener = loguru_enqueue_and_listen(_configure_file_sink)
    assert logger_is_enqueued(logger)
    logger.info("Hello, world")
    listener.stop()
    contents = tmp_log_file.read_text()
    assert "Hello, world" in contents


def _configure_two_sinks() -> None:
    from loguru import logger

    logger.remove()
    logger.add(sys.stdout)
    logger.add(str(_tmp_log_file_two_sinks))


def test_two_sinks(capfd, tmp_log_file_two_sinks):
    listener = loguru_enqueue_and_listen(_configure_two_sinks)
    assert logger_is_enqueued(logger)
    logger.info("Hello, world")
    listener.stop()
    captured = capfd.readouterr()
    assert "Hello, world" in captured.out
    assert "Hello, world" not in captured.err
    contents = tmp_log_file_two_sinks.read_text()
    assert "Hello, world" in contents


def test_stop():
    listener = loguru_enqueue_and_listen(_configure_no_sink)
    assert logger_is_enqueued(logger)
    listener.stop()
    assert listener._process is None
