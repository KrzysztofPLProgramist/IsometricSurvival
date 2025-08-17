from config import *

class TileManager:
    def __init__(self, game):
        self.game = game
        self.tiles = {}
        self.changes = {}

    def load_rect(self, name, start_pos, size):
        for x in range(size[0]):
            for y in range(size[1]):
                for z in range(size[2]):
                    pos = (start_pos[0] + x, start_pos[1] + y, start_pos[2] + z)
                    self.tiles[pos] = Tile(pos[0], pos[1], pos[2], self.game, name=name)

    def draw(self):
        for pos, tile in sorted(self.tiles.items(), key=lambda item: (item[0][0] + item[0][1], item[0][2])):
            tile:Tile
            tpos = self.iso_to_screen(pos)
            tpos[0] += self.game.scroll[0]
            tpos[1] += self.game.scroll[1]
            if pos[2]+1<=self.game.current_z:
                self.game.screen.blit(tile.image, tpos)
            elif pos[2]<=self.game.current_z:
                img = tile.image.copy()
                img.set_alpha(120)
                self.game.screen.blit(img, tpos)

    def iso_to_screen(self, pos):
        x, y, z = pos
        # z += self.game.current_z
        sx = (x - y) * (TILE_SIZE // 2) * self.game.scale
        sy = (x + y) * (TILE_SIZE // 4) * self.game.scale  - z * (TILE_SIZE // 2) * self.game.scale
        return [sx, sy]

class Tile:
    def __init__(self, x, y, z, game, name="templateTile"):
        self.game = game
        self.name = name
        self.image = pygame.image.load(f"assets/tiles/{self.name}.png")
        self.img = self.image
        self.image = pygame.transform.scale_by(self.img, self.game.scale)

        self.x, self.y, self.z = x,y,z
