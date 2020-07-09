import tcod

from enum import Enum, auto
from game_states import GameStates
from menus import inventory_menu, appendage_menu


class RenderOrder(Enum):
    STAIRS = auto()
    OPEN_DOOR = auto()
    CORPSE = auto()
    ITEM = auto()
    CLOSED_DOOR = auto()
    ACTOR = auto()


def render_all(con, panel, entities, animator, player, game_map, fov_map, fov_recompute, message_log, screen_width,
               screen_height, bar_width, panel_height, panel_y, game_state, target_x, target_y, target_entity,
               turn_count):
    if fov_recompute:
        for y in range(game_map.height):
            for x in range(game_map.width):
                visible = tcod.map_is_in_fov(fov_map, x, y)

                if visible:
                    tcod.console_set_char_background(con, x, y, game_map.tiles[x][y].light_color, tcod.BKGND_SET)

                    game_map.tiles[x][y].explored = True

                elif game_map.tiles[x][y].explored:
                    tcod.console_set_char_background(con, x, y, game_map.tiles[x][y].dark_color, tcod.BKGND_SET)

    # RENDER ANIMATIONS
    for animation in animator.animations:
        frame = animation.frames[animation.current_frame]
        for char in frame.characters:
            tcod.console_set_default_foreground(con, char.color)
            tcod.console_put_char(con, char.x, char.y, char.char, tcod.BKGND_NONE)

    entities_in_render_order = sorted(entities, key=lambda n: n.render_order.value)
    for entity in entities_in_render_order:
        draw_entity(con, entity, fov_map, game_map)

    tcod.console_set_default_foreground(con, tcod.white)

    tcod.console_blit(con, 0, 0, screen_width, screen_height, 0, 0, 0)

    tcod.console_set_default_background(panel, tcod.black)
    tcod.console_clear(panel)

    # Print player status
    tcod.console_set_default_foreground(panel, tcod.white)
    tcod.console_print_ex(panel, 1, 0, tcod.BKGND_NONE, tcod.LEFT, f'TURN: {turn_count}')
    tcod.console_print_ex(panel, 1, 1, tcod.BKGND_NONE, tcod.LEFT, f'Player PAIN: {player.body.get_pain_percent()}%')
    for i in range(1, 7):  # big dumb
        tcod.console_set_char_background(panel, i, 1, tcod.darker_gray)
        i += 1

    y = 2
    for appendage in player.body.appendages:
        text_color = tcod.gray
        if player.body.selected_appendage == appendage:
            text_color = tcod.white

        grabber = appendage.grabber
        if grabber and grabber.grabbed_entity:
            name = "{0} ({1})".format(appendage.name, grabber.grabbed_entity.char)
        else:
            name = appendage.name

        render_bar(panel, 1, y, bar_width, name, appendage.hp, appendage.max_hp,
                   tcod.light_red, tcod.darkest_red, text_color=text_color)
        y += 1

    # Print game messages
    y = len(message_log.messages)
    for message in message_log.messages:
        tcod.console_set_default_foreground(panel, message.color)
        tcod.console_print_ex(panel, message_log.x, y, tcod.BKGND_NONE, tcod.LEFT, message.text)

        y -= 1

    # Print Target entity status
    if target_entity:
        x = screen_width - bar_width - 1
        tcod.console_set_default_foreground(panel, target_entity.color)
        string = target_entity.name
        if target_entity.body:
            string = f'{target_entity.name} PAIN: {target_entity.body.get_pain_percent()}%'
        tcod.console_print_ex(panel, x, 1, tcod.BKGND_NONE, tcod.LEFT, string)
        for i in range(x, x + len(target_entity.name)):
            tcod.console_set_char_background(panel, i, 1, tcod.darker_gray)
            i += 1

        y = 2
        target_body = target_entity.body
        if target_body:
            for appendage in target_body.appendages:
                render_bar(panel, x, y, bar_width, appendage.name, appendage.hp, appendage.max_hp,
                           tcod.light_red, tcod.darker_red)
                y += 1

    tcod.console_blit(panel, 0, 0, screen_width, panel_height, 0, 0, panel_y)

    if game_state == GameStates.SHOW_INVENTORY:
        inventory_menu(con, 'CHOOSE AN ITEM TO USE...\n', player.inventory, 50, screen_width, screen_height)

    elif game_state == GameStates.DROP_INVENTORY:
        inventory_menu(con, 'CHOOSE AN ITEM TO DROP...\n', player.inventory, 50, screen_width, screen_height)
    elif game_state == GameStates.SWAP_APPENDAGE:
        appendage_menu(con, "CHOOSE AN APPENDAGE TO READY...\n", player, screen_width, screen_height)
    elif game_state == GameStates.TARGET_APPENDAGE:
        appendage_menu(con,
                       "CHOOSE AN APPENDAGE TO ATTACK WITH YOUR {0}...".format(player.body.selected_appendage.name),
                       target_entity, screen_width, screen_height)

    elif game_state in (GameStates.TARGETING, GameStates.LOOKING):
        tcod.console_set_default_foreground(con, tcod.lighter_yellow)
        tcod.console_put_char(con, target_x, target_y, 'X', tcod.BKGND_NONE)


def clear_all(con, entities):
    tcod.console_clear(con)
    for entity in entities:
        clear_entity(con, entity)


def draw_entity(con, entity, fov_map, game_map):
    if tcod.map_is_in_fov(fov_map, entity.x, entity.y) or (
            (entity.structure or entity.item) and game_map.tiles[entity.x][entity.y].explored):
        tcod.console_set_default_foreground(con, entity.color)
        tcod.console_put_char(con, entity.x, entity.y, entity.char, tcod.BKGND_NONE)


def clear_entity(con, entity):
    tcod.console_put_char(con, entity.x, entity.y, ' ', tcod.BKGND_NONE)


def render_bar(panel, x, y, total_width, name, value, maximum, bar_color, back_color, text_color=tcod.white):
    bar_width = int(float(value) / maximum * total_width)

    tcod.console_set_default_background(panel, back_color)
    tcod.console_rect(panel, x, y, total_width, 1, False, tcod.BKGND_SCREEN)

    tcod.console_set_default_background(panel, bar_color)
    if bar_width > 0:
        tcod.console_rect(panel, x, y, bar_width, 1, False, tcod.BKGND_SCREEN)

    tcod.console_set_default_foreground(panel, text_color)
    tcod.console_print_ex(panel, x, y, tcod.BKGND_NONE, tcod.LEFT,
                          '{0}: {1}/{2}'.format(name, value, maximum))
