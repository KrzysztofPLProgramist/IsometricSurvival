from config import *
R = 8.314  # Ideal gas constant J/(mol*K)
C_v = 20.8 # Molar heat capacity J/(mol*K), approx for diatomic gases

class CellManager:
    def __init__(self, game):
        self.game = game
        self.cells = {}
        self.changes = {}
        self.cell_cache = {"yellowDot": pygame.image.load("assets/cells/yellowDot.png")}

        self.k_diff = 0.5  # diffusion coefficient
        self.k_heat = 1.0  # heat transfer coefficient

    def adjacent_cells(self, cell):
        x, y, z = cell["pos"]
        offsets = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
        for dx, dy, dz in offsets:
            neighbor = self.cells.get((x + dx, y + dy, z + dz))
            if neighbor:
                yield neighbor

    def diffuse(self, A, B, dt):
        if A["n_total"] <= 0 and B["n_total"] <= 0:
            return

        deltaP = A["P"] - B["P"]
        if abs(deltaP) < 1e-6:
            return

        # how many moles should move (scaled by dt)
        delta_n = self.k_diff * deltaP * dt / (R * ((A["T"] + B["T"]) / 2.0))
        delta_n = min(max(delta_n, -A["n_total"]), B["n_total"] + A["n_total"])  # clamp

        # move gases proportionally
        for gas, frac in A["fractions"].items():
            moved = frac * delta_n
            A["n"][gas] -= moved
            B["n"][gas] = B["n"].get(gas, 0) + moved

    # --- Heat exchange between cells ---
    def transfer_heat(self, A, B):
        dt = self.game.dt
        A = A.cell
        B = B.cell
        if A["n_total"] <= 0 or B["n_total"] <= 0:
            return

        deltaT = A["T"] - B["T"]
        if abs(deltaT) < 1e-6:
            return

        q = self.k_heat * deltaT * dt

        dT_A = -q / (A["n_total"] * C_v)
        dT_B = q / (B["n_total"] * C_v)

        A["T"] += dT_A
        B["T"] += dT_B

    # --- Update cell properties after changes ---
    def update_cell(self, cell):
        n_total = sum(cell["n"].values())
        cell["n_total"] = n_total

        if n_total > 0:
            cell["P"] = (n_total * R * cell["T"]) / cell["V"]
            cell["fractions"] = {g: n / n_total for g, n in cell["n"].items()}
        else:
            cell["P"] = 0
            cell["fractions"] = {}

    def get_cell(self, pos):
        if self.cells.get(tuple(pos)):
            return self.cells[pos]
        else:
            self.set_cell(pos, Cell(pos, self.game, "gas"))

    def set_cell(self, pos, cell):
        self.cells[tuple(pos)] = cell

    def update_gases(self):
        dt = self.game.dt

        # Diffusion
        for cell in self.tiles.values():
            for neighbor in self.adjacent_cells(cell):
                self.diffuse(cell, neighbor, dt)

        # Heat
        for cell in self.tiles.values():
            for neighbor in self.adjacent_cells(cell):
                self.transfer_heat(cell, neighbor, dt)

        # Update properties
        for cell in self.tiles.values():
            self.update_cell(cell)

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

        return int(x // 1) - 1, int(y // 1) - 1, z

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

            if cell.name == "gas":
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

            # compute how far this cell's z is from current z
            dz = pos[2] - self.game.current_z + 1

            if dz == 0 or dz == -1:
                # current layer = normal
                self.game.screen.blit(cell.image, tpos)

            elif dz == 1:
                # one layer above = faded
                img = cell.image_faded if hasattr(cell, "image_faded") else self.make_faded(cell)
                self.game.screen.blit(img, tpos)

            # deeper layers not drawn

    def make_faded(self, cell):
        img = cell.image.copy()
        img.set_alpha(120)
        cell.image_faded = img
        return img

    def iso_to_screen(self, pos):
        x, y, z = pos
        sx = (x - y) * (WALL_SIZE // 2) * self.game.scale
        sy = (x + y) * (WALL_SIZE // 4) * self.game.scale  - z * (WALL_SIZE // 2) * self.game.scale
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


class Cell:
    def __init__(self, pos, game, name="templatecell", tags=None, cell=None):
        if cell is None:
            cell = {
                "V": 1.0,  # volume (m³)
                "T": 293.15,  # temperature (K)
                "n": {"O2": 8.3, "N2": 33.2},  # moles of each gas
                "n_total": 8.3 + 33.2
            }
        if tags is None:
            tags = []
        self.game = game
        self.tags = tags
        self.cell_handler = self.game.cell_handler
        self.name = name
        self.cell = cell

        if name not in self.cell_handler.cell_cache:
            a = pygame.image.load(f"assets/cells/{name}.png")
            self.cell_handler.cell_cache[name] = a
        else:
            a = self.cell_handler.cell_cache[name]
        self.img = a
        self.image = pygame.transform.scale_by(self.img, self.game.scale)

        self.x, self.y, self.z = tuple(pos)

    def has_tag(self, tag):
        return self.tags.__contains__(tag)
