AI assistance was used to help review the project structure, clarify and simplify
this README, and identify how the configuration, maze generation, scoring, and
ghost pathfinding work together. The game-specific implementation, asset choices,
Scores are stored in the JSON file selected by `highscore_filename`. At game
over, the player enters a name of one to ten letters, numbers, or spaces. The
scoreboard keeps at most the ten highest scores, sorted in descending order. If
JSON was chosen because the scoreboard is small, human-readable, and does not
need a database or a server. The configuration loader creates an empty score
file when it does not exist or does not contain a valid list.
The game uses the assigned `mazegenerator` package from
`wheels/mazegenerator-2.0.2-py3-none-any.whl`. `Pacman.maze_init()` creates a
`MazeGenerator` with the selected width, height, and seed, then calls
Python 3.11+ with Arcade for the window, rendering, sprites, textures, and
    keyboard events.
`ParseConfig` validates the command-line JSON and produces a `ConfigData`
`pac-man.py` is the entry point. It creates `ParseConfig`, constructs the
`Pacman` game view, opens an Arcade window, and displays `MainMenu`.
The main relationships are:
`enums.py` defines movement directions, movement vectors, and ghost modes.
`load_config.py` is responsible for input validation and defaults. `pacman.py`
owns the game loop and composes the other systems. `ghosts_algorithm.py`
## Resources

- [Python documentation](https://docs.python.org/3/): language and standard-library reference.
- [Arcade documentation](https://api.arcade.academy/): window, view, sprite, texture, and input APIs.
- [Python `json` documentation](https://docs.python.org/3/library/json.html): configuration and score-file handling.
- [Breadth-first search](https://en.wikipedia.org/wiki/Breadth-first_search): basis for ghost path finding on the maze grid.
- The assigned `mazegenerator` package included in `wheels/`: maze creation and wall-grid representation.

AI tools were used as a development aid for understanding requirements,
reviewing the existing module structure, suggesting documentation structure,
and checking that the README describes the implemented configuration, scoring,
maze generation, and architecture. The final implementation and project-specific
technical decisions remain part of this repository and should be reviewed by
the project author.
*This project has been created as part of the 42 curriculum by zee.*

# Pac-Man

## Description

Pac-Man is a desktop arcade game written in Python. The player navigates
procedurally generated mazes, collects pac-gums, avoids four ghosts, and tries to
complete a sequence of increasingly large levels before the timer expires.

The game includes a main menu, pause menu, highscore screen, configurable scoring,
multiple lives, fullscreen support, and an optional cheat mode for testing.

## Instructions

### Requirements


Install the dependencies, including the assigned local maze-generator package:

```bash
uv sync
```

Start the game with one configuration file argument:

```bash
uv run pac-man.py config.json
```

The equivalent Make targets are `make install` and `make run`. Use the arrow keys
or `WASD` to move, `Enter` to select menu items, `Escape` to pause, and `F` to
toggle fullscreen.

## Configuration

The configuration file is JSON. The parser also accepts comments beginning with
`#` or `//`, and block comments. Invalid or missing values use the defaults below.
The highscore file is created automatically when it does not exist.

| Key | Type | Default | Purpose |
| --- | --- | --- | --- |
| `highscore_filename` | string | `track_score.json` | JSON file used to store highscores. It must be a local `.json` filename. |
| `lives` | positive integer | `3` | Starting lives for each game. |
| `pacgum` | positive integer | `42` | Configured pac-gum count value. |
| `points_per_pacgum` | positive integer | `1` | Points for a regular pac-gum. |
| `points_per_super_pacgum` | positive integer | `50` | Points for a corner super pac-gum. |
| `points_per_ghost` | positive integer | `200` | Points for eating an edible ghost. |
| `seed` | integer | `42` | Seed for the first maze. Later levels use random seeds. |
| `level_max_time` | integer | `90` | Time limit in seconds for each level. |
| `levels` | array | 10 levels | Maze dimensions, with each width and height between 10 and 40. |

Default level sizes are `10x10`, `25x25`, `29x25`, `29x29`, `33x29`, `33x33`,
`37x33`, `37x37`, `41x37`, and `41x41` as configured by the validator. A level
outside the accepted range falls back to its default entry.

Example:

```json
{
    "highscore_filename": "track_score.json",
    "lives": 3,
    "points_per_pacgum": 1,
    "points_per_super_pacgum": 50,
    "points_per_ghost": 200,
    "seed": 42,
    "level_max_time": 90,
    "levels": [
        {"width": 10, "height": 10},
        {"width": 25, "height": 25}
    ]
}
```

## Highscore

Scores are stored as a list of player names and scores in the JSON file selected
by `highscore_filename`. Names may contain letters, numbers, and spaces and may be
up to ten characters long. Only positive scores are saved. The scoreboard keeps
the ten highest scores, sorts them in descending order, and replaces an existing
player's score only when the new score is higher.

JSON was chosen because the scoreboard is small, human-readable, and does not
need a database or network service. The filename is validated to prevent absolute
paths and parent-directory traversal.

## Maze Generation

The project uses the assigned `mazegenerator` package from
`wheels/mazegenerator-2.0.2-py3-none-any.whl`. `Pacman` creates a
`MazeGenerator` with a configured size and seed, calls `generate()`, and reads the
resulting grid and wall flags to draw the maze and determine legal movement.

The first level uses the configured seed so that it can be reproduced. Each later
level receives a new random seed. Maze cells are also used to place pac-gums,
spawn ghosts in the corners, and calculate ghost paths.

## Implementation

    highscore screen.

## General Software Architecture

`pac-man.py` is the entry point. It parses the configuration, creates the Arcade
window, constructs `Pacman`, opens `MainMenu`, and starts the event loop.

    `ConfigData`.
    timers, level progression, and rendering.
    Clyde, and Inky behaviors.

`MainMenu` and `PauseMenu` switch views on the shared `Pacman` game object.
`Pacman` receives validated configuration data and owns a `score_board`, while
ghost objects receive the current maze and movement state from `Pacman` during each
update.

## Resources


AI assistance was used to help review the project structure, clarify and simplify
this README, and identify how the configuration, maze generation, scoring, and
ghost pathfinding work together. The game-specific implementation, asset choices,
and final validation remain part of the project work.
Scores are stored in the JSON file selected by `highscore_filename`. At game
over, the player enters a name of one to ten letters, numbers, or spaces. The
scoreboard keeps at most the ten highest scores, sorted in descending order. If
the same player already exists, only their highest score is retained.

JSON was chosen because the scoreboard is small, human-readable, and does not
need a database or a server. The configuration loader creates an empty score
file when it does not exist or does not contain a valid list.

## Maze Generation

The game uses the assigned `mazegenerator` package from
`wheels/mazegenerator-2.0.2-py3-none-any.whl`. `Pacman.maze_init()` creates a
`MazeGenerator` with the selected width, height, and seed, then calls
`generate()`. The resulting grid stores wall information as direction flags.
The game converts that grid into screen coordinates, draws the walls, places
gums in accessible cells, and uses the same grid for movement and ghost path
finding. The configured seed makes level 1 reproducible; subsequent levels are
randomized.

## Implementation

- Python 3.11+ with Arcade for the window, rendering, sprites, textures, and
    keyboard events.
- `ParseConfig` validates the command-line JSON and produces a `ConfigData`
    dataclass.
- `Pacman` manages the maze, player movement, animation, lives, timer, scoring,
    level progression, collisions, and game state.
- Four ghost classes extend the abstract `Ghost` sprite. They use maze-aware
    movement, breadth-first search for chase paths, and distance calculations to
    move away from Pac-Man while vulnerable.
- Arcade `View` classes provide the main menu, pause menu, cheat mode, game-over
    name entry, and scoreboard screens.
- `score_board` loads, validates, sorts, and persists highscore data as JSON.

## General Software Architecture

`pac-man.py` is the entry point. It creates `ParseConfig`, constructs the
`Pacman` game view, opens an Arcade window, and displays `MainMenu`.

The main relationships are:

```text
pac-man.py
    -> ParseConfig / ConfigData
    -> Pacman (Arcade game view)
             -> MazeGenerator
             -> Ghost subclasses (Pinky, Blinky, Clyde, Inky)
             -> score_board
             -> MainMenu, PauseMenu, GameOverView, ScoreboardView
```

`enums.py` defines movement directions, movement vectors, and ghost modes.
`load_config.py` is responsible for input validation and defaults. `pacman.py`
owns the game loop and composes the other systems. `ghosts_algorithm.py`
contains the ghost behavior. `main_menu.py` contains screen transitions, while
`speed_screen.py` implements the cheat-mode speed screen.

## Resources

- [Python documentation](https://docs.python.org/3/): language and standard-library reference.
- [Arcade documentation](https://api.arcade.academy/): window, view, sprite, texture, and input APIs.
- [Python `json` documentation](https://docs.python.org/3/library/json.html): configuration and score-file handling.
- [Breadth-first search](https://en.wikipedia.org/wiki/Breadth-first_search): basis for ghost path finding on the maze grid.
- The assigned `mazegenerator` package included in `wheels/`: maze creation and wall-grid representation.

AI tools were used as a development aid for understanding requirements,
reviewing the existing module structure, suggesting documentation structure,
and checking that the README describes the implemented configuration, scoring,
maze generation, and architecture. The final implementation and project-specific
technical decisions remain part of this repository and should be reviewed by
the project author.