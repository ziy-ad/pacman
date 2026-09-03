from enum import IntFlag
from rich import print
from .load_config import ConfigData
import arcade
from mazegenerator import MazeGenerator
from rich.traceback import install
from typing import TYPE_CHECKING
from PIL import Image, ImageFilter

if TYPE_CHECKING:
    from .main_menu import MainMenu


install()

class directions(IntFlag):
    UP = 1
    RIGHT = 2
    DOWN = 4
    LEFT = 8


MOVE_DIRECTIONS = {
    directions.UP:    ('y', 1),
    directions.DOWN:  ('y', -1),
    directions.RIGHT: ('x', 1),
    directions.LEFT:  ('x', -1),
}


class Point:
    def __init__(self,x, y):
        self.x = x
        self.y = y
    def __repr__(self) -> str:
        return f"x = {self.x} - y = {self.y}"
    def __iter__(self):
        yield self.x
        yield self.y
    def __add__(self, other):
        x, y = other
        return Point(self.x + x, self.y + y) 

class Pacman(arcade.View):
    def __init__(self, parser: ConfigData):
        self.parser = parser
        self.wall_color = arcade.color.BLUE
        super().__init__(background_color=arcade.color.PINK_SHERBET)

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
        self.visited_cells = set()
        self.current_key = directions.UP
        self.next_key = directions.UP
        # speed mechanism
        self.current_index = Point(self.pac_man_possition.x, self.pac_man_possition.y)
        self.speed = 0.01
        self.pause_menu: MainMenu | None = None

        # levels
        self.level_index = 0 
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
        move = self.cell_size * self.speed
        MOVE_VECTORS = {
            directions.UP:(0,1),
            directions.DOWN:(0,-1),
            directions.RIGHT:(1,0),
            directions.LEFT:(-1,0)
        }
        dx, dy = MOVE_VECTORS[self.current_key]
        step = self.cell_size * self.speed
    
        if dx != 0:
            target = self.current_index.x + dx * self.cell_size
            new_x = self.pac_man_possition.x + dx * step
            self.pac_man_possition.x = min(new_x, target) if dx > 0 else max(new_x, target)
            if self.pac_man_possition.x == target:
                self.current_index.x = target

        if dy != 0:
            target = self.current_index.y + dy * self.cell_size
            new_y = self.pac_man_possition.y + dy * step
            self.pac_man_possition.y = min(new_y, target) if dy > 0 else max(new_y, target)
            if self.pac_man_possition.y == target:
                self.current_index.y = target

    def on_update(self, delta_time):
        self.pac_man_seconds += delta_time
        if self.pac_man_seconds >= 0.2:
            self.pac_man_frame_index += self.pac_man_next
            if self.pac_man_frame_index == 0 or self.pac_man_frame_index == 2:
                self.pac_man_next *= -1
            self.pac_man_seconds = 0
        if self.can_move():
            self.make_move()

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
    def setup(self):
        px, py = self.pac_man_possition
        self.visited_cells.add((px, py))

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
                        arcade.draw_point(x, y , arcade.color.DARK_BLUE, size=4)
            px, py = self.pac_man_possition
            if (px, py) in self.points_cord:
                self.visited_cells.add((px, py))
            arcade.draw_texture_rect(self.get_pac_man_frame(), arcade.XYWH(px , py, 40, 40))

    
    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.F:
            self.window.set_fullscreen(not self.window.fullscreen)            
        if symbol == arcade.key.RIGHT or symbol == arcade.key.D:
            self.next_key = directions.RIGHT
        if symbol == arcade.key.LEFT or symbol == arcade.key.A:
            self.next_key = directions.LEFT            
        if symbol == arcade.key.DOWN or symbol == arcade.key.S:
            self.next_key = directions.DOWN            
        if symbol == arcade.key.UP or symbol == arcade.key.W:
            self.next_key = directions.UP
        if symbol == arcade.key.ESCAPE:
            if self.pause_menu is not None:
                image = arcade.get_image()
                image = image.filter(ImageFilter.GaussianBlur(radius=5))
                self.pause_menu.image = image
                self.window.show_view(self.pause_menu)