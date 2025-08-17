from config import *

class Player:
    def __init__(self, game, pos=[1,1,0]):
        self.game = game
        self.pos = pos
        self.img = pygame.image.load("assets/player/player.png")
        self.image = pygame.transform.scale_by(self.img, self.game.scale)

    def update(self):
        pass

    def draw(self):
        self.game.screen.blit(self.image, (halfWIDTH-16*self.game.scale, halfHEIGHT))
