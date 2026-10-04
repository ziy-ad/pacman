.PHONY: install run debug clean lint lint-strict

install:
	uv sync

run:
	uv run pac-man.py config.json

debug:
	python3 -m pdb main.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} \;
	find . -type d -name ".mypy_cache" -exec rm -rf {} \;
	find . -type d -name ".pytest_cache" -exec rm -rf {} \;
	find . -type f -name "*.pyc" -delete

lint:
	uv run flake8 src pac-man.py
	uv run mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

