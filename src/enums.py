from enum import IntFlag, Enum

class directions(IntFlag):
    UP = 1
    RIGHT = 2
    DOWN = 4
    LEFT = 8


class moves(Enum):
    UP = (directions.UP,    0, -1)
    RIGHT = (directions.RIGHT, 1,  0)
    DOWN = (directions.DOWN,  0,  1)
    LEFT = (directions.LEFT, -1,  0)

class Ghost_modes(Enum):
    Fight_mode = 1
    Chase_mode = 2
