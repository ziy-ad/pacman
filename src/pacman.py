from enum import IntFlag
from pyglet.libs.x11.xlib import False_, True_
from rich import print
import arcade
from mazegenerator import MazeGenerator
from pyglet.window.key import KeyStateHandler
from rich.traceback import install

install()

class directions(IntFlag):
    N = 1
    E = 2
    S = 4
    W = 8


class Point:
    def __init__(self,x, y):
        self.x = x
        self.y = y
    def __iter__(self):
        yield self.x
        yield self.y

class Parser:
    def __init__(self, validated_data):
        self.highscore_filename = validated_data["highscore_filename"]
        self.lives = validated_data["lives"] 
        self.pacgum = validated_data["pacgum"] 
        self.points_per_pacgum = validated_data["points_per_pacgum"] 
        self.points_per_super_pacgum = validated_data["points_per_super_pacgum"] 
        self.points_per_ghost = validated_data["points_per_ghost"] 
        self.seed = validated_data["seed"] 
        self.level_max_time = validated_data["level_max_time"] 
        self.levels = validated_data["levels"] 


class Pacman(arcade.Window):
    def __init__(self, parser: Parser):
        super().__init__(fullscreen=True)
        self.parser = parser
        self.flag = True

        self.maze = MazeGenerator(seed=self.parser.seed)
        self.maze.generate(seed=self.parser.seed)
        self.camera = arcade.Camera2D()
        self.cx, self.cy = self.camera.position
        self.cell_size = 60
        self.cell_positions = [[] for i in  range(len(self.maze.maze))]
        self.forbiden_cells = set()
        self.to_move = 5
        y = 900
        self.points_cord = {}
        for idy, row in enumerate(self.maze.maze):
            x = self.width // 2 - len(row) * 35
            for idx, _ in enumerate(row):
                if self.maze.maze[idy][idx] == 15:
                    self.forbiden_cells.add((idx, idy))
                else:
                    self.points_cord.update({(x,y): (idx, idy)})
                self.cell_positions[idy] += [(x,y)]

                x += self.cell_size
            y -= self.cell_size
    
        self.pac_man_frames = [
            arcade.load_texture("src/assets/pacman_closed.png"),
            arcade.load_texture("src/assets/pacman_half.png"),
            arcade.load_texture("src/assets/pacman_open.png"),
        ]
        self.pac_man_seconds = 0
        self.pac_man_next = 1
        self.pac_man_frame_index = 0
        x, y = self.cell_positions[len(self.cell_positions) // 2][len(self.cell_positions) // 2]
        print(self.points_cord)
        self.pac_man_possition = Point(x, y)
        self.points_set = set()
        self.keys = KeyStateHandler()
        self.push_handlers(self.keys)
        self.current = directions.S
        self.last_key = directions.S
        self.pac_man = self.pac_man_frames[self.pac_man_next]

    def can_move(self, dir: directions):
        x, y = self.pac_man_possition
        result = True
        if (x, y) in self.points_cord:
            idx, idy = self.points_cord[(x, y)]
            result =  not self.maze.maze[idy][idx] & dir
        self.current = dir if result else self.current
        return result

    def make_move(self):
        if self.last_key == directions.E and self.can_move(directions.E):
            self.pac_man_possition.x += self.to_move
            self.current = directions.E
        elif self.last_key == directions.W and self.can_move(directions.W):
            self.pac_man_possition.x -= self.to_move
            self.current = directions.W            
        elif self.last_key == directions.S and self.can_move(directions.S):
            self.pac_man_possition.y -= self.to_move
            self.current = directions.S         
        elif self.last_key == directions.N and self.can_move(directions.N):
            self.pac_man_possition.y += self.to_move
            self.current = directions.N

    def check_last_key(self):
        if (self.keys[arcade.key.RIGHT] or self.keys[arcade.key.D]):
            self.last_key = directions.E
        elif (self.keys[arcade.key.LEFT] or self.keys[arcade.key.A]):
            self.last_key = directions.W            
        elif (self.keys[arcade.key.DOWN] or self.keys[arcade.key.S]):
            self.last_key = directions.S            
        elif (self.keys[arcade.key.UP] or self.keys[arcade.key.W]):
            self.last_key = directions.N

    def on_update(self, delta_time):
        self.pac_man_seconds += delta_time
        if self.pac_man_seconds >= 0.2:
            self.pac_man_frame_index += self.pac_man_next
            if self.pac_man_frame_index == 0 or self.pac_man_frame_index == 2:
                self.pac_man_next *= -1
            self.pac_man_seconds = 0
        self.check_last_key()
        self.make_move()

    def get_pac_man_frame(self):
        match self.last_key:
            case directions.N:
                return self.pac_man_frames[self.pac_man_frame_index].rotate_270()
            case directions.E:
                return self.pac_man_frames[self.pac_man_frame_index]
            case directions.S:
                return self.pac_man_frames[self.pac_man_frame_index].rotate_90()
            case directions.W:
                return self.pac_man_frames[self.pac_man_frame_index].flip_horizontally()




    def on_draw(self):
        self.clear()
        with self.camera.activate():
            text = arcade.Text(f"score: {len(self.points_set)}", 40, self.height - 100, arcade.color.ALLOY_ORANGE, font_size=30)
            text.draw()
            for idy, row in enumerate(self.cell_positions):
                for idx, cell in enumerate(row):
                    x, y = cell
                    if self.maze.maze[idy][idx] & directions.N:
                        arcade.draw_line(x - self.cell_size // 2, y + self.cell_size // 2, x + self.cell_size // 2, y + self.cell_size // 2 , arcade.color.GOLD_FUSION, line_width=15)
                    if self.maze.maze[idy][idx] & directions.E:
                        arcade.draw_line(x + self.cell_size // 2, y - self.cell_size // 2 , x + self.cell_size // 2, y + self.cell_size // 2, arcade.color.GOLD_FUSION, line_width=15)
                    if self.maze.maze[idy][idx] & directions.W:
                        arcade.draw_line(x - self.cell_size // 2, y - self.cell_size // 2, x - self.cell_size // 2 , y + self.cell_size // 2, arcade.color.GOLD_FUSION, line_width=15)
                    if self.maze.maze[idy][idx] & directions.S:
                        arcade.draw_line(x - self.cell_size // 2, y - self.cell_size // 2 , x + self.cell_size // 2, y - self.cell_size // 2 , arcade.color.GOLD_FUSION, line_width=15)
                    if (idx, idy) not in self.points_set and (idx, idy) not in self.forbiden_cells:
                        arcade.draw_point(x, y , arcade.color.BABY_BLUE_EYES, size=4)
            px, py = self.pac_man_possition
            self.points_set.add((px, py))
            pac_man = arcade.XYWH(px , py, 40, 40)
            arcade.draw_texture_rect(self.get_pac_man_frame(), pac_man)
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.cx -= dx
        self.cy -= dy
        self.camera.position = (self.cx, self.cy)
    
    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.F:
            self.set_fullscreen(not self.fullscreen)
