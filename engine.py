import tcod

from actions import Action, ActionType
from input_handlers import handle_keys, handle_keys_main_menu
from entity import get_blocking_entities_at_location
from render_functions import render_all, clear_all
from fov_functions import initialize_fov, recompute_fov
from game_states import GameStates
from death_functions import kill_player, kill_entity
from game_messages import Message
from path_functions import recompute_path
from loader_functions.initialize_new_game import get_constants, get_game_variables
from loader_functions.data_loaders import save_game, load_game
from menus import main_menu, message_box
import os


def main():
    constants = get_constants()

    player = None
    entities = []
    game_map = None
    message_log = []
    game_state = None

    tcod.console_set_custom_font("dejavu16x16_gs_tc.png", tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD)

    panel = tcod.console.Console(constants['screen_width'], constants['panel_height'])

    # play_game(player, entities, game_map, message_log, game_state, panel, constants)

    show_main_menu = True
    show_load_error_message = False

    with tcod.console_init_root(
            w=constants['screen_width'],
            h=constants['screen_height'],
            title=constants['window_title'],
            order="F",
            vsync=True
    ) as root_console:
        while True:
            if show_main_menu:
                main_menu(root_console, constants['screen_width'], constants['screen_height'])
                tcod.console_flush()

                if show_load_error_message:
                    message_box(root_console, 'No save game to load', 50, constants['screen_width'],
                                constants['screen_height'])

                # Handle Events
                for event in tcod.event.wait():
                    if event.type == "KEYDOWN":
                        action: [Action, None] = handle_keys_main_menu(event.sym)
                        action_type: ActionType = action.action_type

                        show_load_error_message = False

                        if action_type == ActionType.NEW_GAME:
                            player, entities, game_map, message_log, game_state = get_game_variables(constants)
                            show_main_menu = False
                        elif action_type == ActionType.LOAD_GAME:
                            try:
                                player, entities, game_map, message_log, game_state = load_game()
                                show_main_menu = False
                            except FileNotFoundError:
                                show_load_error_message = True
                                show_main_menu = True
                        elif action_type == ActionType.ESCAPE:
                            raise SystemExit()
                    if event.type == "QUIT":
                        raise SystemExit()
            else:
                play_game(root_console, player, entities, game_map, message_log, game_state, panel, constants)

        show_main_menu = True

    # if show_main_menu:
    #     with tcod.console_init_root(
    #             w=constants['screen_width'],
    #             h=constants['screen_height'],
    #             title=constants['window_title'],
    #             order="F",
    #             vsync=True
    #     ) as root_console:


def play_game(con, player, entities, game_map, message_log, game_state, panel, constants):
    while True:
        fov_algorithm = 2
        fov_light_walls = True
        fov_radius = 10
        fov_recompute = True
        fov_map = initialize_fov(game_map)

        path_map = recompute_path(game_map, entities)

        path_map = recompute_path(game_map, entities)

        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y, fov_radius, fov_light_walls, fov_algorithm)

        render_all(con, panel, entities, player, game_map, fov_map, fov_recompute, message_log,
                   constants['screen_width'], constants['screen_height'], constants['bar_width'],
                   constants['panel_height'], constants['panel_y'], constants['colors'], game_state)

        fov_recompute = True  # False

        tcod.console_flush()

        clear_all(con, entities)

        player_turn_results = []

        # Handle Game State
        if game_state == GameStates.ENEMY_TURN:
            for entity in entities:
                if entity.ai:
                    entity_turn_results = entity.ai.take_turn(player, fov_map, fov_map, game_map)

                    for entity_turn_result in entity_turn_results:
                        message = entity_turn_result.get('message')
                        dead_entity = entity_turn_result.get('dead')

                        if message:
                            message_log.add_message(message)

                        if dead_entity:
                            if dead_entity == player:
                                message, game_state = kill_player(player)
                            else:
                                message = kill_entity(dead_entity)

                            message_log.add_message(message)

                            if game_state == GameStates.PLAYER_DEAD:
                                break

                    if game_state == GameStates.PLAYER_DEAD:
                        break
            else:
                game_state = GameStates.PLAYER_TURN

        # Handle Events
        for event in tcod.event.wait():
            if event.type == "QUIT":
                save_game(player, entities, game_map, message_log, game_state)
                raise SystemExit()

            if event.type == "KEYDOWN":
                action: [Action, None] = handle_keys(event.sym, game_state)

                if action is None:
                    continue

                action_type: ActionType = action.action_type

                if action_type == ActionType.ESCAPE:
                    if game_state == GameStates.TARGETING:
                        game_state = GameStates.PLAYER_TURN

                elif action_type == ActionType.EXECUTE:
                    if game_state == GameStates.TARGETING:
                        targeting_item = player.fighter.targeting_item
                        print(targeting_item)
                        target_x = player.fighter.target_x
                        target_y = player.fighter.target_y
                        item_use_results = player.inventory.use(targeting_item, entities=entities, fov_map=fov_map,
                                                                game_map=game_map,
                                                                target_x=target_x, target_y=target_y)
                        player_turn_results.extend(item_use_results)
                        game_state = GameStates.ENEMY_TURN

                if action_type == ActionType.MOVEMENT:
                    dx: int = action.kwargs.get("dx", 0)
                    dy: int = action.kwargs.get("dy", 0)

                    # Player Movement
                    if game_state == GameStates.PLAYER_TURN:
                        destination_x = player.x + dx
                        destination_y = player.y + dy
                        if not game_map.is_blocked(destination_x, destination_y):
                            target = get_blocking_entities_at_location(entities, destination_x, destination_y)

                            if target:
                                attack_results = player.fighter.attack(target.fighter)
                                player_turn_results.extend(attack_results)
                            else:
                                player.move(dx, dy)

                                fov_recompute = True
                        else:
                            message_log.add_message(Message("You slam yourself into the wall!", tcod.orange))

                        game_state = GameStates.ENEMY_TURN

                    # Targeting
                    elif game_state == GameStates.TARGETING:
                        player.fighter.target_x += dx
                        player.fighter.target_y += dy

                elif action_type == ActionType.GRAB:
                    for entity in entities:
                        if entity.item and entity.x == player.x and entity.y == player.y:
                            pickup_result = player.inventory.add_item(entity)
                            player_turn_results.extend(pickup_result)
                            break
                    else:
                        message_log.add_message(Message('You grab at the air', tcod.yellow))

                    game_state = GameStates.ENEMY_TURN

                elif action_type == ActionType.TOGGLE_INVENTORY:

                    if game_state == GameStates.SHOW_INVENTORY:
                        game_state = GameStates.PLAYER_TURN
                    elif game_state == GameStates.PLAYER_TURN:
                        clear_all(con, entities)
                        game_state = GameStates.SHOW_INVENTORY

                elif action_type == ActionType.ACTIVATE_INVENTORY_ITEM:
                    item_index = action.kwargs.get("item_index", None)

                    if item_index < len(player.inventory.items):
                        item = player.inventory.items[item_index]
                        if item:
                            if game_state == GameStates.SHOW_INVENTORY:
                                activate_item_results = player.inventory.use(item, fov_map=fov_map,
                                                                             game_map=game_map,
                                                                             entities=entities)
                                player_turn_results.extend(activate_item_results)
                            elif game_state == GameStates.DROP_INVENTORY:
                                drop_item_results = player.inventory.drop_item(item)
                                player_turn_results.extend(drop_item_results)

                    game_state = GameStates.ENEMY_TURN

                elif action_type == ActionType.DROP_INVENTORY_ITEM:
                    game_state = GameStates.DROP_INVENTORY
                elif action_type == ActionType.ESCAPE:
                    if game_state == GameStates.TARGETING:
                        game_state = GameStates.PLAYER_TURN
                    else:
                        save_game(player, entities, game_map, message_log, game_state)
                        raise SystemExit()
                elif action_type == ActionType.RESTART:
                    main()

        # Process player turn results
        for player_turn_result in player_turn_results:
            message = player_turn_result.get('message')
            dead_entity = player_turn_result.get('dead')
            item_added = player_turn_result.get('item_added')
            item_consumed = player_turn_result.get('consumed')
            item_dropped = player_turn_result.get('item_dropped')
            targeting = player_turn_result.get('targeting')
            map_changed = player_turn_result.get('map_changed')

            if message:
                message_log.add_message(message)

            if dead_entity:
                if dead_entity == player:
                    message, game_state = kill_player(player)
                else:
                    message_log.add_message(kill_entity(dead_entity))

            if item_added:
                entities.remove(item_added)
                game_state = GameStates.ENEMY_TURN

            if item_dropped:
                entities.append(item_dropped)

                game_state = GameStates.ENEMY_TURN

            if targeting:
                game_state = GameStates.TARGETING

                player.fighter.targeting_item = targeting
                player.fighter.target_x = player.x
                player.fighter.target_y = player.y

                message_log.add_message(Message("You begin aiming the {0}.".format(targeting.name)))

            if map_changed:
                fov_map = initialize_fov(game_map)


if __name__ == "__main__":
    main()
