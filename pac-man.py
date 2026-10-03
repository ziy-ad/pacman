import arcade
from src import *


def main():
    parse = ParseConfig()
    window = arcade.Window(fullscreen=True, vsync=False)
    pacman = Pacman(parse.valid_data)
    window.show_view(MainMenu(window, pacman))
    window.run()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
