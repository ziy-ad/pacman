from enum import IntFlag
from rich import print
from .load_config import ConfigData
import arcade
from mazegenerator import MazeGenerator
from rich.traceback import install
from abc import ABC, abstractmethod
import random

install()

class Ghost(ABC):
    def __init__(self, coordinates):
        # coordinates are logical grid indices (idx, idy)
        self.coordinates: tuple[int, int] = coordinates
        self.target_x = 0
        self.target_y = 0
        self.speed = 6.0 # Matches Pacman's speed (cell_size * 0.1)

    @abstractmethod
    def get_path(self, maze, pacman_pos):
        """Return next (idx, idy) cell to move to, or None to stay still."""
        ...


class BlueGhost(Ghost):
    def __init__(self, coordinates):
        super().__init__(coordinates)
        self.sprite = arcade.Sprite("src/assets/blueghost.png", scale=0.1)

    def get_path(self, maze, pacman_pos):
        gx, gy = self.coordinates
        options = []
        if not maze.maze[gy][gx] & directions.UP and gy > 0:
            options.append((gx, gy - 1))
        if not maze.maze[gy][gx] & directions.DOWN and gy < len(maze.maze) - 1:
            options.append((gx, gy + 1))
        if not maze.maze[gy][gx] & directions.LEFT and gx > 0:
            options.append((gx - 1, gy))
        if not maze.maze[gy][gx] & directions.RIGHT and gx < len(maze.maze[0]) - 1:
            options.append((gx + 1, gy))
        
        if not options:
            return self.coordinates # Stay still if trapped
        return random.choice(options)


class PinkGhost(Ghost):
    def __init__(self, coordinates):
        super().__init__(coordinates)
        self.sprite = arcade.Sprite("src/assets/pinkghost.png", scale=0.1)

    def get_path(self, maze, pacman_pos):
        gx, gy = self.coordinates
        options = []
        if not maze.maze[gy][gx] & directions.UP and gy > 0:
            options.append((gx, gy - 1))
        if not maze.maze[gy][gx] & directions.DOWN and gy < len(maze.maze) - 1:
            options.append((gx, gy + 1))
        if not maze.maze[gy][gx] & directions.LEFT and gx > 0:
            options.append((gx - 1, gy))
        if not maze.maze[gy][gx] & directions.RIGHT and gx < len(maze.maze[0]) - 1:
            options.append((gx + 1, gy))
        
        if not options:
            return self.coordinates
        return random.choice(options)


class RedGhost(Ghost):
    def __init__(self, coordinates):
        super().__init__(coordinates)
        self.sprite = arcade.Sprite("src/assets/redghost.png", scale=0.1)

    def get_path(self, maze, pacman_pos):
        gx, gy = self.coordinates
        options = []
        if not maze.maze[gy][gx] & directions.UP and gy > 0:
            options.append((gx, gy - 1))
        if not maze.maze[gy][gx] & directions.DOWN and gy < len(maze.maze) - 1:
            options.append((gx, gy + 1))
        if not maze.maze[gy][gx] & directions.LEFT and gx > 0:
            options.append((gx - 1, gy))
        if not maze.maze[gy][gx] & directions.RIGHT and gx < len(maze.maze[0]) - 1:
            options.append((gx + 1, gy))
        
        if not options:
            return self.coordinates
        return random.choice(options)


class OrangeGhost(Ghost):
    def __init__(self, coordinates):
        super().__init__(coordinates)
        self.sprite = arcade.Sprite("src/assets/orangeghost.png", scale=0.1)

    def get_path(self, maze, pacman_pos):
        gx, gy = self.coordinates
        options = []
        if not maze.maze[gy][gx] & directions.UP and gy > 0:
            options.append((gx, gy - 1))
        if not maze.maze[gy][gx] & directions.DOWN and gy < len(maze.maze) - 1:
            options.append((gx, gy + 1))
        if not maze.maze[gy][gx] & directions.LEFT and gx > 0:
            options.append((gx - 1, gy))
        if not maze.maze[gy][gx] & directions.RIGHT and gx < len(maze.maze[0]) - 1:
            options.append((gx + 1, gy))
        
        if not options:
            return self.coordinates
        return random.choice(options)


class directions(IntFlag):
    UP = 1
    RIGHT = 2
    DOWN = 4
    LEFT = 8


class Point:
    def __init__(self, x, y):
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
        self.cell_positions = [[] for i in range(len(self.maze.maze))]
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
        
        # spawn ghosts in the four corners of the maze (using grid indices)
        top_left_cell = (0, 0)
        top_right_cell = (len(self.maze.maze[0]) - 1, 0)
        bottom_left_cell = (0, len(self.maze.maze) - 1)
        bottom_right_cell = (len(self.maze.maze[0]) - 1, len(self.maze.maze) - 1)

        self.ghosts = []
        self.ghost_list = arcade.SpriteList()
        
        # Create ghosts and assign initial pixel positions
        p = PinkGhost(top_left_cell)
        px, py = self.cell_positions[0][0]
        p.sprite.center_x, p.sprite.center_y = px, py
        p.target_x, p.target_y = px, py
        self.ghost_list.append(p.sprite)

        r = RedGhost(top_right_cell)
        px, py = self.cell_positions[0][-1]
        r.sprite.center_x, r.sprite.center_y = px, py
        r.target_x, r.target_y = px, py
        self.ghost_list.append(r.sprite)

        o = OrangeGhost(bottom_left_cell)
        px, py = self.cell_positions[-1][0]
        o.sprite.center_x, o.sprite.center_y = px, py
        o.target_x, o.target_y = px, py
        self.ghost_list.append(o.sprite)

        b = BlueGhost(bottom_right_cell)
        px, py = self.cell_positions[-1][-1]
        b.sprite.center_x, b.sprite.center_y = px, py
        b.target_x, b.target_y = px, py
        self.ghost_list.append(b.sprite)

        self.ghosts = [p, r, o, b]

        

    def init_pacman_possition(self):
        x, y = self.cell_positions[len(self.cell_positions) // 2][len(self.cell_positions) // 2]
        return Point(x, y)

    def load_pacman_frames(self):
        return [
            arcade.load_texture("src/assets/pacman_closed.png"),
            arcade.load_texture("src/assets/pacman_half.png"),
            arcade.load_texture("src/assets/pacman_open.png"),
        ]

    def map_maze_coordinates(self):
        num_rows = len(self.maze.maze)
        num_cols = len(self.maze.maze[0])

        maze_pixel_w = num_cols * self.cell_size
        maze_pixel_h = num_rows * self.cell_size

        start_x = (self.width - maze_pixel_w) // 2 + self.cell_size // 2
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
            directions.UP: directions.DOWN,
            directions.DOWN: directions.UP,
            directions.LEFT: directions.RIGHT,
            directions.RIGHT: directions.LEFT
        }
        result = True
        if (x, y) in self.points_cord:
            idx, idy = self.points_cord[(x, y)]
            if not self.maze.maze[idy][idx] & self.next_key:
                self.current_key = self.next_key
            result = not self.maze.maze[idy][idx] & self.current_key

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
        # --- Pacman Animation ---
        self.pac_man_seconds += delta_time
        if self.pac_man_seconds >= 0.2:
            self.pac_man_frame_index += self.pac_man_next
            if self.pac_man_frame_index == 0 or self.pac_man_frame_index == 2:
                self.pac_man_next *= -1
            self.pac_man_seconds = 0
        if self.can_move():
            self.make_move()

        # --- Ghost Update and Smooth Animation ---
        for ghost in self.ghosts:
            # Check if ghost has reached the center of its target cell
            if abs(ghost.sprite.center_x - ghost.target_x) <= ghost.speed and \
               abs(ghost.sprite.center_y - ghost.target_y) <= ghost.speed:
                
                # Snap to exact target to prevent floating point drift
                ghost.sprite.center_x = ghost.target_x
                ghost.sprite.center_y = ghost.target_y

                # Ask AI for the next grid cell to move to
                next_cell = ghost.get_path(self.maze, self.pac_man_possition)
                
                if next_cell:
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
                        arcade.draw_line(x - self.cell_size // 2, y + self.cell_size // 2, x + self.cell_size // 2, y + self.cell_size // 2, self.wall_color, line_width=5)
                    if self.maze.maze[idy][idx] & directions.RIGHT:
                        arcade.draw_line(x + self.cell_size // 2, y - self.cell_size // 2, x + self.cell_size // 2, y + self.cell_size // 2, self.wall_color, line_width=5)
                    if self.maze.maze[idy][idx] & directions.LEFT:
                        arcade.draw_line(x - self.cell_size // 2, y - self.cell_size // 2, x - self.cell_size // 2, y + self.cell_size // 2, self.wall_color, line_width=5)
                    if self.maze.maze[idy][idx] & directions.DOWN:
                        arcade.draw_line(x - self.cell_size // 2, y - self.cell_size // 2, x + self.cell_size // 2, y - self.cell_size // 2, self.wall_color, line_width=5)
                    if (x, y) not in self.visited_cells and (idx, idy) not in self.forbiden_cells:
                        arcade.draw_point(x, y, arcade.color.BABY_BLUE_EYES, size=4)
            
            # Draw ghosts
            self.ghost_list.draw()

            # Pacman rendering
            px, py = self.pac_man_possition
            if (px, py) in self.points_cord:
                self.visited_cells.add((px, py))
            pac_man = arcade.XYWH(px, py, 40, 40)
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