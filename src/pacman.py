from enum import IntFlag, Enum
from rich import print
from .load_config import ConfigData
import arcade
from mazegenerator import MazeGenerator
from rich.traceback import install
import time
from .ghosts_algorithm import *
from .score_tracker import score_board
from pathlib import Path
from .ghosts_algorithm import *
install()

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
        self.cell_size = 30
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
        self.caught_by_ghost = False
        self.catch_freeze_time = 0.0
        self.catch_freeze_duration = 1.2
        self.score_path = Path(__file__).resolve().parent.parent / "highscore.json"
        self.scoreboard = score_board(str(self.score_path))
        self.score = 0
        self.edible = False
        self.edible_duration = 0.0
        self.edible_time = 0.0
        self.speed = 0.05
        self.current_level = 0
        self.lives = self.parser.lives
        self.scoreboard.load_scores()
        # spawn the ghosts in the corners of the maze
        self.corner_grid_coords = [
            (0, 0),
            (len(self.maze.maze[0]) - 1, 0),
            (0, len(self.maze.maze) - 1),
            (len(self.maze.maze[0]) - 1, len(self.maze.maze) - 1),
        ]
        self.positions = [self.cell_positions[0][0], self.cell_positions[0][-1], self.cell_positions[-1][0], self.cell_positions[-1][-1]]
        self.ghost_name = ["PinkGhost", "RedGhost", "OrangeGhost", "BlueGhost"]
        self.ghost_speed = self.speed
        self.set_ghosts()

    def maze_init(self):
        random_seed = random.randint(0, 1000000)
        self.maze = MazeGenerator(seed=random_seed, size=(self.parser.levels[self.current_level]["width"], self.parser.levels[self.current_level]["height"]))
        self.maze.generate(seed=random_seed)
        self.cell_positions = [[] for i in  range(len(self.maze.maze))]
        self.forbiden_cells = set()
        self.points_cord = {}
        self.map_maze_coordinates()
        self.pac_man_possition = self.init_pacman_possition()
        self.visited_cells = set()
        self.pac_man_grid = (len(self.maze.maze[0]) // 2, len(self.maze.maze) // 2)
        self.used_cells = set()
        self.reset(death=True)

    def set_main_menu(self, main_menu):
        self.main_menu = main_menu

    def set_ghosts(self):
        self.ghosts = {}
        self.ghost_list = arcade.SpriteList()

        self.start_time = None
        self.pause_start = None
        self.corner_grid_coords = [
                    (0, 0),
                    (len(self.maze.maze[0]) - 1, 0),
                    (0, len(self.maze.maze) - 1),
                    (len(self.maze.maze[0]) - 1, len(self.maze.maze) - 1),
                ]
        for position, name in zip(self.corner_grid_coords, self.ghost_name):
            ghost_class = globals()[name]
            ghost = ghost_class(position, self.maze.maze)
            gx, gy = position
            ghost.center_x, ghost.center_y = self.cell_positions[gy][gx]
            ghost.target_x, ghost.target_y = self.cell_positions[gy][gx]
            self.ghost_list.append(ghost)
            self.ghosts[name] = ghost

    def reset(self, death=False):
        self.set_ghosts()
        if not death:
            self.visited_cells.clear()
        if death:
            self.start_time = time.time()
            self.pause_start = None
        self.pac_man_possition = self.init_pacman_possition()
        self.caught_by_ghost = False

    def pause(self):
        if self.start_time is not None and self.pause_start is None:
            self.pause_start = time.time()

    def resume(self):
        if self.pause_start is not None and self.start_time is not None:
            self.start_time += time.time() - self.pause_start
            self.pause_start = None


    def init_pacman_possition(self):
        x, y = self.cell_positions[len(self.cell_positions) // 2][len(self.cell_positions) // 2]
        self.current_index = Point(x, y)
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
        if self.start_time:
            if time.time() - self.start_time >= self.parser.level_max_time:
                from .main_menu import GameOverView
                self.window.show_view(GameOverView(self.window, self.scoreboard, self.score, self))
        if self.edible:
            self.edible_duration += delta_time
            if self.edible_duration >= self.edible_time:
                self.edible = False
                self.ghost_speed = self.ghost_speed * 1.2
                self.edible_duration = 0.0
                self.edible_time = 0.0

        if self.caught_by_ghost:
            self.catch_freeze_time += delta_time
            if self.catch_freeze_time >= self.catch_freeze_duration:
                self.lives -= 1
                if self.lives > 0:
                    self.reset(death=True)
                else:
                    self.lives = self.parser.lives
                    from .main_menu import GameOverView
                    # pass scoreboard and final score, plus this pacman instance
                    self.window.show_view(GameOverView(self.window, self.scoreboard, self.score, self))
            return
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



        catch_distance = self.cell_size * 0.5
        for ghost in self.ghosts.values():
            if abs(ghost.center_x - px) <= catch_distance and \
            abs(ghost.center_y - py) <= catch_distance:
                if self.edible:
                    ghost.eatable = True
                    self.score += self.parser.points_per_ghost
                else:
                    if not ghost.eatable:
                        self.catch_freeze_time = 0.0
                        self.caught_by_ghost = True
                        break

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
            text = arcade.Text(f"score: {self.score}", 40, self.height - 100, arcade.color.ALLOY_ORANGE, font_size=30)
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
                        if self.points_cord[(x, y)] in self.corner_grid_coords:
                            arcade.draw_point(x, y , arcade.color.YELLOW, size=8)
                        else:
                            arcade.draw_point(x, y , arcade.color.BABY_BLUE_EYES, size=4)

                px, py = self.pac_man_possition
                if (px, py) in self.points_cord and (px, py) not in self.visited_cells:
                    self.visited_cells.add((px, py))
                    if self.points_cord[(px, py)] in self.corner_grid_coords:
                        self.score += self.parser.points_per_super_pacgum
                        self.edible = True
                        self.ghost_speed = self.ghost_speed * 0.8
                        self.edible_time += 5
                    else:
                        self.score += self.parser.points_per_pacgum

            px, py = self.pac_man_possition
            if (px, py) in self.points_cord:
                self.visited_cells.add((px, py))
            pac_man = arcade.XYWH(px , py, 20, 20)
            arcade.draw_texture_rect(self.get_pac_man_frame(), pac_man)
            
            # print(len(self.visited_cells), len(self.forbiden_cells))
            if len(self.visited_cells) + len(self.forbiden_cells) == len(self.points_cord):
                if self.current_level + 1 < len(self.parser.levels):
                    self.current_level += 1
                    self.maze_init()
                else:
                    from .main_menu import GameOverView
                    # pass scoreboard and final score, plus this pacman instance
                    self.window.show_view(GameOverView(self.window, self.scoreboard, self.score, self))

            self.ghost_list.draw()

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.cx -= dx
        self.cy -= dy
        self.camera.position = (self.cx, self.cy)
    
    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.F:
            self.window.set_fullscreen(not self.window.fullscreen)            
        if symbol == arcade.key.RIGHT or symbol == arcade.key.D:
            self.next_key = directions.RIGHT
        if symbol == arcade.key.ESCAPE:
            self.pause()
            self.window.show_view(self.main_menu)
        elif symbol == arcade.key.LEFT or symbol == arcade.key.A:
            self.next_key = directions.LEFT            
        elif symbol == arcade.key.DOWN or symbol == arcade.key.S:
            self.next_key = directions.DOWN            
        elif symbol == arcade.key.UP or symbol == arcade.key.W:
            self.next_key = directions.UP
