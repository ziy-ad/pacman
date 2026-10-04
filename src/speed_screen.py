"""Cheat mode and speed screens."""

import arcade
from .pacman import Point
from .paths import resource_path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .main_menu import MainMenu, PauseMenu


class CheatModeView(arcade.View):
    """View listing the cheat mode options."""

    def __init__(self, pause_menu: "PauseMenu | MainMenu") -> None:
        """Set up the cheat mode options."""
        super().__init__(background_color=arcade.color.BLACK)
        self.pause_menu = pause_menu
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
        self.toggel_text = arcade.Text(
            "",
            self.width // 2,
            self.height - 400,
            arcade.color.WHITE,
            font_size=1,
            anchor_x="center",
            font_name="Rowdies",
            bold=True,
        )
        self.title = arcade.Text(
            "CHEAT MODE",
            self.width // 2,
            self.height - 200,
            arcade.color.YELLOW,
            font_size=50,
            font_name="Silkscreen",
            anchor_x="center",
            bold=True,
        )
        self.is_toggel = False
        self.is_toggel_time = 0.0
        self.toggel_value = ""
        self.boolean_map = {True: False, False: True}

    def on_draw(self) -> None:
        """Draw the cheat mode options."""
        self.clear()
        cx = self.width // 2
        cy = self.height // 2
        if self.is_toggel:
            self.toggel_text.text = (
                f"{self.options[self.selected]}: {self.toggel_value}"
            )
            self.toggel_text.draw()
        self.title.draw()

        for index, label in enumerate(self.options):
            y = cy + 60 - index * 60
            if index == self.selected:
                text_color = arcade.color.BLACK
                bg_color = arcade.color.YELLOW
            else:
                text_color = arcade.color.WHITE
                bg_color = arcade.color.DARK_SLATE_BLUE

            arcade.draw_rect_filled(arcade.XYWH(cx, y, 260, 50), bg_color)
            arcade.Text(
                label,
                cx,
                y,
                text_color,
                font_size=20,
                anchor_x="center",
                anchor_y="center",
                bold=index == self.selected,
                font_name="Rowdies",
            ).draw()

    def on_update(self, delta_time: float) -> None:
        """Animate the toggled option text."""
        if self.is_toggel:
            if self.is_toggel_time < 0.5:
                if self.toggel_text.font_size <= 38:
                    self.toggel_text.font_size += 4
            elif self.toggel_text.font_size - 4 >= 1:
                self.toggel_text.font_size -= 4
            else:
                self.toggel_text.visible = False
            if self.is_toggel_time >= 0.7:
                self.is_toggel_time = 0.0
                self.is_toggel = False
                self.toggel_text.visible = True
            self.is_toggel_time += delta_time

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        """Handle the cheat mode keys."""
        self.is_toggel = False
        self.is_toggel_time = 0
        self.toggel_text.font_size = 0
        self.toggel_text.visible = True

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
                self.pause_menu.game_view.cheater.invincible = (
                    self.boolean_map[value]
                )
                self.toggel_value = f"{self.boolean_map[value]}"
                self.is_toggel = True
            elif label == "Ghost Freeze":
                value = self.pause_menu.game_view.cheater.ghost_freeze
                self.pause_menu.game_view.cheater.ghost_freeze = (
                    self.boolean_map[value]
                )
                self.toggel_value = f"{self.boolean_map[value]}"
                self.is_toggel = True
            elif label == "Show Ghosts Path":
                value = self.pause_menu.game_view.cheater.show_ghost_path
                self.toggel_value = f"{self.boolean_map[value]}"
                self.is_toggel = True
                self.pause_menu.game_view.cheater.show_ghost_path = (
                    self.boolean_map[value]
                )
            elif label == "Level Skip":
                value = self.pause_menu.game_view.cheater.level_skip
                self.toggel_value = f"{self.boolean_map[value]}"
                self.is_toggel = True
                self.pause_menu.game_view.cheater.level_skip = (
                    self.boolean_map[value]
                )
            elif label == "Extra Lives":
                self.pause_menu.game_view.lives += 1
                self.is_toggel = True
                live = self.pause_menu.game_view.live_pac_man
                self.pause_menu.game_view.live_textures += [live]
                self.toggel_value = f"Lives: {self.pause_menu.game_view.lives}"
                self.pause_menu.game_view.sort_lives()
            elif label == "Back":
                self.window.show_view(self.pause_menu)
        elif symbol == arcade.key.ESCAPE:
            self.window.show_view(self.pause_menu)


class speed_view(arcade.View):
    """View used to change the game speed."""

    def __init__(self, pause_menu: "PauseMenu | MainMenu") -> None:
        """Set up the speed screen."""
        super().__init__(background_color=arcade.color.BLACK)
        self.cy = self.height // 2
        self.pause_menu = pause_menu
        self.cell_size = 60
        self.start_x = int((self.width // 2) - self.cell_size * 6)
        self.end_x = int((self.width // 2) + self.cell_size * 6)
        self.pac_man_position = Point(self.start_x, self.cy)
        self.pac_man_frames = self.load_pacman_frames()
        self.pac_man_seconds: float = 0
        self.pac_man_next = 1
        self.pac_man_frame_index = 0
        self.pac_man = self.pac_man_frames[self.pac_man_frame_index]
        self.pac_man_speed_text = arcade.Text(
            "LEVEL",
            self.width // 2,
            self.height - 200,
            arcade.color.WHITE,
            font_size=38,
            anchor_x="center",
            font_name="VT323",
        )

    def load_pacman_frames(self) -> list[arcade.Texture]:
        """Load the Pac-Man frames."""
        return [
            arcade.load_texture(resource_path("src/assets/pacman_closed.png")),
            arcade.load_texture(resource_path("src/assets/pacman_half.png")),
            arcade.load_texture(resource_path("src/assets/pacman_open.png")),
        ]

    def draw_background(self) -> None:
        """Draw the background lines."""
        r, g, b, _ = arcade.color.WHITE
        for x in range(0, int(self.width * 3), 40):
            arcade.draw_line(x, 0, x, self.height, (r, g, b, 100), 1)

        start = 20
        for y in range(0, int(self.height * 3), 40):
            arcade.draw_line(
                0, y, self.width, abs(y - start), (r, g, b, 100), 1
            )
            start = y // 2

    def on_draw(self) -> None:
        """Draw the speed screen."""
        self.clear()
        self.draw_background()
        arcade.draw_rect_filled(
            arcade.XYWH(
                self.width // 2, self.cy, self.cell_size * 12, self.cell_size
            ),
            arcade.color.BLACK,
        )
        arcade.draw_line(
            self.start_x,
            self.cy + (self.cell_size // 2),
            self.start_x,
            self.cy - (self.cell_size // 2),
            arcade.color.BLUE,
            5,
        )
        arcade.draw_line(
            self.end_x,
            self.cy + (self.cell_size // 2),
            self.end_x,
            self.cy - (self.cell_size // 2),
            arcade.color.BLUE,
            5,
        )
        arcade.draw_line(
            self.start_x,
            self.cy + (self.cell_size // 2),
            self.end_x,
            self.cy + (self.cell_size // 2),
            arcade.color.BLUE,
            5,
        )
        arcade.draw_line(
            self.start_x,
            self.cy - (self.cell_size // 2),
            self.end_x,
            self.cy - (self.cell_size // 2),
            arcade.color.BLUE,
            5,
        )
        self.pac_man_speed_text.text = (
            f"Speed: {round(self.pause_menu.game_view.speed * 100)} %"
        )
        arcade.draw_rect_filled(
            arcade.XYWH(
                self.width // 2,
                self.height - 185,
                self.cell_size * 4,
                self.cell_size,
            ),
            arcade.color.BLACK,
        )
        arcade.draw_rect_outline(
            arcade.XYWH(
                self.width // 2,
                self.height - 185,
                self.cell_size * 4,
                self.cell_size,
            ),
            arcade.color.BLUE,
            3,
        )
        self.pac_man_speed_text.draw()

        arcade.draw_texture_rect(
            self.pac_man_frames[self.pac_man_frame_index],
            arcade.XYWH(
                self.pac_man_position.x,
                self.pac_man_position.y,
                self.cell_size * 0.7,
                self.cell_size * 0.7,
            ),
        )

    def on_update(self, delta_time: float) -> None:
        """Animate Pac-Man and move him forward."""
        self.pac_man_seconds += delta_time
        to_add = int(
            self.pause_menu.game_view.cell_size
            * self.pause_menu.game_view.speed
        )
        if self.pac_man_seconds >= 0.2:
            self.pac_man_frame_index += self.pac_man_next
            if self.pac_man_frame_index == 0 or self.pac_man_frame_index == 2:
                self.pac_man_next *= -1
            self.pac_man_seconds = 0
        if self.pac_man_position.x + to_add < self.end_x - self.cell_size // 2:
            self.pac_man_position.x += to_add

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        """Change the speed with the arrow keys."""
        if symbol == arcade.key.UP:
            if self.pause_menu.game_view.speed < 1.0:
                self.pac_man_position.x = self.start_x + self.cell_size // 2
                speed = self.pause_menu.game_view.speed + 0.01
                self.pause_menu.game_view.speed = round(speed, 2)
        if symbol == arcade.key.DOWN:
            if self.pause_menu.game_view.speed > 0.02:
                self.pac_man_position.x = self.start_x + self.cell_size // 2
                speed = self.pause_menu.game_view.speed - 0.01
                self.pause_menu.game_view.speed = round(speed, 2)
        if symbol == arcade.key.RETURN or symbol == arcade.key.ESCAPE:
            self.window.show_view(CheatModeView(self.pause_menu))
