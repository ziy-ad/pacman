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
from .ghosts_algorithm import Ghost_modes, Ghost
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

class CheatMode:
    def __init__(self, default_val=False):
        self.invincible = default_val
        self.ghost_freeze = default_val
        self.level_skip = default_val
        self.show_ghost_path = default_val


class Pacman(arcade.View):
    def __init__(self, parser: ConfigData):
        self.parser = parser
        self.wall_color = arcade.color.BLUE
        super().__init__(background_color=arcade.color.DARK_SLATE_BLUE)
        self.change_ghost_texture = False
        # maze config
        self.maze = MazeGenerator(seed=self.parser.seed, size=(self.parser.levels[0]["width"], self.parser.levels[0]["height"]))
        self.maze.generate(seed=self.parser.seed)
        # camera settings
        self.camera = arcade.Camera2D()
        self.cx, self.cy = self.camera.position
        # cell settings
        self.cell_size = int(min(self.width  / len(self.maze.maze[0]), (self.height - 120)  / len(self.maze.maze)))
        self.cell_positions = [[] for i in  range(len(self.maze.maze))]
        self.forbiden_cells = set()
        self.points_cord = {}
        self.map_maze_coordinates()
        self.lives = self.parser.lives

        self.assets_path = Path(__file__).resolve().parent / "assets"
        self.live_pac_man = arcade.load_texture(self.assets_path / "live_pacman.png")
        self.dead_pac_man = arcade.load_texture(self.assets_path / "dead_pacman.png")
        self.live_textures = []
        self.set_pac_man_lives()
            
        arcade.load_font(str(self.assets_path / "Silkscreen-Regular.ttf"))
        arcade.load_font(str(self.assets_path / "Silkscreen-Bold.ttf"))
        arcade.load_font(str(self.assets_path / "VT323-Regular.ttf"))
        arcade.load_font(str(self.assets_path / "Rowdies-Regular.ttf"))
        arcade.load_font(str(self.assets_path / "Rowdies-Bold.ttf"))
        

        self.label_level = arcade.Text(
            "LEVEL",
            self.width - 60,
            self.height - 50,
            arcade.color.WHITE,
            font_size=18,
            bold=True,
            anchor_x="right",
            font_name="Silkscreen")
        self.game_over = arcade.Text(
            "GAME OVER",
            self.width // 2,
            self.height // 2,
            arcade.color.RED_BROWN,
            font_size=100,
            bold=True,
            anchor_x="center",
            font_name="Silkscreen")

        # Dynamic values (updated as the game runs)
        self.score_text = arcade.Text(
            "000000",
            50,
            self.height - 50,
            arcade.color.YELLOW,
            font_size=20,
            bold=True,
            font_name="Silkscreen")
        self.level_text = arcade.Text(
            "01",
            self.width - 10,
            self.height - 50,
            arcade.color.CYAN,
            font_size=20,
            bold=True,
            anchor_x="right",
            font_name="Silkscreen")
        self.timer = self.parser.level_max_time
        self.timer_text = arcade.Text(
            "01",
            self.width // 2 - 300,
            self.height - 50,
            arcade.color.GREEN_YELLOW,
            font_size=20,
            bold=True,
            anchor_x="center",
            font_name="Silkscreen")

        # pac man settings
        self.pac_man_frames = self.load_pacman_frames() 
        self.pac_man_seconds = 0
        self.cheater = CheatMode()
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
        self.catch_freeze_duration = 2.2
        self.score_path = Path(__file__).resolve().parent.parent / self.parser.highscore_filename
        self.scoreboard = score_board(str(self.score_path))
        self.score = 0
        self.edible = False
        self.edible_duration = 0.0
        self.edible_time = 0.0
        self.speed = 0.05
        self.current_level = 8
        self.inv_start_time = 0.0
        self.inv_freeze_time = 4.0
        self.scoreboard.load_scores()
        self.ghost_list: arcade.SpriteList[Ghost] = arcade.SpriteList()
        # spawn the ghosts in the corners of the maze
        self.corner_grid_coords = [
            (0, 0),
            (len(self.maze.maze[0]) - 1, 0),
            (0, len(self.maze.maze) - 1),
            (len(self.maze.maze[0]) - 1, len(self.maze.maze) - 1),
        ]
        self.ghost_name = ["Pinky", "Blinky", "Clyde", "Inky"]
        self.ghost_speed = self.speed
        self.set_ghosts()
        self.start_time = None
    def set_pac_man_lives(self):
        self.live_textures.clear()
        self.lives = self.parser.lives
        for _ in range(self.lives):
            self.live_textures += [self.live_pac_man]
    def maze_init(self):
        if self.current_level == 0:
            random_seed = self.parser.seed
        else:
            random_seed = random.randint(0, 1000000)
        self.maze = MazeGenerator(seed=random_seed, size=(self.parser.levels[self.current_level]["width"], self.parser.levels[self.current_level]["height"]))
        self.maze.generate(seed=random_seed)
        self.cell_positions = [[] for i in  range(len(self.maze.maze))]
        self.forbiden_cells = set()
        self.points_cord = {}
        self.cell_size = int(min(self.width  / len(self.maze.maze[0]), (self.height - 120)  / len(self.maze.maze)))
        self.map_maze_coordinates()
        self.pac_man_possition = self.init_pacman_possition()
        self.visited_cells = set()
        self.pac_man_grid = (len(self.maze.maze[0]) // 2, len(self.maze.maze) // 2)
        self.set_ghosts()
        self.reset(death=True)
        self.inv_start_time = 0.0
        self.cheater.invincible = False

    def sort_lives(self):
        lives = []
        deaths = []
        for live in self.live_textures:
            if live == self.live_pac_man:
                lives += [live]
            else:
                deaths += [live]
        self.live_textures = lives + deaths 
    def set_main_menu(self, main_menu):
        self.main_menu = main_menu

    def set_ghosts(self):
        self.pause_start = None
        self.corner_grid_coords = [
                    (0, 0),
                    (len(self.maze.maze[0]) - 1, 0),
                    (0, len(self.maze.maze) - 1),
                    (len(self.maze.maze[0]) - 1, len(self.maze.maze) - 1),
                ]
        blinky = None
        self.ghost_list.clear()
        for position, name in zip(self.corner_grid_coords, self.ghost_name):
            ghost_class = globals()[name]
            if name != "Inky":
                ghost = ghost_class(position, self.maze.maze, self.cell_size)
                if name == "Blinky":
                    blinky = ghost
            else:
                if blinky:
                    ghost = ghost_class(position, self.maze.maze, self.cell_size, blinky)

            gx, gy = position
            ghost.center_x, ghost.center_y = self.cell_positions[gy][gx]
            ghost.target_x, ghost.target_y = self.cell_positions[gy][gx]
            self.ghost_list.append(ghost)

    def reset(self, death=False):
        if not death:
            self.visited_cells.clear()
            for ghost in self.ghost_list:
                ghost.reset(self.cell_positions)
        if death:
            # self.start_time = time.time()
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
        # Use separate midpoints for rows and columns (handles non-square mazes)
        mid_row = len(self.cell_positions) // 2
        mid_col = len(self.cell_positions[0]) // 2
        x, y = self.cell_positions[mid_row][mid_col]
        self.current_index = Point(x, y)
        return Point(x, y)

    def load_pacman_frames(self):
        frames = [
            arcade.load_texture("src/assets/pacman_closed.png"),
            arcade.load_texture("src/assets/pacman_half.png"),
            arcade.load_texture("src/assets/pacman_open.png"),
        ]
        directions_ = [directions.RIGHT, directions.UP, directions.DOWN, directions.LEFT]
        all_frames = {}
        for dir in directions_:
            all_frames.setdefault(dir, [])
            for frame in frames:
                match dir:
                    case directions.UP:
                        all_frames[dir] += [frame.rotate_270()]
                    case directions.RIGHT:
                        all_frames[dir] += [frame]
                    case directions.DOWN:
                        all_frames[dir] += [frame.rotate_90()]
                    case directions.LEFT:
                        all_frames[dir] += [frame.flip_horizontally()]
        return all_frames

    def map_maze_coordinates(self):
        num_rows = len(self.maze.maze)
        num_cols = len(self.maze.maze[0])

        # Total pixel size of the maze grid
        maze_pixel_w = num_cols * self.cell_size
        maze_pixel_h = num_rows * self.cell_size

        # Top-left cell center, so the whole grid is centered on the window
        start_x = (self.width  - maze_pixel_w) // 2 + self.cell_size // 2
        start_y = (((self.height - 80) + maze_pixel_h) // 2 - self.cell_size // 2) 

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
            result =  not self.maze.maze[idy][idx] & self.current_key
            if not self.maze.maze[idy][idx] & self.next_key:
                self.current_key = self.next_key

        if self.current_key == directions_oposit[self.next_key]:
            self.current_key = self.next_key
        return result
    def draw_ghosts_path(self):
        colors = {Inky: arcade.color.SKY_BLUE, Blinky: arcade.color.RED, Clyde: arcade.color.ORANGE, Pinky: arcade.color.PINK}
        for ghost in self.ghost_list:
            start = ghost.center_x, ghost.center_y
            if not ghost.path:
                continue
            for idx, cell in enumerate(ghost.path):
                start_x, start_y = start
                nx , ny = cell
                end_x, end_y = self.cell_positions[ny][nx]
                arcade.draw_line(start_x, start_y, end_x, end_y, colors[ghost.__class__], 6)
                if idx == len(ghost.path) - 1:
                    cx = end_x - 8
                    ex = end_x + 8
                    cy = end_y - 8
                    ey = end_y + 8
                    arcade.draw_line(cx, cy, ex, ey, colors[ghost.__class__], 4)
                    arcade.draw_line(ex, cy, cx, ey, colors[ghost.__class__], 4)
                start = (end_x, end_y)
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
    def update_pacman_animation(self, delta_time):
        self.pac_man_seconds += delta_time
        if self.pac_man_seconds >= 0.2:
            self.pac_man_frame_index += self.pac_man_next
            if self.pac_man_frame_index == 0 or self.pac_man_frame_index == 2:
                self.pac_man_next *= -1
            self.pac_man_seconds = 0
    def update_pac_gum_count(self):
        px, py = self.pac_man_possition
        if (px, py) in self.points_cord and (px, py) not in self.visited_cells:
            self.visited_cells.add((px, py))
            if self.points_cord[(px, py)] in self.corner_grid_coords:
                self.score += self.parser.points_per_super_pacgum
                self.change_ghost_texture = True
                self.edible = True
                self.ghost_speed = self.ghost_speed * 0.8
                self.edible_time += 5
            else:
                center_x = len(self.cell_positions) // 2
                center_y = len(self.cell_positions[0]) // 2
                mid = self.cell_positions[center_x][center_y]
                if (px, py) != mid:
                    self.score += self.parser.points_per_pacgum
    def is_touching_ghost(self, ghost: Ghost):
        catch_distance = self.cell_size * 0.4
        px, py = self.pac_man_possition
        return (
            abs(ghost.center_x - px) <= catch_distance and 
            abs(ghost.center_y - py) <= catch_distance
        )
    def check_toucing_ghosts(self):
        for ghost in self.ghost_list:
            is_touching = self.is_touching_ghost(ghost)
            if is_touching and not ghost.eatable:
                ghost.eatable = True
    def handle_edible(self, delta_time):
        if self.edible:
            self.edible_duration += delta_time
            if self.change_ghost_texture:
                for ghost in self.ghost_list:
                    ghost.texture = ghost.fight_mode_texture
                    ghost.mode = Ghost_modes.Fight_mode
            self.check_toucing_ghosts()
            
            if self.edible_duration >= self.edible_time:
                self.edible = False
                self.change_ghost_texture = False
                for ghost in self.ghost_list:
                    ghost.texture = ghost.normal_mode_texture
                    ghost.mode = Ghost_modes.Chase_mode
                self.ghost_speed = self.ghost_speed * 1.2
                self.edible_duration = 0.0
                self.edible_time = 0.0
    def on_update(self, delta_time):
        if self.start_time:
            self.timer = self.parser.level_max_time - (time.time() - self.start_time)
        self.update_pacman_animation(delta_time)
        self.update_pac_gum_count()
        self.handle_edible(delta_time)
        if self.cheater.invincible and self.inv_start_time > 0.0:
            if (time.time() - self.inv_start_time) >= self.inv_freeze_time:
                self.inv_start_time = 0.0
                self.cheater.invincible = False
        if self.start_time:
            if time.time() - self.start_time >= self.parser.level_max_time:
                self.start_time = None
                self.pause()
                self.lives = self.parser.lives
                self.current_level = 0
                self.score = 0
                self.scoreboard.load_scores()
                self.pause()
                self.maze_init()
                from .main_menu import GameOverView
                self.window.show_view(GameOverView(self.window, self.scoreboard, self.score, self))
                return


        if self.caught_by_ghost:
            self.timer += delta_time

            if self.catch_freeze_time <= 0.0:
                self.lives -= 1
                self.live_textures[self.lives] = self.dead_pac_man

            self.catch_freeze_time += delta_time
            if self.catch_freeze_time >= self.catch_freeze_duration:
                self.catch_freeze_time = 0.0
                self.reset(death=self.lives > 0)
                if self.lives > 0:
                    self.inv_start_time = time.time()
                    self.cheater.invincible = True
                else:
                    self.cheater.invincible = False
                    self.inv_start_time = 0.0
                    from .main_menu import GameOverView
                    # pass scoreboard and final score, plus this pacman instance
                    self.start_time = None
                    self.lives = self.parser.lives
                    self.current_level = 0
                    self.score = 0
                    self.scoreboard.load_scores()
                    self.pause()
                    self.maze_init()
                    self.window.show_view(GameOverView(self.window, self.scoreboard, self.score, self))
            return


        if self.can_move():
            self.make_move()

        px, py = self.pac_man_possition
        grid_lookup = self.points_cord.get((px, py))
        if grid_lookup is not None:
            self.pac_man_grid = grid_lookup

        catch_distance = self.cell_size * 0.5
        self.ghost_list.update(
            delta_time,
            cell_positions=self.cell_positions,
            used_cells=self.used_cells,
            ghost_speed=self.ghost_speed,
            current_key=self.current_key,
            start_time=self.start_time,
            pac_man_grid=self.pac_man_grid,
            edible = self.edible,
            cheater=self.cheater
        )
        
        for ghost in self.ghost_list:
            if abs(ghost.center_x - px) <= catch_distance and \
            abs(ghost.center_y - py) <= catch_distance:
                if self.edible and not ghost.eatable:
                    ghost.eatable = True
                    self.score += self.parser.points_per_ghost
                else:
                    if not ghost.eatable and not self.cheater.invincible:
                        self.caught_by_ghost = True
                        break
        self.used_cells.clear()

    def get_pac_man_frame(self):
            return self.pac_man_frames[self.current_key][self.pac_man_frame_index]

    def draw_lives(self):
        start_x = self.width // 2 + 300
        border_x = start_x
        count = 0
        offsit = 0
        for idx, texture in enumerate(self.live_textures):
            if idx < 5:
                rect = arcade.XYWH(start_x, self.height - 50, 30, 30)
                arcade.draw_texture_rect(texture, rect)
                start_x += 30
                if idx + 1 != self.lives:
                    start_x += 5
                count += 1
            else:
                if texture == self.live_pac_man:
                    offsit += 1
        r, g, b, _ = arcade.color.YELLOW
        if offsit > 0:
            arcade.Text(
                f"+{self.lives - 5}",
                start_x + 10,
                self.height - 45,
                (r,g,b, 150),
                20,
                font_name="Rowdies",
                anchor_x="center",
                anchor_y="center",
                bold=True
            ).draw()
        border_x = (start_x - border_x) // 2 + border_x 
        rect = arcade.XYWH(border_x - 15 ,self.height - 50 , 36 * count, 36)

        arcade.draw_rect_outline(rect, (r,g,b, 100), 2)

    def draw_map(self):
        center_x = len(self.cell_positions) // 2
        center_y = len(self.cell_positions[0]) // 2
        mid = self.cell_positions[center_x][center_y]

        self.visited_cells.add(mid)
        for idy, row in enumerate(self.cell_positions):
            for idx, cell in enumerate(row):
                x, y = cell
                start_x = x - self.cell_size // 2
                end_x = x + self.cell_size // 2
                start_y = y - self.cell_size // 2
                end_y = y + self.cell_size // 2

                rect = arcade.rect.XYWH(x, y, self.cell_size, self.cell_size)
                arcade.draw_rect_filled(rect, arcade.color.BLACK)
                if self.maze.maze[idy][idx] & directions.UP:
                    arcade.draw_line(start_x, end_y, end_x, end_y , self.wall_color , line_width=5)
                if self.maze.maze[idy][idx] & directions.RIGHT:
                    arcade.draw_line(end_x, start_y , end_x, end_y, self.wall_color , line_width=5)
                if self.maze.maze[idy][idx] & directions.LEFT:
                    arcade.draw_line(start_x, start_y, start_x, end_y, self.wall_color , line_width=5)
                if self.maze.maze[idy][idx] & directions.DOWN:
                    arcade.draw_line(start_x, start_y , end_x, start_y,self.wall_color , line_width=5)
                if (x, y) not in self.visited_cells and (idx, idy) not in self.forbiden_cells:
                    if self.points_cord[(x, y)] in self.corner_grid_coords:
                        arcade.draw_point(x, y , arcade.color.YELLOW, size=8)
                    else:
                        arcade.draw_point(x, y , arcade.color.BABY_BLUE_EYES, size=4)

    def on_draw(self):
        self.clear()
        
        self.score_text.text = f"{self.score:06d}"
        self.level_text.text = f"{self.current_level + 1:02d}"
        self.timer_text.text = f"{int(self.timer // 60):02d}:{int(self.timer % 60):02d}"
        self.timer_text.draw()
        self.score_text.draw()
        self.label_level.draw()
        self.level_text.draw()
        self.draw_lives()
        with self.camera.activate():
            self.draw_map()
            if self.cheater.show_ghost_path:
                self.draw_ghosts_path()
            px, py = self.pac_man_possition
            pac_man = arcade.XYWH(px , py, self.cell_size * 0.7, self.cell_size * 0.7)
            arcade.draw_texture_rect(self.get_pac_man_frame(), pac_man)

            target_visited_cells = len(self.maze.maze) * len(self.maze.maze[0]) - len(self.forbiden_cells)
            if len(self.visited_cells) >= target_visited_cells or self.cheater.level_skip:
                self.cheater.level_skip = False
                if self.current_level + 1 < len(self.parser.levels):
                    self.current_level += 1
                    self.start_time = time.time()
                    self.pause_start = None
                    self.maze_init()
                else:
                    self.start_time = None
                    self.lives = self.parser.lives
                    self.current_level = 0
                    self.score = 0
                    self.scoreboard.load_scores()
                    self.pause()
                    self.maze_init()
                    from .main_menu import GameOverView
                    # pass scoreboard and final score, plus this pacman instance
                    self.window.show_view(GameOverView(self.window, self.scoreboard, self.score, self))

            self.ghost_list.draw()
            if self.caught_by_ghost and self.lives <= 0:
                r , g, b , _ = arcade.color.BLACK_LEATHER_JACKET
                rect = arcade.rect.XYWH(self.width // 2, self.height // 2 , self.width * 2 , self.height * 2)
                arcade.draw_rect_filled(rect, (r, g, b, 150))
                self.game_over.draw()
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
