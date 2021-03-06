import tcod

from actions import Action, ActionType
from input_handlers import handle_keys, handle_keys_main_menu
from entity import get_blocking_entities_at_location, get_entities_at_location
from render_functions import render_all, clear_all
from fov_functions import initialize_fov, recompute_fov, recompute_walkable
from path_functions import generate_path_map
from game_states import GameStates
from death_functions import kill_player, kill_entity
from game_messages import Message
from loader_functions.initialize_new_game import get_constants, get_game_variables
from loader_functions.data_loaders import save_game, load_game
from menus import main_menu, message_box
from game_map import GameMap
from animation import Animator
from components.ai import Player

def main():
    constants = get_constants()

    player = None
    entities = []
    game_map = None
    message_log = []
    game_state = None
    animator = None

    tcod.console_set_custom_font("Codepage-437.png", tcod.FONT_LAYOUT_CP437)

    tileset = tcod.tileset.load_tilesheet(
        "Codepage-437.png", 16, 16, tcod.tileset.CHARMAP_CP437
    )

    panel = tcod.console.Console(constants['screen_width'], constants['panel_height'])

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
                        if action:
                            action_type: ActionType = action.action_type

                            show_load_error_message = False

                            if action_type == ActionType.NEW_GAME:
                                player, entities, animator, turn_count, game_map, message_log, game_state = get_game_variables(
                                    constants)
                                show_main_menu = False
                            elif action_type == ActionType.LOAD_GAME:
                                try:
                                    player, entities, animator, turn_count, game_map, message_log, game_state = load_game()
                                    show_main_menu = False
                                except FileNotFoundError:
                                    show_load_error_message = True
                                    show_main_menu = True
                            elif action_type == ActionType.ESCAPE:
                                raise SystemExit()
                    if event.type == "QUIT":
                        raise SystemExit()
            else:
                play_game(root_console, player, entities, animator, turn_count, game_map, message_log, game_state,
                          panel, constants)


def play_game(con, player, entities, animator: Animator, turn_count: int, game_map: GameMap, message_log, game_state,
              panel, constants):
    target_x, target_y = player.x, player.y
    targeting_item = None
    target_entity = None

    while True:
        fov_algorithm = 2
        fov_light_walls = True
        fov_radius = 20
        fov_recompute = True
        fov_map = initialize_fov(game_map)

        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y, fov_radius, fov_light_walls, fov_algorithm)

        render_all(con, panel, entities, animator, player, game_map, fov_map, fov_recompute, message_log,
                   constants['screen_width'], constants['screen_height'], constants['bar_width'],
                   constants['panel_height'], constants['panel_y'], game_state, target_x, target_y,
                   target_entity, turn_count)

        tcod.console_flush()

        clear_all(con, entities)

        player_turn_results = []

        animator.advance_frame()

        # Handle Game State
        if game_state == GameStates.ENEMY_TURN:
            turn_count += 1

            # Generate path map with all static tiles (ignore entities for now)
            path_map = generate_path_map(game_map, entities=None, player=player)

            for entity in entities:
                if entity.ai and entity.ai != Player:
                    recompute_walkable(fov_map, game_map, entities, entity)
                    entity_turn_results = entity.ai.take_turn(player, fov_map, game_map, entities, path_map)

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
                save_game(player, entities, animator, turn_count, game_map, message_log, game_state)
                raise SystemExit()

            if event.type == "KEYDOWN":
                action: [Action, None] = handle_keys(event.sym, game_state)

                if action is None:
                    continue

                action_type: ActionType = action.action_type

                if action_type == ActionType.EXECUTE:
                    if game_state == GameStates.TARGETING:
                        item_use_results = player.body.use_selected_appendage(entities=entities,
                                                                              fov_map=fov_map,
                                                                              game_map=game_map,
                                                                              target_x=target_x, target_y=target_y)
                        player_turn_results.extend(item_use_results)
                        game_state = GameStates.ENEMY_TURN
                    elif game_state == GameStates.LOOKING:
                        look_results = []

                        looked_at_entities = get_entities_at_location(entities, target_x, target_y)
                        if tcod.map_is_in_fov(fov_map, target_x, target_y):
                            if looked_at_entities:
                                for entity in looked_at_entities:
                                    look_results.extend(entity.get_description())
                                    target_entity = entity
                            else:
                                if game_map.tiles[target_x][target_y].blocked:
                                    look_results.append({
                                        'message': Message("You stare at the wall.")
                                    })
                                else:
                                    look_results.append({
                                        'message': Message("You stare into empty space.")
                                    })
                        else:
                            look_results.append({
                                'message': Message("You can't see that far.")
                            })

                        game_state = GameStates.PLAYER_TURN
                        player_turn_results.extend(look_results)

                if action_type == ActionType.MOVEMENT:
                    dx: int = action.kwargs.get("dx", 0)
                    dy: int = action.kwargs.get("dy", 0)

                    # Player Movement
                    if game_state == GameStates.PLAYER_TURN:
                        destination_x = player.x + dx
                        destination_y = player.y + dy

                        tile_results = game_map.tiles[destination_x][destination_y].overlap_entity(player)
                        player_turn_results.extend(tile_results)

                        if not game_map.is_blocked(destination_x, destination_y):
                            target_appendage = get_blocking_entities_at_location(entities, destination_x, destination_y)

                            if target_appendage:
                                if target_appendage.body:
                                    player_fighter = player.body.selected_appendage.fighter

                                    if player_fighter:
                                        target_entity = target_appendage
                                        game_state = GameStates.TARGET_APPENDAGE
                                    else:
                                        player_turn_results.append({
                                            'message': Message("You cannot attack with your {0}.".format(
                                                player.body.selected_appendage.name), tcod.yellow)
                                        })
                                elif target_appendage.structure:
                                    structure_interact_results = target_appendage.structure.interact(player)
                                    player_turn_results.extend(structure_interact_results)
                            else:
                                player.move(dx, dy)
                        else:
                            player_turn_results.append(
                                {'message': Message("You slam yourself into the wall!", tcod.orange)})

                        if game_state != GameStates.TARGET_APPENDAGE:
                            game_state = GameStates.ENEMY_TURN

                    # Targeting
                    elif game_state in (GameStates.TARGETING, GameStates.LOOKING):
                        new_x = target_x + dx
                        new_y = target_y + dy
                        if player.distance(new_x, new_y) < targeting_radius:
                            target_x = new_x
                            target_y = new_y

                elif action_type == ActionType.GRAB:
                    for entity in entities:
                        if entity.item and entity.x == player.x and entity.y == player.y:
                            pickup_result = player.body.grab_entity(entity)
                            player_turn_results.extend(pickup_result)
                            break
                    else:
                        player_turn_results.append({'message': Message('You grab at the air', tcod.yellow)})

                    game_state = GameStates.ENEMY_TURN

                elif action_type == ActionType.LOOK:
                    game_state = GameStates.LOOKING
                    target_x, target_y = player.x, player.y
                    targeting_radius = 100

                elif action_type == ActionType.WAIT:
                    player_turn_results.append({'message': Message('You stare blankly into space', tcod.yellow)})
                    game_state = GameStates.ENEMY_TURN

                elif action_type == ActionType.CHOOSE_OPTION:
                    option_index = action.kwargs.get("option_index", None)

                    if game_state == GameStates.SWAP_APPENDAGE:
                        if option_index < len(player.body.appendages):
                            item = player.body.appendages[option_index]
                            swap_results = player.body.select_appendage(item)
                            player_turn_results.extend(swap_results)
                            game_state = GameStates.PLAYER_TURN

                    elif game_state == GameStates.TARGET_APPENDAGE:
                        if option_index < len(target_entity.body.appendages):
                            target_appendage = target_entity.body.appendages[option_index]
                            attack_results = player.body.selected_appendage.fighter.attack_appendage(target_appendage)
                            player_turn_results.extend(attack_results)
                            game_state = GameStates.ENEMY_TURN

                elif action_type == ActionType.INTERACT:
                    for entity in entities:
                        if entity.structure and entity.x == player.x and entity.y == player.y:
                            interact_results = entity.structure.interact(player)
                            player_turn_results.extend(interact_results)
                            break
                    else:
                        if game_state == GameStates.PLAYER_TURN:
                            activate_item_results = player.body.use_selected_appendage(fov_map=fov_map,
                                                                                       game_map=game_map,
                                                                                       entities=entities)
                            if activate_item_results:
                                player_turn_results.extend(activate_item_results)
                                game_state = GameStates.ENEMY_TURN

                elif action_type == ActionType.DROP_INVENTORY_ITEM:
                    grabber = player.body.selected_appendage.grabber
                    if grabber:
                        player_turn_results.extend(grabber.drop())
                    # game_state = GameStates.DROP_INVENTORY

                elif action_type == ActionType.SWAP_APPENDAGE:
                    game_state = GameStates.SWAP_APPENDAGE

                elif action_type == ActionType.ESCAPE:
                    if game_state == GameStates.TARGETING:
                        game_state = GameStates.PLAYER_TURN
                    elif game_state == GameStates.PLAYER_TURN:
                        save_game(player, entities, animator, turn_count, game_map, message_log, game_state)
                        main()
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
            next_floor = player_turn_result.get('next_floor')

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

                targeting_item = targeting
                targeting_radius = targeting.item.targeting_radius
                target_x = player.x
                target_y = player.y

                message_log.add_message(Message("You begin aiming the {0}.".format(targeting.name)))
                # TODO: Replace occurrences of add_message with player_turn_result approach
                # player_turn_results.append({'message': Message("You begin aiming the {0}.".format(targeting.name))})

            if next_floor:
                entities = game_map.next_floor(player, constants)
                fov_map = initialize_fov(game_map)
                tcod.console_clear(con)


if __name__ == "__main__":
    main()
