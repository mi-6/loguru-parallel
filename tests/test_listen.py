import json
import sys
import tempfile
from pathlib import Path

import pytest
from loguru import logger

from loguru_parallel import loguru_enqueue_and_listen
from loguru_parallel.enqueue import logger_is_enqueued, create_log_queue


def _configure_no_sink() -> None:
    from loguru import logger

    logger.remove()


def test_no_sink(capfd):
    queue = create_log_queue()
    listener = loguru_enqueue_and_listen(_configure_no_sink, queue)
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
    queue = create_log_queue()
    listener = loguru_enqueue_and_listen(_configure_stdout_sink, queue)
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
    queue = create_log_queue()
    listener = loguru_enqueue_and_listen(_configure_stderr_sink, queue)
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
    queue = create_log_queue()
    listener = loguru_enqueue_and_listen(_configure_file_sink, queue)
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
    queue = create_log_queue()
    listener = loguru_enqueue_and_listen(_configure_two_sinks, queue)
    assert logger_is_enqueued(logger)
    logger.info("Hello, world")
    listener.stop()
    captured = capfd.readouterr()
    assert "Hello, world" in captured.out
    assert "Hello, world" not in captured.err
    contents = tmp_log_file_two_sinks.read_text()
    assert "Hello, world" in contents


def test_stop():
    queue = create_log_queue()
    listener = loguru_enqueue_and_listen(_configure_no_sink, queue)
    assert logger_is_enqueued(logger)
    listener.stop()
    assert listener._process is None


def _config_serialized_sink_logger() -> None:
    from loguru import logger

    logger.remove()
    logger.add(sys.stderr, serialize=True)


def test_serialized_sink(capfd):
    queue = create_log_queue()
    listener = loguru_enqueue_and_listen(_config_serialized_sink_logger, queue)
    assert logger_is_enqueued(logger)
    logger.info("Hello, world")
    logger.debug("Hello, debug")
    listener.stop()
    captured = capfd.readouterr()

    records = [json.loads(line) for line in captured.err.splitlines()]
    assert len(records) == 2
    assert "Hello, world" in records[0]["record"]["message"]
    assert "Hello, world" in records[0]["text"]
    assert "Hello, debug" in records[1]["record"]["message"]
    assert "Hello, debug" in records[1]["text"]


def test_extra_data(capfd):
    logger.configure(extra={"extra_key": "extra_value"})
    queue = create_log_queue()
    listener = loguru_enqueue_and_listen(_config_serialized_sink_logger, queue)
    assert logger_is_enqueued(logger)
    # logger.info("Hello, world", extra={"extra_key": "extra_value"})
    logger.info("Hello, world")
    logger.info("Hello, world", extra_key2="extra_value2")
    listener.stop()
    captured = capfd.readouterr()
    records = [json.loads(line) for line in captured.err.splitlines()]
    assert len(records) == 2
    assert "Hello, world" in records[0]["record"]["message"]
    assert records[0]["record"]["extra"]["extra_key"] == "extra_value"
    assert records[0]["record"]["function"] == "test_extra_data"
    assert "Hello, world" in records[1]["record"]["message"]
    assert records[1]["record"]["extra"]["extra_key2"] == "extra_value2"
    assert records[1]["record"]["function"] == "test_extra_data"


@pytest.fixture()
def logger_patcher():
    logger.configure(patcher=lambda record: record.update(message="patched"))
    yield
    logger.configure(patcher=lambda record: record)


def test_patcher(capfd, logger_patcher):
    queue = create_log_queue()
    listener = loguru_enqueue_and_listen(_config_serialized_sink_logger, queue)
    logger.info("Hello, world")
    listener.stop()
    captured = capfd.readouterr()
    records = [json.loads(line) for line in captured.err.splitlines()]
    assert len(records) == 1
    assert records[0]["record"]["message"] == "patched"
