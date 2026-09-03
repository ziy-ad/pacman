import arcade




class D(arcade.Window):
    def __init__(self, width: int = 1280, height: int = 720, title: str | None = "Arcade Window", fullscreen: bool = False) -> None:
        super().__init__(width, height, title)
        self.ima = arcade.Sprite("src/assets/blueghost.png")
        self.ima.center_x = width // 2 
        self.ima.center_y = height // 2
        self.ima.scale = 10
    def draw(self, dt) -> None:
        self.ima.draw()


d = D()
d.run()