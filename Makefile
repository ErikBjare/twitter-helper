build:
	poetry install

test:
	poetry run pytest

typecheck:
	poetry run mypy --ignore-missing-imports twitter_helper
