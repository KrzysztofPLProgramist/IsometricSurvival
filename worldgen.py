from random import randint
from draw import CellManager, Cell

class WorldGenerator:

    def __init__(self, cell_manager: CellManager):
        self.cell_manager = cell_manager
    def generate(self):
        self.cell_manager.load_rect("stone", (-10, -10, -2), (20, 20, 1), None)
        for x in range(-10, 10):
            for y in range(-10, 10):
                if (randint(0, 1) == 0):
                    self.cell_manager.set_cell(Cell((x, y, -1,), self.cell_manager.game, "stone", ["solid", "can_stand_on"]))