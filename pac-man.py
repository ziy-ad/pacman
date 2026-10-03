"""Entry point of the Pac-Man game."""

import arcade
from src import ParseConfig, Pacman, MainMenu


def main() -> None:
    """Create the window and start the game."""
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
