from pygame.examples.grid import TILE_SIZE

from config import *



class CellManager:
    def __init__(self, game):
        self.game = game
        self.cells = {}
        self.changes = {}
        self.cell_cache = {"yellowDot": pygame.image.load("assets/cells/yellowDot.png"), "empty": None}

        self.diffusion_speed = 0.5
        self.heat_transfer_speed = 1.0  # heat transfer coefficient

    def adjacent_cells(self, cell):
        x, y, z = cell["pos"]
        offsets = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
        for dx, dy, dz in offsets:
            neighbor = self.cells.get((x + dx, y + dy, z + dz))
            if neighbor:
                yield neighbor

    def get_cell(self, pos):
        if self.cells.get(tuple(pos)):
            return self.cells[pos]
        else:
            self.set_cell(Cell(pos, self.game, "empty"))
            return self.cells[pos]

    def simulate(self):
        for i in self.cells:
            i.update()

    def set_cell(self, cell):
        self.cells[(cell.x, cell.y, cell.z)] = cell

    def cell_distance(self, a, b):
        """
        Returns distance between two cells (in cells).
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
                    self.cells[pos] = Cell(pos, self.game, name=name, tags=tags)

    def screen_to_iso(self, mouse_pos, z=0):
        mx, my = mouse_pos

        mx -= halfWIDTH
        my -= halfHEIGHT - 16 * self.game.scale

        A = mx / (WALL_SIZE // 2 * self.game.scale)
        B = (my + z * (WALL_SIZE // 2 * self.game.scale)) / (WALL_SIZE // 4 * self.game.scale)

        x = (A + B) / 2 + self.game.player.pos[0]
        y = (B - A) / 2 + self.game.player.pos[1]

        return int(x // 1) - 1 - self.game.current_z, int(y // 1) - 1 - self.game.current_z, z

    def draw(self):
        """
        Draw cells with z_offset controlling which layers are visible.
        - current layer = fully visible
        - one layer above = faded
        - deeper layers = hidden
        """
        # sort by depth for proper isometric rendering
        for pos, cell in sorted(self.cells.items(), key=lambda item: (item[0][0] + item[0][1], item[0][2])):
            cell: cell

            if cell.name == "empty":
                continue

            ppos = list(pos)
            ppos[0] -= self.game.player.pos[0]
            ppos[1] -= self.game.player.pos[1]
            ppos[2] -= self.game.player.pos[2]
            tpos = self.iso_to_screen(ppos)
            tpos[0] += halfWIDTH - (WALL_SIZE//2) * self.game.scale
            # tpos[1] += halfHEIGHT + (cell_SIZE//2-2) * self.game.scale
            tpos[1] += halfHEIGHT - (WALL_SIZE//2) * self.game.scale

            if cell is self.game.current_cell:
                tpos[1] += 0.1

            if 0+WALL_SIZE*self.game.scale > tpos[0] > WIDTH:
                continue
            if 0+WALL_SIZE*self.game.scale > tpos[1] > HEIGHT:
                continue

            # compute how far this cell's z is from current z
            dz = pos[2] - self.game.current_z + 1
            # if dz == 0 or (pos[2] >= self.game.player.pos[2] and (pos[1] > self.game.player.pos[1] and pos[0] > self.game.player.pos[0])):

            if 1 >= dz >= -1:
                # current layer = normal
                self.game.screen.blit(cell.image, tpos)
            elif dz == 0:
                # one layer above = faded
                img = cell.image_faded if hasattr(cell, "image_faded") else self.make_faded(cell)
                self.game.screen.blit(img, tpos)


            # deeper layers not drawn

    def make_faded(self, cell):
        img = cell.image.copy()
        img.set_alpha(60)
        cell.image_faded = img
        return img

    def iso_to_screen(self, pos):
        x, y, z = pos
        sx = (x - y) * (WALL_SIZE // 2) * self.game.scale
        sy = (x + y) * (WALL_SIZE // 4) * self.game.scale  - z * (WALL_SIZE // 2) * self.game.scale
        return [sx, sy]


class Cell:
    def __init__(self, pos, game, name="templateCell", tags=None, cell=None):
        if cell is None:
            cell = {
                "temperature": 293,  # temperature (K)
                "gas": {"O2": 0.2, "N2": 0.8},  # 1m^3 of each gas
                "gas_total": 1,
                "fluid": {},
                "fluid_total": 0
            }
        if tags is None:
            tags = []
        self.game = game
        self.tags = tags
        self.cell_manager = self.game.cell_manager
        self.name = name
        self.cell = cell

        if name not in self.cell_manager.cell_cache:
            a = pygame.image.load(f"assets/cells/{name}.png")
            self.cell_manager.cell_cache[name] = a
        else:
            a = self.cell_manager.cell_cache[name]
        self.img = a
        self.image = None
        if self.img is not None: self.image = pygame.transform.scale_by(self.img, self.game.scale)

        self.x, self.y, self.z = tuple(pos)

    def update(self):
        neighbors = self.cell_manager.adjacent_cells
        neighbors.shuffle()
        for i in neighbors:
            if self.cell["gas_total"] > i.cell["gas_total"]:
                difference = self.cell["gas_total"] - i.cell["gas_total"]
                calc_difference = difference * self.cell_manager.diffusion_speed()
                i.cell["gas_total"] += calc_difference
                self.cell["gas_total"] -= calc_difference

    def has_tag(self, tag):
        return self.tags.__contains__(tag)
