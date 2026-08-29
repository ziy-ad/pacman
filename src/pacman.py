from enum import IntFlag
from rich import print
from .load_config import ConfigData
import arcade
from mazegenerator import MazeGenerator
from rich.traceback import install
from abc import ABC, abstractmethod
import random
import time
install()

    
from collections import deque


class Ghost(ABC):
    def __init__(self, coordinates, speed):
        self.coordinates: tuple[int, int] = coordinates
        self.target_x = 0
        self.target_y = 0
        self.speed = speed



    @abstractmethod
    def get_path(self, start_time, used_cells, maze, pacman_pos, last_key=None):
        ...


def bfs_to_next_move(ghost_coordinates, used_cells, maze, pacman_pos, last_key=None):
        if ghost_coordinates == pacman_pos:
            return ghost_coordinates

        maze = maze.maze
        rows, cols = len(maze), len(maze[0])
        
        queue = deque([ghost_coordinates])
        visited = {ghost_coordinates: None}
        
        moves = [
            (directions.UP,    0, -1),
            (directions.RIGHT, 1,  0),
            (directions.DOWN,  0,  1),
            (directions.LEFT, -1,  0),
        ]
        
        while queue:
            cx, cy = queue.popleft()
            
            for wall_flag, dx, dy in moves:
                nx, ny = cx + dx, cy + dy
                
                if not (0 <= nx < cols and 0 <= ny < rows):
                    continue
                if (nx, ny) in visited:
                    continue
                if maze[cy][cx] & wall_flag:
                    continue

                if (nx, ny) in used_cells:
                    continue
                
                visited[(nx, ny)] = (cx, cy)
                
                if (nx, ny) == pacman_pos:
                    step = (nx, ny)
                    while visited[step] != ghost_coordinates:
                        print(step, end=" ")
                        step = visited[step]
                    # print(step)
                    return step
                
                queue.append((nx, ny))
        
        return ghost_coordinates


def random_next_move(ghost_coordinates, maze):
    gx, gy = ghost_coordinates
    options = []

    maze = maze.maze

    if not maze[gy][gx] & directions.UP and gy > 0:
        options.append((gx, gy - 1))
    if not maze[gy][gx] & directions.DOWN and gy < len(maze) - 1:
        options.append((gx, gy + 1))
    if not maze[gy][gx] & directions.LEFT and gx > 0:
        options.append((gx - 1, gy))
    if not maze[gy][gx] & directions.RIGHT and gx < len(maze[0]) - 1:
        options.append((gx + 1, gy))
    
    if not options:
        return ghost_coordinates
    return random.choice(options)


class BlueGhost(Ghost):
    def __init__(self, coordinates, speed):
        super().__init__(coordinates, speed)
        self.sprite = arcade.Sprite("src/assets/blueghost.png", scale=0.1)
        self.required_time = 3

    def get_path(self, start_time, used_cells, maze, pacman_pos, last_key=None):
        current = time.time()
        if current < self.required_time:
            return self.coordinates

        if pacman_pos == self.coordinates:
            return self.coordinates

        if pacman_pos in used_cells:
            return random_next_move(self.coordinates, maze)

        
        return bfs_to_next_move(self.coordinates, used_cells, maze, pacman_pos, last_key)


class PinkGhost(Ghost):
    def __init__(self, coordinates, speed):
        super().__init__(coordinates, speed)
        self.sprite = arcade.Sprite("src/assets/pinkghost.png", scale=0.1)
        self.required_time = 0

    def get_path(self, start_time, used_cells, maze, pacman_pos, last_key=None):
        current = time.time()
        if (current - start_time) < self.required_time:
            return self.coordinates
        
        return random_next_move(self.coordinates, maze)
        # gx, gy = self.coordinates
        # options = []
        # if not maze.maze[gy][gx] & directions.UP and gy > 0:
        #     options.append((gx, gy - 1))
        # if not maze.maze[gy][gx] & directions.DOWN and gy < len(maze.maze) - 1:
        #     options.append((gx, gy + 1))
        # if not maze.maze[gy][gx] & directions.LEFT and gx > 0:
        #     options.append((gx - 1, gy))
        # if not maze.maze[gy][gx] & directions.RIGHT and gx < len(maze.maze[0]) - 1:
        #     options.append((gx + 1, gy))
        
        # if not options:
        #     return self.coordinates # Stay still if trapped
        # return random.choice(options)


class RedGhost(Ghost):
    def __init__(self, coordinates, speed):
        super().__init__(coordinates, speed)
        self.sprite = arcade.Sprite("src/assets/redghost.png", scale=0.1)
        self.required_time = 6

    def get_path(self, start_time, used_cells, maze, pacman_pos, last_key=None):
        current = time.time()
        if (current - start_time) < self.required_time:
            return self.coordinates

        if self.coordinates == pacman_pos:
            return self.coordinates

        if pacman_pos in used_cells:
            return random_next_move(self.coordinates, maze)

        temp_maze = maze
        maze = maze.maze
        rows, cols = len(maze), len(maze[0])

        # if last_key is not None:
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

        return bfs_to_next_move(self.coordinates, used_cells, temp_maze, pacman_pos, last_key)


class OrangeGhost(Ghost):
    def __init__(self, coordinates, speed):
        super().__init__(coordinates, speed)
        self.sprite = arcade.Sprite("src/assets/orangeghost.png", scale=0.1)
        self.required_time = 9
        self.min_distance = 6

    def get_path(self, start_time, used_cells, maze, pacman_pos, last_key=None):
        current = time.time()
        if (current - start_time) < self.required_time:
            return self.coordinates

        if pacman_pos == self.coordinates:
            return self.coordinates

        if pacman_pos in used_cells:
            return random_next_move(self.coordinates, maze)


        maze_grid = maze.maze
        gx, gy = self.coordinates
        px, py = pacman_pos

        distance = abs(gx - px) + abs(gy - py)
        if distance > self.min_distance:
            target = self.get_position_infront(maze_grid, pacman_pos, last_key, self.min_distance)
            return bfs_to_next_move(self.coordinates, used_cells, maze, target, last_key)

        return bfs_to_next_move(self.coordinates, used_cells, maze, pacman_pos, last_key)
        
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
            # Check if we can move in this direction
            if maze_grid[y][x] & direction:
                break  # Wall blocks us, stop here
            
            # Move to next cell
            x += dx
            y += dy
            
            # Check bounds
            if not (0 <= x < cols and 0 <= y < rows):
                break
        
        return (x, y)


class directions(IntFlag):
    UP = 1
    RIGHT = 2
    DOWN = 4
    LEFT = 8


class Point:
    def __init__(self,x, y):
        self.x = x
        self.y = y
    def __iter__(self):
        yield self.x
        yield self.y


class Pacman(arcade.View):
    def __init__(self, parser: ConfigData):
        self.parser = parser
        self.wall_color = arcade.color.BLUE
        super().__init__(background_color=arcade.color.DARK_SLATE_BLUE)

        # maze config
        self.maze = MazeGenerator(seed=self.parser.seed, size=(self.parser.levels[0]["width"], self.parser.levels[0]["height"]))
        self.maze.generate(seed=self.parser.seed)
        # camera settings
        self.camera = arcade.Camera2D()
        self.cx, self.cy = self.camera.position
        # cell settings
        self.cell_size = 60
        self.cell_positions = [[] for i in  range(len(self.maze.maze))]
        self.forbiden_cells = set()
        self.points_cord = {}
        self.map_maze_coordinates()
        # pac man settings
        self.pac_man_frames = self.load_pacman_frames() 
        self.pac_man_seconds = 0
        self.pac_man_next = 1
        self.pac_man_frame_index = 0
        self.pac_man_possition = self.init_pacman_possition()
        self.pac_man = self.pac_man_frames[self.pac_man_next]
        self.visited_cells = set()
        self.current_key = directions.UP
        self.next_key = directions.UP
        self.pac_man_grid = (len(self.maze.maze[0]) // 2, len(self.maze.maze) // 2)
        self.used_cells = set()


        # spawn the ghosts in the corners of the maze
        self.corner_grid_coords = [
            (0, 0),
            (len(self.maze.maze[0]) - 1, 0),
            (0, len(self.maze.maze) - 1),
            (len(self.maze.maze[0]) - 1, len(self.maze.maze) - 1),
        ]
        self.positions = [self.cell_positions[0][0], self.cell_positions[0][-1], self.cell_positions[-1][0], self.cell_positions[-1][-1]]
        self.ghost_name = ["PinkGhost", "RedGhost", "OrangeGhost", "BlueGhost"]
        self.ghost_speed = self.cell_size * 0.1 * 0.8
        self.ghosts = {}
        self.ghost_list = arcade.SpriteList()

        self.start_time = time.time()

        for position, name in zip(self.corner_grid_coords, self.ghost_name):
            ghost_class = globals()[name]
            ghost = ghost_class(position, self.ghost_speed)
            gx, gy = position
            ghost.sprite.center_x, ghost.sprite.center_y = self.cell_positions[gy][gx]
            ghost.target_x, ghost.target_y = self.cell_positions[gy][gx]
            self.ghost_list.append(ghost.sprite)
            self.ghosts[name] = ghost

        


    def init_pacman_possition(self):
        x, y = self.cell_positions[len(self.cell_positions) // 2][len(self.cell_positions) // 2]
        return Point(x, y)

    def load_pacman_frames(self):
        return  [
            arcade.load_texture("src/assets/pacman_closed.png"),
            arcade.load_texture("src/assets/pacman_half.png"),
            arcade.load_texture("src/assets/pacman_open.png"),
        ]
    def map_maze_coordinates(self):
        num_rows = len(self.maze.maze)
        num_cols = len(self.maze.maze[0])

        # Total pixel size of the maze grid
        maze_pixel_w = num_cols * self.cell_size
        maze_pixel_h = num_rows * self.cell_size

        # Top-left cell center, so the whole grid is centered on the window
        start_x = (self.width  - maze_pixel_w) // 2 + self.cell_size // 2
        start_y = (self.height + maze_pixel_h) // 2 - self.cell_size // 2

        for idy, row in enumerate(self.maze.maze):
            y = start_y - idy * self.cell_size
            x = start_x
            for idx, _ in enumerate(row):
                if self.maze.maze[idy][idx] == 15:
                    self.forbiden_cells.add((idx, idy))
                else:
                    self.points_cord.update({(x, y): (idx, idy)})
                self.cell_positions[idy] += [(x, y)]
                x += self.cell_size
    

    def can_move(self):
        x, y = self.pac_man_possition
        directions_oposit = {
            directions.UP:directions.DOWN,
            directions.DOWN:directions.UP,
            directions.LEFT:directions.RIGHT,
            directions.RIGHT:directions.LEFT
            }
        result = True
        if (x, y) in self.points_cord:
            idx, idy = self.points_cord[(x, y)]
            if not self.maze.maze[idy][idx] & self.next_key:
                self.current_key = self.next_key
            result =  not self.maze.maze[idy][idx] & self.current_key

        if self.current_key == directions_oposit[self.next_key]:
            self.current_key = self.next_key  
        return result

    def make_move(self):
        match self.current_key:
            case directions.UP:
                self.pac_man_possition.y += self.cell_size * 0.1
            case directions.DOWN:
                self.pac_man_possition.y -= self.cell_size * 0.1
            case directions.RIGHT:
                self.pac_man_possition.x += self.cell_size * 0.1
            case directions.LEFT:
                self.pac_man_possition.x -= self.cell_size * 0.1

    def on_update(self, delta_time):
        self.pac_man_seconds += delta_time
        if self.pac_man_seconds >= 0.2:
            self.pac_man_frame_index += self.pac_man_next
            if self.pac_man_frame_index == 0 or self.pac_man_frame_index == 2:
                self.pac_man_next *= -1
            self.pac_man_seconds = 0
        if self.can_move():
            self.make_move()




        px, py = self.pac_man_possition.x, self.pac_man_possition.y
        grid_lookup = self.points_cord.get((px, py))
        if grid_lookup is not None:
            self.pac_man_grid = grid_lookup

        # print(self.pac_man_grid)
        for ghost in self.ghosts.values():
            self.used_cells.add(ghost.coordinates)

        for ghost in self.ghosts.values():
            # Check if ghost has reached the center of its target cell
            if abs(ghost.sprite.center_x - ghost.target_x) <= ghost.speed and \
                abs(ghost.sprite.center_y - ghost.target_y) <= ghost.speed:
                
                # Snap to exact target to prevent floating point drift
                ghost.sprite.center_x = ghost.target_x
                ghost.sprite.center_y = ghost.target_y

                # Ask AI for the next grid cell to move to
                # position = self.cell_positions[self.pac_man_possition.y][self.pac_man_possition.x]
                next_cell = ghost.get_path(self.start_time, self.used_cells, self.maze, self.pac_man_grid, last_key=self.current_key)
                
                if next_cell:
                    self.used_cells.add(next_cell)
                    gx, gy = next_cell
                    ghost.coordinates = (gx, gy)  # Update logical grid position
                    # Assign new pixel target to move towards
                    ghost.target_x, ghost.target_y = self.cell_positions[gy][gx]
            
            # Smoothly move the sprite towards the target position
            if ghost.sprite.center_x < ghost.target_x:
                ghost.sprite.center_x += ghost.speed
            elif ghost.sprite.center_x > ghost.target_x:
                ghost.sprite.center_x -= ghost.speed
                
            if ghost.sprite.center_y < ghost.target_y:
                ghost.sprite.center_y += ghost.speed
            elif ghost.sprite.center_y > ghost.target_y:
                ghost.sprite.center_y -= ghost.speed
        print(self.used_cells)
        self.used_cells = set()

    def get_pac_man_frame(self):
        match self.current_key:
            case directions.UP:
                return self.pac_man_frames[self.pac_man_frame_index].rotate_270()
            case directions.RIGHT:
                return self.pac_man_frames[self.pac_man_frame_index]
            case directions.DOWN:
                return self.pac_man_frames[self.pac_man_frame_index].rotate_90()
            case directions.LEFT:
                return self.pac_man_frames[self.pac_man_frame_index].flip_horizontally()



    def on_draw(self):
        self.clear()
        with self.camera.activate():
            text = arcade.Text(f"score: {len(self.visited_cells)}", 40, self.height - 100, arcade.color.ALLOY_ORANGE, font_size=30)
            text.draw()
            for idy, row in enumerate(self.cell_positions):
                for idx, cell in enumerate(row):
                    x, y = cell
                    if self.maze.maze[idy][idx] & directions.UP:
                        arcade.draw_line(x - self.cell_size // 2, y + self.cell_size // 2, x + self.cell_size // 2, y + self.cell_size // 2 , self.wall_color , line_width=5)
                    if self.maze.maze[idy][idx] & directions.RIGHT:
                        arcade.draw_line(x + self.cell_size // 2, y - self.cell_size // 2 , x + self.cell_size // 2, y + self.cell_size // 2, self.wall_color , line_width=5)
                    if self.maze.maze[idy][idx] & directions.LEFT:
                        arcade.draw_line(x - self.cell_size // 2, y - self.cell_size // 2, x - self.cell_size // 2 , y + self.cell_size // 2, self.wall_color , line_width=5)
                    if self.maze.maze[idy][idx] & directions.DOWN:
                        arcade.draw_line(x - self.cell_size // 2, y - self.cell_size // 2 , x + self.cell_size // 2, y - self.cell_size // 2 ,self.wall_color , line_width=5)
                    if (x, y) not in self.visited_cells and (idx, idy) not in self.forbiden_cells:
                        arcade.draw_point(x, y , arcade.color.BABY_BLUE_EYES, size=4)

            self.ghost_list.draw()
            px, py = self.pac_man_possition
            if (px, py) in self.points_cord:
                self.visited_cells.add((px, py))
            pac_man = arcade.XYWH(px , py, 40, 40)
            arcade.draw_texture_rect(self.get_pac_man_frame(), pac_man)
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.cx -= dx
        self.cy -= dy
        self.camera.position = (self.cx, self.cy)
    
    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.F:
            self.window.set_fullscreen(not self.window.fullscreen)            
        if symbol == arcade.key.RIGHT or symbol == arcade.key.D:
            self.next_key = directions.RIGHT
        elif symbol == arcade.key.LEFT or symbol == arcade.key.A:
            self.next_key = directions.LEFT            
        elif symbol == arcade.key.DOWN or symbol == arcade.key.S:
            self.next_key = directions.DOWN            
        elif symbol == arcade.key.UP or symbol == arcade.key.W:
            self.next_key = directions.UP
