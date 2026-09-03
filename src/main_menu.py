import arcade
from PIL import Image
from typing import TYPE_CHECKING
from .pause_menu import speed_view 
if TYPE_CHECKING:
    from .pacman import Pacman

class MainMenu(arcade.View):
    def __init__(self, window: arcade.Window, game_view: "Pacman") -> None:
        super().__init__(window, background_color=arcade.color.BLACK)
        self.game_view = game_view
        self.game_view.setup()
        self.game_view.pause_menu = self
        self.playing = False
        self.buttons = ["Play", "Speed", "Quit"]
        self.selected = 0
        self.image: Image.Image | None = None
        self.button_width = 250
        self.button_height = 50
        self.button_spacing = 20
        self.speed_view = speed_view(self)
        self.background = arcade.load_texture("src/assets/menu_background_riso.jpg")
    def on_draw(self):
        self.clear()
        r = arcade.rect.XYWH(self.width // 2 , self.height // 2 , self.width, self.height)
        arcade.draw_texture_rect(self.background, r)
        cx = self.width // 2
        cy = self.height // 2 - 125
        if self.image:
            self.pause_background = arcade.Texture(
                name="pause_background",
                image=self.image
            )
            arcade.draw_texture_rect(
                self.pause_background,
                arcade.LRBT(
                    0, self.width,
                    0, self.height
                )
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
                self.buttons[self.selected] = "Resume"
                self.window.show_view(self.game_view)
            elif self.buttons[self.selected] == "Resume":
                self.window.show_view(self.game_view)
            elif self.buttons[self.selected] == "Speed":
                self.window.show_view(self.speed_view)
            elif self.buttons[self.selected] == "Quit":
                arcade.exit()