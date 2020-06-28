import tcod

from components.fighter import Fighter
from components.inventory import Inventory
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

    map_width: int = 80
    map_height: int = 43

    room_max_size = 20
    room_min_size = 6
    max_rooms = 30

    min_entities_per_room = 0
    max_entities_per_room = 10

    max_items_per_room = 30

    bar_width = 20
    panel_height = 7
    panel_y = screen_height - panel_height

    message_x = bar_width + 2
    message_width = screen_width - bar_width - 2
    message_height = panel_height - 1

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
        'colors': colors
    }

    return constants


def get_game_variables(constants):
    fighter_component = Fighter(hp=30, defense=2, power=5)
    inventory_component = Inventory(26)
    body_component = get_human_body()
    player = Entity(int(constants['screen_width'] / 2), int(constants['screen_height'] / 2), '@', tcod.white, "Player",
                    blocks=True, render_order=RenderOrder.ACTOR, ai=None, fighter=fighter_component,
                    inventory=inventory_component, body=body_component)

    entities = [player]

    animator = Animator([])

    game_map = GameMap(constants['map_width'], constants['map_height'])
    game_map.make_map(constants['max_rooms'], constants['room_min_size'], constants['room_max_size'],
                      constants['map_width'], constants['map_height'], player, entities,
                      constants['min_entities_per_room'], constants['max_entities_per_room'],
                      constants['max_items_per_room'])

    message_log = MessageLog(constants['message_x'], constants['message_width'], constants['message_height'])

    game_state = GameStates.PLAYER_TURN

    return player, entities, animator, game_map, message_log, game_state
