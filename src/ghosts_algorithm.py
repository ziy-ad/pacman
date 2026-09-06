from enum import IntFlag, Enum
from abc import ABC, abstractmethod
import random
import time
import arcade
from pathlib import Path

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

class Ghost(arcade.Sprite, ABC):
    normal_mode_texture: arcade.Texture
    def __init__(self, coordinates, maze, cell_size):
        self.all_texture: dict[directions, arcade.Texture] = {}
        super().__init__(scale=0.1 )
        self.maze = maze
        self.cell_size = cell_size
        self.direction = directions.LEFT
        self.mode = Ghost_modes.Chase_mode
        self.fight_mode_texture = arcade.load_texture("src/assets/ghosts/fright/frightened_blue.png")
        self.width = self.cell_size * 0.7
        self.height = self.cell_size * 0.7
        self.coordinates: tuple[int, int] = coordinates
        self.init_coord: tuple[int, int] = coordinates
        self.last_coordinates = []
        self.target_x = 0
        self.target_y = 0
        self.eatable = False
        self.time_to_respawn = 0
        self.load_textures()
        self.normal_mode_texture = self.all_texture[self.direction]
        self.texture = self.normal_mode_texture
    def load_textures(self):
        assets_path = Path(__file__).resolve().parent / "assets" / "ghosts"
        for dir in directions:
            path = assets_path / self.__class__.__name__ / (str(dir.name).lower() + ".png")
            self.all_texture[dir] = arcade.load_texture(path)
        

    def update(self, delta_time: float = 1 / 60, *args, **kwargs) -> None:
        cell_positions = kwargs["cell_positions"]
        used_cells = kwargs["used_cells"]
        ghost_speed = kwargs["ghost_speed"]
        current_key = kwargs["current_key"]
        start_time = kwargs["start_time"]
        pac_man_grid = kwargs["pac_man_grid"]
        edible = kwargs["edible"]
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
        if abs(self.center_x - self.target_x) <= ghost_step and \
            abs(self.center_y - self.target_y) <= ghost_step:
            
            # Snap to exact target to prevent floating point drift
            self.center_x = self.target_x
            self.center_y = self.target_y

            # Ask AI for the next grid cell to move to
            # position = self.cell_positions[self.pac_man_possition.y][self.pac_man_possition.x]
            if self.mode == Ghost_modes.Fight_mode:
                next_cell = self.run_away(pac_man_grid)
            else:
                next_cell = self.get_path(
                    start_time,
                    used_cells,
                    pac_man_grid,
                    current_key)
            
            if next_cell:

                used_cells.add(next_cell)
                gx, gy = next_cell
                if len(self.last_coordinates) > 2:
                    self.last_coordinates.pop(0)
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
            # Smoothly move the sprite towards the target position
            if self.center_x < self.target_x:
                self.center_x += ghost_step
            elif self.center_x > self.target_x:
                self.center_x -= ghost_step
                
            if self.center_y < self.target_y:
                self.center_y += ghost_step
            elif self.center_y > self.target_y:
                self.center_y -= ghost_step

    def reset(self, cell_position):
        gx, gy = self.init_coord
        self.coordinates = self.init_coord
        self.center_x, self.center_y = cell_position[gy][gx]
        self.target_x, self.target_y = cell_position[gy][gx]

    @abstractmethod
    def get_path(self, start_time, used_cells, pacman_pos, edible, last_key=None):
        ...


    def bfs_to_next_move(self, used_cells, pacman_pos, last_key=None):
        if self.coordinates == pacman_pos:
            return self.coordinates

        rows, cols = len(self.maze), len(self.maze[0])
        recent_coordinates = set(self.last_coordinates)

        queue = [self.coordinates]
        visited = {self.coordinates: None}

        while queue:
            cx, cy = queue.pop(0)
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
                        step = visited[step]
                    return step

                queue.append((nx, ny))

        gx, gy = self.coordinates
        fallback = []
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
            filtered = [cell for cell in fallback if cell not in recent_coordinates]
            return random.choice(filtered if filtered else fallback)

        return self.coordinates


    def random_next_move(self):
        gx, gy = self.coordinates
        options = []
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

        filtred_options = []
        for option in options:
            if option not in self.last_coordinates:
                filtred_options.append(option)

        if not filtred_options:
            return random.choice(options)
        
        return random.choice(filtred_options)

    def run_away(self, pacman_pos):
        gx, gy = self.coordinates
        rows, cols = len(self.maze), len(self.maze[0])
        far = float('inf')


        def bfs_distances(source):
            """Real corridor distance from source to every reachable cell."""
            rows, cols = len(self.maze), len(self.maze[0])
            dist = {source: 0}
            queue = [source]

            while queue:
                cx, cy = queue.pop(0)
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

        valid = {}
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

        forward = {k: v for k, v in valid.items() if k not in self.last_coordinates}
        if forward:
            valid = forward

        best = max(v for _ , v in valid.items())
        valid = {k: v for k, v in valid.items() if v == best}
        return random.choice(list(valid.keys()))


class Inky(Ghost):
    def __init__(self, coordinates, maze,  cell_size):
        super().__init__(coordinates=coordinates, maze=maze ,cell_size=cell_size)

        self.required_time = 3

    def get_path(self, start_time, used_cells, pacman_pos, last_key=None):
        current = time.time()
        if (current - start_time) < self.required_time:
            return self.coordinates

        if pacman_pos == self.coordinates:
            return self.coordinates


        if pacman_pos in used_cells:
            return self.random_next_move()

        
        return self.bfs_to_next_move(used_cells, pacman_pos, last_key)


class Pinky(Ghost):
    def __init__(self, coordinates, maze,  cell_size):
        super().__init__(coordinates=coordinates, maze=maze ,cell_size=cell_size)
        self.required_time = 0

    def get_path(self, start_time, used_cells, pacman_pos, last_key=None):
        current = time.time()
        if (current - start_time) < self.required_time:
            return self.coordinates

        if pacman_pos == self.coordinates:
            return self.coordinates


        return self.random_next_move()


class Blinky(Ghost):
    def __init__(self, coordinates, maze,  cell_size):
        super().__init__(coordinates=coordinates, maze=maze ,cell_size=cell_size)

        self.required_time = 6

    def get_path(self, start_time, used_cells, pacman_pos, last_key=None):
        current = time.time()
        if (current - start_time) < self.required_time:
            return self.coordinates

        if self.coordinates == pacman_pos:
            return self.coordinates

        if pacman_pos in used_cells:
            return self.random_next_move()

        rows, cols = len(self.maze), len(self.maze[0])

        if last_key is not None:
            gx , gy = pacman_pos
            if last_key == directions.LEFT and gx > 0 and not self.maze[gy][gx] & directions.LEFT:
                    pacman_pos = (gx - 1, gy)
            elif last_key == directions.RIGHT and gx < cols - 1 and not self.maze[gy][gx] & directions.RIGHT:
                    pacman_pos = (gx + 1, gy)
            elif last_key == directions.UP and gy > 0 and not self.maze[gy][gx] & directions.UP:
                    pacman_pos = (gx, gy - 1)
            elif last_key == directions.DOWN and gy < rows - 1 and not self.maze[gy][gx] & directions.DOWN:
                    pacman_pos = (gx, gy + 1)

        return self.bfs_to_next_move(used_cells, pacman_pos, last_key)


class Clyde(Ghost):
    def __init__(self, coordinates, maze,  cell_size):
        super().__init__(coordinates=coordinates, maze=maze ,cell_size=cell_size)
        self.required_time = 9

        self.min_distance = 6

    def get_path(self, start_time, used_cells, pacman_pos, last_key=None):
        current = time.time()
        if (current - start_time) < self.required_time:
            return self.coordinates

        if pacman_pos == self.coordinates:
            return self.coordinates


        if pacman_pos in used_cells:
            return self.random_next_move()

        gx, gy = self.coordinates
        px, py = pacman_pos

        distance = abs(gx - px) + abs(gy - py)
        if distance > self.min_distance:
            target = self.get_position_infront(self.maze, pacman_pos, last_key, self.min_distance)
            return self.bfs_to_next_move(used_cells,  target, last_key)

        return self.bfs_to_next_move(used_cells, pacman_pos, last_key)
        
    def get_position_infront(self, maze_grid, start_pos, direction, max_steps):
        """Look up to max_steps ahead in the given direction, stopping at walls."""
        x, y = start_pos
        rows, cols = len(maze_grid), len(maze_grid[0])
        
        direction_delta = {
            directions.UP:    (0, -1),
            directions.RIGHT: (1,  0),
            directions.DOWN:  (0,  1),
            directions.LEFT:  (-1, 0),
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
