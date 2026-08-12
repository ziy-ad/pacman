import arcade


class Ghost:
    def __init(self, texture_path) -> None:
        self.sprite = arcade.Sprite(texture_path)

class GhostsList:
    ghosts = arcade.SpriteList()

    @classmethod
    def add_ghost(cls, texture_path):
        cls.ghosts.append(arcade.Srpite(texture_path))



class Game(arcade.Window):
    def __init__(self):

        super().__init__(400, 400, "window")



game = Game()
game.run()


ghosts = GhostsList()
