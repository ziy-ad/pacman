.PHONY: install run debug clean lint lint-strict

install:
	uv sync

run:
	uv run pac-man.py config.json

debug:
	python3 -m pdb main.py

clean:
	uv run -m pyclean --debris all -- .

lint:
	uv run flake8 src pac-man.py
	uv run mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
