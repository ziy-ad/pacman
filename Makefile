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

package:
	uv sync
	rm -rf build dist
	uv run pyinstaller --noconfirm --onedir --name pacman \
	--hidden-import mazegenerator \
	--add-data "src/assets:src/assets" pac-man.py
	rm -rf dist/pacman/_internal/arcade/VERSION
	cp "$$(uv run python -c 'import arcade,os;print(os.path.join(os.path.dirname(arcade.__file__),"VERSION"))')" dist/pacman/_internal/arcade/VERSION
