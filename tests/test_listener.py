from loguru_parallel.listener import start_log_listener
from loguru_parallel.log_queue import get_global_log_queue
from loguru import logger
import sys
import tempfile
from pathlib import Path


def _configure_no_sink() -> None:
    from loguru import logger

    logger.remove()


def test_no_sink(capfd):
    queue = get_global_log_queue()
    start_log_listener(_configure_no_sink)
    logger.info("Hello, world")
    captured = capfd.readouterr()
    assert "Hello, world" not in captured.out
    assert "Hello, world" not in captured.err
    queue.put(None)


def _configure_stdout_sink() -> None:
    from loguru import logger

    logger.remove()
    logger.add(sys.stdout)


def test_stdout_sink(capfd):
    listener = start_log_listener(_configure_stdout_sink)
    logger.info("Hello, world")
    listener.stop()
    captured = capfd.readouterr()
    assert "Hello, world" in captured.out


def _configure_stderr_sink() -> None:
    from loguru import logger

    logger.remove()
    logger.add(sys.stderr)


def test_stderr_sink(capfd):
    listener = start_log_listener(_configure_stderr_sink)
    logger.info("Hello, world")
    listener.stop()
    captured = capfd.readouterr()
    assert "Hello, world" in captured.err


_tmp_log_file = Path(tempfile.NamedTemporaryFile().name).parent / "tmp.log"
_tmp_log_file_two_sinks = (
    Path(tempfile.NamedTemporaryFile().name).parent / "tmp_two_sinks.log"
)


def _configure_file_sink() -> None:
    from loguru import logger

    logger.remove()
    logger.add(str(_tmp_log_file))


def test_file_sink():
    listener = start_log_listener(_configure_file_sink)
    logger.info("Hello, world")
    listener.stop()
    contents = _tmp_log_file.read_text()
    assert "Hello, world" in contents
    _tmp_log_file.unlink()


def _configure_two_sinks() -> None:
    from loguru import logger

    logger.remove()
    logger.add(sys.stdout)
    logger.add(str(_tmp_log_file_two_sinks))


def test_two_sinks(capfd):
    listener = start_log_listener(_configure_two_sinks)
    logger.info("Hello, world")
    listener.stop()
    captured = capfd.readouterr()
    assert "Hello, world" in captured.out
    assert "Hello, world" not in captured.err
    contents = _tmp_log_file_two_sinks.read_text()
    assert "Hello, world" in contents
    _tmp_log_file_two_sinks.unlink()


def test_stop():
    listener = start_log_listener(_configure_no_sink)
    listener.stop()
    assert listener._process is None
