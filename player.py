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
        self.fall_cooldown = 0.5
        self.destination = None
        self.destination_cell = None

    def update(self):
        if self.move_cooldown > 0:
            self.move_cooldown -= self.game.dt
        if self.fall_cooldown > 0:
            self.fall_cooldown -= self.game.dt
        if self.game.m1_down_tf:
            if self.game.cell_manager.cell_distance(self.pos, self.game.calculated_mouse_pos) < 2:
                self.destination = self.game.calculated_mouse_pos
                self.destination_cell = self.game.current_cell

        if self.destination is not None and self.move_cooldown <= 0:
            if not self.destination == "player":
                # if self.destination_cell is None or self.destination_cell.get_tag("can_stand_on"):
                self.game.cell_manager.get_cell(self.destination).has_tag("can_stand_on")
                self.pos = self.destination
                self.destination = None

                self.move_cooldown = 0.5
        p = self.pos
        if self.game.cell_manager.get_cell((p[0],p[1],p[2]-1)).has_tag("can_stand_on") is False and self.fall_cooldown <= 0:
            self.fall_cooldown = 0.5
            self.pos = (p[0],p[1],p[2]-1)

    def draw(self):
        self.game.screen.blit(self.image, (halfWIDTH-16*self.game.scale, halfHEIGHT-16*self.game.scale))
