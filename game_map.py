import tcod

from random import randint

from tile import Tile
from map_generation_functions import generate_prison, generate_cell_block


class GameMap:
    def __init__(self, width, height, dungeon_level=1):
        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()
        self.dungeon_level = dungeon_level

    def initialize_tiles(self):
        tiles = [[Tile(True) for y in range(self.height)] for x in range(self.width)]
        return tiles

    def make_map(self, player, entities, constants):
        self.tiles = self.initialize_tiles()

        generate_prison(self, player, entities, constants['min_cell_size'], constants['max_cell_size'],
                        constants['min_hall_width'], constants['max_hall_width'], constants['min_cells_per_block'],
                        constants['max_cells_per_block'])

    def next_floor(self, player, constants):
        self.dungeon_level += 1
        entities = [player]

        self.tiles = self.initialize_tiles()
        self.make_map(player, entities, constants)

        # player.fighter.heal(player.fighter.max_hp // 2)

        return entities

    def is_blocked(self, x, y):
        if self.tiles[x][y].blocked:
            return True
        return False

    def rect_is_blocked(self, rect) -> bool:
        for x in range(rect.x1 + 1, rect.x2):
            for y in range(rect.y1 + 1, rect.y2):
                if self.tiles[x][y]:
                    if not self.tiles[x][y].blocked:
                        return False
        return True
