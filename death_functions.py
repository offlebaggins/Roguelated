import tcod

from game_states import GameStates
from render_functions import RenderOrder
from game_messages import Message
from components.item import Item


def kill_player(player):
    player.char = '%'
    player.color = tcod.dark_red

    return Message('You died!', tcod.dark_red), GameStates.PLAYER_DEAD


def kill_entity(entity):
    death_message = Message("The {0} dies!".format(entity.name), tcod.dark_red)

    entity.char = '%'
    entity.color = tcod.dark_red
    entity.blocks = False
    entity.ai = None
    entity.fighter = None
    entity.name = entity.name + " corpse"
    entity.render_order = RenderOrder.CORPSE
    entity.item = Item()

    return death_message