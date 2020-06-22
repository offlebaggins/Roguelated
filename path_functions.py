import tcod


def recompute_path(game_map, entities):
    path_map = tcod.map_new(game_map.width, game_map.height)

    path_map.walkable[:] = True

    for y in range(game_map.width):
        for x in range(game_map.height):
            path_map.walkable[x, y] = True

    # for entity in entities:
    #     if entity.blocks:
    #         path_map.walkable[entity.x, entity.y] = False

    return path_map

