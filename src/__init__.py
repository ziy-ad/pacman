"""Pac-Man game package."""

from .load_config import ParseConfig
from .pacman import Pacman
from .main_menu import MainMenu

__all__ = ["ParseConfig", "Pacman", "MainMenu"]
