import arcade
from .pacman import Pacman, Point

        


class Pause_menu(arcade.View):
    def __init__(self, game_view: Pacman) -> None:
        super().__init__(background_color=arcade.color.BLACK)
        self.game_view = game_view

        self.buttons = ["SPEED", "BACK"]
        self.selected = 0
        self.button_width = 250
        self.button_height = 50
        self.button_spacing = 20

    def on_draw(self):
        self.clear()
        cx = self.width // 2
        cy = self.height // 2

        for i, label in enumerate(self.buttons):
            y = cy - i * (self.button_height + self.button_spacing)
            if i == self.selected:
                bg_color = arcade.color.YELLOW
                text_color = arcade.color.BLACK
            else:
                bg_color = arcade.color.DARK_SLATE_BLUE
                text_color = arcade.color.WHITE
            rect = arcade.XYWH(cx, y, self.button_width, self.button_height)
            arcade.draw_rect_filled(rect, bg_color)

            arcade.draw_text(
                    label,
                    cx, y,
                    text_color,
                    font_size=22,
                    anchor_x="center",
                    anchor_y="center",
                    bold=i == self.selected,
                )

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.UP:
            self.selected = (self.selected - 1) % len(self.buttons)

        elif symbol == arcade.key.DOWN:
            self.selected = (self.selected + 1) % len(self.buttons)

        elif symbol == arcade.key.RETURN:
            if self.buttons[self.selected] == "SPEED":
                self.window.show_view(speed_view(self))
            elif self.buttons[self.selected] == "BACK":
                self.window.show_view(self.game_view)

class speed_view(arcade.View):
    def __init__(self, pause_menu: Pause_menu) -> None:
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
            self.pac_man_position.x += self.pause_menu.game_view.cell_size * self.pause_menu.game_view.speed

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.UP:
            self.pac_man_position.x = self.start_x
            self.pause_menu.game_view.speed += 0.01
        if symbol == arcade.key.DOWN:
            self.pac_man_position.x = self.start_x
            self.pause_menu.game_view.speed -= 0.01
        if symbol == arcade.key.RETURN or symbol == arcade.key.ESCAPE:
            self.window.show_view(self.pause_menu)