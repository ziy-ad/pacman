"""Menus and score screens."""

import arcade
from .pacman import Pacman
from .score_tracker import score_board
import re
import time
from .speed_screen import CheatModeView
from .paths import resource_path
from PIL import ImageFilter
from typing import Any


class MainMenu(arcade.View):
    """Main menu view."""

    def __init__(self, window: arcade.Window, game_view: Pacman) -> None:
        """Set up the main menu buttons."""
        super().__init__(window)
        self.background = arcade.load_texture(
            resource_path("src/assets/pacmanbackground.jpg")
        )
        self.game_view = game_view
        self.pause_view = PauseMenu(window, game_view, self)
        self.buttons = [
            "Play",
            "Instructions",
            "Highscores",
            "CheatMode",
            "Quit",
        ]
        self.selected = 0
        self.button_width = 250
        self.button_height = 50
        self.button_spacing = 20
        self.game_view.set_main_menu(self)

    def on_draw(self) -> None:
        """Draw the main menu."""
        self.clear()
        arcade.draw_texture_rect(
            self.background, arcade.LRBT(0, self.width, 0, self.height)
        )
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

            arcade.Text(
                label,
                cx,
                y,
                text_color,
                font_size=22,
                font_name="Rowdies",
                anchor_x="center",
                anchor_y="center",
                bold=i == self.selected,
            ).draw()

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        """Handle the main menu keys."""
        if symbol == arcade.key.UP:
            self.selected = (self.selected - 1) % len(self.buttons)

        elif symbol == arcade.key.DOWN:
            self.selected = (self.selected + 1) % len(self.buttons)

        elif symbol == arcade.key.RETURN:
            label = self.buttons[self.selected]
            if label == "Play":
                if self.game_view.start_time is None:
                    self.game_view.start_time = time.time()
                self.game_view.resume()
                self.window.show_view(self.game_view)
            elif label == "CheatMode":
                self.game_view.pause()
                self.window.show_view(CheatModeView(self))
            elif label == "Instructions":
                self.window.show_view(InstructionsView(self.window, self))
            elif label == "Highscores":
                self.game_view.pause()
                self.window.show_view(
                    ScoreboardView(
                        self.window, self.game_view.scoreboard, self.game_view
                    )
                )
            elif label == "Quit":
                arcade.exit()


class InstructionsView(arcade.View):
    """View explaining the game controls and objective."""

    def __init__(self, window: arcade.Window, main_view: MainMenu) -> None:
        """Set up the instructions view."""
        super().__init__(window)
        self.background = main_view.background
        self.main_view = main_view

    def on_draw(self) -> None:
        """Draw the game instructions."""
        self.clear()
        arcade.draw_texture_rect(
            self.background, arcade.LRBT(0, self.width, 0, self.height)
        )
        cx = self.width // 2
        cy = self.height // 2

        arcade.Text(
            "How to Play",
            cx,
            cy + 280,
            arcade.color.YELLOW,
            font_name="Silkscreen",
            font_size=54,
            bold=True,
            anchor_x="center",
        ).draw()

        instructions = [
            ("Move", "Arrow keys or W A S D", arcade.color.WHITE),
            ("Goal", "Eat every pellet in the maze", arcade.color.WHITE),
            (
                "Power pellets",
                "Eat one to chase and eat ghosts",
                arcade.color.AERO_BLUE,
            ),
            (
                "Warning",
                "Avoid ghosts unless they are frightened",
                arcade.color.WHITE,
            ),
            ("Pause", "Press Escape during a game", arcade.color.WHITE),
        ]
        rect_ = arcade.XYWH(cx, cy - 100, 1600, 600)
        r, g, b, _ = arcade.color.BLACK
        y = cy
        arcade.draw_rect_filled(rect_, (r, g, b, 190))
        for index, (heading, text, color) in enumerate(instructions):
            y = cy + 120 - index * 100
            arcade.Text(
                heading,
                cx - 750,
                y,
                arcade.color.YELLOW,
                font_name="Rowdies",
                font_size=31,
                bold=True,
                anchor_x="left"
            ).draw()
            arcade.Text(
                text,
                cx + 150,
                y,
                color,
                font_name="Rowdies",
                font_size=25,
                anchor_x="left"

            ).draw()

        arcade.Text(
            "Press Enter or Escape to return to the menu",
            cx,
            y - 100,
            arcade.color.GRAY,
            font_size=20,
            anchor_x="center",
            font_name="Rowdies"
        ).draw()

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        """Return to the main menu."""
        if symbol in (arcade.key.RETURN, arcade.key.ENTER, arcade.key.ESCAPE):
            self.window.show_view(self.main_view)


class PauseMenu(arcade.View):
    """Pause menu view."""

    def __init__(
        self, window: arcade.Window, game_view: Pacman, main_view: MainMenu
    ) -> None:
        """Set up the pause menu buttons."""
        super().__init__(window, background_color=arcade.color.BLACK)
        self.game_view = game_view
        self.main_view = main_view
        self.buttons = ["Resume", "CheatMode", "Back"]
        self.selected = 0
        self.button_width = 250
        self.button_height = 50
        self.button_spacing = 20
        self.game_view.set_main_menu(self)
        self.is_started = self.game_view.start_time is not None

    def on_draw(self) -> None:
        """Draw the pause menu."""
        self.clear()
        cx = self.width // 2
        cy = self.height // 2

        arcade.draw_texture_rect(
            self.main_view.background,
            arcade.LRBT(0, self.width, 0, self.height),
        )
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

            arcade.Text(
                label,
                cx,
                y,
                text_color,
                font_size=22,
                font_name="Rowdies",
                anchor_x="center",
                anchor_y="center",
                bold=i == self.selected,
            ).draw()

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        """Handle the pause menu keys."""
        if symbol == arcade.key.UP:
            self.selected = (self.selected - 1) % len(self.buttons)

        elif symbol == arcade.key.DOWN:
            self.selected = (self.selected + 1) % len(self.buttons)

        elif symbol == arcade.key.RETURN:
            label = self.buttons[self.selected]
            if label == "Resume":
                self.is_started = True
                self.buttons[0] = "Resume"
                if self.game_view.start_time is None:
                    self.game_view.start_time = time.time()
                self.game_view.resume()
                self.window.show_view(self.game_view)
            elif label == "CheatMode":
                self.game_view.pause()
                self.window.show_view(CheatModeView(self))
            elif label == "Back":
                self.main_view.pause_view.is_started = False
                self.main_view.buttons[0] = "Play"
                self.game_view.setup_everything(with_score=True)
                self.window.show_view(self.main_view)
        elif (
            symbol == arcade.key.ESCAPE
            and self.is_started
            and self.game_view.pause_start is not None
        ):
            self.game_view.resume()
            self.window.show_view(self.game_view)


class GameOverView(arcade.View):
    """View asking the player name after the game."""

    def __init__(
        self,
        window: arcade.Window,
        scoreboard: score_board,
        score: int,
        pacman_view: Pacman,
    ) -> None:
        """Set up the game over view."""
        super().__init__(window, background_color=arcade.color.BLACK)
        self.button_width = 220
        self.button_height = 52
        self.button_x = self.width // 2
        self.button_y = self.height // 2 - 130
        self.chars_to_move: list[list[Any]] = []
        self.chars_map = self.create_char_map()
        image = arcade.get_image()
        image = image.filter(ImageFilter.GaussianBlur(radius=15))
        self.background = arcade.Texture(image=image)
        self.scoreboard = scoreboard
        self.score = score
        self.pacman_view = pacman_view
        self.input_name = ""
        self.message = "Enter your name (max 10, letters/numbers/spaces):"
        self.valid_re = re.compile(r"^[A-Za-z0-9 ]{1,10}$")

    def create_char_map(self) -> dict[str, list[int]]:
        screen_width = self.window.width
        strings = [
            "1234567890",
            "qwertyuiop",
            "asdfghjkl",
            "zxcvbnm",
        ]
        char_pos: dict[str, list[int]] = {}

        for string in strings:
            for i, char in enumerate(string):
                x = int(round(5 + (i % 10) * (screen_width - 5) / 9))
                char_pos[char] = [x, 0]
                if char.isalpha():
                    char_pos[char.upper()] = [x, 0]
        return char_pos

    def on_draw(self) -> None:
        """Draw the name input and the score."""
        self.clear()
        r = arcade.rect.XYWH(
            self.width // 2, self.height // 2, self.width, self.height
        )
        arcade.draw_texture_rect(self.background, r)
        cx = self.width // 2
        cy = self.height // 2 + 300

        if self.chars_to_move:
            for item in self.chars_to_move:
                char, cords = item
                x, y = cords
                arcade.Text(
                    f"{char}",
                    x,
                    y,
                    arcade.color.AERO_BLUE,
                    font_size=108,
                    font_name="VT323",
                    anchor_x="center",
                ).draw()

        arcade.Text(
            self.input_name + ("_" if int(time.time() * 2) % 2 == 0 else ""),
            cx,
            cy - 80,
            arcade.color.AERO_BLUE,
            font_name="VT323",
            font_size=48,
            anchor_x="center",
        ).draw()

        arcade.Text(
            "Your score:",
            cx - 100,
            cy,
            arcade.color.YELLOW,
            font_size=28,
            font_name="Silkscreen",
            bold=True,
            anchor_x="right",
        ).draw()
        arcade.Text(
            f"{self.pacman_view.previous_score}",
            cx + 100,
            cy,
            arcade.color.YELLOW,
            font_size=25,
            font_name="Rowdies",
            bold=True,
            anchor_x="left",
        ).draw()

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        """Handle the name input keys."""
        if symbol in (arcade.key.RETURN, arcade.key.ENTER):
            name = self.input_name.strip()
            if self.valid_re.match(name):
                self.scoreboard.add_score(name, self.score)
                from .main_menu import ScoreboardView

                self.window.show_view(
                    ScoreboardView(
                        self.window, self.scoreboard, self.pacman_view
                    )
                )
                return
            else:
                self.message = "Invalid name. Use 1-10 letters/numbers/spaces."

        elif symbol == arcade.key.BACKSPACE:
            self.input_name = self.input_name[:-1]
        elif symbol == arcade.key.ESCAPE:
            self.pacman_view.reset()
            self.pacman_view.set_pac_man_lives()
            self.pacman_view.score = 0
            self.window.show_view(MainMenu(self.window, self.pacman_view))

    def on_text(self, text: str) -> None:
        """Add the typed characters to the name."""
        if not text:
            return
        for ch in text:
            if len(self.input_name) < 10 and (ch.isalnum() or ch == " "):
                if ch == " ":
                    self.input_name += ch
                    continue
                self.chars_to_move += [[ch, self.chars_map[ch].copy()]]

    def on_update(self, delta_time: float) -> None:
        cx = self.width // 2
        cy = self.height // 2 + 300 - 100
        to_remove = []
        if self.chars_to_move:
            min_dist = 50
            for index in range(len(self.chars_to_move)):
                item = self.chars_to_move[index]
                char_x, char_y = self.chars_map[item[0]]
                nx = (cx - char_x) * 0.05
                ny = (cy - char_y) * 0.05
                if (
                    abs(cx - item[1][0] + nx) <= min_dist
                    and abs(cy - item[1][1] + ny) <= min_dist
                ):
                    to_remove += [item]
                    self.input_name += item[0]
                else:
                    self.chars_to_move[index][1][0] += int(nx)
                    self.chars_to_move[index][1][1] += int(ny)
        for item in to_remove:
            self.chars_to_move.remove(item)


class ScoreboardView(arcade.View):
    """View showing the highscores."""

    def __init__(
        self,
        window: arcade.Window,
        scoreboard: score_board,
        pacman_view: Pacman,
    ) -> None:
        """Store the scoreboard and the game view."""
        super().__init__(window, background_color=arcade.color.BLACK)
        self.scoreboard = scoreboard
        self.pacman_view = pacman_view

    def on_draw(self) -> None:
        """Draw the highscores."""
        self.clear()
        cx = self.width // 2
        cy = self.height // 2

        arcade.Text(
            "Highscores",
            cx,
            cy + 380,
            arcade.color.YELLOW,
            font_name="Silkscreen",
            font_size=50,
            bold=True,
            anchor_x="center",
        ).draw()

        scores = self.scoreboard.get_all_scores()
        y: float = 0
        if not scores:
            arcade.Text(
                "No highscores yet",
                cx,
                cy + 120,
                arcade.color.GRAY,
                font_name="Rowdies",
                font_size=20,
                anchor_x="center",
            ).draw()
        else:
            start_y = cy + 120
            line_h = 34
            colors = {
                1: (22, arcade.color.GOLD),
                2: (20, arcade.color.SILVER_CHALICE),
                3: (18, arcade.color.BRONZE),
            }
            for i, entry in enumerate(scores):
                y = start_y - i * line_h
                name = entry.get("name", "")
                score = entry.get("score", 0)
                size, color = colors.get(i + 1, (15, arcade.color.WHITE))
                arcade.Text(
                    f"{i+1:2}. {name}",
                    cx - 200,
                    y,
                    color,
                    font_name="Rowdies",
                    bold=True,
                    font_size=size,
                ).draw()
                arcade.Text(
                    f"{score}",
                    cx + 200,
                    y,
                    arcade.color.AERO_BLUE,
                    font_name="Rowdies",
                    font_size=size,
                    anchor_x="right",
                ).draw()
        y -= 200
        arcade.Text(
            "Press Enter or Escape to return to menu",
            cx,
            y,
            arcade.color.GRAY,
            font_size=24,
            font_name="Rowdies",
            bold=True,
            anchor_x="center",
        ).draw()

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        """Go back to the main menu."""
        if symbol in (arcade.key.RETURN, arcade.key.ENTER, arcade.key.ESCAPE):
            self.pacman_view.reset()
            self.pacman_view.set_pac_man_lives()
            self.pacman_view.score = 0
            self.window.show_view(MainMenu(self.window, self.pacman_view))
