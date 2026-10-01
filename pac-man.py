import arcade
from src.load_config import ParseConfig
from src.pacman import Pacman
from src.main_menu import MainMenu
def main():
    parse = ParseConfig()
    window = arcade.Window(fullscreen=True, vsync=False)
    pacman = Pacman(parse.valid_data)
    window.show_view(MainMenu(window, pacman))
    window.run()


if __name__ == "__main__":
    main()
