import arcade
from mazegenerator import MazeGenerator
from .load_config import ParseConfig
from .pacman import Pacman, Parser
def main():
    parse = ParseConfig()
    pacman = Pacman(Parser(parse.valid_data))
    pacman.run()


if __name__ == "__main__":
    main()
