# import arcade
# class A(arcade.Sprite):
#     def __init__(self, cords) -> None:
#         super().__init__(scale=0.1)
#         self.normal = arcade.load_texture("src/assets/cyanghost.png")
#         self.fight = arcade.load_texture("src/assets/blueghost.png")
#         self.texture = self.normal
#         self.center_x, self.center_y = cords
#     def draw(self):
#         x, y = self.center_x, self.center_y
#         r = arcade.rect.XYWH(x, y, 40, 40)
#         arcade.draw_texture_rect(self.texture, r)
#     def change_image(self):
#         self.texture = self.fight
# class Game(arcade.Window):
#     def __init__(self):
#         super().__init__()
#         self.l = arcade.SpriteList()
#         self.init_spirits()
#     def init_spirits(self):
#         cell_size =  100
#         y = 900
#         for i in range(8):
#             x = 40 
#             for j in range(8):
#                 self.l.append(A((x, y)))
#                 x += cell_size
#             y -= cell_size    
#     def on_draw(self):
#         self.clear()
#         self.l.draw()
#     def on_key_press(self, symbol: int, modifiers: int) :
#         if symbol == arcade.key.ENTER:
#             for ghost in self.l:
#                 ghost.change_image()
# g = Game()
# g.run()

from enum import Enum

class A(Enum):
    a= 1
    b= 2
    c =4

for x in A:
    print(type(x.name))


x= (1 , 3)
y= (2 , 3)

print(tuple(x  + y for x, y in zip(x, y)))