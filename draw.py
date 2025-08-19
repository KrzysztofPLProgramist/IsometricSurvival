from config import *

class TileManager:
    def __init__(self, game):
        self.game = game
        self.tiles = {}
        self.changes = {}
        self.tile_cache = {"yellowDot": pygame.image.load("assets/tiles/yellowDot.png")}

    def get_tile(self, pos):
        return self.tiles[pos] if self.tiles.get(pos) else None

    def tile_distance(self, a, b):
        """
        Returns distance between two tiles (in tiles).
        a, b = (x, y, z) tuples
        """
        ax, ay, az = a
        bx, by, bz = b

        dx = ax - bx
        dy = ay - by
        dz = az - bz

        # 3D Manhattan distance (grid steps)
        return abs(dx) + abs(dy) + abs(dz)

    def load_rect(self, name, start_pos, size, tags=None):
        if tags is None:
            tags = ["solid", "can_stand_on"]
        for x in range(size[0]):
            for y in range(size[1]):
                for z in range(size[2]):
                    pos = (start_pos[0] + x, start_pos[1] + y, start_pos[2] + z)
                    self.tiles[pos] = Tile(pos[0], pos[1], pos[2], self.game, self, name=name, tags=tags)

    def screen_to_iso(self, mouse_pos, z=0):
        mx, my = mouse_pos

        mx -= halfWIDTH
        my -= halfHEIGHT - 16 * self.game.scale

        A = mx / (TILE_SIZE // 2 * self.game.scale)
        B = (my + z * (TILE_SIZE // 2 * self.game.scale)) / (TILE_SIZE // 4 * self.game.scale)

        x = (A + B) / 2 + self.game.player.pos[0]
        y = (B - A) / 2 + self.game.player.pos[1]

        return int(x // 1) - 1, int(y // 1) - 1, z


    def draw(self):
        for pos, tile in sorted(self.tiles.items(), key=lambda item: (item[0][0] + item[0][1], item[0][2])):
            tile:Tile

            underground_check = self.tiles.get((pos[0],pos[1],pos[2]+1))
            if underground_check:
                if underground_check.get_tag("solid"):
                    continue
            dpos = list(pos)
            dpos[0] -= self.game.player.pos[0]
            dpos[1] -= self.game.player.pos[1]
            dpos[2] -= self.game.player.pos[2]
            tpos = self.iso_to_screen(dpos)
            tpos[0] += halfWIDTH - (TILE_SIZE//2) * self.game.scale
            tpos[1] += halfHEIGHT - (TILE_SIZE//2-2) * self.game.scale

            if pos[2]-1<=self.game.current_z:
                a = 3
                if self.game.player.pos[0] <= pos[0] <= self.game.player.pos[0]+a and \
                    self.game.player.pos[1] <= pos[1]<=self.game.player.pos[1]+a and pos[2]==self.game.player.pos[2]:
                    img = tile.image.copy()
                    if self.game.player.pos[0]+1 >= pos[0] and self.game.player.pos[1]+1 >= pos[1]:
                        img.set_alpha(70)
                    else:
                        img.set_alpha(30)
                    self.game.screen.blit(img, tpos)
                else:
                    self.game.screen.blit(tile.image, tpos)
            elif pos[2]-2<=self.game.current_z:
                img = tile.image.copy()
                img.set_alpha(120)
                self.game.screen.blit(img, tpos)

            if self.game.calculated_mouse_pos == (pos[0],pos[1],pos[2]+1) and not underground_check:
                # dpos[2] += 0.05
                self.game.screen.blit(self.tile_cache.get("yellowDot"), (tpos[0],tpos[1]+TILE_SIZE*self.game.scale))
                print("d")
                pass

    def iso_to_screen(self, pos):
        x, y, z = pos
        # z += self.game.current_z
        sx = (x - y) * (TILE_SIZE // 2) * self.game.scale
        sy = (x + y) * (TILE_SIZE // 4) * self.game.scale  - z * (TILE_SIZE // 2) * self.game.scale
        return [sx, sy]

class Tile:
    def __init__(self, x, y, z, game, tile_handler, name="templateTile", tags=None):
        if tags is None:
            tags = []
        self.game = game
        self.tags = tags
        self.tile_handler = tile_handler
        self.name = name
        if name not in self.tile_handler.tile_cache:
            a = pygame.image.load(f"assets/tiles/{name}.png")
            tile_handler.tile_cache[name] = a
        else:
            a = tile_handler.tile_cache[name]
        self.img = a
        self.image = pygame.transform.scale_by(self.img, self.game.scale)

        self.x, self.y, self.z = x,y,z

    def get_tag(self, tag):
        return self.tags.__contains__(tag)
