from config import *

class TileManager:
    def __init__(self, game):
        self.game = game
        self.tiles = {}
        self.changes = {}
        self.tile_cache = {"yellowDot": pygame.image.load("assets/tiles/yellowDot.png")}

    def get_tile(self, pos):
        if self.tiles.get(tuple(pos)):
            return self.tiles[pos]
        else:
            self.set_tile(pos, Tile(pos, self.game, "gas"))

    def set_tile(self, pos, tile):
        self.tiles[tuple(pos)] = tile

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
                    self.tiles[pos] = Tile(pos, self.game, name=name, tags=tags)

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
        """
        Draw tiles with z_offset controlling which layers are visible.
        - current layer = fully visible
        - one layer above = faded
        - deeper layers = hidden
        """
        # sort by depth for proper isometric rendering
        for pos, tile in sorted(self.tiles.items(), key=lambda item: (item[0][0] + item[0][1], item[0][2])):
            tile: Tile

            if tile.name == "gas":
                continue

            ppos = list(pos)
            ppos[0] -= self.game.player.pos[0]
            ppos[1] -= self.game.player.pos[1]
            ppos[2] -= self.game.player.pos[2]
            tpos = self.iso_to_screen(ppos)
            tpos[0] += halfWIDTH - (TILE_SIZE//2) * self.game.scale
            # tpos[1] += halfHEIGHT + (TILE_SIZE//2-2) * self.game.scale
            tpos[1] += halfHEIGHT - (TILE_SIZE//2) * self.game.scale

            if tile is self.game.current_tile:
                tpos[1] += 0.1

            # compute how far this tile's z is from current z
            dz = pos[2] - self.game.current_z + 1

            if dz == 0 or dz == -1:
                # current layer = normal
                self.game.screen.blit(tile.image, tpos)

            elif dz == 1:
                # one layer above = faded
                img = tile.image_faded if hasattr(tile, "image_faded") else self.make_faded(tile)
                self.game.screen.blit(img, tpos)

            # deeper layers not drawn

    def make_faded(self, tile):
        img = tile.image.copy()
        img.set_alpha(120)
        tile.image_faded = img
        return img

    def iso_to_screen(self, pos):
        x, y, z = pos
        sx = (x - y) * (TILE_SIZE // 2) * self.game.scale
        sy = (x + y) * (TILE_SIZE // 4) * self.game.scale  - z * (TILE_SIZE // 2) * self.game.scale
        return [sx, sy]

    def moles_in_cube(self, pressure_pa=101325, temperature_k=290.15, volume_m3=1.0):
        """
        Calculate number of moles of ideal gas in a cube.

        pressure_pa: Pressure in Pascals (Pa)
        temperature_k: Temperature in Kelvin (K)
        volume_m3: Volume in cubic meters (default=1 m³)

        Returns: number of moles
        """
        R = 8.314462618  # J/(mol*K)
        return (pressure_pa * volume_m3) / (R * temperature_k)


class Tile:
    def __init__(self, pos, game, name="templateTile", tags=None, gas=None, temperature=290.15, pressure=101325):
        if gas is None:
            gas = {"O2": 8.3, "N2": 33.2}
        if tags is None:
            tags = []
        self.game = game
        self.tags = tags
        self.tile_handler = self.game.tile_handler
        self.name = name
        self.gas = gas
        self.temperature = temperature

        if name not in self.tile_handler.tile_cache:
            a = pygame.image.load(f"assets/tiles/{name}.png")
            self.tile_handler.tile_cache[name] = a
        else:
            a = self.tile_handler.tile_cache[name]
        self.img = a
        self.image = pygame.transform.scale_by(self.img, self.game.scale)

        self.x, self.y, self.z = tuple(pos)

    def has_tag(self, tag):
        return self.tags.__contains__(tag)
