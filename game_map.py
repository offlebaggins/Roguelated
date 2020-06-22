import tcod

from random import randint

from tile import Tile
from rect import Rect
from entity import Entity
from components.ai import BasicMonster
from components.fighter import Fighter
from render_functions import RenderOrder
from components.item import Item
from item_functions import heal, teleport, cast_lighting, cast_fireball, cast_explosion


class GameMap:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()

    def initialize_tiles(self):
        tiles = [[Tile(True) for y in range(self.height)] for x in range(self.width)]
        return tiles

    def place_entities(self, room, entities, min_entities_per_room, max_entities_per_room, max_items_per_room):
        number_of_enemies = randint(min_entities_per_room, max_entities_per_room)
        number_of_items = randint(0, max_items_per_room)

        for i in range(number_of_enemies):
            # Choose location for entity
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)

            if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                ai_component = BasicMonster(fov_radius=10)
                fighter_component = Fighter(5, 0, 3)
                monster = Entity(x, y, 'G', tcod.desaturated_green, "Goblin", blocks=True,
                                 render_order=RenderOrder.ACTOR, ai=ai_component, fighter=fighter_component)
                entities.append(monster)

        for i in range(number_of_items):
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)

            if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                number = randint(0, 4)
                if number == 0:
                    item_component = Item(use_function=heal, amount=4)
                    item = Entity(x, y, '!', tcod.light_red, 'Health Potion', render_order=RenderOrder.ITEM,
                                  item=item_component)
                elif number == 1:
                    item_component = Item(use_function=cast_lighting, damage=20, maximum_range=5)
                    item = Entity(x, y, '!', tcod.lighter_yellow, 'Lightning Potion', render_order=RenderOrder.ITEM,
                                  item=item_component)
                elif number == 2:
                    item_component = Item(use_function=teleport)
                    item = Entity(x, y, '!', tcod.light_blue, 'Teleportation Potion', render_order=RenderOrder.ITEM,
                                  item=item_component)
                elif number == 3:
                    item_component = Item(use_function=cast_fireball, targeting=True, damage=10, radius=3)
                    item = Entity(x, y, 'I', tcod.desaturated_yellow, "Fire Ball Scroll", render_order=RenderOrder.ITEM,
                                  item=item_component)
                elif number == 4:
                    item_component = Item(use_function=cast_explosion, targeting=True, damage=10, radius=5)
                    item = Entity(x, y, 'I', tcod.light_orange, "Explosion Scroll", render_order=RenderOrder.ITEM,
                                  item=item_component)

                entities.append(item)

    def make_map(self, max_rooms, room_min_size, room_max_size, map_width, map_height, player, entities,
                 min_entities_per_room, max_entities_per_room, max_items_per_room):

        self.tiles = self.initialize_tiles()

        rooms = []
        num_rooms = 0

        for r in range(max_rooms):
            w = randint(room_min_size, room_max_size)
            h = randint(room_min_size, room_max_size)
            x = randint(0, map_width - w - 1)
            y = randint(0, map_height - h - 1)

            new_room = Rect(x, y, w, h)

            for other_room in rooms:
                if new_room.intersect(other_room):
                    break
            else:
                # new room does not intersect any other rooms
                self.create_room(new_room)
                (new_x, new_y) = new_room.center()

                if num_rooms == 0:
                    player.x = new_x
                    player.y = new_y
                else:
                    (prev_x, prev_y) = rooms[num_rooms - 1].center()

                    if randint(0, 1) == 1:
                        # first move horizontally, then vertically
                        self.create_h_tunnel(prev_x, new_x, prev_y)
                        self.create_v_tunnel(prev_y, new_y, new_x)
                    else:
                        # first move vertically, then horizontally
                        self.create_v_tunnel(prev_y, new_y, prev_x)
                        self.create_h_tunnel(prev_x, new_x, new_y)

                rooms.append(new_room)
                self.place_entities(new_room, entities, min_entities_per_room, max_entities_per_room,
                                    max_items_per_room)
                num_rooms += 1

    def create_room(self, room):
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                self.tiles[x][y].blocked = False
                self.tiles[x][y].block_sight = False

    def create_h_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def create_v_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def is_blocked(self, x, y):
        if self.tiles[x][y].blocked:
            return True
        return False
