import arcade
from .pacman import Pacman


class MainMenu(arcade.View):
    def __init__(self, window: arcade.Window, game_view: Pacman) -> None:
        super().__init__(window, background_color=arcade.color.BLACK)
        self.game_view = game_view

        self.buttons = ["Play", "Settings", "Quit"]
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
            if self.buttons[self.selected] == "Play":
                self.window.show_view(self.game_view)
            elif self.buttons[self.selected] == "Quit":
                arcade.exit()