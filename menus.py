import tcod


def menu(con, header, options, width, screen_width, screen_height, option_colors=None):
    if option_colors is None:
        option_colors = []
        for i in range(len(options)):
            option_colors.append(tcod.white)

    if len(options) > 26:
        raise ValueError('Cannot have more than 26 options')

    # calculate total height for the header (after auto-wrap) and one line per option
    header_height = tcod.console_get_height_rect(con, 0, 0, width, screen_height, header)
    height = len(options) + header_height + 3

    window = tcod.console_new(width, height)

    # print the header, with auto-wrap
    tcod.console_print_rect_ex(window, 0, 0, width, height, tcod.BKGND_DARKEN, tcod.LEFT, header)

    # tcod.console_pfovrint_ex(window, 0, 0, tcod.BKGND_NONE, tcod.LEFT, horizontal_border)

    # for x in range(width):
    #     tcod.console_put_char(window, x, 0, 33, tcod.BKGND_NONE)
    #     tcod.console_put_char(window, x, height - 1, 33, tcod.BKGND_NONE)

    y = header_height + 1
    letter_index = ord('a')

    for option_text in options:
        tcod.console_set_default_foreground(window, option_colors[y - header_height - 2])
        text = '(' + chr(letter_index) + ') ' + option_text
        tcod.console_print_ex(window, 0, y, tcod.BKGND_NONE, tcod.LEFT, text)
        y += 1
        letter_index += 1

    # blit the contents of "window" to the root console
    x = int(screen_width / 2 - width / 2)
    y = int(screen_height / 2 - height / 2)
    tcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)


def inventory_menu(con, header, inventory, inventory_width, screen_width, screen_height):
    if len(inventory.items) == 0:
        options = ['Inventory is empty.']
        option_colors = [tcod.white]
    else:
        options = [item.name for item in inventory.items]
        option_colors = [item.color for item in inventory.items]

    menu(con, header, options, inventory_width, screen_width, screen_height, option_colors)


def appendage_menu(con, header, entity, screen_width, screen_height):
    appendages = []
    for appendage in entity.body.appendages:
        if appendage.fighter:
            appendages.append(appendage.name)
        else:
            appendages.append(appendage.name)

    if len(appendages) == 0:
        appendages = ["The {0} has no appendages".format(entity.name)]

    menu(con, header, appendages, 50, screen_width, screen_height)


def main_menu(con, screen_width, screen_height):
    tcod.console_print_ex(0, int(screen_width / 2), int(screen_height / 2) - 10, tcod.BKGND_NONE, tcod.CENTER,
                          'ROGUESIMILAR')

    menu(con, '', ['NEW GAME', 'CONTINUE', 'QUIT'], 24, screen_width, screen_height)


def message_box(con, header, width, screen_width, screen_height):
    menu(con, header, [], width, screen_width, screen_height)
