import tcod

from enum import Enum, auto
from game_states import GameStates
from menus import inventory_menu


class RenderOrder(Enum):
    CORPSE = auto()
    ITEM = auto()
    ACTOR = auto()


def render_all(con, panel, entities, player, game_map, fov_map, fov_recompute, message_log, screen_width, screen_height,
               bar_width, panel_height, panel_y, colors, game_state):
    if fov_recompute:
        for y in range(game_map.height):
            for x in range(game_map.width):
                visible = tcod.map_is_in_fov(fov_map, x, y)
                wall = game_map.tiles[x][y].block_sight

                if visible:
                    if wall:
                        tcod.console_set_char_background(con, x, y, colors.get('light_wall'), tcod.BKGND_SET)
                    else:
                        tcod.console_set_char_background(con, x, y, colors.get('light_ground'), tcod.BKGND_SET)

                    game_map.tiles[x][y].explored = True

                elif game_map.tiles[x][y].explored:
                    if wall:
                        tcod.console_set_char_background(con, x, y, colors.get('dark_wall'), tcod.BKGND_SET)
                    else:
                        tcod.console_set_char_background(con, x, y, colors.get('dark_ground'), tcod.BKGND_SET)

    entities_in_render_order = sorted(entities, key=lambda n: n.render_order.value)
    for entity in entities_in_render_order:
        draw_entity(con, entity, fov_map)

    tcod.console_set_default_foreground(con, tcod.white)
    tcod.console_print_ex(con, 1, screen_height - 2, tcod.BKGND_NONE, tcod.LEFT,
                          'HP: {0:02}/{1:02}'.format(player.fighter.hp, player.fighter.max_hp))

    tcod.console_blit(con, 0, 0, screen_width, screen_height, 0, 0, 0)

    tcod.console_set_default_background(panel, tcod.black)
    tcod.console_clear(panel)

    # Print game messages
    y = len(message_log.messages)
    for message in message_log.messages:
        tcod.console_set_default_foreground(panel, message.color)
        tcod.console_print_ex(panel, message_log.x, y, tcod.BKGND_NONE, tcod.LEFT, message.text)
        y -= 1
    render_bar(panel, 1, 1, bar_width, 'HP', player.fighter.hp, player.fighter.max_hp, tcod.light_red, tcod.darker_red)

    tcod.console_blit(panel, 0, 0, screen_width, panel_height, 0, 0, panel_y)

    if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
        inventory_menu(con, 'INVENTORY\n', player.inventory, 50, screen_width, screen_height)
    elif game_state == GameStates.TARGETING:
        target_x = player.fighter.target_x
        target_y = player.fighter.target_y
        print(target_x, target_y)
        tcod.console_set_default_foreground(con, tcod.lighter_yellow)
        tcod.console_put_char(con, target_x, target_y, 'X', tcod.BKGND_NONE)


def clear_all(con, entities):
    tcod.console_clear(con)
    for entity in entities:
        clear_entity(con, entity)


def draw_entity(con, entity, fov_map):
    if tcod.map_is_in_fov(fov_map, entity.x, entity.y) or entity.render_order == RenderOrder.CORPSE:
        tcod.console_set_default_foreground(con, entity.color)
        tcod.console_put_char(con, entity.x, entity.y, entity.char, tcod.BKGND_NONE)


def clear_entity(con, entity):
    tcod.console_put_char(con, entity.x, entity.y, ' ', tcod.BKGND_NONE)


def render_bar(panel, x, y, total_width, name, value, maximum, bar_color, back_color):
    bar_width = int(float(value) / maximum * total_width)

    tcod.console_set_default_background(panel, back_color)
    tcod.console_rect(panel, x, y, total_width, 1, False, tcod.BKGND_SCREEN)

    tcod.console_set_default_background(panel, bar_color)
    if bar_width > 0:
        tcod.console_rect(panel, x, y, bar_width, 1, False, tcod.BKGND_SCREEN)

    tcod.console_set_default_foreground(panel, tcod.white)
    tcod.console_print_ex(panel, int(x + total_width / 2), y, tcod.BKGND_NONE, tcod.CENTER,
                          '{0}: {1}/{2}'.format(name, value, maximum))
