from enum import IntFlag
from rich import print
import arcade
from mazegenerator import MazeGenerator
from rich.traceback import install
from abc import ABC, abstractmethod

install()


class Ghost(ABC):
    def __init__(self, coordinates):
        self.coordinates: tuple[int, int] = coordinates


    @abstractmethod
    def get_path(self):
        ...




class BlueGhost(Ghost):
    def __init__(self, coordinates):
        super().__init__(coordinates)
        self.sprite = arcade.Sprite("src/assets/blue_ghost.png", scale=0.1)


    def get_path(self):
        ...


class PinkGhost(Ghost):
    def __init__(self, coordinates):
        super().__init__(coordinates)
        self.sprite = arcade.Sprite("src/assets/pink_ghost.png", scale=0.1)

    def get_path(self):
        ...


class RedGhost(Ghost):
    def __init__(self, coordinates):
        super().__init__(coordinates)
        self.sprite = arcade.Sprite("src/assets/red_ghost.png", scale=0.1)

    def get_path(self):
        ...


class OrangeGhost(Ghost):
    def __init__(self, coordinates):
        super().__init__(coordinates)
        self.sprite = arcade.Sprite("src/assets/orange_ghost.png", scale=0.1)

    def get_path(self):
        ...