import tcod

from tile_components.tile_types import TileType, Lava


class Tile:
    """
        A tile on a map. It may or may not be blocked, and may or may not block sight.
    """

    def __init__(self, blocked, block_sight=None, name=None, light_color=None, dark_color=None, description=None,
                 tile_type: TileType = None):
        self.blocked = blocked

        # By default, if a tile is blocked it blocks sight
        if block_sight is None:
            block_sight = blocked

        if light_color:
            self.light_color = light_color
        else:
            self.light_color = tcod.Color(30, 30, 30)

        if dark_color:
            self.dark_color = dark_color
        else:
            self.dark_color = tcod.Color(20, 20, 20)

        self.block_sight = block_sight

        self.name = name

        self.explored = True # False

        self.description = description

        self.type = self.set_type(tile_type)

    def set_type(self, tile_type):
        self.type = tile_type

        if self.type:
            self.type.set_owner(self)

        return tile_type

    def overlap_entity(self, entity):
        results = []

        if self.type:
            overlap_results = self.type.overlap_entity(entity)
            results.extend(overlap_results)

        return results

    def hollow(self):
        self.light_color = tcod.Color(50, 50, 50)
        self.dark_color = tcod.Color(40, 40, 40)
        self.blocked = False
        self.block_sight = False
