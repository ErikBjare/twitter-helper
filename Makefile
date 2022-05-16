build:
	poetry install

test:
	poetry run pytest

typecheck:
	poetry run mypy twitter_helper
