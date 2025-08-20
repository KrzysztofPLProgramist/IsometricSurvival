def draw(self):
    """
    Draw tiles with z_offset controlling which layers are visible.
    - current layer = fully visible
    - one layer below = faded
    - deeper layers = hidden
    """
    # sort by depth for proper isometric rendering
    for pos, tile in sorted(self.tiles.items(), key=lambda item: (item[0][0] + item[0][1], item[0][2])):
        tile: Tile
        tpos = self.iso_to_screen(pos)

        # compute how far this tile's z is from current z_offset
        dz = pos[2] - self.game.z_offset

        if dz == 0:
            # current layer = normal
            self.game.screen.blit(tile.image, tpos)

        elif dz == -1:
            # one layer below = faded
            img = tile.image_faded if hasattr(tile, "image_faded") else self._make_faded(tile)
            self.game.screen.blit(img, tpos)

        # deeper layers not drawn