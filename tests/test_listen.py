import json
import sys
import tempfile
import time
from pathlib import Path

import pytest
from loguru import logger

from loguru_parallel import loguru_enqueue_and_listen
from loguru_parallel.enqueue import logger_is_enqueued


def test_no_sink(capfd):
    listener = loguru_enqueue_and_listen(handlers=[])
    assert logger_is_enqueued(logger)
    logger.info("Hello, world")
    captured = capfd.readouterr()
    assert "Hello, world" not in captured.out
    assert "Hello, world" not in captured.err
    listener.stop()


def test_stdout_sink(capfd):
    listener = loguru_enqueue_and_listen(handlers=[dict(sink=sys.stdout)])
    assert logger_is_enqueued(logger)
    logger.info("Hello, world")
    listener.stop()
    captured = capfd.readouterr()
    assert "Hello, world" in captured.out


def test_stderr_sink(capfd):
    listener = loguru_enqueue_and_listen(handlers=[dict(sink=sys.stderr)])
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


def test_file_sink(tmp_log_file):
    listener = loguru_enqueue_and_listen(handlers=[dict(sink=str(_tmp_log_file))])
    assert logger_is_enqueued(logger)
    logger.info("Hello, world")
    listener.stop()
    contents = tmp_log_file.read_text()
    assert "Hello, world" in contents


def test_two_sinks(capfd, tmp_log_file_two_sinks):
    listener = loguru_enqueue_and_listen(
        handlers=[dict(sink=sys.stdout), dict(sink=str(_tmp_log_file_two_sinks))]
    )
    assert logger_is_enqueued(logger)
    logger.info("Hello, world")
    listener.stop()
    captured = capfd.readouterr()
    assert "Hello, world" in captured.out
    assert "Hello, world" not in captured.err
    contents = tmp_log_file_two_sinks.read_text()
    assert "Hello, world" in contents


def test_stop():
    listener = loguru_enqueue_and_listen(handlers=[])
    assert logger_is_enqueued(logger)
    listener.stop()
    assert listener._thread is None


def test_serialized_sink(capfd):
    listener = loguru_enqueue_and_listen(
        handlers=[dict(sink=sys.stderr, serialize=True)]
    )
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


def test_add_handler(capfd):
    listener = loguru_enqueue_and_listen(handlers=[])
    logger.info("No handler, so this should not be emitted.")
    time.sleep(0.1)
    captured = capfd.readouterr()
    assert captured.out == "" and captured.err == ""
    listener.sink_logger.add(sys.stderr)
    logger.info("Hello, world")
    time.sleep(0.1)
    captured = capfd.readouterr()
    assert "Hello, world" in captured.err
    listener.sink_logger.remove()
    listener.sink_logger.add(sys.stdout, serialize=True)
    logger.info("Hello, world")
    time.sleep(0.1)
    captured = capfd.readouterr()
    record = json.loads(captured.out)
    assert record["record"]["message"] == "Hello, world"
    assert captured.err == ""
    listener.stop()


def test_extra_data(capfd):
    logger.configure(extra={"extra_key": "extra_value"})
    listener = loguru_enqueue_and_listen(
        handlers=[dict(sink=sys.stderr, serialize=True)]
    )
    assert logger_is_enqueued(logger)
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
    listener = loguru_enqueue_and_listen(
        handlers=[dict(sink=sys.stderr, serialize=True)]
    )
    logger.info("Hello, world")
    listener.stop()
    captured = capfd.readouterr()
    records = [json.loads(line) for line in captured.err.splitlines()]
    assert len(records) == 1
    assert records[0]["record"]["message"] == "patched"


def test_log_levels(capfd):
    listener = loguru_enqueue_and_listen(
        handlers=[dict(sink=sys.stderr, serialize=True)]
    )
    levels = ["DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"]
    for level in levels:
        log_method = getattr(logger, level.lower())
        log_method(level)
    listener.stop()
    captured = capfd.readouterr()
    records = [json.loads(line) for line in captured.err.splitlines()]
    assert len(records) == 6
    for record, level in zip(records, levels):
        assert record["record"]["level"]["name"] == level
        assert record["record"]["message"] == level
