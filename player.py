from config import *

class Player:
    def __init__(self, game, pos=None):
        if pos is None:
            pos = [0, 0, 0]
        self.game = game
        self.pos = pos
        self.img = pygame.image.load("assets/player/player.png")
        self.image = pygame.transform.scale_by(self.img, self.game.scale)

        self.move_cooldown = 0.5
        self.destination = None
        self.destination_tile = None

    def update(self):
        if self.move_cooldown > 0:
            self.move_cooldown -= self.game.dt
        if self.move_cooldown < 0:
            self.move_cooldown = 0
        if self.game.m1_down_tf:
            if self.game.tile_manager.tile_distance(self.pos, self.game.calculated_mouse_pos) < 2:
                self.destination = self.game.calculated_mouse_pos
                self.destination_tile = self.game.current_tile

        if self.destination is not None and self.move_cooldown == 0:
            if self.destination_tile is None or self.destination_tile.get_tag("can_stand_on"):
                self.pos = self.destination
                self.destination = None

                self.move_cooldown = 0.5

    def draw(self):
        self.game.screen.blit(self.image, (halfWIDTH-16*self.game.scale, halfHEIGHT))
