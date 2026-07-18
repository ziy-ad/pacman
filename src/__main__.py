import arcade
from mazegenerator import MazeGenerator
from enum import IntFlag
from rich.traceback import install
install()

class directions(IntFlag):
    N = 1
    E = 2
    W = 4
    S = 8


class Point:
    def __init__(self,x, y):
        self.x = 0
        self.y = 0
    def __iter__(self):
        for i in [self.x, self.y]:
            yield i

class Pacman(arcade.Window):
    def __init__(self, maze: MazeGenerator):
        super().__init__(fullscreen=True)
        self.maze = maze
        self.maze.generate()
        self.camera = arcade.Camera2D()
        self.cx, self.cy = self.camera.position
        self.cell_size = 60
        self.pac_man_frames = [
            arcade.load_texture("src/assets/pacman_closed.png"),
            arcade.load_texture("src/assets/pacman_half.png"),
            arcade.load_texture("src/assets/pacman_open.png"),
        ]
        self.cell_positions = [[] for i in  range(len(self.maze.maze))]
        y = 900
        for idx, row in enumerate(self.maze.maze):
            x = self.width // 2 - len(row) * 35
            for cell in row:
                self.cell_positions[idx] += [(x,y)]
                x += self.cell_size
            y -= self.cell_size
                
        self.pac_man_seconds = 0
        self.pac_man_next = 1
        self.pac_man_frame_index = 0
        self.pac_man_possition = Point(len(self.cell_positions) // 2, len(self.cell_positions) // 2 ) 
    def on_update(self, delta_time):
        self.pac_man_seconds += delta_time
        if self.pac_man_seconds >= 0.2:
            self.pac_man_frame_index += self.pac_man_next
            if self.pac_man_frame_index == 0 or self.pac_man_frame_index == 2:
                self.pac_man_next *= -1
            self.pac_man_seconds = 0
    def on_draw(self):
        self.clear()
        with self.camera.activate():
            for idy, row in enumerate(self.cell_positions):
                for idx, cell in enumerate(row):
                    x, y = cell
                    if self.maze.maze[idy][idx] & directions.N:
                        arcade.draw_line(x, y + self.cell_size, x + self.cell_size, y + self.cell_size , arcade.color.APRICOT, line_width=15)
                    if self.maze.maze[idy][idx] & directions.E:
                        arcade.draw_line(x + self.cell_size, y , x + self.cell_size, y + self.cell_size, arcade.color.APRICOT, line_width=15)
                    if self.maze.maze[idy][idx] & directions.S:
                        arcade.draw_line(x , y, x  , y + self.cell_size, arcade.color.APRICOT, line_width=15)
                    if self.maze.maze[idy][idx] & directions.W:
                        arcade.draw_line(x, y , x + self.cell_size, y , arcade.color.APRICOT, line_width=15)

                    arcade.draw_point(x + (self.cell_size // 2), y + (self.cell_size // 2), arcade.color.BABY_BLUE_EYES)

            px, py = self.pac_man_possition
            x, y =  [i + (self.cell_size // 2) for i in self.cell_positions[py][px]]
            pac_man = arcade.XYWH(x , y, 20, 20)
            arcade.draw_texture_rect(self.pac_man_frames[self.pac_man_frame_index], pac_man)
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.cx -= dx
        self.cy -= dy
        self.camera = (self.cx, self.cy)
    
    def on_key_press(self, symbol, modifiers):
        x, y = self.pac_man_possition
        if symbol == arcade.key.RIGHT and not self.maze.maze[y][x] & directions.E :
            self.pac_man_possition.x += 1
        if symbol == arcade.key.LEFT and not self.maze.maze[y][x] & directions.W:
            self.pac_man_possition.x -= 1
        if symbol == arcade.key.DOWN and not self.maze.maze[y][x] & directions.S:
            self.pac_man_possition.y += 1
        if symbol == arcade.key.UP and not self.maze.maze[y][x] & directions.N:
            self.pac_man_possition.y -= 1


def main():
    pacman = Pacman(MazeGenerator())
    pacman.run()



if __name__ == "__main__":
    main()