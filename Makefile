format:
	@poetry run ruff format .
	@poetry run ruff check . --fix

mypy:
	@poetry run mypy .

ruff-check:
	@poetry run ruff format --check .
	@poetry run ruff check .

code-assessment: version-check ruff-check mypy