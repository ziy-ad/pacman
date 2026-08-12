import arcade
from .load_config import ParseConfig
from .pacman import Pacman
from .main_menu import MainMenu
def main():
    parse = ParseConfig()
    window = arcade.Window(fullscreen=True)
    pacman = Pacman(parse.valid_data)
    window.show_view(MainMenu(window, pacman))
    window.run()


if __name__ == "__main__":
    main()
