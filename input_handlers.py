import tcod.event

from actions import Action, ActionType
from game_states import GameStates


def handle_keys_main_menu(key):
    action: [Action, None] = None

    if key == tcod.event.K_a:
        action = Action(ActionType.NEW_GAME)
    elif key == tcod.event.K_b:
        action = Action(ActionType.LOAD_GAME)
    elif key in (tcod.event.K_c, tcod.event.K_ESCAPE):
        action = Action(ActionType.ESCAPE)

    return action


def handle_keys(key, game_state):
    action: [Action, None] = None

    if game_state == GameStates.PLAYER_TURN:
        return handle_keys_player_turn(key)
    elif game_state == GameStates.PLAYER_DEAD:
        return handle_keys_player_dead(key)
    elif game_state in (GameStates.TARGETING, GameStates.LOOKING):
        return handle_keys_targeting(key)
    elif game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY,
                        GameStates.SWAP_APPENDAGE, GameStates.TARGET_APPENDAGE):
        return handle_keys_choose_option(key)
    return action


def handle_keys_player_turn(key) -> [Action, None]:
    action: [Action, None] = None

    if key == tcod.event.K_g:
        action = Action(ActionType.GRAB)

    elif key == tcod.event.K_a:
        action = Action(ActionType.TOGGLE_INVENTORY)

    elif key == tcod.event.K_d:
        action = Action(ActionType.DROP_INVENTORY_ITEM)

    elif key == tcod.event.K_PERIOD:
        action = Action(ActionType.WAIT)

    elif key == tcod.event.K_SPACE:
        action = Action(ActionType.INTERACT)

    elif key == tcod.event.K_e:
        action = Action(ActionType.LOOK)

    elif key == tcod.event.K_ESCAPE:
        action = Action(ActionType.ESCAPE)

    elif key == tcod.event.K_r:
        action = Action(ActionType.SWAP_APPENDAGE)

    elif action is None:
        action = handle_movement_keys(key)

    # No valid key was pressed
    return action


def handle_keys_player_dead(key):
    if key == tcod.event.K_TAB:
        return Action(ActionType.TOGGLE_INVENTORY)

    return Action(ActionType.RESTART)


def handle_keys_choose_option(key):
    action: [Action, None] = None

    index = key - 97
    if index >= 0:
        return Action(ActionType.CHOOSE_OPTION, option_index=index)

    elif key == tcod.event.K_TAB or key == tcod.event.K_ESCAPE:
        return Action(ActionType.TOGGLE_INVENTORY)
    return action


def handle_keys_targeting(key):
    action: [Action, None] = None

    action = handle_movement_keys(key)

    if action is None:
        if key == tcod.event.K_ESCAPE:
            action = Action(ActionType.ESCAPE)
        elif key in (tcod.event.K_KP_ENTER, tcod.event.K_SPACE):
            action = Action(ActionType.EXECUTE)

    return action


def handle_movement_keys(key):
    action: [Action, None] = None

    if key == tcod.event.K_u:
        action = Action(ActionType.MOVEMENT, dx=0, dy=-1)
    elif key == tcod.event.K_j:
        action = Action(ActionType.MOVEMENT, dx=0, dy=1)
    elif key == tcod.event.K_k:
        action = Action(ActionType.MOVEMENT, dx=1, dy=0)
    elif key == tcod.event.K_h:
        action = Action(ActionType.MOVEMENT, dx=-1, dy=0)
    elif key == tcod.event.K_y:
        action = Action(ActionType.MOVEMENT, dx=-1, dy=-1)
    elif key == tcod.event.K_i:
        action = Action(ActionType.MOVEMENT, dx=1, dy=-1)
    elif key == tcod.event.K_n:
        action = Action(ActionType.MOVEMENT, dx=-1, dy=1)
    elif key == tcod.event.K_m:
        action = Action(ActionType.MOVEMENT, dx=1, dy=1)

    return action
