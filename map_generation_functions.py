import tcod
import math
import random

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


def generate_prison(game_map, player, entities, min_cell_size, max_cell_size, min_hall_width, max_hall_width,
                    min_cells_per_block, max_cells_per_block):
    room_size = randint(5, 7)

    x = randint(0, game_map.width - room_size - 1)
    y = randint(0, game_map.height - room_size - 1)
    player.x, player.y = x + 1, y + 1

    start_room = Rect(x, y, room_size, room_size)
    create_room(game_map, start_room)
    connector_rooms = [start_room]

    for connector_room in connector_rooms:
        # Create new cell block for each side of connector room
        place_entities(connector_room, entities, 0, 1, 5)

        for i in range(1000):  # this is dumb maybe?
            # Attempt to add cell block on right side
            cell_width, cell_height = randint(min_cell_size, max_cell_size), randint(min_cell_size, max_cell_size)
            hall_width, hall_height = cell_width * randint(min_cells_per_block, max_cells_per_block), randint(
                min_hall_width, max_hall_width)
            x = connector_room.x2
            y = int((connector_room.y1 + connector_room.y2) / 2) - cell_height - int(hall_height / 2)
            double_sided = random.choice([True, False])
            if generate_cell_block(game_map, entities, x, y, hall_width, hall_height, double_sided, cell_width,
                                   cell_height):
                connector_rooms.extend(
                    add_connector_rooms(game_map, x, y, hall_width, hall_height, cell_width, cell_height))

            # Attempt to add cell block on left side
            cell_width, cell_height = randint(min_cell_size, max_cell_size), randint(min_cell_size, max_cell_size)
            hall_width, hall_height = cell_width * randint(min_cells_per_block, max_cells_per_block), randint(
                min_hall_width, max_hall_width)
            x = connector_room.x1 - hall_width
            y = int((connector_room.y1 + connector_room.y2) / 2) - cell_height - int(hall_height / 2)
            double_sided = random.choice([True, False])
            if generate_cell_block(game_map, entities, x, y, hall_width, hall_height, double_sided, cell_width,
                                   cell_height):
                connector_rooms.extend(
                    add_connector_rooms(game_map, x, y, hall_width, hall_height, cell_width, cell_height))

            # Attempt to add cell block on top
            cell_width, cell_height = randint(min_cell_size, max_cell_size), randint(min_cell_size, max_cell_size)
            hall_width, hall_height = randint(min_hall_width, max_hall_width), cell_height * randint(
                min_cells_per_block, max_cells_per_block)
            x = int((connector_room.x1 + connector_room.x2) / 2) - cell_width - int(hall_width / 2)
            y = connector_room.y1 - hall_height
            double_sided = random.choice([True, False])
            if generate_cell_block(game_map, entities, x, y, hall_width, hall_height, double_sided, cell_width,
                                   cell_height):
                connector_rooms.extend(
                    add_connector_rooms(game_map, x, y, hall_width, hall_height, cell_width, cell_height))

            # Attempt to add cell block on bottom
            cell_width, cell_height = randint(min_cell_size, max_cell_size), randint(min_cell_size, max_cell_size)
            hall_width, hall_height = randint(min_hall_width, max_hall_width), cell_height * randint(
                min_cells_per_block, max_cells_per_block)
            x = int((connector_room.x1 + connector_room.x2) / 2) - cell_width - int(hall_width / 2)
            y = connector_room.y2
            double_sided = random.choice([True, False])
            if generate_cell_block(game_map, entities, x, y, hall_width, hall_height, double_sided, cell_width,
                                   cell_height):
                connector_rooms.extend(
                    add_connector_rooms(game_map, x, y, hall_width, hall_height, cell_width, cell_height))


def add_connector_rooms(game_map, x, y, hall_width, hall_height, cell_width, cell_height):
    connector_rooms = []

    if hall_width > hall_height:
        # Add connector rooms to the left & right
        room_size = hall_height + (cell_height * 2) + 3
        right_room = Rect(x + hall_width, y, room_size, room_size)
        if create_room(game_map, right_room, no_overlap=True):
            connector_rooms.append(right_room)
        left_room = Rect(x - room_size, y, room_size, room_size)
        if create_room(game_map, left_room, no_overlap=True):
            connector_rooms.append(left_room)
    else:
        # Add connector rooms above/below
        room_size = hall_width + (cell_width * 2) + 3
        top_room = Rect(x, y - room_size, room_size, room_size)
        if create_room(game_map, top_room, no_overlap=True):
            connector_rooms.append(top_room)
        bottom_room = Rect(x, y + hall_height, room_size, room_size)
        if create_room(game_map, bottom_room, no_overlap=True):
            connector_rooms.append(bottom_room)

    return connector_rooms


def generate_level(game_map, player, entities, max_cell_blocks, map_width, map_height):
    cell_blocks = []

    for i in range(max_cell_blocks):
        # Get position, width, & height
        cell_width, cell_height = randint(3, 5), randint(3, 5)

        if randint(0, 1) == 1:
            hall_width = randint(5, 30)
            hall_height = randint(1, 5)
            w = hall_width
            h = hall_height + (cell_height * 2) + 2
        else:
            hall_width = randint(1, 5)
            hall_height = randint(5, 30)
            w = hall_width + (cell_width * 2) + 2
            h = hall_height

        x, y = randint(0, map_width - w), randint(0, map_height - h)

        for cell_block in cell_blocks:
            if Rect(x, y, w, h).intersect(cell_block):
                max_cell_blocks += 1
                break
        else:
            player.x = x + 1
            player.y = y + 1
            generate_cell_block(game_map, entities, x, y, hall_width, hall_height,
                                cell_width=cell_width, cell_height=cell_height, double_sided=True)
            cell_blocks.append(Rect(x, y, w, h))


def generate_cell_block(game_map, entities, x_start, y_start, hall_width, hall_height, double_sided: bool = True,
                        cell_width: int = 3, cell_height: int = 4):
    if hall_width > hall_height:
        # Horizontal cell block
        cell_count = int(hall_width / cell_width)
        width = x_start + hall_width
        height = y_start + hall_height + (cell_height * 2)
    else:
        # Vertical cell block
        cell_count = int(hall_height / cell_height)
        width = x_start + hall_width + (cell_width * 2)
        height = y_start + hall_height

    x = x_start
    y = y_start

    # Check if cell block is within map and there are no other rooms in the way
    if width < game_map.width - 1 and x > 0 and height < game_map.height - 1 and y > 0:
        # TODO: Map Gen: Stop cell blocks from overlapping rooms (something to fix in game_map.rect_is_blocked() maybe?)
        if game_map.rect_is_blocked(Rect(x, y, width - x, height - y)):
            for i in range(cell_count):
                if hall_width > hall_height:
                    # Create horizontal cell block segment
                    # Create top cell
                    create_room(game_map, Rect(x, y, cell_width, cell_height))
                    place_door(x + int(cell_width / 2), y + cell_height, entities, game_map)

                    # Create hall segment
                    for _x in range(x, x + cell_width + 1):
                        for _y in range(y + cell_height + 1, y + cell_height + 1 + hall_height):
                            game_map.tiles[_x][_y].hollow()
                    # Create bottom room
                    if double_sided:
                        create_room(game_map, Rect(x, y + 1 + cell_height + hall_height, cell_width, cell_height))
                        place_door(x + int(cell_width / 2), y + cell_height + hall_height + 1, entities, game_map)

                    x += cell_width
                else:
                    # Create vertical cell block segment
                    create_room(game_map, Rect(x, y, cell_width, cell_height))
                    place_door(x + cell_width, y + int(cell_height / 2), entities, game_map)

                    # Create hall segment
                    for _x in range(x + cell_width + 1, x + cell_width + 1 + hall_width):
                        for _y in range(y, y + cell_height + 1):
                            game_map.tiles[_x][_y].hollow()

                    # Create right room
                    if double_sided:
                        create_room(game_map, Rect(x + cell_width + 1 + hall_width, y, cell_width, cell_height))
                        place_door(x + cell_width + hall_width + 1, y + int(cell_height / 2), entities, game_map)

                    y += cell_height
            return True

    return False


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


def create_room(game_map, room: Rect, no_overlap=False):
    if room.x1 < 0 or room.x2 > game_map.width or room.y1 < 0 or room.y2 > game_map.height:
        return False

    if no_overlap:
        if not game_map.rect_is_blocked(room):
            return False

    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 + 1, room.y2):
            game_map.tiles[x][y].hollow()
    return True


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
