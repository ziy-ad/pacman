import arcade
from .pacman import Point
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .main_menu import MainMenu
class speed_view(arcade.View):
    def __init__(self, pause_menu: "MainMenu") -> None:
        super().__init__( background_color=arcade.color.BLACK)
        self.start_x = int((self.width // 2) - 200 )
        self.cy = self.height // 2
        self.pause_menu = pause_menu
        self.end_x = int(self.start_x + 400)
        self.pac_man_position = Point(self.start_x, self.cy)
        self.pac_man_frames = self.load_pacman_frames()
        self.pac_man_seconds = 0
        self.pac_man_next = 1
        self.pac_man_frame_index = 0
        self.pac_man = self.pac_man_frames[self.pac_man_frame_index]

    def load_pacman_frames(self):
        return  [
            arcade.load_texture("src/assets/pacman_closed.png"),
            arcade.load_texture("src/assets/pacman_half.png"),
            arcade.load_texture("src/assets/pacman_open.png"),
        ]
    def on_draw(self):
        self.clear()
        lines = []
        for x in range(self.start_x,self.end_x, 30):
            lines += [(x + 20, self.cy) ]
        arcade.draw_lines(lines, color=arcade.color.RED, line_width=5)
        arcade.draw_texture_rect(
            self.pac_man_frames[self.pac_man_frame_index],
            arcade.XYWH(
                    self.pac_man_position.x ,
                    self.pac_man_position.y,
                    40,
                    40)
            )

    def on_update(self, delta_time):
        self.pac_man_seconds += delta_time
        if self.pac_man_seconds >= 0.2:
            self.pac_man_frame_index += self.pac_man_next
            if self.pac_man_frame_index == 0 or self.pac_man_frame_index == 2:
                self.pac_man_next *= -1
            self.pac_man_seconds = 0
        if self.pac_man_position.x < self.end_x:
            self.pac_man_position.x += int(self.pause_menu.game_view.cell_size * self.pause_menu.game_view.speed)

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.UP:
            self.pac_man_position.x = self.start_x
            self.pause_menu.game_view.speed += 0.01
        if symbol == arcade.key.DOWN:
            self.pac_man_position.x = self.start_x
            self.pause_menu.game_view.speed -= 0.01
        if symbol == arcade.key.RETURN or symbol == arcade.key.ESCAPE:
            self.window.show_view(self.pause_menu)