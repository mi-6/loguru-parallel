uv:
	curl -LsSf https://astral.sh/uv/install.sh | sh

format:
	@uv run ruff format .
	@uv run ruff check . --fix

lint:
	@uv run ruff format --check .
	@uv run ruff check .

test:
	@uv run pytest
