# loguru-parallel

## Usage

```py
from loguru_parallel import loguru_enqueue_and_listen

def config_sink() -> None:
    logger.remove()
    logger.add(sys.stderr, serialize=True)

def worker_func(x):
    logger.info(f"Hello {x}")

if __name__ == "__main__":
    # Configure loguru to log to a queue and start a listener that writes
    # logs to the sink configured in `config_sink`.
    loguru_enqueue_and_listen(config_sink)

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

