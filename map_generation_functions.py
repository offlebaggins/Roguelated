import tcod
import math

from components.fighter import Fighter
from render_functions import RenderOrder
from components.item import Item
from components.door import Door
from item_functions import heal, teleport, cast_lighting, cast_fireball, cast_explosion
from components.ai import BasicMonster
from random_utils import random_choice_from_dict
from stairs import Stairs
from random import randint
from entity import Entity
from rect import Rect
from bodies import get_human_body


def generate_prison(game_map, player, entities, max_cell_blocks, map_width, map_height):
    cell_blocks = []

    prev_x, prev_y = 0, 0

    for r in range(max_cell_blocks):
        w = 31
        h = 10
        x = randint(0, map_width - w - 1)
        y = randint(0, map_height - h - 1)

        cell_block = Rect(x, y, w, h)

        for other_cell_block in cell_blocks:
            if cell_block.intersect(other_cell_block):
                break
        else:

            cell_blocks.append(cell_block)

            hall = Rect(x + 1, y + 3, w - 1, 3)
            create_room(game_map, hall)

            for x_pos in range(x, x + w, 4):
                cell = Rect(x_pos, y, 4, 3)
                create_room(game_map, cell)
                place_entities(cell, entities, 0, 1, 3)
                place_door(x_pos + 2, y + 3, entities, game_map)

                cell = Rect(x_pos, y + 6, 4, 3)
                create_room(game_map, cell)
                place_entities(cell, entities, 1, 1, 3)
                place_door(x_pos + 2, y + 6, entities, game_map)

            if len(cell_blocks) == 1:
                player.x = x + 1
                player.y = y + 1

            else:
                path_map = tcod.map_new(game_map.width, game_map.height)
                # Create path with blocked cells walkable to carve out paths
                # This is a bad idea isnt it
                for y1 in range(game_map.height):
                    for x1 in range(game_map.width):
                        if game_map.tiles[x1][y1].blocked:
                            # Make walkable if not adjacent to unblocked tile
                            tcod.map_set_properties(path_map, x1, y1, True, False)

                        else:
                            tcod.map_set_properties(path_map, x1, y1, True, False)

                # Allocate a A* path
                my_path = tcod.path_new_using_map(path_map, 1.41)
                if x > prev_x:
                    path = my_path.get_path(x + 1, y + 5, prev_x + w, prev_y + 5)
                else:
                    path = my_path.get_path(x + w, y + 5, prev_x + 1, prev_y + 5)
                if path:
                    for point in path:
                        game_map.tiles[point[0]][point[1]].hollow()

                tcod.path_delete(my_path)
                tcod.map_delete(path_map)

        prev_x, prev_y = x, y


def generate_dungeon(game_map, max_rooms, room_min_size, room_max_size, map_width, map_height, player, entities,
                     min_entities_per_room, max_entities_per_room, max_items_per_room):
    rooms = []
    num_rooms = 0

    last_room_center_x = None
    last_room_center_y = None

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
            create_room(game_map, new_room)
            (new_x, new_y) = new_room.center()

            last_room_center_x = new_x
            last_room_center_y = new_y

            if num_rooms == 0:
                player.x = new_x
                player.y = new_y
            else:
                (prev_x, prev_y) = rooms[num_rooms - 1].center()

                create_corner_tunnel(game_map, prev_x, prev_y, new_x, new_y)
            rooms.append(new_room)

            num_rooms += 1

    stairs = Stairs(game_map.dungeon_level + 1)
    stairs_entity = Entity(last_room_center_x, last_room_center_y, '>', tcod.white, 'Stairs',
                           render_order=RenderOrder.STAIRS, structure=stairs)
    entities.append(stairs_entity)


def place_door(x, y, entities, game_map):
    game_map.tiles[x][y].hollow()

    door = Door(is_open=False)
    door_entity = Entity(x, y, '+', tcod.darker_orange, 'Door',
                         render_order=RenderOrder.STAIRS, structure=door)
    entities.append(door_entity)


def create_room(game_map, room: Rect):
    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 + 1, room.y2):
            game_map.tiles[x][y].hollow()


def create_h_tunnel(game_map, x1, x2, y):
    for x in range(min(x1, x2), max(x1, x2) + 1):
        game_map.tiles[x][y].hollow()


def create_v_tunnel(game_map, y1, y2, x):
    for y in range(min(y1, y2), max(y1, y2) + 1):
        game_map.tiles[x][y].hollow()


def create_corner_tunnel(game_map, x1, y1, x2, y2):
    if randint(0, 1) == 1:
        # first move horizontally, then vertically
        create_h_tunnel(game_map, x1, x2, y1)
        create_v_tunnel(game_map, y1, y2, x2)
    else:
        # first move vertically, then horizontally
        create_v_tunnel(game_map, y1, y2, x1)
        create_h_tunnel(game_map, x1, x2, y2)


def place_entities(room, entities, min_entities_per_room, max_entities_per_room, max_items_per_room):
    number_of_enemies = randint(min_entities_per_room, max_entities_per_room)
    number_of_items = randint(0, max_items_per_room)

    item_chances = {'healing_potion': 10, 'lightning_scroll': 10, 'fireball_scroll': 10,
                    'teleportation_potion': 10, 'explosion_scroll': 10}

    for i in range(number_of_enemies):
        # Choose location for entity
        x = randint(room.x1 + 1, room.x2 - 1)
        y = randint(room.y1 + 1, room.y2 - 1)

        if not any([entity for entity in entities if entity.x == x and entity.y == y]):
            ai_component = BasicMonster(fov_radius=10)
            body_component = get_human_body()
            monster = Entity(x, y, 'G', tcod.desaturated_green, "Goblin", blocks=True,
                             render_order=RenderOrder.ACTOR, ai=ai_component, body=body_component,
                             description="It's green and scrawny.")
            entities.append(monster)

    for i in range(number_of_items):
        x = randint(room.x1 + 1, room.x2 - 1)
        y = randint(room.y1 + 1, room.y2 - 1)

        if not any([entity for entity in entities if entity.x == x and entity.y == y]):
            item_choice = random_choice_from_dict(item_chances)
            if item_choice == 'healing_potion':
                item_component = Item(use_function=heal, amount=4)
                item = Entity(x, y, '!', tcod.light_red, 'Health Potion', render_order=RenderOrder.ITEM,
                              item=item_component)
            elif item_choice == 'lightning_scroll':
                item_component = Item(use_function=cast_lighting, damage=20, maximum_range=5)
                item = Entity(x, y, '!', tcod.lighter_yellow, 'Lightning Potion', render_order=RenderOrder.ITEM,
                              item=item_component)
            elif item_choice == 'teleportation_potion':
                item_component = Item(use_function=teleport)
                item = Entity(x, y, '!', tcod.light_blue, 'Teleportation Potion', render_order=RenderOrder.ITEM,
                              item=item_component)
            elif item_choice == 'fireball_scroll':
                item_component = Item(use_function=cast_fireball, targeting=True, damage=10, radius=3)
                item = Entity(x, y, 'I', tcod.desaturated_yellow, "Fireball Scroll", render_order=RenderOrder.ITEM,
                              item=item_component)
            elif item_choice == 'explosion_scroll':
                item_component = Item(use_function=cast_explosion, targeting=True, damage=10, radius=5,
                                      targeting_radius=6)
                item = Entity(x, y, 'I', tcod.light_orange, "Explosion Scroll", render_order=RenderOrder.ITEM,
                              item=item_component)

            entities.append(item)


def get_distance(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    return math.sqrt(dx ** 2 + dy ** 2)
