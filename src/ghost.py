from enum import Enum
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .pacman import Pacman
class GhostType(Enum):
    Blinky = "red"
    Pinky = "pink"
    Inky = "cyan"
    Clyde = "orange"

class Ghost:
    def __init__(self, type: GhostType, game: "Pacman") -> None:
        self.type = type
        self.position = None
        self.current_cell = (0, 0)
        self.target_cell = (0, 0)
        self.game = game

    def set_up(self):
        d = self.game.parser.levels[self.game.level_index]
        match self.type:
            case GhostType.Blinky:
                self.position = self.game.cell_positions[0][d["width"] - 1]
            case GhostType.Inky:
                self.position = self.game.cell_positions[d["height"] - 1][d["width"] - 1]
            case GhostType.Pinky:
                self.position = self.game.cell_positions[0][0]
            case GhostType.Clyde:
                self.position = self.game.cell_positions[d["height"] - 1][0]
        

        
    
