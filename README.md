# loguru-parallel
Makes loguru usable with parallel processing using `multiprocessing` or `joblib`.

Caution: This package most likely does not support all of loguru's features and depends on some private APIs that may break in future version.

## Usage

```py
from loguru_parallel import loguru_enqueue_and_listen

def worker_func(x):
    logger.info(f"Hello {x}")

if __name__ == "__main__":
    # Configure loguru to log to a queue and start a listener that writes
    # logs to the sinks configured in the handlers.
    loguru_enqueue_and_listen(handlers=[dict(sink=sys.stderr)])

    # Pass the enqueued logger to a parallelized function.
    funcs = [delayed_with_logger(worker_func, logger)(x) for x in range(10)]
    Parallel(n_jobs=4)(funcs)
```

## Setup dev environment

```sh
# Install uv for environment and dependency management
make uv

# Create Python environment
uv sync

# Run tests
uv run pytest

# Run example script
uv run examples/joblib_.py
```

## Dev Docker container

```sh
docker build -t loguru-parallel .
docker run -it -v $(pwd):/app loguru-parallel bash

# in container
pytest
python examples/joblib_.py
```

