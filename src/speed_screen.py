import arcade
from .pacman import Point, Pacman
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .main_menu import MainMenu


class CheatModeView(arcade.View):
    def __init__(self, pause_menu: "MainMenu") -> None:
        super().__init__(background_color=arcade.color.BLACK)
        self.pause_menu = pause_menu
        self.title = "CHEAT MODE"
        self.options = [
            "Increase Speed",
            "Invincibility",
            "Level Skip",
            "Ghost Freeze",
            "Extra Lives",
            "Show Ghosts Path",
            "Back",
        ]
        self.selected = 0
        self.boolean_map = {True: False, False: True}

    def on_draw(self):
        self.clear()
        cx = self.width // 2
        cy = self.height // 2

        arcade.draw_text(
            self.title,
            cx,
            cy + 180,
            arcade.color.YELLOW,
            font_size=34,
            anchor_x="center",
            bold=True,
        )
        arcade.draw_text(
            "Use the menu to choose a cheat. Effects are wired elsewhere.",
            cx,
            cy + 140,
            arcade.color.LIGHT_GRAY,
            font_size=16,
            anchor_x="center",
        )

        for index, label in enumerate(self.options):
            y = cy + 60 - index * 42
            if index == self.selected:
                text_color = arcade.color.BLACK
                bg_color = arcade.color.YELLOW
            else:
                text_color = arcade.color.WHITE
                bg_color = arcade.color.DARK_SLATE_BLUE

            arcade.draw_rect_filled(arcade.XYWH(cx, y, 260, 34), bg_color)
            arcade.draw_text(
                label,
                cx,
                y,
                text_color,
                font_size=18,
                anchor_x="center",
                anchor_y="center",
                bold=index == self.selected,
            )

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.UP:
            self.selected = (self.selected - 1) % len(self.options)
        elif symbol == arcade.key.DOWN:
            self.selected = (self.selected + 1) % len(self.options)
        elif symbol in (arcade.key.RETURN, arcade.key.ENTER):
            label = self.options[self.selected]
            if label == "Increase Speed":
                self.window.show_view(speed_view(self.pause_menu))
            elif label == "Invincibility":
                value = self.pause_menu.game_view.cheater.invincible
                self.pause_menu.game_view.cheater.invincible = self.boolean_map[value]
            elif label == "Ghost Freeze":
                value = self.pause_menu.game_view.cheater.ghost_freeze
                self.pause_menu.game_view.cheater.ghost_freeze = self.boolean_map[value]
            elif label == "Show Ghosts Path":
                value = self.pause_menu.game_view.cheater.show_ghost_path
                self.pause_menu.game_view.cheater.show_ghost_path = self.boolean_map[value]
            elif label == "Level Skip":
                value = self.pause_menu.game_view.cheater.level_skip
                self.pause_menu.game_view.cheater.level_skip = self.boolean_map[value]
            elif label == "Extra Lives":
                self.pause_menu.game_view.lives += 1
            elif label == "Back":
                self.window.show_view(self.pause_menu)
        elif symbol == arcade.key.ESCAPE:
            self.window.show_view(self.pause_menu)



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
            self.pause_menu.game_view.ghost_speed -= 0.01
        if symbol == arcade.key.RETURN or symbol == arcade.key.ESCAPE:
            self.window.show_view(CheatModeView(self.pause_menu))
