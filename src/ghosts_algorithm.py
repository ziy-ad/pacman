from enum import IntFlag, Enum
from abc import ABC, abstractmethod
import random
import time
import arcade


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


class Ghost(ABC):
    def __init__(self, coordinates):
        self.coordinates: tuple[int, int] = coordinates
        self.init_coord: tuple[int, int] = coordinates
        self.last_coordinates = []
        self.target_x = 0
        self.target_y = 0
        self.eatable = False
        self.time_to_respawn = 0

    @abstractmethod
    def get_path(self, start_time, used_cells, maze, pacman_pos, edible, last_key=None):
        ...


    def bfs_to_next_move(self, used_cells, maze, pacman_pos, last_key=None):
        if self.coordinates == pacman_pos:
            return self.coordinates

        maze = maze.maze
        rows, cols = len(maze), len(maze[0])
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
                if maze[cy][cx] & wall_flag:
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
            if maze[gy][gx] & wall_flag:
                continue
            if (nx, ny) in used_cells:
                continue
            fallback.append((nx, ny))

        if fallback:
            filtered = [cell for cell in fallback if cell not in recent_coordinates]
            return random.choice(filtered if filtered else fallback)

        return self.coordinates


    def random_next_move(self, maze):
        gx, gy = self.coordinates
        options = []

        maze = maze.maze

        for move in moves:
            wall_flag, dx, dy = move.value
            nx, ny = gx + dx, gy + dy
            
            if not (0 <= nx < len(maze[0]) and 0 <= ny < len(maze)):
                continue
            if maze[gy][gx] & wall_flag:
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

    def run_away(self, maze, pacman_pos, last_coordinates):
        gx, gy = self.coordinates
        grid = maze.maze
        rows, cols = len(grid), len(grid[0])
        far = float('inf')


        def bfs_distances(maze, source):
            """Real corridor distance from source to every reachable cell."""
            grid = maze.maze
            rows, cols = len(grid), len(grid[0])
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
                    if grid[cy][cx] & wall_flag:
                        continue
                    dist[(nx, ny)] = dist[(cx, cy)] + 1
                    queue.append((nx, ny))
            return dist

        dist = bfs_distances(maze, pacman_pos)

        valid = {}
        for move in moves:
            wall_flag, dx, dy = move.value
            nx, ny = gx + dx, gy + dy
            if not (0 <= nx < cols and 0 <= ny < rows):
                continue
            if grid[gy][gx] & wall_flag:
                continue
            valid[(nx, ny)] = dist.get((nx, ny), far)

        if not valid:
            return self.coordinates

        forward = {k: v for k, v in valid.items() if k not in last_coordinates}
        if forward:
            valid = forward

        best = max(v for _ , v in valid.items())
        valid = {k: v for k, v in valid.items() if v == best}
        return random.choice(list(valid.keys()))


class BlueGhost(Ghost):
    def __init__(self, coordinates):
        super().__init__(coordinates)
        self.sprite = arcade.Sprite("src/assets/blueghost.png", scale=0.1)
        self.sprite.width = 20
        self.sprite.height = 20
        self.required_time = 3

    def get_path(self, start_time, used_cells, maze, pacman_pos, edible, last_key=None):
        current = time.time()
        if (current - start_time) < self.required_time:
            return self.coordinates

        if pacman_pos == self.coordinates:
            return self.coordinates

        if edible:
            return self.run_away(maze, pacman_pos, self.last_coordinates)

        # return run_away(self.coordinates, maze, pacman_pos, self.last_coordinates)
        if pacman_pos in used_cells:
            return self.random_next_move(maze)

        
        return self.bfs_to_next_move(used_cells, maze, pacman_pos, last_key)


class PinkGhost(Ghost):
    def __init__(self, coordinates):
        super().__init__(coordinates)
        self.sprite = arcade.Sprite("src/assets/pinkghost.png", scale=0.1)
        self.sprite.width = 20
        self.sprite.height = 20
        self.required_time = 0

    def get_path(self, start_time, used_cells, maze, pacman_pos, edible, last_key=None):
        current = time.time()
        if (current - start_time) < self.required_time:
            return self.coordinates

        if pacman_pos == self.coordinates:
            return self.coordinates

        if edible:
            return self.run_away(maze, pacman_pos, self.last_coordinates)

        return self.random_next_move(maze)


class RedGhost(Ghost):
    def __init__(self, coordinates):
        super().__init__(coordinates)
        self.sprite = arcade.Sprite("src/assets/redghost.png", scale=0.1)
        self.sprite.width = 20
        self.sprite.height = 20
        self.required_time = 6

    def get_path(self, start_time, used_cells, maze, pacman_pos, edible, last_key=None):
        current = time.time()
        if (current - start_time) < self.required_time:
            return self.coordinates

        if self.coordinates == pacman_pos:
            return self.coordinates

        if edible:
            return self.run_away(maze, pacman_pos, self.last_coordinates)

        if pacman_pos in used_cells:
            return self.random_next_move(maze)

        temp_maze = maze
        maze = maze.maze
        rows, cols = len(maze), len(maze[0])

        if last_key is not None:
            gx , gy = pacman_pos
            if last_key == directions.LEFT and gx > 0 and not maze[gy][gx] & directions.LEFT:
                    pacman_pos = (gx - 1, gy)
            elif last_key == directions.RIGHT and gx < cols - 1 and not maze[gy][gx] & directions.RIGHT:
                    pacman_pos = (gx + 1, gy)
            elif last_key == directions.UP and gy > 0 and not maze[gy][gx] & directions.UP:
                    pacman_pos = (gx, gy - 1)
            elif last_key == directions.DOWN and gy < rows - 1 and not maze[gy][gx] & directions.DOWN:
                    pacman_pos = (gx, gy + 1)

        return self.bfs_to_next_move(used_cells, temp_maze, pacman_pos, last_key)


class OrangeGhost(Ghost):
    def __init__(self, coordinates, ):
        super().__init__(coordinates)
        self.sprite = arcade.Sprite("src/assets/orangeghost.png", scale=0.1)
        self.sprite.width = 20
        self.sprite.height = 20
        self.required_time = 9
        self.min_distance = 6

    def get_path(self, start_time, used_cells, maze, pacman_pos, edible, last_key=None):
        current = time.time()
        if (current - start_time) < self.required_time:
            return self.coordinates

        if pacman_pos == self.coordinates:
            return self.coordinates

        if edible:
            return self.run_away(maze, pacman_pos, self.last_coordinates)

        if pacman_pos in used_cells:
            return self.random_next_move(maze)

        maze_grid = maze.maze
        gx, gy = self.coordinates
        px, py = pacman_pos

        distance = abs(gx - px) + abs(gy - py)
        if distance > self.min_distance:
            target = self.get_position_infront(maze_grid, pacman_pos, last_key, self.min_distance)
            return self.bfs_to_next_move(used_cells, maze, target, last_key)

        return self.bfs_to_next_move(used_cells, maze, pacman_pos, last_key)
        
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
