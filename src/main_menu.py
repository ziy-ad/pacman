import arcade
from .pacman import Pacman
from .score_tracker import score_board
import re
import time
from .speed_screen import speed_view


class MainMenu(arcade.View):
    def __init__(self, window: arcade.Window, game_view: Pacman) -> None:
        super().__init__(window, background_color=arcade.color.BLACK)
        self.game_view = game_view
        self.is_started = False
        self.buttons = ["Play", "Highscores", "Settings", "Quit"]
        self.selected = 0
        self.button_width = 250
        self.button_height = 50
        self.button_spacing = 20 
        self.game_view.set_main_menu(self)
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
            label = self.buttons[self.selected]
            if label == "Play" or label == "Resume":
                self.is_started = True
                self.buttons[0] = "Resume"
                if self.game_view.start_time is None:
                    self.game_view.start_time = time.time()
                self.window.show_view(self.game_view)
            elif label == "Settings":
                self.window.show_view(speed_view(self))
            elif label == "Highscores":
                self.window.show_view(ScoreboardView(self.window, self.game_view.scoreboard, self.game_view))
            elif label == "Quit":
                arcade.exit()
        elif symbol == arcade.key.ESCAPE:
            if self.is_started:
                self.window.show_view(self.game_view)



class GameOverView(arcade.View):
    def __init__(self, window: arcade.Window, scoreboard: score_board, score: int, pacman_view: Pacman) -> None:
        super().__init__(window, background_color=arcade.color.BLACK)
        self.button_width = 220
        self.button_height = 52
        self.button_x = self.width // 2
        self.button_y = self.height // 2 - 130
        self.background = arcade.load_texture("src/assets/game_over_bg.png")
        self.scoreboard = scoreboard
        self.score = score
        self.pacman_view = pacman_view
        self.input_name = ""
        self.message = "Enter your name (max 10, letters/numbers/spaces):"
        self.valid_re = re.compile(r"^[A-Za-z0-9 ]{1,10}$")

    def on_draw(self):
        self.clear()
        r = arcade.rect.XYWH(self.width // 2 , self.height // 2, self.width, self.height)
        arcade.draw_texture_rect(self.background, r)
        cx = self.width // 2
        cy = self.height // 2

        arcade.draw_text(
            self.input_name + ("_" if int(time.time() * 2) % 2 == 0 else ""),
            cx,
            cy - 80,
            arcade.color.AERO_BLUE,
            font_size=28,
            anchor_x="center",
        )

    def on_key_press(self, symbol, modifiers):
        if symbol in (arcade.key.RETURN, arcade.key.ENTER):
            name = self.input_name.strip()
            if self.valid_re.match(name):
                # save and show scoreboard
                self.scoreboard.add_score(name, self.score)
                from .main_menu import ScoreboardView

                self.window.show_view(ScoreboardView(self.window, self.scoreboard, self.pacman_view))
                return
            else:
                self.message = "Invalid name. Use 1-10 letters/numbers/spaces."

        elif symbol == arcade.key.BACKSPACE:
            self.input_name = self.input_name[:-1]
        elif symbol == arcade.key.ESCAPE:
            self.pacman_view.reset()
            self.window.show_view(MainMenu(self.window, self.pacman_view))

    def on_text(self, text: str) -> None:
        if not text:
            return
        for ch in text:
            if len(self.input_name) < 10 and (ch.isalnum() or ch == " "):
                self.input_name += ch


class ScoreboardView(arcade.View):
    def __init__(self, window: arcade.Window, scoreboard: score_board, pacman_view: Pacman) -> None:
        super().__init__(window, background_color=arcade.color.BLACK)
        self.scoreboard = scoreboard
        self.pacman_view = pacman_view

    def on_draw(self):
        self.clear()
        cx = self.width // 2
        cy = self.height // 2

        arcade.draw_text(
            "Highscores",
            cx,
            cy + 180,
            arcade.color.WHITE,
            font_size=36,
            anchor_x="center",
        )

        scores = self.scoreboard.get_all_scores()
        if not scores:
            arcade.draw_text(
                "No highscores yet",
                cx,
                cy + 120,
                arcade.color.GRAY,
                font_size=20,
                anchor_x="center",
            )
        else:
            start_y = cy + 120
            line_h = 34
            for i, entry in enumerate(scores):
                y = start_y - i * line_h
                name = entry.get("name", "")
                score = entry.get("score", 0)
                arcade.draw_text(f"{i+1:2}. {name}", cx - 120, y, arcade.color.WHITE, font_size=22)
                arcade.draw_text(f"{score}", cx + 120, y, arcade.color.AERO_BLUE, font_size=22, anchor_x="right")

        arcade.draw_text(
            "Press Enter or Escape to return to menu",
            cx,
            cy - 200,
            arcade.color.GRAY,
            font_size=14,
            anchor_x="center",
        )

    def on_key_press(self, symbol, modifiers):
        if symbol in (arcade.key.RETURN, arcade.key.ENTER, arcade.key.ESCAPE):
            # Return to main menu; reuse pacman_view instance
            self.pacman_view.reset()
            self.window.show_view(MainMenu(self.window, self.pacman_view))