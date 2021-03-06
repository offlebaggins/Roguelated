import tcod

from components.fighter import Fighter
from components.inventory import Inventory
from components.ai import Player
from entity import Entity
from render_functions import RenderOrder
from game_map import GameMap
from game_messages import MessageLog
from game_states import GameStates
from animation import Animator
from bodies import get_human_body

def get_constants():
    window_title = "Roguesimilar"

    screen_width: int = 80
    screen_height: int = 50

    room_max_size = 20
    room_min_size = 6
    max_rooms = 30

    min_entities_per_room = 0
    max_entities_per_room = 10

    max_items_per_room = 30

    bar_width = 20
    panel_height = 15
    panel_y = screen_height - panel_height

    map_width: int = 80
    map_height: int = screen_height - panel_height

    message_x = bar_width + 2
    message_width = screen_width - bar_width - 4 - bar_width
    message_height = panel_height - 1

    min_cell_size = 3
    max_cell_size = 6
    min_hall_width = 1
    max_hall_width = 4
    min_cells_per_block = 1
    max_cells_per_block = 4

    colors = {
        'dark_wall': tcod.Color(20, 20, 20),
        'dark_ground': tcod.Color(40, 40, 40),
        'light_wall': tcod.Color(30, 30, 30),
        'light_ground': tcod.Color(50, 50, 50)
    }

    constants = {
        'window_title': window_title,
        'screen_width': screen_width,
        'screen_height': screen_height,
        'map_width': map_width,
        'map_height': map_height,
        'room_max_size': room_max_size,
        'room_min_size': room_min_size,
        'max_rooms': max_rooms,
        'min_entities_per_room': min_entities_per_room,
        'max_entities_per_room': max_entities_per_room,
        'max_items_per_room': max_items_per_room,
        'bar_width': bar_width,
        'panel_height': panel_height,
        'panel_y': panel_y,
        'message_x': message_x,
        'message_width': message_width,
        'message_height': message_height,
        'colors': colors,
        'min_cell_size': min_cell_size,
        'max_cell_size': max_cell_size,
        'min_hall_width': min_hall_width,
        'max_hall_width': max_hall_width,
        'min_cells_per_block': min_cells_per_block,
        'max_cells_per_block': max_cells_per_block
    }

    return constants


def get_game_variables(constants):
    inventory_component = Inventory(26)
    body_component = get_human_body()
    player = Entity(int(constants['screen_width'] / 2), int(constants['screen_height'] / 2), '@', tcod.white, "Player",
                    blocks=True, render_order=RenderOrder.ACTOR, ai=Player,
                    inventory=inventory_component, body=body_component)

    entities = [player]

    animator = Animator([])

    turn_count = 0

    game_map = GameMap(constants['map_width'], constants['map_height'])
    game_map.make_map(player, entities, constants)

    message_log = MessageLog(constants['message_x'], constants['message_width'], constants['message_height'])

    game_state = GameStates.PLAYER_TURN

    return player, entities, animator, turn_count, game_map, message_log, game_state
