uv sync
rm -rf build dist pac-man.spec
uv run pyinstaller --noconfirm --onedir --name pacman \
--add-data "src/assets:src/assets" pac-man.py
rm -rf dist/pacman/_internal/arcade/VERSION
cp "$(uv run python -c 'import arcade,os;print(os.path.join(os.path.dirname(arcade.__file__),"VERSION"))')" dist/pacman/_internal/arcade/VERSION
cp config.json dist/pacman
cd dist/ && zip -r pacman-linux.zip pacman
