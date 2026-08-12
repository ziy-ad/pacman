import arcade
from .load_config import ParseConfig
from .pacman import Pacman
def main():
    parse = ParseConfig()
    window = arcade.Window(fullscreen=True)
    pacman = Pacman(parse.valid_data)
    window.show_view(pacman)
    window.run()


if __name__ == "__main__":
    main()
