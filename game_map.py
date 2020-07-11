import tcod

from random import randint

from tile import Tile
from map_generation_functions import generate_dungeon, generate_prison, generate_cell_block


class GameMap:
    def __init__(self, width, height, dungeon_level=1):
        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()
        self.dungeon_level = dungeon_level

    def initialize_tiles(self):
        tiles = [[Tile(True) for y in range(self.height)] for x in range(self.width)]
        return tiles

    def make_map(self, max_rooms, room_min_size, room_max_size, map_width, map_height, player, entities,
                 min_entities_per_room, max_entities_per_room, max_items_per_room):
        self.tiles = self.initialize_tiles()
        # generate_dungeon(self, max_rooms, room_min_size, room_max_size, map_width, map_height, player, entities,
        #          min_entities_per_room, max_entities_per_room, max_items_per_room)

        # generate_prison(self, player, entities, max_rooms, map_width, map_height)
        generate_cell_block(self, entities, player.x - 15, player.y - 15, randint(1, 5), randint(15, 30),
                            cell_width=randint(3, 5), cell_height=randint(3, 5))

    def next_floor(self, player, constants):
        self.dungeon_level += 1
        entities = [player]

        self.tiles = self.initialize_tiles()
        self.make_map(constants['max_rooms'], constants['room_min_size'], constants['room_max_size'],
                      constants['map_width'], constants['map_height'], player, entities,
                      constants['min_entities_per_room'], constants['max_entities_per_room'],
                      constants['max_items_per_room'])

        player.fighter.heal(player.fighter.max_hp // 2)

        return entities

    def is_blocked(self, x, y):
        if self.tiles[x][y].blocked:
            return True

        return False
