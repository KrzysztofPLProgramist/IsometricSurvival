import pygame.time

from draw import *
from player import *

class Game:
    def __init__(self):
        self.scale = SCALE
        self.current_z = 0

        # Managers
        self.tile_manager = TileManager(self)
        self.player = Player(self)

        # Text
        self.font = pygame.font.SysFont("Arial", 32, False)

        # Clock
        self.clock = pygame.time.Clock()
        self.dt = 0

        # Screen
        # self.screen = pygame.display.set_mode((WIDTH,HEIGHT), pygame.FULLSCREEN)
        self.screen = pygame.display.set_mode((WIDTH,HEIGHT))

        # States
        self.main_loop_running = True

        # mouse
        self.m1_down_tf = False
        "Mouse button 1 down this frame"

        self.m1_down = False
        self.mouse_pos = []
        self.calculated_mouse_pos = []

        self.current_tile = None

        # ppos = self.tile_manager.iso_to_screen(self.player.pos)
        # self.scroll = [ppos[0]+halfWIDTH-16, ppos[1]+halfHEIGHT-16]

    def text(self, txt, pos, color):
        render = self.font.render(str(txt), False, color)
        self.screen.blit(render, pos)

    def key_check(self):
        self.m1_down = False
        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0]:
            self.m1_down = True

        if keys[pygame.K_ESCAPE]: self.main_loop_running = False


    def events(self):
        self.m1_down_tf = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.m1_down_tf = True

    def update(self):
        self.current_z = self.player.pos[2]
        self.mouse_pos = pygame.mouse.get_pos()
        self.calculated_mouse_pos = self.tile_manager.screen_to_iso(self.mouse_pos, self.current_z)
        c = self.calculated_mouse_pos
        self.current_tile = self.tile_manager.get_tile(c)
        if self.current_tile is None or self.current_tile.get_tag("pass_throughs"):
            self.current_tile = self.tile_manager.get_tile((c[0],c[1],c[2]-1))


        self.player.update()
        # ppos = self.tile_manager.iso_to_screen(self.player.pos)
        # self.scroll = [-ppos[0]-(16 * self.scale) + halfWIDTH, -ppos[1]-(16 * self.scale) + halfHEIGHT]

    def draw(self):
        self.tile_manager.draw()
        self.player.draw()
        s = pygame.surface.Surface((3,3))
        s.fill("red")
        self.screen.blit(s, (halfWIDTH-1, halfHEIGHT-1))

        self.text(f"Calculated mouse pos: {self.calculated_mouse_pos}", (10, 10), "black")
        self.text(f"Active tile name: {self.current_tile.name if self.current_tile is not None else "None"}", (10, 40), "black")
        self.text(f"FPS: {self.clock.get_fps()}", (10, 70), "black")
        self.text(f"Move cooldown: {self.player.move_cooldown}", (10, 100), "black")

    def main_loop_test(self):
        while self.main_loop_running:
            self.screen.fill("white")
            self.key_check()
            self.events()
            self.update()
            self.draw()

            self.dt = self.clock.tick(24) / 1000

            pygame.display.flip()

if __name__ == '__main__':
    game = Game()
    game.tile_manager.load_rect("stone", (-8,-8,-8), (16, 16, 8))
    game.main_loop_test()
