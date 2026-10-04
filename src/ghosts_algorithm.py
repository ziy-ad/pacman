"""Ghost classes and their movement algorithms."""

from abc import ABC, abstractmethod
import random
import time
import arcade
from collections import deque
from typing import Any
from .enums import directions, moves, Ghost_modes
from .paths import resource_path
import sys

class Ghost(arcade.Sprite, ABC):
    """Base class of all the ghosts."""

    normal_mode_texture: arcade.Texture

    def __init__(
        self,
        coordinates: tuple[int, int],
        maze: list[list[int]],
        cell_size: int,
    ) -> None:
        """Set up the ghost sprite and its state."""
        self.all_texture: dict[directions, arcade.Texture] = {}
        super().__init__(scale=0.1)
        self.maze = maze
        self.cell_size = cell_size
        self.direction = directions.LEFT
        self.mode = Ghost_modes.Chase_mode
        self.fight_mode_texture = arcade.load_texture(
            resource_path("src/assets/ghosts/fright/frightened_blue.png")
        )
        self.width = self.cell_size * 0.7
        self.height = self.cell_size * 0.7
        self.coordinates: tuple[int, int] = coordinates
        self.init_coord: tuple[int, int] = coordinates
        self.last_coordinates: deque[tuple[int, int]] = deque()
        self.target_x: float = 0
        self.target_y: float = 0
        self.eatable = False
        self.time_to_respawn: float = 0
        self.load_textures()
        self.normal_mode_texture = self.all_texture[self.direction]
        self.texture = self.normal_mode_texture
        self.path: list[tuple[int, int]] = []

    def load_textures(self) -> None:
        """Load the textures of each direction."""
        assets_path = resource_path("src/assets/ghosts")
        for dir in directions:
            path = (
                assets_path
                / self.__class__.__name__
                / (str(dir.name).lower() + ".png")
            )
            self.all_texture[dir] = arcade.load_texture(path)

    def update(
        self, delta_time: float = 1 / 60, *args: Any, **kwargs: Any
    ) -> None:
        """Move the ghost and choose its next cell."""
        cell_positions = kwargs["cell_positions"]
        used_cells = kwargs["used_cells"]
        ghost_speed = kwargs["ghost_speed"]
        current_key = kwargs["current_key"]
        start_time = kwargs["start_time"]
        pac_man_grid = kwargs["pac_man_grid"]
        edible = kwargs["edible"]
        cheater = kwargs["cheater"]

        if cheater.ghost_freeze:
            return

        if self.eatable:
            self.time_to_respawn += delta_time
            self.visible = False
            if self.time_to_respawn >= 5.0:
                self.eatable = False
                self.visible = True
                self.time_to_respawn = 0.0
                self.coordinates = self.init_coord
                gx, gy = self.coordinates
                self.center_x, self.center_y = cell_positions[gy][gx]
                self.target_x, self.target_y = cell_positions[gy][gx]
        used_cells.add(self.coordinates)
        ghost_step = self.cell_size * ghost_speed
        if (
            abs(self.center_x - self.target_x) <= ghost_step
            and abs(self.center_y - self.target_y) <= ghost_step
        ):

            self.center_x = self.target_x
            self.center_y = self.target_y
            self.path.clear()
            if self.mode == Ghost_modes.Fight_mode:
                next_cell = self.run_away(pac_man_grid)
            else:
                next_cell = self.get_path(
                    start_time, used_cells, pac_man_grid, current_key
                )

            if next_cell:

                used_cells.add(next_cell)
                gx, gy = next_cell
                if len(self.last_coordinates) > 2:
                    self.last_coordinates.popleft()
                self.last_coordinates.append(self.coordinates)
                self.coordinates = (gx, gy)
                self.target_x, self.target_y = cell_positions[gy][gx]
                if self.center_x == self.target_x:
                    if self.center_y > self.target_y:
                        self.direction = directions.DOWN
                    else:
                        self.direction = directions.UP
                else:
                    if self.center_x > self.target_x:
                        self.direction = directions.LEFT
                    else:
                        self.direction = directions.RIGHT
                if not edible:
                    self.normal_mode_texture = self.all_texture[self.direction]
                    self.texture = self.normal_mode_texture
        else:
            if self.center_x < self.target_x:
                self.center_x += ghost_step
            elif self.center_x > self.target_x:
                self.center_x -= ghost_step

            if self.center_y < self.target_y:
                self.center_y += ghost_step
            elif self.center_y > self.target_y:
                self.center_y -= ghost_step

    def reset(self, cell_position: list[list[tuple[float, float]]]) -> None:
        """Send the ghost back to its starting cell."""
        gx, gy = self.init_coord
        self.coordinates = self.init_coord
        self.center_x, self.center_y = cell_position[gy][gx]
        self.target_x, self.target_y = cell_position[gy][gx]

    @abstractmethod
    def get_path(
        self,
        start_time: float,
        used_cells: set[tuple[int, int]],
        pacman_pos: tuple[int, int],
        last_key: directions | None = None,
    ) -> tuple[int, int]:
        """Return the next cell the ghost should go to."""
        ...

    def bfs_to_next_move(
        self,
        used_cells: set[tuple[int, int]],
        pacman_pos: tuple[int, int],
        last_key: directions | None = None,
    ) -> tuple[int, int]:
        """Return the next cell on the shortest path to the target."""
        if self.coordinates == pacman_pos:
            return self.coordinates

        rows, cols = len(self.maze), len(self.maze[0])
        recent_coordinates = set(self.last_coordinates)

        queue = deque([self.coordinates])
        visited: dict[tuple[int, int], Any] = {self.coordinates: None}
        while queue:
            cx, cy = queue.popleft()
            for move in moves:
                wall_flag, dx, dy = move.value
                nx, ny = cx + dx, cy + dy

                if not (0 <= nx < cols and 0 <= ny < rows):
                    continue
                if (nx, ny) in visited:
                    continue
                if self.maze[cy][cx] & wall_flag:
                    continue

                if (nx, ny) in used_cells or (nx, ny) in recent_coordinates:
                    continue

                visited[(nx, ny)] = (cx, cy)

                if (nx, ny) == pacman_pos:
                    step = (nx, ny)
                    while visited[step] != self.coordinates:
                        self.path += [step]
                        step = visited[step]
                    self.path += [step]
                    self.path = self.path[::-1]
                    return step

                queue.append((nx, ny))
        gx, gy = self.coordinates
        fallback: list[tuple[int, int]] = []
        for move in moves:
            wall_flag, dx, dy = move.value
            nx, ny = gx + dx, gy + dy

            if not (0 <= nx < cols and 0 <= ny < rows):
                continue
            if self.maze[gy][gx] & wall_flag:
                continue
            if (nx, ny) in used_cells:
                continue
            fallback.append((nx, ny))

        if fallback:
            filtered = [
                cell for cell in fallback if cell not in recent_coordinates
            ]
            th = random.choice(filtered if filtered else fallback)
            self.path += [th]
            return th

        return self.coordinates

    def random_next_move(self) -> tuple[int, int]:
        """Return a random neighbouring cell."""
        gx, gy = self.coordinates
        options: list[tuple[int, int]] = []
        for move in moves:
            wall_flag, dx, dy = move.value
            nx, ny = gx + dx, gy + dy

            if not (0 <= nx < len(self.maze[0]) and 0 <= ny < len(self.maze)):
                continue
            if self.maze[gy][gx] & wall_flag:
                continue
            options.append((nx, ny))

        if not options:
            return self.coordinates

        filtred_options: list[tuple[int, int]] = []
        for option in options:
            if option not in self.last_coordinates:
                filtred_options.append(option)

        if not filtred_options:
            th = random.choice(options)
            self.path += [th]
            return th
        th = random.choice(filtred_options)
        self.path += [th]
        return th

    def run_away(self, pacman_pos: tuple[int, int]) -> tuple[int, int]:
        """Return the neighbouring cell farthest from Pac-Man."""
        gx, gy = self.coordinates
        rows, cols = len(self.maze), len(self.maze[0])
        far = float("inf")

        def bfs_distances(
            source: tuple[int, int],
        ) -> dict[tuple[int, int], int]:
            """Real corridor distance from source to every reachable cell."""
            rows, cols = len(self.maze), len(self.maze[0])
            dist = {source: 0}
            queue = deque([source])

            while queue:
                cx, cy = queue.popleft()
                for move in moves:
                    wall_flag, dx, dy = move.value
                    nx, ny = cx + dx, cy + dy
                    if (nx, ny) in dist:
                        continue
                    if not (0 <= nx < cols and 0 <= ny < rows):
                        continue
                    if self.maze[cy][cx] & wall_flag:
                        continue
                    dist[(nx, ny)] = dist[(cx, cy)] + 1
                    queue.append((nx, ny))
            return dist

        dist = bfs_distances(pacman_pos)

        valid: dict[tuple[int, int], float] = {}
        for move in moves:
            wall_flag, dx, dy = move.value
            nx, ny = gx + dx, gy + dy
            if not (0 <= nx < cols and 0 <= ny < rows):
                continue
            if self.maze[gy][gx] & wall_flag:
                continue
            valid[(nx, ny)] = dist.get((nx, ny), far)

        if not valid:
            return self.coordinates

        forward = {
            k: v for k, v in valid.items() if k not in self.last_coordinates
        }
        if forward:
            valid = forward

        best = max(v for _, v in valid.items())
        valid = {k: v for k, v in valid.items() if v == best}
        return random.choice(list(valid.keys()))


class Inky(Ghost):
    """Ghost that targets a cell based on Pac-Man and Blinky."""

    def __init__(
        self,
        coordinates: tuple[int, int],
        maze: list[list[int]],
        cell_size: int,
        blinky: Ghost,
    ) -> None:
        """Set up Inky and keep a reference to Blinky."""
        super().__init__(
            coordinates=coordinates, maze=maze, cell_size=cell_size
        )
        self.blinky = blinky
        self.required_time = 3

    def get_path(
        self,
        start_time: float,
        used_cells: set[tuple[int, int]],
        pacman_pos: tuple[int, int],
        last_key: directions | None = None,
    ) -> tuple[int, int]:
        """Return the next cell, aiming ahead of Pac-Man."""
        current = time.time()
        if not pacman_pos:
            print("test")
            sys.exit()
        if (current - start_time) < self.required_time:
            return self.coordinates

        if pacman_pos == self.coordinates:
            return self.coordinates
        target: Any = (0, -2)
        match last_key:
            case directions.UP:
                target: Any = (0, -2)
            case directions.DOWN:
                target = (0, 2)
            case directions.LEFT:
                target = (-2, 0)
            case directions.RIGHT:
                target = (2, 0)
        target = list(t + p for p, t in zip(pacman_pos, target))
        while target[0] < 0:
            target[0] += 1
        while target[0] > len(self.maze[0]) - 1:
            target[0] -= 1
        while target[1] < 0:
            target[1] += 1
        while target[1] > len(self.maze) - 1:
            target[1] -= 1
        x = target[0] * 2 - self.blinky.coordinates[0]
        y = target[1] * 2 - self.blinky.coordinates[1]
        x = max(min(len(self.maze[0]) - 1, x), 0)
        y = max(min(len(self.maze) - 1, y), 0)
        target = (x, y)
        return self.bfs_to_next_move(used_cells, target, last_key)


class Pinky(Ghost):
    """Ghost that moves randomly."""

    def __init__(
        self,
        coordinates: tuple[int, int],
        maze: list[list[int]],
        cell_size: int,
    ) -> None:
        """Set up Pinky."""
        super().__init__(
            coordinates=coordinates, maze=maze, cell_size=cell_size
        )
        self.required_time = 0

    def get_path(
        self,
        start_time: float,
        used_cells: set[tuple[int, int]],
        pacman_pos: tuple[int, int],
        last_key: directions | None = None,
    ) -> tuple[int, int]:
        """Return a random next cell once the delay is over."""
        current = time.time()
        if (current - start_time) < self.required_time:
            self.path += [self.coordinates]
            return self.coordinates

        if pacman_pos == self.coordinates:
            self.path += [self.coordinates]

            return self.coordinates

        return self.random_next_move()


class Blinky(Ghost):
    """Ghost that chases Pac-Man directly."""

    def __init__(
        self,
        coordinates: tuple[int, int],
        maze: list[list[int]],
        cell_size: int,
    ) -> None:
        """Set up Blinky."""
        super().__init__(
            coordinates=coordinates, maze=maze, cell_size=cell_size
        )

        self.required_time = 6

    def get_path(
        self,
        start_time: float,
        used_cells: set[tuple[int, int]],
        pacman_pos: tuple[int, int],
        last_key: directions | None = None,
    ) -> tuple[int, int]:
        """Return the next cell towards Pac-Man."""
        current = time.time()
        if (current - start_time) < self.required_time:
            return self.coordinates

        if self.coordinates == pacman_pos:
            return self.coordinates

        rows, cols = len(self.maze), len(self.maze[0])

        if last_key is not None:
            gx, gy = pacman_pos
            if (
                last_key == directions.LEFT
                and gx > 0
                and not self.maze[gy][gx] & directions.LEFT
            ):
                pacman_pos = (gx - 1, gy)
            elif (
                last_key == directions.RIGHT
                and gx < cols - 1
                and not self.maze[gy][gx] & directions.RIGHT
            ):
                pacman_pos = (gx + 1, gy)
            elif (
                last_key == directions.UP
                and gy > 0
                and not self.maze[gy][gx] & directions.UP
            ):
                pacman_pos = (gx, gy - 1)
            elif (
                last_key == directions.DOWN
                and gy < rows - 1
                and not self.maze[gy][gx] & directions.DOWN
            ):
                pacman_pos = (gx, gy + 1)

        return self.bfs_to_next_move(used_cells, pacman_pos, last_key)


class Clyde(Ghost):
    """Ghost that chases Pac-Man or goes back to its corner."""

    def __init__(
        self,
        coordinates: tuple[int, int],
        maze: list[list[int]],
        cell_size: int,
    ) -> None:
        """Set up Clyde."""
        super().__init__(
            coordinates=coordinates, maze=maze, cell_size=cell_size
        )
        self.required_time = 9

        self.min_distance = 6

    def get_path(
        self,
        start_time: float,
        used_cells: set[tuple[int, int]],
        pacman_pos: tuple[int, int],
        last_key: directions | None = None,
    ) -> tuple[int, int]:
        """Return the next cell, chasing or retreating."""
        current = time.time()
        if (current - start_time) < self.required_time:
            return self.coordinates

        if pacman_pos == self.coordinates:
            return self.coordinates

        gx, gy = self.coordinates
        px, py = pacman_pos

        distance = abs(gx - px) + abs(gy - py)
        if distance > self.min_distance:
            target = self.get_position_infront(
                self.maze, pacman_pos, last_key, self.min_distance
            )
            return self.bfs_to_next_move(used_cells, target, last_key)

        return self.bfs_to_next_move(used_cells, self.init_coord, last_key)

    def get_position_infront(
        self,
        maze_grid: list[list[int]],
        start_pos: tuple[int, int],
        direction: Any,
        max_steps: int,
    ) -> tuple[int, int]:
        """Return the cell up to max_steps ahead, stopping at walls."""
        x, y = start_pos
        rows, cols = len(maze_grid), len(maze_grid[0])

        direction_delta = {
            directions.UP: (0, -1),
            directions.RIGHT: (1, 0),
            directions.DOWN: (0, 1),
            directions.LEFT: (-1, 0),
        }

        dx, dy = direction_delta.get(direction, (0, 0))

        for _ in range(max_steps):
            if maze_grid[y][x] & direction:
                break

            x += dx
            y += dy

            if not (0 <= x < cols and 0 <= y < rows):
                break
        return (x, y)
